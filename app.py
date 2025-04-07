import streamlit as st
import PyPDF2
from pathlib import Path
import os
import openai

# KONFIGURACJA OPENAI (wstaw swój klucz API)
openai.api_key = st.secrets.get("openai_api_key", "")

# Ustawienia aplikacji
st.set_page_config(page_title="Finture - Porownywarka OWU", layout="wide")
st.title("📄 Inteligentna Porownywarka OWU")

# Folder na OWU
OWU_FOLDER = "owu_files"
os.makedirs(OWU_FOLDER, exist_ok=True)

# Sesja: zaczytane OWU i checklisty
if "owu_files" not in st.session_state:
    st.session_state.owu_files = []
if "checklist" not in st.session_state:
    st.session_state.checklist = []

# Upload nowych OWU
st.subheader("📥 Dodaj nowe OWU (PDF)")
uploaded = st.file_uploader("Przeciągnij pliki lub wybierz z dysku", type="pdf", accept_multiple_files=True)
for file in uploaded:
    filepath = os.path.join(OWU_FOLDER, file.name)
    with open(filepath, "wb") as f:
        f.write(file.read())
    if file.name not in st.session_state.owu_files:
        st.session_state.owu_files.append(file.name)

# Lista dostępnych OWU
st.sidebar.header("📂 Dostępne dokumenty OWU")
all_files = sorted([f for f in os.listdir(OWU_FOLDER) if f.endswith(".pdf")])
for f in all_files:
    st.sidebar.markdown(f"✅ {f}")

# Parser PDF → tekst
@st.cache_data(show_spinner=False)
def parse_pdf(path):
    reader = PyPDF2.PdfReader(path)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

# Zaczytaj wszystkie teksty OWU
parsed_texts = {file: parse_pdf(os.path.join(OWU_FOLDER, file)) for file in all_files}

# Wyszukiwarka słów kluczowych
st.subheader("🔍 Wyszukiwanie słów kluczowych")
query = st.text_input("Wpisz słowo lub frazę")
if query:
    for file, text in parsed_texts.items():
        if query.lower() in text.lower():
            st.success(f"✅ Fraza **{query}** znaleziona w: {file}")
        else:
            st.info(f"❌ Brak frazy w: {file}")

# Porownywarka dwóch OWU
st.subheader("📊 Porównywarka dokumentów")
col1, col2 = st.columns(2)
file1 = col1.selectbox("Dokument 1", all_files, key="doc1")
file2 = col2.selectbox("Dokument 2", all_files, index=1 if len(all_files) > 1 else 0, key="doc2")

if st.button("🔁 Porównaj dokumenty"):
    text1 = parsed_texts[file1].splitlines()
    text2 = parsed_texts[file2].splitlines()
    diff = set(text1).symmetric_difference(set(text2))
    st.markdown("### 🔍 Różnice pomiędzy OWU:")
    for line in diff:
        st.write(f"- {line}")

# Asystent AI – rekomendacja
st.subheader("🤖 Zaproponuj produkt (AI)")
need = st.text_area("Wpisz potrzeby klienta:", placeholder="Np. klient chce auto zastępcze, holowanie za granicą...")
if st.button("🧠 Wygeneruj rekomendację") and need:
    with st.spinner("Generuję propozycję..."):
        prompt = f"Na podstawie potrzeb klienta: {need}, wybierz najlepszy produkt OWU z poniższych dokumentów i uzasadnij.\n\nLista OWU:\n" + ", ".join(all_files)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        rec = response.choices[0].message.content
        st.markdown("### ✅ Rekomendacja AI")
        st.write(rec)

        # Automatyczny e-mail
        st.markdown("### 📧 E-mail do klienta")
        mail = f"Szanowny Kliencie,\n\nNa podstawie podanych potrzeb rekomendujemy produkt ubezpieczeniowy:\n\n{rec}\n\nPozdrawiamy,\nZespół Finture"
        st.code(mail)
        st.download_button("📤 Pobierz e-mail jako TXT", mail, file_name="rekomendacja.txt")

# Checklisty klienta
st.subheader("🧾 Checklisty klienta")
with st.form("checklist_form"):
    task = st.text_input("Dodaj notatkę lub zadanie (np. brak zgody, brak danych)")
    submitted = st.form_submit_button("➕ Dodaj do checklisty")
    if submitted and task:
        st.session_state.checklist.append(task)

if st.session_state.checklist:
    st.markdown("### 📋 Lista notatek i zadań")
    for idx, item in enumerate(st.session_state.checklist):
        st.write(f"{idx+1}. {item}")

# Slownik pojec
with st.expander("📘 Słownik pojęć ubezpieczeniowych"):
    st.markdown("""
    - **Franszyza redukcyjna** – minimalna kwota szkody, za którą nie przysługuje odszkodowanie.  
    - **Udział własny** – część szkody pokrywana przez ubezpieczonego.  
    - **AC (AutoCasco)** – dobrowolne ubezpieczenie pojazdu od uszkodzeń i kradzieży.  
    - **NNW** – ubezpieczenie od następstw nieszczęśliwych wypadków.  
    - **Sumy ubezpieczenia** – maksymalna wartość odszkodowania.  
    - **Wyłączenia odpowiedzialności** – sytuacje, w których ubezpieczyciel nie wypłaci świadczenia.  
    """)
