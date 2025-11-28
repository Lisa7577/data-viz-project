# 🚀 Quick Start Guide - Marketing Analytics Dashboard

## ⚡ Lancement Rapide (2 minutes)

### 1️⃣ Vérification des Prérequis
```bash
# Vérifier Python (3.9+ requis)
python --version

# Installer les dépendances
pip install -r requirements.txt
```

### 2️⃣ Lancement de l'Application
```bash
# Option recommandée - Script automatique
./run_app.sh

# OU manuel
streamlit run app/app.py
```

### 3️⃣ Accès à l'Interface
- **URL**: http://localhost:8501
- **Navigation**: 5 onglets dans la sidebar
- **Premier démarrage**: ~10 secondes de chargement

## 📊 Tour des Fonctionnalités (5 minutes)

### 🏠 Vue d'ensemble
- **KPIs principaux** en haut de page
- **Graphiques temporels** pour les tendances  
- **Répartition géographique** des revenus
- **Filtres** dans la sidebar à gauche

### 👥 Analyse des Cohortes
- **Heatmap de rétention** (couleurs = performance)
- **Sélection des cohortes** à comparer
- **Courbes d'évolution** interactives
- **Export Excel** des données

### 🎯 Segmentation RFM  
- **11 segments clients** avec métriques
- **Matrice de priorisation** (graphique à bulles)
- **Recommandations stratégiques** par segment
- **Visualisations 3D** des segments

### 💰 Scénarios CLV
- **Sliders d'amélioration** (rétention, fréquence, montant)
- **Calcul d'impact** en temps réel
- **Comparaison avant/après** 
- **Scénarios prédéfinis** (boutons rapides)

### 📤 Export de Données
- **Sélection multi-datasets**
- **3 formats**: Excel, CSV, JSON
- **Rapport exécutif** automatique
- **Horodatage** des exports

## 🔧 Résolution Problèmes Courants

### ❌ "Module not found"
```bash
pip install streamlit plotly pandas numpy scikit-learn
```

### ❌ "No data found"
```bash
# Vérifier la présence des fichiers
ls data/processed/
# Doit contenir: online_retail_clean.csv, rfm_metrics.csv, etc.
```

### ❌ "Port already in use" 
```bash
streamlit run app/app.py --server.port 8502
```

### ❌ Cache issues
```bash
# Dans l'app Streamlit: Menu > Clear cache
# OU redémarrer l'application
```

## 📈 Cas d'Usage Rapides

### 🎯 Identifier les Clients VIP
1. Aller dans **Segmentation RFM**
2. Sélectionner segment **"Champions"**
3. Noter le nombre et la CLV moyenne
4. Exporter la liste via **Export de Données**

### 📊 Analyser la Rétention
1. Aller dans **Analyse des Cohortes**  
2. Regarder la **heatmap** (vert = bonne rétention)
3. Sélectionner les **meilleures cohortes**
4. Comparer leurs **courbes d'évolution**

### 💡 Simuler Impact Marketing
1. Aller dans **Scénarios CLV**
2. Ajuster les **sliders d'amélioration**
3. Cliquer **"Calculer l'Impact"**
4. Noter l'**impact total** en £

### 📋 Créer un Rapport
1. Aller dans **Export de Données**
2. Sélectionner **"KPIs consolidés"** + autres datasets
3. Cliquer **"Générer Rapport Exécutif"**
4. Télécharger le **fichier Markdown**

## 🏆 Tips Pro

### ⚡ Performance
- Utiliser les **filtres de date** pour accélérer les calculs
- **Limiter à 1-2 pays** pour les analyses détaillées
- **Recharger la page** si l'interface devient lente

### 📊 Analyses Avancées  
- **Comparer plusieurs segments** dans la matrice de priorisation
- **Tester différents scénarios** pour le business planning
- **Exporter en Excel** pour analyses complémentaires dans Excel/Power BI

### 🎨 Interface
- **Mode sombre** : Settings > Theme > Dark
- **Sidebar réduite** : Flèche en haut à gauche
- **Plein écran** : F11 sur la plupart des navigateurs

---

**🎉 Vous êtes prêt ! L'application contient 400K+ transactions analysées et 4K+ clients segmentés.**

**📞 Support** : Consultez le README.md pour la documentation complète.
