import pandas as pd
import os
from django.conf import settings
import logging
from django.conf import settings



# Konfiguracija logovanja
logging.basicConfig(level=logging.INFO)



def create_company_directory_adjusted(file_paths):
    all_data = []

    for fp in file_paths:
        try:
            data = pd.read_excel(fp, usecols=['Naziv kompanije', 'Opština', 'Unnamed: 4'], engine='openpyxl')
            # Preimenovanje kolone 'Unnamed: 4' u 'Naziv opštine'
            data.rename(columns={'Unnamed: 4': 'Naziv opštine'}, inplace=True)
            all_data.append(data)  # Dodajemo DataFrame u listu
        except Exception as e:
            logging.error(f"Greška prilikom učitavanja fajla {fp}: {e}")

    if not all_data:
        logging.error("Nijedan podatak nije učitan.")
        return {}

    # Spajamo sve DataFrame objekte iz liste u jedan DataFrame
    all_data = pd.concat(all_data, ignore_index=True)

    if 'Naziv opštine' not in all_data.columns:
        logging.error("Kolona 'Naziv opštine' ne postoji u učitanim podacima.")
        return {}

    # Grupisanje po nazivima opština i brojanje firmi
    companies_count = all_data.groupby('Naziv opštine')['Naziv kompanije'].nunique()

    return companies_count.to_dict()

# Definiranje putanja do fajlova
BASE_DIR = settings.BASE_DIR
file_paths = [
   
    BASE_DIR / 'static' / 'Baza 2003.xlsx',
    
]

# Primjer korištenja funkcije
companies_count_by_city = create_company_directory_adjusted(file_paths)
