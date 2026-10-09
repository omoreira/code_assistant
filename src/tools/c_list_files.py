#!/usr/bin/env python3
import argparse, os, pathlib, fnmatch

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", default="*")
    ap.add_argument("--max_results", type=int, default=200)
    args = ap.parse_args()

    root = pathlib.Path(os.getcwd()).resolve()

    results = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if fnmatch.fnmatch(str(rel), args.pattern):
            results.append(str(rel))
        if len(results) >= args.max_results:
            break

    for r in results:
        print(r)

if __name__ == "__main__":
    main()
