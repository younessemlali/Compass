import streamlit as st
import xml.etree.ElementTree as ET

def process_xml(xml_text):
    """Transforme MODELE en CYCLE et détecte BH"""
    try:
        root = ET.fromstring(xml_text)
        alerts = []
        
        for elem in root.iter('IdValue'):
            if elem.get('name') == 'MODELE':
                # Alerte si BH
                if elem.text == 'BH':
                    alerts.append("ALERTE: Valeur BH détectée")
                
                # Changer MODELE en CYCLE
                elem.set('name', 'CYCLE')
        
        result = ET.tostring(root, encoding='unicode')
        return result, alerts
    except:
        return None, ["Erreur XML"]

st.title("XML Processor - MODELE vers CYCLE")

# Zone de saisie
xml_input = st.text_area("Collez votre XML ici:", height=300, value="""<StaffingShift>
<Id><IdValue name="MODELE">BH</IdValue></Id>
</StaffingShift>""")

# Traitement
if xml_input.strip():
    result_xml, alerts = process_xml(xml_input)
    
    # Alertes
    for alert in alerts:
        st.warning(alert)
    
    if result_xml:
        st.success("XML transformé avec succès")
        
        # BOUTON DE TÉLÉCHARGEMENT
        st.download_button(
            "TÉLÉCHARGER XML CORRIGÉ", 
            result_xml,
            "xml_corrige.xml",
            "application/xml"
        )
        
        # Aperçu (optionnel)
        with st.expander("Voir le XML corrigé"):
            st.code(result_xml, language='xml')
    else:
        st.error("Erreur dans le XML")
