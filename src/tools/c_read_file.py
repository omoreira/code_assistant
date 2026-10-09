#!/usr/bin/env python3
import argparse, os, pathlib

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="Path relative to workspace root")
    ap.add_argument("--start", type=int, default=None, help="1-based inclusive line number")
    ap.add_argument("--end", type=int, default=None, help="1-based inclusive line number")
    ap.add_argument("--max_chars", type=int, default=40000)
    args = ap.parse_args()

    workspace_root = pathlib.Path(os.getcwd()).resolve()
    target = (workspace_root / args.path).resolve()

    if not str(target).startswith(str(workspace_root)):
        raise SystemExit("Refusing to read outside workspace")

    if not target.exists() or not target.is_file():
        raise SystemExit("File not found or not a file")

    text = target.read_text(encoding="utf-8", errors="replace")

    if args.start is not None or args.end is not None:
        lines = text.splitlines(True)  # keep newlines
        start = 1 if args.start is None else max(1, args.start)
        end = len(lines) if args.end is None else min(len(lines), args.end)
        text = "".join(lines[start-1:end])

    if len(text) > args.max_chars:
        text = text[:args.max_chars] + "\n[TRUNCATED]"

    print(text, end="")

if __name__ == "__main__":
    main()
