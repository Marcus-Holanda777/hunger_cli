from pathlib import Path
from shutil import rmtree


def del_download():
    arq = Path() / 'download'
    if arq.is_dir():
        rmtree(arq, ignore_errors=True)