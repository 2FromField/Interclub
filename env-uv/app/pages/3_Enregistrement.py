from datetime import date
import streamlit as st
import utils
from auth import check_record_password

# 🔒 Accès administrateur
if not check_record_password(page_key="admin", secret_path="admin.password"):
    st.stop()

##################################################################
#                          DONNEES                               #
##################################################################

# --- Accès aux tables
INTERCLUB_TABLE = utils.TABLE_INTERCLUB
MATCHS_TABLE = utils.TABLE_MATCHS
PLAYERS_TABLE = utils.TABLE_PLAYERS

# --- Données brutes
EQUIPE = ["H2", "V3", "PR", "D2", "D3", "D5"]
EQUIPE_NOMS = ["AOB35-1", "AOB35-2", "AOB35-3", "AOB35-4"]


##################################################################
#                         FONCTIONS                              #
##################################################################
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


def reset_sh1():
    """Reset du dropdown lors de la désélection"""
    # optionnel : oublie la sélection dépendante si la catégorie change
    st.session_state.pop("sh1_player_home", None)

@st.dialog("Vérification de l'enregistrement", width="large")
def afficher_popup(df_filtered, row_interclub):
    home_team, home_score, away_score, away_team = st.columns([5, 1, 1, 5], gap="small")
    a_score = df_filtered["win"].fillna("").str.count("opponent").sum()
    h_score = df_filtered["win"].fillna("").str.count("aob").sum()
    with home_team :
        st.markdown(
            f'<p style="margin:0; color:white; text-align:left; font-size:2em; margin-bottom:15px; opacity:{utils.opacity_check_interclub(h_score,a_score)[0]}">{aob_team}</p>',
            unsafe_allow_html=True,
        )
    with home_score:
        st.markdown(
            f'<p style="margin:0; color:white; text-align:center; font-size:2em; margin-bottom:15px; opacity:{utils.opacity_check_interclub(h_score,a_score)[0]}">{h_score}</p>',
            unsafe_allow_html=True,
        )
    with away_score:
        st.markdown(
            f'<p style="margin:0; color:white; text-align:center; font-size:2em; margin-bottom:15px; opacity:{utils.opacity_check_interclub(h_score,a_score)[1]}">{a_score}</p>',
            unsafe_allow_html=True,
        )
    with away_team:
        st.markdown(
            f'<p style="margin:0; color:white; text-align:right; font-size:2em; margin-bottom:15px; opacity:{utils.opacity_check_interclub(h_score,a_score)[1]}">{opponent_team}</p>',
            unsafe_allow_html=True,
        )
    #
    for k in range(len(df_filtered)):
        r1c1, r1c2, r1c3 = st.columns([4, 2, 4], gap="small")
        with r1c1:
            # Joueurs de l'AOB
            if "/" in str(df_filtered["aob_player_id"].loc[k]):
                p1_id = int(df_filtered["aob_player_id"].loc[k].split("/")[0])
                p2_id = int(df_filtered["aob_player_id"].loc[k].split("/")[1])
                #
                p1_name = (
                    PLAYERS_TABLE[PLAYERS_TABLE["id_player"] == int(p1_id)]
                    .reset_index(drop=True)["name"]
                    .loc[0]
                )
                p2_name = (
                    PLAYERS_TABLE[PLAYERS_TABLE["id_player"] == int(p2_id)]
                    .reset_index(drop=True)["name"]
                    .loc[0]
                )
                utils.match_name_histo(
                    f"{p1_name}/{p2_name}",
                    df_filtered["aob_rank"].loc[k],
                    "left",
                    utils.opacity_check(
                        "aob",
                        df_filtered["set1"].loc[k],
                        df_filtered["set2"].loc[k],
                        df_filtered["set3"].loc[k],
                    ),
                )
            else:
                utils.match_name_histo(
                    PLAYERS_TABLE[
                        PLAYERS_TABLE["id_player"]
                        == int(df_filtered["aob_player_id"].loc[k])
                    ]
                    .reset_index(drop=True)["name"]
                    .loc[0],
                    df_filtered["aob_rank"].loc[k],
                    "left",
                    utils.opacity_check(
                        "aob",
                        df_filtered["set1"].loc[k],
                        df_filtered["set2"].loc[k],
                        df_filtered["set3"].loc[k],
                    ),
                )
        with r1c2:
            # Scores des différents sets
            utils.match_score_histo(
                df_filtered["set1"].loc[k],
                df_filtered["set2"].loc[k],
                df_filtered["set3"].loc[k],
            )
        with r1c3:
            # Joueurs de l'extérieur
            utils.match_name_histo(
                df_filtered["opponent_player"].loc[k],
                df_filtered["opponent_rank"].loc[k],
                "right",
                utils.opacity_check(
                    "opponent",
                    df_filtered["set1"].loc[k],
                    df_filtered["set2"].loc[k],
                    df_filtered["set3"].loc[k],
                ),
            )
    
    if st.button("Enregistrer"):
        # Ajouter les nouvelles lignes
        if categorie == "H2":
            utils.append_rows_sheet(
                [sh1_row, sh2_row, sh3_row, sh4_row, dh1_row, dh2_row],
                "TABLE_MATCHS",
            )
        elif categorie == "D5":
            utils.append_rows_sheet(
                [sh1_row, sh2_row, sd1_row, dh_row, dd_row, mx1_row, mx2_row],
                "TABLE_MATCHS",
            )
        elif categorie == "V3":
            utils.append_rows_sheet(
                [sh1_row, sh2_row, dh_row, dd_row, mx1_row, mx2_row],
                "TABLE_MATCHS",
            )
        else: # D2/D3/PR
            utils.append_rows_sheet(
                [
                    sh1_row,
                    sh2_row,
                    sd1_row,
                    sd2_row,
                    dh_row,
                    dd_row,
                    mx1_row,
                    mx2_row,
                ],
                "TABLE_MATCHS",
            )
        #
        # Mise à jour de la table INTERCLUB
        utils.append_row_sheet(row_interclub, "TABLE_INTERCLUB")
        st.session_state["flash"] = ("success", "✅ Enregistrement effectué !")
        st.rerun()


##################################################################
#                           LAYOUT                               #
##################################################################
st.set_page_config(page_title="Record", page_icon="🗂️", layout="wide")

# Flash message après rerun
flash = st.session_state.pop("flash", None)
if flash:
    level, text = flash
    getattr(st, level)(text)


# -- Dropdown des différentes division de l'AOB
categorie = st.selectbox("Catégorie", EQUIPE, key="categorie", on_change=reset_sh1)

# -- Formulaire
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

    if categorie == "H2":  # interclub MIXTE
        left_col, sep, right_col = st.columns([3, 0.4, 3])
        with sep:
            pass

        with left_col:
            # SH1
            utils.simple_match(PLAYERS_TABLE, categorie, "sh1")
            st.caption("-------------------")
            # SH2
            utils.simple_match(PLAYERS_TABLE, categorie, "sh2")
            st.caption("-------------------")
            # DH1
            utils.double_match(PLAYERS_TABLE, categorie, "dh1")

        with right_col:
            # SH3
            utils.simple_match(PLAYERS_TABLE, categorie, "sh3")
            st.caption("-------------------")
            # SH4
            utils.simple_match(PLAYERS_TABLE, categorie, "sh4")
            st.caption("-------------------")
            # DH2
            utils.double_match(PLAYERS_TABLE, categorie, "dh2")
    #
    elif categorie == "D5":
        left_col, sep, right_col = st.columns([3, 0.1, 3])
        with sep:
            pass

        with left_col:
            # SH1
            utils.simple_match(PLAYERS_TABLE, categorie, "sh1")
            st.caption("-------------------")
            # SH2
            utils.simple_match(PLAYERS_TABLE, categorie, "sh2")
            st.caption("-------------------")
            # DH1
            utils.double_match(PLAYERS_TABLE, categorie, "dh")
            st.caption("-------------------")
            # MX1
            utils.double_match(PLAYERS_TABLE, categorie, "mx1")

        with right_col:
            # SD1
            utils.simple_match(PLAYERS_TABLE, categorie, "sd1")
            st.caption("-------------------")
            # DH1
            utils.double_match(PLAYERS_TABLE, categorie, "dd")
            st.caption("-------------------")
            # MX2
            utils.double_match(PLAYERS_TABLE, categorie, "mx2")
    #
    elif categorie == "V3":
        left_col, sep, right_col = st.columns([3, 0.1, 3])
        with sep:
            pass

        with left_col:
            # SH1
            utils.simple_match(PLAYERS_TABLE, categorie, "sh1")
            st.caption("-------------------")
            # DH1
            utils.double_match(PLAYERS_TABLE, categorie, "dh")
            st.caption("-------------------")
            # MX1
            utils.double_match(PLAYERS_TABLE, categorie, "mx1")

        with right_col:
            # SH2
            utils.simple_match(PLAYERS_TABLE, categorie, "sh2")
            st.caption("-------------------")
            # DH1
            utils.double_match(PLAYERS_TABLE, categorie, "dd")
            st.caption("-------------------")
            # MX2
            utils.double_match(PLAYERS_TABLE, categorie, "mx2")

    else:
        left_col, sep, right_col = st.columns([3, 0.1, 3])
        with sep:
            pass

        with left_col:
            # SH1
            utils.simple_match(PLAYERS_TABLE, categorie, "sh1")
            st.caption("-------------------")
            # SH2
            utils.simple_match(PLAYERS_TABLE, categorie, "sh2")
            st.caption("-------------------")
            # DH1
            utils.double_match(PLAYERS_TABLE, categorie, "dh")
            st.caption("-------------------")
            # MX1
            utils.double_match(PLAYERS_TABLE, categorie, "mx1")

        with right_col:
            # SD1
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

    submitted = st.form_submit_button("Vérification")

# -- Sauvegarde des données enregistrées sur Google SHEET
if submitted:
    if not opponent_team.strip():  # oublie nom d'équipe adverse
        st.error("Veuillez renseigner le champ **Adversaire**.")
    else:
        # Mise à jour de la table MATCHS
        try:
            if categorie == "H2":
                sh1_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "SH1",
                    "aob_player_id": str(
                        utils.get_player_id(
                            PLAYERS_TABLE, st.session_state.get("sh1_aob_name")
                        )
                    ),
                    "opponent_player": st.session_state.get("sh1_opponent_name"),
                    "aob_rank": st.session_state.get("sh1_aob_rank"),
                    "opponent_rank": st.session_state.get("sh1_opponent_rank"),
                    "aob_pts": str(st.session_state.get("sh1_aob_pts")),
                    "opponent_pts": str(st.session_state.get("sh1_opponent_pts")),
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
                    "aob_player_id": str(
                        utils.get_player_id(
                            PLAYERS_TABLE, st.session_state.get("sh2_aob_name")
                        )
                    ),
                    "opponent_player": st.session_state.get("sh2_opponent_name"),
                    "aob_rank": st.session_state.get("sh2_aob_rank"),
                    "opponent_rank": st.session_state.get("sh2_opponent_rank"),
                    "aob_pts": str(st.session_state.get("sh2_aob_pts")),
                    "opponent_pts": str(st.session_state.get("sh2_opponent_pts")),
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
                    "aob_player_id": str(
                        utils.get_player_id(
                            PLAYERS_TABLE, st.session_state.get("sh3_aob_name")
                        )
                    ),
                    "opponent_player": st.session_state.get("sh3_opponent_name"),
                    "aob_rank": st.session_state.get("sh3_aob_rank"),
                    "opponent_rank": st.session_state.get("sh3_opponent_rank"),
                    "aob_pts": str(st.session_state.get("sh3_aob_pts")),
                    "opponent_pts": str(st.session_state.get("sh3_opponent_pts")),
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
                    "aob_player_id": str(
                        utils.get_player_id(
                            PLAYERS_TABLE, st.session_state.get("sh4_aob_name")
                        )
                    ),
                    "opponent_player": st.session_state.get("sh4_opponent_name"),
                    "aob_rank": st.session_state.get("sh4_aob_rank"),
                    "opponent_rank": st.session_state.get("sh4_opponent_rank"),
                    "aob_pts": str(st.session_state.get("sh4_aob_pts")),
                    "opponent_pts": str(st.session_state.get("sh4_opponent_pts")),
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
                    "aob_grind": f'{str(st.session_state.get("dh1_aob1_grind"))}/{str(st.session_state.get("dh1_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("dh1_opponent1_grind"))}/{str(st.session_state.get("dh1_opponent2_grind"))}',
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
                    "aob_grind": f'{str(st.session_state.get("dh2_aob1_grind"))}/{str(st.session_state.get("dh2_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("dh2_opponent1_grind"))}/{str(st.session_state.get("dh2_opponent2_grind"))}',
                    "win": winner(
                        set1=f'{st.session_state.get("dh2_aob_set1")}/{st.session_state.get("dh2_opponent_set1")}',
                        set2=f'{st.session_state.get("dh2_aob_set2")}/{st.session_state.get("dh2_opponent_set2")}',
                        set3=f'{st.session_state.get("dh2_aob_set3")}/{st.session_state.get("dh2_opponent_set3")}',
                    ),
                }
                #
                match_df = utils.create_df_from_dict(
                    [sh1_row, sh2_row, sh3_row, sh4_row, dh1_row, dh2_row]
                )
            #
            elif categorie == "D5":
                sh1_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "SH1",
                    "aob_player_id": str(
                        utils.get_player_id(
                            PLAYERS_TABLE, st.session_state.get("sh1_aob_name")
                        )
                    ),
                    "opponent_player": st.session_state.get("sh1_opponent_name"),
                    "aob_rank": st.session_state.get("sh1_aob_rank"),
                    "opponent_rank": st.session_state.get("sh1_opponent_rank"),
                    "aob_pts": str(st.session_state.get("sh1_aob_pts")),
                    "opponent_pts": str(st.session_state.get("sh1_opponent_pts")),
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
                    "aob_player_id": str(
                        utils.get_player_id(
                            PLAYERS_TABLE, st.session_state.get("sh2_aob_name")
                        )
                    ),
                    "opponent_player": st.session_state.get("sh2_opponent_name"),
                    "aob_rank": st.session_state.get("sh2_aob_rank"),
                    "opponent_rank": st.session_state.get("sh2_opponent_rank"),
                    "aob_pts": str(st.session_state.get("sh2_aob_pts")),
                    "opponent_pts": str(st.session_state.get("sh2_opponent_pts")),
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
                    "aob_player_id": str(
                        utils.get_player_id(
                            PLAYERS_TABLE, st.session_state.get("sd1_aob_name")
                        )
                    ),
                    "opponent_player": st.session_state.get("sd1_opponent_name"),
                    "aob_rank": st.session_state.get("sd1_aob_rank"),
                    "opponent_rank": st.session_state.get("sd1_opponent_rank"),
                    "aob_pts": str(st.session_state.get("sd1_aob_pts")),
                    "opponent_pts": str(st.session_state.get("sd1_opponent_pts")),
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
                    "aob_grind": f'{str(st.session_state.get("dh_aob1_grind"))}/{str(st.session_state.get("dh_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("dh_opponent1_grind"))}/{str(st.session_state.get("dh_opponent2_grind"))}',
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
                    "aob_grind": f'{str(st.session_state.get("dd_aob1_grind"))}/{str(st.session_state.get("dd_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("dd_opponent1_grind"))}/{str(st.session_state.get("dd_opponent2_grind"))}',
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
                    "aob_grind": f'{str(st.session_state.get("mx1_aob1_grind"))}/{str(st.session_state.get("mx1_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("mx1_opponent1_grind"))}/{str(st.session_state.get("mx1_opponent2_grind"))}',
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
                    "aob_grind": f'{str(st.session_state.get("mx2_aob1_grind"))}/{str(st.session_state.get("mx2_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("mx2_opponent1_grind"))}/{str(st.session_state.get("mx2_opponent2_grind"))}',
                    "win": winner(
                        set1=f'{st.session_state.get("mx2_aob_set1")}/{st.session_state.get("mx2_opponent_set1")}',
                        set2=f'{st.session_state.get("mx2_aob_set2")}/{st.session_state.get("mx2_opponent_set2")}',
                        set3=f'{st.session_state.get("mx2_aob_set3")}/{st.session_state.get("mx2_opponent_set3")}',
                    ),
                }
                #
                match_df = utils.create_df_from_dict(
                    [sh1_row, sh2_row, sd1_row, dh_row, dd_row, mx1_row, mx2_row]
                )
            #
            elif categorie == "V3":
                sh1_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "SH1",
                    "aob_player_id": str(
                        utils.get_player_id(
                            PLAYERS_TABLE, st.session_state.get("sh1_aob_name")
                        )
                    ),
                    "opponent_player": st.session_state.get("sh1_opponent_name"),
                    "aob_rank": st.session_state.get("sh1_aob_rank"),
                    "opponent_rank": st.session_state.get("sh1_opponent_rank"),
                    "aob_pts": str(st.session_state.get("sh1_aob_pts")),
                    "opponent_pts": str(st.session_state.get("sh1_opponent_pts")),
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
                    "aob_player_id": str(
                        utils.get_player_id(
                            PLAYERS_TABLE, st.session_state.get("sh2_aob_name")
                        )
                    ),
                    "opponent_player": st.session_state.get("sh2_opponent_name"),
                    "aob_rank": st.session_state.get("sh2_aob_rank"),
                    "opponent_rank": st.session_state.get("sh2_opponent_rank"),
                    "aob_pts": str(st.session_state.get("sh2_aob_pts")),
                    "opponent_pts": str(st.session_state.get("sh2_opponent_pts")),
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
                    "aob_grind": f'{str(st.session_state.get("dh_aob1_grind"))}/{str(st.session_state.get("dh_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("dh_opponent1_grind"))}/{str(st.session_state.get("dh_opponent2_grind"))}',
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
                    "aob_grind": f'{str(st.session_state.get("dd_aob1_grind"))}/{str(st.session_state.get("dd_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("dd_opponent1_grind"))}/{str(st.session_state.get("dd_opponent2_grind"))}',
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
                    "aob_grind": f'{str(st.session_state.get("mx1_aob1_grind"))}/{str(st.session_state.get("mx1_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("mx1_opponent1_grind"))}/{str(st.session_state.get("mx1_opponent2_grind"))}',
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
                    "aob_grind": f'{str(st.session_state.get("mx2_aob1_grind"))}/{str(st.session_state.get("mx2_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("mx2_opponent1_grind"))}/{str(st.session_state.get("mx2_opponent2_grind"))}',
                    "win": winner(
                        set1=f'{st.session_state.get("mx2_aob_set1")}/{st.session_state.get("mx2_opponent_set1")}',
                        set2=f'{st.session_state.get("mx2_aob_set2")}/{st.session_state.get("mx2_opponent_set2")}',
                        set3=f'{st.session_state.get("mx2_aob_set3")}/{st.session_state.get("mx2_opponent_set3")}',
                    ),
                }
                #
                match_df = utils.create_df_from_dict(
                    [sh1_row, sh2_row, dh_row, dd_row, mx1_row, mx2_row]
                )
            #
            else:
                sh1_row = {
                    "id": MATCHS_TABLE["id"].max() + 1,
                    "type_match": "SH1",
                    "aob_player_id": str(
                        utils.get_player_id(
                            PLAYERS_TABLE, st.session_state.get("sh1_aob_name")
                        )
                    ),
                    "opponent_player": st.session_state.get("sh1_opponent_name"),
                    "aob_rank": st.session_state.get("sh1_aob_rank"),
                    "opponent_rank": st.session_state.get("sh1_opponent_rank"),
                    "aob_pts": str(st.session_state.get("sh1_aob_pts")),
                    "opponent_pts": str(st.session_state.get("sh1_opponent_pts")),
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
                    "aob_player_id": str(
                        utils.get_player_id(
                            PLAYERS_TABLE, st.session_state.get("sh2_aob_name")
                        )
                    ),
                    "opponent_player": st.session_state.get("sh2_opponent_name"),
                    "aob_rank": st.session_state.get("sh2_aob_rank"),
                    "opponent_rank": st.session_state.get("sh2_opponent_rank"),
                    "aob_pts": str(st.session_state.get("sh2_aob_pts")),
                    "opponent_pts": str(st.session_state.get("sh2_opponent_pts")),
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
                    "aob_player_id": str(
                        utils.get_player_id(
                            PLAYERS_TABLE, st.session_state.get("sd1_aob_name")
                        )
                    ),
                    "opponent_player": st.session_state.get("sd1_opponent_name"),
                    "aob_rank": st.session_state.get("sd1_aob_rank"),
                    "opponent_rank": st.session_state.get("sd1_opponent_rank"),
                    "aob_pts": str(st.session_state.get("sd1_aob_pts")),
                    "opponent_pts": str(st.session_state.get("sd1_opponent_pts")),
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
                    "aob_player_id": str(
                        utils.get_player_id(
                            PLAYERS_TABLE, st.session_state.get("sd2_aob_name")
                        )
                    ),
                    "opponent_player": st.session_state.get("sd2_opponent_name"),
                    "aob_rank": st.session_state.get("sd2_aob_rank"),
                    "opponent_rank": st.session_state.get("sd2_opponent_rank"),
                    "aob_pts": str(st.session_state.get("sd2_aob_pts")),
                    "opponent_pts": str(st.session_state.get("sd2_opponent_pts")),
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
                    "aob_grind": f'{str(st.session_state.get("dh_aob1_grind"))}/{str(st.session_state.get("dh_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("dh_opponent1_grind"))}/{str(st.session_state.get("dh_opponent2_grind"))}',
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
                    "aob_grind": f'{str(st.session_state.get("dd_aob1_grind"))}/{str(st.session_state.get("dd_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("dd_opponent1_grind"))}/{str(st.session_state.get("dd_opponent2_grind"))}',
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
                    "aob_grind": f'{str(st.session_state.get("mx1_aob1_grind"))}/{str(st.session_state.get("mx1_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("mx1_opponent1_grind"))}/{str(st.session_state.get("mx1_opponent2_grind"))}',
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
                    "aob_grind": f'{str(st.session_state.get("mx2_aob1_grind"))}/{str(st.session_state.get("mx2_aob2_grind"))}',
                    "opponent_grind": f'{str(st.session_state.get("mx2_opponent1_grind"))}/{str(st.session_state.get("mx2_opponent2_grind"))}',
                    "win": winner(
                        set1=f'{st.session_state.get("mx2_aob_set1")}/{st.session_state.get("mx2_opponent_set1")}',
                        set2=f'{st.session_state.get("mx2_aob_set2")}/{st.session_state.get("mx2_opponent_set2")}',
                        set3=f'{st.session_state.get("mx2_aob_set3")}/{st.session_state.get("mx2_opponent_set3")}',
                    ),
                }
                #
                match_df = utils.create_df_from_dict(
                    [
                        sh1_row,
                        sh2_row,
                        sd1_row,
                        sd2_row,
                        dh_row,
                        dd_row,
                        mx1_row,
                        mx2_row,
                    ]
                )
                #
            
            # Mise à jour de la table INTERCLUB
            row_interclub = {
                # id;date;journey;division;aob_team;opponent_team;aob_score;opponent_score
                "id": len(INTERCLUB_TABLE) + 1,
                "date": str(date_match),
                "journey": f"J{journey}",
                "division": categorie,
                "aob_team": aob_team,
                "opponent_team": opponent_team,
                "aob_score": match_df["win"].fillna("").str.count("aob").sum(),
                "opponent_score": match_df["win"]
                .fillna("")
                .str.count("opponent")
                .sum(),
            }
            #
            # Ouvrir la fenêtre de vérification
            afficher_popup(match_df, row_interclub)
            #
        except Exception as e:
            st.session_state["flash"] = (
                "error",
                f"❌ Impossible d'enregistrer la rencontre : {e}",
            )