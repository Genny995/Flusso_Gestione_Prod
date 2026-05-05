# Dashboard Processi Agrifood – Controllo Input

## 🧩 Descrizione

Questa applicazione consente di gestire e validare gli **input obbligatori per i processi SIAN** relativi al settore **vitivinicolo**, nell’ambito di un’applicazione di **digitalizzazione della filiera agrifood**.

L'app, sviluppata con **Streamlit**, garantisce coerenza tra:
- configurazioni definite in Excel
- regole di prodotto definite in un file JSON

Permette all’utente di:
- selezionare un processo
- visualizzare le informazioni generali obbligatorie
- selezionare prodotti e categorie
- visualizzare automaticamente gli input validi

---

## ⚙️ Funzionalità principali

- ✅ Selezione dinamica del processo  
- ✅ Visualizzazione delle **Informazioni Generali**  
- ✅ Gestione di processi con:
  - prodotti associati
  - solo informazioni generali (senza prodotti)  
- ✅ Selezione categoria per ciascun prodotto  
- ✅ Matching automatico tra:
  - input Excel  
  - campi JSON  
- ✅ Gestione robusta di:
  - spazi extra  
  - accenti (Unicode)  
  - differenze di formattazione  
- ✅ Gestione input sempre visibili (eccezioni di business)  

---

## 🗂️ Struttura del progetto

flusso_gestione_prod/
│
├── flusso_2.py # Script principale Streamlit
├── Check_Input_GestionePROD.xlsx # Configurazione processi e prodotti
├── output_prodotti_produzione_new.json # Definizione campi per categoria
├── requirements.txt # Dipendenze Python
├── runtime.txt # Versione Python (Streamlit Cloud)



---

## 📥 Input dati

### 📄 Excel – `Check_Input_GestionePROD.xlsx`

#### Foglio: **Tabella Processi**
Contiene:
- `Processo`
- `Informazione` (Informazioni generali, Prodotto_1, Prodotto_2, …)
- `Input`
- `Stato`
- `Tipologia`

#### Foglio: **Categorie per processo**
Contiene:
- `Processo`
- `Prodotto` (Prodotto_1, Prodotto_2, …)
- `Categoria`

---

### 📦 JSON – `output_prodotti_produzione_new.json`

Per ogni categoria di prodotto:
- nome prodotto (`prodotto`)
- lista campi (`campi`)

Esempio:

```json
{
  "prodotto": "Succo di uve in volume",
  "campi": [
    "Provenienza",
    "Varietà",
    "Quantità carico/scarico"
  ]
}

### Logica Applicativa

1) L’utente seleziona un processo
2) Vengono mostrate le informazioni generali
3) Se il processo prevede prodotti:
    - l’utente seleziona una categoria per ciascun prodotto
    - viene effettuato un match tra:
          - input Excel (per prodotto)
          - campi JSON (per categoria)
4) Vengono mostrati solo gli input validi


#### Eccezioni Gestite
Alcuni input vengono sempre mostrati anche se non presenti nel JSON:
- Categoria prodotto vitivinicolo/prodotto
- Nome prodotto
- Quantità carico/scarico
