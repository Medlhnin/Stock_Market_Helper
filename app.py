import streamlit as st
import math
import hmac
import psycopg

from decimal import Decimal
from psycopg.rows import dict_row

st.set_page_config(page_title="Simulateur Trading", layout="centered")

st.title("📈 Simulateur de Trading")

# Constantes
frais_achat = 0.0099
frais_vente = 0.01
taxe = 0.15  # TPCVM

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Trading (objectif)",
    "💰 Gain actuel",
    "📈 Compound interest ",
    "⏳ Calcul du temps t",
    "💼 Mon portefeuille"
])
# =========================================================
# TAB 1 : Objectif de gain
# =========================================================
with tab1:

    st.markdown("### 🧮 1. Paramètres d'achat")

    prix = st.number_input("Prix d'achat de l'action (DH)", min_value=0.0, value=100.0, key="prix_achat")
    qte = st.number_input("Quantité achetée", min_value=1, value=10, key="qte_achat")

    pne = qte * prix * (1 + frais_achat)

    st.markdown("### 💰 Résultat achat")
    st.write(f"**Prix Net Exécuté (PNE)** : {pne:.2f} DH")

    st.markdown("---")

    st.markdown("### 🎯 2. Objectif")

    gain = st.number_input("Gain souhaité (DH)", min_value=0.0, value=200.0)

    po = pne + gain

    pc = (po - pne * taxe) / (1 - frais_vente - (1 - frais_vente) * taxe)

    prix_vente_unitaire = pc / qte

    st.markdown("### 📊 Résultat final")
    st.write(f"**Prix Objectif (PO)** : {po:.2f} DH")
    st.write(f"**Prix de Cession (PC)** : {pc:.2f} DH")
    st.write(f"**Prix de vente par action** : {prix_vente_unitaire:.2f} DH")

    rentabilite = (gain / pne) * 100 if pne > 0 else 0
    st.write(f"📈 **Rentabilité** : {rentabilite:.2f} %")


# =========================================================
# TAB 2 : Gain actuel
# =========================================================
with tab2:

    st.markdown("### 📊 1. Position actuelle")

    prix_achat = st.number_input("Prix d'achat moyen (DH)", min_value=0.0, value=100.0, key="pa")
    prix_actuel = st.number_input("Prix actuel de l'action (DH)", min_value=0.0, value=120.0)
    qte2 = st.number_input("Quantité détenue", min_value=1, value=10, key="qte2")

    pne2 = qte2 * prix_achat * (1 + frais_achat)

    valeur_vente_brute = qte2 * prix_actuel
    valeur_vente_nette = valeur_vente_brute * (1 - frais_vente)

    gain_brut = valeur_vente_nette - pne2
    gain_net = gain_brut * (1 - taxe)

    st.markdown("### 💰 Résultat simulation vente")

    st.write(f"**Valeur de vente brute** : {valeur_vente_brute:.2f} DH")
    st.write(f"**Valeur après frais de vente** : {valeur_vente_nette:.2f} DH")

    st.write(f"📈 **Gain brut** : {gain_brut:.2f} DH")
    st.write(f"💵 **Gain net après TPCVM** : {gain_net:.2f} DH")

    rent = (gain_net / pne2) * 100 if pne2 > 0 else 0
    st.write(f"📊 **Rentabilité nette** : {rent:.2f} %")

with tab3:

    st.markdown("### 📈 Formule : A = P(1 + r)^t")

    P = st.number_input("Capital initial P", value=1000.0)
    r = st.number_input("Taux r (ex: 5% = 0.05)", value=0.05)
    t = st.number_input("Temps t (années)", value=5.0)

    A = P * (1 + r) ** t

    st.write(f"📌 Capital final A : **{A:.2f}**")

# =========================================================
# TAB 4 : CALCUL DU TEMPS t
# =========================================================
with tab4:

    st.markdown("### ⏳ Formule : t = ln(A/P) / ln(1+r)")

    P2 = st.number_input("Capital initial P", value=1000.0, key="P2")
    A2 = st.number_input("Capital final A", value=2000.0)
    r2 = st.number_input("Taux r", value=0.05, key="r2")

    if P2 > 0 and r2 > -1 and r2 != 0:
        t_calc = math.log(A2 / P2) / math.log(1 + r2)
        st.write(f"⏳ Temps nécessaire t : **{t_calc:.2f} ans**")
    else:
        st.warning("Valeurs invalides pour le calcul")

def connexion_bd():
    return psycopg.connect(
        st.secrets["database"]["url"],
        row_factory=dict_row,
        connect_timeout=10,
    )


def initialiser_portefeuille():
    with connexion_bd() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS portefeuille (
                id BIGSERIAL PRIMARY KEY,
                nom TEXT NOT NULL CHECK (length(trim(nom)) > 0),
                prix_achat NUMERIC NOT NULL CHECK (prix_achat > 0),
                quantite INTEGER NOT NULL CHECK (quantite > 0),
                date_creation TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)


def ajouter_achat(nom, prix_achat, quantite):
    with connexion_bd() as conn:
        conn.execute(
            """
            INSERT INTO portefeuille (nom, prix_achat, quantite)
            VALUES (%s, %s, %s)
            """,
            (nom, Decimal(str(prix_achat)), quantite),
        )


def lire_portefeuille():
    with connexion_bd() as conn:
        return conn.execute("""
            SELECT id, nom, prix_achat, quantite
            FROM portefeuille
            ORDER BY date_creation DESC, id DESC
        """).fetchall()


def afficher_portefeuille():
    initialiser_portefeuille()

    st.subheader("Ajouter un achat")

    with st.form("form_ajout_achat", clear_on_submit=True):
        nom = st.text_input("Nom de l’action", max_chars=100)

        prix_achat = st.number_input(
            "Prix d’achat unitaire (DH)",
            min_value=0.01,
            value=100.0,
            step=0.01,
        )

        quantite = st.number_input(
            "Quantité achetée",
            min_value=1,
            value=10,
            step=1,
        )

        enregistrer = st.form_submit_button("💾 Enregistrer")

    if enregistrer:
        if not nom.strip():
            st.warning("Saisis le nom de l’action.")
        else:
            ajouter_achat(nom.strip(), prix_achat, quantite)
            st.success("Achat enregistré.")

    st.subheader("Mes investissements")
    st.caption(
        "Saisis le prix actuel de chaque action pour simuler une vente. "
        "Ces prix restent dans la session et ne sont pas enregistrés en base."
    )

    achats = lire_portefeuille()

    if not achats:
        st.info("Aucun achat enregistré pour le moment.")
        return

    taux_achat = Decimal(str(frais_achat))
    taux_vente = Decimal(str(frais_vente))
    taux_taxe = Decimal(str(taxe))

    lignes = []
    total_investi = Decimal("0")
    total_gain = Decimal("0")

    for achat in achats:
        identifiant = achat["id"]
        prix = achat["prix_achat"]
        qte = achat["quantite"]

        st.markdown(
            f"**{achat['nom']}** — {qte} action(s) "
            f"achetée(s) à {prix:.2f} DH"
        )

        actuel = st.number_input(
            "Prix actuel unitaire (DH)",
            min_value=0.0,
            value=float(prix),
            step=0.01,
            key=f"portefeuille_cours_{identifiant}",
        )

        capital_investi = prix * qte * (1 + taux_achat)
        vente_brute = Decimal(str(actuel)) * qte
        vente_nette = vente_brute * (1 - taux_vente)

        resultat_avant_taxe = vente_nette - capital_investi

        # Hypothèse de simulation :
        # taxe uniquement sur les gains positifs.
        taxe_simulee = max(
            resultat_avant_taxe, Decimal("0")
        ) * taux_taxe

        gain_net = resultat_avant_taxe - taxe_simulee
        rentabilite = gain_net / capital_investi * 100

        lignes.append({
            "Action": achat["nom"],
            "Quantité": qte,
            "Prix d’achat (DH)": float(prix),
            "Prix actuel (DH)": actuel,
            "Capital investi, frais inclus (DH)": round(
                float(capital_investi), 2
            ),
            "Gain / Perte net(te) (DH)": round(float(gain_net), 2),
            "Rentabilité (%)": round(float(rentabilite), 2),
        })

        total_investi += capital_investi
        total_gain += gain_net

    st.subheader("Récapitulatif")
    st.dataframe(lignes, hide_index=True, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    col1.metric("Capital investi", f"{total_investi:,.2f} DH")
    col2.metric("Gain / Perte net(te)", f"{total_gain:+,.2f} DH")
    col3.metric(
        "Rentabilité globale",
        f"{total_gain / total_investi * 100:+.2f} %",
    )

    st.caption(
        "Simulation basée sur les frais et le taux de taxe définis "
        "dans l’application, sans compensation fiscale entre les lignes."
    )


with tab5:
    st.header("💼 Mon portefeuille")

    if not st.session_state.get("portefeuille_autorise", False):
        with st.form("connexion_portefeuille"):
            mot_de_passe = st.text_input(
                "Mot de passe du portefeuille",
                type="password",
            )
            connexion = st.form_submit_button("Accéder")

        if connexion:
            attendu = st.secrets["portfolio"]["password"]

            if hmac.compare_digest(
                mot_de_passe.encode("utf-8"),
                attendu.encode("utf-8"),
            ):
                st.session_state["portefeuille_autorise"] = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect.")

    else:
        if st.button("Se déconnecter du portefeuille"):
            st.session_state["portefeuille_autorise"] = False
            st.rerun()

        try:
            afficher_portefeuille()
        except psycopg.Error:
            st.error(
                "Impossible d’accéder à la base de données. "
                "Vérifie la connexion PostgreSQL dans les secrets."
            )
