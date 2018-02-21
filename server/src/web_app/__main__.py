"""Top-level program for cyber-dojo's repl_runner_python web_app.
"""

import argparse
import logging

from .app import run
from .logging import configure_logging


parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int, default=None,
                    help='The port on which to serve HTTP.')
parser.add_argument('--auto-reload', action='store_true',
                    help='run in auto-reload mode')
parser.add_argument('-v', action='store_true',
                    help='enable verbose logging mode')
parser.add_argument('-vv', action='store_true',
                    help='enable very verbose logging mode')
args = parser.parse_args()

level = logging.INFO if args.v else logging.WARNING
level = logging.DEBUG if args.vv else level
configure_logging(level)

if args.auto_reload:
    import aiohttp_autoreload
    aiohttp_autoreload.start()

run(port=args.port)
