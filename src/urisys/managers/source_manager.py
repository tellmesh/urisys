from __future__ import annotations

import hashlib
import io
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import parse_qs, unquote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

_GITHUB_SHORT = re.compile(
    r"^github:(?P<owner>[^/]+)/(?P<repo>[^/]+)/(?P<path>.+?)(?:@(?P<ref>[^/]+))?$"
)
_GH_URI = re.compile(
    r"^gh://(?P<owner>[^/]+)/(?P<repo>[^/]+)/(?P<path>.+?)(?:\?(?P<query>.*))?$"
)


class SourceError(ValueError):
    """Raised when a Markpact source cannot be resolved."""


class SourceManager:
    """Resolve Markpact sources from local paths, HTTP(S), GitHub, git repos and ZIP archives."""

    def __init__(self, cache_root: str | Path = ".urisys/cache/sources") -> None:
        self.cache_root = Path(cache_root)

    def is_remote_source(self, source: str) -> bool:
        value = source.strip()
        if value.startswith(("gh://", "git+", "zip+", "raw+https://", "raw+http://", "github:", "file://", "http://", "https://")):
            return True
        return "://" in value and not Path(value).exists()

    def resolve(self, source: str) -> Path:
        return self.fetch(source)["local_path"]

    def fetch(self, source: str, *, force: bool = False) -> dict[str, Any]:
        spec = source.strip()
        if not spec:
            raise SourceError("Empty Markpact source.")

        if spec.startswith("file://"):
            local = Path(unquote(urlsplit(spec).path))
            if not local.exists():
                raise SourceError(f"Local file not found: {local}")
            return self._result(spec, local, cached=False)

        if spec.startswith(("http://", "https://", "raw+http://", "raw+https://")):
            return self._fetch_http(spec, force=force)

        if spec.startswith("gh://"):
            return self._fetch_github_uri(spec, force=force)

        match = _GITHUB_SHORT.match(spec)
        if match:
            ref = match.group("ref") or "main"
            return self._fetch_github_raw(
                match.group("owner"),
                match.group("repo"),
                match.group("path"),
                ref,
                original=spec,
                force=force,
            )

        if spec.startswith("git+"):
            return self._fetch_git(spec, force=force)

        if spec.startswith("zip+"):
            return self._fetch_zip(spec, force=force)

        local = Path(spec).expanduser()
        if local.exists():
            return self._result(spec, local.resolve(), cached=False)

        raise SourceError(f"Unsupported or missing Markpact source: {spec!r}")

    def _result(self, source: str, local_path: Path, *, cached: bool, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ok": True,
            "source": source,
            "local_path": str(local_path),
            "cached": cached,
            "bytes": local_path.stat().st_size if local_path.exists() else 0,
        }
        if extra:
            payload.update(extra)
        return payload

    def _cache_dir(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        return self.cache_root / digest

    def _fetch_http(self, spec: str, *, force: bool) -> dict[str, Any]:
        url = spec[4:] if spec.startswith("raw+") else spec
        cache_dir = self._cache_dir(url)
        filename = Path(urlsplit(url).path).name or "source.markpact.md"
        local_path = cache_dir / filename
        meta_path = cache_dir / "source.json"

        if local_path.exists() and meta_path.exists() and not force:
            return self._result(spec, local_path, cached=True, extra={"url": url})

        cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            request = Request(url, headers={"User-Agent": "urisys-markpact-fetch/0.1"})
            with urlopen(request, timeout=30) as response:
                data = response.read()
        except URLError as exc:
            raise SourceError(f"Failed to fetch {url}: {exc}") from exc

        local_path.write_bytes(data)
        meta_path.write_text(json.dumps({"source": spec, "url": url}, ensure_ascii=False, indent=2), encoding="utf-8")
        return self._result(spec, local_path, cached=True, extra={"url": url})

    def _fetch_github_uri(self, spec: str, *, force: bool) -> dict[str, Any]:
        match = _GH_URI.match(spec)
        if not match:
            raise SourceError(f"Invalid gh:// source: {spec!r}")
        query = parse_qs(match.group("query") or "")
        ref = (query.get("ref") or ["main"])[0]
        return self._fetch_github_raw(match.group("owner"), match.group("repo"), match.group("path"), ref, original=spec, force=force)

    def _fetch_github_raw(self, owner: str, repo: str, path: str, ref: str, *, original: str, force: bool) -> dict[str, Any]:
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path.lstrip('/')}"
        cache_dir = self._cache_dir(f"github:{owner}/{repo}@{ref}:{path}")
        filename = Path(path).name or "source.markpact.md"
        local_path = cache_dir / filename
        meta_path = cache_dir / "source.json"

        if local_path.exists() and meta_path.exists() and not force:
            return self._result(original, local_path, cached=True, extra={"url": url, "ref": ref})

        cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            request = Request(url, headers={"User-Agent": "urisys-markpact-fetch/0.1"})
            with urlopen(request, timeout=30) as response:
                data = response.read()
        except URLError as exc:
            raise SourceError(f"Failed to fetch GitHub raw {url}: {exc}") from exc

        local_path.write_bytes(data)
        meta_path.write_text(
            json.dumps({"source": original, "url": url, "owner": owner, "repo": repo, "ref": ref, "path": path}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self._result(original, local_path, cached=True, extra={"url": url, "ref": ref})

    def _fetch_git(self, spec: str, *, force: bool) -> dict[str, Any]:
        body = spec[4:]
        if "//" not in body:
            raise SourceError(f"git+ source must include repo URL and in-repo path separated by //: {spec!r}")
        repo_url, in_repo_path = body.split("//", 1)
        parsed = urlsplit(repo_url)
        query = parse_qs(parsed.query)
        ref = (query.get("ref") or ["main"])[0]
        clean_repo_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
        cache_dir = self._cache_dir(f"git:{clean_repo_url}@{ref}:{in_repo_path}")
        filename = Path(in_repo_path).name or "source.markpact.md"
        local_path = cache_dir / filename

        if local_path.exists() and not force:
            return self._result(spec, local_path, cached=True, extra={"repo": clean_repo_url, "ref": ref, "path": in_repo_path})

        cache_dir.mkdir(parents=True, exist_ok=True)
        checkout_dir = cache_dir / "repo"
        if checkout_dir.exists():
            shutil.rmtree(checkout_dir)
        checkout_dir.mkdir(parents=True, exist_ok=True)

        cmd = ["git", "clone", "--depth", "1", "--branch", ref, clean_repo_url, str(checkout_dir)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            fallback = ["git", "clone", "--depth", "1", clean_repo_url, str(checkout_dir)]
            proc = subprocess.run(fallback, capture_output=True, text=True)
            if proc.returncode != 0:
                raise SourceError(f"git clone failed for {clean_repo_url}: {proc.stderr.strip() or proc.stdout.strip()}")

        source_file = checkout_dir / in_repo_path.lstrip("/")
        if not source_file.exists():
            raise SourceError(f"Markpact not found in git repo: {in_repo_path}")
        local_path.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")
        return self._result(spec, local_path, cached=True, extra={"repo": clean_repo_url, "ref": ref, "path": in_repo_path})

    def _fetch_zip(self, spec: str, *, force: bool) -> dict[str, Any]:
        body = spec[4:]
        if "//" not in body:
            raise SourceError(f"zip+ source must include archive URL and in-archive path separated by //: {spec!r}")
        archive_url, in_archive_path = body.split("//", 1)
        cache_dir = self._cache_dir(f"zip:{archive_url}:{in_archive_path}")
        filename = Path(in_archive_path).name or "source.markpact.md"
        local_path = cache_dir / filename

        if local_path.exists() and not force:
            return self._result(spec, local_path, cached=True, extra={"archive_url": archive_url, "path": in_archive_path})

        cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            request = Request(archive_url, headers={"User-Agent": "urisys-markpact-fetch/0.1"})
            with urlopen(request, timeout=60) as response:
                archive_bytes = response.read()
        except URLError as exc:
            raise SourceError(f"Failed to download ZIP {archive_url}: {exc}") from exc

        normalized_target = in_archive_path.lstrip("/")
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zf:
            names = zf.namelist()
            candidate = normalized_target
            if candidate not in names:
                matches = [name for name in names if name.endswith(normalized_target)]
                if len(matches) == 1:
                    candidate = matches[0]
                else:
                    raise SourceError(f"Path {in_archive_path!r} not found in ZIP archive.")
            local_path.write_bytes(zf.read(candidate))

        return self._result(spec, local_path, cached=True, extra={"archive_url": archive_url, "path": in_archive_path})
