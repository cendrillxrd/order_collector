import pandas as pd

df = pd.read_excel('Заказы OZON.xlsx')
print(df['Бренд'].unique())