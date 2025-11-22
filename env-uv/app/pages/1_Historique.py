import streamlit as st
import pandas as pd
import utils

##################################################################
#                        VARIABLES                               #
##################################################################
EQUIPE = ["H2", "V3", "PR", "D2", "D3", "D5"]


##################################################################
#                        FONCTIONS                               #
##################################################################
@st.cache_data(ttl=30)  # Cache limitant la lecture
def load_interclub_table():
    """Chargement cacheté de la table 'INTERCLUB' hébergée sur un Google SHEET"""
    return utils.TABLE_INTERCLUB


def filter_by_result(
    df: pd.DataFrame, selected: list, home_col="aob_score", away_col="opponent_score"
) -> pd.DataFrame:
    """Filtrage des données basé sur l'issue de la rencontre (Victoire / Défaite / Match nul)

    Args:
        df (pd.DataFrame): Données brutes.
        selected (list): Choix issu(s) du dropdown multi-choix.
        home_col (str, optional): Nom de la colonne correspondant aux score de l'équipe de l'AOB ("aob_score" par défaut).
        away_col (str, optional): Nom de la colonne correspondant aux score de l'équipe adverse ("opponent_score" par défaut).
    """
    if not selected:  # si le dropdown est vide
        return df

    # Convertit en numériques (au cas où ce sont des strings)
    s_home = pd.to_numeric(df[home_col], errors="coerce")
    s_away = pd.to_numeric(df[away_col], errors="coerce")

    # -- Filtrage
    mask = False
    if "Victoire" in selected:
        mask |= s_home > s_away
    if "Défaite" in selected:
        mask |= s_home < s_away
    if "Nulle" in selected:
        mask |= s_home == s_away

    return df[mask].reset_index(drop=True)


##################################################################
#                           LAYOUT                               #
##################################################################
st.set_page_config(page_title="Historique", layout="wide")

c1, c2, c3 = st.columns([3, 1, 1], gap="small")
with c1:
    # -- Dropdown de filtrage d'équipe
    categorie = st.multiselect("Equipe(s)", EQUIPE, key="equipe")
with c2:
    # -- Dropdown des journées
    day = st.multiselect(
        "Journée(s)",
        list(utils.TABLE_INTERCLUB["journey"].unique()),
        key="day",
    )
with c3:
    # -- Dropdown des journées
    result = st.multiselect(
        "Résultat(s)",
        ["Victoire", "Défaite", "Nulle"],
        key="result",
    )


df = load_interclub_table()  # Chargement des données de la table 'INTERCLUB'

# -- Filtre basé sur la division des équipes
if categorie:  # si liste non vide
    df = df[df["division"].isin(categorie)].reset_index(
        drop=True
    )  # adapte la colonne si besoin

# -- Filtre basé sur la journée de rencontre des équipes
if day:
    df = df[df["journey"].isin(day)].reset_index(drop=True)

# -- Filtre basé sur l'issue des rencontres
if result:
    df = filter_by_result(utils.TABLE_INTERCLUB, result)

# -- Affichage du nombre de match trouvés en fonctions des filtres
st.caption(f"{len(df)} matchs trouvés")

# -- Affichage des rencontres avec leurs détails
for i in reversed(range(len(df))):
    if df["aob_score"].loc[i] > df["opponent_score"].loc[i]:  # Victoire de l'AOB
        utils.box_color_histo(
            df["date"].loc[i],  # date de la recontre (format iso "DD-MM-YYYY")
            df["journey"].loc[i],  # journée de la rencontre (ex: J2)
            df["id"].loc[i],  # identifiant unique de la recontre
            f'{df["aob_team"].loc[i]} ({df["division"].loc[i]})',  # nom de l'équipe de l'AOB (+ division)
            df["opponent_team"].loc[i],  # nom de l'équipe adverse
            df["aob_score"].loc[i],  # score de l'équipe de l'AOB
            df["opponent_score"].loc[i],  # score de l'équipe adverse
            box_style=utils.win_box,  # style CSS
        )
    elif (
        df["aob_score"].loc[i] < df["opponent_score"].loc[i]
    ):  # Victoire de l'adversaire
        utils.box_color_histo(
            df["date"].loc[i],
            df["journey"].loc[i],
            df["id"].loc[i],
            f'{df["aob_team"].loc[i]} ({df["division"].loc[i]})',
            df["opponent_team"].loc[i],
            df["aob_score"].loc[i],
            df["opponent_score"].loc[i],
            box_style=utils.loose_box,
        )
    else:  # Match nul
        utils.box_color_histo(
            df["date"].loc[i],
            df["journey"].loc[i],
            df["id"].loc[i],
            f'{df["aob_team"].loc[i]} ({df["division"].loc[i]})',
            df["opponent_team"].loc[i],
            df["aob_score"].loc[i],
            df["opponent_score"].loc[i],
            box_style=utils.draw_box,
        )
