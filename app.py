import streamlit as st
import xml.etree.ElementTree as ET
import re

def read_uploaded_file(uploaded_file):
    """Lit un fichier uploadé avec gestion des encodages"""
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'cp1252']
    
    for encoding in encodings:
        try:
            uploaded_file.seek(0)
            content = uploaded_file.read().decode(encoding)
            return content, encoding, None
        except UnicodeDecodeError:
            continue
        except Exception as e:
            continue
    
    # Dernier recours
    try:
        uploaded_file.seek(0)
        content = uploaded_file.read().decode('utf-8', errors='ignore')
        return content, 'utf-8 (erreurs ignorées)', "Certains caractères ont pu être perdus"
    except Exception as e:
        return None, None, f"Erreur: {str(e)}"

def process_xml_transformation(xml_content, replacement_value=None):
    """
    Transforme le XML:
    1. Change name="MODELE" vers name="CYCLE"
    2. Détecte les valeurs BH
    3. Remplace BH si une nouvelle valeur est fournie
    """
    alerts = []
    transformations = []
    
    try:
        root = ET.fromstring(xml_content)
        
        # Rechercher toutes les balises IdValue avec name="MODELE"
        for idvalue_elem in root.iter('IdValue'):
            if idvalue_elem.get('name') == 'MODELE':
                current_value = idvalue_elem.text if idvalue_elem.text else ""
                
                # Alerte si valeur BH détectée
                if current_value == 'BH':
                    alerts.append("Valeur par défaut 'BH' détectée")
                    
                    # Remplacer BH si nouvelle valeur fournie
                    if replacement_value and replacement_value.strip():
                        idvalue_elem.text = replacement_value.strip()
                        transformations.append(f"Valeur 'BH' remplacée par '{replacement_value.strip()}'")
                
                # Transformation principale: MODELE -> CYCLE
                idvalue_elem.set('name', 'CYCLE')
                transformations.append("Attribut 'MODELE' transformé en 'CYCLE'")
        
        # Convertir le XML modifié en string
        result_xml = ET.tostring(root, encoding='unicode')
        return result_xml, alerts, transformations, None
        
    except ET.ParseError as e:
        return None, [], [], f"Erreur de parsing XML: {str(e)}"
    except Exception as e:
        return None, [], [], f"Erreur inattendue: {str(e)}"

def validate_replacement_value(value):
    """Valide qu'une valeur est alphanumérique"""
    if not value:
        return False, "La valeur ne peut pas être vide"
    
    if not re.match(r'^[A-Za-z0-9]+$', value):
        return False, "La valeur doit contenir uniquement des lettres et des chiffres"
    
    return True, "Valeur valide"

def main():
    # Configuration de la page
    st.set_page_config(
        page_title="XML Processor",
        page_icon="🔄",
        layout="wide"
    )
    
    # Titre principal
    st.title("🔄 Processeur XML - Transformation MODELE → CYCLE")
    st.markdown("---")
    
    # Interface en deux colonnes
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Import du fichier XML")
        
        # Upload de fichier
        uploaded_file = st.file_uploader(
            "Sélectionnez votre fichier XML",
            type=['xml'],
            help="Choisissez un fichier XML à traiter"
        )
        
        # Zone de saisie manuelle
        st.subheader("Ou saisie manuelle")
        manual_xml = st.text_area(
            "Collez votre XML ici:",
            height=200,
            placeholder='''<StaffingShift shiftPeriod="weekly">
    <Id idOwner="EXT0">
        <IdValue name="MODELE">BH</IdValue>
    </Id>
    <Name>Base horaire hebdomadaire</Name>
    <Hours>36.30</Hours>
    <StartTime>08:30:00</StartTime>
</StaffingShift>'''
        )
        
        # Option de remplacement des valeurs BH
        st.subheader("💡 Remplacement des valeurs BH")
        replacement_value = st.text_input(
            "Nouvelle valeur pour remplacer 'BH':",
            placeholder="Exemple: CYC001, HEBDO1, etc.",
            help="Laissez vide pour garder les valeurs BH (seule l'alerte sera affichée)"
        )
        
        # Validation de la valeur de remplacement
        if replacement_value:
            is_valid, validation_message = validate_replacement_value(replacement_value)
            if is_valid:
                st.success(f"✅ {validation_message}")
            else:
                st.error(f"❌ {validation_message}")
                replacement_value = None  # Invalider la valeur
    
    with col2:
        st.header("📥 Résultat du traitement")
        
        xml_content = None
        
        # Traiter le fichier uploadé
        if uploaded_file is not None:
            content, encoding, warning = read_uploaded_file(uploaded_file)
            
            if content is not None:
                xml_content = content
                st.success(f"✅ Fichier chargé avec succès (encodage: {encoding})")
                if warning:
                    st.warning(f"⚠️ {warning}")
            else:
                st.error("❌ Impossible de lire le fichier")
        
        # Traiter la saisie manuelle
        elif manual_xml.strip():
            xml_content = manual_xml
            st.success("✅ XML saisi manuellement")
        
        # Effectuer la transformation si du contenu XML est disponible
        result_xml = None
        if xml_content:
            result_xml, alerts, transformations, error = process_xml_transformation(
                xml_content, 
                replacement_value
            )
            
            if error:
                st.error(f"❌ {error}")
            elif result_xml:
                # Afficher les alertes
                if alerts:
                    st.error("🚨 ALERTES DÉTECTÉES")
                    for alert in alerts:
                        st.warning(f"⚠️ {alert}")
                
                # Afficher les transformations effectuées
                if transformations:
                    st.success("✅ TRANSFORMATIONS EFFECTUÉES")
                    for transformation in transformations:
                        st.info(f"🔄 {transformation}")
                
                # Afficher le XML transformé
                st.subheader("XML transformé")
                st.code(result_xml, language='xml')
        
        # Bouton de téléchargement - TOUJOURS PRÉSENT
        download_data = result_xml if result_xml else "<!-- Aucun XML traité -->"
        st.download_button(
            label="📥 Télécharger le XML modifié",
            data=download_data,
            file_name="xml_transforme.xml",
            mime="application/xml",
            disabled=(result_xml is None),
            help="Traitez d'abord un fichier XML pour activer le téléchargement"
        )
    
    # Section de test des valeurs
    st.markdown("---")
    st.header("🧪 Testeur de valeurs")
    
    col3, col4 = st.columns([1, 1])
    
    with col3:
        test_value = st.text_input(
            "Testez une valeur:",
            placeholder="Exemple: CYC001",
            help="Vérifiez si une valeur est valide pour remplacer 'BH'"
        )
        
        if st.button("Valider"):
            if test_value:
                is_valid, message = validate_replacement_value(test_value)
                if is_valid:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Saisissez une valeur à tester")
    
    with col4:
        st.subheader("Exemples valides")
        st.code("""CYC001
HEBDO1
CYCLE2024
H36
TEMP123""")
        
        st.subheader("Exemples invalides")
        st.code("""CYC-001  (tiret)
CYCLE 1  (espace)
CYC_001  (underscore)
CYCLÉ    (accent)""")

if __name__ == "__main__":
    main()
