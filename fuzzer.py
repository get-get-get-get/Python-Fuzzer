#!/usr/bin/env python3
import argparse
import os
import queue
import threading
import requests


# Walk local directory to create paths, returns list
def get_wordlist(wordlist, filters=None):

    paths = []

    with open(wordlist, "r") as f:
        for line in f.readlines():
            paths.append(line.strip())

    return paths


def test_remote(url_queue, fail_codes=None, success_codes=None):

    while not url_queue.empty():
        url = url_queue.get()

        # Test if resource exists
        r = requests.get(url)
        code = r.status_code
        if code in fail_codes:
            continue
        if success_codes:
            if code not in success_codes:
                continue

        # Resource exists
        print(f"[{code}] => {url}")


def main():

    target = args.target.strip("/")

    # Read wordlist file into list
    wordlist = get_wordlist(args.wordlistwordlist, filters)

    # What we're looking for (and not)
    filters = [ext.strip(".") for ext in args.filters.split(",")]
    fail_codes = [int(code) for code in args.blacklist.split(",")]
    success_codes = [int(code) for code in args.whitelist.split(",")]

    # Format URLs to form queue
    url_queue = queue.Queue()
    for word in wordlist:
        url_queue.put(f"{target}{path}")

    # Spawn threads
    print("Spawning %d threads..." % args.threads)
    for i in range(args.threads):
        t = threading.Thread(
            target=test_remote,
            args=(url_queue, fail_codes, success_codes)
        )
        t.start()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "target",
        help="Base URL of target to fuzz"
    )
    parser.add_argument(
        "-w",
        "--wordlist",
        required=True,
        help="Path to wordlist"
    )
    parser.add_argument(
        "-f",
        "--filters",
        default="jpg,gif,png,css",
        help="Extensions to exclude as comma-separated list"
    )
    parser.add_argument(
        "-cB",
        "--blacklist",
        default="404",
        help="Status codes indicating failure, as comma-separated list"
    )
    parser.add_argument(
        "-cW",
        "--whitelist",
        default="200,301,302,401,403",
        help="Status codes indicating success, as comma-separated list"
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=10,
        help="Request threads"
    )
    args = parser.parse_args()

    main()
