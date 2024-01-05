# "Date","Price","Open","High","Low","Vol.","Change %"
import csv
import os
from dataclasses import dataclass
from datetime import datetime
from functools import cache

from utils import JSONFile, Log

DIR_DATA = os.path.join('data')
DIR_DATA_RAW = os.path.join(DIR_DATA, 'raw')
DATA_PATH = os.path.join(DIR_DATA, 'data.json')
DATETIME_FORMAT = '%Y-%m-%d'

log = Log('Data')


def parse_float(x):
    x = str(x)
    x = x.replace(',', '')
    x = x.replace('%', '')
    try:
        return float(x)
    except BaseException:
        return 0


@dataclass
class Data:
    date: datetime
    price_close: float
    price_open: float
    price_high: float
    price_low: float
    volume_m: float
    change: float

    def to_dict(self) -> dict:
        return {
            'date': self.date.strftime(DATETIME_FORMAT),
            'price_close': self.price_close,
            'price_open': self.price_open,
            'price_high': self.price_high,
            'price_low': self.price_low,
            'volume_m': self.volume_m,
            'change': self.change,
        }

    @staticmethod
    def from_dict(d: dict) -> 'Data':
        return Data(
            date=datetime.strptime(d['date'], DATETIME_FORMAT),
            price_close=d['price_close'],
            price_open=d['price_open'],
            price_high=d['price_high'],
            price_low=d['price_low'],
            volume_m=d['volume_m'],
            change=d['change'],
        )

    @property
    def year(self) -> datetime:
        return datetime.strptime(self.date.strftime('%Y'), '%Y')

    @property
    def month(self) -> datetime:
        return datetime.strptime(self.date.strftime('%Y-%m'), '%Y-%m')

    @staticmethod
    def group_by(
        data_list: list['Data'], func_data_to_date: callable
    ) -> dict:
        date_to_data = {}
        for data in data_list:
            date = func_data_to_date(data)
            if date not in date_to_data:
                date_to_data[date] = []
            date_to_data[date].append(data)
        return date_to_data

    @staticmethod
    def aggregate(date: datetime, data_list: list['Data']) -> 'Data':
        price_close = data_list[-1].price_close
        price_open = data_list[0].price_open
        price_high = max([d.price_high for d in data_list])
        price_low = min([d.price_low for d in data_list])
        volume_m = sum([d.volume_m for d in data_list])
        change = (price_close - price_open) / price_open
        return Data(
            date=date,
            price_close=price_close,
            price_open=price_open,
            price_high=price_high,
            price_low=price_low,
            volume_m=volume_m,
            change=change,
        )

    @staticmethod
    def list_all_aggr(
        label: str, func_data_to_date: callable
    ) -> list['Data']:
        data_list = Data.list_all()
        date_to_data = Data.group_by(data_list, func_data_to_date)
        aggr_data_list = [
            Data.aggregate(x[0], x[1]) for x in date_to_data.items()
        ]
        path = os.path.join(DIR_DATA, f'data.{label}.json')
        JSONFile(path).write([d.to_dict() for d in aggr_data_list])
        log.info(f'Wrote {len(aggr_data_list)} data to {path}')
        return aggr_data_list

    @staticmethod
    def list_all_nocache() -> list['Data']:
        data_list = []
        for file in os.listdir(DIR_DATA_RAW):
            file_path = os.path.join(DIR_DATA_RAW, file)
            csv_reader = csv.reader(
                open(file_path, newline=''), delimiter=','
            )
            is_header = True
            for row in csv_reader:
                if is_header:
                    is_header = False
                    continue
                (
                    date,
                    price_close,
                    price_open,
                    price_high,
                    price_low,
                    volume_m,
                    change,
                ) = row
                date = datetime.strptime(date, '%m/%d/%Y')
                price_close = parse_float(price_close)
                price_open = parse_float(price_open)
                price_high = parse_float(price_high)
                price_low = parse_float(price_low)
                volume_m = parse_float(volume_m[:-1])
                change = parse_float(change) / 100.0
                data = Data(
                    date,
                    price_close,
                    price_open,
                    price_high,
                    price_low,
                    volume_m,
                    change,
                )
                data_list.append(data)
        data_list = sorted(data_list, key=lambda x: x.date)
        return data_list

    @staticmethod
    @cache
    def list_all() -> list['Data']:
        json_file = JSONFile(DATA_PATH)
        if json_file.exists:
            data_list = [Data.from_dict(d) for d in json_file.read()]
            log.info(f'Read {len(data_list)} data from {DATA_PATH}')
            return data_list

        data_list = Data.list_all_nocache()
        json_file.write([d.to_dict() for d in data_list])
        log.info(f'Wrote {len(data_list)} data to {DATA_PATH}')
        return data_list


if __name__ == '__main__':
    Data.list_all()
    Data.list_all_aggr('by_year', lambda d: d.year)
    Data.list_all_aggr('by_month', lambda d: d.month)
