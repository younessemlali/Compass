# 🔄 Processeur XML - Transformation MODELE → CYCLE

Application Streamlit pour traiter les fichiers XML et transformer automatiquement les balises `name="MODELE"` en `name="CYCLE"` avec détection des valeurs par défaut.

## 🎯 Fonctionnalités

- **Transformation automatique** : Change `name="MODELE"` en `name="CYCLE"`
- **Détection d'alertes** : Identifie les valeurs par défaut "BH" 
- **Validation** : Vérifie que les valeurs sont alphanumériques
- **Import flexible** : Upload de fichier ou saisie manuelle
- **Export** : Téléchargement du XML modifié

## 🚀 Installation et utilisation

### Installation locale

1. Clonez le repository :
```bash
git clone https://github.com/votre-username/xml-processor-app.git
cd xml-processor-app
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancez l'application :
```bash
streamlit run app.py
```

### Déploiement sur Streamlit Cloud

1. Forkez ce repository
2. Connectez-vous sur [share.streamlit.io](https://share.streamlit.io)
3. Déployez directement depuis GitHub

## 📋 Structure du projet

```
xml-processor-app/
├── app.py              # Application principale
├── requirements.txt    # Dépendances Python
├── README.md          # Documentation
└── .streamlit/        # Configuration Streamlit (optionnel)
    └── config.toml
```

## 🔧 Utilisation

1. **Import** : Chargez votre fichier XML ou collez le contenu
2. **Traitement** : L'application transforme automatiquement les balises
3. **Alertes** : Vérifiez les alertes pour les valeurs "BH" détectées
4. **Validation** : Testez vos nouvelles valeurs CYCLE
5. **Export** : Téléchargez le fichier XML modifié

## ⚠️ Règles de validation

### Valeurs acceptées pour CYCLE
- **Alphanumériques uniquement** : lettres (A-Z, a-z) et chiffres (0-9)
- **Pas d'espaces** ni de caractères spéciaux
- **Exemples valides** : `CYC001`, `HEBDO1`, `CYCLE2024`

### Valeurs à éviter
- `BH` : Valeur par défaut de l'ERP (génère une alerte)
- Caractères spéciaux : `-`, `_`, espaces, accents

## 📊 Exemple de transformation

**Avant :**
```xml
<IdValue name="MODELE">BH</IdValue>
```

**Après :**
```xml
<IdValue name="CYCLE">VOTRE_VALEUR</IdValue>
```

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📝 License

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.

## 📞 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.
