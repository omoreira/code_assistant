#!/usr/bin/env python3
import argparse, os, pathlib

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="Path relative to workspace root")
    ap.add_argument("--start", type=int, default=None, help="1-based start line")
    ap.add_argument("--end", type=int, default=None, help="1-based end line (inclusive)")
    ap.add_argument("--max_chars", type=int, default=40000)
    args = ap.parse_args()

    # Restrict to current working directory (use your workspace root when calling)
    workspace_root = pathlib.Path(os.getcwd()).resolve()
    target = (workspace_root / args.path).resolve()

    if not str(target).startswith(str(workspace_root)):
        raise SystemExit("Refusing to read outside workspace")

    if not target.exists() or not target.is_file():
        raise SystemExit("File not found or not a file")

    # Optional: extension allowlist
    # allowed = {".py",".ts",".js",".tsx",".jsx",".go",".java",".rs",".c",".h",".cpp",".md",".json",".yml",".yaml",".toml"}
    # if target.suffix not in allowed: raise SystemExit("Extension not allowed")

    text = target.read_text(encoding="utf-8", errors="replace")

    if args.start is not None or args.end is not None:
        lines = text.splitlines(True)  # keep newlines
        start = 1 if args.start is None else max(1, args.start)
        end = len(lines) if args.end is None else min(len(lines), args.end)
        # Convert to 0-based slice; end inclusive
        text = "".join(lines[start-1:end])

    if len(text) > args.max_chars:
        text = text[:args.max_chars] + "\n[TRUNCATED]"

    print(text, end="")

if __name__ == "__main__":
    main()
