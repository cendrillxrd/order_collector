import pandas as pd

from base.config import BASE_MAIN_COLUMNS_NAME
from base.dto.all_agg_info_dto import AllAggInfoColumnsDTO
from base.dto.columns_main_dto import ColumnsBaseDTO
from base.utils.date_helper import filter_until_last_sunday

df_columns = ColumnsBaseDTO()
agg_columns = AllAggInfoColumnsDTO()

def correction_dataframe_orders(df: pd.DataFrame, project_name: str) -> pd.DataFrame:
    df[df_columns.create_at] = pd.to_datetime(
        df[df_columns.order_date].str.split().str[0],
        format='%d.%m.%Y',
        errors='coerce'
    )
    df.rename({'Номенклатура.Фирма производитель': df_columns.brand}, axis=1, inplace=True)
    df[df_columns.brand] = df[df_columns.brand].replace('Marc Cony', 'MARC CONY')
    df[df_columns.order_sum] = df[df_columns.order_sum].fillna(0)

    df[agg_columns.market] = project_name
    df[agg_columns.year] = df[df_columns.create_at].dt.year
    df[agg_columns.month] =df[df_columns.create_at].dt.month
    df[agg_columns.week] = df[df_columns.create_at].dt.isocalendar().week

    df['canceled_price'] = -df[df_columns.order_sum].where(
        df[df_columns.order_is_canceled].notna(), 0)

    grouped = df.groupby([agg_columns.market, agg_columns.year,
                              agg_columns.month, agg_columns.week,
                              agg_columns.brand]).agg(
        sum_orders=(df_columns.order_sum, 'sum'),
        total_orders=(df_columns.quantity, 'sum'),
        returned=(df_columns.order_is_canceled, lambda x: x[x.notna()].count()),
        total_main_orders=(df_columns.order_id, 'nunique'),
        returned_sum=('canceled_price', 'sum'),
    ).reset_index()

    columns_name = [column for column in grouped.columns if column in BASE_MAIN_COLUMNS_NAME]

    columns_rename = {k: BASE_MAIN_COLUMNS_NAME.get(k) for k in columns_name}
    grouped.rename(columns_rename,
                   inplace=True,
                   axis=1)
    return grouped

def correction_dataframe_returns(df: pd.DataFrame, project_name: str) -> pd.DataFrame:
    df[df_columns.returned_at] = pd.to_datetime(
        df[df_columns.returned_date].str.split().str[0],
        format='%d.%m.%Y',
        errors='coerce'
    )
    df.rename({'Номенклатура.Фирма производитель': df_columns.brand}, axis=1, inplace=True)
    df[df_columns.brand] = df[df_columns.brand].replace('Marc Cony', 'MARC CONY')
    df[df_columns.order_sum] = df[df_columns.order_sum].fillna(0)

    df = filter_until_last_sunday(df, df_columns.returned_at)

    df[agg_columns.market] = project_name
    df[agg_columns.year] = df[df_columns.returned_at].dt.year
    df[agg_columns.month] =df[df_columns.returned_at].dt.month
    df[agg_columns.week] = df[df_columns.returned_at].dt.isocalendar().week

    df['canceled_price'] = -df[df_columns.return_sum].where(
        df[df_columns.doc_return].notna(), 0)

    grouped = df.groupby([agg_columns.market, agg_columns.year,
                              agg_columns.month, agg_columns.week,
                              agg_columns.brand]).agg(
        returned=(df_columns.doc_return, lambda x: x[x.notna()].count()),
        returned_sum=('canceled_price', 'sum'),
    ).reset_index()

    columns_name = [column for column in grouped.columns if column in BASE_MAIN_COLUMNS_NAME]

    columns_rename = {k: BASE_MAIN_COLUMNS_NAME.get(k) for k in columns_name}
    grouped.rename(columns_rename,
                   inplace=True,
                   axis=1)
    return grouped

def concat_main_info(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    merge_on = [agg_columns.market, agg_columns.year, agg_columns.month,
                agg_columns.week, agg_columns.brand]
    merged = pd.concat([df1, df2]).groupby(merge_on, as_index=False).sum()
    return merged