import streamlit as st
import re
import os

st.set_page_config(
    page_title="Compass Group — Correcteur XML",
    page_icon="🔧",
    layout="wide"
)

# ============================================================
# LOGIQUE DE CORRECTION
# ============================================================

def corriger_xml_compass(contenu_bytes):
    contenu = contenu_bytes.decode("iso-8859-1")
    warnings = []
    corrections = []

    # Étape 1 : supprimer les blocs StaffingShift parasites (tout sauf weekly)
    pattern_bloc_parasite = re.compile(
        r'[ \t]*<StaffingShift\s+shiftPeriod="(?!weekly)[^"]*">.*?</StaffingShift>\r?\n?',
        re.DOTALL
    )
    blocs_supprimes = pattern_bloc_parasite.findall(contenu)
    if blocs_supprimes:
        corrections.append(f"🗑️ {len(blocs_supprimes)} bloc(s) StaffingShift parasite(s) supprimé(s)")
    contenu = pattern_bloc_parasite.sub("", contenu)

    # Étape 2 : supprimer balises superflues dans les blocs weekly
    balises_supprimees = []
    for balise in ["Name", "n", "Hours", "StartTime", "Comment"]:
        pattern = re.compile(
            r'[ \t]*<' + balise + r'(\s[^>]*)?>.*?</' + balise + r'>\r?\n?',
            re.DOTALL
        )
        matches = pattern.findall(contenu)
        if matches:
            balises_supprimees.append(f"<{balise}>")
        contenu = pattern.sub("", contenu)
    if balises_supprimees:
        corrections.append(f"🧹 Balises superflues supprimées : {', '.join(balises_supprimees)}")

    # Étape 3 : détecter les IdValue invalides
    pattern_contrats = re.compile(
        r'<ContractId[^>]*>\s*<IdValue>([^<]+)</IdValue>\s*</ContractId>'
    )
    contrat_ids = pattern_contrats.findall(contenu)

    pattern_idvalue = re.compile(
        r'<StaffingShift shiftPeriod="weekly">.*?<IdValue[^>]*>([^<]+)</IdValue>',
        re.DOTALL
    )
    idvalues = pattern_idvalue.findall(contenu)

    for i, val in enumerate(idvalues):
        val = val.strip()
        if not re.match(r'^\d{6}$', val):
            contrat_ref = contrat_ids[i] if i < len(contrat_ids) else f"contrat #{i+1}"
            warnings.append(
                f"Contrat **{contrat_ref}** : `IdValue = '{val}'` — code horaire invalide "
                f"(doit être numérique à 6 chiffres). ⚠️ Correction manuelle requise."
            )

    return contenu.encode("iso-8859-1"), corrections, warnings


def extraire_staffingshifts(contenu_str):
    """Extrait les blocs StaffingShift pour comparaison."""
    pattern = re.compile(
        r'<StaffingShift[^>]*>.*?</StaffingShift>',
        re.DOTALL
    )
    return pattern.findall(contenu_str)


def compter_contrats(contenu_str):
    return len(re.findall(r'<ContractId', contenu_str))


# ============================================================
# INTERFACE
# ============================================================

st.title("🔧 Compass Group — Correcteur XML Pixid")
st.markdown("Correction automatique des balises `StaffingShift` pour intégration ADP.")

st.divider()

# Upload
uploaded_file = st.file_uploader(
    "📂 Charger un fichier XML Compass",
    type=["xml"],
    help="Fichier contrat XML généré par Osmose/Pixid"
)

if uploaded_file:
    contenu_original = uploaded_file.read()
    nom_fichier = uploaded_file.name
    contenu_original_str = contenu_original.decode("iso-8859-1")

    nb_contrats = compter_contrats(contenu_original_str)
    blocs_avant = extraire_staffingshifts(contenu_original_str)

    st.success(f"✅ Fichier chargé : `{nom_fichier}` — **{nb_contrats} contrat(s)** détecté(s)")

    st.divider()

    # --------------------------------------------------------
    # ANALYSE AVANT CORRECTION
    # --------------------------------------------------------
    st.header("🔍 Analyse du fichier original")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Contrats dans le fichier", nb_contrats)
    with col2:
        nb_parasites = len(re.findall(r'<StaffingShift\s+shiftPeriod="(?!weekly)[^"]*">', contenu_original_str))
        st.metric("Blocs StaffingShift parasites", nb_parasites,
                  delta=f"-{nb_parasites} à supprimer" if nb_parasites > 0 else None,
                  delta_color="inverse")
    with col3:
        nb_balises = sum(
            len(re.findall(r'<' + b + r'(\s[^>]*)?>.*?</' + b + r'>', contenu_original_str, re.DOTALL))
            for b in ["Name", "n", "Hours", "StartTime", "Comment"]
        )
        st.metric("Balises superflues", nb_balises,
                  delta=f"-{nb_balises} à supprimer" if nb_balises > 0 else None,
                  delta_color="inverse")

    if blocs_avant:
        with st.expander(f"📄 StaffingShift détectés AVANT correction ({len(blocs_avant)} blocs)", expanded=False):
            for i, bloc in enumerate(blocs_avant):
                st.code(bloc.strip(), language="xml")

    st.divider()

    # --------------------------------------------------------
    # APERÇU DES CORRECTIONS À APPLIQUER
    # --------------------------------------------------------
    st.header("🔄 Aperçu des corrections")

    if nb_parasites == 0 and nb_balises == 0:
        st.info("ℹ️ Aucune correction automatique nécessaire. Le fichier semble déjà conforme.")
    else:
        data_avant = []
        data_apres = []

        if nb_parasites > 0:
            data_avant.append(f"❌ {nb_parasites} bloc(s) `StaffingShift` avec `shiftPeriod != weekly`")
            data_apres.append(f"✅ Supprimés")

        if nb_balises > 0:
            data_avant.append(f"❌ {nb_balises} balise(s) superflue(s) (`Name`, `Hours`, `StartTime`...)")
            data_apres.append(f"✅ Supprimées")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ❌ Avant")
            for item in data_avant:
                st.markdown(f"- {item}")
        with col2:
            st.markdown("### ✅ Après")
            for item in data_apres:
                st.markdown(f"- {item}")

    st.divider()

    # --------------------------------------------------------
    # BOUTON CORRECTION
    # --------------------------------------------------------
    st.header("⚡ Correction automatique")

    if st.button("🔧 Appliquer les corrections", type="primary", use_container_width=True):
        with st.spinner("Correction en cours..."):
            contenu_corrige, corrections, warnings = corriger_xml_compass(contenu_original)
            contenu_corrige_str = contenu_corrige.decode("iso-8859-1")
            blocs_apres = extraire_staffingshifts(contenu_corrige_str)

        st.success("✅ Corrections appliquées avec succès !")

        # Résumé
        if corrections:
            st.markdown("**Corrections effectuées :**")
            for c in corrections:
                st.markdown(f"- {c}")

        # Avertissements manuels
        if warnings:
            st.warning("⚠️ Corrections manuelles requises :")
            for w in warnings:
                st.markdown(f"- {w}")

        st.divider()

        # Comparaison avant/après blocs StaffingShift
        st.subheader("📊 Comparaison StaffingShift avant / après")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**❌ Avant — {len(blocs_avant)} bloc(s)**")
            for bloc in blocs_avant:
                st.code(bloc.strip(), language="xml")

        with col2:
            st.markdown(f"**✅ Après — {len(blocs_apres)} bloc(s)**")
            if blocs_apres:
                for bloc in blocs_apres:
                    st.code(bloc.strip(), language="xml")
            else:
                st.info("Aucun bloc StaffingShift restant.")

        st.divider()

        # Téléchargement
        base, ext = os.path.splitext(nom_fichier)
        nom_corrige = base + "_CORRIGE" + ext

        st.download_button(
            label="📥 Télécharger le XML corrigé",
            data=contenu_corrige,
            file_name=nom_corrige,
            mime="application/xml",
            type="primary",
            use_container_width=True
        )
        st.info(f"💾 Fichier : `{nom_corrige}`")
        st.warning("⚠️ Vérifiez les avertissements ci-dessus avant d'envoyer à Pixid.")

else:
    st.info("👆 Chargez un fichier XML pour commencer.")

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
    Compass Group Corrector v1.0 | Randstad France — Intégration Pixid
</div>
""", unsafe_allow_html=True)
