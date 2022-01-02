'''
Modul, který stáhne data o počasí.
'''
import requests
from bs4 import BeautifulSoup
import pandas as pd

class DataScraper:
    '''
    Třída, která stáhne data.
    '''
    def __init__(self):
        self.initialized = True

    def stahnout_data_o_pocasi(self, datum = "2021-10-08"):
        # vytvoříme si slovník s kraji a jejich labely, které jim web přiřadil
        link = 'https://www.in-pocasi.cz/archiv/archiv.php?historie=2021-10-08&region=1'
        raw = requests.get(link).content
        soup = BeautifulSoup(raw, 'html.parser')
        labels = []
        names = []
        for region in soup.find("select", {"name": "archiv_kraj"}).findAll("option"):
            labels.append(region["value"])

            if region.text == "Praha":
                name = "Hlavní město Praha"
            elif region.text == "Vysočina":
                name = "Kraj Vysočina"
            else: name = region.text + " kraj"
            names.append(name)
        regions = dict(zip(labels, names))

        # web obsahuje dva typy meteor. stanic a každý má trochu jiné měřené hodnoty, proto ze začátku vytvoříme 2 datasety
        list_klimaticke_stanice = []
        list_soukrome_stanice = []
        date = datum
        for region_label in list(regions.keys()): # projdeme všechny kraje

            link = f'https://www.in-pocasi.cz/archiv/archiv.php?historie={date}&region={region_label}'
            raw = requests.get(link).content
            soup = BeautifulSoup(raw, 'html.parser') # uložíme zdrojový kód
            soup_tables = soup.find('div',{'class':'typography'}).findAll("tbody") # tabulky s daty

            for table_type, table in enumerate(soup_tables):
                soup_rows = table.findAll("tr")

                for row in soup_rows:
                    data = [] # list na data z konkrétní stanice                   
                    for element in row.findAll("td"): # přiřazujeme všechny hodnoty
                        data.append(element.text)
                    data.append(regions[region_label]) # přiřadíme kraj
                    data.append(date) #přiřadíme datum
                    data.append(row.findAll("td")[0].find("a")["href"]) # uložíme si odkaz na meteor. stanici
                    if table_type == 0: # přidáme do příslušného listu
                        list_klimaticke_stanice.append(data)
                    else: list_soukrome_stanice.append(data)

        # vytvoříme datasety s neupravenými daty (pouze stringy)
        cols_klima = ["Stanice", "Maximální teplota (°C)", "Minimální teplota (°C)", "Náraz větru (km/h)", "Srážky (mm)", "Sněhová pokrývka (cm)", "Sluneční svit (hod)", "Kraj", "Datum", "Odkaz"]
        cols_soukr = ["Stanice", "Maximální teplota (°C)", "Minimální teplota (°C)", "Náraz větru (km/h)", "Srážky (mm)", "Nejvyšší tlak (hPa)", "Nejvyšší vlhkost (%)", "Kraj", "Datum", "Odkaz"]
        raw_df_klima = pd.DataFrame(list_klimaticke_stanice, columns=cols_klima)
        raw_df_soukr = pd.DataFrame(list_soukrome_stanice, columns=cols_soukr)

        return raw_df_klima, raw_df_soukr
