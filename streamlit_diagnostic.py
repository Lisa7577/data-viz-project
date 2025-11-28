#!/usr/bin/env python3
"""
🔧 Diagnostic Streamlit - Résolution des Problèmes
================================================

Script de diagnostic pour identifier et résoudre les problèmes Streamlit
"""

import sys
import os
import traceback
from pathlib import Path

# Ajouter le répertoire app au chemin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_data_loading():
    """Test spécifique du chargement des données"""
    print("🔍 Test du chargement des données...")
    try:
        from utils import load_processed_data
        data = load_processed_data()
        
        if data is None:
            print("❌ Problème: load_processed_data() retourne None")
            return False
        
        # Vérifier la structure des données
        required_keys = ['clean_data', 'rfm_data', 'customer_stats', 'cohorts_data']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            print(f"❌ Clés manquantes dans les données: {missing_keys}")
            return False
        
        # Vérifier les colonnes essentielles
        df = data['clean_data']
        required_columns = ['Customer ID', 'TotalAmount', 'InvoiceDate', 'Country']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Colonnes manquantes: {missing_columns}")
            print(f"   Colonnes disponibles: {list(df.columns)}")
            return False
        
        print(f"✅ Données chargées: {len(df)} transactions, {df['Customer ID'].nunique()} clients")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement des données: {e}")
        traceback.print_exc()
        return False

def test_streamlit_functions():
    """Test des fonctions Streamlit critiques"""
    print("\n🔍 Test des fonctions Streamlit...")
    try:
        from utils import (
            calculate_kpis, get_rfm_segments, get_cohort_table,
            create_revenue_trend, create_segment_treemap
        )
        
        # Charger les données de test
        from utils import load_processed_data
        data = load_processed_data()
        if data is None:
            print("❌ Impossible de tester - pas de données")
            return False
        
        df_clean = data['clean_data']
        rfm_data = data['rfm_data']
        
        # Test des KPIs
        print("  🧪 Test calculate_kpis...")
        kpis = calculate_kpis(df_clean)
        print(f"     ✅ {len(kpis)} KPIs calculés")
        
        # Test RFM segments
        print("  🧪 Test get_rfm_segments...")
        rfm_segments = get_rfm_segments(rfm_data)
        print(f"     ✅ {len(rfm_segments)} clients segmentés")
        
        # Test cohort table
        print("  🧪 Test get_cohort_table...")
        cohort_table = get_cohort_table(df_clean)
        print(f"     ✅ Tableau de cohortes: {cohort_table.shape}")
        
        # Test visualizations
        print("  🧪 Test create_revenue_trend...")
        fig_revenue = create_revenue_trend(df_clean)
        print(f"     ✅ Graphique de revenus créé")
        
        print("  🧪 Test create_segment_treemap...")
        fig_treemap = create_segment_treemap(rfm_segments)
        print(f"     ✅ Treemap créé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans les fonctions Streamlit: {e}")
        traceback.print_exc()
        return False

def test_streamlit_compatibility():
    """Test de compatibilité Streamlit"""
    print("\n🔍 Test de compatibilité Streamlit...")
    try:
        import streamlit as st
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
        
        print("✅ Imports Streamlit OK")
        
        # Test des fonctions Streamlit de base
        print("  🧪 Test st.cache_data...")
        
        @st.cache_data
        def test_cache():
            return pd.DataFrame({'test': [1, 2, 3]})
        
        df_test = test_cache()
        print("     ✅ Cache Streamlit fonctionne")
        
        # Test Plotly
        print("  🧪 Test Plotly...")
        fig = px.bar(x=[1, 2, 3], y=[4, 5, 6])
        print("     ✅ Plotly fonctionne")
        
        return True
        
    except Exception as e:
        print(f"❌ Problème de compatibilité Streamlit: {e}")
        traceback.print_exc()
        return False

def test_file_paths():
    """Vérifier tous les chemins de fichiers"""
    print("\n🔍 Vérification des chemins de fichiers...")
    
    base_path = Path(__file__).parent
    required_files = [
        'data/processed/online_retail_clean.csv',
        'data/processed/rfm_metrics.csv', 
        'data/processed/customer_stats.csv',
        'data/processed/customer_cohorts.csv',
        'app/app.py',
        'app/utils.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            size = full_path.stat().st_size / (1024*1024)  # MB
            print(f"✅ {file_path} ({size:.1f} MB)")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - MANQUANT")
    
    if missing_files:
        print(f"\n⚠️ Fichiers manquants: {missing_files}")
        return False
    
    return True

def generate_fix_suggestions(results):
    """Génère des suggestions de correction"""
    print("\n" + "="*50)
    print("🔧 SUGGESTIONS DE CORRECTION")
    print("="*50)
    
    if not results['files']:
        print("❌ PROBLÈME CRITIQUE: Fichiers de données manquants")
        print("   💡 Solution:")
        print("   1. Exécuter le notebook 01_exploration.ipynb")
        print("   2. Vérifier que les exports se font dans data/processed/")
        print("   3. Ou re-télécharger les données depuis UCI")
        
    if not results['data']:
        print("❌ PROBLÈME: Chargement des données")
        print("   💡 Solutions possibles:")
        print("   1. Vérifier les noms de colonnes dans les CSV")
        print("   2. Contrôler l'encoding des fichiers (UTF-8)")
        print("   3. Vérifier les chemins relatifs dans utils.py")
        
    if not results['functions']:
        print("❌ PROBLÈME: Fonctions utilitaires")
        print("   💡 Solutions possibles:")
        print("   1. Vérifier les noms de colonnes utilisés")
        print("   2. Contrôler les types de données")
        print("   3. Ajouter des vérifications de nullité")
        
    if not results['streamlit']:
        print("❌ PROBLÈME: Compatibilité Streamlit") 
        print("   💡 Solutions possibles:")
        print("   1. Mettre à jour Streamlit: pip install --upgrade streamlit")
        print("   2. Vérifier la version Python (3.9+)")
        print("   3. Réinstaller les dépendances: pip install -r requirements.txt")
    
    if all(results.values()):
        print("🎉 AUCUN PROBLÈME DÉTECTÉ!")
        print("   L'application devrait fonctionner correctement.")
        print("   Pour lancer: streamlit run app/app.py")

def main():
    """Fonction principale de diagnostic"""
    print("🔧 DIAGNOSTIC STREAMLIT - RÉSOLUTION DES PROBLÈMES")
    print("=" * 55)
    
    results = {
        'files': test_file_paths(),
        'data': test_data_loading(), 
        'functions': test_streamlit_functions(),
        'streamlit': test_streamlit_compatibility()
    }
    
    generate_fix_suggestions(results)
    
    # Résumé final
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n📊 RÉSUMÉ: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🚀 L'application est PRÊTE pour le lancement!")
        return True
    else:
        print("⚠️ Corrections nécessaires avant le lancement.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
