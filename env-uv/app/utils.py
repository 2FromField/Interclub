import streamlit as st
import pandas as pd
import numpy as np
from streamlit_extras.stylable_container import stylable_container
import gspread
from google.oauth2.service_account import Credentials
import datetime as dt
import yaml
from pathlib import Path

# -- Définition de l'environnement
BASE_DIR = Path(__file__).resolve().parent  # /.../app
PROJECT_ROOT = BASE_DIR.parent  # /.../ (un niveau au-dessus)
CONFIG_PATH = PROJECT_ROOT / "config.yaml"  # /.../config.yaml

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)
env = config["env"]  # "dev" ou "prod"


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


# def read_sheet(worksheet="Feuille1") -> pd.DataFrame:
#     ws = _ws(st.secrets["SHEET_ID"], worksheet)
#     rows = ws.get_all_records()  # suppose la 1re ligne = en-têtes
#     return pd.DataFrame(rows)


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
    ws = _ws(st.secrets["prod"]["SHEET_ID"], worksheet)
    headers = ws.row_values(1)
    if not headers:
        headers = list(row.keys())
        ws.update("A1", [headers])

    # -> convertit chaque valeur en type natif
    values = [to_native(row.get(h, "")) for h in headers]
    ws.append_row(values, value_input_option="USER_ENTERED")


@st.cache_data
def load_table(env: str, table: str) -> pd.DataFrame:
    """Chargement des données dev/prod, mis en cache par Streamlit."""
    if env == "prod":
        # SHEET_ID vient de .streamlit/secrets.toml, section [prod]
        sheet_id = st.secrets["prod"]["SHEET_ID"]

        # à adapter : ici tu utilises _ws pour récupérer la worksheet
        ws = _ws(sheet_id, table)  # ou autre nom d’onglet
        rows = ws.get_all_records()  # suppose 1re ligne = en-têtes
        df = pd.DataFrame(rows)

    elif env == "dev":
        # TABLE_INTERCLUB / TABLE_MATCHS / TABLE_PLAYERS viennent de [dev]
        paths = st.secrets["dev"]
        df = pd.read_csv(paths[table], sep=";")

    else:
        raise ValueError(f"Environnement inconnu : {env}")

    return df


# -- Téléchargement des données
TABLE_INTERCLUB = load_table(env, "TABLE_INTERCLUB")
TABLE_MATCHS = load_table(env, "TABLE_MATCHS")
TABLE_PLAYERS = load_table(env, "TABLE_PLAYERS")

# Données brutes
CLASSEMENTS = [
    "N1",
    "N2",
    "N3",
    "R4",
    "R5",
    "R6",
    "D7",
    "D8",
    "D9",
    "P10",
    "P11",
    "P12",
    "NC",
]


# Créer un dataframe à partir des dictionnaires de chaque match
def create_df_from_dict(dicts: list):
    rows = dicts

    # --- 2) Assigner des IDs uniques (évite d’avoir le même id partout)
    start_id = (int(TABLE_MATCHS["id"].max()) if not TABLE_MATCHS.empty else 0) + 1
    for i, r in enumerate(rows):
        r["id"] = start_id + i

    # --- 3) DataFrame final
    df_matches = pd.DataFrame(rows)

    # (optionnel) ordonner les colonnes
    cols = [
        "id",
        "type_match",
        "aob_player_id",
        "opponent_player",
        "aob_rank",
        "opponent_rank",
        "aob_pts",
        "opponent_pts",
        "set1",
        "set2",
        "set3",
        "aob_grind",
        "opponent_grind",
        "win",
    ]
    df_matches = df_matches.reindex(columns=cols)
    return df_matches


# -- Match de simple (SH,SD)
def simple_match(table, categorie, match):
    (
        title_col_aob,
        player_col_aob,
        rank_col_aob,
        pts_col_aob,
        set1_col_aob,
        set2_col_aob,
        set3_col_aob,
        grind_col_aob,
    ) = st.columns([1, 3, 1.5, 1, 1, 1, 1, 1], gap="small")
    with title_col_aob:
        st.markdown(
            f'<p style="margin:0; color:cyan">{match.upper()}</p>',
            unsafe_allow_html=True,
        )
        st.caption("AOB")

    # --- filtre dépendant de 'categorie' ---
    categorie_norm = categorie.strip().upper()
    mask_div = (
        table["division"]
        .fillna("")
        .str.split("/")
        .apply(lambda xs: any(x.strip().upper() == categorie_norm for x in xs))
    )
    df_filtre = table.loc[mask_div].sort_values("name")

    with player_col_aob:
        gender = "H" if match in ["sh1", "sh2", "sh3", "sh4"] else "F"
        name_aob = st.selectbox(
            "Joueur(s)",
            df_filtre[(df_filtre["gender"] == gender)]["name"].to_list(),
            key=f"{match}_aob_name",
        )

    with rank_col_aob:
        rank_aob = st.selectbox(
            "Rang",
            CLASSEMENTS,
            key=f"{match}_aob_rank",
        )

    with pts_col_aob:
        pts_aob = st.number_input(
            "Points", min_value=400, step=1, format="%d", key=f"{match}_aob_pts"
        )

    with set1_col_aob:
        set1_aob = st.number_input(
            "Set 1", min_value=0, step=1, format="%d", key=f"{match}_aob_set1"
        )

    with set2_col_aob:
        set2_aob = st.number_input(
            "Set 2", min_value=0, step=1, format="%d", key=f"{match}_aob_set2"
        )

    with set3_col_aob:
        set3_aob = st.number_input(
            "Set 3", min_value=0, step=1, format="%d", key=f"{match}_aob_set3"
        )

    with grind_col_aob:
        grind_aob = st.text_input("+/-", key=f"{match}_aob_grind")

    #####

    (
        title_col_opponent,
        player_col_opponent,
        rank_col_opponent,
        pts_col_opponent,
        set1_col_opponent,
        set2_col_opponent,
        set3_col_opponent,
        grind_col_opponent,
    ) = st.columns([1, 3, 1.5, 1, 1, 1, 1, 1], gap="small")
    with title_col_opponent:
        pass
        st.caption("EXT")

    with player_col_opponent:
        opponent_name = st.text_input(
            "", key=f"{match}_opponent_name", label_visibility="collapsed"
        )

    with rank_col_opponent:
        opponent_rank = st.selectbox(
            "",
            options=CLASSEMENTS,
            key=f"{match}_opponent_rank",
            label_visibility="collapsed",
        )

    with pts_col_opponent:
        opponent_pts = st.number_input(
            "",
            min_value=400,
            step=1,
            format="%d",
            key=f"{match}_opponent_pts",
            label_visibility="collapsed",
        )

    with set1_col_opponent:
        opponent_set1 = st.number_input(
            "",
            min_value=0,
            step=1,
            format="%d",
            key=f"{match}_opponent_set1",
            label_visibility="collapsed",
        )

    with set2_col_opponent:
        opponent_set2 = st.number_input(
            "",
            min_value=0,
            step=1,
            format="%d",
            key=f"{match}_opponent_set2",
            label_visibility="collapsed",
        )

    with set3_col_opponent:
        opponent_set3 = st.number_input(
            "",
            min_value=0,
            step=1,
            format="%d",
            key=f"{match}_opponent_set3",
            label_visibility="collapsed",
        )

    with grind_col_opponent:
        grind_opponent = st.text_input(
            "+/-", key=f"{match}_opponent_grind", label_visibility="collapsed"
        )


# Match de double (DH,DD,MX)
def double_match(table, categorie, match):
    (
        title_col_aob1,
        player_col_aob1,
        rank_col_aob1,
        pts_col_aob1,
        set1_col_aob1,
        set2_col_aob1,
        set3_col_aob1,
        grind_col_aob1,
    ) = st.columns([1, 3, 1.5, 1, 1, 1, 1, 1], gap="small")
    with title_col_aob1:
        st.markdown(
            f'<p style="margin:0; color:cyan">{match.upper()}</p>',
            unsafe_allow_html=True,
        )
        st.caption("AOB")

    # --- filtre dépendant de 'categorie' ---
    categorie_norm = categorie.strip().upper()
    mask_div = (
        table["division"]
        .fillna("")
        .str.split("/")
        .apply(lambda xs: any(x.strip().upper() == categorie_norm for x in xs))
    )
    df_filtre = table.loc[mask_div].sort_values("name")

    with player_col_aob1:
        gender = "H" if match in ["dh", "dh1", "dh2", "mx1", "mx2", "mx"] else "F"
        name_aob1 = st.selectbox(
            "Joueur(s)",
            df_filtre[(df_filtre["gender"] == gender)]["name"].to_list(),
            key=f"{match}_aob1_name",
        )

    with rank_col_aob1:
        rank_aob1 = st.selectbox(
            "Rang",
            CLASSEMENTS,
            key=f"{match}_aob1_rank",
        )

    with pts_col_aob1:
        pts_aob1 = st.number_input(
            "Points", min_value=400, step=1, format="%d", key=f"{match}_aob1_pts"
        )

    with set1_col_aob1:
        set1_aob = st.markdown(
            f'<p style="margin:0; color:white">Set 1</p>',
            unsafe_allow_html=True,
        )

    with set2_col_aob1:
        set2_aob = st.markdown(
            f'<p style="margin:0; color:white">Set 2</p>',
            unsafe_allow_html=True,
        )

    with set3_col_aob1:
        set3_aob = st.markdown(
            f'<p style="margin:0; color:white">Set 3</p>',
            unsafe_allow_html=True,
        )

    with grind_col_aob1:
        grind_aob1 = st.text_input("+/-", key=f"{match}_aob1_grind")

    #####

    (
        title_col_aob2,
        player_col_aob2,
        rank_col_aob2,
        pts_col_aob2,
        set1_col_aob2,
        set2_col_aob2,
        set3_col_aob2,
        grind_col_aob2,
    ) = st.columns([1, 3, 1.5, 1, 1, 1, 1, 1], gap="small")
    with title_col_aob2:
        pass
        # st.caption("EXT")

    with player_col_aob2:
        gender = "H" if match in ["dh", "dh1", "dh2"] else "F"
        name_aob2 = st.selectbox(
            "",
            options=df_filtre[(df_filtre["gender"] == gender)]["name"].to_list(),
            key=f"{match}_aob2_name",
            label_visibility="collapsed",
        )

    with rank_col_aob2:
        rank_aob2 = st.selectbox(
            "",
            options=CLASSEMENTS,
            key=f"{match}_aob2_rank",
            label_visibility="collapsed",
        )

    with pts_col_aob2:
        pts_aob2 = st.number_input(
            "",
            min_value=400,
            step=1,
            format="%d",
            key=f"{match}_aob2_pts",
            label_visibility="collapsed",
        )

    with set1_col_aob2:
        set1_aob = st.number_input(
            "",
            min_value=0,
            step=1,
            format="%d",
            key=f"{match}_aob_set1",
            label_visibility="collapsed",
        )

    with set2_col_aob2:
        set2_aob = st.number_input(
            "",
            min_value=0,
            step=1,
            format="%d",
            key=f"{match}_aob_set2",
            label_visibility="collapsed",
        )

    with set3_col_aob2:
        set3_aob = st.number_input(
            "",
            min_value=0,
            step=1,
            format="%d",
            key=f"{match}_aob_set3",
            label_visibility="collapsed",
        )

    with grind_col_aob2:
        grind_aob2 = st.text_input(
            "+/-", key=f"{match}_aob2_grind", label_visibility="collapsed"
        )

    # Adversaires
    (
        title_col_opponent1,
        player_col_opponent1,
        rank_col_opponent1,
        pts_col_opponent1,
        set1_col_opponent1,
        set2_col_opponent1,
        set3_col_opponent1,
        grind_col_opponent1,
    ) = st.columns([1, 3, 1.5, 1, 1, 1, 1, 1], gap="small")
    with title_col_opponent1:
        st.caption("EXT")

    with player_col_opponent1:
        name_opponent1 = st.text_input(
            "", key=f"{match}_opponent1_name", label_visibility="collapsed"
        )

    with rank_col_opponent1:
        rank_opponent1 = st.selectbox(
            "", CLASSEMENTS, key=f"{match}_opponent1_rank", label_visibility="collapsed"
        )

    with pts_col_opponent1:
        pts_opponent1 = st.number_input(
            "",
            min_value=400,
            step=1,
            format="%d",
            key=f"{match}_opponent1_pts",
            label_visibility="collapsed",
        )

    with set1_col_opponent1:
        set1_opponent = st.number_input(
            "",
            min_value=0,
            step=1,
            format="%d",
            key=f"{match}_opponent_set1",
            label_visibility="collapsed",
        )

    with set2_col_opponent1:
        set2_opponent = st.number_input(
            "",
            min_value=0,
            step=1,
            format="%d",
            key=f"{match}_opponent_set2",
            label_visibility="collapsed",
        )

    with set3_col_opponent1:
        set3_opponent = st.number_input(
            "",
            min_value=0,
            step=1,
            format="%d",
            key=f"{match}_opponent_set3",
            label_visibility="collapsed",
        )

    with grind_col_opponent1:
        grind_opponent1 = st.text_input(
            "", key=f"{match}_opponent1_grind", label_visibility="collapsed"
        )

    #####

    (
        title_col_opponent2,
        player_col_opponent2,
        rank_col_opponent2,
        pts_col_opponent2,
        set1_col_opponent2,
        set2_col_opponent2,
        set3_col_opponent2,
        grind_col_opponent2,
    ) = st.columns([1, 3, 1.5, 1, 1, 1, 1, 1], gap="small")
    with title_col_opponent2:
        pass
        # st.caption("EXT")

    with player_col_opponent2:
        name_opponent2 = st.text_input(
            "", key=f"{match}_opponent2_name", label_visibility="collapsed"
        )

    with rank_col_opponent2:
        rank_opponent2 = st.selectbox(
            "",
            options=CLASSEMENTS,
            key=f"{match}_opponent2_rank",
            label_visibility="collapsed",
        )

    with pts_col_opponent2:
        pts_opponent2 = st.number_input(
            "",
            min_value=400,
            step=1,
            format="%d",
            key=f"{match}_opponent2_pts",
            label_visibility="collapsed",
        )

    with grind_col_opponent2:
        grind_opponent2 = st.text_input(
            "+/-", key=f"{match}_opponent2_grind", label_visibility="collapsed"
        )


# Récupérer l'ID d'un joueur
def get_player_id(table, name):
    m = table["name"] == name
    return int(table.loc[m, "id_player"].iloc[0]) if m.any() else None


loose_box = """
        {
        border: 2px solid red;
        border-radius: 12px;
        padding: 12px 14px;
        background: rgba(22,163,74,.06);
        margin: 6px 0 12px 0;
        display: flex;
        align-items: stretch;
        }
        """
win_box = """
        {
        border: 2px solid green;
        border-radius: 12px;
        padding: 12px 14px;
        background: rgba(22,163,74,.06);
        margin: 6px 0 12px 0;
        display: flex;
        align-items: stretch;
        }
        """
draw_box = """
        {
        border: 2px solid whitesmoke;
        border-radius: 12px;
        padding: 12px 14px;
        background: rgba(22,163,74,.06);
        margin: 6px 0 12px 0;
        display: flex;
        align-items: stretch;
        }
        """


# Gestionnaire des colonnes latérales d'affichage des noms de joueurs
def match_name_histo(name, rank, side, opacity):
    st.markdown(
        f"<span style='font-size:1rem;opacity:{opacity};float:{side}'>{name} ({rank})</span>",
        unsafe_allow_html=True,
    )


# Gestionnaire de la colonne centrale d'affichage des sets du match
def match_score_histo(set1, set2, set3=None):
    if set3 != "0/0":
        c1, c2, c3 = st.columns(3, gap="small")
        with c1:
            st.markdown(
                f"<div style='font-size:1rem;opacity:1;text-align:center;background-color:white; color:black; margin-bottom:15px'>{set1.replace('/','-')}</div>",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"<div style='font-size:1rem;opacity:1;text-align:center;background-color:white; color:black; margin-bottom:15px'>{set2.replace('/','-')}</div>",
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"<div style='font-size:1rem;opacity:1;text-align:center;background-color:white; color:black; margin-bottom:15px'>{set3.replace('/','-')}</div>",
                unsafe_allow_html=True,
            )
    else:
        c1, c2 = st.columns(2, gap="small")
        with c1:
            st.markdown(
                f"<div style='font-size:1rem;opacity:1;text-align:center;background-color:white; color:black; margin-bottom:15px'>{set1.replace('/','-')}</div>",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"<div style='font-size:1rem;opacity:1;text-align:center;background-color:white; color:black; margin-bottom:15px'>{set2.replace('/','-')}</div>",
                unsafe_allow_html=True,
            )


# Configuration de l'opacité des noms en fonction de la victoire/défaite
def opacity_check(side, set1, set2, set3):
    if side == "aob":
        if int(set1.split("/")[0]) > int(set1.split("/")[1]) and int(
            set2.split("/")[0]
        ) > int(set2.split("/")[1]):
            return 1
        elif (
            int(set1.split("/")[0]) < int(set1.split("/")[1])
            and int(set2.split("/")[0]) > int(set2.split("/")[1])
            and int(set3.split("/")[0]) > int(set3.split("/")[1])
        ):
            return 1
        elif (
            int(set1.split("/")[0]) > int(set1.split("/")[1])
            and int(set2.split("/")[0]) < int(set2.split("/")[1])
            and int(set3.split("/")[0]) > int(set3.split("/")[1])
        ):
            return 1
        else:
            return 0.4
    else:
        if int(set1.split("/")[0]) < int(set1.split("/")[1]) and int(
            set2.split("/")[0]
        ) < int(set2.split("/")[1]):
            return 1
        elif (
            int(set1.split("/")[0]) < int(set1.split("/")[1])
            and int(set2.split("/")[0]) > int(set2.split("/")[1])
            and int(set3.split("/")[0]) < int(set3.split("/")[1])
        ):
            return 1
        elif (
            int(set1.split("/")[0]) > int(set1.split("/")[1])
            and int(set2.split("/")[0]) < int(set2.split("/")[1])
            and int(set3.split("/")[0]) < int(set3.split("/")[1])
        ):
            return 1
        else:
            return 0.4


# Gestion de l'opacité des visuels des vainqueurs/perdants
def opacity_check_interclub(aob_score, opponent_score):
    if aob_score > opponent_score:
        return 1, 0.4
    elif aob_score == opponent_score:
        return 1, 1
    else:
        return 0.4, 1


# Lignes de la page "Historique"
def box_color_histo(
    date, journey, key_id, aob_team, opponent_team, aob_score, opponent_score, box_style
):
    with stylable_container(key=f"box-vert-{key_id}", css_styles=box_style):
        # Ligne principale
        c1, c2 = st.columns([1, 9], gap="small")
        with c1:
            st.markdown(
                f"<span style='font-size:1rem;opacity:0.6'>{journey}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='background-color:rgba(0, 0, 0, {opacity_check_interclub(aob_score,opponent_score)[0]}); margin-top:-15px'><span style='font-size:1rem; text-align: center; opacity:{opacity_check_interclub(aob_score,opponent_score)[0]}'>{aob_score}</span></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='background-color:rgba(0, 0, 0, {opacity_check_interclub(aob_score,opponent_score)[1]})'><span style='font-size:1rem; text-align: center; opacity:{opacity_check_interclub(aob_score,opponent_score)[1]}'>{opponent_score}</span></div>",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"<span style='font-size:1rem; opacity:.6; float:right'>{date}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='background-color:rgba(0, 0, 0, {opacity_check_interclub(aob_score,opponent_score)[0]}); margin-top:-15px'><span style='font-size:1rem; opacity:{opacity_check_interclub(aob_score,opponent_score)[0]}; margin-top:-20px'>{aob_team}</span></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='background-color:rgba(0, 0, 0, {opacity_check_interclub(aob_score,opponent_score)[1]}); margin-bottom: 15px'><span style='font-size:1rem;opacity:{opacity_check_interclub(aob_score,opponent_score)[1]}; margin-top:-20px'>{opponent_team}</span></div>",
                unsafe_allow_html=True,
            )

        # Toggle détails (à droite)
        _left, _sp, _right = st.columns([6, 1, 1])
        with _left:
            show = st.toggle(
                "Afficher les détails", key=f"details_{key_id}", value=False
            )

        # Détails : s'affichent seulement si activé (slide button)
        if show:
            df_filtered = TABLE_MATCHS[(TABLE_MATCHS["id"] == key_id)].reset_index(
                drop=True
            )
            #
            for k in range(len(df_filtered)):
                r1c1, r1c2, r1c3 = st.columns([4, 2, 4], gap="small")
                with r1c1:
                    # Joueurs de l'AOB
                    if "/" in str(df_filtered["aob_player_id"].loc[k]):
                        p1_id = df_filtered["aob_player_id"].loc[k].split("/")[0]
                        p2_id = df_filtered["aob_player_id"].loc[k].split("/")[1]
                        #
                        p1_name = (
                            TABLE_PLAYERS[TABLE_PLAYERS["id_player"] == int(p1_id)]
                            .reset_index(drop=True)["name"]
                            .loc[0]
                        )
                        p2_name = (
                            TABLE_PLAYERS[TABLE_PLAYERS["id_player"] == int(p2_id)]
                            .reset_index(drop=True)["name"]
                            .loc[0]
                        )
                        match_name_histo(
                            f"{p1_name}/{p2_name}",
                            df_filtered["aob_rank"].loc[k],
                            "left",
                            opacity_check(
                                "aob",
                                df_filtered["set1"].loc[k],
                                df_filtered["set2"].loc[k],
                                df_filtered["set3"].loc[k],
                            ),
                        )
                    else:
                        match_name_histo(
                            TABLE_PLAYERS[
                                TABLE_PLAYERS["id_player"]
                                == df_filtered["aob_player_id"].loc[k]
                            ]
                            .reset_index(drop=True)["name"]
                            .loc[0],
                            df_filtered["aob_rank"].loc[k],
                            "left",
                            opacity_check(
                                "aob",
                                df_filtered["set1"].loc[k],
                                df_filtered["set2"].loc[k],
                                df_filtered["set3"].loc[k],
                            ),
                        )
                with r1c2:
                    # Scores des différents sets
                    match_score_histo(
                        df_filtered["set1"].loc[k],
                        df_filtered["set2"].loc[k],
                        df_filtered["set3"].loc[k],
                    )
                with r1c3:
                    # Joueurs de l'extérieur
                    match_name_histo(
                        df_filtered["opponent_player"].loc[k],
                        df_filtered["opponent_rank"].loc[k],
                        "right",
                        opacity_check(
                            "opponent",
                            df_filtered["set1"].loc[k],
                            df_filtered["set2"].loc[k],
                            df_filtered["set3"].loc[k],
                        ),
                    )
