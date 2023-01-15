from spider.spider import main_spider
import argparse
import configparser
from pathlib import Path
import sys
from dateutil.parser import parse

ARQ_INIT = Path() / "config.init"
VERSION_CLI = 'HUNGER RUSH VERSION CLI 0.1'


if __name__ == '__main__':
    if not ARQ_INIT.is_file():
        print(f"[ERRO] Arquivo '{ARQ_INIT}' nao encontrador !")
        sys.exit()

    config = configparser.ConfigParser()
    config.read(ARQ_INIT)
    
    login = config['SESSION']['Login']
    password = config['SESSION']['Password']
    url = config['SESSION']['Url']

    parser = argparse.ArgumentParser(
        prog="HUNGER RUSH",
        description="Download the .csv files",
        epilog="Des. Marcus Holanda"
    )

    parser.version = VERSION_CLI
    parser.add_argument('-v', '--version', action="version")
    parser.add_argument('-d', '--date', help="initial date", type=str, required=True)
    parser.add_argument('-p', '--period', help="execution period", type=int)

    args = parser.parse_args()

    if args.date:
        dias = args.period if args.period else 1

        main_spider(args.date, dias, login, password, url)
