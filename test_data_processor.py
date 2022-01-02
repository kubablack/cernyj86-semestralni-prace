import pytest
from scraper import DataScraper
from processor import DataProcessor
import pandas as pd
scraper = DataScraper()
raw_df_klima, raw_df_soukr = scraper.stahnout_data_o_pocasi("2021-01-01")
processor = DataProcessor()
df_klima, df_soukr, df = processor.zpracovat_data_o_pocasi(raw_df_klima, raw_df_soukr)
processor.spocitat_vzdalenosti_mezi_obcemi_a_finalizovat_df(df_klima, df_soukr, df)
df = pd.read_csv("data_final/df_2021-01-01.csv")
def test_data_processor_shape():   
    assert df_klima.shape[0] > 0
    assert df_klima.shape[1] > 0
    assert df_soukr.shape[0] > 0
    assert df_soukr.shape[1] > 0

def test_data_processor_NAs(): 
    assert df_klima["kod_obec"].isna().sum() < 5
    assert df_soukr["kod_obec"].isna().sum() < 5
    assert df.loc[:,['Maximální teplota (°C)', 'Minimální teplota (°C)', 'Náraz větru (km/h)', 'Srážky (mm)', 'Sněhová pokrývka (cm)',
            'Sluneční svit (hod)','Nejvyšší tlak (hPa)', 'Nejvyšší vlhkost (%)']].isna().sum().sum() < 5
