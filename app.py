import streamlit as st
import xml.etree.ElementTree as ET

def read_file(uploaded_file):
    """Lit le fichier avec gestion des encodages"""
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252']
    for encoding in encodings:
        try:
            uploaded_file.seek(0)
            return uploaded_file.read().decode(encoding)
        except:
            continue
    return None

def transform_xml(xml_content):
    """Transforme MODELE en CYCLE et détecte BH - SANS NAMESPACES"""
    try:
        alerts = []
        
        # Transformation par remplacement de texte simple
        result = xml_content
        
        # Chercher et remplacer name="MODELE" par name="CYCLE"
        import re
        pattern = r'name="MODELE"'
        if re.search(pattern, result):
            result = re.sub(pattern, 'name="CYCLE"', result)
            alerts.append("Transformation: MODELE changé en CYCLE")
        
        # Détecter les valeurs BH
        bh_pattern = r'<[^>]*IdValue[^>]*>BH</[^>]*IdValue>'
        if re.search(bh_pattern, result):
            alerts.append("ALERTE: Valeur BH détectée")
        
        return result, alerts
    except Exception as e:
        return None, [f"Erreur: {str(e)}"]

st.title("Processeur XML - MODELE vers CYCLE")

# Description de l'application
st.markdown("""
## Description de l'application

Cette application transforme vos fichiers XML en effectuant automatiquement :

**1. Transformation principale :**
- Change tous les attributs `name="MODELE"` en `name="CYCLE"`
- Exemple : `<IdValue name="MODELE">BH</IdValue>` devient `<IdValue name="CYCLE">BH</IdValue>`

**2. Détection d'alertes :**
- Identifie automatiquement les valeurs "BH" (valeurs par défaut de l'ERP)
- Affiche une alerte pour chaque valeur "BH" détectée

**3. Instructions d'utilisation :**
- Chargez votre fichier XML avec le bouton ci-dessous
- Ou collez directement votre contenu XML dans la zone de texte
- Téléchargez le fichier corrigé une fois le traitement terminé

---
""")

# Upload de fichier
uploaded_file = st.file_uploader("Chargez votre fichier XML", type=['xml'])

xml_content = None
transformed_xml = None

if uploaded_file:
    xml_content = read_file(uploaded_file)
    if xml_content:
        st.success("Fichier chargé")
        transformed_xml, alerts = transform_xml(xml_content)
        
        for alert in alerts:
            st.warning(alert)
        
        if transformed_xml:
            st.success("Transformation réussie")

# Zone de texte comme alternative
if not xml_content:
    xml_manual = st.text_area("Ou collez votre XML ici:", height=200)
    if xml_manual.strip():
        xml_content = xml_manual
        transformed_xml, alerts = transform_xml(xml_content)
        
        for alert in alerts:
            st.warning(alert)
        
        if transformed_xml:
            st.success("Transformation réussie")

# BOUTON DE TÉLÉCHARGEMENT - Toujours présent
st.markdown("---")

if transformed_xml:
    st.download_button(
        label="TÉLÉCHARGER LE FICHIER XML CORRIGÉ",
        data=transformed_xml,
        file_name="fichier_corrige.xml",
        mime="application/xml",
        key="download_btn"
    )
else:
    st.info("Chargez un fichier XML pour activer le téléchargement")

# Aperçu du résultat
if transformed_xml:
    with st.expander("Aperçu du XML corrigé"):
        st.code(transformed_xml, language='xml')
