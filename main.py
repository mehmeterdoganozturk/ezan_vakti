#!/usr/bin/env python3
#
# Copyright (c) 2026 Mehmet Erdoğan Öztürk <mehmeterdoganozturk@gmail.com>
# Licensed under the MIT License. See LICENSE in the project root for details.
#
import sys
import os

# Add local package to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ezan_vakti_pro.app import EzanApp

def main():
    app = EzanApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
