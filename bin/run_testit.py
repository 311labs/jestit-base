#!/usr/bin/env python

import paths
paths.load_apps()
from testit import runner


if __name__ == "__main__":
    runner.main(runner.setup_parser())
