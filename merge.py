from contextlib import contextmanager
import json
from pathlib import Path
import os
import shutil
import datetime as dt
from rich.console import Console

console = Console()

big_result_json = {}


def backup():
    p = Path('./data/production.json')
    if p.exists():
        backup_file = f'./local/backup_{dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'
        shutil.copy(p, backup_file)
        console.print(f"Backup file created: {backup_file}")
    else:
        console.print("[red]Error: No production.json file found.")


@contextmanager
def edit_big_json():
    global big_result_json
    backup()
    console.print('Loading production.json file...')
    with open('./data/production.json', 'r', encoding='utf-8') as f:
        big_result_json = json.load(f)
    yield
    date = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(f'./local/production_{date}.json', 'w', encoding='utf-8') as f:
        json.dump(big_result_json, f, ensure_ascii=False, indent=4)
    console.print(f'Saved local production file: production_{date}.json')


def merge_one_json(exported_json: dict, order: int = 0) -> None:
    dates = [i['date'] for i in big_result_json['list']]
    # sort_dates = sorted(dates)
    # earlest_date = dt.datetime.strptime(sort_dates[0], '%Y-%m-%d')
    min_date = min(dates)
    earlest_date = dt.datetime.strptime(min_date, '%Y-%m-%d')

    for data in exported_json['data']:
        date = data['create_timestamp']
        parsed_date = dt.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        # card = data['car_license_no']
        card = data.get('car_license_no', '')

        if not card:
            console.print(
                "[yellow]Skipping data with no card number. Skipping...")
            continue

        if parsed_date > earlest_date:
            console.print(
                "[yellow]Importing data that is older than the production data. Skipping...")
            continue
        console.print(
            f"Merging data for card [green]{card[-4:]}[/green] on [blue]{date}[/blue]")
        obj = {
            "no": card[-4:],
            "date": parsed_date.strftime('%Y-%m-%d'),
            "note": f"merge from {order}"
        }
        big_result_json['list'].append(obj)


def sort_big_json() -> None:
    big_result_json['list'] = sorted(
        big_result_json['list'], key=lambda x: x['date'])


def merge_file() -> None:
    files = [
        Path('./local/orderList1.json'),
        Path('./local/orderList2.json'),
        Path('./local/orderList3.json')
    ]
    with edit_big_json():
        for idx, file in enumerate(files):
            # merge_one_json()
            with open(file, 'r', encoding='utf-8') as f:
                exported_json = json.load(f)
            merge_one_json(exported_json, order=idx+1)
        sort_big_json()


def main():
    merge_file()


if __name__ == '__main__':
    main()
