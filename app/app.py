"""
📊 Application Streamlit - Aide à la Décision Marketing
=====================================================

Application interactive pour l'analyse des cohortes, segmentation RFM, 
et calcul de la valeur vie client (CLV) basée sur le dataset Online Retail II.

Auteur: Assistant IA
Date: 2024
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import warnings
from pathlib import Path
from io import BytesIO

# Imports locaux
from utils import (
    load_processed_data, get_cohort_table, get_retention_rates,
    create_cohort_heatmap, create_retention_curve, get_rfm_segments,
    create_rfm_scatter, calculate_clv_empirical, calculate_clv_parametric,
    simulate_scenario, create_segment_treemap, calculate_kpis,
    filter_data_by_date, create_revenue_trend, apply_filters,
    create_rfm_visualization, create_kpi_cards
)

# Configuration
warnings.filterwarnings('ignore')
st.set_page_config(
    page_title="🛒 Marketing Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_all_data():
    """Charge toutes les données processées avec mise en cache"""
    try:
        data = load_processed_data()
        return data
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return None

def show_kpi_definitions():
    """Affiche les définitions des KPIs dans un expander"""
    with st.expander("📚 Définitions des KPIs", expanded=False):
        st.markdown("""
        **📊 KPIs Principaux:**
        - **Chiffre d'Affaires Total**: Somme de toutes les transactions sur la période
        - **Nombre de Clients**: Clients uniques ayant effectué au moins un achat
        - **Panier Moyen**: Montant moyen par transaction
        - **CLV Moyenne**: Customer Lifetime Value moyenne (valeur vie client)
        
        **🔄 Métriques de Rétention:**
        - **Taux de Rétention**: % de clients qui reviennent acheter
        - **Fréquence d'Achat**: Nombre moyen de commandes par client
        - **Récence Moyenne**: Nombre de jours depuis le dernier achat
        
        **🎯 Segmentation RFM:**
        - **R (Recency)**: Depuis quand le client n'a pas acheté
        - **F (Frequency)**: Fréquence d'achat du client
        - **M (Monetary)**: Montant total dépensé par le client
        """)

def render_sidebar():
    """Interface de la barre latérale avec filtres"""
    st.sidebar.markdown("## 🎛️ Filtres & Navigation")
    
    # Sélection de la vue
    view = st.sidebar.selectbox(
        "📊 Sélectionnez une vue:",
        ["🏠 Vue d'ensemble", "👥 Analyse des Cohortes", "🎯 Segmentation RFM", 
         "💰 Scénarios CLV", "📤 Export des Données"],
        help="Choisissez la vue analytique que vous souhaitez explorer"
    )
    
    st.sidebar.markdown("---")
    
    # Filtres temporels
    st.sidebar.markdown("### 📅 Période d'Analyse")
    
    # Chargement des données pour les filtres
    data = load_all_data()
    if data is None:
        return view, None, None, None, None
    
    df_clean = data['clean_data']
    min_date = pd.to_datetime(df_clean['InvoiceDate']).min().date()
    max_date = pd.to_datetime(df_clean['InvoiceDate']).max().date()
    
    date_range = st.sidebar.date_input(
        "Plage de dates:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Sélectionnez la période d'analyse"
    )
    
    # Filtres géographiques
    countries = sorted(df_clean['Country'].unique())
    selected_countries = st.sidebar.multiselect(
        "🌍 Pays:",
        countries,
        default=['United Kingdom'],
        help="Sélectionnez les pays à analyser"
    )
    
    # Filtres par type de client
    customer_types = st.sidebar.radio(
        "👤 Type de clients:",
        ["Tous", "Retail uniquement", "Wholesale uniquement"],
        help="Filtrez par type de clientèle"
    )
    
    # Seuils personnalisés
    st.sidebar.markdown("### ⚙️ Paramètres Avancés")
    min_clv = st.sidebar.number_input(
        "CLV minimum (£):", 
        min_value=0, 
        value=0, 
        step=50,
        help="Valeur vie client minimale pour l'analyse"
    )
    
    return view, date_range, selected_countries, customer_types, min_clv

def overview_view(data):
    """Vue d'ensemble avec KPIs principaux et tendances"""
    st.markdown('<h1 class="main-header">🏠 Vue d\'ensemble - Marketing Analytics</h1>', 
                unsafe_allow_html=True)
    
    df_clean = data['clean_data']
    rfm_data = data['rfm_data']
    
    # Calcul des KPIs
    kpis = calculate_kpis(df_clean)
    
    # Affichage des KPIs en colonnes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Chiffre d'Affaires",
            value=f"£{kpis['total_revenue']:,.0f}",
            delta=f"+{kpis['growth_rate']:.1f}%",
            help="Chiffre d'affaires total sur la période"
        )
    
    with col2:
        st.metric(
            label="👥 Nombre de Clients",
            value=f"{kpis['total_customers']:,}",
            delta=f"{kpis['new_customers']} nouveaux",
            help="Nombre total de clients uniques"
        )
    
    with col3:
        st.metric(
            label="🛒 Panier Moyen",
            value=f"£{kpis['avg_order_value']:.0f}",
            delta=f"±{kpis['aov_std']:.0f}",
            help="Montant moyen par commande"
        )
    
    with col4:
        st.metric(
            label="💎 CLV Moyenne",
            value=f"£{kpis['avg_clv']:,.0f}",
            delta=f"Max: £{kpis['max_clv']:,.0f}",
            help="Customer Lifetime Value moyenne"
        )
    
    # Graphiques de tendances
    st.markdown("## 📈 Tendances Temporelles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Évolution du CA mensuel
        fig_revenue = create_revenue_trend(df_clean)
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        # Distribution des segments RFM
        fig_segments = create_segment_treemap(rfm_data)
        st.plotly_chart(fig_segments, use_container_width=True)
    
    # Analyses géographiques et par produit
    st.markdown("## 🌍 Répartition Géographique")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 des pays par CA
        country_revenue = df_clean.groupby('Country')['TotalAmount'].sum().sort_values(ascending=False).head(10)
        fig_geo = px.bar(
            x=country_revenue.values,
            y=country_revenue.index,
            orientation='h',
            title="Top 10 Pays par Chiffre d'Affaires",
            labels={'x': 'Chiffre d\'Affaires (£)', 'y': 'Pays'},
            color=country_revenue.values,
            color_continuous_scale='Blues'
        )
        fig_geo.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_geo, use_container_width=True)
    
    with col2:
        # Distribution des montants des commandes
        fig_dist = px.histogram(
            df_clean, 
            x='TotalAmount', 
            nbins=50,
            title="Distribution des Montants de Commandes",
            labels={'TotalAmount': 'Montant (£)', 'count': 'Nombre de commandes'},
            marginal='box'
        )
        fig_dist.update_layout(height=400)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    # Affichage des définitions
    show_kpi_definitions()

def cohorts_view(data):
    """Vue d'analyse des cohortes d'acquisition"""
    st.markdown('<h1 class="main-header">👥 Analyse des Cohortes d\'Acquisition</h1>', 
                unsafe_allow_html=True)
    
    df_clean = data['clean_data']
    
    st.markdown("""
    <div class="info-box">
    <b>💡 Analyse des Cohortes:</b> Suivez l'évolution des groupes de clients selon leur mois d'acquisition. 
    Identifiez les tendances de rétention et optimisez vos stratégies d'acquisition.
    </div>
    """, unsafe_allow_html=True)
    
    # Calcul des cohortes
    with st.spinner("Calcul des cohortes en cours..."):
        cohort_table = get_cohort_table(df_clean)
        retention_rates = get_retention_rates(cohort_table)
    
    # Options d'affichage
    col1, col2 = st.columns([3, 1])
    
    with col2:
        metric_type = st.selectbox(
            "📊 Métrique à afficher:",
            ["Taux de rétention (%)", "Nombre de clients"],
            help="Choisissez entre pourcentages de rétention ou nombres absolus"
        )
        
        show_values = st.checkbox(
            "Afficher les valeurs", 
            value=True,
            help="Affiche les valeurs numériques dans les heatmaps"
        )
    
    with col1:
        if metric_type == "Taux de rétention (%)":
            fig_heatmap = create_cohort_heatmap(retention_rates, show_values=show_values)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            fig_heatmap = create_cohort_heatmap(cohort_table, show_values=show_values, is_percentage=False)
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Courbes de rétention
    st.markdown("## 📉 Courbes de Rétention par Cohorte")
    
    # Sélection des cohortes à comparer
    available_cohorts = retention_rates.index.tolist()
    selected_cohorts = st.multiselect(
        "Sélectionnez les cohortes à comparer:",
        available_cohorts,
        default=available_cohorts[:5] if len(available_cohorts) >= 5 else available_cohorts,
        help="Comparez l'évolution de la rétention entre différentes cohortes"
    )
    
    if selected_cohorts:
        fig_retention = create_retention_curve(retention_rates, selected_cohorts)
        st.plotly_chart(fig_retention, use_container_width=True)
    
    # Statistiques des cohortes
    st.markdown("## 📊 Statistiques Détaillées")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔢 Tailles des Cohortes")
        cohort_sizes = cohort_table.iloc[:, 0].sort_values(ascending=False)
        
        fig_sizes = px.bar(
            x=cohort_sizes.index.astype(str),
            y=cohort_sizes.values,
            title="Nombre de Clients par Cohorte d'Acquisition",
            labels={'x': 'Mois d\'acquisition', 'y': 'Nombre de clients'},
            color=cohort_sizes.values,
            color_continuous_scale='Viridis'
        )
        fig_sizes.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_sizes, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Rétention à 3 mois")
        if len(retention_rates.columns) >= 3:
            retention_3m = retention_rates.iloc[:, 2].dropna().sort_values(ascending=False)
            
            fig_ret3m = px.bar(
                x=retention_3m.index.astype(str),
                y=retention_3m.values,
                title="Taux de Rétention à 3 Mois (%)",
                labels={'x': 'Cohorte d\'acquisition', 'y': 'Taux de rétention (%)'},
                color=retention_3m.values,
                color_continuous_scale='RdYlGn'
            )
            fig_ret3m.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_ret3m, use_container_width=True)
        else:
            st.info("Données insuffisantes pour calculer la rétention à 3 mois")
    
    # Export des données de cohortes
    if st.button("📥 Exporter les données de cohortes"):
        cohort_export = pd.concat([
            cohort_table.round(0).astype(int),
            retention_rates.round(1)
        ], keys=['Nombre_Clients', 'Taux_Retention_%'])
        
        st.download_button(
            label="💾 Télécharger cohorts.xlsx",
            data=cohort_export.to_excel(index=True),
            file_name=f"cohorts_analysis_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def rfm_view(data):
    """Vue de segmentation RFM avec priorisation des segments"""
    st.markdown('<h1 class="main-header">🎯 Segmentation RFM & Priorisation</h1>', 
                unsafe_allow_html=True)
    
    rfm_data = data['rfm_data']
    
    st.markdown("""
    <div class="info-box">
    <b>🎯 Segmentation RFM:</b> Analysez vos clients selon 3 dimensions clés - 
    Récence (quand), Fréquence (combien de fois), et Montant (combien). 
    Identifiez vos segments prioritaires pour optimiser vos actions marketing.
    </div>
    """, unsafe_allow_html=True)
    
    # Calcul des segments RFM
    rfm_segments = get_rfm_segments(rfm_data)
    
    # Métriques des segments
    st.markdown("## 📊 Vue d'ensemble des Segments")
    
    segment_stats = rfm_segments.groupby('Segment').agg({
        'Recency': ['count', 'mean'],  # count pour nombre de clients, mean pour récence moyenne
        'Monetary': ['mean', 'sum'],
        'Frequency': 'mean'
    }).round(2)
    
    segment_stats.columns = ['Nb_Clients', 'Recence_Moy', 'CLV_Moyen', 'CA_Total', 'Freq_Moy']
    segment_stats['Pourcentage'] = (segment_stats['Nb_Clients'] / len(rfm_segments) * 100).round(1)
    
    # Sélection du segment à analyser
    selected_segment = st.selectbox(
        "🎯 Sélectionnez un segment à analyser:",
        options=segment_stats.index.tolist(),
        index=0,
        help="Explorez les détails d'un segment spécifique"
    )
    
    # Affichage des stats du segment sélectionné
    seg_data = segment_stats.loc[selected_segment]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Clients", f"{seg_data['Nb_Clients']:,}", f"{seg_data['Pourcentage']:.1f}%")
    with col2:
        st.metric("💰 CLV Moyen", f"£{seg_data['CLV_Moyen']:,.0f}")
    with col3:
        st.metric("🔄 Fréquence Moy.", f"{seg_data['Freq_Moy']:.1f}")
    with col4:
        st.metric("⏰ Récence Moy.", f"{seg_data['Recence_Moy']:.0f} jours")
    
    # Visualisations RFM
    st.markdown("## 📈 Visualisations des Segments")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Scatter plot RFM
        fig_scatter = create_rfm_scatter(rfm_segments)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        # Treemap des segments
        fig_treemap = create_segment_treemap(rfm_segments)
        st.plotly_chart(fig_treemap, use_container_width=True)
    
    # Matrice de priorisation
    st.markdown("## 🎯 Matrice de Priorisation des Segments")
    
    # Calcul des scores de priorité
    priority_matrix = segment_stats.copy()
    priority_matrix['Score_CLV'] = (priority_matrix['CLV_Moyen'] / priority_matrix['CLV_Moyen'].max() * 100).round(0)
    priority_matrix['Score_Taille'] = (priority_matrix['Nb_Clients'] / priority_matrix['Nb_Clients'].max() * 100).round(0)
    priority_matrix['Score_Priorite'] = (priority_matrix['Score_CLV'] + priority_matrix['Score_Taille']) / 2
    
    # Visualisation de la matrice
    fig_priority = px.scatter(
        priority_matrix.reset_index(),
        x='Score_CLV',
        y='Score_Taille',
        size='CA_Total',
        color='Score_Priorite',
        text='Segment',
        title="Matrice de Priorisation: CLV vs Taille des Segments",
        labels={
            'Score_CLV': 'Score CLV (% du maximum)',
            'Score_Taille': 'Score Taille (% du maximum)',
            'Score_Priorite': 'Score de Priorité'
        },
        color_continuous_scale='RdYlGn'
    )
    
    fig_priority.update_traces(textposition="middle center")
    fig_priority.update_layout(height=500)
    fig_priority.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
    fig_priority.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)
    
    st.plotly_chart(fig_priority, use_container_width=True)
    
    # Recommandations par segment
    st.markdown("## 💡 Recommandations Stratégiques")
    
    recommendations = {
        'Champions': "🏆 **VIP Treatment**: Programmes de fidélité premium, accès privilégié aux nouveautés",
        'Loyal Customers': "💎 **Récompenser la fidélité**: Offres personnalisées, programmes de parrainage",
        'Potential Loyalists': "🚀 **Développer l'engagement**: Campagnes de up-selling, programmes de fidélisation",
        'New Customers': "🌟 **Onboarding optimisé**: Guides d'utilisation, offres de bienvenue",
        'Promising': "📈 **Stimuler la fréquence**: Recommandations produits, notifications personnalisées",
        'Need Attention': "⚠️ **Réactivation proactive**: Enquêtes satisfaction, offres spéciales limitées",
        'About to Sleep': "😴 **Campagnes de réveil**: E-mails de réactivation, remises attractives",
        'At Risk': "🚨 **Rétention d'urgence**: Contacts personnalisés, offres de reconquête",
        'Cannot Lose Them': "🆘 **Sauvetage VIP**: Intervention directe, offres exceptionnelles",
        'Hibernating': "❄️ **Reconquête ciblée**: Campagnes multi-canal, nouveaux produits",
        'Lost': "👋 **Win-back campaigns**: Sondages de départ, offres de retour"
    }
    
    if selected_segment in recommendations:
        st.success(f"**{selected_segment}**: {recommendations[selected_segment]}")
    
    # Table détaillée des segments
    with st.expander("📋 Tableau Détaillé des Segments", expanded=False):
        st.dataframe(priority_matrix.sort_values('Score_Priorite', ascending=False), use_container_width=True)

def scenarios_view(data):
    """Vue de simulation de scénarios CLV"""
    st.markdown('<h1 class="main-header">💰 Simulation de Scénarios CLV</h1>', 
                unsafe_allow_html=True)
    
    df_clean = data['clean_data']
    rfm_data = data['rfm_data']
    
    st.markdown("""
    <div class="info-box">
    <b>💰 Simulation CLV:</b> Modélisez l'impact de vos actions marketing sur la valeur vie client. 
    Testez différents scénarios d'amélioration de la rétention, fréquence et montant moyen.
    </div>
    """, unsafe_allow_html=True)
    
    # Paramètres de simulation
    st.markdown("## ⚙️ Paramètres de Simulation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔄 Rétention")
        retention_improvement = st.slider(
            "Amélioration du taux de rétention:",
            min_value=-20.0,
            max_value=50.0,
            value=0.0,
            step=1.0,
            format="%.1f%%",
            help="Impact sur le taux de rétention client"
        )
        
    with col2:
        st.markdown("### 📊 Fréquence")
        frequency_improvement = st.slider(
            "Amélioration de la fréquence d'achat:",
            min_value=-20.0,
            max_value=50.0,
            value=0.0,
            step=1.0,
            format="%.1f%%",
            help="Impact sur la fréquence d'achat"
        )
        
    with col3:
        st.markdown("### 💵 Montant")
        monetary_improvement = st.slider(
            "Amélioration du panier moyen:",
            min_value=-20.0,
            max_value=50.0,
            value=0.0,
            step=1.0,
            format="%.1f%%",
            help="Impact sur le montant moyen par commande"
        )
    
    # Calcul du scénario
    if st.button("🚀 Calculer l'Impact du Scénario", type="primary"):
        with st.spinner("Simulation en cours..."):
            # CLV actuelle
            current_clv = calculate_clv_empirical(df_clean)
            
            # Simulation du nouveau scénario
            scenario_results = simulate_scenario(
                df_clean, 
                retention_change=retention_improvement/100,
                frequency_change=frequency_improvement/100,
                monetary_change=monetary_improvement/100
            )
            
            # Affichage des résultats
            st.markdown("## 📊 Résultats de la Simulation")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                current_avg = current_clv.mean()
                new_avg = scenario_results['new_clv'].mean()
                improvement = ((new_avg - current_avg) / current_avg) * 100
                
                st.metric(
                    "CLV Moyenne Actuelle",
                    f"£{current_avg:,.0f}",
                    help="Valeur vie client moyenne actuelle"
                )
                
            with col2:
                st.metric(
                    "Nouvelle CLV Moyenne",
                    f"£{new_avg:,.0f}",
                    delta=f"{improvement:+.1f}%",
                    help="Nouvelle valeur vie client avec le scénario"
                )
                
            with col3:
                total_current = current_clv.sum()
                total_new = scenario_results['new_clv'].sum()
                total_improvement = total_new - total_current
                
                st.metric(
                    "Impact Total",
                    f"£{total_improvement:,.0f}",
                    delta=f"{((total_new - total_current) / total_current) * 100:+.1f}%",
                    help="Impact financier total du scénario"
                )
                
            with col4:
                affected_customers = len(scenario_results['new_clv'])
                st.metric(
                    "Clients Impactés",
                    f"{affected_customers:,}",
                    help="Nombre de clients concernés par l'analyse"
                )
            
            # Graphiques de comparaison
            st.markdown("## 📈 Comparaison des Distributions CLV")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribution actuelle vs nouvelle
                fig_comparison = go.Figure()
                
                fig_comparison.add_trace(go.Histogram(
                    x=current_clv,
                    name="CLV Actuelle",
                    opacity=0.7,
                    nbinsx=50,
                    marker_color='lightblue'
                ))
                
                fig_comparison.add_trace(go.Histogram(
                    x=scenario_results['new_clv'],
                    name="CLV Scénario",
                    opacity=0.7,
                    nbinsx=50,
                    marker_color='orange'
                ))
                
                fig_comparison.update_layout(
                    title="Distribution des CLV: Actuelle vs Scénario",
                    xaxis_title="CLV (£)",
                    yaxis_title="Nombre de clients",
                    barmode='overlay',
                    height=400
                )
                
                st.plotly_chart(fig_comparison, use_container_width=True)
                
            with col2:
                # Analyse par segments
                if 'segment_impact' in scenario_results:
                    segment_impact = scenario_results['segment_impact']
                    
                    fig_segments = px.bar(
                        x=segment_impact.index,
                        y=segment_impact.values,
                        title="Impact par Segment RFM",
                        labels={'x': 'Segment', 'y': 'Amélioration CLV (£)'},
                        color=segment_impact.values,
                        color_continuous_scale='RdYlGn'
                    )
                    fig_segments.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_segments, use_container_width=True)
    
    # Scénarios prédéfinis
    st.markdown("## 🎯 Scénarios Prédéfinis")
    
    predefined_scenarios = {
        "🚀 Optimiste": {"retention": 15, "frequency": 10, "monetary": 8},
        "📊 Réaliste": {"retention": 8, "frequency": 5, "monetary": 3},
        "⚠️ Conservateur": {"retention": 3, "frequency": 2, "monetary": 1},
        "🔥 Agressif": {"retention": 25, "frequency": 20, "monetary": 15}
    }
    
    scenario_cols = st.columns(len(predefined_scenarios))
    
    for i, (scenario_name, params) in enumerate(predefined_scenarios.items()):
        with scenario_cols[i]:
            if st.button(f"{scenario_name}", key=f"scenario_{i}"):
                # Appliquer automatiquement les paramètres
                st.session_state['retention_slider'] = params['retention']
                st.session_state['frequency_slider'] = params['frequency'] 
                st.session_state['monetary_slider'] = params['monetary']
                st.rerun()

def export_view(data):
    """Vue d'export des données et rapports"""
    st.markdown('<h1 class="main-header">📤 Export des Données & Rapports</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <b>📤 Export:</b> Téléchargez vos données analysées et rapports personnalisés 
    dans différents formats pour vos présentations et analyses approfondies.
    </div>
    """, unsafe_allow_html=True)
    
    df_clean = data['clean_data']
    rfm_data = data['rfm_data']
    
    # Options d'export
    st.markdown("## 📋 Sélection des Données à Exporter")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_options = st.multiselect(
            "Choisissez les datasets à inclure:",
            [
                "📊 Données nettoyées",
                "🎯 Segments RFM",
                "👥 Cohortes d'acquisition", 
                "💰 Métriques CLV",
                "📈 KPIs consolidés"
            ],
            default=["📊 Données nettoyées", "🎯 Segments RFM"],
            help="Sélectionnez les données que vous souhaitez exporter"
        )
        
    with col2:
        export_format = st.selectbox(
            "Format de sortie:",
            ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"],
            help="Choisissez le format d'export"
        )
        
        date_suffix = st.checkbox(
            "Ajouter la date au nom de fichier",
            value=True,
            help="Inclut la date d'export dans le nom de fichier"
        )
    
    # Génération des exports
    if st.button("📦 Générer les Exports", type="primary"):
        with st.spinner("Préparation des exports..."):
            export_data = {}
            
            # Préparer les données selon les sélections
            if "📊 Données nettoyées" in export_options:
                export_data['donnees_nettoyees'] = df_clean
                
            if "🎯 Segments RFM" in export_options:
                rfm_segments = get_rfm_segments(rfm_data)
                export_data['segments_rfm'] = rfm_segments
                
            if "👥 Cohortes d'acquisition" in export_options:
                cohort_table = get_cohort_table(df_clean)
                retention_rates = get_retention_rates(cohort_table)
                export_data['cohortes_tailles'] = cohort_table
                export_data['cohortes_retention'] = retention_rates
                
            if "💰 Métriques CLV" in export_options:
                clv_metrics = calculate_clv_empirical(df_clean)
                clv_df = pd.DataFrame({
                    'CustomerID': clv_metrics.index,
                    'CLV_Empirique': clv_metrics.values
                })
                export_data['metriques_clv'] = clv_df
                
            if "📈 KPIs consolidés" in export_options:
                kpis = calculate_kpis(df_clean)
                kpis_df = pd.DataFrame([kpis]).T
                kpis_df.columns = ['Valeur']
                export_data['kpis_consolides'] = kpis_df
            
            # Génération des fichiers d'export
            timestamp = datetime.now().strftime('%Y%m%d_%H%M') if date_suffix else ""
            
            for dataset_name, dataset in export_data.items():
                filename = f"{dataset_name}_{timestamp}" if timestamp else dataset_name
                
                if export_format == "Excel (.xlsx)":
                    # Export Excel avec multiple sheets si plusieurs datasets
                    if len(export_data) > 1:
                        # Créer un fichier Excel multi-onglets
                        buffer = BytesIO()
                        
                        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                            for sheet_name, sheet_data in export_data.items():
                                sheet_data.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                        
                        st.download_button(
                            label=f"💾 Télécharger export_complet_{timestamp}.xlsx",
                            data=buffer.getvalue(),
                            file_name=f"export_complet_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        break  # Un seul fichier pour tous les datasets
                    else:
                        # Export Excel simple
                        buffer = BytesIO()
                        dataset.to_excel(buffer, index=False)
                        
                        st.download_button(
                            label=f"💾 Télécharger {filename}.xlsx",
                            data=buffer.getvalue(),
                            file_name=f"{filename}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                elif export_format == "CSV (.csv)":
                    csv_data = dataset.to_csv(index=False)
                    st.download_button(
                        label=f"💾 Télécharger {filename}.csv",
                        data=csv_data,
                        file_name=f"{filename}.csv",
                        mime="text/csv"
                    )
                    
                elif export_format == "JSON (.json)":
                    json_data = dataset.to_json(orient='records', indent=2)
                    st.download_button(
                        label=f"💾 Télécharger {filename}.json",
                        data=json_data,
                        file_name=f"{filename}.json",
                        mime="application/json"
                    )
    
    # Rapport exécutif
    st.markdown("## 📑 Rapport Exécutif Personnalisé")
    
    if st.button("📋 Générer Rapport Exécutif"):
        with st.spinner("Génération du rapport..."):
            # Calcul des métriques pour le rapport
            kpis = calculate_kpis(df_clean)
            rfm_segments = get_rfm_segments(rfm_data)
            segment_stats = rfm_segments.groupby('Segment').agg({
                'Recency': 'count',  # count pour nombre de clients
                'Monetary': ['mean', 'sum']
            }).round(2)
            
            # Génération du rapport en markdown
            report_content = f"""
# 📊 Rapport Exécutif - Marketing Analytics
**Généré le**: {datetime.now().strftime('%d/%m/%Y à %H:%M')}

## 🔑 Points Clés

### Performance Globale
- **Chiffre d'affaires total**: £{kpis['total_revenue']:,.0f}
- **Nombre de clients**: {kpis['total_customers']:,}
- **Panier moyen**: £{kpis['avg_order_value']:.0f}
- **CLV moyenne**: £{kpis['avg_clv']:,.0f}

### Segmentation Clientèle
{segment_stats.to_markdown()}

### Recommandations Prioritaires
1. **Segment Champions**: Maintenir l'engagement avec des programmes VIP
2. **Clients à Risque**: Lancer des campagnes de rétention immédiates  
3. **Nouveaux Clients**: Optimiser le parcours d'onboarding
4. **Clients Endormis**: Déployer des campagnes de réactivation

## 📈 Opportunités Identifiées
- Potentiel d'amélioration de la rétention: +{kpis.get('retention_opportunity', 15):.0f}%
- Opportunité d'augmentation du panier moyen: +{kpis.get('aov_opportunity', 12):.0f}%
- Impact estimé sur la CLV: +£{kpis.get('clv_opportunity', 500):,.0f} par client

---
*Rapport généré automatiquement par le système Marketing Analytics*
            """
            
            st.download_button(
                label="📄 Télécharger Rapport Exécutif (Markdown)",
                data=report_content,
                file_name=f"rapport_executif_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
    
    # Statistiques d'utilisation
    st.markdown("## 📊 Statistiques de l'Application")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📁 Datasets Disponibles", "5")
    with col2:
        st.metric("🔧 Fonctionnalités", "25+")  
    with col3:
        st.metric("📊 Visualisations", "15+")

def main():
    """Fonction principale de l'application Streamlit"""
    
    # Chargement des données avec gestion d'erreur
    data = load_all_data()
    if data is None:
        st.error("❌ Impossible de charger les données. Vérifiez que les fichiers sont présents dans le dossier data/processed/")
        st.stop()
    
    # Interface sidebar
    view, date_range, selected_countries, customer_type, min_clv = render_sidebar()
    
    # Application des filtres si nécessaire
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        data['clean_data'] = filter_data_by_date(data['clean_data'], start_date, end_date)
    
    if selected_countries:
        data['clean_data'] = data['clean_data'][data['clean_data']['Country'].isin(selected_countries)]
    
    # Routage vers les différentes vues
    if view == "🏠 Vue d'ensemble":
        overview_view(data)
    elif view == "👥 Analyse des Cohortes":
        cohorts_view(data)
    elif view == "🎯 Segmentation RFM":
        rfm_view(data)
    elif view == "💰 Scénarios CLV":
        scenarios_view(data)
    elif view == "📤 Export des Données":
        export_view(data)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
        📊 Marketing Analytics Dashboard | Powered by Streamlit & Python | 
        Données: Online Retail II Dataset (UCI Machine Learning Repository)
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()