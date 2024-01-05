from cse_lk_trends.Data import Data


class DataUSDLKR(Data):
    @classmethod
    def get_id(cls) -> str:
        return 'usd-lkr'
