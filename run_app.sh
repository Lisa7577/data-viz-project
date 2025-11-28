#!/bin/bash

# 📊 Script de lancement de l'application Marketing Analytics Dashboard
# ================================================================

echo "🚀 Lancement de l'application Marketing Analytics Dashboard"
echo "=================================================="

# Vérifier si nous sommes dans le bon répertoire
if [ ! -f "app/app.py" ]; then
    echo "❌ Erreur: Veuillez exécuter ce script depuis le répertoire racine du projet"
    echo "   Répertoire attendu: Projet_Data_Viz/"
    exit 1
fi

# Vérifier la présence des données
if [ ! -f "data/processed/online_retail_clean.csv" ]; then
    echo "❌ Erreur: Fichiers de données manquants dans data/processed/"
    echo "   Assurez-vous d'avoir exécuté le notebook d'exploration en premier"
    exit 1
fi

echo "✅ Vérifications réussies"
echo ""

echo "📊 Démarrage de Streamlit..."
echo "💡 L'application sera accessible sur: http://localhost:8501"
echo ""
echo "🔧 Pour arrêter l'application, utilisez Ctrl+C"
echo "=================================================="
echo ""

# Lancer Streamlit
streamlit run app/app.py --server.port 8501 --server.address localhost
