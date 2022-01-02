'''
Modul, který připraví polygony k tvorbě grafů.
'''
# import geopandas as gpd

class PreparePolygons:
    '''
    Třída, která vybere a uloží polygony ČR.
    '''
    def __init__(self):
        self.initialized = True

    #def dostat_polygony_CR(self):
        # # načteme polygonovou strukturu (data z Eurostatu, musíme vybrat obce ČR)
        # poly = gpd.read_file('data/polygons/COMM_RG_01M_2013.shp')
        # poly = poly[10630:16883]
        # # upravíme index
        # poly = poly.reset_index().drop(columns="index")
        # poly["COMM_ID"] = poly["COMM_ID"].apply(lambda x: x[-6:])
        # poly = poly.rename(columns={"COMM_ID": "kod"})
        # poly["kod"] = poly["kod"].astype(int)
        # poly = poly.set_index("kod")
        # poly.to_file("data_final/poly_cze.shp")