# -*- coding: utf-8 -*-
"""
Fonctions utilitaires pour l'application Streamlit
Projet d'Aide à la Décision Marketing - Online Retail II
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta
import base64
from io import BytesIO
import os

# ==================== CHARGEMENT DES DONNÉES ====================

@st.cache_data
def load_data():
    """Charge toutes les données nécessaires à l'application"""
    try:
        # Chemins des fichiers (depuis le dossier app/)
        base_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
        
        # Dataset principal nettoyé
        df_path = os.path.join(base_path, 'online_retail_clean.csv')
        df = pd.read_csv(df_path)
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        
        # Métriques RFM
        rfm_path = os.path.join(base_path, 'rfm_metrics.csv')
        rfm = pd.read_csv(rfm_path, index_col=0)
        
        # Statistiques clients
        stats_path = os.path.join(base_path, 'customer_stats.csv')
        customer_stats = pd.read_csv(stats_path, index_col=0)
        
        # Cohortes
        cohorts_path = os.path.join(base_path, 'customer_cohorts.csv')
        cohorts = pd.read_csv(cohorts_path)
        cohorts['CohortMonth'] = pd.to_datetime(cohorts['CohortMonth'])
        
        return df, rfm, customer_stats, cohorts
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return None, None, None, None

# ==================== FILTRES ET TRANSFORMATION ====================

def apply_filters(df, date_range, countries, customer_types, min_amount):
    """Applique les filtres sélectionnés aux données"""
    df_filtered = df.copy()
    
    # Filtre par date
    if date_range:
        start_date, end_date = date_range
        df_filtered = df_filtered[
            (df_filtered['InvoiceDate'] >= pd.to_datetime(start_date)) &
            (df_filtered['InvoiceDate'] <= pd.to_datetime(end_date))
        ]
    
    # Filtre par pays
    if countries:
        df_filtered = df_filtered[df_filtered['Country'].isin(countries)]
    
    # Filtre par montant minimum
    if min_amount > 0:
        df_filtered = df_filtered[df_filtered['TotalAmount'] >= min_amount]
    
    return df_filtered

# ==================== ANALYSES COHORTES ====================

def calculate_cohort_table(df):
    """Calcule la table de rétention des cohortes"""
    # Créer les cohortes par mois d'acquisition
    df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M')
    
    # Première transaction par client
    cohort_data = df.groupby('Customer ID')['InvoiceDate'].min().reset_index()
    cohort_data.columns = ['Customer ID', 'CohortMonth']
    cohort_data['CohortMonth'] = cohort_data['CohortMonth'].dt.to_period('M')
    
    # Joindre avec les données principales
    df_cohort = df.merge(cohort_data, on='Customer ID')
    df_cohort['CohortAge'] = (df_cohort['InvoiceMonth'] - df_cohort['CohortMonth']).apply(lambda x: x.n)
    
    # Table de rétention
    cohort_table = df_cohort.groupby(['CohortMonth', 'CohortAge'])['Customer ID'].nunique().reset_index()
    cohort_table = cohort_table.pivot(index='CohortMonth', columns='CohortAge', values='Customer ID')
    
    # Taille des cohortes
    cohort_sizes = cohort_data.groupby('CohortMonth').size()
    
    # Taux de rétention
    retention_table = cohort_table.divide(cohort_sizes, axis=0)
    
    return cohort_table, retention_table, cohort_sizes

def create_cohort_heatmap(retention_table, show_values=True, is_percentage=True):
    """Crée une heatmap de rétention des cohortes"""
    # Titre dynamique selon le type de données
    title = "📈 Heatmap de Rétention par Cohorte" if is_percentage else "📊 Heatmap du Nombre de Clients par Cohorte"
    
    fig = px.imshow(
        retention_table.values,
        x=[f"M+{i}" for i in retention_table.columns],
        y=[str(idx) for idx in retention_table.index],
        color_continuous_scale='RdYlBu_r',
        aspect="auto",
        title=title
    )
    
    fig.update_layout(
        xaxis_title="Âge de la Cohorte",
        yaxis_title="Mois d'Acquisition",
        height=600
    )
    
    # Ajouter les valeurs dans les cellules si demandé
    if show_values:
        for i, row in enumerate(retention_table.values):
            for j, val in enumerate(row):
                if not pd.isna(val):
                    if is_percentage:
                        text = f"{val:.1%}"
                    else:
                        text = f"{int(val):,}" if val >= 1 else f"{val:.1f}"
                    
                    fig.add_annotation(
                        x=j, y=i,
                        text=text,
                        showarrow=False,
                        font=dict(color="white" if val < (0.5 if is_percentage else retention_table.values.max()/2) else "black")
                    )
    
    return fig

# ==================== SEGMENTATION RFM ====================

def create_rfm_segments(rfm):
    """Crée les segments RFM avec scoring"""
    rfm_seg = rfm.copy()
    
    # Scoring RFM (1-5)
    rfm_seg['R_Score'] = pd.qcut(rfm_seg['Recency'].rank(method='first'), 5, labels=[5,4,3,2,1])
    rfm_seg['F_Score'] = pd.qcut(rfm_seg['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
    rfm_seg['M_Score'] = pd.qcut(rfm_seg['Monetary'].rank(method='first'), 5, labels=[1,2,3,4,5])
    
    # Score RFM combiné
    rfm_seg['RFM_Score'] = rfm_seg['R_Score'].astype(str) + rfm_seg['F_Score'].astype(str) + rfm_seg['M_Score'].astype(str)
    
    # Segmentation détaillée
    segment_map = {
        r'[4-5][4-5][4-5]': 'Champions',
        r'[3-5][2-4][3-5]': 'Loyal Customers',
        r'[4-5][1-2][1-3]': 'Potential Loyalists',
        r'[4-5][1-2][4-5]': 'New Customers',
        r'[3-4][3-4][3-4]': 'Promising',
        r'[2-3][2-3][2-3]': 'Need Attention',
        r'[2-3][1-2][4-5]': 'About to Sleep',
        r'[1-2][4-5][4-5]': 'At Risk',
        r'[1-2][4-5][1-3]': 'Cannot Lose Them',
        r'[1-2][1-2][4-5]': 'Hibernating',
        r'[1-2][1-2][1-2]': 'Lost'
    }
    
    rfm_seg['Segment'] = 'Others'
    for pattern, segment in segment_map.items():
        mask = rfm_seg['RFM_Score'].str.match(pattern)
        rfm_seg.loc[mask, 'Segment'] = segment
    
    return rfm_seg

def create_rfm_visualization(rfm_seg):
    """Crée les visualisations RFM"""
    # Distribution des segments
    segment_dist = rfm_seg['Segment'].value_counts()
    
    fig1 = px.bar(
        x=segment_dist.index,
        y=segment_dist.values,
        title="📊 Distribution des Segments RFM",
        labels={'x': 'Segment', 'y': 'Nombre de clients'}
    )
    fig1.update_layout(xaxis_tickangle=-45)
    
    # Scatter RFM
    fig2 = px.scatter_3d(
        rfm_seg,
        x='Recency',
        y='Frequency',
        z='Monetary',
        color='Segment',
        title="🎯 Visualisation 3D des Segments RFM",
        hover_data=['RFM_Score']
    )
    
    return fig1, fig2

# ==================== CALCUL CLV ====================

def calculate_empirical_clv(df, cohorts):
    """Calcule la CLV empirique basée sur les cohortes"""
    # Joindre avec les cohortes
    df_clv = df.merge(cohorts[['Customer ID', 'CohortMonth']], on='Customer ID')
    df_clv['CohortMonth'] = pd.to_datetime(df_clv['CohortMonth'])
    df_clv['InvoiceMonth'] = df_clv['InvoiceDate'].dt.to_period('M')
    df_clv['CohortAge'] = (df_clv['InvoiceMonth'] - df_clv['CohortMonth'].dt.to_period('M')).apply(lambda x: x.n)
    
    # CLV par âge de cohorte
    clv_by_age = df_clv.groupby(['Customer ID', 'CohortAge'])['TotalAmount'].sum().reset_index()
    clv_empirical = clv_by_age.groupby('Customer ID')['TotalAmount'].sum()
    
    return clv_empirical

def calculate_parametric_clv(rfm, retention_rate=0.75, discount_rate=0.1, margin_rate=0.2):
    """Calcule la CLV paramétrique avec formule fermée"""
    # CLV = (Monetary * margin_rate * retention_rate) / (1 + discount_rate - retention_rate)
    clv_parametric = (rfm['Monetary'] * margin_rate * retention_rate) / (1 + discount_rate - retention_rate)
    return clv_parametric

def simulate_scenarios(rfm, base_retention=0.75, base_margin=0.2, base_discount=0.1):
    """Simule différents scénarios business"""
    scenarios = {
        'Baseline': calculate_parametric_clv(rfm, base_retention, base_discount, base_margin),
        '+5% Rétention': calculate_parametric_clv(rfm, base_retention + 0.05, base_discount, base_margin),
        '-10% Marge': calculate_parametric_clv(rfm, base_retention, base_discount, base_margin - 0.02),
        '+5% Rétention & -10% Marge': calculate_parametric_clv(rfm, base_retention + 0.05, base_discount, base_margin - 0.02)
    }
    
    return scenarios

# ==================== VISUALISATIONS ====================

def create_kpi_cards(df, rfm):
    """Crée les KPI cards pour le dashboard"""
    total_customers = df['Customer ID'].nunique()
    total_revenue = df['TotalAmount'].sum()
    avg_order_value = df['TotalAmount'].mean()
    avg_clv = rfm['Monetary'].mean()
    
    return {
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'avg_clv': avg_clv
    }

def create_revenue_evolution(df):
    """Crée le graphique d'évolution du CA"""
    daily_revenue = df.groupby(df['InvoiceDate'].dt.date)['TotalAmount'].sum()
    
    fig = px.line(
        x=daily_revenue.index,
        y=daily_revenue.values,
        title="💰 Évolution du Chiffre d'Affaires",
        labels={'x': 'Date', 'y': 'CA (£)'}
    )
    
    return fig

# ==================== EXPORT ====================

def create_export_data(df, rfm_seg, selected_segments=None):
    """Prépare les données pour export"""
    # S'assurer que la colonne Segment existe
    if 'Segment' not in rfm_seg.columns:
        rfm_seg = create_rfm_segments(rfm_seg)
    
    if selected_segments:
        export_customers = rfm_seg[rfm_seg['Segment'].isin(selected_segments)]
    else:
        export_customers = rfm_seg
    
    # Enrichir avec informations client
    customer_summary = df.groupby('Customer ID').agg({
        'InvoiceDate': ['min', 'max', 'count'],
        'TotalAmount': ['sum', 'mean'],
        'Country': 'first'
    }).round(2)
    
    customer_summary.columns = ['First_Purchase', 'Last_Purchase', 'Order_Count', 'Total_Spent', 'Avg_Order_Value', 'Country']
    
    # Joindre avec RFM
    export_data = export_customers.merge(customer_summary, left_index=True, right_index=True)
    
    return export_data

def create_download_link(df, filename, text="Télécharger CSV"):
    """Crée un lien de téléchargement pour un DataFrame"""
    csv = df.to_csv(index=True)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# ==================== AIDE ET DÉFINITIONS ====================

def show_definitions():
    """Affiche les définitions des métriques"""
    definitions = {
        "CLV (Customer Lifetime Value)": "Valeur totale qu'un client apporte sur toute sa relation avec l'entreprise",
        "Rétention à t": "Pourcentage de clients d'une cohorte encore actifs au mois t",
        "RFM Score": "Score basé sur Recency (récence), Frequency (fréquence), Monetary (valeur monétaire)",
        "Cohorte": "Groupe de clients acquis dans la même période (mois)",
        "CPA (Cost Per Acquisition)": "Coût d'acquisition d'un nouveau client",
        "Panier moyen": "Montant moyen dépensé par transaction",
        "Taux d'actualisation": "Taux utilisé pour actualiser les flux futurs en valeur présente"
    }
    
    return definitions

# ==================== MÉTRIQUES AVANCÉES ====================

def calculate_cohort_revenue_curves(df, cohorts):
    """Calcule les courbes de revenus par âge de cohorte"""
    df_cohort = df.merge(cohorts[['Customer ID', 'CohortMonth']], on='Customer ID')
    df_cohort['CohortMonth'] = pd.to_datetime(df_cohort['CohortMonth'])
    df_cohort['InvoiceMonth'] = df_cohort['InvoiceDate'].dt.to_period('M')
    df_cohort['CohortAge'] = (df_cohort['InvoiceMonth'] - df_cohort['CohortMonth'].dt.to_period('M')).apply(lambda x: x.n)
    
    # Revenus cumulés par âge de cohorte
    revenue_by_age = df_cohort.groupby(['CohortMonth', 'CohortAge'])['TotalAmount'].sum().reset_index()
    revenue_cumsum = revenue_by_age.groupby('CohortMonth')['TotalAmount'].cumsum()
    revenue_by_age['Cumulative_Revenue'] = revenue_cumsum
    
    return revenue_by_age

def get_segment_priorities():
    """Définit les priorités d'activation par segment RFM"""
    priorities = {
        'Champions': {'priority': 1, 'action': 'Récompenser', 'color': '#2E8B57'},
        'Loyal Customers': {'priority': 2, 'action': 'Upsell', 'color': '#4169E1'},
        'Potential Loyalists': {'priority': 3, 'action': 'Offres membres', 'color': '#32CD32'},
        'New Customers': {'priority': 4, 'action': 'Onboarding', 'color': '#FFD700'},
        'Promising': {'priority': 5, 'action': 'Offres gratuites', 'color': '#FF6347'},
        'Need Attention': {'priority': 6, 'action': 'Offres limitées', 'color': '#FF4500'},
        'About to Sleep': {'priority': 7, 'action': 'Recommandations', 'color': '#B22222'},
        'At Risk': {'priority': 8, 'action': 'Réactivation', 'color': '#8B0000'},
        'Cannot Lose Them': {'priority': 9, 'action': 'Reconquête', 'color': '#800080'},
        'Hibernating': {'priority': 10, 'action': 'Autres produits', 'color': '#4B0082'},
        'Lost': {'priority': 11, 'action': 'Ignorer', 'color': '#2F4F4F'}
    }
    
    return priorities

# ==================== FONCTIONS COMPLÉMENTAIRES POUR STREAMLIT ====================

@st.cache_data
def load_processed_data():
    """Charge toutes les données processées avec mise en cache - Alias pour load_data()"""
    df, rfm, customer_stats, cohorts = load_data()
    if df is not None:
        return {
            'clean_data': df,
            'rfm_data': rfm,
            'customer_stats': customer_stats,
            'cohorts_data': cohorts
        }
    return None

def get_cohort_table(df):
    """Alias pour calculate_cohort_table() - retourne seulement le tableau des cohortes"""
    cohort_table, _, _ = calculate_cohort_table(df)
    return cohort_table

def get_retention_rates(cohort_table):
    """Calcule les taux de rétention à partir du tableau des cohortes"""
    return cohort_table.divide(cohort_table.iloc[:, 0], axis=0) * 100

def create_retention_curve(retention_rates, selected_cohorts):
    """Crée une courbe de rétention pour les cohortes sélectionnées"""
    fig = go.Figure()
    
    for cohort in selected_cohorts:
        if cohort in retention_rates.index:
            y_data = retention_rates.loc[cohort].dropna()
            x_data = list(range(len(y_data)))
            
            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                mode='lines+markers',
                name=f'Cohorte {cohort}',
                line=dict(width=3),
                marker=dict(size=8)
            ))
    
    fig.update_layout(
        title="Courbes de Rétention par Cohorte",
        xaxis_title="Période (mois)",
        yaxis_title="Taux de rétention (%)",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def get_rfm_segments(rfm_data):
    """Alias pour create_rfm_segments() - s'assure que la colonne Segment existe"""
    rfm_with_segments = create_rfm_segments(rfm_data)
    return rfm_with_segments

def create_rfm_scatter(rfm_segments):
    """Crée un scatter plot 3D des segments RFM"""
    # S'assurer que la colonne Segment existe
    if 'Segment' not in rfm_segments.columns:
        rfm_segments = create_rfm_segments(rfm_segments)
    
    fig = px.scatter_3d(
        rfm_segments, 
        x='Recency', 
        y='Frequency', 
        z='Monetary',
        color='Segment',
        title="Visualisation 3D des Segments RFM",
        labels={
            'Recency': 'Récence (jours)',
            'Frequency': 'Fréquence',
            'Monetary': 'Valeur monétaire (£)'
        },
        height=500
    )
    
    fig.update_layout(
        scene=dict(
            xaxis_title="Récence (jours)",
            yaxis_title="Fréquence",
            zaxis_title="Valeur monétaire (£)"
        )
    )
    
    return fig

def create_segment_treemap(rfm_segments):
    """Crée un treemap des segments RFM"""
    # S'assurer que la colonne Segment existe
    if 'Segment' not in rfm_segments.columns:
        rfm_segments = create_rfm_segments(rfm_segments)
    
    segment_summary = rfm_segments.groupby('Segment').agg({
        'Recency': 'count',  # Utiliser Recency au lieu de CustomerID pour compter
        'Monetary': 'sum'
    }).reset_index()
    
    segment_summary.columns = ['Segment', 'Nombre_Clients', 'CA_Total']
    
    fig = px.treemap(
        segment_summary,
        path=['Segment'],
        values='Nombre_Clients',
        color='CA_Total',
        title="Répartition des Segments RFM",
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=400)
    return fig

def calculate_clv_empirical(df):
    """Calcule la CLV empirique - Utilise les vraies données de cohortes"""
    # Charger les données de cohortes
    _, _, _, cohorts = load_data()
    if cohorts is not None:
        return calculate_empirical_clv(df, cohorts)
    else:
        # Fallback: calculer la CLV simple par client
        return df.groupby('Customer ID')['TotalAmount'].sum()

def calculate_clv_parametric(rfm_data):
    """Alias pour calculate_parametric_clv()"""
    return calculate_parametric_clv(rfm_data)

def simulate_scenario(df, retention_change=0, frequency_change=0, monetary_change=0):
    """Simule un scénario d'amélioration des métriques"""
    # Calcul CLV de base
    base_clv = df.groupby('Customer ID')['TotalAmount'].sum()
    
    # Application des changements
    retention_factor = 1 + retention_change
    frequency_factor = 1 + frequency_change
    monetary_factor = 1 + monetary_change
    
    # Nouvelle CLV simulée
    new_clv = base_clv * retention_factor * frequency_factor * monetary_factor
    
    return {
        'new_clv': new_clv,
        'improvement': new_clv - base_clv
    }

def calculate_kpis(df):
    """Calcule les KPIs principaux"""
    total_revenue = df['TotalAmount'].sum()
    total_customers = df['Customer ID'].nunique()
    avg_order_value = df['TotalAmount'].mean()
    aov_std = df['TotalAmount'].std()
    
    # CLV moyenne
    customer_totals = df.groupby('Customer ID')['TotalAmount'].sum()
    avg_clv = customer_totals.mean()
    max_clv = customer_totals.max()
    
    # Croissance (simulée pour l'exemple)
    growth_rate = 12.5  # Placeholder
    new_customers = int(total_customers * 0.15)  # Placeholder
    
    return {
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'avg_order_value': avg_order_value,
        'aov_std': aov_std,
        'avg_clv': avg_clv,
        'max_clv': max_clv,
        'growth_rate': growth_rate,
        'new_customers': new_customers
    }

def filter_data_by_date(df, start_date, end_date):
    """Filtre les données par plage de dates"""
    df_filtered = df.copy()
    df_filtered['InvoiceDate'] = pd.to_datetime(df_filtered['InvoiceDate'])
    
    mask = (df_filtered['InvoiceDate'].dt.date >= start_date) & (df_filtered['InvoiceDate'].dt.date <= end_date)
    return df_filtered.loc[mask]

def create_revenue_trend(df):
    """Crée un graphique de l'évolution du chiffre d'affaires"""
    df_copy = df.copy()
    df_copy['InvoiceDate'] = pd.to_datetime(df_copy['InvoiceDate'])
    df_copy['YearMonth'] = df_copy['InvoiceDate'].dt.to_period('M')
    
    monthly_revenue = df_copy.groupby('YearMonth')['TotalAmount'].sum().reset_index()
    monthly_revenue['YearMonth'] = monthly_revenue['YearMonth'].astype(str)
    
    fig = px.line(
        monthly_revenue,
        x='YearMonth',
        y='TotalAmount',
        title="Évolution Mensuelle du Chiffre d'Affaires",
        labels={'TotalAmount': 'Chiffre d\'Affaires (£)', 'YearMonth': 'Mois'}
    )
    
    fig.update_layout(height=400)
    return fig