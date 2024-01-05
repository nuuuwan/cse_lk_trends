from datetime import datetime
from functools import cached_property

from cse_lk_trends.Data import Data
from cse_lk_trends.DataUSDLKR import DataUSDLKR


class DataCSEASPI(Data):
    @classmethod
    def get_id(cls) -> str:
        return 'cse-aspi'

    @cached_property
    def date_start_usd_lkr(self) -> datetime:
        idx = DataUSDLKR.idx_by_date()
        return idx[self.date_start].price_close

    @cached_property
    def date_end_usd_lkr(self) -> datetime:
        idx = DataUSDLKR.idx_by_date()
        return idx[self.date_end].price_close

    @cached_property
    def price_close_usd(self) -> float:
        return self.price_close / self.date_end_usd_lkr

    @cached_property
    def price_open_usd(self) -> float:
        return self.price_open / self.date_start_usd_lkr

    @cached_property
    def change_usd(self) -> float:
        return (
            self.price_close_usd - self.price_open_usd
        ) / self.price_open_usd
