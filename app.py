import streamlit as st
import xml.etree.ElementTree as ET
import re

def safe_read_file(uploaded_file):
    """Lit un fichier avec gestion des encodages"""
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'cp1252']
    
    for encoding in encodings:
        try:
            uploaded_file.seek(0)
            content = uploaded_file.read().decode(encoding)
            return content, encoding
        except:
            continue
    
    # Dernier recours
    uploaded_file.seek(0)
    content = uploaded_file.read().decode('utf-8', errors='ignore')
    return content, 'utf-8-ignore'

def process_xml(xml_content, new_value=None):
    """Transforme le XML MODELE -> CYCLE"""
    alerts = []
    
    try:
        root = ET.fromstring(xml_content)
        
        for elem in root.iter('IdValue'):
            if elem.get('name') == 'MODELE':
                current_val = elem.text
                
                # Alerte si BH détecté
                if current_val == 'BH':
                    alerts.append("⚠️ Valeur BH détectée !")
                    
                    # Remplacer si nouvelle valeur fournie
                    if new_value:
                        elem.text = new_value
                        alerts.append(f"✅ BH remplacé par {new_value}")
                
                # Transformation MODELE -> CYCLE
                elem.set('name', 'CYCLE')
        
        return ET.tostring(root, encoding='unicode'), alerts
    
    except Exception as e:
        st.error(f"Erreur XML: {e}")
        return None, []

def validate_value(value):
    """Valide une valeur alphanumérique"""
    if not value:
        return False, "Vide"
    if not re.match(r'^[A-Za-z0-9]+$', value):
        return False, "Doit être alphanumérique"
    return True, "OK"

# Interface principale
st.title("🔄 XML Processor - MODELE → CYCLE")

col1, col2 = st.columns(2)

with col1:
    st.header("📤 Import")
    
    # Upload fichier
    uploaded = st.file_uploader("Fichier XML", type=['xml'])
    
    # Saisie manuelle
    st.subheader("Ou saisie manuelle")
    manual = st.text_area("XML:", height=150, 
        value="""<StaffingShift>
<Id><IdValue name="MODELE">BH</IdValue></Id>
</StaffingShift>""")
    
    # Valeur de remplacement
    st.subheader("Remplacement BH")
    replacement = st.text_input("Nouvelle valeur:", placeholder="CYC001")
    
    if replacement:
        valid, msg = validate_value(replacement)
        if valid:
            st.success(f"✅ {msg}")
        else:
            st.error(f"❌ {msg}")
            replacement = None

with col2:
    st.header("📥 Résultat")
    
    xml_content = None
    
    # Lire le fichier
    if uploaded:
        content, encoding = safe_read_file(uploaded)
        xml_content = content
        st.success(f"✅ Fichier lu ({encoding})")
    elif manual.strip():
        xml_content = manual
        st.success("✅ XML manuel")
    
    # Traiter
    if xml_content:
        result, alerts = process_xml(xml_content, replacement)
        
        if result:
            # Afficher alertes
            for alert in alerts:
                if alert.startswith("⚠️"):
                    st.warning(alert)
                else:
                    st.info(alert)
            
            # Afficher résultat
            st.subheader("XML transformé")
            st.code(result, language='xml')
            
            # Téléchargement
            st.download_button(
                "📥 Télécharger",
                data=result,
                file_name="xml_modifie.xml",
                mime="application/xml"
            )

# Section test
st.markdown("---")
st.header("🧪 Test validateur")

test_val = st.text_input("Tester une valeur:", placeholder="CYC001")
if st.button("Valider"):
    if test_val:
        valid, msg = validate_value(test_val)
        if valid:
            st.success(f"✅ {msg}")
        else:
            st.error(f"❌ {msg}")

st.markdown("---")
st.info("🔧 App XML Processor - MODELE → CYCLE")
