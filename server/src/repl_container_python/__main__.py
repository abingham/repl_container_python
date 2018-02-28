"""Top-level program for cyber-dojo's repl_runner_python web_app.
"""

import argparse
import logging

from .app import create_app


parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int, default=None,
                    help='The port on which to serve HTTP.')
parser.add_argument('--host', type=str, default=None,
                    help='The host on which to server HTTP.')
parser.add_argument('-v', action='store_true',
                    help='enable verbose logging mode')
parser.add_argument('-vv', action='store_true',
                    help='enable very verbose logging mode')
args = parser.parse_args()

level = logging.INFO if args.v else logging.WARNING
level = logging.DEBUG if args.vv else level

app = create_app(log_level=level)
app.run(host=args.host, port=args.port)
