#!/usr/bin/env python
#coding: utf-8

import argparse

listvars = {
    "all": {
        "hosts": ["127.0.0.1","127.0.0.2","127.0.0.3","127.0.0.4"]
        }
}
hostvars = {
    "_meta": {
        "hostvars": {
            "127.0.0.1": {
                "x" : 1
            },
            "127.0.0.2": {
                "x": 2
            },
            "127.0.0.3": {
                "x": 3
            },
            "127.0.0.4": {
                "x": 4
            }
        }
    }
}

parser = argparse.ArgumentParser()
parser.add_argument("--list", help="list host", action="store_true")
parser.add_argument("--host", type=str, help="increase output verbosity")
args = parser.parse_args()


if __name__ == '__main__':
    if args.list:
        print listvars
    elif args.host:
        print hostvars['_meta']['hostvars'][args.host]
    else:
        print 'error'
        sys.exit(1)
