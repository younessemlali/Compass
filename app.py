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
    """Transforme MODELE en CYCLE et détecte BH"""
    try:
        # Parser le XML
        root = ET.fromstring(xml_content)
        alerts = []
        
        # Chercher TOUTES les balises IdValue
        for elem in root.iter('IdValue'):
            name_attr = elem.get('name')
            if name_attr == 'MODELE':
                # Alerte si valeur BH
                if elem.text and elem.text.strip() == 'BH':
                    alerts.append("ALERTE: Valeur BH détectée")
                
                # Changer l'attribut name de MODELE vers CYCLE
                elem.set('name', 'CYCLE')
        
        # Retourner le XML transformé
        transformed = ET.tostring(root, encoding='unicode', method='xml')
        return transformed, alerts
    except Exception as e:
        return None, [f"Erreur XML: {str(e)}"]

st.title("Processeur XML - MODELE vers CYCLE")

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
