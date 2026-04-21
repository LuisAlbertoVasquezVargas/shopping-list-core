# core/logger.py

import sys

class Logger:
    @staticmethod
    def info(msg):
        print(f"[\033[94mINFO\033[0m] {msg}")

    @staticmethod
    def brain(action, value):
        print(f"[\033[95mBRAIN\033[0m] Action: {action} | Value: {value}")

    @staticmethod
    def error(ctx, msg):
        print(f"[\033[91mERROR\033[0m] {ctx}: {msg}", file=sys.stderr)

    @staticmethod
    def server(model, port=8000):
        print(f"--- Shopping List Core ---")
        print(f"[\033[92mREADY\033[0m] http://localhost:{port} | Model: {model}")
