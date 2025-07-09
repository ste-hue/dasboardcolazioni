import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import math

# Configurazione del tema
st.set_page_config(
    page_title="Dashboard Colazioni",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definizione del tema personalizzato
st.markdown("""
    <style>
    /* Colori principali */
    :root {
        --primary-color: #8B6914;
        --secondary-color: #FFF8DC;
        --accent-color: #D2691E;
        --background-color: #FFFFFF;
        --text-color: #333333;
        --card-bg: #F8F9FA;
        --border-color: #E0E0E0;
    }

    /* Stile generale */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    /* Stile titoli */
    h1, h2, h3 {
        color: var(--text-color) !important;
    }

    /* Stile metriche */
    [data-testid="metric-container"] {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: var(--text-color) !important;
    }

    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: var(--primary-color) !important;
        font-weight: bold;
    }

    /* Stile tab */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: var(--card-bg);
        border-radius: 10px;
        padding: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 5px;
        padding: 10px 20px;
        color: var(--text-color);
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white !important;
    }

    /* Stile bottoni */
    .stButton button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        background-color: var(--accent-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Stile dataframe */
    .dataframe {
        background-color: var(--card-bg);
        border-radius: 10px;
        border: 1px solid var(--border-color);
        overflow: hidden;
    }

    .dataframe thead tr th {
        background-color: var(--primary-color) !important;
        color: white !important;
        font-weight: bold;
        padding: 12px !important;
    }

    .dataframe tbody tr:nth-child(even) {
        background-color: #F5F5F5;
    }

    .dataframe tbody tr:hover {
        background-color: #E8E8E8;
    }

    /* Stile selectbox e input */
    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: white;
        color: var(--text-color);
        border: 1px solid var(--border-color);
        border-radius: 5px;
    }

    .stSelectbox > label,
    .stTextInput > label,
    .stNumberInput > label {
        color: var(--text-color) !important;
        font-weight: 500;
    }

    /* Stile sidebar */
    .css-1d391kg {
        background-color: var(--card-bg);
    }

    /* Stile alerts */
    .stAlert {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        color: var(--text-color);
    }

    /* Miglioramento contrasto per i grafici */
    .js-plotly-plot .plotly {
        background-color: white !important;
    }

    /* Card personalizzate */
    .custom-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Miglioramento leggibilità testo */
    p, span, div {
        color: var(--text-color) !important;
    }

    /* Stile per expander */
    .streamlit-expanderHeader {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 5px;
        color: var(--text-color) !important;
    }

    .streamlit-expanderContent {
        background-color: white;
        border: 1px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 5px 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Costanti per i file
DASHBOARD_FILE = "breakfast_dashboard.xlsx"
CONSUMI_FILE = "unified_consumi_data.csv"
COLATIONI_FILE = "colazionigiornalierecount2024.csv"
MAX_PAX_GIORNALIERI = 194  # Numero massimo di colazioni giornaliere

# Dizionario dei nomi dei mesi
NOMI_MESI = {
    4: 'Aprile',
    5: 'Maggio',
    6: 'Giugno',
    7: 'Luglio',
    8: 'Agosto',
    9: 'Settembre',
    10: 'Ottobre'
}

# Dizionario dei costi mensili
COSTI_MENSILI = {
    'Aprile': 8883.02,
    'Maggio': 15004.04,
    'Giugno': 18966.23,
    'Luglio': 22540.99,
    'Agosto': 21773.70,
    'Settembre': 19710.02,
    'Ottobre': 13749.44
}

# Colazioni mensili reali (basate sui dati effettivi)
COLATIONI_MENSILI = {
    'Aprile': 1279,
    'Maggio': 3459,
    'Giugno': 4896,
    'Luglio': 5199,
    'Agosto': 5159,
    'Settembre': 4337,
    'Ottobre': 3202
}

# Caricamento dati
@st.cache_data
def carica_dati():
    """Carica i dati dai file"""
    dati = {}

    # Carica il file dashboard se esiste
    if os.path.exists(DASHBOARD_FILE):
        try:
            # Carica coefficienti di ogni mese
            for numero_mese, nome_mese in NOMI_MESI.items():
                try:
                    df = pd.read_excel(DASHBOARD_FILE, sheet_name=nome_mese, skiprows=3)
                    # Converti i coefficienti in valori numerici
                    if 'Coefficiente' in df.columns:
                        df['Coefficiente'] = pd.to_numeric(df['Coefficiente'], errors='coerce')
                    dati[nome_mese] = df
                except Exception as e:
                    st.warning(f"Impossibile caricare il foglio {nome_mese}: {e}")

            # Carica coefficienti combinati
            try:
                df_coeff = pd.read_excel(DASHBOARD_FILE, sheet_name='Coefficienti Mensili')
                dati['coefficienti'] = df_coeff
            except Exception as e:
                print(f"Impossibile caricare il foglio Coefficienti Mensili: {e}")

            # Carica dati dei costi dai consumi
            if os.path.exists(CONSUMI_FILE):
                try:
                    df_consumi = pd.read_csv(CONSUMI_FILE)
                    # Pulisci il nome delle colonne
                    df_consumi.columns = df_consumi.columns.str.strip()
                    dati['consumi'] = df_consumi
                except Exception as e:
                    st.warning(f"Impossibile caricare il file consumi: {e}")

        except Exception as e:
            st.error(f"Errore nel caricamento del file dashboard: {e}")

    return dati

# Cerca costi e dettagli di un prodotto
def trova_informazioni_prodotto(df_consumi, articolo):
    """Cerca le informazioni di costo per un prodotto nel dataset dei consumi"""
    if df_consumi is None or articolo is None:
        return None

    # Pulizia del nome articolo per migliorare la corrispondenza
    articolo_pulito = str(articolo).strip().upper()

    # Cerca corrispondenza esatta
    match = df_consumi[df_consumi['Articolo'].str.strip().str.upper() == articolo_pulito]

    if match.empty:
        # Cerca corrispondenza parziale
        match = df_consumi[df_consumi['Articolo'].str.contains(articolo_pulito, case=False, na=False)]

    if not match.empty:
        # Prendi il primo match
        info = match.iloc[0]
        return {
            'costo_medio': info.get('Euro Medio', 0),
            'uma': info.get('U.M.A.', ''),
            'umc': info.get('U.M.C.', ''),
            'coeff_conv': info.get('Coeff Conv', 1),
            'classe': info.get('Classe', '')
        }

    return None

# Applicazione principale
def main():
    # Titolo dell'app
    st.title("🍳 Dashboard Colazioni")

    # Carica i dati
    dati = carica_dati()
    if not dati:
        st.warning("Nessun dato disponibile. Verifica che i file Excel siano presenti.")
        st.stop()

    # Filtra mesi disponibili
    mesi_disponibili = [m for m in NOMI_MESI.values() if m in dati]

    # Layout principale a tab
    tab1, tab2, tab3 = st.tabs(["📈 Dettaglio Mensile", "🔄 Confronto Mesi", "📝 Pianificazione Ordini"])

    # Tab 1: Dettaglio Mensile
    with tab1:
        col1, col2 = st.columns([1, 3])

        with col1:
            # Selezione del mese
            mese_selezionato = st.selectbox("Seleziona Mese", mesi_disponibili, key="tab1_mese")

            # Mostra dati mensili
            st.subheader(f"Dati {mese_selezionato} 2024")
            st.metric("Colazioni Servite", f"{COLATIONI_MENSILI.get(mese_selezionato, 0):,}")
            st.metric("Costo Totale", f"{COSTI_MENSILI.get(mese_selezionato, 0):,.2f} €")

            if mese_selezionato in COLATIONI_MENSILI and COLATIONI_MENSILI[mese_selezionato] > 0:
                costo_medio = COSTI_MENSILI.get(mese_selezionato, 0) / COLATIONI_MENSILI[mese_selezionato]
                st.metric("Costo Medio per Colazione", f"{costo_medio:.2f} €")

        with col2:
            # Mostra i top 10 coefficienti di consumo
            if mese_selezionato in dati:
                df_mese = dati[mese_selezionato].copy()
                df_coefficienti = df_mese[df_mese['Coefficiente'] > 0].copy()

                if not df_coefficienti.empty:
                    st.subheader("📊 Top 10 Coefficienti di Consumo")

                    # Ordina per coefficiente decrescente e prendi i top 10
                    df_top_coefficienti = df_coefficienti.nlargest(10, 'Coefficiente')[['Articolo', 'Coefficiente', 'UDM']]

                    # Crea un grafico a barre orizzontali
                    fig_coeff = go.Figure()
                    fig_coeff.add_trace(go.Bar(
                        x=df_top_coefficienti['Coefficiente'],
                        y=df_top_coefficienti['Articolo'],
                        orientation='h',
                        marker_color='#8B6914',
                        text=df_top_coefficienti['Coefficiente'].apply(lambda x: f'{x:.5f}'),
                        textposition='outside'
                    ))

                    fig_coeff.update_layout(
                        title='Prodotti con Maggior Consumo per Colazione',
                        xaxis_title='Coefficiente di Consumo',
                        yaxis_title='Prodotto',
                        height=400,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='#333333'),
                        xaxis=dict(
                            showgrid=True,
                            gridwidth=1,
                            gridcolor='#E0E0E0'
                        ),
                        yaxis=dict(
                            showgrid=False,
                            autorange='reversed'
                        ),
                        margin=dict(l=200)
                    )

                    st.plotly_chart(fig_coeff, use_container_width=True)

                    # Mostra anche una tabella compatta
                    with st.expander("📋 Vedi tutti i coefficienti"):
                        st.dataframe(
                            df_coefficienti[['Categoria', 'Articolo', 'Coefficiente', 'UDM']].sort_values('Coefficiente', ascending=False).style.format({
                                'Coefficiente': '{:.5f}'
                            }),
                            use_container_width=True,
                            height=300
                        )

            # Carica e mostra dati delle colazioni reali
            try:
                df_colazioni = pd.read_csv('colazionigiornalierecount2024.csv')
                # Pulisci i nomi delle colonne rimuovendo spazi extra
                df_colazioni.columns = df_colazioni.columns.str.strip()
                # Converti la data nel formato corretto
                df_colazioni['data'] = pd.to_datetime(df_colazioni['data'], format='%d/%m/%Y %H.%M.%S')
                df_colazioni['mese'] = df_colazioni['data'].dt.month

                # Filtra per il mese selezionato
                mese_numero = [k for k, v in NOMI_MESI.items() if v == mese_selezionato][0]
                df_mese_colazioni = df_colazioni[df_colazioni['mese'] == mese_numero]

                if not df_mese_colazioni.empty:
                    colazioni_totali = df_mese_colazioni['CONSUMO REALE COLAZIONI'].sum()

                    # Mostra metriche di confronto
                    col2a, col2b = st.columns(2)
                    with col2a:
                        st.metric("Colazioni Reali", f"{colazioni_totali:,.0f}")
                    with col2b:
                        st.metric("Differenza vs Target", f"{colazioni_totali - COLATIONI_MENSILI.get(mese_selezionato, 0):+,.0f}")

                    # Grafico di confronto giornaliero
                    st.subheader("Confronto Giornaliero")
                    fig = go.Figure()

                    # Aggiungi linea delle colazioni target
                    fig.add_trace(go.Scatter(
                        x=df_mese_colazioni['data'],
                        y=[COLATIONI_MENSILI.get(mese_selezionato, 0)/len(df_mese_colazioni)] * len(df_mese_colazioni),
                        name='Target Giornaliero',
                        line=dict(color='#8B6914', dash='dash', width=2)
                    ))

                    # Aggiungi linea delle colazioni reali
                    fig.add_trace(go.Scatter(
                        x=df_mese_colazioni['data'],
                        y=df_mese_colazioni['CONSUMO REALE COLAZIONI'],
                        name='Colazioni Reali',
                        line=dict(color='#D2691E', width=3)
                    ))

                    fig.update_layout(
                        title=f'Confronto Target vs Colazioni Reali - {mese_selezionato}',
                        xaxis_title='Data',
                        yaxis_title='Numero Colazioni',
                        hovermode='x unified',
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='#333333'),
                        xaxis=dict(
                            showgrid=True,
                            gridwidth=1,
                            gridcolor='#E0E0E0',
                            showline=True,
                            linewidth=1,
                            linecolor='#E0E0E0'
                        ),
                        yaxis=dict(
                            showgrid=True,
                            gridwidth=1,
                            gridcolor='#E0E0E0',
                            showline=True,
                            linewidth=1,
                            linecolor='#E0E0E0'
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Tabella dettaglio giornaliero
                    st.subheader("Dettaglio Giornaliero")
                    df_dettaglio = df_mese_colazioni[['data', 'CONSUMO REALE COLAZIONI']].copy()
                    df_dettaglio['data'] = df_dettaglio['data'].dt.strftime('%d/%m/%Y')
                    df_dettaglio.columns = ['Data', 'Colazioni Reali']
                    st.dataframe(
                        df_dettaglio.style.format({'Colazioni Reali': '{:,.0f}'}),
                        use_container_width=True,
                        height=200
                    )
            except Exception as e:
                st.warning(f"Impossibile caricare i dati delle colazioni reali: {e}")

            if mese_selezionato in dati:
                df_mese = dati[mese_selezionato].copy()

                # Filtra prodotti con coefficiente > 0
                df_mese_filtrato = df_mese[df_mese['Coefficiente'] > 0].copy()

                if not df_mese_filtrato.empty:
                    # Calcola consumo totale
                    colazioni = COLATIONI_MENSILI.get(mese_selezionato, 0)
                    df_mese_filtrato['Consumo Totale'] = df_mese_filtrato['Coefficiente'] * colazioni

                    # Aggiungi informazione sui coefficienti
                    st.subheader(f"📦 Consumi Prodotti - {mese_selezionato}")

                    # Mostra alcune statistiche sui coefficienti
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    with col_stat1:
                        st.metric("N° Prodotti", len(df_mese_filtrato))
                    with col_stat2:
                        st.metric("Coeff. Medio", f"{df_mese_filtrato['Coefficiente'].mean():.5f}")
                    with col_stat3:
                        st.metric("Coeff. Max", f"{df_mese_filtrato['Coefficiente'].max():.5f}")

                    # Mostra tabella
                    st.dataframe(
                        df_mese_filtrato[['Categoria', 'Articolo', 'UDM', 'Coefficiente', 'Consumo Totale']].style.format({
                            'Coefficiente': '{:.5f}',
                            'Consumo Totale': '{:.2f}'
                        }),
                        use_container_width=True,
                        height=400
                    )

                    # Download CSV
                    csv = df_mese_filtrato.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Scarica dati come CSV",
                        csv,
                        f"storico_colazioni_{mese_selezionato}_2024.csv",
                        "text/csv",
                        key='download-mensile'
                    )

                    # Grafico distribuzione categorie
                    st.subheader(f"Distribuzione Categorie - {mese_selezionato}")

                    # Assicurati che Categoria non sia vuota
                    df_categorie = df_mese_filtrato.dropna(subset=['Categoria'])
                    if not df_categorie.empty:
                        df_categorie = df_categorie.groupby('Categoria')['Consumo Totale'].sum().reset_index()
                        df_categorie = df_categorie.sort_values('Consumo Totale', ascending=False)

                        fig = px.pie(
                            df_categorie,
                            values='Consumo Totale',
                            names='Categoria',
                            title=f'Consumo per Categoria - {mese_selezionato}',
                            color_discrete_sequence=['#8B6914', '#D2691E', '#CD853F', '#DEB887', '#F4A460', '#DAA520', '#B8860B', '#FFD700']
                        )
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        fig.update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font=dict(color='#333333')
                        )
                        st.plotly_chart(fig, use_container_width=True)

    # Tab 2: Confronto Mesi
    with tab2:
        st.subheader("Confronto tra Mesi")

        col1, col2 = st.columns(2)

        with col1:
            # Selezione dei mesi da confrontare
            mesi_confronto = st.multiselect(
                "Seleziona mesi da confrontare",
                options=mesi_disponibili,
                default=mesi_disponibili[:2] if len(mesi_disponibili) >= 2 else mesi_disponibili
            )

        with col2:
            # Selezione della categoria da confrontare
            categorie_disponibili = set()
            for mese in mesi_confronto:
                if mese in dati:
                    df_mese = dati[mese]
                    categorie_mese = df_mese['Categoria'].dropna().unique()
                    categorie_disponibili.update(categorie_mese)

            categoria_selezionata = st.selectbox(
                "Seleziona categoria da confrontare",
                options=sorted(list(categorie_disponibili)) if categorie_disponibili else [""]
            )

        # Crea dataframe di confronto
        if mesi_confronto and categoria_selezionata:
            dati_confronto = []

            for mese in mesi_confronto:
                if mese in dati:
                    df_mese = dati[mese].copy()
                    df_categoria = df_mese[df_mese['Categoria'] == categoria_selezionata].copy()

                    if not df_categoria.empty:
                        presenze = COLATIONI_MENSILI.get(mese, 0)
                        df_categoria['Consumo Totale'] = df_categoria['Coefficiente'] * presenze

                        # Per ogni prodotto nella categoria
                        for _, row in df_categoria.iterrows():
                            if pd.notna(row['Articolo']) and pd.notna(row['Coefficiente']):
                                dati_confronto.append({
                                    'Mese': mese,
                                    'Prodotto': row['Articolo'],
                                    'Coefficiente': row['Coefficiente'],
                                    'Consumo Totale': row['Consumo Totale']
                                })

            if dati_confronto:
                df_confronto = pd.DataFrame(dati_confronto)

                # Mostra tabella di confronto
                st.subheader(f"Confronto Consumi - {categoria_selezionata}")
                st.dataframe(
                    df_confronto.pivot(index='Prodotto', columns='Mese', values='Consumo Totale').style.format('{:.2f}'),
                    use_container_width=True
                )

                # Grafico confronto consumi
                fig = px.bar(
                    df_confronto,
                    x='Prodotto',
                    y='Consumo Totale',
                    color='Mese',
                    title=f'Confronto Consumi per Mese - {categoria_selezionata}',
                    barmode='group',
                    color_discrete_sequence=['#8B6914', '#D2691E', '#CD853F', '#DEB887', '#F4A460', '#DAA520', '#B8860B']
                )
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='#333333'),
                    xaxis=dict(
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='#E0E0E0',
                        showline=True,
                        linewidth=1,
                        linecolor='#E0E0E0'
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='#E0E0E0',
                        showline=True,
                        linewidth=1,
                        linecolor='#E0E0E0'
                    ),
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig, use_container_width=True)

                # Download confronto
                csv_confronto = df_confronto.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Scarica confronto come CSV",
                    csv_confronto,
                    f"confronto_{categoria_selezionata}.csv",
                    "text/csv",
                    key='download-confronto'
                )

    # Tab 3: Pianificazione Ordini
    with tab3:
        st.subheader("Pianificazione Ordini")

        col1, col2 = st.columns(2)

        with col1:
            # Selezione del mese di riferimento
            mese_riferimento = st.selectbox("Mese di riferimento", mesi_disponibili, key="tab3_mese")

            # Input diretto del numero di colazioni
            num_colazioni = st.number_input(
                "Numero di colazioni da preparare",
                min_value=1,
                value=100,
                step=10
            )

            # Buffer
            buffer_percentuale = st.slider(
                "Buffer (%)",
                min_value=0,
                max_value=50,
                value=10,
                step=5
            )

        with col2:
            # Esclusione categorie
            categorie_disponibili = []
            if mese_riferimento in dati:
                df_mese = dati[mese_riferimento]
                categorie_disponibili = df_mese['Categoria'].dropna().unique().tolist()

            escludere_prodotti = st.multiselect(
                "Escludere categorie",
                options=categorie_disponibili
            )

            # Opzione per includere giacenze
            include_giacenze = st.checkbox("Considera giacenze attuali")

        # Calcolo quantità
        if mese_riferimento in dati:
            df_mese = dati[mese_riferimento].copy()

            # Calcola numero giorni necessari in base al massimo giornaliero
            giorni_necessari = math.ceil(num_colazioni / MAX_PAX_GIORNALIERI)
            colazioni_giornaliere = round(num_colazioni / giorni_necessari, 2)

            # Mostra info su distribuzione colazioni
            st.info(f"Per {num_colazioni} colazioni servono almeno {giorni_necessari} giorni (massimo {MAX_PAX_GIORNALIERI} pax/giorno).\n"
                   f"Media giornaliera stimata: {colazioni_giornaliere} colazioni/giorno.")

            # Filtra prodotti
            mask = df_mese['Coefficiente'] > 0
            if escludere_prodotti:
                mask = mask & (~df_mese['Categoria'].isin(escludere_prodotti))

            df_mese_filtrato = df_mese[mask].copy()

            # Ottieni dati sui costi dai dati di consumo
            df_consumi = dati.get('consumi', None)

            if not df_mese_filtrato.empty:
                # Calcola consumo previsto
                df_mese_filtrato['Consumo Previsto'] = df_mese_filtrato['Coefficiente'] * num_colazioni

                # Arricchisci con dati di costo
                if df_consumi is not None:
                    # Prepara un mapping di prodotti
                    mapping_prodotti = {}
                    for _, row in df_consumi.iterrows():
                        desc = row['Descrizione']
                        if pd.notna(desc):
                            mapping_prodotti[desc] = {
                                'costo_medio': row['Euro Medio'],
                                'uma': row['U.M.A.'],
                                'umc': row['U.M.C.'],
                                'coeff_conv': row['Coeff Conv']
                            }

                    # Aggiungi colonne per il costo
                    df_mese_filtrato['Costo Unitario'] = 0.0
                    df_mese_filtrato['U.M.A.'] = ''
                    df_mese_filtrato['U.M.C.'] = ''
                    df_mese_filtrato['Costo Totale Previsto'] = 0.0

                    # Cerca corrispondenza tra prodotti e dati di costo
                    for idx, row in df_mese_filtrato.iterrows():
                        prodotto = row['Articolo']
                        for key, info in mapping_prodotti.items():
                            if pd.notna(prodotto) and pd.notna(key) and (prodotto.upper() in key.upper() or key.upper() in prodotto.upper()):
                                df_mese_filtrato.at[idx, 'Costo Unitario'] = info['costo_medio']
                                df_mese_filtrato.at[idx, 'U.M.A.'] = info['uma']
                                df_mese_filtrato.at[idx, 'U.M.C.'] = info['umc']
                                df_mese_filtrato.at[idx, 'Costo Teorico Consumo'] = info['costo_medio'] * row['Consumo Previsto'] / info['coeff_conv']
                                break

                # Applica buffer
                if buffer_percentuale > 0:
                    fattore_buffer = 1 + (buffer_percentuale / 100)
                    df_mese_filtrato['Quantità con Buffer'] = df_mese_filtrato['Consumo Previsto'] * fattore_buffer

                    # Per quantità piccole, assicura che il buffer aggiunga almeno 1 unità
                    df_mese_filtrato['Quantità con Buffer'] = df_mese_filtrato.apply(
                        lambda row: max(row['Quantità con Buffer'], row['Consumo Previsto'] + 1)
                        if row['Consumo Previsto'] < 10 and pd.notna(row.get('UDM')) and row['UDM'] in ['pz', 'kg', 'conf']
                        else row['Quantità con Buffer'],
                        axis=1
                    )
                else:
                    df_mese_filtrato['Quantità con Buffer'] = df_mese_filtrato['Consumo Previsto']

                # Calcola il costo dell'ordine con buffer
                if 'Costo Unitario' in df_mese_filtrato.columns:
                    df_mese_filtrato['Costo Ordine con Buffer'] = df_mese_filtrato['Quantità con Buffer'] * df_mese_filtrato['Costo Unitario']

                # Arrotonda quantità preservando l'effetto del buffer
                df_mese_filtrato['Quantità con Buffer'] = df_mese_filtrato.apply(
                    lambda row: math.ceil(row['Quantità con Buffer'])  # Arrotonda sempre per eccesso
                    if pd.notna(row.get('UDM')) and row['UDM'] in ['pz', 'kg', 'conf']
                    else round(row['Quantità con Buffer'], 2),
                    axis=1
                )

                # Inizializza le colonne 'Giacenza' e 'Da Ordinare'
                df_mese_filtrato['Giacenza'] = 0.0
                df_mese_filtrato['Da Ordinare'] = 0.0

                if include_giacenze:
                    st.subheader("Carica il file Excel con le Giacenze")
                    uploaded_file = st.file_uploader("Scegli il file giacenze_magazzino.xlsx", type=['xlsx', 'xls'])

                    if uploaded_file is not None:
                        try:
                            # Legge il file excel usando la colonna 'Magazz.' e gestendo i decimali con la virgola
                            df_giacenze = pd.read_excel(
                                uploaded_file,
                                usecols=['Descrizione', 'Magazz.'], # Leggi solo le colonne necessarie
                                decimal=','                      # Imposta la virgola come separatore decimale
                            )

                            # Rinomina le colonne per la logica successiva dello script
                            df_giacenze.columns = ['Articolo', 'Giacenza']

                            # Converte la colonna Giacenza in numerico, gestendo errori
                            df_giacenze['Giacenza'] = pd.to_numeric(df_giacenze['Giacenza'], errors='coerce')

                            # Sostituisce i valori non numerici con 0
                            df_giacenze['Giacenza'] = df_giacenze['Giacenza'].fillna(0)

                            # Unisce i dati delle giacenze con il dataframe principale
                            df_mese_filtrato = pd.merge(
                                df_mese_filtrato.drop(columns=['Giacenza']),
                                df_giacenze,
                                on='Articolo',
                                how='left'
                            )

                            # Sostituisce le giacenze non trovate (NaN) con 0
                            df_mese_filtrato['Giacenza'] = df_mese_filtrato['Giacenza'].fillna(0)

                            st.success("File giacenze caricato usando la colonna 'Magazz.'!")

                        except Exception as e:
                            st.error(f"⚠️ Errore durante la lettura del file Excel: {e}")

                # Calcola la quantità da ordinare usando le giacenze appena caricate
                df_mese_filtrato['Da Ordinare'] = df_mese_filtrato['Quantità con Buffer'] - df_mese_filtrato['Giacenza']
                # Assicura che la quantità da ordinare non sia mai negativa
                df_mese_filtrato['Da Ordinare'] = df_mese_filtrato['Da Ordinare'].apply(lambda x: max(0, x))

                # Arrotonda la quantità da ordinare
                df_mese_filtrato['Da Ordinare'] = df_mese_filtrato.apply(
                    lambda row: round(row['Da Ordinare'])
                    if pd.notna(row.get('UDM')) and row['UDM'] in ['pz', 'kg', 'g', 'conf']
                    else round(row['Da Ordinare'], 2),
                    axis=1
                )

                # Mostra la tabella finale con i risultati
                st.subheader("Lista Prodotti da Ordinare")

                # Mostra info sul buffer applicato
                if buffer_percentuale > 0:
                    st.info(f"📊 Buffer del {buffer_percentuale}% applicato. Per quantità < 10 unità, il buffer garantisce almeno +1 unità.")
                cols_display = ['Categoria', 'Articolo', 'UDM', 'Coefficiente', 'Consumo Previsto', 'Quantità con Buffer']

                if include_giacenze:
                    cols_display.extend(['Giacenza', 'Da Ordinare'])

                # Aggiunge colonne di costo se disponibili
                costo_totale_ordine = 0
                if 'Costo Unitario' in df_mese_filtrato.columns:
                    cols_display.extend(['Costo Unitario'])
                    # Se NON ci sono giacenze, mostra il costo dell'ordine con buffer
                    if not include_giacenze:
                        cols_display.append('Costo Ordine con Buffer')
                        costo_totale_ordine = df_mese_filtrato['Costo Ordine con Buffer'].sum()
                        if costo_totale_ordine > 0:
                            st.metric("Costo Totale Ordine (con buffer)", f"{costo_totale_ordine:,.2f} €")
                    # Se CI SONO giacenze, calcola il costo effettivo da ordinare
                    elif 'Da Ordinare' in df_mese_filtrato.columns:
                        df_mese_filtrato['Costo Ordine Effettivo'] = df_mese_filtrato['Da Ordinare'] * df_mese_filtrato['Costo Unitario']
                        costo_totale_ordine = df_mese_filtrato['Costo Ordine Effettivo'].sum()
                        if costo_totale_ordine > 0:
                            st.metric("Costo Totale Ordine Effettivo", f"{costo_totale_ordine:,.2f} €")
                        cols_display.append('Costo Ordine Effettivo')

                # Aggiungi colonna per mostrare la differenza del buffer
                df_mese_filtrato['Buffer Applicato'] = df_mese_filtrato['Quantità con Buffer'] - df_mese_filtrato['Consumo Previsto']

                # Inserisci la colonna Buffer Applicato dopo Quantità con Buffer
                idx_buffer = cols_display.index('Quantità con Buffer') + 1
                cols_display.insert(idx_buffer, 'Buffer Applicato')

                st.dataframe(
                    df_mese_filtrato[cols_display].style.format({
                        'Coefficiente': '{:.4f}',
                        'Consumo Previsto': '{:,.2f}',
                        'Quantità con Buffer': '{:,.0f}',
                        'Buffer Applicato': '{:,.0f}',
                        'Giacenza': '{:,.2f}',
                        'Da Ordinare': '{:,.2f}',
                        'Costo Unitario': '{:,.2f} €',
                        'Costo Ordine con Buffer': '{:,.2f} €',
                        'Costo Ordine Effettivo': '{:,.2f} €'
                    }),
                    use_container_width=True,
                    height=400
                )

                # Lista ordinata per il report (solo se giacenze sono incluse)
                if include_giacenze and 'Da Ordinare' in df_mese_filtrato.columns:
                    st.subheader("Report Ordine")

                    # Filtra solo prodotti da ordinare
                    df_da_ordinare = df_mese_filtrato[df_mese_filtrato['Da Ordinare'] > 0].copy()

                    if not df_da_ordinare.empty:
                        # Ordina per categoria
                        df_da_ordinare = df_da_ordinare.sort_values(['Categoria', 'Articolo'])

                        # Crea report per categoria
                        categorie_ordine = df_da_ordinare['Categoria'].unique()

                        report_text = f"ORDINE COLAZIONI - {datetime.now().strftime('%d/%m/%Y')}\n"
                        report_text += f"Numero colazioni: {num_colazioni} (Buffer: {buffer_percentuale}%)\n"
                        report_text += f"Distribuzione: {colazioni_giornaliere} colazioni/giorno per {giorni_necessari} giorni\n\n"

                        for categoria in categorie_ordine:
                            report_text += f"--- {str(categoria).upper()} ---\n"
                            prodotti_cat = df_da_ordinare[df_da_ordinare['Categoria'] == categoria]

                            for _, row in prodotti_cat.iterrows():
                                costo_info = ""
                                if 'Costo Unitario' in row and pd.notna(row['Costo Unitario']) and row['Costo Unitario'] > 0:
                                    costo_info = f" - {row['Costo Unitario']:.2f}€/unità"

                                report_text += f"{row['Articolo']}: {row['Da Ordinare']} {row['UDM']}{costo_info}\n"

                            report_text += "\n"

                        if costo_totale_ordine > 0:
                            report_text += f"\nCosto totale stimato: {costo_totale_ordine:.2f} €\n"

                        # Mostra e permetti download
                        st.text_area("Report Ordine", report_text, height=300)

                        st.download_button(
                            "Scarica Report Ordine",
                            report_text,
                            f"ordine_colazioni_{datetime.now().strftime('%Y%m%d')}.txt",
                            key="download-report"
                        )

                        # Download CSV dell'ordine
                        csv_ordine = df_da_ordinare.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "Scarica Ordine come CSV",
                            csv_ordine,
                            f"ordine_colazioni_{datetime.now().strftime('%Y%m%d')}.csv",
                            "text/csv",
                            key='download-ordine-csv'
                        )


if __name__ == "__main__":
    main()
