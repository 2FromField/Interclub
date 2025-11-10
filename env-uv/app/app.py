import os
from datetime import datetime, date
import numpy as np
import pandas as pd
import datetime as dt
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import utils

# --- Configuration de la page
st.set_page_config(page_title="Interclub AOB", page_icon="🗂️", layout="wide")

st.title("Interclub AOB")

# Accès aux données


# Flash message après rerun
flash = st.session_state.pop("flash", None)
if flash:
    level, text = flash
    getattr(st, level)(text)


# --- Fonctions utilitaires
def winner(set1: str, set2: str, set3: str) -> None:
    """Déterminer l'équipe victorieuse de la rencontre"""
    winner_team = None
    #
    home_score = [
        int(set1.split("/")[0]),
        int(set2.split("/")[0]),
        int(set3.split("/")[0]),
    ]
    away_score = [
        int(set1.split("/")[1]),
        int(set2.split("/")[1]),
        int(set3.split("/")[1]),
    ]
    #
    if set3 == "0/0":
        if home_score[0] > away_score[0] and home_score[1] > away_score[1]:
            winner_team = "aob"
        else:
            winner_team = "opponent"
    else:
        if home_score[2] > away_score[2]:
            winner_team = "aob"
        else:
            winner_team = "opponent"

    return winner_team


# --- Accès aux google sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


@st.cache_resource
def _gspread_client():
    creds = Credentials.from_service_account_info(st.secrets["gcp"], scopes=SCOPES)
    return gspread.authorize(creds)


def _ws(sheet_id: str, worksheet: str):
    """Récupère une worksheet par nom, crée si absente."""
    gc = _gspread_client()
    sh = gc.open_by_key(sheet_id)
    try:
        return sh.worksheet(worksheet)
    except gspread.WorksheetNotFound:
        return sh.add_worksheet(title=worksheet, rows=1000, cols=26)


def read_sheet(worksheet="Feuille1") -> pd.DataFrame:
    ws = _ws(st.secrets["SHEET_ID"], worksheet)
    rows = ws.get_all_records()  # suppose la 1re ligne = en-têtes
    return pd.DataFrame(rows)


def to_native(v):
    # NaN/NaT -> ""
    if (
        v is None
        or (isinstance(v, float) and pd.isna(v))
        or (isinstance(v, str) and v == "nan")
    ):
        return ""
    if isinstance(v, (pd.Timestamp, dt.datetime, dt.date)):
        return v.isoformat()
    if isinstance(v, np.generic):  # numpy.int64, float64, bool_...
        return v.item()
    return v


def append_row_sheet(row: dict, worksheet="Feuille1"):
    ws = _ws(st.secrets["SHEET_ID"], worksheet)
    headers = ws.row_values(1)
    if not headers:
        headers = list(row.keys())
        ws.update("A1", [headers])

    # -> convertit chaque valeur en type natif
    values = [to_native(row.get(h, "")) for h in headers]
    ws.append_row(values, value_input_option="USER_ENTERED")


# --- Accès aux tables
INTERCLUB_TABLE = read_sheet("TABLE_INTERCLUB")
MATCHS_TABLE = read_sheet("TABLE_MATCHS")
PLAYERS_TABLE = read_sheet("TABLE_PLAYERS")

# --- Données brutes
EQUIPE = ["H2", "V3", "PR", "D2", "D3", "D5"]
EQUIPE_NOMS = ["AOB35-1", "AOB35-2", "AOB35-3", "AOB35-4"]


# --- Formulaire
def reset_sh1():
    # optionnel : oublie la sélection dépendante si la catégorie change
    st.session_state.pop("sh1_player_home", None)


categorie = st.selectbox("Catégorie", EQUIPE, key="categorie", on_change=reset_sh1)

# Formulaire
with st.form("match_record"):
    col2, col3 = st.columns(2)
    with col2:
        date_match = st.date_input("Date", value=date.today(), key="date")
    with col3:
        journey = st.number_input(
            "Journée", min_value=1, step=1, format="%d", key="journey"
        )

    col4, col5 = st.columns(2)
    with col4:
        aob_team = st.selectbox("Domicile", EQUIPE_NOMS, key="domicile")
    with col5:
        opponent_team = st.text_input("Adversaire (EXT)", key="exterieur")

    st.divider()

    if categorie != "H2":  # interclub MIXTE
        left_col, sep, right_col = st.columns([3, 0.4, 3])
        with sep:
            pass

        with left_col:
            # SH1
            utils.simple_match(PLAYERS_TABLE, categorie, "sh1")
            st.caption("-------------------")
            # SD1
            utils.simple_match(PLAYERS_TABLE, categorie, "sh2")
            st.caption("-------------------")
            # DH1
            utils.double_match(PLAYERS_TABLE, categorie, "dh")
            st.caption("-------------------")
            # MX1
            utils.double_match(PLAYERS_TABLE, categorie, "mx1")

        with right_col:
            # SH2
            utils.simple_match(PLAYERS_TABLE, categorie, "sd1")
            st.caption("-------------------")
            # SD2
            utils.simple_match(PLAYERS_TABLE, categorie, "sd2")
            st.caption("-------------------")
            # DH1
            utils.double_match(PLAYERS_TABLE, categorie, "dd")
            st.caption("-------------------")
            # MX2
            utils.double_match(PLAYERS_TABLE, categorie, "mx2")

    else:  # interclub HOMME
        left_col, sep, right_col = st.columns([3, 0.4, 3])
        with sep:
            pass

        with left_col:
            # SH1
            utils.simple_match(PLAYERS_TABLE, categorie, "sh1")
            st.caption("-------------------")
            # SD1
            utils.simple_match(PLAYERS_TABLE, categorie, "sh2")
            st.caption("-------------------")
            # DH1
            utils.double_match(PLAYERS_TABLE, categorie, "dh1")

        with right_col:
            # SH2
            utils.simple_match(PLAYERS_TABLE, categorie, "sh3")
            st.caption("-------------------")
            # SD2
            utils.simple_match(PLAYERS_TABLE, categorie, "sh4")
            st.caption("-------------------")
            # DH1
            utils.double_match(PLAYERS_TABLE, categorie, "dh2")

    submitted = st.form_submit_button("Enregistrer")

# Enregistrement
if submitted:
    if not opponent_team.strip():  # oublie nom d'équipe adverse
        st.error("Veuillez renseigner le champ **Adversaire**.")
    else:
        row_interclub = {
            # id;date;journey;division;aob_team;opponent_team;aob_score;opponent_score
            "id": len(INTERCLUB_TABLE) + 1,
            "date": str(date_match),
            "journey": f"j{journey}",
            "division": categorie,
            "aob_team": aob_team,
            "opponent_team": opponent_team,
            "aob_score": 5,
            "opponent_score": 2,
        }
        # Mise à jour de la table INTERCLUB
        try:
            append_row_sheet(row_interclub, "TABLE_INTERCLUB")
            st.session_state["flash"] = (
                "success",
                "✅ Mise à jour de la table INTERCLUB effectuée !",
            )
        except Exception as e:
            st.session_state["flash"] = (
                "error",
                f"❌ Impossible de mettre à jour la table INTERCLUB : {e}",
            )

        # Mise à jour de la table MATCHS
        try:
            if categorie != "H2":
                sh1_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "SH1",
                    "aob_player_id": utils.get_player_id(
                        PLAYERS_TABLE, st.session_state.get("sh1_aob_name")
                    ),
                    "opponent_player": st.session_state.get("sh1_opponent_name"),
                    "aob_rank": st.session_state.get("sh1_aob_rank"),
                    "opponent_rank": st.session_state.get("sh1_opponent_rank"),
                    "aob_pts": st.session_state.get("sh1_aob_pts"),
                    "opponent_pts": st.session_state.get("sh1_opponent_pts"),
                    "set1": f'{st.session_state.get("sh1_aob_set1")}/{st.session_state.get("sh1_opponent_set1")}',
                    "set2": f'{st.session_state.get("sh1_aob_set2")}/{st.session_state.get("sh1_opponent_set2")}',
                    "set3": f'{st.session_state.get("sh1_aob_set3")}/{st.session_state.get("sh1_opponent_set3")}',
                    "aob_grind": str(st.session_state.get("sh1_aob_grind")),
                    "opponent_grind": str(st.session_state.get("sh1_opponent_grind")),
                    "win": winner(
                        set1=f'{st.session_state.get("sh1_aob_set1")}/{st.session_state.get("sh1_opponent_set1")}',
                        set2=f'{st.session_state.get("sh1_aob_set2")}/{st.session_state.get("sh1_opponent_set2")}',
                        set3=f'{st.session_state.get("sh1_aob_set3")}/{st.session_state.get("sh1_opponent_set3")}',
                    ),
                }
                #
                sh2_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "SH2",
                    "aob_player_id": utils.get_player_id(
                        PLAYERS_TABLE, st.session_state.get("sh2_aob_name")
                    ),
                    "opponent_player": st.session_state.get("sh2_opponent_name"),
                    "aob_rank": st.session_state.get("sh2_aob_rank"),
                    "opponent_rank": st.session_state.get("sh2_opponent_rank"),
                    "aob_pts": st.session_state.get("sh2_aob_pts"),
                    "opponent_pts": st.session_state.get("sh2_opponent_pts"),
                    "set1": f'{st.session_state.get("sh2_aob_set1")}/{st.session_state.get("sh2_opponent_set1")}',
                    "set2": f'{st.session_state.get("sh2_aob_set2")}/{st.session_state.get("sh2_opponent_set2")}',
                    "set3": f'{st.session_state.get("sh2_aob_set3")}/{st.session_state.get("sh2_opponent_set3")}',
                    "aob_grind": str(st.session_state.get("sh2_aob_grind")),
                    "opponent_grind": str(st.session_state.get("sh2_opponent_grind")),
                    "win": winner(
                        set1=f'{st.session_state.get("sh2_aob_set1")}/{st.session_state.get("sh2_opponent_set1")}',
                        set2=f'{st.session_state.get("sh2_aob_set2")}/{st.session_state.get("sh2_opponent_set2")}',
                        set3=f'{st.session_state.get("sh2_aob_set3")}/{st.session_state.get("sh2_opponent_set3")}',
                    ),
                }
                #
                sd1_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "SD1",
                    "aob_player_id": utils.get_player_id(
                        PLAYERS_TABLE, st.session_state.get("sd1_aob_name")
                    ),
                    "opponent_player": st.session_state.get("sd1_opponent_name"),
                    "aob_rank": st.session_state.get("sd1_aob_rank"),
                    "opponent_rank": st.session_state.get("sd1_opponent_rank"),
                    "aob_pts": st.session_state.get("sd1_aob_pts"),
                    "opponent_pts": st.session_state.get("sd1_opponent_pts"),
                    "set1": f'{st.session_state.get("sd1_aob_set1")}/{st.session_state.get("sd1_opponent_set1")}',
                    "set2": f'{st.session_state.get("sd1_aob_set2")}/{st.session_state.get("sd1_opponent_set2")}',
                    "set3": f'{st.session_state.get("sd1_aob_set3")}/{st.session_state.get("sd1_opponent_set3")}',
                    "aob_grind": str(st.session_state.get("sd1_aob_grind")),
                    "opponent_grind": str(st.session_state.get("sd1_opponent_grind")),
                    "win": winner(
                        set1=f'{st.session_state.get("sd1_aob_set1")}/{st.session_state.get("sd1_opponent_set1")}',
                        set2=f'{st.session_state.get("sd1_aob_set2")}/{st.session_state.get("sd1_opponent_set2")}',
                        set3=f'{st.session_state.get("sd1_aob_set3")}/{st.session_state.get("sd1_opponent_set3")}',
                    ),
                }
                #
                sd2_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "SD2",
                    "aob_player_id": utils.get_player_id(
                        PLAYERS_TABLE, st.session_state.get("sd2_aob_name")
                    ),
                    "opponent_player": st.session_state.get("sd2_opponent_name"),
                    "aob_rank": st.session_state.get("sd2_aob_rank"),
                    "opponent_rank": st.session_state.get("sd2_opponent_rank"),
                    "aob_pts": st.session_state.get("sd2_aob_pts"),
                    "opponent_pts": st.session_state.get("sd2_opponent_pts"),
                    "set1": f'{st.session_state.get("sd2_aob_set1")}/{st.session_state.get("sd2_opponent_set1")}',
                    "set2": f'{st.session_state.get("sd2_aob_set2")}/{st.session_state.get("sd2_opponent_set2")}',
                    "set3": f'{st.session_state.get("sd2_aob_set3")}/{st.session_state.get("sd2_opponent_set3")}',
                    "aob_grind": str(st.session_state.get("sd2_aob_grind")),
                    "opponent_grind": str(st.session_state.get("sd2_opponent_grind")),
                    "win": winner(
                        set1=f'{st.session_state.get("sd2_aob_set1")}/{st.session_state.get("sd2_opponent_set1")}',
                        set2=f'{st.session_state.get("sd2_aob_set2")}/{st.session_state.get("sd2_opponent_set2")}',
                        set3=f'{st.session_state.get("sd2_aob_set3")}/{st.session_state.get("sd2_opponent_set3")}',
                    ),
                }
                #
                dh_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "DH",
                    "aob_player_id": f'{utils.get_player_id(PLAYERS_TABLE, st.session_state.get("dh_aob1_name"))}/{utils.get_player_id(PLAYERS_TABLE, st.session_state.get("dh_aob2_name"))}',
                    "opponent_player": f'{st.session_state.get("dh_opponent1_name")}/{st.session_state.get("dh_opponent2_name")}',
                    "aob_rank": f'{st.session_state.get("dh_aob1_rank")}/{st.session_state.get("dh_aob2_rank")}',
                    "opponent_rank": f'{st.session_state.get("dh_opponent1_rank")}/{st.session_state.get("dh_opponent2_rank")}',
                    "aob_pts": f'{st.session_state.get("dh_aob1_pts")}/{st.session_state.get("dh_aob2_pts")}',
                    "opponent_pts": f'{st.session_state.get("dh_opponent1_pts")}/{st.session_state.get("dh_opponent2_pts")}',
                    "set1": f'{st.session_state.get("dh_aob_set1")}/{st.session_state.get("dh_opponent_set1")}',
                    "set2": f'{st.session_state.get("dh_aob_set2")}/{st.session_state.get("dh_opponent_set2")}',
                    "set3": f'{st.session_state.get("dh_aob_set3")}/{st.session_state.get("dh_opponent_set3")}',
                    "aob_grind": f'{st.session_state.get("dh_aob1_grind")}/{st.session_state.get("dh_aob2_grind")}',
                    "opponent_grind": f'{st.session_state.get("dh_opponent1_grind")}/{st.session_state.get("dh_opponent2_grind")}',
                    "win": winner(
                        set1=f'{st.session_state.get("dh_aob_set1")}/{st.session_state.get("dh_opponent_set1")}',
                        set2=f'{st.session_state.get("dh_aob_set2")}/{st.session_state.get("dh_opponent_set2")}',
                        set3=f'{st.session_state.get("dh_aob_set3")}/{st.session_state.get("dh_opponent_set3")}',
                    ),
                }
                #
                dd_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "DD",
                    "aob_player_id": f'{utils.get_player_id(PLAYERS_TABLE, st.session_state.get("dd_aob1_name"))}/{utils.get_player_id(PLAYERS_TABLE, st.session_state.get("dd_aob2_name"))}',
                    "opponent_player": f'{st.session_state.get("dd_opponent1_name")}/{st.session_state.get("dd_opponent2_name")}',
                    "aob_rank": f'{st.session_state.get("dd_aob1_rank")}/{st.session_state.get("dd_aob2_rank")}',
                    "opponent_rank": f'{st.session_state.get("dd_opponent1_rank")}/{st.session_state.get("dd_opponent2_rank")}',
                    "aob_pts": f'{st.session_state.get("dd_aob1_pts")}/{st.session_state.get("dd_aob2_pts")}',
                    "opponent_pts": f'{st.session_state.get("dd_opponent1_pts")}/{st.session_state.get("dd_opponent2_pts")}',
                    "set1": f'{st.session_state.get("dd_aob_set1")}/{st.session_state.get("dd_opponent_set1")}',
                    "set2": f'{st.session_state.get("dd_aob_set2")}/{st.session_state.get("dd_opponent_set2")}',
                    "set3": f'{st.session_state.get("dd_aob_set3")}/{st.session_state.get("dd_opponent_set3")}',
                    "aob_grind": f'{st.session_state.get("dd_aob1_grind")}/{st.session_state.get("dd_aob2_grind")}',
                    "opponent_grind": f'{st.session_state.get("dd_opponent1_grind")}/{st.session_state.get("dd_opponent2_grind")}',
                    "win": winner(
                        set1=f'{st.session_state.get("dd_aob_set1")}/{st.session_state.get("dd_opponent_set1")}',
                        set2=f'{st.session_state.get("dd_aob_set2")}/{st.session_state.get("dd_opponent_set2")}',
                        set3=f'{st.session_state.get("dd_aob_set3")}/{st.session_state.get("dd_opponent_set3")}',
                    ),
                }
                #
                mx1_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "MX1",
                    "aob_player_id": f'{utils.get_player_id(PLAYERS_TABLE, st.session_state.get("mx1_aob1_name"))}/{utils.get_player_id(PLAYERS_TABLE, st.session_state.get("mx1_aob2_name"))}',
                    "opponent_player": f'{st.session_state.get("mx1_opponent1_name")}/{st.session_state.get("mx1_opponent2_name")}',
                    "aob_rank": f'{st.session_state.get("mx1_aob1_rank")}/{st.session_state.get("mx1_aob2_rank")}',
                    "opponent_rank": f'{st.session_state.get("mx1_opponent1_rank")}/{st.session_state.get("mx1_opponent2_rank")}',
                    "aob_pts": f'{st.session_state.get("mx1_aob1_pts")}/{st.session_state.get("mx1_aob2_pts")}',
                    "opponent_pts": f'{st.session_state.get("mx1_opponent1_pts")}/{st.session_state.get("mx1_opponent2_pts")}',
                    "set1": f'{st.session_state.get("mx1_aob_set1")}/{st.session_state.get("mx1_opponent_set1")}',
                    "set2": f'{st.session_state.get("mx1_aob_set2")}/{st.session_state.get("mx1_opponent_set2")}',
                    "set3": f'{st.session_state.get("mx1_aob_set3")}/{st.session_state.get("mx1_opponent_set3")}',
                    "aob_grind": f'{st.session_state.get("mx1_aob1_grind")}/{st.session_state.get("mx1_aob2_grind")}',
                    "opponent_grind": f'{st.session_state.get("mx1_opponent1_grind")}/{st.session_state.get("mx1_opponent2_grind")}',
                    "win": winner(
                        set1=f'{st.session_state.get("mx1_aob_set1")}/{st.session_state.get("mx1_opponent_set1")}',
                        set2=f'{st.session_state.get("mx1_aob_set2")}/{st.session_state.get("mx1_opponent_set2")}',
                        set3=f'{st.session_state.get("mx1_aob_set3")}/{st.session_state.get("mx1_opponent_set3")}',
                    ),
                }
                #
                mx2_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "MX2",
                    "aob_player_id": f'{utils.get_player_id(PLAYERS_TABLE, st.session_state.get("mx2_aob1_name"))}/{utils.get_player_id(PLAYERS_TABLE, st.session_state.get("mx2_aob2_name"))}',
                    "opponent_player": f'{st.session_state.get("mx2_opponent1_name")}/{st.session_state.get("mx2_opponent2_name")}',
                    "aob_rank": f'{st.session_state.get("mx2_aob1_rank")}/{st.session_state.get("mx2_aob2_rank")}',
                    "opponent_rank": f'{st.session_state.get("mx2_opponent1_rank")}/{st.session_state.get("mx2_opponent2_rank")}',
                    "aob_pts": f'{st.session_state.get("mx2_aob1_pts")}/{st.session_state.get("mx2_aob2_pts")}',
                    "opponent_pts": f'{st.session_state.get("mx2_opponent1_pts")}/{st.session_state.get("mx2_opponent2_pts")}',
                    "set1": f'{st.session_state.get("mx2_aob_set1")}/{st.session_state.get("mx2_opponent_set1")}',
                    "set2": f'{st.session_state.get("mx2_aob_set2")}/{st.session_state.get("mx2_opponent_set2")}',
                    "set3": f'{st.session_state.get("mx2_aob_set3")}/{st.session_state.get("mx2_opponent_set3")}',
                    "aob_grind": f'{st.session_state.get("mx2_aob1_grind")}/{st.session_state.get("mx2_aob2_grind")}',
                    "opponent_grind": f'{st.session_state.get("mx2_opponent1_grind")}/{st.session_state.get("mx2_opponent2_grind")}',
                    "win": winner(
                        set1=f'{st.session_state.get("mx2_aob_set1")}/{st.session_state.get("mx2_opponent_set1")}',
                        set2=f'{st.session_state.get("mx2_aob_set2")}/{st.session_state.get("mx2_opponent_set2")}',
                        set3=f'{st.session_state.get("mx2_aob_set3")}/{st.session_state.get("mx2_opponent_set3")}',
                    ),
                }
                #
                # Ajouter les nouvelles lignes
                # append_row_sheet("data/matchs.csv", sh2_row)
                append_row_sheet(sh1_row, "TABLE_MATCHS")
                append_row_sheet(sh2_row, "TABLE_MATCHS")
                append_row_sheet(sd1_row, "TABLE_MATCHS")
                append_row_sheet(sd2_row, "TABLE_MATCHS")
                append_row_sheet(dh_row, "TABLE_MATCHS")
                append_row_sheet(dd_row, "TABLE_MATCHS")
                append_row_sheet(mx1_row, "TABLE_MATCHS")
                append_row_sheet(mx2_row, "TABLE_MATCHS")
                #
                st.session_state["flash"] = ("success", "✅ Enregistrement effectué !")
                st.rerun()
            #
            else:
                sh1_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "SH1",
                    "aob_player_id": utils.get_player_id(
                        PLAYERS_TABLE, st.session_state.get("sh1_aob_name")
                    ),
                    "opponent_player": st.session_state.get("sh1_opponent_name"),
                    "aob_rank": st.session_state.get("sh1_aob_rank"),
                    "opponent_rank": st.session_state.get("sh1_opponent_rank"),
                    "aob_pts": st.session_state.get("sh1_aob_pts"),
                    "opponent_pts": st.session_state.get("sh1_opponent_pts"),
                    "set1": f'{st.session_state.get("sh1_aob_set1")}/{st.session_state.get("sh1_opponent_set1")}',
                    "set2": f'{st.session_state.get("sh1_aob_set2")}/{st.session_state.get("sh1_opponent_set2")}',
                    "set3": f'{st.session_state.get("sh1_aob_set3")}/{st.session_state.get("sh1_opponent_set3")}',
                    "aob_grind": str(st.session_state.get("sh1_aob_grind")),
                    "opponent_grind": str(st.session_state.get("sh1_opponent_grind")),
                    "win": winner(
                        set1=f'{st.session_state.get("sh1_aob_set1")}/{st.session_state.get("sh1_opponent_set1")}',
                        set2=f'{st.session_state.get("sh1_aob_set2")}/{st.session_state.get("sh1_opponent_set2")}',
                        set3=f'{st.session_state.get("sh1_aob_set3")}/{st.session_state.get("sh1_opponent_set3")}',
                    ),
                }
                #
                sh2_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "SH2",
                    "aob_player_id": utils.get_player_id(
                        PLAYERS_TABLE, st.session_state.get("sh2_aob_name")
                    ),
                    "opponent_player": st.session_state.get("sh2_opponent_name"),
                    "aob_rank": st.session_state.get("sh2_aob_rank"),
                    "opponent_rank": st.session_state.get("sh2_opponent_rank"),
                    "aob_pts": st.session_state.get("sh2_aob_pts"),
                    "opponent_pts": st.session_state.get("sh2_opponent_pts"),
                    "set1": f'{st.session_state.get("sh2_aob_set1")}/{st.session_state.get("sh2_opponent_set1")}',
                    "set2": f'{st.session_state.get("sh2_aob_set2")}/{st.session_state.get("sh2_opponent_set2")}',
                    "set3": f'{st.session_state.get("sh2_aob_set3")}/{st.session_state.get("sh2_opponent_set3")}',
                    "aob_grind": str(st.session_state.get("sh2_aob_grind")),
                    "opponent_grind": str(st.session_state.get("sh2_opponent_grind")),
                    "win": winner(
                        set1=f'{st.session_state.get("sh2_aob_set1")}/{st.session_state.get("sh2_opponent_set1")}',
                        set2=f'{st.session_state.get("sh2_aob_set2")}/{st.session_state.get("sh2_opponent_set2")}',
                        set3=f'{st.session_state.get("sh2_aob_set3")}/{st.session_state.get("sh2_opponent_set3")}',
                    ),
                }
                #
                sh3_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "SH3",
                    "aob_player_id": utils.get_player_id(
                        PLAYERS_TABLE, st.session_state.get("sh3_aob_name")
                    ),
                    "opponent_player": st.session_state.get("sh3_opponent_name"),
                    "aob_rank": st.session_state.get("sh3_aob_rank"),
                    "opponent_rank": st.session_state.get("sh3_opponent_rank"),
                    "aob_pts": st.session_state.get("sh3_aob_pts"),
                    "opponent_pts": st.session_state.get("sh3_opponent_pts"),
                    "set1": f'{st.session_state.get("sh3_aob_set1")}/{st.session_state.get("sh3_opponent_set1")}',
                    "set2": f'{st.session_state.get("sh3_aob_set2")}/{st.session_state.get("sh3_opponent_set2")}',
                    "set3": f'{st.session_state.get("sh3_aob_set3")}/{st.session_state.get("sh3_opponent_set3")}',
                    "aob_grind": str(st.session_state.get("sh3_aob_grind")),
                    "opponent_grind": str(st.session_state.get("sh3_opponent_grind")),
                    "win": winner(
                        set1=f'{st.session_state.get("sh3_aob_set1")}/{st.session_state.get("sh3_opponent_set1")}',
                        set2=f'{st.session_state.get("sh3_aob_set2")}/{st.session_state.get("sh3_opponent_set2")}',
                        set3=f'{st.session_state.get("sh3_aob_set3")}/{st.session_state.get("sh3_opponent_set3")}',
                    ),
                }
                #
                sh4_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "SH4",
                    "aob_player_id": utils.get_player_id(
                        PLAYERS_TABLE, st.session_state.get("sh4_aob_name")
                    ),
                    "opponent_player": st.session_state.get("sh4_opponent_name"),
                    "aob_rank": st.session_state.get("sh4_aob_rank"),
                    "opponent_rank": st.session_state.get("sh4_opponent_rank"),
                    "aob_pts": st.session_state.get("sh4_aob_pts"),
                    "opponent_pts": st.session_state.get("sh4_opponent_pts"),
                    "set1": f'{st.session_state.get("sh4_aob_set1")}/{st.session_state.get("sh4_opponent_set1")}',
                    "set2": f'{st.session_state.get("sh4_aob_set2")}/{st.session_state.get("sh4_opponent_set2")}',
                    "set3": f'{st.session_state.get("sh4_aob_set3")}/{st.session_state.get("sh4_opponent_set3")}',
                    "aob_grind": str(st.session_state.get("sh4_aob_grind")),
                    "opponent_grind": str(st.session_state.get("sh4_opponent_grind")),
                    "win": winner(
                        set1=f'{st.session_state.get("sh4_aob_set1")}/{st.session_state.get("sh4_opponent_set1")}',
                        set2=f'{st.session_state.get("sh4_aob_set2")}/{st.session_state.get("sh4_opponent_set2")}',
                        set3=f'{st.session_state.get("sh4_aob_set3")}/{st.session_state.get("sh4_opponent_set3")}',
                    ),
                }
                #
                dh1_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "DH1",
                    "aob_player_id": f'{utils.get_player_id(PLAYERS_TABLE, st.session_state.get("dh1_aob1_name"))}/{utils.get_player_id(PLAYERS_TABLE, st.session_state.get("dh1_aob2_name"))}',
                    "opponent_player": f'{st.session_state.get("dh1_opponent1_name")}/{st.session_state.get("dh1_opponent2_name")}',
                    "aob_rank": f'{st.session_state.get("dh1_aob1_rank")}/{st.session_state.get("dh1_aob2_rank")}',
                    "opponent_rank": f'{st.session_state.get("dh1_opponent1_rank")}/{st.session_state.get("dh1_opponent2_rank")}',
                    "aob_pts": f'{st.session_state.get("dh1_aob1_pts")}/{st.session_state.get("dh1_aob2_pts")}',
                    "opponent_pts": f'{st.session_state.get("dh1_opponent1_pts")}/{st.session_state.get("dh1_opponent2_pts")}',
                    "set1": f'{st.session_state.get("dh1_aob_set1")}/{st.session_state.get("dh1_opponent_set1")}',
                    "set2": f'{st.session_state.get("dh1_aob_set2")}/{st.session_state.get("dh1_opponent_set2")}',
                    "set3": f'{st.session_state.get("dh1_aob_set3")}/{st.session_state.get("dh1_opponent_set3")}',
                    "aob_grind": f'{st.session_state.get("dh1_aob1_grind")}/{st.session_state.get("dh1_aob2_grind")}',
                    "opponent_grind": f'{st.session_state.get("dh1_opponent1_grind")}/{st.session_state.get("dh1_opponent2_grind")}',
                    "win": winner(
                        set1=f'{st.session_state.get("dh1_aob_set1")}/{st.session_state.get("dh1_opponent_set1")}',
                        set2=f'{st.session_state.get("dh1_aob_set2")}/{st.session_state.get("dh1_opponent_set2")}',
                        set3=f'{st.session_state.get("dh1_aob_set3")}/{st.session_state.get("dh1_opponent_set3")}',
                    ),
                }
                #
                dh2_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "DH2",
                    "aob_player_id": f'{utils.get_player_id(PLAYERS_TABLE, st.session_state.get("dh2_aob1_name"))}/{utils.get_player_id(PLAYERS_TABLE, st.session_state.get("dh2_aob2_name"))}',
                    "opponent_player": f'{st.session_state.get("dh2_opponent1_name")}/{st.session_state.get("dh2_opponent2_name")}',
                    "aob_rank": f'{st.session_state.get("dh2_aob1_rank")}/{st.session_state.get("dh2_aob2_rank")}',
                    "opponent_rank": f'{st.session_state.get("dh2_opponent1_rank")}/{st.session_state.get("dh2_opponent2_rank")}',
                    "aob_pts": f'{st.session_state.get("dh2_aob1_pts")}/{st.session_state.get("dh2_aob2_pts")}',
                    "opponent_pts": f'{st.session_state.get("dh2_opponent1_pts")}/{st.session_state.get("dh2_opponent2_pts")}',
                    "set1": f'{st.session_state.get("dh2_aob_set1")}/{st.session_state.get("dh2_opponent_set1")}',
                    "set2": f'{st.session_state.get("dh2_aob_set2")}/{st.session_state.get("dh2_opponent_set2")}',
                    "set3": f'{st.session_state.get("dh2_aob_set3")}/{st.session_state.get("dh2_opponent_set3")}',
                    "aob_grind": f'{st.session_state.get("dh2_aob1_grind")}/{st.session_state.get("dh2_aob2_grind")}',
                    "opponent_grind": f'{st.session_state.get("dh2_opponent1_grind")}/{st.session_state.get("dh2_opponent2_grind")}',
                    "win": winner(
                        set1=f'{st.session_state.get("dh2_aob_set1")}/{st.session_state.get("dh2_opponent_set1")}',
                        set2=f'{st.session_state.get("dh2_aob_set2")}/{st.session_state.get("dh2_opponent_set2")}',
                        set3=f'{st.session_state.get("dh2_aob_set3")}/{st.session_state.get("dh2_opponent_set3")}',
                    ),
                }
                #
                # Ajouter les nouvelles lignes
                # append_row("data/matchs.csv", sh1_row)
                append_row_sheet(sh1_row, "TABLE_MATCHS")
                append_row_sheet(sh2_row, "TABLE_MATCHS")
                append_row_sheet(sh3_row, "TABLE_MATCHS")
                append_row_sheet(sh4_row, "TABLE_MATCHS")
                append_row_sheet(dh1_row, "TABLE_MATCHS")
                append_row_sheet(dh2_row, "TABLE_MATCHS")
                #
                st.session_state["flash"] = ("success", "✅ Enregistrement effectué !")
                st.rerun()
        except Exception as e:
            st.session_state["flash"] = ("error", f"❌ Impossible d'enregistrer : {e}")
