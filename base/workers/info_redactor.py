import pandas as pd

from base.services import redaction


class InfoRedactor:
    @staticmethod
    def redact_info(info_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
        result = []
        for key, df in info_dict.items():
            orders = redaction.correction_dataframe_orders(df, key)
            returns = redaction.correction_dataframe_returns(df, key)
            agg_table = redaction.concat_main_info(orders, returns)
            result.append(agg_table)
        combined_df = pd.concat(result)
        return combined_df


