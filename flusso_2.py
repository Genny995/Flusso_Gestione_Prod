import streamlit as st
import pandas as pd
import json
import unicodedata
import re

# =========================
# LOAD DATI
# =========================

#@st.cache_data
def load_data():
    # "Carica i dati da Excel e JSON"

    tab_processi = pd.read_excel(
        "Check_Input_GestionePROD.xlsx",
        sheet_name="Tabella Processi"
    )

    categorie_processi = pd.read_excel(
        "Check_Input_GestionePROD.xlsx",
        sheet_name="Categorie per processo"
    )

    with open("output_prodotti_produzione_new.json") as f:
        json_data = json.load(f)

    return tab_processi, categorie_processi, json_data


tab_processi, categorie_processi, json_data = load_data()


# =========================
# NORMALIZZAZIONE DATI
# =========================

# "Funzione per pulire le stringhe"
def clean_text(x):
    if isinstance(x, str):
        x = x.replace("\u00A0", " ")  # NBSP Excel
        x = x.strip().rstrip(".").lower()

        # unicode (accenti)
        x = unicodedata.normalize("NFKD", x)
        x = "".join(c for c in x if not unicodedata.combining(c))

        # spazi multipli
        x = re.sub(r"\s+", " ", x)

        # trattini normalizzati
        x = re.sub(r"\s*-\s*", "-", x)

        return x
    return x


# "Pulizia colonne principali"
tab_processi["Input_clean"] = tab_processi["Input"].apply(clean_text)
tab_processi["Informazione_clean"] = tab_processi["Informazione"].apply(clean_text)

categorie_processi["Categoria_clean"] = categorie_processi["Categoria"].apply(clean_text)


# =========================
# PREPARAZIONE JSON
# =========================

# "Creiamo una mappa pulita: prodotto → lista campi"
json_map = {
    clean_text(item["prodotto"]): [clean_text(c) for c in item["campi"]]
    for item in json_data
}


# =========================
# INPUT SPECIALI (ECCEZIONE)
# =========================

# "Input da mostrare sempre, anche se non presenti nel JSON"
INPUT_SEMPRE_PRESENTI = [
    clean_text("Categoria prodotto vitivinicolo/prodotto"),
    clean_text("Nome prodotto"),
    clean_text("Quantità carico/scarico")
]


# =========================
# DASHBOARD
# =========================

st.title("Dashboard Processi Agrifood")


# =========================
# 1. SELEZIONE PROCESSO
# =========================

processi = tab_processi["Processo"].drop_duplicates().to_list()

proc = st.selectbox("Seleziona processo", processi)


if proc:

    # =========================
    # 2. FILTRO PER PROCESSO
    # =========================

    # "Filtriamo solo le righe del processo selezionato"
    filtro_proc = tab_processi[
        tab_processi["Processo"] == proc
    ]


    # =========================
    # 3. INFORMAZIONI GENERALI
    # =========================

    st.subheader("Informazioni Generali")

    # "Selezioniamo le informazioni generali"
    general_info = filtro_proc[
        filtro_proc["Informazione_clean"] == clean_text("Informazioni generali")
    ]

    for _, row in general_info.iterrows():
        st.write(
            f"**{row['Input']}** - {row['Stato']} ({row['Tipologia']})"
        )


    # =========================
    # 4. PRODOTTI ASSOCIATI
    # =========================

    st.subheader("Prodotti")

    prodotti_processi = categorie_processi[
        categorie_processi["Processo"] == proc
    ]

    lista_prodotti = prodotti_processi["Prodotto"].drop_duplicates().to_list()


    # =========================
    # 5. CICLO SUI PRODOTTI
    # =========================

    for prodotto in lista_prodotti:

        st.markdown(f"### {prodotto}")

        # =========================
        # 5.1 CATEGORIE DISPONIBILI (FIX APPLICATO)
        # =========================

        # "Filtriamo categorie per prodotto"
        categorie_disp = prodotti_processi[
            prodotti_processi["Prodotto"] == prodotto
        ].copy()

        # "Creiamo una colonna 'pulita' anche per la visualizzazione"
        categorie_disp["Categoria_label"] = categorie_disp["Categoria"].apply(clean_text)

        # "Rimuoviamo duplicati dopo la pulizia"
        categorie_disp = categorie_disp.drop_duplicates(subset=["Categoria_label"])

        # "Selectbox con valori puliti"
        categoria_label = st.selectbox(
            f"Seleziona categoria per {prodotto}",
            categorie_disp["Categoria_label"],
            key=prodotto
        )

        # "Usiamo direttamente il valore pulito"
        categoria_clean = categoria_label



        # =========================
        # 5.2 INPUT DA EXCEL
        # =========================

        # "Input associati a quel prodotto (Prodotto_i)"
        input_tab = filtro_proc[
            filtro_proc["Informazione_clean"] == clean_text(prodotto)
        ]


        # =========================
        # 5.3 INPUT DA JSON
        # =========================

        input_json = json_map.get(categoria_clean, [])


        # =========================
        # 5.4 MATCH + ECCEZIONE
        # =========================

        input_finali = input_tab[
            (input_tab["Input_clean"].isin(input_json)) |
            (input_tab["Input_clean"].isin(INPUT_SEMPRE_PRESENTI))
        ]


        # =========================
        # 5.5 OUTPUT
        # =========================

        st.write("Input disponibili:")

        if input_finali.empty:
            st.warning("Nessun input disponibile per questa combinazione")
        else:
            for _, row in input_finali.iterrows():
                st.write(
                    f"- **{row['Input']}** | {row['Stato']} | {row['Tipologia']}"
                )