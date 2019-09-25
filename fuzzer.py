#!/usr/bin/env python3
import argparse
import queue
import threading
from urllib.parse import urljoin
import requests


# Walk local directory to create paths, returns list
def get_wordlist(wordlist):

    paths = []

    with open(wordlist, "r") as f:
        for line in f.readlines():
            paths.append(line.strip())

    return paths


# Test if resource exists at target
def fuzz_target(url_queue, headers=None, fail_codes=None, success_codes=None):

    while not url_queue.empty():
        url = url_queue.get()

        # Test if resource exists
        r = requests.get(url, headers=headers)
        code = r.status_code
        if code in fail_codes:
            continue
        if success_codes:
            if code not in success_codes:
                continue

        # Resource exists
        print(f"{url} => [{code}]")


def main():

    target = args.target.strip("/")

    # Read wordlist file into list
    wordlist = get_wordlist(args.wordlist)

    # What we're looking for (and not)
    fail_codes = [int(code) for code in args.blacklist.split(",")]
    success_codes = [int(code) for code in args.whitelist.split(",")]

    # Format URLs to form queue
    url_queue = queue.Queue()
    for word in wordlist:
        url = urljoin(target, word)
        url_queue.put(url)

    # Requests headers
    headers = {
        "user-agent": args.agent,
    }
    
    # Spawn threads
    print("Spawning %d threads..." % args.threads)
    for i in range(args.threads):
        t = threading.Thread(
            target=fuzz_target,
            args=(url_queue, headers, fail_codes, success_codes)
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
        "--blacklist",
        default="404",
        help="Status codes indicating failure, as comma-separated list"
    )
    parser.add_argument(
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
    parser.add_argument(
        "-a",
        "--agent",
        default="Mozilla/5.0",
        help="User-agent"
    )
    args = parser.parse_args()

    main()
