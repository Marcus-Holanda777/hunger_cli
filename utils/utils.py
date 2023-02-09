from pathlib import Path
from shutil import rmtree


def load_config(config, report: str):
    if report == 'qu':
        session = 'SESSION_QU'
    elif report == 'rush':
        session = 'SESSION'

    log = {
        'login': config[session]['Login'], 
        'password': config[session]['Password'],
        'url': config[session]['Url']
    }

    return log


def del_download(report: str):
    if report == 'qu':
        arq = Path() / 'download_qu'
    elif report == 'rush':
        arq = Path() / 'download'

    if arq.is_dir():
        rmtree(arq, ignore_errors=True)