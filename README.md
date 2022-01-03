## Zobrazování dat v mapě

Tato práce umožňuje scrapovat data o počasí, zpracovávat je a přiřazovat k obcím v ČR. Následně je zobrazí v mapě.

#### Struktura: 
Repozitář obsahuje skript na scrapování *(scraper.py)*, skript na zpracování dat *(processor.py)*, skript na zpracování polygonů *(polygons.py)*, notebook, ve kterém byly psány testy *(writing_tests.ipynb)*, sadu testů, skript umožňující stáhnout data manuálně *(download_data.py)* a skript s aplikací *(run_app.py)*. Spuštěním posledního zmíněného skriptu by se měla otevřít streamlit aplikace, která zobrazuje data. Ostatní skripty není třeba spouštět, protože se použijí při stahování nových dat (dostupné z aplikace) nebo při testování, které se zahájí příkazem *pytest* v konzoli.

Při stahování dat se výsledek ukládá do složky data_final, kde jsou také uloženy pomocné datasety, polygony a části matice se vzdálenostmi. Provedením příkazu *pytest* se otestují outputy jednotlivých skriptů- zda obsahují data a zda tam nejsou chybějící hodnoty. Některé části skriptů jsou záměrně zakomentované, protože obsahují dlouhé výpočty nebo příliš velká data. Ta jsem nejprve vyfiltroval (uvedeným zakomentovaným kódem) a poté načetl jejich potřebnou část, aby repozitář nebyl příliš velký. Požadované balíčky jsou k dispozici v *requirements.txt*.
