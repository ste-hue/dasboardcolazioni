import pandas as pd

# Dati mensili
data = {
    'Mese': ['Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre'],
    'Colazioni_Servite': [1279, 3459, 4896, 5199, 5159, 4337, 3202],
    'Costo_Totale': [8883.02, 15004.04, 18966.23, 22540.99, 21773.70, 19710.02, 13749.44],
    'Giorni_Mese': [30, 31, 30, 31, 31, 30, 31]  # Numero di giorni in ogni mese
}

# Crea DataFrame
df = pd.DataFrame(data)

# Calcola costo medio per colazione
df['Costo_Medio_per_Colazione'] = df['Costo_Totale'] / df['Colazioni_Servite']

# Calcola consumo giornaliero medio
df['Consumo_Giornaliero'] = df['Costo_Totale'] / df['Giorni_Mese']

# Calcola colazioni giornaliere medie
df['Colazioni_Giornaliere'] = df['Colazioni_Servite'] / df['Giorni_Mese']

# Salva in CSV
df.to_csv('consumi_giornalieri.csv', index=False)
print("File CSV creato con successo!")

# Stampa i risultati con tutti i decimali
pd.set_option('display.float_format', lambda x: '%.4f' % x)
print("\nRisultati:")
print(df.to_string()) 