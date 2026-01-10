"""
Module de gestion des données - Génération et chargement de données
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import CATEGORIES_COUTS, CENTRES_RESPONSABILITE


def generer_donnees_financieres(nb_mois: int = 24) -> pd.DataFrame:
    """
    Génère des données financières simulées pour une entreprise
    """
    np.random.seed(42)
    
    dates = pd.date_range(
        end=datetime.now(),
        periods=nb_mois,
        freq='ME'
    )
    
    # Tendance croissante avec saisonnalité
    base_ca = 500000
    tendance = np.linspace(0, 0.3, nb_mois)
    saisonnalite = 0.15 * np.sin(2 * np.pi * np.arange(nb_mois) / 12)
    bruit = np.random.normal(0, 0.05, nb_mois)
    
    chiffre_affaires = base_ca * (1 + tendance + saisonnalite + bruit)
    
    # Coûts variables (proportionnels au CA)
    taux_cout_variable = 0.45 + np.random.normal(0, 0.03, nb_mois)
    couts_variables = chiffre_affaires * taux_cout_variable
    
    # Coûts fixes avec légère augmentation
    couts_fixes = 150000 * (1 + np.linspace(0, 0.1, nb_mois) + np.random.normal(0, 0.02, nb_mois))
    
    # Calcul des marges
    marge_brute = chiffre_affaires - couts_variables
    resultat_exploitation = marge_brute - couts_fixes
    
    # Ajout d'anomalies pour la détection
    anomalies_idx = [5, 14, 20]
    for idx in anomalies_idx:
        if idx < nb_mois:
            couts_variables[idx] *= 1.25  # Surcoût anormal
            resultat_exploitation[idx] = marge_brute[idx] - couts_fixes[idx] - (couts_variables[idx] - chiffre_affaires[idx] * 0.45)
    
    df = pd.DataFrame({
        'date': dates,
        'mois': dates.strftime('%Y-%m'),
        'chiffre_affaires': np.round(chiffre_affaires, 2),
        'couts_variables': np.round(couts_variables, 2),
        'couts_fixes': np.round(couts_fixes, 2),
        'marge_brute': np.round(marge_brute, 2),
        'resultat_exploitation': np.round(resultat_exploitation, 2),
        'taux_marge_brute': np.round((marge_brute / chiffre_affaires) * 100, 2),
        'taux_resultat': np.round((resultat_exploitation / chiffre_affaires) * 100, 2)
    })
    
    return df


def generer_donnees_couts_detailles(nb_mois: int = 12) -> pd.DataFrame:
    """
    Génère des données de coûts détaillés par catégorie
    """
    np.random.seed(42)
    
    dates = pd.date_range(
        end=datetime.now(),
        periods=nb_mois,
        freq='ME'
    )
    
    data = []
    for date in dates:
        for categorie in CATEGORIES_COUTS:
            # Base différente selon la catégorie
            bases = {
                "Matières premières": 120000,
                "Main d'œuvre directe": 80000,
                "Frais généraux de production": 40000,
                "Frais administratifs": 25000,
                "Frais commerciaux": 35000,
                "Frais financiers": 15000,
                "Amortissements": 20000
            }
            
            base = bases.get(categorie, 30000)
            montant = base * (1 + np.random.normal(0, 0.1))
            budget = base * 1.02  # Budget légèrement supérieur
            
            data.append({
                'date': date,
                'mois': date.strftime('%Y-%m'),
                'categorie': categorie,
                'montant_reel': round(montant, 2),
                'budget': round(budget, 2),
                'ecart': round(montant - budget, 2),
                'ecart_pct': round(((montant - budget) / budget) * 100, 2)
            })
    
    return pd.DataFrame(data)


def generer_donnees_centres_responsabilite(nb_mois: int = 12) -> pd.DataFrame:
    """
    Génère des données par centre de responsabilité
    """
    np.random.seed(42)
    
    dates = pd.date_range(
        end=datetime.now(),
        periods=nb_mois,
        freq='ME'
    )
    
    data = []
    for date in dates:
        for centre in CENTRES_RESPONSABILITE:
            # Configuration par centre
            configs = {
                "Production": {"budget": 250000, "effectif": 45, "productivite_cible": 100},
                "Commercial": {"budget": 120000, "effectif": 20, "productivite_cible": 110},
                "Administratif": {"budget": 60000, "effectif": 10, "productivite_cible": 95},
                "R&D": {"budget": 80000, "effectif": 8, "productivite_cible": 100},
                "Logistique": {"budget": 70000, "effectif": 15, "productivite_cible": 105},
                "Qualité": {"budget": 40000, "effectif": 5, "productivite_cible": 100}
            }
            
            config = configs.get(centre, {"budget": 50000, "effectif": 10, "productivite_cible": 100})
            
            budget = config["budget"]
            depenses = budget * (1 + np.random.normal(0, 0.08))
            productivite = config["productivite_cible"] + np.random.normal(0, 8)
            
            data.append({
                'date': date,
                'mois': date.strftime('%Y-%m'),
                'centre': centre,
                'budget': round(budget, 2),
                'depenses_reelles': round(depenses, 2),
                'ecart': round(depenses - budget, 2),
                'effectif': config["effectif"],
                'productivite': round(productivite, 2),
                'cout_par_employe': round(depenses / config["effectif"], 2)
            })
    
    return pd.DataFrame(data)


def generer_kpis_operationnels(nb_mois: int = 12) -> pd.DataFrame:
    """
    Génère des KPIs opérationnels
    """
    np.random.seed(42)
    
    dates = pd.date_range(
        end=datetime.now(),
        periods=nb_mois,
        freq='ME'
    )
    
    data = []
    for i, date in enumerate(dates):
        # Simulation avec tendance et bruit
        taux_occupation = min(100, max(60, 82 + i * 0.3 + np.random.normal(0, 5)))
        delai_livraison = max(1, 5 + np.random.normal(0, 1.5))
        taux_service = min(100, max(85, 96 + np.random.normal(0, 2)))
        rotation_stocks = max(2, 8 + np.random.normal(0, 1))
        taux_rebut = max(0, 2.5 + np.random.normal(0, 0.8))
        satisfaction_client = min(10, max(5, 7.8 + i * 0.02 + np.random.normal(0, 0.3)))
        
        data.append({
            'date': date,
            'mois': date.strftime('%Y-%m'),
            'taux_occupation': round(taux_occupation, 2),
            'delai_livraison_jours': round(delai_livraison, 1),
            'taux_service': round(taux_service, 2),
            'rotation_stocks': round(rotation_stocks, 2),
            'taux_rebut': round(taux_rebut, 2),
            'satisfaction_client': round(satisfaction_client, 1)
        })
    
    return pd.DataFrame(data)


def charger_donnees_csv(fichier) -> pd.DataFrame:
    """
    Charge les données depuis un fichier CSV uploadé
    """
    try:
        df = pd.read_csv(fichier)
        # Convertir les colonnes de date si présentes
        for col in df.columns:
            if 'date' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass
        return df
    except Exception as e:
        raise Exception(f"Erreur lors du chargement du fichier CSV: {str(e)}")


def charger_donnees_excel(fichier) -> dict:
    """
    Charge les données depuis un fichier Excel (toutes les feuilles)
    """
    try:
        excel_file = pd.ExcelFile(fichier)
        dfs = {}
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(fichier, sheet_name=sheet_name)
            # Convertir les colonnes de date si présentes
            for col in df.columns:
                if 'date' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except:
                        pass
            dfs[sheet_name] = df
        return dfs
    except Exception as e:
        raise Exception(f"Erreur lors du chargement du fichier Excel: {str(e)}")


def calculer_statistiques_descriptives(df: pd.DataFrame) -> dict:
    """
    Calcule les statistiques descriptives pour les colonnes numériques
    """
    stats = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        stats[col] = {
            'moyenne': round(df[col].mean(), 2),
            'mediane': round(df[col].median(), 2),
            'ecart_type': round(df[col].std(), 2),
            'min': round(df[col].min(), 2),
            'max': round(df[col].max(), 2),
            'q1': round(df[col].quantile(0.25), 2),
            'q3': round(df[col].quantile(0.75), 2)
        }
    
    return stats


def preparer_donnees_pour_analyse(df: pd.DataFrame) -> str:
    """
    Prépare un résumé des données pour l'analyse IA
    """
    resume = []
    
    # Informations générales
    resume.append(f"Nombre d'observations: {len(df)}")
    resume.append(f"Colonnes: {', '.join(df.columns.tolist())}")
    resume.append("")
    
    # Statistiques pour chaque colonne numérique
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        resume.append(f"\n{col}:")
        resume.append(f"  - Moyenne: {df[col].mean():.2f}")
        resume.append(f"  - Min: {df[col].min():.2f}")
        resume.append(f"  - Max: {df[col].max():.2f}")
        resume.append(f"  - Écart-type: {df[col].std():.2f}")
    
    # Dernières valeurs
    resume.append("\nDernières observations:")
    resume.append(df.tail(5).to_string())
    
    return "\n".join(resume)


def generer_donnees_bilan(nb_mois: int = 12) -> pd.DataFrame:
    """
    Génère des données de bilan simplifiées pour le calcul de l'effet de levier
    """
    np.random.seed(42)
    
    dates = pd.date_range(
        end=datetime.now(),
        periods=nb_mois,
        freq='ME'
    )
    
    # Capitaux propres de base avec croissance
    base_capitaux_propres = 2000000
    capitaux_propres = base_capitaux_propres * (1 + np.linspace(0, 0.15, nb_mois) + np.random.normal(0, 0.02, nb_mois))
    
    # Dettes financières
    base_dettes = 1500000
    dettes_financieres = base_dettes * (1 + np.linspace(0, 0.05, nb_mois) + np.random.normal(0, 0.03, nb_mois))
    
    # Actif total = Capitaux propres + Dettes
    actif_total = capitaux_propres + dettes_financieres
    
    # Taux d'intérêt moyen sur la dette (entre 3% et 5% annuel)
    taux_interet_annuel = 0.04 + np.random.normal(0, 0.005, nb_mois)
    taux_interet_mensuel = taux_interet_annuel / 12
    
    # Charges financières
    charges_financieres = dettes_financieres * taux_interet_mensuel
    
    df = pd.DataFrame({
        'date': dates,
        'mois': dates.strftime('%Y-%m'),
        'capitaux_propres': np.round(capitaux_propres, 2),
        'dettes_financieres': np.round(dettes_financieres, 2),
        'actif_total': np.round(actif_total, 2),
        'taux_interet_annuel': np.round(taux_interet_annuel * 100, 2),
        'charges_financieres': np.round(charges_financieres, 2)
    })
    
    return df


def calculer_effet_levier(df_financier: pd.DataFrame, df_bilan: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les indicateurs d'effet de levier financier et opérationnel
    
    Formules:
    - Levier financier (LF) = Actif total / Capitaux propres
    - Rentabilité économique (ROA) = Résultat d'exploitation / Actif total
    - Coût de la dette (i) = Charges financières / Dettes
    - Différentiel de levier = ROA - i
    - Bras de levier = Dettes / Capitaux propres
    - Effet de levier = Différentiel × Bras de levier
    - Rentabilité financière (ROE) = ROA + Effet de levier
    - Levier opérationnel = Marge sur CV / Résultat d'exploitation
    """
    # Fusionner les données
    df = pd.merge(df_financier, df_bilan, on='mois', how='inner', suffixes=('', '_bilan'))
    
    # Calculs des indicateurs
    # Levier financier
    df['levier_financier'] = df['actif_total'] / df['capitaux_propres']
    
    # Rentabilité économique (ROA) - annualisée
    df['roa'] = (df['resultat_exploitation'] * 12 / df['actif_total']) * 100
    
    # Coût de la dette (annualisé)
    df['cout_dette'] = df['taux_interet_annuel']
    
    # Résultat net (après charges financières)
    df['resultat_net'] = df['resultat_exploitation'] - df['charges_financieres']
    
    # Rentabilité financière (ROE) - annualisée
    df['roe'] = (df['resultat_net'] * 12 / df['capitaux_propres']) * 100
    
    # Différentiel de levier
    df['differentiel_levier'] = df['roa'] - df['cout_dette']
    
    # Bras de levier (ratio d'endettement)
    df['bras_levier'] = df['dettes_financieres'] / df['capitaux_propres']
    
    # Effet de levier
    df['effet_levier'] = df['differentiel_levier'] * df['bras_levier']
    
    # Vérification: ROE = ROA + Effet de levier
    df['roe_verifie'] = df['roa'] + df['effet_levier']
    
    # Levier opérationnel (DOL - Degree of Operating Leverage)
    # DOL = Marge sur coûts variables / Résultat d'exploitation
    df['levier_operationnel'] = df['marge_brute'] / df['resultat_exploitation']
    
    # Levier combiné = Levier opérationnel × Levier financier
    df['levier_combine'] = df['levier_operationnel'] * df['levier_financier']
    
    # Arrondir les résultats
    colonnes_arrondies = ['levier_financier', 'roa', 'roe', 'differentiel_levier', 
                          'bras_levier', 'effet_levier', 'levier_operationnel', 'levier_combine']
    for col in colonnes_arrondies:
        df[col] = np.round(df[col], 2)
    
    return df
