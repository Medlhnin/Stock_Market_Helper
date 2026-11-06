import streamlit as st
import math

st.set_page_config(page_title="Simulateur Trading", layout="centered")

st.title("📈 Simulateur de Trading")

# Constantes
frais_achat = 0.0099
frais_vente = 0.01
taxe = 0.15  # TPCVM

tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Trading (objectif)",
    "💰 Gain actuel",
    "📈 Compound interest ",
    "⏳ Calcul du temps t"
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
