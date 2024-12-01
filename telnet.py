import os
import subprocess
import time
from typing import IO


class TelenetConnection:
    def __init__(self, auth_token: str | None = None, host: str = 'localhost', port=5554, logfile=None):
        if auth_token is None:
            auth_token = open(
                os.path.expanduser('~/.emulator_console_auth_token')
            ).read().strip()

        self._logfile = logfile
        self._pipe = subprocess.Popen(
            ['telnet', host, str(port)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        self.read_until_ok()
            
        time.sleep(0.5)
        self.write('auth ' + auth_token)
        self.check_ok(1)
        time.sleep(0.3)

    def log(self, s):
        if self._logfile is not None:
            print(s, file=self._logfile)

    def _get_input(self) -> IO:
        assert self._pipe is not None
        assert self._pipe.stdin is not None
        return self._pipe.stdin

    def _get_output(self) -> IO:
        assert self._pipe is not None
        assert self._pipe.stdout is not None
        return self._pipe.stdout

    def readline(self) -> str:
        assert self._pipe is not None
        s = self._get_output().readline().decode()[:-1]
        self.log('> ' + s)
        return s

    def write(self, s: str):
        self.log('< ' + s)
        self._get_input().write((s + '\n').encode())
        self._get_input().flush()

    def read_until_ok(self):
        while True:
            s = self.readline()
            if s == 'OK':
                break

    def check_ok(self, skip_lines_cnt=0):
        for _ in range(skip_lines_cnt):
            self.readline()

        s = self.readline()
        assert s == 'OK'
