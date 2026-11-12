"""Find duplicate files by size and content hash."""

import argparse
import hashlib
from collections import defaultdict
from pathlib import Path

CHUNK = 65536


def file_md5(path):
    digest = hashlib.md5()
    with path.open("rb") as fh:
        while True:
            block = fh.read(CHUNK)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def scan(root):
    by_size = defaultdict(list)
    for path in root.rglob("*"):
        if path.is_file():
            by_size[path.stat().st_size].append(path)
    groups = []
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        by_hash = defaultdict(list)
        for path in paths:
            by_hash[file_md5(path)].append(path)
        for digest, dupes in by_hash.items():
            if len(dupes) > 1:
                groups.append(dupes)
    return groups


def main():
    parser = argparse.ArgumentParser(description="find duplicate files")
    parser.add_argument("directory", nargs="?", default=".", help="root to scan")
    args = parser.parse_args()
    root = Path(args.directory)
    if not root.is_dir():
        print(f"error: {args.directory} is not a directory")
        return 1
    groups = scan(root)
    print(f"found {len(groups)} duplicate group(s)")
    for group in groups:
        print("  " + " == ".join(str(p) for p in group))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

