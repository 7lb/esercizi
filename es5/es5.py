#! /usr/bin/python
#-*- coding:utf-8 -*-

import argparse
import urlparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The url of the webpage to download")
    parser.parse_args()


def validate(url):
    valid_schemes = ["http", "https"]
    parse_res = urlparse.urlparse(url)
    if parse_res.scheme in valid_schemes:
        return True
    return False


if __name__ == "__main__":
    main()
