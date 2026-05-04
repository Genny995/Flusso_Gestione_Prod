import streamlit as st
import pandas as pd
import json
import unicodedata
import re

# =========================
# LOAD DATI
# =========================

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

def clean_text(x):
    if isinstance(x, str):
        x = x.replace("\u00A0", " ")
        x = x.strip().rstrip(".").lower()

        x = unicodedata.normalize("NFKD", x)
        x = "".join(c for c in x if not unicodedata.combining(c))

        x = re.sub(r"\s+", " ", x)
        x = re.sub(r"\s*-\s*", "-", x)

        return x
    return x


tab_processi["Input_clean"] = tab_processi["Input"].apply(clean_text)
tab_processi["Informazione_clean"] = tab_processi["Informazione"].apply(clean_text)

categorie_processi["Categoria_clean"] = categorie_processi["Categoria"].apply(clean_text)


# =========================
# PREPARAZIONE JSON
# =========================

json_map = {
    clean_text(item["prodotto"]): [clean_text(c) for c in item["campi"]]
    for item in json_data
}


# =========================
# INPUT SPECIALI
# =========================

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
    # 2. FILTRO PROCESSO
    # =========================

    filtro_proc = tab_processi[
        tab_processi["Processo"] == proc
    ]


    # =========================
    # 3. INFORMAZIONI GENERALI
    # =========================

    st.subheader("Informazioni Generali")

    general_info = filtro_proc[
        filtro_proc["Informazione_clean"] == clean_text("Informazioni generali")
    ]

    if general_info.empty:
        st.info("Nessuna informazione generale disponibile.")
    else:
        for _, row in general_info.iterrows():
            st.write(
                f"**{row['Input'].strip()}** - {row['Stato']} ({row['Tipologia']})"
            )


    # =========================
    # 4. PRODOTTI ASSOCIATI
    # =========================

    prodotti_processi = categorie_processi[
        categorie_processi["Processo"] == proc
    ]

    lista_prodotti = prodotti_processi["Prodotto"].drop_duplicates().to_list()


    # =========================
    # 5. GESTIONE CASO SENZA PRODOTTI
    # =========================

    if prodotti_processi.empty or len(lista_prodotti) == 0:

        st.info("Processo non SIAN, conterrà solo le informazioni generali (sheet 'NEW 2.3 Gestione Produzione').")

    else:

        st.subheader("Prodotti")

        # =========================
        # 6. CICLO PRODOTTI
        # =========================

        for prodotto in lista_prodotti:

            st.markdown(f"### {prodotto}")

            # =========================
            # 6.1 CATEGORIE DISPONIBILI
            # =========================

            categorie_disp = prodotti_processi[
                prodotti_processi["Prodotto"] == prodotto
            ].copy()

            categorie_disp["Categoria_label"] = categorie_disp["Categoria"].apply(clean_text)

            categorie_disp = categorie_disp.drop_duplicates(subset=["Categoria_label"])

            if categorie_disp.empty:
                st.warning("Nessuna categoria disponibile per questo prodotto")
                continue

            categoria_label = st.selectbox(
                f"Seleziona categoria per {prodotto}",
                categorie_disp["Categoria_label"],
                key=prodotto
            )

            categoria_clean = categoria_label


            # =========================
            # 6.2 INPUT EXCEL
            # =========================

            input_tab = filtro_proc[
                filtro_proc["Informazione_clean"] == clean_text(prodotto)
            ]

            if input_tab.empty:
                st.warning("Nessun input configurato in Excel per questo prodotto")
                continue


            # =========================
            # 6.3 INPUT JSON
            # =========================

            input_json = json_map.get(categoria_clean, [])

            if not input_json:
                st.warning("Categoria non trovata nel JSON o senza campi")
                continue


            # =========================
            # 6.4 MATCH
            # =========================

            input_finali = input_tab[
                (input_tab["Input_clean"].isin(input_json)) |
                (input_tab["Input_clean"].isin(INPUT_SEMPRE_PRESENTI))
            ]


            # =========================
            # 6.5 OUTPUT
            # =========================

            st.write("Input disponibili:")

            if input_finali.empty:
                st.warning("Nessun input disponibile per questa combinazione")
            else:
                for _, row in input_finali.iterrows():
                    st.write(
                        f"- **{row['Input'].strip()}** | {row['Stato']} | {row['Tipologia']}"
                    )