"""
Tableau de Bord Intelligent de Pilotage de la Performance
Application principale Streamlit
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# Import des modules du projet
from data_manager import (
    generer_donnees_financieres,
    generer_donnees_couts_detailles,
    generer_donnees_centres_responsabilite,
    generer_kpis_operationnels,
    generer_donnees_bilan,
    calculer_effet_levier,
    charger_donnees_csv,
    charger_donnees_excel,
    preparer_donnees_pour_analyse
)
from gemini_analyzer import GeminiAnalyzer
from anomaly_detector import DetecteurAnomalies, calculer_score_sante
from config import COULEURS, SEUILS_ALERTE

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Pilotage Performance",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
st.markdown("""
<style>
    /* Global settings */
    .main {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A; /* Dark Blue */
        text-align: center;
        margin-top: 2rem;
        margin-bottom: 2rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
        border-bottom: 2px solid #E5E7EB;
        padding-bottom: 0.5rem;
    }
    
    /* Metrics styling */
    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e1e4e8;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stMetricLabel"] {
        color: #64748B;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #1E3A8A;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px 8px 0 0;
        border: 1px solid transparent;
        padding: 10px 20px;
        color: #64748B;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #1E3A8A;
        background-color: #F8FAFC;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #1E3A8A !important;
        border: 1px solid #e5e7eb !important;
        border-bottom: 1px solid white !important;
        font-weight: 600 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e1e4e8;
    }
    
    /* Alerts styling */
    .alert-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid transparent;
    }
    
    /* Custom utility classes */
    .text-center { text-align: center; }
    .text-muted { color: #64748B; }
    
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialise les variables de session"""
    if 'df_financier' not in st.session_state:
        st.session_state.df_financier = generer_donnees_financieres(24)
    if 'df_couts' not in st.session_state:
        st.session_state.df_couts = generer_donnees_couts_detailles(12)
    if 'df_centres' not in st.session_state:
        st.session_state.df_centres = generer_donnees_centres_responsabilite(12)
    if 'df_kpis' not in st.session_state:
        st.session_state.df_kpis = generer_kpis_operationnels(12)
    if 'df_bilan' not in st.session_state:
        st.session_state.df_bilan = generer_donnees_bilan(12)
    if 'gemini_analyzer' not in st.session_state:
        st.session_state.gemini_analyzer = GeminiAnalyzer()
    if 'detecteur' not in st.session_state:
        st.session_state.detecteur = DetecteurAnomalies()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


def afficher_sidebar():
    """Affiche la barre latérale de configuration"""
    with st.sidebar:
        st.title("Configuration")
        
        st.divider()
        
        # Configuration API Gemini
        st.subheader("API Gemini")
        api_key = st.text_input(
            "Clé API Gemini",
            type="password",
            help="Obtenez votre clé gratuite sur aistudio.google.com"
        )
        
        if api_key:
            st.session_state.gemini_analyzer = GeminiAnalyzer(api_key)
            if st.session_state.gemini_analyzer.is_configured:
                st.success("API configurée avec succès")
            else:
                st.error("Erreur de configuration API")
        
        st.divider()
        
        # Upload de données
        st.subheader("Importer des données")
        uploaded_file = st.file_uploader(
            "Charger un fichier CSV/Excel",
            type=['csv', 'xlsx', 'xls']
        )
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    st.session_state.df_custom = charger_donnees_csv(uploaded_file)
                    st.success(f"{len(st.session_state.df_custom)} lignes chargées")
                else:
                    dfs = charger_donnees_excel(uploaded_file)
                    st.session_state.df_custom = dfs
                    st.success(f"{len(dfs)} feuilles chargées")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
        
        st.divider()
        
        # Régénérer les données
        st.subheader("Données de démonstration")
        if st.button("Régénérer les données", use_container_width=True):
            st.session_state.df_financier = generer_donnees_financieres(24)
            st.session_state.df_couts = generer_donnees_couts_detailles(12)
            st.session_state.df_centres = generer_donnees_centres_responsabilite(12)
            st.session_state.df_kpis = generer_kpis_operationnels(12)
            st.rerun()
        
        st.divider()
        st.caption("Projet AMIFI 2025-2026")
        st.caption("Pilotage de la Performance avec IA")


def afficher_kpis_principaux():
    """Affiche les KPIs principaux en haut du dashboard"""
    df = st.session_state.df_financier
    df_kpis = st.session_state.df_kpis
    
    derniere_periode = df.iloc[-1]
    periode_precedente = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
    
    # Calculs
    ca = derniere_periode['chiffre_affaires']
    ca_evolution = ((ca - periode_precedente['chiffre_affaires']) / periode_precedente['chiffre_affaires']) * 100
    
    marge = derniere_periode['taux_marge_brute']
    marge_evolution = marge - periode_precedente['taux_marge_brute']
    
    resultat = derniere_periode['resultat_exploitation']
    resultat_evolution = ((resultat - periode_precedente['resultat_exploitation']) / abs(periode_precedente['resultat_exploitation'])) * 100 if periode_precedente['resultat_exploitation'] != 0 else 0
    
    # Score de santé
    df_merge = pd.merge(df.tail(1), df_kpis.tail(1), on='mois', how='outer')
    score_sante = calculer_score_sante(df_merge)
    
    # Affichage en colonnes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Chiffre d'Affaires",
            value=f"{ca:,.0f} €",
            delta=f"{ca_evolution:+.1f}%"
        )
    
    with col2:
        st.metric(
            label="Marge Brute",
            value=f"{marge:.1f}%",
            delta=f"{marge_evolution:+.1f} pts"
        )
    
    with col3:
        st.metric(
            label="Résultat d'Exploitation",
            value=f"{resultat:,.0f} €",
            delta=f"{resultat_evolution:+.1f}%"
        )
    
    with col4:
        st.metric(
            label="Score de Santé",
            value=f"{score_sante}/100",
            delta="Bon" if score_sante >= 70 else ("Moyen" if score_sante >= 50 else "Faible")
        )


def afficher_alertes():
    """Affiche les alertes et anomalies détectées"""
    detecteur = st.session_state.detecteur
    df = st.session_state.df_financier
    df_kpis = st.session_state.df_kpis
    
    # Vérifier les alertes
    alertes = detecteur.verifier_seuils_alerte(df)
    alertes_kpis = detecteur.verifier_seuils_alerte(df_kpis)
    toutes_alertes = alertes + alertes_kpis
    
    if toutes_alertes:
        with st.expander(f"Alertes actives ({len(toutes_alertes)})", expanded=True):
            for alerte in toutes_alertes:
                if alerte['type'] == 'critique':
                    st.error(f"**CRITIQUE:** {alerte['message']}")
                else:
                    st.warning(f"ATTENTION: {alerte['message']}")
    else:
        st.success("Aucune alerte - Tous les indicateurs sont dans les normes")


def afficher_graphiques_financiers():
    """Affiche les graphiques financiers principaux"""
    df = st.session_state.df_financier
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Évolution du CA et des coûts
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['mois'],
            y=df['chiffre_affaires'],
            name='Chiffre d\'affaires',
            line=dict(color=COULEURS['primaire'], width=3),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['mois'],
            y=df['couts_variables'] + df['couts_fixes'],
            name='Coûts totaux',
            line=dict(color=COULEURS['danger'], width=2, dash='dash')
        ))
        
        fig.update_layout(
            title='Évolution CA vs Coûts',
            xaxis_title='Période',
            yaxis_title='Montant (€)',
            height=400,
            hovermode='x unified',
            template='plotly_white',
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Évolution des marges
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['mois'],
            y=df['taux_marge_brute'],
            name='Marge brute (%)',
            marker_color=COULEURS['succes']
        ))
        
        fig.add_trace(go.Scatter(
            x=df['mois'],
            y=df['taux_resultat'],
            name='Résultat (%)',
            line=dict(color=COULEURS['primaire'], width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Évolution des Marges',
            xaxis_title='Période',
            yaxis=dict(title='Marge brute (%)', side='left'),
            yaxis2=dict(title='Résultat (%)', side='right', overlaying='y'),
            height=400,
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            template='plotly_white',
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)


def afficher_analyse_couts():
    """Affiche l'analyse détaillée des coûts"""
    df = st.session_state.df_couts
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Répartition des coûts par catégorie
        df_dernier_mois = df[df['mois'] == df['mois'].max()]
        
        fig = px.pie(
            df_dernier_mois,
            values='montant_reel',
            names='categorie',
            title='Répartition des Coûts',
            hole=0.4
        )
        fig.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Écarts budgétaires par catégorie
        df_ecarts = df.groupby('categorie').agg({
            'montant_reel': 'sum',
            'budget': 'sum',
            'ecart': 'sum'
        }).reset_index()
        
        df_ecarts['ecart_pct'] = (df_ecarts['ecart'] / df_ecarts['budget']) * 100
        df_ecarts = df_ecarts.sort_values('ecart_pct', ascending=True)
        
        colors = ['#e74c3c' if x > 0 else '#2ecc71' for x in df_ecarts['ecart_pct']]
        
        fig = go.Figure(go.Bar(
            y=df_ecarts['categorie'],
            x=df_ecarts['ecart_pct'],
            orientation='h',
            marker_color=colors,
            text=[f"{x:+.1f}%" for x in df_ecarts['ecart_pct']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Écarts Budgétaires (%)',
            xaxis_title='Écart (%)',
            height=400,
            template='plotly_white',
            xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black')
        )
        
        st.plotly_chart(fig, use_container_width=True)


def afficher_centres_responsabilite():
    """Affiche l'analyse par centre de responsabilité"""
    df = st.session_state.df_centres
    
    # Agrégation par centre
    df_centres = df.groupby('centre').agg({
        'budget': 'sum',
        'depenses_reelles': 'sum',
        'productivite': 'mean',
        'effectif': 'first'
    }).reset_index()
    
    df_centres['ecart'] = df_centres['depenses_reelles'] - df_centres['budget']
    df_centres['ecart_pct'] = (df_centres['ecart'] / df_centres['budget']) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Comparaison Budget vs Réalisé
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Budget',
            x=df_centres['centre'],
            y=df_centres['budget'],
            marker_color=COULEURS['info']
        ))
        
        fig.add_trace(go.Bar(
            name='Réalisé',
            x=df_centres['centre'],
            y=df_centres['depenses_reelles'],
            marker_color=COULEURS['primaire']
        ))
        
        fig.update_layout(
            title='Budget vs Réalisé par Centre',
            barmode='group',
            height=400,
            template='plotly_white',
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Productivité par centre
        fig = go.Figure(go.Bar(
            x=df_centres['centre'],
            y=df_centres['productivite'],
            marker_color=[COULEURS['succes'] if p >= 100 else COULEURS['avertissement'] for p in df_centres['productivite']],
            text=[f"{p:.0f}%" for p in df_centres['productivite']],
            textposition='outside'
        ))
        
        fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Objectif 100%")
        
        fig.update_layout(
            title='Productivité par Centre (%)',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Tableau détaillé
    st.subheader("Détail par Centre de Responsabilité")
    
    df_affichage = df_centres[['centre', 'effectif', 'budget', 'depenses_reelles', 'ecart', 'ecart_pct', 'productivite']].copy()
    df_affichage.columns = ['Centre', 'Effectif', 'Budget (€)', 'Réalisé (€)', 'Écart (€)', 'Écart (%)', 'Productivité (%)']
    
    st.dataframe(
        df_affichage.style.format({
            'Budget (€)': '{:,.0f}',
            'Réalisé (€)': '{:,.0f}',
            'Écart (€)': '{:+,.0f}',
            'Écart (%)': '{:+.1f}',
            'Productivité (%)': '{:.1f}'
        }).applymap(
            lambda x: 'color: red' if isinstance(x, (int, float)) and x > 5 else '',
            subset=['Écart (%)']
        ),
        use_container_width=True
    )


def afficher_kpis_operationnels():
    """Affiche les KPIs opérationnels"""
    df = st.session_state.df_kpis
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Jauge de satisfaction client
        derniere_valeur = df.iloc[-1]['satisfaction_client']
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=derniere_valeur,
            title={'text': "Satisfaction Client"},
            delta={'reference': 7.5, 'relative': False},
            gauge={
                'axis': {'range': [0, 10]},
                'bar': {'color': COULEURS['succes'] if derniere_valeur >= 7 else COULEURS['avertissement']},
                'steps': [
                    {'range': [0, 5], 'color': 'lightgray'},
                    {'range': [5, 7], 'color': '#fff9e6'},
                    {'range': [7, 10], 'color': '#e6ffe6'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 7
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Taux de service
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=df.iloc[-1]['taux_service'],
            title={'text': "Taux de Service (%)"},
            delta={'reference': 95, 'relative': False},
            gauge={
                'axis': {'range': [80, 100]},
                'bar': {'color': COULEURS['primaire']},
                'steps': [
                    {'range': [80, 90], 'color': '#ffe6e6'},
                    {'range': [90, 95], 'color': '#fff9e6'},
                    {'range': [95, 100], 'color': '#e6ffe6'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Évolution des KPIs
    st.subheader("Évolution des KPIs Opérationnels")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Taux d\'occupation', 'Délai de livraison', 'Rotation des stocks', 'Taux de rebut')
    )
    
    fig.add_trace(
        go.Scatter(x=df['mois'], y=df['taux_occupation'], name='Taux occupation', line=dict(color=COULEURS['primaire'])),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['mois'], y=df['delai_livraison_jours'], name='Délai livraison', line=dict(color=COULEURS['succes'])),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=df['mois'], y=df['rotation_stocks'], name='Rotation stocks', line=dict(color=COULEURS['info'])),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['mois'], y=df['taux_rebut'], name='Taux rebut', line=dict(color=COULEURS['danger'])),
        row=2, col=2
    )
    
    fig.update_layout(height=500, showlegend=False, template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)


def afficher_effet_levier():
    """Affiche l'analyse de l'effet de levier financier et opérationnel"""
    st.header("Analyse de l'Effet de Levier")
    
    # Calculer les données d'effet de levier
    df_financier = st.session_state.df_financier.tail(12)
    df_bilan = st.session_state.df_bilan
    
    df_levier = calculer_effet_levier(df_financier, df_bilan)
    
    # Explication
    with st.expander("Comprendre l'effet de levier", expanded=False):
        st.markdown("""
        ### Formules utilisées
        
        **Levier Financier:**
        - **Levier financier** = Actif total / Capitaux propres
        - **ROA** (Rentabilité économique) = Résultat d'exploitation / Actif total
        - **ROE** (Rentabilité financière) = Résultat net / Capitaux propres
        - **Différentiel** = ROA - Coût de la dette
        - **Bras de levier** = Dettes / Capitaux propres
        - **Effet de levier** = Différentiel × Bras de levier
        
        **Levier Opérationnel:**
        - **DOL** = Marge sur coûts variables / Résultat d'exploitation
        
        **Interprétation:**
        - Si le différentiel est **positif** → L'endettement améliore la rentabilité des actionnaires
        - Si le différentiel est **négatif** → L'endettement détruit de la valeur
        """)
    
    st.divider()
    
    # KPIs principaux
    derniere_periode = df_levier.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="ROA (Rentabilité économique)",
            value=f"{derniere_periode['roa']:.1f}%",
            help="Résultat d'exploitation / Actif total (annualisé)"
        )
    
    with col2:
        st.metric(
            label="ROE (Rentabilité financière)",
            value=f"{derniere_periode['roe']:.1f}%",
            help="Résultat net / Capitaux propres (annualisé)"
        )
    
    with col3:
        effet = derniere_periode['effet_levier']
        st.metric(
            label="Effet de Levier",
            value=f"{effet:+.1f}%",
            delta="Favorable" if effet > 0 else "Défavorable",
            delta_color="normal" if effet > 0 else "inverse"
        )
    
    with col4:
        st.metric(
            label="Levier Financier",
            value=f"{derniere_periode['levier_financier']:.2f}x",
            help="Actif total / Capitaux propres"
        )
    
    st.divider()
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Comparaison ROA vs ROE
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_levier['mois'],
            y=df_levier['roa'],
            name='ROA',
            line=dict(color=COULEURS['primaire'], width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=df_levier['mois'],
            y=df_levier['roe'],
            name='ROE',
            line=dict(color=COULEURS['succes'], width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=df_levier['mois'],
            y=df_levier['cout_dette'],
            name='Coût de la dette',
            line=dict(color=COULEURS['danger'], width=2, dash='dash')
        ))
        
        fig.update_layout(
            title='Rentabilité: ROA vs ROE vs Coût de la dette',
            xaxis_title='Période',
            yaxis_title='Taux (%)',
            height=400,
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Décomposition de l'effet de levier
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df_levier['mois'],
            y=df_levier['differentiel_levier'],
            name='Différentiel (ROA - i)',
            marker_color=[COULEURS['succes'] if x > 0 else COULEURS['danger'] for x in df_levier['differentiel_levier']]
        ))
        
        fig.add_trace(go.Scatter(
            x=df_levier['mois'],
            y=df_levier['effet_levier'],
            name='Effet de levier',
            line=dict(color=COULEURS['primaire'], width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Décomposition de l\'effet de levier',
            xaxis_title='Période',
            yaxis=dict(title='Différentiel (%)', side='left'),
            yaxis2=dict(title='Effet de levier (%)', side='right', overlaying='y'),
            height=400,
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Deuxième ligne de graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Structure financière
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df_levier['mois'],
            y=df_levier['capitaux_propres'],
            name='Capitaux propres',
            marker_color=COULEURS['succes']
        ))
        
        fig.add_trace(go.Bar(
            x=df_levier['mois'],
            y=df_levier['dettes_financieres'],
            name='Dettes financières',
            marker_color=COULEURS['danger']
        ))
        
        fig.update_layout(
            title='Structure Financière',
            barmode='stack',
            xaxis_title='Période',
            yaxis_title='Montant (€)',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Leviers opérationnel et combiné
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_levier['mois'],
            y=df_levier['levier_operationnel'],
            name='Levier opérationnel (DOL)',
            line=dict(color=COULEURS['info'], width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=df_levier['mois'],
            y=df_levier['levier_combine'],
            name='Levier combiné (DCL)',
            line=dict(color=COULEURS['avertissement'], width=3)
        ))
        
        fig.update_layout(
            title='Levier Opérationnel et Combiné',
            xaxis_title='Période',
            yaxis_title='Coefficient',
            height=400,
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Tableau récapitulatif
    st.subheader("Tableau Récapitulatif")
    
    df_affichage = df_levier[[
        'mois', 'capitaux_propres', 'dettes_financieres', 'roa', 'roe', 
        'cout_dette', 'differentiel_levier', 'bras_levier', 'effet_levier',
        'levier_operationnel'
    ]].copy()
    
    df_affichage.columns = [
        'Période', 'Capitaux Propres (€)', 'Dettes (€)', 'ROA (%)', 'ROE (%)',
        'Coût Dette (%)', 'Différentiel (%)', 'Bras Levier', 'Effet Levier (%)',
        'Levier Opérationnel'
    ]
    
    st.dataframe(
        df_affichage.style.format({
            'Capitaux Propres (€)': '{:,.0f}',
            'Dettes (€)': '{:,.0f}',
            'ROA (%)': '{:.2f}',
            'ROE (%)': '{:.2f}',
            'Coût Dette (%)': '{:.2f}',
            'Différentiel (%)': '{:+.2f}',
            'Bras Levier': '{:.2f}',
            'Effet Levier (%)': '{:+.2f}',
            'Levier Opérationnel': '{:.2f}'
        }).applymap(
            lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0 else ('color: red' if isinstance(x, (int, float)) and x < 0 else ''),
            subset=['Différentiel (%)', 'Effet Levier (%)']
        ),
        use_container_width=True
    )
    
    # Analyse et interprétation
    st.subheader("Interprétation")
    
    moy_effet = df_levier['effet_levier'].mean()
    moy_diff = df_levier['differentiel_levier'].mean()
    moy_bras = df_levier['bras_levier'].mean()
    
    if moy_diff > 0:
        st.success(f"""
        **Effet de levier favorable** : Le différentiel moyen est de **{moy_diff:+.2f}%**.
        
        L'entreprise génère une rentabilité économique (ROA) supérieure au coût de sa dette.
        L'endettement amplifie la rentabilité des capitaux propres de **{moy_effet:+.2f}%** en moyenne.
        
        Avec un bras de levier de **{moy_bras:.2f}**, la structure financière permet de créer de la valeur.
        """)
    else:
        st.error(f"""
        **Effet de levier défavorable** : Le différentiel moyen est de **{moy_diff:+.2f}%**.
        
        L'entreprise génère une rentabilité économique (ROA) inférieure au coût de sa dette.
        L'endettement diminue la rentabilité des capitaux propres de **{abs(moy_effet):.2f}%** en moyenne.
        
        Il est recommandé de réduire l'endettement ou d'améliorer la performance opérationnelle.
        """)


def afficher_detection_anomalies():
    """Affiche la page de détection d'anomalies"""
    st.header("Détection d'Anomalies")
    
    detecteur = st.session_state.detecteur
    df = st.session_state.df_financier
    
    # Générer le rapport d'anomalies
    rapport = detecteur.generer_rapport_anomalies(df)
    
    # Résumé
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Outliers IQR", rapport['resume']['nb_outliers_iqr'])
    with col2:
        st.metric("Outliers Z-Score", rapport['resume']['nb_outliers_zscore'])
    with col3:
        st.metric("Anomalies Multidim.", rapport['resume']['nb_anomalies_multidim'])
    with col4:
        st.metric("Alertes Seuils", rapport['resume']['nb_alertes'])
    
    st.markdown("---")
    
    # Détails des anomalies
    tab1, tab2, tab3 = st.tabs(["Outliers Statistiques", "Anomalies Multidimensionnelles", "Ruptures de Tendance"])
    
    with tab1:
        if rapport['outliers_iqr'] is not None and len(rapport['outliers_iqr']) > 0:
            st.dataframe(rapport['outliers_iqr'], use_container_width=True)
        else:
            st.info("Aucun outlier statistique détecté")
    
    with tab2:
        if rapport['anomalies_multidim'] is not None and len(rapport['anomalies_multidim']) > 0:
            st.dataframe(rapport['anomalies_multidim'], use_container_width=True)
        else:
            st.info("Aucune anomalie multidimensionnelle détectée")
    
    with tab3:
        if rapport['ruptures']:
            for r in rapport['ruptures']:
                st.write(f"**{r['colonne']}**")
                st.dataframe(r['ruptures'], use_container_width=True)
        else:
            st.info("Aucune rupture de tendance détectée")
    
    # Analyse IA des anomalies
    st.markdown("---")
    st.subheader("Analyse IA des Anomalies")
    
    if st.button("Analyser avec Gemini AI", type="primary"):
        with st.spinner("Analyse en cours..."):
            analyzer = st.session_state.gemini_analyzer
            analyse = analyzer.detecter_anomalies_ia(df)
            st.markdown(analyse)


def afficher_aide_decision():
    """Affiche la page d'aide à la décision avec IA"""
    st.header("Aide à la Décision IA")
    
    analyzer = st.session_state.gemini_analyzer
    df_fin = st.session_state.df_financier
    df_kpis = st.session_state.df_kpis
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Analyse Globale",
        "Prévisions",
        "Recommandations",
        "Chat IA"
    ])
    
    with tab1:
        st.subheader("Analyse de Performance Globale")
        
        if st.button("Lancer l'analyse complète", type="primary", key="btn_analyse"):
            with st.spinner("Analyse IA en cours..."):
                analyse = analyzer.analyser_performance_globale(df_fin, df_kpis)
                st.markdown(analyse)
    
    with tab2:
        st.subheader("Prévisions et Tendances")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            colonne_cible = st.selectbox(
                "Indicateur à prévoir",
                options=['chiffre_affaires', 'marge_brute', 'resultat_exploitation', 'couts_variables']
            )
        
        with col2:
            horizon = st.slider("Horizon (mois)", 1, 12, 3)
        
        if st.button("Générer les prévisions", type="primary", key="btn_prev"):
            with st.spinner("Génération des prévisions..."):
                previsions = analyzer.prevoir_tendances(df_fin, colonne_cible, horizon)
                st.markdown(previsions)
    
    with tab3:
        st.subheader("Recommandations Stratégiques")
        
        # Préparer le contexte
        dernier_mois = df_fin.iloc[-1]
        contexte = {
            "chiffre_affaires_mensuel": float(dernier_mois['chiffre_affaires']),
            "taux_marge_brute": float(dernier_mois['taux_marge_brute']),
            "taux_resultat": float(dernier_mois['taux_resultat']),
            "tendance_ca": "croissante" if df_fin['chiffre_affaires'].iloc[-1] > df_fin['chiffre_affaires'].iloc[-3] else "décroissante",
            "nb_employes": int(st.session_state.df_centres['effectif'].sum() / 12),
            "secteur": "Industrie"
        }
        
        st.json(contexte)
        
        if st.button("Obtenir des recommandations", type="primary", key="btn_reco"):
            with st.spinner("Génération des recommandations..."):
                recommandations = analyzer.generer_recommandations_strategiques(contexte)
                st.markdown(recommandations)
    
    with tab4:
        st.subheader("Assistant Contrôle de Gestion")
        
        # Historique du chat
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input utilisateur
        if prompt := st.chat_input("Posez votre question sur la performance..."):
            # Afficher le message utilisateur
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Préparer le contexte
            contexte = preparer_donnees_pour_analyse(df_fin)
            
            # Obtenir la réponse IA
            with st.chat_message("assistant"):
                with st.spinner("Réflexion..."):
                    reponse = analyzer.chat_controleur_gestion(prompt, contexte)
                    st.markdown(reponse)
            
            st.session_state.chat_history.append({"role": "assistant", "content": reponse})


def afficher_export_donnees():
    """Page d'export des données"""
    st.header("Export des Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Données Financières")
        st.dataframe(st.session_state.df_financier.tail(12), use_container_width=True)
        
        csv = st.session_state.df_financier.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Télécharger CSV",
            csv,
            "donnees_financieres.csv",
            "text/csv",
            key='download_fin'
        )
    
    with col2:
        st.subheader("Données des Coûts")
        st.dataframe(st.session_state.df_couts.tail(12), use_container_width=True)
        
        csv = st.session_state.df_couts.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Télécharger CSV",
            csv,
            "donnees_couts.csv",
            "text/csv",
            key='download_couts'
        )


def main():
    """Fonction principale"""
    init_session_state()
    afficher_sidebar()
    
    # Titre principal
    st.markdown('<h1 class="main-header">Tableau de Bord de Pilotage de la Performance</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Solution intelligente d\'aide à la décision avec Gemini AI</p>', unsafe_allow_html=True)
    
    # Navigation par onglets
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Vue d'ensemble",
        "Analyse des Coûts",
        "Centres de Responsabilité",
        "KPIs Opérationnels",
        "Effet de Levier",
        "Détection Anomalies",
        "Aide à la Décision IA"
    ])
    
    with tab1:
        st.subheader("Indices de Performance")
        afficher_kpis_principaux()
        
        st.divider()
        afficher_alertes()
        
        st.divider()
        st.subheader("Analyse Financière")
        afficher_graphiques_financiers()
    
    with tab2:
        afficher_analyse_couts()
    
    with tab3:
        afficher_centres_responsabilite()
    
    with tab4:
        afficher_kpis_operationnels()
    
    with tab5:
        afficher_effet_levier()
    
    with tab6:
        afficher_detection_anomalies()
    
    with tab7:
        afficher_aide_decision()
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style="text-align: center; color: #888; padding: 1rem;">
            <p>Projet AMIFI - Pilotage de la Performance avec Intelligence Artificielle</p>
            <p>Développé avec Streamlit & Gemini AI | 2025-2026</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
