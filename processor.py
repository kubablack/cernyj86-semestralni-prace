'''
Modul, který zpracuje stažená data a vyprodukuje data frame.
'''
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd

class DataProcessor:
    '''
    Třída, která zpracuje data.
    '''
    def __init__(self):
        self.initialized = True

    def zpracovat_data_o_pocasi(self, klima_df, soukr_df):
        raw_df_klima = klima_df
        raw_df_soukr = soukr_df
        # převedeme data na čísla
        def substitute(string):
            parts = string.split(" ")
            if len(parts) == 1:
                return np.nan
            elif len(parts) == 2:
                try:
                    return float(parts[0])
                except ValueError as err:
                    print("Inappropriate format: ", err) 
            else: raise ValueError("Inappropriate format!")

        def modify_values(init_df):
            df = init_df.copy()
            for col in df.columns[1:7]:
                df[col] = df[col].apply(substitute)
            return df

        df_klima = modify_values(raw_df_klima)
        df_soukr = modify_values(raw_df_soukr)

        # ciselnik stazen z https://www.czso.cz
        ciselnik = pd.read_csv('data/ciselnik_uzemi_CR_1_1_2021.csv')
        df = ciselnik.iloc[:, :2] # začátek datasetu

        # data z https://www.rozpocetobce.cz
        coords = pd.read_csv('data/coords.csv')

        # nalezneme chybné řádky a smažeme:
        # for i, mun in enumerate(coords['OBEC_CSU_KOD']):
        #     if len(mun) != 6: 
        #         print(f"row {i} has invalid length!")
        coords = coords.drop(index= 5835)
        # změníme datový typ
        coords = coords.astype({'OBEC_CSU_KOD': int})
        # přidáme data do datasetu
        df = df.merge(coords, how="outer", left_on= "kod_obec", right_on= "OBEC_CSU_KOD").drop(["OBEC_NAZEV", "OBEC_CSU_KOD"], axis=1)

        # vyscrapujeme potřebná data z wikipedie (musíme ručně poskytnout odkazy)
        missing_id = list(df[df["LONGITUDE"].isna()]["kod_obec"])
        missing_data = []
        links = ['https://cs.wikipedia.org/wiki/Město_Libavá', 'https://cs.wikipedia.org/wiki/Bražec_(okres_Karlovy_Vary)', 
        'https://cs.wikipedia.org/wiki/Vojenský_újezd_Boletice', 'https://cs.wikipedia.org/wiki/Vojenský_újezd_Březina',
        'https://cs.wikipedia.org/wiki/Doupovské_Hradiště', 'https://cs.wikipedia.org/wiki/Hlučín',
        'https://cs.wikipedia.org/wiki/Vojenský_újezd_Hradiště', 'https://cs.wikipedia.org/wiki/Kozlov_(okres_Olomouc)',
        'https://cs.wikipedia.org/wiki/Krhová', 'https://cs.wikipedia.org/wiki/Vojenský_újezd_Libavá',
        'https://cs.wikipedia.org/wiki/Libhošť', 'https://cs.wikipedia.org/wiki/Luboměř_pod_Strážnou',
        'https://cs.wikipedia.org/wiki/Město_Libavá', 'https://cs.wikipedia.org/wiki/Petrov_nad_Desnou',
        'https://cs.wikipedia.org/wiki/Poličná', 'https://cs.wikipedia.org/wiki/Polná_na_Šumavě',
        'https://cs.wikipedia.org/wiki/Želešice']
        for lin in links:
            source = requests.get(lin).content
            soup_obce = BeautifulSoup(source, 'html.parser')
            lat_string = soup_obce.find('span', {'class': 'coordinates'}).find_all('span')[0].text
            lon_string = soup_obce.find('span', {'class': 'coordinates'}).find_all('span')[1].text
            
            try: 
                lat = float(lat_string[:lat_string.find('°')]) + float(lat_string[lat_string.find('°') + 1:lat_string.find('′')]) / 60 + float(lat_string[lat_string.find('′') + 1: lat_string.find('″')]) / 3600
            except:
                lat = float(lat_string[:lat_string.find('°')]) + float(lat_string[lat_string.find('°') + 1:lat_string.find('′')]) / 60
            
            try: 
                lon = float(lon_string[:lon_string.find('°')]) + float(lon_string[lon_string.find('°') + 1:lon_string.find('′')]) / 60 + float(lon_string[lon_string.find('′') + 1: lon_string.find('″')]) / 3600
            except:
                lon = float(lon_string[:lon_string.find('°')]) + float(lon_string[lon_string.find('°') + 1:lon_string.find('′')]) / 60 
            
            try:
                psc = ''.join((soup_obce.find('th', string = "PSČ").find_next('td').text).split(' '))
            except: psc = np.nan
            adresa = str(soup_obce.find('th', string = "Kontakt").find_next('td')).split('<br/>')[0][4:]
            ico = np.nan
            try:
                email = soup_obce.find('th', string = "Kontakt").find_next('td').find('a')['href'][7:]
            except: 
                email = np.nan
            missing_data.append([adresa, psc, ico, lin, lat, lon, email])

        # doplníme chybějící hodnoty
        for i, id in enumerate(missing_id):
            for j in range(7):
                df.loc[df["kod_obec"] == id, df.columns[3 + j]] = missing_data[i][j]

        # funkce na přiřazení kódů obcí k meteostanicím
        def get_mun_codes(mun_data):   
            data = mun_data.copy()
            mun_codes = []
            combinations = pd.Series(list(ciselnik["nazev_obec"] + ciselnik["nazev_kraj"]))
            for i in range(data.shape[0]):
                if sum(data.iloc[i, 0] + data.iloc[i, 7] == combinations) == 1:
                    mun_codes.append(ciselnik["kod_obec"][data.iloc[i, 0] + data.iloc[i, 7] == combinations].values[0])
                elif "-" in data.iloc[i, 0]:
                    try:
                        mun_codes.append(ciselnik["kod_obec"][data.iloc[i, 0][:data.iloc[i, 0].find("-")-1] + data.iloc[i, 7] == combinations].values[0])
                    except: 
                        mun_codes.append(np.nan)
                else:
                    mun_codes.append(np.nan)
            data["kod_obec"] = mun_codes
            return data

        df_klima = get_mun_codes(df_klima) # přiřadíme kódy
        # dataset obsahuje chybějící hodnoty, přepíšeme ručně názvy stanic (na nejbližší obci) a poté znovu aplikujeme funkci get_mun_codes()

        old_mun = ['Churáňov', 'Pec pod Snežkou', 'Sněžka', 'Červená hora', 'Lysá hora', 'Šerák', 'Milešovka', 'Tušimice', 'Kramolín (Křešín)', 'Kunovice']
        new_name = ["Stachy", "Pec pod Sněžkou", "Pec pod Sněžkou", "Budišov nad Budišovkou", "Ostravice", 
        "Ostružná", "Velemín", "Kadaň", "Křešín", "Kunovice"]
        new_mun = dict(zip(old_mun, new_name))
        for stanice in list(new_mun.keys()):
            df_klima.loc[df_klima["Stanice"] == stanice, "Stanice"] = new_mun[stanice]
        df_klima = get_mun_codes(df_klima)
        df_klima.loc[df_klima["Stanice"] == "Kunovice", "kod_obec"] = 550744 # 1 hodnotu musíme doplnit ručně

        # to samé pro druhý dataframe
        df_soukr = get_mun_codes(df_soukr)
        old_mun2 = ['Janova Ves', 'Řasnice', 'Břeclav Poštorná', 'Drnovice (Vyškov)', 'Louka', 'Němčičky', 'Padochov', 'Vysočany', 'Zbyšov', 
        'Albrechtice u Frýdlantu', 'Horní Sytová', 'Lubina', 'Suchá Rudná', 'Studený Zejf', 'Filipova Huť', 'Mrchojedy (Meclov)', 
        'Podmokly', 'Praha 10, Bohdalec', 'Praha 4 - Krč', 'Praha 5, Velká Chuchle', 'Praha 9, Prosek', 'Brandýs nad Labem',
        'Jestřábí Lhota', 'Jivina', 'Petrovice (Rakovník)', 'Staré Ouholice', 'Šlotava', 'Vysoký Újezd', 'Radešín', 'Střelná', 
        'Dobrá Voda', 'Hostákov', 'Opatov', 'Petrovice (Třebíč)', 'Týmova Ves', 'Kunovice']
        new_name2 = ["Pohorská Ves", "Strážný", "Břeclav", "Vyškov", "Velká nad Veličkou", "Ivančice", 
        "Oslavany", "Blansko", "Zbýšov", "Frýdlant", "Víchová nad Jizerou", "Kopřivnice", "Světlá Hora", "Písečná", 
        "Modrava", "Meclov", "Zbiroh", "Praha", "Praha", "Praha", "Praha", "Brandýs nad Labem-Stará Boleslav", 
        "Kolín", "Mnichovo Hradiště", "Rakovník", "Nová Ves", "Budiměřice", "Vysoký Újezd", "Chuderov", "Košťany",
        "Velké Meziříčí", "Vladislav", "Opatov", "Třebíč", "Lukavec", "Kunovice"]
        new_mun2 = dict(zip(old_mun2, new_name2))
        for stanice in list(new_mun2.keys()):
            df_soukr.loc[df_soukr["Stanice"] == stanice, "Stanice"] = new_mun2[stanice]
        df_soukr = get_mun_codes(df_soukr)
        # ručně doplníme problémové obce
        df_soukr.loc[df_soukr["Stanice"] == "Opatov", "kod_obec"] = 591319
        df_soukr.loc[df_soukr["Stanice"] == "Vysoký Újezd", "kod_obec"] = 531961
        df_soukr.loc[df_soukr["Stanice"] == "Kunovice", "kod_obec"] = 550744
        df_soukr.loc[df_soukr["Stanice"] == "Zbýšov", "kod_obec"] = 584223
        df_soukr.loc[df_soukr["Stanice"] == "Nová Ves", "kod_obec"] = 532355

        return df_klima, df_soukr, df

    def spocitat_vzdalenosti_mezi_obcemi_a_finalizovat_df(self, df_klima, df_soukr, df):
        # from geopy.distance import great_circle
        # import gzip
        # import pickle

        # spočítáme všechny vzájemné vzdálenosti mezi obcemi, vytvoříme data frame a uložíme

        # length = df.shape[0]
        # distances_np = np.zeros((length, length))
        # for i in range(length):
        #     for j in range(length):
        #         distances_np[i, j] = great_circle((df["LATITUDE"][i], df["LONGITUDE"][i]), (df["LATITUDE"][j], df["LONGITUDE"][j])).km

        # dist_df = pd.DataFrame(distances_np, index=df["kod_obec"], columns=df["kod_obec"])
        # with gzip.open("data/municipal_distances_df", "wb") as dists:
        #     pickle.dump(dist_df, dists)

        # from geopy.distance import great_circle
        # import gzip
        # import pickle

        # # spočítáme všechny vzájemné vzdálenosti mezi obcemi, vytvoříme data frame a uložíme

        # length = df.shape[0]
        # distances_np = np.zeros((length, length))
        # for i in range(length):
        #     for j in range(length):
        #         distances_np[i, j] = great_circle((df["LATITUDE"][i], df["LONGITUDE"][i]), (df["LATITUDE"][j], df["LONGITUDE"][j])).km

        # dist_df = pd.DataFrame(distances_np, index=df["kod_obec"], columns=df["kod_obec"])
        # with gzip.open("data/municipal_distances_df", "wb") as dists:
        #     pickle.dump(dist_df, dists)

        # # kód na načtení matice vzdáleností
        # with gzip.open('data/municipal_distances_df', 'rb') as f:
        #     distances = pickle.load(f)

        # # zredukujeme dataset vzdáleností (sloupce jsou už jen ty obce, kde je meteostanice) a nalezneme nejbližší meteostanici pro každou obec
        # df_klima = df_klima.drop_duplicates(subset = "kod_obec")
        # dist_reduced_klima = distances.loc[:, df_klima["kod_obec"]]
        # nearest_klima = []
        # nearest_klima_vzd = []
        # for i in range(dist_reduced_klima.shape[0]):
        #     nearest_klima.append(dist_reduced_klima.columns[np.argmin(dist_reduced_klima.iloc[i,:])])
        #     nearest_klima_vzd.append(min(dist_reduced_klima.iloc[i,:]))
        # dist_reduced_klima["nejblizsi_stanice"] = nearest_klima
        # dist_reduced_klima["nejblizsi_stanice_vzd"] = nearest_klima_vzd

        # # zredukujeme dataset vzdáleností (sloupce jsou už jen ty obce, kde je meteostanice) a nalezneme nejbližší meteostanici pro každou obec
        # df_soukr = df_soukr.drop_duplicates(subset = "kod_obec")
        # dist_reduced_soukr = distances.loc[:, df_soukr["kod_obec"]]
        # nearest_soukr = []
        # nearest_soukr_vzd = []
        # for i in range(dist_reduced_soukr.shape[0]):
        #     nearest_soukr.append(dist_reduced_soukr.columns[np.argmin(dist_reduced_soukr.iloc[i,:])])
        #     nearest_soukr_vzd.append(min(dist_reduced_soukr.iloc[i,:]))
        # dist_reduced_soukr["nejblizsi_stanice"] = nearest_soukr
        # dist_reduced_soukr["nejblizsi_stanice_vzd"] = nearest_soukr_vzd

        # # uložíme
        # dist_reduced_klima.to_csv("data_final/dist_reduced_klima.csv")
        # dist_reduced_soukr.to_csv("data_final/dist_reduced_soukr.csv")

        # načteme data
        dist_reduced_klima = pd.read_csv("data_final/dist_reduced_klima.csv", index_col="kod_obec")
        dist_reduced_soukr = pd.read_csv("data_final/dist_reduced_soukr.csv", index_col="kod_obec")

        df_klima = df_klima.drop_duplicates(subset = "kod_obec")
        df_soukr = df_soukr.drop_duplicates(subset = "kod_obec")
        # propojujeme základní dataframe s daty z nejbližší klimatické meteostanice
        df = df.merge(dist_reduced_klima["nejblizsi_stanice"], how = "outer", right_index = True, left_on = "kod_obec")
        df = df.merge(dist_reduced_klima["nejblizsi_stanice_vzd"], how = "outer", right_index = True, left_on = "kod_obec")
        df = df.rename(columns={"kod_obec": "kod"})
        df = df.merge(df_klima, how="left", left_on = "nejblizsi_stanice", right_on = "kod_obec")
        df = df.drop(columns=["kod_obec"])

        # propojujeme základní dataframe s daty z nejbližší soukromé meteostanice
        df = df.merge(dist_reduced_soukr["nejblizsi_stanice"], how = "outer", right_index = True, left_on = "kod")
        df = df.merge(dist_reduced_soukr["nejblizsi_stanice_vzd"], how = "outer", right_index = True, left_on = "kod")
        df_soukr = df_soukr.drop(columns=["Kraj", "Datum", "Odkaz"])
        df = df.merge(df_soukr, how="left", left_on = "nejblizsi_stanice_y", right_on = "kod_obec")
        df = df.drop(columns=["kod_obec"])

        # vybereme data z nejbližší stanice
        final_stanice = []
        for i in range(len(df)):
            if df["nejblizsi_stanice_vzd_x"][i] <= df["nejblizsi_stanice_vzd_y"][i]:
                final_stanice.append(list(df.iloc[i, 10:17]))
            else:
                final_stanice.append(list(df.iloc[i, 22:29]))

        final_stanice_df = pd.DataFrame(final_stanice, columns=['nejblizsi_stanice', 'nejblizsi_stanice_vzd', 'Stanice',
            'Maximální teplota (°C)', 'Minimální teplota (°C)',
            'Náraz větru (km/h)', 'Srážky (mm)'])
        df = pd.concat([df, final_stanice_df], axis=1)
        df = df.set_index("kod")


        # doplníme chybějící hodnoty a upravíme formát
        vals = ['Maximální teplota (°C)',
        'Minimální teplota (°C)', 'Náraz větru (km/h)', 'Srážky (mm)',
        'Sněhová pokrývka (cm)', 'Sluneční svit (hod)', 'Nejvyšší tlak (hPa)',
        'Nejvyšší vlhkost (%)']
        for val in vals:
            df[val] = df[val].fillna(df[val].mean())
        
        df['OBEC_ORG_ULICE'] = df['OBEC_ORG_ULICE'].fillna("přesná adresa není k dispozici")

        df["nejblizsi_stanice_vzd"] = round(df["nejblizsi_stanice_vzd"],2)

        # uložíme data frame
        df.loc[:,['nazev_obec', 'Kraj', 'Datum', 'URL_WIKIPEDIA', 'OBEC_ORG_NAZEV', 'OBEC_ORG_ULICE', 'OBEC_ORG_PSC',
            'OBEC_ICO_ORG', 'LONGITUDE', 'LATITUDE', 'EMAIL_PODATELNA', 'nejblizsi_stanice', 'nejblizsi_stanice_vzd', 'Stanice', 'Odkaz',
            'Maximální teplota (°C)', 'Minimální teplota (°C)', 'Náraz větru (km/h)', 'Srážky (mm)', 'Sněhová pokrývka (cm)',
            'Sluneční svit (hod)','Nejvyšší tlak (hPa)', 'Nejvyšší vlhkost (%)']].to_csv(f"data_final/df_{df.iloc[1, 19]}.csv")
