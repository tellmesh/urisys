import argparse, json, os
from .env import load_urisys_env
from .runtime import Runtime, load_json, run_flow, serve


def build_runtime(args):
    config = load_json(getattr(args, 'config', None))
    rt = Runtime(events_path=getattr(args, 'events', 'data/events.jsonl'), config=config)
    packs = set((getattr(args, 'packs', 'kvm,him,ocr,llm') or '').split(','))
    if 'him' in packs:
        import urihim; urihim.register(rt)
    if 'ocr' in packs:
        import uriocr; uriocr.register(rt)
    if 'llm' in packs:
        import urillm; urillm.register(rt)
    if 'kvm' in packs:
        import urikvm; urikvm.register(rt)
    return rt


def main(argv=None):
    p = argparse.ArgumentParser(prog='urisys-kvm')
    p.add_argument('--packs', default='kvm,him,ocr,llm')
    p.add_argument('--config', default=os.environ.get('URISYS_CONFIG', 'config/kvm-profile.json'))
    p.add_argument('--events', default='data/events.jsonl')
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('call')
    c.add_argument('uri')
    c.add_argument('--payload', default='{}')
    c.add_argument('--approve', action='store_true')
    c.add_argument('--dry-run', action='store_true')
    c.add_argument('--allow-real', action='store_true')
    s = sub.add_parser('serve')
    s.add_argument('--host', default='0.0.0.0')
    s.add_argument('--port', type=int, default=8794)
    f = sub.add_parser('flow')
    f.add_argument('path')
    f.add_argument('--approve', action='store_true')
    f.add_argument('--dry-run', action='store_true')
    f.add_argument('--allow-real', action='store_true')
    args = p.parse_args(argv)
    load_urisys_env()
    rt = build_runtime(args)
    if args.cmd == 'serve':
        return serve(rt, args.host, args.port)
    if args.cmd == 'call':
        res = rt.call(args.uri, json.loads(args.payload), {'approved': args.approve, 'dry_run': args.dry_run, 'allow_real': args.allow_real})
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res.get('ok') else 1
    if args.cmd == 'flow':
        res = run_flow(rt, args.path, {'approved': args.approve, 'dry_run': args.dry_run, 'allow_real': args.allow_real})
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if all(r.get('ok') for r in res) else 1

if __name__ == '__main__':
    raise SystemExit(main())
