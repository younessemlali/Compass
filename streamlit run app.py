import streamlit as st
import xml.etree.ElementTree as ET
from io import StringIO
import re

def process_xml_content(xml_content):
    """
    Traite le contenu XML pour remplacer MODELE par CYCLE et détecter les valeurs BH
    """
    alerts = []
    
    try:
        # Parser le XML
        root = ET.fromstring(xml_content)
        
        # Rechercher toutes les balises IdValue avec name="MODELE"
        for idvalue in root.iter('IdValue'):
            if idvalue.get('name') == 'MODELE':
                current_value = idvalue.text
                
                # Vérifier si la valeur est "BH" (valeur par défaut)
                if current_value == 'BH':
                    alerts.append(f"⚠️ Valeur par défaut 'BH' détectée dans IdValue name='MODELE'")
                
                # Changer l'attribut name de "MODELE" à "CYCLE"
                idvalue.set('name', 'CYCLE')
        
        # Convertir l'arbre XML modifié en string
        modified_xml = ET.tostring(root, encoding='unicode')
        
        return modified_xml, alerts
        
    except ET.ParseError as e:
        st.error(f"Erreur de parsing XML : {e}")
        return None, []

def validate_cycle_value(value):
    """
    Valide que la valeur saisie est alphanumérique
    """
    if not value:
        return False, "La valeur ne peut pas être vide"
    
    if not re.match(r'^[A-Za-z0-9]+$', value):
        return False, "La valeur doit être alphanumérique (lettres et chiffres uniquement)"
    
    return True, "Valeur valide"

def main():
    st.set_page_config(
        page_title="Processeur XML - MODELE vers CYCLE",
        page_icon="🔄",
        layout="wide"
    )
    
    st.title("🔄 Processeur XML - Transformation MODELE → CYCLE")
    st.markdown("---")
    
    # Sidebar pour les instructions
    with st.sidebar:
        st.header("📋 Instructions")
        st.markdown("""
        **Cette application permet de :**
        1. Charger un fichier XML
        2. Transformer automatiquement `name="MODELE"` en `name="CYCLE"`
        3. Détecter les valeurs par défaut "BH" 
        4. Valider les nouvelles valeurs saisies
        5. Télécharger le fichier modifié
        """)
        
        st.header("⚠️ Alertes")
        st.markdown("""
        - **BH** : Valeur par défaut générée par l'ERP
        - Les agences doivent saisir une valeur **alphanumérique**
        - Lettres et chiffres autorisés uniquement
        """)
    
    # Interface principale
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Import du fichier XML")
        
        # Option 1: Upload de fichier
        uploaded_file = st.file_uploader(
            "Choisir un fichier XML", 
            type=['xml'],
            help="Sélectionnez votre fichier XML à traiter"
        )
        
        # Option 2: Saisie manuelle
        st.subheader("Ou saisie manuelle du XML")
        manual_xml = st.text_area(
            "Collez votre contenu XML ici",
            height=200,
            placeholder="""<StaffingShift shiftPeriod="weekly">
<Id idOwner="EXT0">
<IdValue name="MODELE">BH</IdValue>
</Id>
<Name>Base horaire hebdomadaire</Name>
<Hours>36.30</Hours>
<StartTime>08:30:00</StartTime>
</StaffingShift>"""
        )
    
    with col2:
        st.header("📥 Résultat du traitement")
        
        xml_content = None
        
        # Récupérer le contenu XML
        if uploaded_file is not None:
            xml_content = uploaded_file.read().decode('utf-8')
            st.success("✅ Fichier chargé avec succès")
        elif manual_xml.strip():
            xml_content = manual_xml
            st.success("✅ XML saisi manuellement")
        
        # Traiter le XML si disponible
        if xml_content:
            modified_xml, alerts = process_xml_content(xml_content)
            
            if modified_xml:
                # Afficher les alertes
                if alerts:
                    st.error("🚨 **ALERTES DÉTECTÉES**")
                    for alert in alerts:
                        st.warning(alert)
                    
                    st.markdown("---")
                    st.info("💡 **Action requise :** Remplacez les valeurs 'BH' par des valeurs alphanumériques appropriées")
                else:
                    st.success("✅ Aucune valeur par défaut 'BH' détectée")
                
                # Afficher le XML modifié
                st.subheader("XML transformé")
                st.code(modified_xml, language='xml')
                
                # Bouton de téléchargement
                st.download_button(
                    label="📥 Télécharger le XML modifié",
                    data=modified_xml,
                    file_name="xml_modifie.xml",
                    mime="application/xml"
                )
    
    # Section pour tester les valeurs CYCLE
    st.markdown("---")
    st.header("🧪 Validateur de valeurs CYCLE")
    
    col3, col4 = st.columns([1, 1])
    
    with col3:
        test_value = st.text_input(
            "Testez une valeur CYCLE",
            placeholder="Ex: CYC001, HEBDO1, etc.",
            help="Saisissez une valeur pour vérifier si elle est valide"
        )
        
        if st.button("Valider la valeur"):
            if test_value:
                is_valid, message = validate_cycle_value(test_value)
                if is_valid:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
    
    with col4:
        st.subheader("Exemples de valeurs valides")
        st.markdown("""
        - `CYC001`
        - `HEBDO1` 
        - `CYCLE2024`
        - `H36`
        - `TEMP123`
        """)
        
        st.subheader("Exemples de valeurs invalides")
        st.markdown("""
        - `CYC-001` (tiret non autorisé)
        - `CYCLE 1` (espace non autorisé)
        - `CYC_001` (underscore non autorisé)
        - `CYCLÉ` (accent non autorisé)
        """)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        🔧 Application de traitement XML - Transformation MODELE → CYCLE
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
