import pandas as pd
import os
from django.conf import settings
import logging
from django.conf import settings
BASE_DIR = settings.BASE_DIR


# Konfiguracija logovanja
logging.basicConfig(level=logging.INFO)

def create_company_directory_adjusted(file_paths, letter):
    """
    Unaprijeđena funkcija za kreiranje adresara kompanija.
    
    Args:
    file_paths (list): Lista putanja do Excel fajlova.
    letter (str): Slovo za filtriranje naziva kompanija.
    
    Returns:
    list: Lista kompanija čiji naziv počinje s određenim slovom, sortirane abecedno.
    """
    if not letter.isalpha() or len(letter) != 1:
        logging.error("Uneseno slovo nije validno.")
        return []

    letter = letter.upper()  # Pretvoriti slovo u veliko slovo za konzistentnost
    all_data = pd.DataFrame()

    for fp in file_paths:
        try:
            data = pd.read_excel(fp, usecols=['Naziv kompanije', 'Opština'])
            all_data = pd.concat([all_data, data], ignore_index=True)
        except Exception as e:
            logging.error(f"Greška prilikom učitavanja fajla {fp}: {e}")

        # Spajanje svih podataka u jedan DataFrame
    all_data = pd.concat([pd.read_excel(fp, usecols=['Naziv kompanije', 'Opština']) for fp in file_paths], ignore_index=True)

    # Provjera da li kolona 'Naziv kompanije' postoji
    if 'Naziv kompanije' not in all_data.columns:
        logging.error("Kolona 'Naziv kompanije' ne postoji u učitanim podacima.")
        return []

    # Filtriranje i sortiranje podataka
    filtered_data = all_data[all_data['Naziv kompanije'].str.startswith(letter, na=False)]
    sorted_data = filtered_data.sort_values(by='Naziv kompanije')

    return sorted_data.to_dict('records')

# Definiranje putanja do fajlova
file_paths = [
    BASE_DIR / 'static' / 'Baza 2000.xlsx',
    BASE_DIR / 'static' / 'Baza 2001.xlsx',
    BASE_DIR / 'static' / 'Baza 2002.xlsx',
    BASE_DIR / 'static' / 'Baza 2003.xlsx',
    BASE_DIR / 'static' / 'Baza 2005.xlsx',
    BASE_DIR / 'static' / 'Baza 2006.xlsx',
    BASE_DIR / 'static' / 'Baza 2007.xlsx',
    BASE_DIR / 'static' / 'Baza 2008.xlsx',
    BASE_DIR / 'static' / 'Baza 2009.xlsx',
    
]


# Primjer korištenja funkcije
sample_companies_adjusted = create_company_directory_adjusted(file_paths, 'A')
print(sample_companies_adjusted[:5])  # Prikaz prvih 5 kompanija za testiranje
