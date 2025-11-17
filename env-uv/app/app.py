import streamlit as st
import utils
from auth import check_password

# Vérification du password
if not check_password():
    st.stop()

st.set_page_config(page_title="Interclub AOB", layout="wide")

st.title("Highlights")
st.switch_page("pages/0_Accueil.py")
