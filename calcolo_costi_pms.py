import pandas as pd
import numpy as np
from datetime import datetime

# Carica i dati dei consumi
df_consumi = pd.read_csv('unified_consumi_data.csv')

# Carica i dati delle colazioni giornaliere
df_colazioni = pd.read_csv('colazionigiornalierecount2024.csv')
df_colazioni.columns = df_colazioni.columns.str.strip()
df_colazioni['data'] = pd.to_datetime(df_colazioni['data'], format='%d/%m/%Y %H.%M.%S')
df_colazioni['mese'] = df_colazioni['data'].dt.month

# Mappa numeri mesi a nomi
nomi_mesi = {
    4: 'Aprile',
    5: 'Maggio',
    6: 'Giugno',
    7: 'Luglio',
    8: 'Agosto',
    9: 'Settembre',
    10: 'Ottobre'
}

# Calcola statistiche per ogni mese
risultati = []
risultati_categoria = []

for mese in df_consumi['Mese'].unique():
    # Filtra i dati per mese
    dati_mese = df_consumi[df_consumi['Mese'] == mese]
    
    # Calcola il numero di colazioni per il mese
    num_mese = int(mese.split('_')[0])  # Estrae il numero del mese (es. 05 da "05_Maggio")
    colazioni_mese = df_colazioni[df_colazioni['mese'] == num_mese]
    num_colazioni = colazioni_mese['CONSUMO REALE COLAZIONI'].sum()
    giorni_servizio = len(colazioni_mese)
    
    # Calcola i costi per classe (BEVERAGE, FOOD, PULIZIA, VARIE)
    costi_classe = dati_mese.groupby('Classe').agg({
        'Costo Totale': 'sum',
        'Quantita': 'sum'
    }).reset_index()
    
    # Calcola il costo totale del mese
    costo_totale = dati_mese['Costo Totale'].sum()
    
    # Calcola medie e statistiche
    if num_colazioni > 0 and giorni_servizio > 0:
        costo_medio_colazione = costo_totale / num_colazioni
        colazioni_giorno = num_colazioni / giorni_servizio
        costo_giornaliero = costo_totale / giorni_servizio
    else:
        costo_medio_colazione = 0
        colazioni_giorno = 0
        costo_giornaliero = 0
    
    # Aggiungi i risultati mensili
    risultati.append({
        'Mese': mese,
        'Numero Colazioni': num_colazioni,
        'Giorni di Servizio': giorni_servizio,
        'Costo Totale': costo_totale,
        'Costo Medio per Colazione': costo_medio_colazione,
        'Colazioni per Giorno': colazioni_giorno,
        'Costo Giornaliero': costo_giornaliero
    })
    
    # Aggiungi i risultati per categoria
    for _, cat in costi_classe.iterrows():
        risultati_categoria.append({
            'Mese': mese,
            'Classe': cat['Classe'],
            'Costo Totale': cat['Costo Totale'],
            'Quantità Totale': cat['Quantita'],
            'Percentuale sul Totale': (cat['Costo Totale'] / costo_totale * 100) if costo_totale > 0 else 0
        })
    
    # Stampa dettagli per classe
    print(f"\nDettaglio costi per classe - {mese}:")
    for _, cat in costi_classe.iterrows():
        print(f"{cat['Classe']}: {cat['Costo Totale']:.2f}€ (Quantità: {cat['Quantita']:.2f})")

# Crea DataFrame con i risultati
df_risultati = pd.DataFrame(risultati)
df_risultati_categoria = pd.DataFrame(risultati_categoria)

# Formatta i numeri per una migliore leggibilità
pd.set_option('display.float_format', lambda x: '{:.4f}'.format(x))

# Stampa i risultati mensili
print("\nRiepilogo mensile:")
print(df_risultati.to_string(index=False))

# Stampa i risultati per categoria
print("\nRiepilogo per categoria:")
print(df_risultati_categoria.to_string(index=False))

# Calcola statistiche aggregate per classe
print("\nStatistiche aggregate per classe:")
stats_classe = df_consumi.groupby('Classe').agg({
    'Costo Totale': ['sum', 'mean'],
    'Quantita': ['sum', 'mean']
}).round(4)
print(stats_classe.to_string())

# Salva i risultati in CSV
df_risultati.to_csv('analisi_costi_mensili_pms.csv', index=False)
df_risultati_categoria.to_csv('analisi_costi_categorie_pms.csv', index=False)
print("\nFile di analisi creati con successo!") 