import pandas as pd
import numpy as np
import sqlite3
from datetime import date

class JGBScraping(object):

    """
    A class for generating "clean" dataset of Japanese Government Bonds(JGB) yield.
    Using historical JGB yield data published in Ministry of Finance Japan site.
    http://www.mof.go.jp/jgbs/reference/interest_rate/index.htm
    """

    def __init__(self):
        self.url_historical = 'http://www.mof.go.jp/jgbs/reference/interest_rate/data/jgbcm_all.csv'
        self.url_current = 'http://www.mof.go.jp/jgbs/reference/interest_rate/jgbcm.csv'
        self.columns = ['date', 'JGB_1Y', 'JGB_2Y', 'JGB_3Y', 'JGB_4Y', 'JGB_5Y',\
         'JGB_6Y', 'JGB_7Y', 'JGB_8Y', 'JGB_9Y', 'JGB_10Y', 'JGB_15Y', 'JGB_20Y',\
          'JGB_25Y', 'JGB_30Y', 'JGB_40Y']

    def convertDate(self, data):
        # A function to convert "wareki" date into "seireki" date
        for d in data:
            d = d.split('.')
            if d[0][0] == 'H':
                yield date(1988+int(d[0][1:]), int(d[1]), int(d[2]))
            else:
                yield date(1925+int(d[0][1:]), int(d[1]), int(d[2]))

    def getData(self, url):
        # Load dataset
        _df = pd.read_csv(url)

        # Set columns
        _df.columns = self.columns

        # Drop NA
        _df = _df.ix[1:,:]
        _df = _df.dropna()

        # Set 'date' coulmn as index
        _df.index = self.convertDate(_df['date'])

        # Replace '-' as numpy nan
        _df = _df.replace('-',np.nan)

        # Drop 'date' column
        _df = _df.drop('date', axis=1)

        return _df

    def getAllData(self):
        # Get current & historical datasets.
        df_hist = self.getData(self.url_historical)
        df_curr = self.getData(self.url_current)

        # Concat current & historical datasets
        df = pd.concat([df_hist, df_curr])

        # Save csv
        df.to_csv('data.csv')

        # Save sql database
        conn = sqlite3.connect("data.db")
        df.to_sql('data', conn, if_exists='replace')

        print(df)

        return df

    def updateData(self):
        # Connect with database
        conn = sqlite3.connect("data.db")

        # Load current dataset
        df = pd.read_sql('select * from data', conn)
        df.index = df['index']
        df = df.drop('index', axis=1)

        # Get new dataset
        df_new = self.getData(self.url_current)

        # Concat current & new datasets
        df = pd.concat([df, df_new])

        # Save csv
        df.to_csv('data.csv')

        # Save sql database
        conn = sqlite3.connect("data.db")
        df.to_sql('data', conn, if_exists='replace')

        print(df)

        return df

if __name__ == '__main__':
    # test
    jgb =JGBScraping()
    jgb.getAllData()
    jgb.updateData()