from pathlib import Path
from shutil import rmtree


def load_config(config, report: str):
    if report == 'qu':
        session = 'SESSION_QU'
    elif report == 'rush' or report == 'sales':
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
    elif report == 'sales':
        arq = Path() / 'download_sales'


    if arq.is_dir():
        rmtree(arq, ignore_errors=True)