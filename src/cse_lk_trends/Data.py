# "Date","Price","Open","High","Low","Vol.","Change %"
import csv
import os
from dataclasses import dataclass
from datetime import datetime
from functools import cache, cached_property

from utils import JSONFile, Log

DATETIME_FORMAT = '%Y-%m-%d'

log = Log('Data')

DIR_DATA = os.path.join('data')
DIR_DATA_RAW = os.path.join(DIR_DATA, 'raw')


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
    date_start: datetime
    date_end: datetime
    price_close: float
    price_open: float
    price_high: float
    price_low: float
    volume_m: float

    def to_dict(self) -> dict:
        return {
            'date_start': self.date_start.strftime(DATETIME_FORMAT),
            'date_end': self.date_end.strftime(DATETIME_FORMAT),
            'price_close': self.price_close,
            'price_open': self.price_open,
            'price_high': self.price_high,
            'price_low': self.price_low,
            'volume_m': self.volume_m,
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            date_start=datetime.strptime(d['date_start'], DATETIME_FORMAT),
            date_end=datetime.strptime(d['date_end'], DATETIME_FORMAT),
            price_close=d['price_close'],
            price_open=d['price_open'],
            price_high=d['price_high'],
            price_low=d['price_low'],
            volume_m=d['volume_m'],
        )

    @cached_property
    def year(self) -> datetime:
        return datetime.strptime(self.date_start.strftime('%Y'), '%Y')

    @cached_property
    def month(self) -> datetime:
        return datetime.strptime(self.date_start.strftime('%Y-%m'), '%Y-%m')

    @cached_property
    def date_str(self) -> str:
        date_format = '%Y%b%d'
        date_str_start = self.date_start.strftime(date_format)
        date_str_end = self.date_end.strftime(date_format)
        n = len(date_str_start)
        for i in range(n, 0, -1):
            if date_str_start[:i] == date_str_end[:i]:
                return date_str_start[:i][2:].upper()
        return ''

    @cached_property
    def change(self) -> float:
        return (self.price_close - self.price_open) / self.price_open

    @staticmethod
    def group_by(data_list: list, func_data_to_date: callable) -> dict:
        date_to_data = {}
        for data in data_list:
            date = func_data_to_date(data)
            if date not in date_to_data:
                date_to_data[date] = []
            date_to_data[date].append(data)
        return date_to_data

    @classmethod
    def aggregate(cls, data_list: list):
        data_list = sorted(data_list, key=lambda x: x.date_start)
        date_start = data_list[0].date_start
        date_end = data_list[-1].date_end
        price_close = data_list[-1].price_close
        price_open = data_list[0].price_open
        price_high = max([d.price_high for d in data_list])
        price_low = min([d.price_low for d in data_list])
        volume_m = sum([d.volume_m for d in data_list])

        return cls(
            date_start=date_start,
            date_end=date_end,
            price_close=price_close,
            price_open=price_open,
            price_high=price_high,
            price_low=price_low,
            volume_m=volume_m,
        )

    @classmethod
    def get_id(cls) -> str:
        raise NotImplementedError

    @classmethod
    def list_all_nocache(cls) -> list:
        data_list = []
        for file in os.listdir(DIR_DATA_RAW):
            if not file.startswith(cls.get_id()):
                continue
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
                    ___,  # change
                ) = row
                date = datetime.strptime(date, '%m/%d/%Y')
                price_close = parse_float(price_close)
                price_open = parse_float(price_open)
                price_high = parse_float(price_high)
                price_low = parse_float(price_low)
                volume_m = parse_float(volume_m[:-1])
                data = cls(
                    date,  # date_start
                    date,  # date_end
                    price_close,
                    price_open,
                    price_high,
                    price_low,
                    volume_m,
                )
                data_list.append(data)
        data_list = sorted(data_list, key=lambda x: x.date_start)
        return data_list

    @classmethod
    def get_data_path(cls) -> str:
        return os.path.join(DIR_DATA, f'{cls.get_id()}.data.json')

    @classmethod
    @cache
    def list_all(cls) -> list:
        data_path = cls.get_data_path()
        json_file = JSONFile(data_path)
        if json_file.exists:
            data_list = [cls.from_dict(d) for d in json_file.read()]
            log.info(f'Read {len(data_list)} data from {data_path}')
            return data_list

        data_list = cls.list_all_nocache()
        json_file.write([d.to_dict() for d in data_list])
        log.info(f'Wrote {len(data_list)} data to {data_path}')
        return data_list

    @classmethod
    @cache
    def list_all_aggr(cls, func_data_to_date: callable) -> list:
        data_list = cls.list_all()
        date_to_data = cls.group_by(data_list, func_data_to_date)
        aggr_data_list = [cls.aggregate(x[1]) for x in date_to_data.items()]
        return aggr_data_list

    @classmethod
    @cache
    def idx_by_date(cls) -> dict:
        data_list = cls.list_all()
        return {d.date_start: d for d in data_list}
