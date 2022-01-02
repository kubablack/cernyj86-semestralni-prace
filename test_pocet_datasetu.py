
def test_pocet():
  import glob
  datasety = len(glob.glob("data_final/df_*"))
  
  assert datasety > 0
