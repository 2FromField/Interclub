import streamlit as st
import utils
from auth import check_pin

# 🔒 protéger cette page avec le PIN
if not check_pin(page_key="record", secret_path="record_lock.pin"):
    st.stop()

###############################################################
#                         LAYOUT                              #
###############################################################
st.set_page_config(page_title="Interclub AOB", layout="wide")

st.title("Highlights")
st.switch_page("pages/0_Accueil.py")  # Redirection vers la page d'accueil
