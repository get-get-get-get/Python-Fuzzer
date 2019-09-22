#!/usr/bin/env python3
import argparse



def main():




if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "positional",
        help=""
    )
    args = parser.parse_args()

    main()
