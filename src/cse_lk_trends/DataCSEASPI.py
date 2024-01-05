from cse_lk_trends.Data import Data


class DataCSEASPI(Data):
    @classmethod
    def get_id(cls) -> str:
        return 'cse-aspi'
