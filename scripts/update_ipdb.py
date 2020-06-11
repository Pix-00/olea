import datetime
import re
import sys
import tempfile
import zipfile
from contextlib import closing
from pathlib import Path

import requests


def readable_size(size: float):
    if size < 1024:
        result = '{:.2f} B'.format(size)
    elif size < 1024**2:
        result = '{:.2f} KB'.format(size / 1024)
    elif size < 1024**3:
        result = '{:.2f} MB'.format(size / 1024**2)
    else:
        result = '{:.2f} GB'.format(size / 1024**3)

    return result


def readable_time(timedelta):
    dt = str(timedelta)
    return re.sub(r'^0:', '', dt)


class Progress():
    def __init__(self, total_size):
        self.start_at = datetime.datetime.utcnow()
        self.total_size = total_size
        self.total_size_readable = readable_size(total_size)
        self.current_size = 0

    def show(self):
        time_ = f'{readable_time(datetime.datetime.utcnow() - self.start_at)}'
        pc = '{:.2f}%'.format((self.current_size / self.total_size) * 100)
        size = f'{readable_size(self.current_size)}/{self.total_size_readable}'

        print(f'\r{time_} | {pc} - {size}    ', end='')

    def update(self, size):
        self.current_size += size


def download(token: str, path: Path):
    url = f'https://www.ip2location.com/download/?token={token}&file=DB3LITEBINIPV6'

    with tempfile.TemporaryFile() as f:
        print('> -- download -- <')
        with closing(requests.get(url, stream=True)) as res:
            i = 0
            progress = Progress(int(res.headers['content-length']))
            for data in res.iter_content(chunk_size=1024 * 4):
                f.write(data)
                progress.update(len(data))
                if i == 50:
                    i = 0
                    progress.show()
                else:
                    i += 1
            progress.show()
            print()

        print('> -- extract -- <')
        f.seek(0)
        with zipfile.ZipFile(f) as z:
            z.extract('IP2LOCATION-LITE-DB3.IPV6.BIN', path=path.parent)

    print('> -- rename -- <')
    path.unlink()
    Path(path.parent / 'IP2LOCATION-LITE-DB3.IPV6.BIN').rename(path)


if __name__ == '__main__':
    sys.path.append(str(Path(__file__).parents[1]))
    from config.default import IPDB_PATH
    from config.instance import IP2LOC_DOWNLOAD_TOKEN

    download(IP2LOC_DOWNLOAD_TOKEN, IPDB_PATH)