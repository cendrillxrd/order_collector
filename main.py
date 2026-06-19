import pandas as pd

from base.base_main import base_main
from lamoda.lamoda_main import lamoda_main
from ozon.ozon_main import ozon_main
from wb.wb_main import wb_main
from excel_corrector import ExcelCorrector
from yandex.yandex_main import yandex_main


def main():
    base_info = base_main()
    lamoda_info = lamoda_main(False)
    ozon_info = ozon_main(True)
    wb_info = wb_main(False)
    yandex_info = yandex_main(False)

    result = pd.concat([ozon_info, wb_info, yandex_info, lamoda_info, base_info])
    excel_corrector = ExcelCorrector()
    excel_corrector.correct_excel(result)

if __name__ == '__main__':
    main()
