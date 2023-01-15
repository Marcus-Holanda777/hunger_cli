from spider.spider import main_spider
import argparse
import configparser
from pathlib import Path
import sys
from datetime import datetime
from utils.utils import del_download


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
        epilog="Des. Marcus Holanda",
        fromfile_prefix_chars="_"
    )

    parser.version = VERSION_CLI
    parser.add_argument('-v', '--version', action="version")
    parser.add_argument('-d', '--date', help="initial date", type=lambda d: datetime.strptime(d, "%Y-%m-%d"), required=True)
    parser.add_argument('-p', '--period', help="execution period", type=int, default=1)
    parser.add_argument('-i', '--invisible', help="show or hide browser", action="store_true")
    parser.add_argument('-r', '--remove', help="delete downloaded files", action='store_true')
    
    try:

        args = parser.parse_args()

    except Exception:

        parser.print_help()
        sys.exit()

    else:
        try:

            print(f"Initial date        -d: {args.date}")
            print(f"Period days         -p: {args.period}")
            print(f"Invisible browser ? -i: {args.invisible}")
            print(f"Delete files ?      -r: {args.remove}")

            if args.remove:
                del_download()

            main_spider(args.date, args.period, login, password, url, args.invisible)

        except Exception as e:

            print(e)
            sys.exit()