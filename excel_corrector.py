import pandas as pd
from openpyxl import load_workbook

from config import BASE_DATA_LIST_NAME, EXCEL_FILE_NAME, MAIN_DIR


class ExcelCorrector:
    @staticmethod
    def correct_excel(data):
        wb = load_workbook(f'{MAIN_DIR}/{EXCEL_FILE_NAME}.xlsx')
        ws = wb[BASE_DATA_LIST_NAME]

        # удаляем старые данные
        ws.delete_rows(2, ws.max_row)

        # записываем новые
        for row in data.itertuples(index=False):
            ws.append(list(row))

        wb.save(f'{MAIN_DIR}/{EXCEL_FILE_NAME}.xlsx')