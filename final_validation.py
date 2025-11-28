#!/usr/bin/env python3
"""
🎯 VALIDATION FINALE - Application Marketing Analytics Dashboard
=============================================================

Script de validation finale pour vérifier que l'application est prête
à être déployée et utilisée.

"""

import sys
import os
from pathlib import Path
import pandas as pd
import importlib.util

def test_file_structure():
    """Vérifier la structure des fichiers"""
    print("📁 Vérification de la structure des fichiers...")
    
    required_files = [
        "app/app.py",
        "app/utils.py",
        "data/processed/online_retail_clean.csv",
        "data/processed/rfm_metrics.csv",
        "data/processed/customer_stats.csv",
        "data/processed/customer_cohorts.csv",
        "requirements.txt",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            size = Path(file_path).stat().st_size / (1024*1024)  # MB
            print(f"   ✅ {file_path} ({size:.1f} MB)")
    
    if missing_files:
        print(f"   ❌ Fichiers manquants: {missing_files}")
        return False
    
    return True

def test_data_integrity():
    """Vérifier l'intégrité des données"""
    print("\n📊 Vérification de l'intégrité des données...")
    
    try:
        # Charger les données principales
        df = pd.read_csv("data/processed/online_retail_clean.csv")
        rfm = pd.read_csv("data/processed/rfm_metrics.csv")
        stats = pd.read_csv("data/processed/customer_stats.csv")
        cohorts = pd.read_csv("data/processed/customer_cohorts.csv")
        
        print(f"   ✅ Transactions: {len(df):,} lignes")
        print(f"   ✅ Métriques RFM: {len(rfm):,} clients")
        print(f"   ✅ Statistiques clients: {len(stats):,} clients")
        print(f"   ✅ Cohortes: {len(cohorts):,} clients")
        
        # Vérifier les colonnes essentielles
        required_cols = {
            'df': ['InvoiceDate', 'Customer ID', 'TotalAmount', 'Country'],
            'rfm': ['Customer ID', 'Recency', 'Frequency', 'Monetary'],
            'stats': ['Customer ID', 'Total_Spending', 'Order_Count'],
            'cohorts': ['Customer ID', 'CohortMonth']
        }
        
        for data_name, cols in required_cols.items():
            data = locals()[data_name]
            missing_cols = [col for col in cols if col not in data.columns]
            if missing_cols:
                print(f"   ❌ Colonnes manquantes dans {data_name}: {missing_cols}")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur de chargement des données: {e}")
        return False

def test_imports():
    """Tester les imports de l'application"""
    print("\n🔧 Test des imports de l'application...")
    
    try:
        # Ajouter le répertoire app au path
        sys.path.insert(0, str(Path.cwd() / "app"))
        
        # Tester l'import de utils
        spec = importlib.util.spec_from_file_location("utils", "app/utils.py")
        utils_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(utils_module)
        print("   ✅ Module utils importé avec succès")
        
        # Tester quelques fonctions clés
        functions_to_test = [
            'load_processed_data',
            'calculate_kpis',
            'get_rfm_segments',
            'get_cohort_table'
        ]
        
        for func_name in functions_to_test:
            if hasattr(utils_module, func_name):
                print(f"   ✅ Fonction {func_name} disponible")
            else:
                print(f"   ❌ Fonction {func_name} manquante")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur d'import: {e}")
        return False

def test_streamlit_compatibility():
    """Tester la compatibilité Streamlit"""
    print("\n🌐 Test de compatibilité Streamlit...")
    
    try:
        import streamlit as st
        import plotly.express as px
        import plotly.graph_objects as go
        print("   ✅ Streamlit et Plotly disponibles")
        return True
    except ImportError as e:
        print(f"   ❌ Dépendance manquante: {e}")
        return False

def main():
    """Fonction principale de validation"""
    print("🎯 VALIDATION FINALE - Marketing Analytics Dashboard")
    print("=" * 55)
    
    tests = [
        ("Structure des fichiers", test_file_structure),
        ("Intégrité des données", test_data_integrity),
        ("Imports de l'application", test_imports),
        ("Compatibilité Streamlit", test_streamlit_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Erreur dans {test_name}: {e}")
            results.append(False)
    
    print("\n" + "=" * 55)
    print("📊 RÉSULTATS DE LA VALIDATION")
    print("=" * 55)
    
    success_count = sum(results)
    total_count = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ RÉUSSI" if results[i] else "❌ ÉCHOUÉ"
        print(f"{test_name:.<30} {status}")
    
    print(f"\nScore global: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        print("\n🎉 APPLICATION PRÊTE POUR LE DÉPLOIEMENT!")
        print("Pour lancer l'application:")
        print("  • Méthode 1: streamlit run app/app.py")
        print("  • Méthode 2: ./run_app.sh")
        print("  • Méthode 3: chmod +x run_app.sh && ./run_app.sh")
        return True
    else:
        print("\n⚠️  Des problèmes ont été détectés. Veuillez les corriger avant le déploiement.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
