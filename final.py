from scraper import DataScraper
from processor import DataProcessor

scraper = DataScraper()
raw_df_klima, raw_df_soukr = scraper.stahnout_data_o_pocasi("2021-10-08")

processor = DataProcessor()
df_klima, df_soukr, df = processor.zpracovat_data_o_pocasi(raw_df_klima, raw_df_soukr)

processor.spocitat_vzdalenosti_mezi_obcemi_a_finalizovat_df(df_klima, df_soukr, df)
