import streamlit as st
import pandas as pd

# Données brutes
CLASSEMENTS = [
    "NC",
    "P12",
    "P11",
    "P10",
    "D9",
    "D8",
    "D7",
    "R6",
    "R5",
    "R4",
    "N3",
    "N2",
    "N1",
]


# Match de simple (SH,SD)
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
    ) = st.columns([1, 3, 2, 1, 1, 1, 1, 1], gap="small")
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
        name_aob = st.selectbox(
            "Joueur(s)",
            df_filtre["name"].to_list(),
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
    ) = st.columns([1, 3, 2, 1, 1, 1, 1, 1], gap="small")
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
    ) = st.columns([1, 3, 2, 1, 1, 1, 1, 1], gap="small")
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
        name_aob1 = st.selectbox(
            "Joueur(s)",
            df_filtre["name"].to_list(),
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
    ) = st.columns([1, 3, 2, 1, 1, 1, 1, 1], gap="small")
    with title_col_aob2:
        pass
        # st.caption("EXT")

    with player_col_aob2:
        name_aob2 = st.selectbox(
            "",
            options=df_filtre["name"].to_list(),
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
    ) = st.columns([1, 3, 2, 1, 1, 1, 1, 1], gap="small")
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
    ) = st.columns([1, 3, 2, 1, 1, 1, 1, 1], gap="small")
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


def get_player_id(table, name):
    m = table["name"] == name
    return int(table.loc[m, "id_player"].iloc[0]) if m.any() else None
