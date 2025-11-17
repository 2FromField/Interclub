import streamlit as st


def check_password():
    """Retourne True si le mot de passe est correct, sinon affiche le formulaire."""

    def password_entered():
        """Callback quand l’utilisateur valide le mot de passe."""
        if st.session_state.get("password") == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state[
                "password"
            ]  # on enlève des state pour ne pas le garder
        else:
            st.session_state["password_correct"] = False

    # Déjà connecté dans cette session ?
    if st.session_state.get("password_correct", False):
        return True

    # Sinon : afficher le formulaire de mot de passe
    st.title("🔐 Accès protégé")
    st.text_input(
        "Renseignez la clé d'authentification:",
        type="password",
        key="password",
        on_change=password_entered,
    )

    # Message d’erreur si tentative ratée
    if st.session_state.get("password_correct") is False:
        st.error("Mot de passe incorrect 😅")

    return False
