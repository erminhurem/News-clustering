import pandas as pd
import os
from django.conf import settings
import logging
from django.conf import settings



# Konfiguracija logovanja
logging.basicConfig(level=logging.INFO)



def create_company_directory_adjusted(file_paths):
    """
    Funkcija za dobijanje broja kompanija po opštinama.

    Args:
    file_paths (list): Lista putanja do Excel fajlova.

    Returns:
    dict: Rečnik gdje su ključevi nazivi opština, a vrijednosti broj kompanija.
    """
    all_data = pd.DataFrame()

    for fp in file_paths:
        try:
            # Učitajte samo potrebne kolone, uključujući naziv opštine, ne kod opštine.
            data = pd.read_excel(fp, usecols=['Naziv kompanije', 'Opština', 'Unnamed: 4'], engine='openpyxl')
            # Preimenovanje kolone 'Unnamed: 4' u 'Naziv opštine' za jasnoću
            data.rename(columns={'Unnamed: 4': 'Naziv opštine'}, inplace=True)
            all_data = pd.concat([all_data, data], ignore_index=True)
        except Exception as e:
            logging.error(f"Greška prilikom učitavanja fajla {fp}: {e}")

    # Provjerite postojanje kolone 'Naziv opštine' umjesto 'Opština'
    if 'Naziv opštine' not in all_data.columns:
        logging.error("Kolona 'Naziv opštine' ne postoji u učitanim podacima.")
        return {}

    # Grupisanje po nazivima opština i brojanje firmi
    companies_count = all_data.groupby('Naziv opštine')['Naziv kompanije'].count()

    return companies_count.to_dict()

# Definiranje putanja do fajlova
BASE_DIR = settings.BASE_DIR
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
companies_count_by_city = create_company_directory_adjusted(file_paths)
