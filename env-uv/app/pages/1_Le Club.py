import streamlit as st
import base64
from pathlib import Path
import utils
import plotly.graph_objects as go
import pandas as pd
import streamlit.components.v1 as components
from streamlit_extras.stylable_container import stylable_container
import numpy as np

##################################################################
#                          DONNEES                               #
##################################################################
TABLE_INTERCLUB = utils.load_table(utils.env, "TABLE_INTERCLUB")

# Chemin relatif vers les fichiers
BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_TEAM_DIR = BASE_DIR / "assets" / "img" / "teams"
ASSETS_DIR = BASE_DIR / "assets" / "img"

##################################################################
#                         FONCTIONS                              #
##################################################################

def winrate_piechart(value1:float, value2:float, value3:float, legend:list, unit:str="tot", key:str="default_id", colors:list=None, pct_list:list=None):
    """Graphique en camembert à 3 secteurs.
    
    Args:
        value1 (float): valeur de la section n°1
        value2 (float): valeur de la section n°2
        value3 (float): valeur de la section n°3
        legend (list[str]): légende de chaque secteur (dans l'ordre)
        unit (str): type de données ('tot' ou 'pct') (default: 'tot')
        key (str): clé d'identification du graphique (default: default_id)
        colors (list[str]): couleurs des sections (default: None = vert/rouge/bleu)
        pct_list (list[float]): valuers en pourcentage pour l'affichage (default: None)
    """
    values = [value1, value2, value3]
    
    # Gestion des couleurs
    if colors is None:
        colors = ["#22C55E", "#EF4444", "#449AEF"]
    
    # Gestion des unités
    if unit == "pct":
        total = sum(values)
        values_display = [round((v / total) * 100, 1) for v in values] if total else [0, 0, 0]
        hovertemplate = "<b>%{label}</b><br>%{value}%<extra></extra>"
        textemplate = "%{value}%"
        labels = legend
    elif unit=="ratio":
        values_display = values
        hovertemplate = "<b>%{label}</b><br>%{value}<extra></extra>"
        textemplate = "%{value}"
        labels = [f"{legend[0]}({pct_list[0]}%)",f"{legend[1]}({pct_list[1]}%)",f"{legend[2]}({pct_list[2]}%)"]
    else:
        values_display = values
        hovertemplate = "<b>%{label}</b><br>%{value}<extra></extra>"
        textemplate = "%{value}"
        labels = legend

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values_display,
                hole=0.62,
                marker=dict(colors=colors),
                textfont=dict(size=16, color="#111827"),
                textinfo="text",
                texttemplate=textemplate,
                hovertemplate=hovertemplate,
                sort=False
            )
        ]
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            y=-0.1,
            x=0.5,
            xanchor="center",
            font=dict(size=14)
        ),
        margin=dict(t=70, b=70, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    chart = st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
        key=key
    )

    return chart


def actual_rank(df:pd.DataFrame, joueur:str, type:str="DD|DH"):
    """Récupération du classement actuel d'un joueur.
    
    Args:
        df (pd.DataFrame): jeu de données des matchs.
        joueur (str): nom du joueur ciblé.
        type (str): type de match ciblé (default: 'DD|DH').
    """
    apply_df = df[(df["type_match"].str.contains(type, na=False)) & (df["player"].str.contains(joueur, na=False))].reset_index(drop=True)
    if not apply_df.empty:
        if type in ["DD|DH", "MX"]:
            line_double = apply_df.loc[len(apply_df)-1]
            name_double = [p.strip() for p in line_double["player"].split("/")]
            rank_double = [p.strip() for p in line_double["rank"].split("/")]
            p_double = dict(zip(name_double, rank_double))
            return p_double[joueur]
        else:
            return apply_df.loc[0]["rank"]
    else:
        return "..."


def box_team(
    date, journey, key_id, aob_team, opponent_team, aob_score, opponent_score, box_style
):
    """Affichage des résultats des matchs contre une équipe sous formats de carrés 
    vert (victoire) ou rouge (défaite) avec le type de match à l'intérieur horodaté.
    
    Args:
        date (str): date de la rencontre au format string YYYY/MM/dd.
        journey (str): numéro de la journée de la rencontre.
        key_id (int): identifiant unique du container streamlit.
        aob_team (str): nom de l'équipe ciblée.
        opponent_team (str): nom de l'équipe adverse.
        aob_score (int): score final de l'AOB.
        opponent_score (int): score final de l'adversaire.
        box_style (str): style CSS ajoutés à la balise html.
    """
    with stylable_container(key=f"box-vert-{key_id}", css_styles=box_style):
        # Ligne principale
        c1, c2 = st.columns([1, 9], gap="small")
        with c1:
            st.markdown(
                f"<div style='font-size:1rem;opacity:0.6'>{journey}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='margin-bottom: 5px; background-color:rgba(0, 0, 0); text-align:center;'><span style='font-size:1rem;'>{aob_score}</span></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='background-color:rgba(0, 0, 0); text-align:center;'><span style='font-size:1rem; '>{opponent_score}</span></div>",
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                f"<div style='font-size:1rem; opacity:.6; text-align:right;'>{date}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='margin-bottom: 5px; background-color:rgba(0, 0, 0);'><span style='font-size:1rem;'>{aob_team}</span></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='margin-bottom:10px; background-color:rgba(0, 0, 0);'><span style='font-size:1rem;'>{opponent_team}</span></div>",
                unsafe_allow_html=True,
            )

        # Toggle détails (à droite)
        _left, _sp, _right = st.columns([6, 1, 1])
        with _left:
            show = st.toggle(
                "Afficher les détails",
                key=f"details_{key_id}",
                value=False,
            )

def img_to_base64(path):
    """Convertion d'une image classique (jpeg/png/...) en base64.
    
    Args:
        path (str): chemin vers l'image.
    """
    return base64.b64encode(Path(path).read_bytes()).decode()


##################################################################
#                             CSS                                #
##################################################################

st.markdown(
    """
    <style>
    .kpi-card{
        background:#f1f3f5;           /* gris clair */
        border:1px solid #e5e7eb;
        border-radius:14px;
        padding:18px 14px;
        text-align:center;
        min-height:110px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        margin-bottom: 30px;
    }
    .kpi-title{
        font-size:.85rem;
        letter-spacing:.02em;
        text-transform:uppercase;
        color:#374151;                 /* gris foncé */
        margin:0 0 6px 0;
        opacity:.85;
    }
    .kpi-value{
        font-size:2rem;                /* valeur bien visible */
        font-weight:800;
        margin:0;
        color:#111827;
    }
    .kpi-sub{
        font-size:.9rem;
        color:#6b7280;
        margin-top:4px;
    }

    .block-container {
        max-width: 100% !important;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    div[data-testid="stSegmentedControl"] {
        width: 100% !important;
    }

    div[data-testid="stSegmentedControl"] div[role="radiogroup"] {
        width: 100% !important;
        display: flex !important;
        background-color: #111827;
        padding: 6px;
        border-radius: 14px;
        gap: 6px;
    }

    div[data-testid="stSegmentedControl"] label {
        flex: 1 1 0 !important;
    }

    div[data-testid="stSegmentedControl"] label > div {
        width: 100% !important;
        justify-content: center !important;
        background-color: #374151;
        color: #F9FAFB;
        border-radius: 10px;
        padding: 10px 22px;
        font-weight: 700;
        transition: all 0.2s ease;
    }

    div[data-testid="stSegmentedControl"] label > div:hover {
        background-color: #4B5563;
        color: #FFFFFF;
    }

    div[data-testid="stSegmentedControl"] label:has(input:checked) > div {
        background-color: #F3F4F6 !important;
        color: #111827 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    </style>
    """,
    unsafe_allow_html=True
)

##################################################################
#                            LAYOUT                              #
##################################################################
st.set_page_config(page_title="Statistiques", layout="wide")

# Navbar horizontale
onglet = st.segmented_control(
    label="Navigation",
    options=["Vue générale", "Joueurs", "Équipes"],
    default="Vue générale",
    label_visibility="collapsed",
    width="stretch"  # important
)

st.divider()

##################################################################
#                            GENERAL                             #
##################################################################

# Récupération des données et assemblage des tables
m_ic = utils.TABLE_MATCHS.merge(
    TABLE_INTERCLUB[["id", "date", "division", "aob_team", "opponent_team"]],
    left_on="id",
    right_on="id",
    how="left",
)

# 2) Découper les champs potentiellement composés
m_ic["aob_p1_id"], m_ic["aob_p2_id"] = utils.split2_col(m_ic, "aob_player_id")
m_ic["aob_rank_p1"], m_ic["aob_rank_p2"] = utils.split2_col(m_ic, "aob_rank")
m_ic["aob_pts_p1"], m_ic["aob_pts_p2"] = utils.split2_col(m_ic, "aob_pts")

# (optionnel) caster les points en numériques
for col in ["aob_pts_p1", "aob_pts_p2"]:
    m_ic[col] = pd.to_numeric(m_ic[col], errors="coerce")

# 3) Résoudre noms via mapping id → name
players = utils.TABLE_PLAYERS.copy()
players["id_norm"] = players["id_player"].astype(str).str.strip()
id_to_name = players.set_index("id_norm")["name"].to_dict()

m_ic["aob_p1_name"] = (
    m_ic["aob_p1_id"].astype(str).str.strip().map(id_to_name).fillna("")
)
m_ic["aob_p2_name"] = (
    m_ic["aob_p2_id"].astype(str).str.strip().map(id_to_name).fillna("")
)

# 4) Colonnes combinées (si 2 joueurs)
m_ic["player"] = utils.join_if_two(m_ic["aob_p1_name"], m_ic["aob_p2_name"])
m_ic["rank"] = utils.join_if_two(m_ic["aob_rank_p1"], m_ic["aob_rank_p2"])

# pts en texte lisible ("12 / 8"), sans 'None'
p1_txt = m_ic["aob_pts_p1"].astype("Int64").astype(str).replace("<NA>", "", regex=False)
p2_txt = m_ic["aob_pts_p2"].astype("Int64").astype(str).replace("<NA>", "", regex=False)
m_ic["pts"] = utils.join_if_two(p1_txt, p2_txt)

# 5) Sélection finale - Dataframe utilisable
result = m_ic[
    [
        "id",
        "type_match",
        "date",
        "division",
        "aob_team",
        "opponent_team",
        "aob_player_id",
        "player",
        "opponent_rank",
        "rank",
        "pts",
        "win",
        "aob_grind",
        "opponent_grind",
    ]
].reset_index(drop=True)

# Copie du dataframe
df = result.copy()

# Navigation dans l'onglet "Vue générale"
if onglet == "Vue générale":
    #
    players = df["player"].str.split("/")
    player_rank = df["rank"].str.split("/")
    points = df["aob_grind"].astype(str).str.split("/")
    categorie = df["type_match"].str.replace(r"\d+", "", regex=True)
    date = df["date"]
    # Explode en gardant l’alignement grâce à l’index
    df_long = pd.DataFrame(
        {
            "player": players.explode().str.strip(),
            "player_rank": player_rank.explode().str.strip(),
            "points": points.explode().str.strip().astype(int),
            "categorie": categorie,
            "date": date,
        }
    )
    #
    l1_c1, l1_c2, l1_c3, l1_c4, l1_c5 = st.columns([2, 2, 2, 2, 2], gap="small")
    with l1_c1:
        
        # Caluler la somme de points remportés en totalité
        df_points_tot_par_joueur = (
            df_long.groupby("player", as_index=False)["points"]
            .sum()
            .sort_values("points", ascending=False)
        ).reset_index(drop=True)

        # Caluler la somme de points remportés par type de match
        df_points_par_joueur = (
            df_long.groupby(["player", "categorie"], as_index=False)["points"]
            .sum()
            .sort_values("points", ascending=False)
        )

        # Dataframe du joueur ayant remporté le plus de points (avec chaque type de match)
        pts_eater = df_points_par_joueur[
            (
                df_points_par_joueur["player"]
                == df_points_tot_par_joueur.loc[0, "player"]
            )
        ].reset_index(drop=True)

        # Simple
        mask_s = pts_eater["categorie"].str.contains("S", na=False)
        pts_s = pts_eater.loc[mask_s, "points"].iloc[0] if mask_s.any() else 0
        if pts_s == 0:
            pts_s = 0
        elif "-" in str(pts_s):
            pts_s = f"{pts_s}"
        else:
            pts_s = f"+{pts_s}"
        # Double
        mask_d = pts_eater["categorie"].str.contains("D", na=False)
        pts_d = pts_eater.loc[mask_d, "points"].iloc[0] if mask_d.any() else 0
        if pts_d == 0:
            pts_d = 0
        elif "-" in str(pts_d):
            pts_d = f"{pts_d}"
        else:
            pts_d = f"+{pts_d}"
        # Mixte
        mask_m = pts_eater["categorie"].str.contains("MX", na=False)
        pts_m = pts_eater.loc[mask_m, "points"].iloc[0] if mask_m.any() else 0
        if pts_m == 0:
            pts_m = 0
        elif "-" in str(pts_m):
            pts_m = f"{pts_m}"
        else:
            pts_m = f"+{pts_m}"
        #
        utils.kpi_card("Point Eater", pts_eater["player"][0], f"{pts_s} / {pts_d} / {pts_m}")
    with l1_c2:
        # Compter les victoires dans l'ordre chronologique
        df_long = df_long.sort_values(["player", "date"])

        # Créer une colonne "is_win" sommant les victoires
        df_long["is_win"] = df_long["points"] > 0

        # Calculer le win streak pour chaque match
        def compute_streak(s):
            # s est une Series de booléens (is_win) pour UN joueur
            groups = (~s).cumsum()  # chaque défaite crée un nouveau groupe
            streak = s.groupby(groups).cumsum()
            return streak

        df_long["win_streak"] = df_long.groupby("player")["is_win"].transform(
            compute_streak
        )

        # Win Streak max par joueur
        df_win_streak = (
            df_long.groupby("player", as_index=False)["win_streak"]
            .max()
            .rename(columns={"win_streak": "best_win_streak"})
            .sort_values("best_win_streak", ascending=False)
        ).reset_index(drop=True)

        #
        utils.kpi_card(
            "Win Streaker",
            df_win_streak["player"][0],
            f"🔥{df_win_streak['best_win_streak'][0]}",
        )
    with l1_c3:
        # Nombre de match total joués par joueur
        df_match_count = (
            df_long.groupby("player", as_index=False)
            .size()  # nombre de lignes = nombre de matchs joués
            .rename(columns={"size": "nb_matchs"})
            .sort_values("nb_matchs", ascending=False)
        ).reset_index(drop=True)
        #
        utils.kpi_card(
            "Match Marathoner",
            df_match_count["player"][0],
            df_match_count["nb_matchs"][0],
        )
    with l1_c4:
        # Garder les matchs remportés
        df_wins = df_long[df_long["points"] > 0].copy()

        # Trouver la ligne avec le nombre de points maximal
        if df_wins.empty:
            # personne n'a de match gagné
            best_row = None
        else:
            best_row = df_wins[
                df_wins["points"] == df_wins["points"].max()
            ].reset_index(drop=True)

        utils.kpi_card("Clutch Performer", best_row["player"][0], f"+{best_row['points'][0]}")
    with l1_c5:
        # Winrate global par joueur
        df_winrate_par_joueur = (
            df_long.assign(is_win=df_long["points"] > 0)  # True si victoire
            .groupby("player", as_index=False)
            .agg(
                nb_matchs=("is_win", "size"),
                nb_wins=("is_win", "sum"),
                winrate=(
                    "is_win",
                    "mean",
                ),  # moyenne de True/False = ratio de victoires
            )
        )

        # passer le winrate en pourcentage
        df_winrate_par_joueur["winrate"] = (
            df_winrate_par_joueur["winrate"] * 100
        ).round(1)

        # optionnel : trier par winrate puis nb_matchs
        df_winrate_par_joueur = df_winrate_par_joueur.sort_values(
            ["winrate", "nb_matchs"], ascending=[False, False]
        ).reset_index(drop=True)

        # Winrate par type de match
        df_winrate_par_joueur_cat = (
            df_long.assign(is_win=df_long["points"] > 0)
            .groupby(["player", "categorie"], as_index=False)
            .agg(
                nb_matchs=("is_win", "size"),
                nb_wins=("is_win", "sum"),
                winrate=("is_win", "mean"),
            )
        )

        df_winrate_par_joueur_cat["winrate"] = (
            df_winrate_par_joueur_cat["winrate"] * 100
        ).round(1)

        df_winrate_par_joueur_cat = df_winrate_par_joueur_cat.sort_values(
            ["player", "categorie"], ascending=[False, False]
        ).reset_index(drop=True)

        df_winrate_master = df_winrate_par_joueur_cat[
            (df_winrate_par_joueur_cat["player"] == df_winrate_par_joueur["player"][0])
        ].reset_index(drop=True)

        # Simple
        mask_s_cat = df_winrate_master["categorie"].str.contains("S", na=False)
        pts_s_cat = (
            df_winrate_master.loc[mask_s_cat, "winrate"].iloc[0]
            if mask_s_cat.any()
            else 0
        )
        nb_s_cat = (
            df_winrate_master.loc[mask_s_cat, "nb_matchs"].iloc[0]
            if mask_s_cat.any()
            else 0
        )
        # Double
        mask_d_cat = df_winrate_master["categorie"].str.contains("D", na=False)
        pts_d_cat = (
            df_winrate_master.loc[mask_d_cat, "winrate"].iloc[0]
            if mask_d_cat.any()
            else 0
        )
        nb_d_cat = (
            df_winrate_master.loc[mask_d_cat, "nb_matchs"].iloc[0]
            if mask_d_cat.any()
            else 0
        )
        # Mixte
        mask_m_cat = df_winrate_master["categorie"].str.contains("MX", na=False)
        pts_m_cat = (
            df_winrate_master.loc[mask_m_cat, "winrate"].iloc[0]
            if mask_m_cat.any()
            else 0
        )
        nb_m_cat = (
            df_winrate_master.loc[mask_m_cat, "nb_matchs"].iloc[0]
            if mask_m_cat.any()
            else 0
        )

        #
        utils.kpi_card(
            "Winrate Master",
            df_winrate_master["player"][0],
            f"{pts_s_cat}%({nb_s_cat}) / {pts_d_cat}%({nb_d_cat}) / {pts_m_cat}%({nb_m_cat})",
        )
    #
    l2_c1, l2_c2, l2_c3 = st.columns([3, 3, 3], gap="small")
    with l2_c1:
        tot_W = (TABLE_INTERCLUB["aob_score"] > TABLE_INTERCLUB["opponent_score"]).sum()
        tot_L = (TABLE_INTERCLUB["aob_score"] < TABLE_INTERCLUB["opponent_score"]).sum()
        tot_D = (TABLE_INTERCLUB["aob_score"] == TABLE_INTERCLUB["opponent_score"]).sum()
        winrate_piechart(value1=tot_W, value2=tot_L, value3=tot_D, unit="pct", legend=["Victoire", "Défaite", "Egalité"], key="1")
    with l2_c2:
        df_players = utils.TABLE_PLAYERS
        tot_H = (df_players["gender"] == "H").sum()
        tot_F = (df_players["gender"] == "F").sum()
        tot_NG = (df_players["gender"] == "NG").sum()
        winrate_piechart(value1=tot_H, value2=tot_F, value3=tot_NG, unit="tot", legend=["Hommes", "Femmes", "Non-Genré"], key="2", colors=["#4C9DFF", "#FF9DF8", "#878787"])
    with l2_c3:
        df_match = utils.TABLE_MATCHS
        tot_simple = (df_match[df_match["type_match"].astype(str).str.startswith(("SH", "SD"))]["win"].eq("aob").sum())
        tot_double = (df_match[df_match["type_match"].astype(str).str.startswith(("DH", "DD"))]["win"].eq("aob").sum())
        tot_mixte = (df_match[df_match["type_match"].astype(str).str.startswith(("MX"))]["win"].eq("aob").sum())
        #
        pct_simple = round((tot_simple/df_match["type_match"].astype(str).str.startswith(("SH", "SD")).sum())*100,1)
        pct_doule = round((tot_double/df_match["type_match"].astype(str).str.startswith(("DH", "DD")).sum())*100,1)
        pct_mixte = round((tot_mixte/df_match["type_match"].astype(str).str.startswith(("MX")).sum())*100,1)
        winrate_piechart(value1=tot_simple, value2=tot_double, value3=tot_mixte, unit="ratio", legend=["Simple", "Double", "Mixte"], key="3", colors=["#EC3232", "#2BEAC7", "#DEF41E"], pct_list=[pct_simple,pct_doule,pct_mixte])
    

##################################################################
#                            JOUEURS                             #
##################################################################

elif onglet == "Joueurs":
    filtered_df = df[["id", "aob_player_id", "type_match", "player", "rank", "date", "opponent_team", "aob_grind"]]
    joueurs = players["name"].unique().tolist()

    @st.dialog("Fiche joueur")
    def show_player_modal(player_id):
        """Affichage de la popup d'un joueur suite au clic sur le bouton à côté
        de la carte d'un joueur spécifique.
        
        Args:
            player_id (str): division de l'équipe.
        """
        player = players.loc[players["id_player"] == player_id].iloc[0]
        
        l1_c1, l1_c2 = st.columns([7,3], gap="small")
        with l1_c1:
            # Photo du joueur
            path_photo = Path(f"{ASSETS_DIR}{player['id_player']}.webp")
            if path_photo.is_file():
                html = f"""
                <div style="display:flex; justify-content:center; padding:8px; border-radius:12px">
                {utils.img_to_html(f"{ASSETS_DIR}/{player['id_player']}.webp", alt="Logo", style="width:220px; border-radius:12px;")}
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)
            else:
                html = f"""
                <div style="display:flex; justify-content:center; padding:8px; border-radius:12px">
                {utils.img_to_html(f"{ASSETS_DIR}/{player['gender']}_nophoto.png", alt="Logo", style="width:220px; border-radius:12px;")}
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)
        
        with l1_c2:
            html = f"""
            <div style="display:flex; justify-content:center; padding:8px; border-radius:12px">
            {utils.img_to_html(f"{ASSETS_TEAM_DIR}/{player['division'][:2]}_logo.png", alt="Logo", style="width:100px; border-radius:12px;")}
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
            st.subheader(player["name"])
            st.metric(f"{player['division']} - {player['age']} ans ({'♂' if player['gender'] == 'H' else '♀'})", "")
        
        # Classements
        st.divider()

        player_sel = player["name"]
        target = player_sel.strip().casefold()
        # explode pour un match vectorisé sur chaque token séparé par '/'
        tokens = (
            filtered_df["player"]
            .fillna("")
            .str.split("/")  # -> liste de noms
            .explode()  # une ligne par nom
            .str.strip()
            .str.casefold()  # normalisation
        )

        #
        df_kpi = filtered_df[filtered_df["player"].astype(str).str.contains(player["name"], na=False)].reset_index(drop=True).copy()

        # Rencontres jouées par le joueur sélectionné
        journeys = list(df_kpi.id.unique())

        # Dataframe des activités
        df_activity = pd.DataFrame(
            [], columns=["date", "opponent", "simple", "double", "mixte"]
        )
        for d in journeys:
            df_popup = df_kpi[df_kpi["id"] == d].reset_index(drop=True)
            df_popup["date"] = pd.to_datetime(df_popup["date"], errors="coerce")
            df_popup["date"] = df_popup["date"].dt.strftime("%d-%m-%Y")

            if df_popup.empty:
                continue  # au cas où aucune ligne pour cette date

            row_idx = len(df_activity)  # index du nouveau dataframe

            df_activity.loc[row_idx, "date"] = df_popup.loc[0, "date"]
            df_activity.loc[row_idx, "opponent"] = df_popup.loc[0, "opponent_team"]

            for i in range(len(df_popup)):
                if df_popup.loc[i, "type_match"].startswith(("SH", "SD")):
                    df_activity.loc[row_idx, "simple"] = df_popup.loc[i, "aob_grind"]
                if df_popup.loc[i, "type_match"].startswith(("DH", "DD")):
                    df_activity.loc[row_idx, "double"] = (
                        df_popup.loc[i, "aob_grind"].split("/")[0]
                        if df_popup.loc[i, "player"].split("/")[0] == player_sel
                        else df_popup.loc[i, "aob_grind"].split("/")[1]
                    )
                if df_popup.loc[i, "type_match"].startswith("MX"):
                    df_activity.loc[row_idx, "mixte"] = (
                        df_popup.loc[i, "aob_grind"].split("/")[0]
                        if df_popup.loc[i, "player"].split("/")[0] == player_sel
                        else df_popup.loc[i, "aob_grind"].split("/")[1]
                    )

        # Entete des catégories
        row_title = f"""
            <div style='
                display: flex;
                flex-wrap: nowrap;
                align-items: center;
                gap: 6px;
                overflow-x: auto;
                padding: 4px 0;
            '>
                <div style='
                    flex: 0 0 100px;          /* largeur fixe de la "colonne" date+équipe */
                    max-width: 180px;
                    white-space: nowrap;      /* tout sur une ligne */
                    overflow: hidden;         /* si trop long, on coupe */
                    text-overflow: ellipsis;  /* ... à la fin */
                    color: white;
                    font-weight: bold;
                '>
                </div>
                <div style='
                        flex: 0 0 100px;          /* largeur fixe de la "colonne" date+équipe */
                        max-width: 180px;
                        white-space: nowrap;      /* tout sur une ligne */
                        overflow: hidden;         /* si trop long, on coupe */
                        text-overflow: ellipsis;  /* ... à la fin */
                        color: white;
                        font-weight: bold;
                    '>
                </div>
                {utils.box_html_indiv("transparent", "S")}
                {utils.box_html_indiv("transparent", "D")}
                {utils.box_html_indiv("transparent", "M")}
            """
        st.markdown(row_title, unsafe_allow_html=True)

        # Points remportés ou non à chaque rencontre
        for k in range(len(df_activity) - 1, -1, -1):
            row_html = f"""
                <div style='
                    display: flex;
                    flex-wrap: nowrap;
                    align-items: center;
                    gap: 6px;
                    overflow-x: auto;
                    padding: 4px 0;
                '>
                    <div style='
                        flex: 0 0 100px;          /* largeur fixe de la "colonne" date+équipe */
                        max-width: 180px;
                        white-space: nowrap;      /* tout sur une ligne */
                        overflow: hidden;         /* si trop long, on coupe */
                        text-overflow: ellipsis;  /* ... à la fin */
                        color: white;
                        font-weight: bold;
                    '>
                        {df_activity.date[k]}
                    </div>
                    <div style='
                        flex: 0 0 100px;          /* largeur fixe de la "colonne" date+équipe */
                        max-width: 180px;
                        white-space: nowrap;      /* tout sur une ligne */
                        overflow: hidden;         /* si trop long, on coupe */
                        text-overflow: ellipsis;  /* ... à la fin */
                        color: white;
                        font-weight: bold;
                    '>
                        {df_activity.opponent[k]}
                    </div>
                    {utils.match_box_indiv(df_activity, 'simple', k)}
                    {utils.match_box_indiv(df_activity, 'double', k)}
                    {utils.match_box_indiv(df_activity, 'mixte', k)}
                """

            st.markdown(row_html, unsafe_allow_html=True)

    for i, joueur in enumerate(joueurs):
        player_row = players.loc[players["name"] == joueur].iloc[0]

        player_id = player_row["id_player"]
        age = player_row["age"]
        gender = player_row["gender"]
        team = player_row["division"]

        ranks = [
            actual_rank(filtered_df, joueur, "SH|SD"),
            actual_rank(filtered_df, joueur, "DD|DH"),
            actual_rank(filtered_df, joueur, "MX"),
        ]

        with stylable_container(
            key=f"player_row_{player_id}",
            css_styles="""
            {
                position: relative;
                width: 100%;
                max-width: 100%;
                min-height: 67px;
                overflow: hidden;
            }

            /* Bouton Streamlit à gauche */
            div.stButton {
                position: absolute !important;
                left: 0 !important;
                top: 0 !important;
                width: 5% !important;
                min-width: 38px !important;
                height: 63px !important;
                z-index: 2 !important;
            }

            div.stButton > button {
                width: 100% !important;
                height: 63px !important;
                min-height: 63px !important;
                padding: 0 !important;
                border-radius: 14px !important;
                background: #111827 !important;
                border: 1px solid #111827 !important;
                color: white !important;
                font-size: 18px !important;
                font-weight: 700 !important;
                box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
                transition: all 0.15s ease !important;
            }

            div.stButton > button:hover {
                background: #374151 !important;
                border-color: #374151 !important;
                color: white !important;
                transform: translateY(-1px);
            }

            /* Card HTML à droite */
            iframe {
                position: absolute !important;
                left: calc(5% + 6px) !important;
                top: 0 !important;
                width: calc(95% - 6px) !important;
                max-width: calc(95% - 6px) !important;
                height: 67px !important;
                overflow: hidden !important;
            }
            """
        ):
            if st.button(
                "",
                key=f"open_player_{player_id}",
                use_container_width=True
            ):
                show_player_modal(player_id)

            html_card = f"""
            <div style="
                width: 100%;
                max-width: 100%;
                height: 63px;
                box-sizing: border-box;
                padding: 10px 12px;
                border-radius: 14px;
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 8px;
                font-family: Arial, sans-serif;
                box-shadow: 0 2px 10px rgba(0,0,0,0.04);
                overflow: hidden;
                margin-top: -7px;
            ">
                <div style="
                    min-width: 0;
                    flex: 1 1 auto;
                    overflow: hidden;
                ">
                    <div style="
                        font-size: 15px;
                        font-weight: 700;
                        color: #111827;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    ">
                        {joueur}
                    </div>
                </div>

                <div style="
                    display: flex;
                    gap: 5px;
                    align-items: center;
                    flex-shrink: 0;
                ">
                    <div style="
                        padding: 6px 7px;
                        border-radius: 9px;
                        background: {utils.rank_stylizing(ranks[0])};
                        color: #FFFFFF;
                        font-size: 11px;
                        font-weight: 700;
                        min-width: 28px;
                        text-align: center;
                        box-sizing: border-box;
                    ">
                        {ranks[0]}
                    </div>

                    <div style="
                        padding: 6px 7px;
                        border-radius: 9px;
                        background: {utils.rank_stylizing(ranks[1])};
                        color: #FFFFFF;
                        font-size: 11px;
                        font-weight: 700;
                        min-width: 28px;
                        text-align: center;
                        box-sizing: border-box;
                    ">
                        {ranks[1]}
                    </div>

                    <div style="
                        padding: 6px 7px;
                        border-radius: 9px;
                        background: {utils.rank_stylizing(ranks[2])};
                        color: #FFFFFF;
                        font-size: 11px;
                        font-weight: 700;
                        min-width: 28px;
                        text-align: center;
                        box-sizing: border-box;
                    ">
                        {ranks[2]}
                    </div>
                </div>
            </div>
            """

            components.html(html_card, height=67)

##################################################################
#                            EQUIPES                             #
##################################################################

elif onglet == "Équipes":
    c1, c2, c3 = st.columns([1, 1, 1], gap="small")
    
    def team_list(team: str):
        """Récupération de l'effectif d'une équipe sous la forme d'une liste de string.
        
        Args:
            team (str): division de l'équipe.
        """
        mask = players["division"].str.contains(team, na=False)
        return players.loc[mask, "name"].tolist()

    def team_card(
        key_id: str,
        team: str,
        logo_path: str,
        team_name: str,
        captain: str,
        players: list[str],
    ):
        """Cartes des équipes d'interclub affichant les informations relatives à celle-ci telles
        que son effectif, ses résultats sur les différentes rencontres et les statistiques inhérentes

        Args:
            key_id (int): id assigné à la carte.
            team (str): division de l'équipe.
            logo_path (str): chemin relatif vers le logo de l'équipe.
            team_name (str): nom de l'équipe.
            captain (str): nom et prénom du capitaine de l'équipe
            players (list[str]): liste des joueurs composant l'effectif. 
        """
        with stylable_container(
            key=f"team_card_{key_id}",
            css_styles="""
            {
                width: 100%;
                min-height: 230px;
                box-sizing: border-box;
                padding: 18px;
                border-radius: 20px;
                background: rgba(204, 205, 211);
                border: 1px solid #e5e7eb;
                font-family: Arial, sans-serif;
                box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
            }
            """
        ):
            top_left, top_right = st.columns([1, 3], vertical_alignment="center")

            with top_left:
                st.image(logo_path, width=90)

            with top_right:
                st.markdown(
                    f"""
                    <div style="
                        font-size: 18px;
                        font-weight: 800;
                        color: #111827;
                        line-height: 1.2;
                    ">
                        {team_name} ({team})
                    </div>

                    <div style="
                        margin-top: 12px;
                        display: inline-block;
                        width: fit-content;
                        padding: 5px 10px;
                        border-radius: 999px;
                        background: #eef2ff;
                        color: #3730a3;
                        font-size: 12px;
                        font-weight: 700;
                    ">
                        Capitaine : {captain}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                """
                <div style="
                    margin-top: 15px;
                    padding-top: 14px;
                    border-top: 1px solid #e5e7eb;
                "></div>
                """,
                unsafe_allow_html=True,
            )

            _left, _sp, _right = st.columns([3, 3, 3])

            with _left:
                show = st.toggle(
                    "Afficher l'effectif",
                    key=f"details_{key_id}_effectif",
                    value=False,
                )

            if show:
                players_html = "".join(
                    f"""
                    <span style="
                        display: inline-block;
                        padding: 4px 8px;
                        margin: 0px;
                        border-radius: 999px;
                        background: #f3f4f6;
                        color: #374151;
                        font-size: 12px;
                        font-weight: 600;
                        border: 1px solid #e5e7eb;
                    ">
                        {player}
                    </span>
                    """
                    for player in players
                )
                
                st.markdown(
                    f"""
                    <div style="
                        display: flex;
                        flex-direction: row;
                        flex-wrap: wrap;
                        align-items: flex-start;
                        gap: 6px;
                        padding-bottom: 2px;
                        margin-top: 0px;
                    ">
                        {players_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                
            with _sp:
                show = st.toggle(
                    "Afficher les matchs",
                    key=f"details_{key_id}_match",
                    value=False,
                )

            if show:
                df_team_page = utils.TABLE_MATCHS.merge(
                    utils.TABLE_INTERCLUB,
                    how="left",
                    on="id"
                )
                df_division = df_team_page[df_team_page["division"] == team].copy()

                df_division["date"] = pd.to_datetime(
                    df_division["date"],
                    errors="coerce"
                )

                journey_ids = list(df_division.id.unique())[
                    ::-1
                ]  # De la date la + récente à la plus ancienne
                for d in journey_ids:
                    id_df = df_division[(df_division.id == d)].reset_index(drop=True)
                    utils.matrix_color(df=id_df, division=team)
                    
            with _right:
                show = st.toggle(
                    "Afficher les stats",
                    key=f"details_{key_id}",
                    value=False,
                )
            if show:
                df_team_page = utils.TABLE_MATCHS.merge(
                    utils.TABLE_INTERCLUB,
                    how="left",
                    on="id"
                )
                df_team_page = df_team_page[df_team_page["division"] == team].reset_index(drop=True)
                df_division = df_team_page[df_team_page["division"] == team].copy()

                utils.kpi_card("Rencontres jouées", f'{df_team_page["id"].nunique()}', "saison 2025/26")
                # Définir V/D/E
                def match_output(team):
                    df = TABLE_INTERCLUB[(TABLE_INTERCLUB["division"] == team)].reset_index(
                        drop=True
                    )
                    v = (df["aob_score"] > df["opponent_score"]).sum()
                    d = (df["aob_score"] < df["opponent_score"]).sum()
                    e = (df["aob_score"] == df["opponent_score"]).sum()

                    # Calcul du nombre de points
                    pts = v * 3 + e * 2 + d * 1
                    return v, e, d, pts

                utils.kpi_card(
                    "Résultats",
                    f"{str(match_output(team)[0])} / {str(match_output(team)[1])} / {str(match_output(team)[2])}",
                    "Victoire(s) / Egalité(s) / Défaite(s)",
                )
                utils.kpi_card(
                    "Matchs joués",
                    f'{len(df[(df["type_match"].isin(["SH1","SH2","SH3","SH4","SD1","SD2"]))])} / {len(df[(df["type_match"].isin(["DH","DH1","DH2","DD", "DD1"]))])} / {len(df[(df["type_match"].isin(["MX","MX1","MX2"]))])}',
                    "Simple / Double / Mixte",
                )
                total_wins = len(df_division[df_division["win"] == "aob"])
                double_wins = len(
                    df_division[
                        (df_division["type_match"].isin(["DH", "DH1", "DH2", "DD", "DD1", "DD2"]))
                        & (df_division["win"] == "aob")
                    ]
                )
                mixed_wins = len(
                    df_division[
                        (df_division["type_match"].isin(["MX", "MX1", "MX2"]))
                        & (df_division["win"] == "aob")
                    ]
                )
                stats = f"{total_wins} / {double_wins} / {mixed_wins}"
                s_rate = utils.group_rate(df_division, utils.S_TYPES)
                d_rate = utils.group_rate(df_division, utils.D_TYPES)
                m_rate = utils.group_rate(df_division, utils.M_TYPES)

                utils.kpi_card(
                    "Victoires",
                    f'{stats}',
                    f"{s_rate} / {d_rate} / {m_rate}",
                )
                interclub_team_sel = TABLE_INTERCLUB[
                    (TABLE_INTERCLUB["division"] == team)
                ].reset_index(drop=True)

                # Nouvelle colonnes éphémère donnant l'issue du match
                interclub_team_sel["result"] = np.where(
                    interclub_team_sel["aob_score"] >= interclub_team_sel["opponent_score"],
                    "W",
                    np.where(
                        interclub_team_sel["aob_score"] < interclub_team_sel["opponent_score"],
                        "L",
                        "D",
                    ),  # "D" pour nul
                )

                matchs_list = interclub_team_sel[
                    "result"
                ].tolist()  # Convertion de la colonne en liste

                kpi_text, kpi_icon = (
                    ("Win Streak", utils.WIN_ICON)
                    if utils.current_streak(matchs_list)[0] == "win"
                    else ("Lose Streak", utils.COLD_ICON)
                )

                #
                utils.kpi_card("Série", f"{utils.current_streak(matchs_list)[1]} {kpi_icon}", kpi_text)

    with c1:
        team_card(1,"PR",f"{ASSETS_TEAM_DIR}/PR_logo.png","Bad'A'Boum","REBEYROL Jeanne",team_list("PR"))
        #
        team_card(2,"D5",f"{ASSETS_TEAM_DIR}/D5_logo.png","AOB35-5","BARON Jerome",team_list("D5"))
    with c2:
        team_card(3,"D2",f"{ASSETS_TEAM_DIR}/D2_logo.png","AOB35-2","BONNIER Julien",team_list("D2"))
        #
        team_card(4,"H2",f"{ASSETS_TEAM_DIR}/H2_logo.png","AOB35-1","JOUBIN Nicolas",team_list("H2"))
    with c3:
        team_card(5,"D3",f"{ASSETS_TEAM_DIR}/D3_logo.png","AOB35-3","BARON Jerome",team_list("D3"))
        #
        team_card(6,"V3",f"{ASSETS_TEAM_DIR}/V3_logo.png","Plumes grisonnantes","PIOC Matthieu",team_list("V3"))

