from spider.spider import main_spider
import argparse
import configparser
from pathlib import Path
import sys
from datetime import datetime


ARQ_INIT = Path() / "config.init"
VERSION_CLI = 'HUNGER RUSH VERSION CLI 0.1'


if __name__ == '__main__':
    if not ARQ_INIT.is_file():
        print(f"[ERR] File '{ARQ_INIT}' not found !")
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
    parser.add_argument('-d', '--date', help="initial date", type=lambda d: datetime.strptime(d, "%Y-%m-%d"), required=True)
    parser.add_argument('-p', '--period', help="execution period", type=int)
    parser.add_argument('-i', '--invisible', help="show or hide browser op: [F | T]", type=str)
    
    try:

        args = parser.parse_args()

    except Exception:

        parser.print_help()

    else:
        try:
            if args.date:
                dias = args.period if args.period else 7
                flag_inv = args.invisible if args.invisible else "F"
                invisible = True if flag_inv.upper()[0] == 'T' else False

                print(f"Initial date -d: {args.date}")
                print(f"Period days -p: {dias}")
                print(f"Invisible browser ? -i: {invisible}")

                main_spider(args.date, dias, login, password, url, invisible)
        except Exception as e:
            print(e)
