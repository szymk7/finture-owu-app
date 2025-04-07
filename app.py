
import streamlit as st
import PyPDF2
import os

st.set_page_config(page_title="Finture OWU", layout="wide")
st.title("📄 Inteligentna Porównywarka OWU - Finture")

BASE_DIR = "owu_files"
kategorie = ["komunikacyjne", "majątkowe", "na_zycie"]
selected_category = st.sidebar.selectbox("📁 Wybierz kategorię OWU:", kategorie)

folder_path = os.path.join(BASE_DIR, selected_category)
files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

@st.cache_data
def parse_pdf(path):
    reader = PyPDF2.PdfReader(path)
    text = "\n".join([p.extract_text() or "" for p in reader.pages])
    return text

parsed_texts = {}
for file in files:
    full_path = os.path.join(folder_path, file)
    parsed_texts[file] = parse_pdf(full_path)

st.subheader("🔍 Wyszukiwanie słów kluczowych")
query = st.text_input("Wpisz frazę:")
if query:
    for file, text in parsed_texts.items():
        if query.lower() in text.lower():
            st.success(f"✅ Znaleziono w: {file}")
        else:
            st.info(f"❌ Brak w: {file}")

st.subheader("📊 Porównywarka OWU")
col1, col2 = st.columns(2)
file1 = col1.selectbox("📄 Dokument 1", files)
file2 = col2.selectbox("📄 Dokument 2", files, index=1 if len(files) > 1 else 0)

if st.button("🔁 Porównaj"):
    text1 = parsed_texts[file1].splitlines()
    text2 = parsed_texts[file2].splitlines()
    diff = set(text1).symmetric_difference(text2)
    for line in diff:
        st.write(f"- {line}")

st.subheader("🤖 AI-asystent (placeholder)")
need = st.text_area("Opisz potrzeby klienta:")
if st.button("🧠 Generuj rekomendację"):
    st.info("🧠 Rekomendacja na podstawie potrzeb klienta (AI placeholder)")
    st.markdown(f"Szanowny Kliencie,\nNa podstawie opisu: *{need}*\nrekomendujemy najlepsze OWU z kategorii **{selected_category}**.")

    mail = f"Szanowny Kliencie,\n\nRekomendujemy produkt OWU dopasowany do potrzeb: {need}\n\nZespół Finture"
    st.download_button("📤 Pobierz e-mail", mail, file_name="rekomendacja.txt")

st.subheader("🧾 Checklisty klienta")
if "checklist" not in st.session_state:
    st.session_state.checklist = []
with st.form("checklist_form"):
    note = st.text_input("Dodaj notatkę:")
    add_note = st.form_submit_button("➕ Dodaj")
    if add_note and note:
        st.session_state.checklist.append(note)
for i, note in enumerate(st.session_state.checklist):
    st.write(f"{i+1}. {note}")

with st.expander("📘 Słownik pojęć"):
    st.markdown("""
    - **Franszyza redukcyjna** – minimalna kwota szkody...
    - **Udział własny** – część szkody pokrywana przez klienta...
    - **AC (AutoCasco)** – ubezpieczenie od uszkodzeń i kradzieży...
    """)
