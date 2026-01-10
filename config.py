"""
Configuration du projet - Tableau de Bord de Pilotage de la Performance
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Seuils d'alerte pour les KPIs
SEUILS_ALERTE = {
    "marge_brute": {"min": 20, "max": 100, "unite": "%"},
    "marge_nette": {"min": 5, "max": 100, "unite": "%"},
    "taux_croissance_ca": {"min": -5, "max": 100, "unite": "%"},
    "ratio_endettement": {"min": 0, "max": 60, "unite": "%"},
    "delai_paiement_clients": {"min": 0, "max": 60, "unite": "jours"},
    "delai_paiement_fournisseurs": {"min": 0, "max": 90, "unite": "jours"},
    "rotation_stocks": {"min": 4, "max": 52, "unite": "fois/an"},
    "taux_occupation": {"min": 70, "max": 100, "unite": "%"},
    "productivite": {"min": 80, "max": 150, "unite": "%"},
}

# Couleurs du dashboard
COULEURS = {
    "primaire": "#1f77b4",
    "succes": "#2ecc71",
    "avertissement": "#f39c12",
    "danger": "#e74c3c",
    "info": "#3498db",
    "gris": "#95a5a6"
}

# Catégories de coûts
CATEGORIES_COUTS = [
    "Matières premières",
    "Main d'œuvre directe",
    "Frais généraux de production",
    "Frais administratifs",
    "Frais commerciaux",
    "Frais financiers",
    "Amortissements"
]

# Centres de responsabilité
CENTRES_RESPONSABILITE = [
    "Production",
    "Commercial",
    "Administratif",
    "R&D",
    "Logistique",
    "Qualité"
]
