from spider.spider import main_spider
from spider.spider_qu import SpiderQu
import argparse
import configparser
from pathlib import Path
import sys
from datetime import datetime
from utils.utils import del_download, load_config


ARQ_INIT = Path() / "config.init"
VERSION_CLI = 'HUNGER RUSH VERSION CLI 0.2'


if __name__ == '__main__':
    if not ARQ_INIT.is_file():
        print(f"[ERR] File '{ARQ_INIT}' not found !")
        sys.exit()

    config = configparser.ConfigParser()
    config.read(ARQ_INIT)

    parser = argparse.ArgumentParser(
        prog="HUNGER RUSH",
        description="Download the .csv, .xlsx files",
        epilog="Des. Marcus Holanda",
        fromfile_prefix_chars="_"
    )

    parser.version = VERSION_CLI
    parser.add_argument('-v', '--version', action="version")

    parser.add_argument('report', help='select web report[rush, qu]', choices=['rush', 'qu'])
    parser.add_argument('-s', '--startdate', help="initial date", type=lambda d: datetime.strptime(d, "%Y-%m-%d"), required=True)
    parser.add_argument('-e', '--enddate', help="final date", type=lambda d: datetime.strptime(d, "%Y-%m-%d"), required=True)
    parser.add_argument('-i', '--invisible', help="show or hide browser", action="store_true")
    parser.add_argument('-r', '--remove', help="delete downloaded files", action='store_true')
    
    try:

        args = parser.parse_args()

    except Exception:

        parser.print_help()
        sys.exit()

    else:
        try:
            
            print(f'Reports: {args.report.upper()}\n')
            print(f"Initial date        -s: {args.startdate}")
            print(f"Final date          -e: {args.enddate}")
            print(f"Invisible browser ? -i: {args.invisible}")
            print(f"Delete files ?      -r: {args.remove}")
            
            session = load_config(config=config, report=args.report)

            if args.remove:
                del_download(report=args.report)
            
            if args.report == 'qu':
                period = (args.enddate - args.startdate).days

                if period > 31:
                    raise ValueError(f"\n[ERR] Days {period} > 31")

                SpiderQu(
                    url=session['url'],
                    implicitly_wait=30.0,
                    login=session['login'],
                    password=session['password'],
                    date_start=args.startdate,
                    date_end=args.enddate,
                    invisible=args.invisible
                ).run()

            elif args.report == 'rush':
                period = (args.enddate - args.startdate).days + 1

                main_spider(args.startdate, period, session['login'], session['password'], session['url'], args.invisible)

        except Exception as e:

            print(e)
            sys.exit()