__all__ = ['download']

import re
import tempfile
import zipfile
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path

import requests


def _readable_size(size: float):
    if size < 1024:
        result = '{:.2f} B'.format(size)
    elif size < 1024**2:
        result = '{:.2f} KB'.format(size / 1024)
    elif size < 1024**3:
        result = '{:.2f} MB'.format(size / 1024**2)
    else:
        result = '{:.2f} GB'.format(size / 1024**3)

    return result


def _readable_time(delta):
    dt = str(timedelta(seconds=int(delta.total_seconds())))
    return re.sub(r'^0:', '', dt)


class Progress():
    def __init__(self, total_size):
        self.start_at = datetime.utcnow()
        self.total_size = total_size
        self.total_size_readable = _readable_size(total_size)
        self.current_size = 0
        self.count = 0

    def show(self):
        if self.count < 50:
            self.count += 1
            return
        self.count = 0

        time_ = f'{_readable_time(datetime.utcnow() - self.start_at)}'
        pc = '{:.2f}%'.format((self.current_size / self.total_size) * 100)
        size = f'{_readable_size(self.current_size)}/{self.total_size_readable}'

        print(f'\r{time_} | {pc} - {size}    ', end='')

    def update(self, size):
        self.current_size += size


def download(path: Path, token: str):
    url = f'https://www.ip2location.com/download/?token={token}&file=DB3LITEBINIPV6'

    print('\n --- ip2loc --- \n')
    with tempfile.TemporaryFile() as f:

        print('> -- download -- <')
        with closing(requests.get(url, stream=True)) as res:
            progress = Progress(int(res.headers['content-length']))
            for data in res.iter_content(chunk_size=1024 * 4):
                f.write(data)
                progress.update(len(data))
                progress.show()
            progress.show()
            print()

        print('> -- extract -- <')
        f.seek(0)
        with zipfile.ZipFile(f) as z:
            z.extract('IP2LOCATION-LITE-DB3.IPV6.BIN', path=str(path.parent))
    Path(path.parent / 'IP2LOCATION-LITE-DB3.IPV6.BIN').replace(path)

    print('\n --- done --- \n')
