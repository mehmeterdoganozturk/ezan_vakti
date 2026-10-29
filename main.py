#!/usr/bin/env python3
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
