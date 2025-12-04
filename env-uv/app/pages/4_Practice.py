import streamlit as st
import random
from itertools import combinations
import pandas as pd

st.set_page_config(page_title="Tournoi - Poules & matchs", page_icon="🏓")

# --- FONCTIONS ---


def generer_poules(joueurs):
    """Mélange les joueurs et les répartit en poules."""
    random.shuffle(joueurs)
    n = len(joueurs)

    if n == 6:
        tailles = [3, 3]  # 2 poules de 3
    elif n == 8:
        tailles = [4, 4]  # 2 poules de 4
    elif n == 10:
        tailles = [5, 5]  # 2 poules de 5
    elif n == 12:
        tailles = [3, 3, 3, 3]  # 4 poules de 3
    else:
        raise ValueError("Nombre de joueurs non supporté")

    poules = []
    index = 0
    for t in tailles:
        poules.append(joueurs[index : index + t])
        index += t
    return poules


def generer_matchs(poules):
    """
    Génère les matchs pour chaque poule en mode championnat
    (tous les joueurs se rencontrent).
    Retourne une liste de dicts avec un id de match.
    """
    matchs = []
    match_id = 0
    for num_poule, poule in enumerate(poules, start=1):
        for j1, j2 in combinations(poule, 2):
            matchs.append(
                {
                    "id": match_id,
                    "poule": num_poule,
                    "joueur1": j1,
                    "joueur2": j2,
                }
            )
            match_id += 1
    return matchs


def calculer_classements(matchs, nb_poules):
    """
    Calcule le classement de chaque poule à partir des scores
    entrés dans st.session_state.

    Hypothèse :
    - Tu saisis les points marqués par chaque joueur pour chaque set.
    - On considère jusqu'à 3 sets par match.
    """
    classements = {p: {} for p in range(1, nb_poules + 1)}

    for match in matchs:
        poule = match["poule"]
        j1 = match["joueur1"]
        j2 = match["joueur2"]
        mid = match["id"]

        # Initialisation des joueurs dans la poule
        for joueur in [j1, j2]:
            if joueur not in classements[poule]:
                classements[poule][joueur] = {
                    "Joueur": joueur,
                    "Victoires": 0,
                    "Sets": 0,
                    "Points": 0,
                }

        p1_sets = p2_sets = 0
        p1_points = p2_points = 0

        # On parcourt les 3 sets max
        for s in [1, 2, 3]:
            s1 = st.session_state.get(f"m{mid}_j1_s{s}", 0)
            s2 = st.session_state.get(f"m{mid}_j2_s{s}", 0)

            # Si les deux sont à 0, on considère le set comme non joué
            if s1 == 0 and s2 == 0:
                continue

            p1_points += s1
            p2_points += s2

            if s1 > s2:
                p1_sets += 1
            elif s2 > s1:
                p2_sets += 1
            # égalité : aucun set gagné

        # Si aucun set/point saisi, on ignore le match
        if p1_sets == 0 and p2_sets == 0 and p1_points == 0 and p2_points == 0:
            continue

        # Victoire du match (on ne gère pas les égalités complètes)
        if p1_sets > p2_sets:
            classements[poule][j1]["Victoires"] += 1
        elif p2_sets > p1_sets:
            classements[poule][j2]["Victoires"] += 1

        # Ajout des sets gagnés
        classements[poule][j1]["Sets"] += p1_sets
        classements[poule][j2]["Sets"] += p2_sets

        # Ajout de l'écart de points
        classements[poule][j1]["Points"] += p1_points - p2_points
        classements[poule][j2]["Points"] += p2_points - p1_points

    return classements


def saisir_match_ko(label: str, match_key: str, joueur1: str, joueur2: str):
    """
    Affiche un match à élimination directe (demie/finale) avec saisie des scores
    en 3 sets max, et retourne le vainqueur (ou None si pas encore déterminable).
    """
    st.markdown(f"**{label}** : {joueur1} vs {joueur2}")

    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    with col1:
        st.markdown(
            f'<div style="text-align:center; margin-top:20px">'
            f'<p style="margin-top:30px">{joueur1}</p>'
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="text-align:center; margin-top:20px">'
            f'<p style="margin-top:10px;">{joueur2}</p>'
            f"</div>",
            unsafe_allow_html=True,
        )

    p1_sets = p2_sets = 0
    p1_points = p2_points = 0

    # 3 sets max comme pour les poules
    for s in [1, 2, 3]:
        with [col2, col3, col4][s - 1]:
            s1 = st.number_input(
                f"Set {s}",
                key=f"{match_key}_j1_s{s}",
                min_value=0,
                step=1,
            )
            s2 = st.number_input(
                "",
                key=f"{match_key}_j2_s{s}",
                min_value=0,
                step=1,
                label_visibility="collapsed",
            )

        if s1 == 0 and s2 == 0:
            continue

        p1_points += s1
        p2_points += s2

        if s1 > s2:
            p1_sets += 1
        elif s2 > s1:
            p2_sets += 1

    # Si rien n'est saisi
    if p1_sets == 0 and p2_sets == 0 and p1_points == 0 and p2_points == 0:
        return None

    # Détermination du vainqueur
    if p1_sets > p2_sets:
        return joueur1
    elif p2_sets > p1_sets:
        return joueur2
    else:
        # Égalité en sets : on départage aux points
        if p1_points > p2_points:
            return joueur1
        elif p2_points > p1_points:
            return joueur2
        else:
            # Perfect tie → pas de vainqueur clair (à gérer manuellement si besoin)
            return None


# --- INIT SESSION ---

if "poules" not in st.session_state:
    st.session_state.poules = None
if "joueurs" not in st.session_state:
    st.session_state.joueurs = []
if "matchs" not in st.session_state:
    st.session_state.matchs = []
if "classements" not in st.session_state:
    st.session_state.classements = None


st.title("Tournoi - Phases de poules")

# --- FORMULAIRE ---

nb_joueurs = st.selectbox(
    "Nombre de joueurs :",
    options=[6, 8, 10, 12],
    index=0,
)

st.write("Saisis les noms des joueurs :")

with st.form("form_joueurs"):
    noms = []
    for i in range(nb_joueurs):
        nom = st.text_input(f"Joueur {i+1}", key=f"joueur_{i}")
        noms.append(nom)

    submitted = st.form_submit_button("Générer les poules et les matchs")

# Traitement après submit
if submitted:
    # Nettoyage et vérification
    noms_valides = [n.strip() for n in noms if n.strip() != ""]
    if len(noms_valides) != nb_joueurs:
        st.error("Merci de remplir tous les noms de joueurs.")
        st.session_state.poules = None
        st.session_state.matchs = []
        st.session_state.classements = None
    else:
        st.session_state.joueurs = noms_valides
        st.session_state.poules = generer_poules(noms_valides)
        st.session_state.matchs = generer_matchs(st.session_state.poules)
        st.session_state.classements = None  # on reset les classements
        st.success("Poules et matchs générés ✅")


# --- AFFICHAGE DES MATCHS AVEC SCORES ---

st.markdown("---")

if st.session_state.matchs:
    matchs = st.session_state.matchs
    nb_poules = len(st.session_state.poules)

    for num_poule in range(1, nb_poules + 1):
        st.markdown(f"### Poule {num_poule} - Matchs")

        matchs_poule = [m for m in matchs if m["poule"] == num_poule]

        for match in matchs_poule:
            mid = match["id"]

            # 7 colonnes : J1 | S1 S2 S3 | S1 S2 S3 | J2
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.markdown(
                    f'<div style="text-align:center; margin-top:20px">'
                    f'<p style="margin-top:30px">{match["joueur1"]}</p>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div style="text-align:center; margin-top:20px">'
                    f'<p style="margin-top:10px;">{match["joueur2"]}</p>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

            with col2:
                st.number_input(
                    "Set 1",
                    key=f"m{mid}_j1_s1",
                    min_value=0,
                    step=1,
                )
                st.number_input(
                    "",
                    key=f"m{mid}_j2_s1",
                    min_value=0,
                    step=1,
                    label_visibility="collapsed",
                )
            with col3:
                st.number_input(
                    "Set 2",
                    key=f"m{mid}_j1_s2",
                    min_value=0,
                    step=1,
                )
                st.number_input(
                    "",
                    key=f"m{mid}_j2_s2",
                    min_value=0,
                    step=1,
                    label_visibility="collapsed",
                )
            with col4:
                st.number_input(
                    "Set 3",
                    key=f"m{mid}_j1_s3",
                    min_value=0,
                    step=1,
                )
                st.number_input(
                    "",
                    key=f"m{mid}_j2_s3",
                    min_value=0,
                    step=1,
                    label_visibility="collapsed",
                )
else:
    st.info("Les matchs seront affichés après génération des poules.")


# --- CLASSEMENTS SOUS FORME DE DATAFRAME ---

st.markdown("---")
st.subheader("Classements")

if st.session_state.matchs:
    # Bouton "submit" global pour mettre à jour les classements
    if st.button("Mettre à jour les classements"):
        st.session_state.classements = calculer_classements(
            st.session_state.matchs, len(st.session_state.poules)
        )

    if st.session_state.classements:
        for num_poule, joueurs_dict in st.session_state.classements.items():
            st.markdown(f"### Poule {num_poule}")
            df = pd.DataFrame(list(joueurs_dict.values()))
            # Tri : victoires puis sets gagnés puis écart de points
            df = df.sort_values(
                by=["Victoires", "Sets", "Points"],
                ascending=False,
            ).reset_index(drop=True)
            df.index = df.index + 1  # classement à partir de 1
            st.dataframe(df, use_container_width=True)
    else:
        st.info(
            "Clique sur **Mettre à jour les classements** après avoir saisi des scores."
        )

# --- PHASE FINALE ---

st.markdown("---")
st.subheader("Phase finale")

if st.session_state.classements:
    nb_poules = len(st.session_state.poules)

    # On reconstruit les classements triés pour récupérer les 1ers / 2es
    classements_ordonnes = {}
    for num_poule, joueurs_dict in st.session_state.classements.items():
        df = pd.DataFrame(list(joueurs_dict.values()))
        df = df.sort_values(
            by=["Victoires", "Sets", "Points"],
            ascending=False,
        ).reset_index(drop=True)
        classements_ordonnes[num_poule] = df

    # ====================
    # CAS 2 POULES (6, 8, 10 joueurs)
    # ====================
    if nb_poules == 2:
        st.markdown("### Demi-finales")

        df_A = classements_ordonnes[1]
        df_B = classements_ordonnes[2]

        # 1er A vs 2e B, 1er B vs 2e A
        if len(df_A) >= 2 and len(df_B) >= 2:
            A1 = df_A.iloc[0]["Joueur"]
            A2 = df_A.iloc[1]["Joueur"]
            B1 = df_B.iloc[0]["Joueur"]
            B2 = df_B.iloc[1]["Joueur"]

            vainqueur_d1 = saisir_match_ko("Demi-finale 1", "demi1", A1, B2)
            vainqueur_d2 = saisir_match_ko("Demi-finale 2", "demi2", B1, A2)

            # Finale si on a les deux vainqueurs
            if vainqueur_d1 and vainqueur_d2:
                st.markdown("### Finale")
                vainqueur_finale = saisir_match_ko(
                    "Finale", "finale", vainqueur_d1, vainqueur_d2
                )

                if vainqueur_finale:
                    st.success(f"🏆 Vainqueur du tournoi : **{vainqueur_finale}**")

        else:
            st.warning(
                "Pas assez de joueurs classés dans chaque poule pour générer la phase finale."
            )

    # ====================
    # CAS 4 POULES (12 joueurs)
    # ====================
    elif nb_poules == 4:
        st.markdown(
            "Pour 4 poules : seuls les **1ers** de chaque poule vont en demi-finales."
        )
        st.markdown("### Demi-finales")

        try:
            A1 = classements_ordonnes[1].iloc[0]["Joueur"]
            B1 = classements_ordonnes[2].iloc[0]["Joueur"]
            C1 = classements_ordonnes[3].iloc[0]["Joueur"]
            D1 = classements_ordonnes[4].iloc[0]["Joueur"]
        except IndexError:
            st.warning(
                "Certains classements de poule sont incomplets, impossible de générer la phase finale."
            )
        else:
            vainqueur_d1 = saisir_match_ko("Demi-finale 1", "demi1", A1, B1)
            vainqueur_d2 = saisir_match_ko("Demi-finale 2", "demi2", C1, D1)

            if vainqueur_d1 and vainqueur_d2:
                st.markdown("### Finale")
                vainqueur_finale = saisir_match_ko(
                    "Finale", "finale", vainqueur_d1, vainqueur_d2
                )

                if vainqueur_finale:
                    st.success(f"🏆 Vainqueur du tournoi : **{vainqueur_finale}**")

    else:
        st.info("Phase finale non définie pour cette configuration de poules.")
else:
    st.info("Génère les poules et classements avant de lancer la phase finale.")
