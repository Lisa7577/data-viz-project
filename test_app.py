"""
Test script to verify the Streamlit application works correctly
"""

import sys
import os
sys.path.append('/Users/bambafall/Documents/0.ECE/Ing5/introduction_to_ML/env/bin/Data_Viz_Project/Projet_Data_Viz/app')

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        import pandas as pd
        print("✅ Pandas imported successfully")
        
        import plotly.express as px
        print("✅ Plotly imported successfully")
        
        import utils
        print("✅ Utils module imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_loading():
    """Test that processed data can be loaded"""
    try:
        from utils import load_processed_data
        data = load_processed_data()
        
        if data is not None:
            print(f"✅ Data loaded successfully")
            print(f"   - Clean data shape: {data['clean_data'].shape}")
            print(f"   - RFM data shape: {data['rfm_data'].shape}")
            return True
        else:
            print("❌ Data loading returned None")
            return False
            
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False

def test_utility_functions():
    """Test that key utility functions work"""
    try:
        from utils import calculate_kpis, get_rfm_segments, get_cohort_table
        
        # Load test data
        from utils import load_processed_data
        data = load_processed_data()
        
        if data is None:
            print("❌ Cannot test utilities - no data")
            return False
        
        # Test KPIs calculation
        kpis = calculate_kpis(data['clean_data'])
        print(f"✅ KPIs calculated: {len(kpis)} metrics")
        
        # Test RFM segmentation
        rfm_segments = get_rfm_segments(data['rfm_data'])
        print(f"✅ RFM segmentation: {len(rfm_segments)} customers segmented")
        
        # Test cohort analysis
        cohort_table = get_cohort_table(data['clean_data'])
        print(f"✅ Cohort analysis: {cohort_table.shape[0]} cohorts identified")
        
        return True
        
    except Exception as e:
        print(f"❌ Utility function error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Marketing Analytics Application")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test imports
    print("\n1️⃣ Testing Imports...")
    if not test_imports():
        all_tests_passed = False
    
    # Test data loading
    print("\n2️⃣ Testing Data Loading...")
    if not test_data_loading():
        all_tests_passed = False
    
    # Test utility functions
    print("\n3️⃣ Testing Utility Functions...")
    if not test_utility_functions():
        all_tests_passed = False
    
    # Final result
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Application is ready to run.")
        print("\n🚀 To launch the dashboard, run:")
        print("   cd /Users/bambafall/Documents/0.ECE/Ing5/introduction_to_ML/env/bin/Data_Viz_Project/Projet_Data_Viz")
        print("   streamlit run app/app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
