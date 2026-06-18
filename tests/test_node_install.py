"""urisys init must not use git+https (GitHub credential prompts)."""

from __future__ import annotations

from urisys.init_setup import default_node_pip_spec, default_pip_specs
from urisys.node_install import pip_spec as node_wheel_spec, wheel_url


def test_default_pip_specs_no_git_urls():
    specs = default_pip_specs()
    assert not any("git+" in s for s in specs)
    assert not any("github.com" in s and "releases/download" not in s for s in specs)


def test_urisys_node_uses_release_wheel():
    spec = default_node_pip_spec()
    assert spec == node_wheel_spec()
    assert "releases/download" in spec
    assert spec.endswith(".whl")
    assert "urisys_node-" in spec
    assert "git+" not in spec


def test_urisys_node_wheel_filename_pep427():
    from urisys.node_install import DEFAULT_GITHUB_VERSION, wheel_filename

    assert wheel_filename("0.1.3") == "urisys_node-0.1.3-py3-none-any.whl"
    assert wheel_filename() == f"urisys_node-{DEFAULT_GITHUB_VERSION}-py3-none-any.whl"


def test_urisys_node_wheel_url_override():
    import os

    os.environ["URISYS_NODE_WHEEL_URL"] = "https://example.com/custom.whl"
    try:
        assert wheel_url() == "https://example.com/custom.whl"
    finally:
        os.environ.pop("URISYS_NODE_WHEEL_URL", None)
