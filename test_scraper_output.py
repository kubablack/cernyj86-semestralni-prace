import pytest
from scraper import DataScraper
scraper = DataScraper()
raw_df_klima, raw_df_soukr = scraper.stahnout_data_o_pocasi("2021-01-01") 

def test_scraper_output():
       
    assert raw_df_klima.shape[0] > 0
    assert raw_df_klima.shape[1] > 0
    assert raw_df_soukr.shape[0] > 0
    assert raw_df_soukr.shape[1] > 0
