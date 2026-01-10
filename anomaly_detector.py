"""
Module de détection d'anomalies et d'alertes
"""
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from config import SEUILS_ALERTE, COULEURS


class DetecteurAnomalies:
    """
    Classe pour la détection d'anomalies dans les données de performance
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
    
    def detecter_outliers_statistiques(self, df: pd.DataFrame, colonnes: list = None) -> pd.DataFrame:
        """
        Détecte les outliers en utilisant la méthode IQR
        """
        if colonnes is None:
            colonnes = df.select_dtypes(include=[np.number]).columns.tolist()
        
        resultats = []
        
        for col in colonnes:
            if col in df.columns:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                borne_inf = q1 - 1.5 * iqr
                borne_sup = q3 + 1.5 * iqr
                
                for idx, valeur in df[col].items():
                    if valeur < borne_inf or valeur > borne_sup:
                        resultats.append({
                            'index': idx,
                            'colonne': col,
                            'valeur': valeur,
                            'borne_inf': borne_inf,
                            'borne_sup': borne_sup,
                            'type_anomalie': 'outlier_IQR',
                            'severite': 'Élevée' if abs(valeur - df[col].mean()) > 3 * df[col].std() else 'Moyenne'
                        })
        
        return pd.DataFrame(resultats)
    
    def detecter_outliers_zscore(self, df: pd.DataFrame, colonnes: list = None, seuil: float = 3.0) -> pd.DataFrame:
        """
        Détecte les outliers en utilisant le Z-score
        """
        if colonnes is None:
            colonnes = df.select_dtypes(include=[np.number]).columns.tolist()
        
        resultats = []
        
        for col in colonnes:
            if col in df.columns and df[col].std() > 0:
                z_scores = np.abs(stats.zscore(df[col].dropna()))
                
                for i, (idx, valeur) in enumerate(df[col].items()):
                    if i < len(z_scores) and z_scores[i] > seuil:
                        resultats.append({
                            'index': idx,
                            'colonne': col,
                            'valeur': valeur,
                            'z_score': z_scores[i],
                            'type_anomalie': 'outlier_zscore',
                            'severite': 'Élevée' if z_scores[i] > 4 else 'Moyenne'
                        })
        
        return pd.DataFrame(resultats)
    
    def detecter_anomalies_isolation_forest(self, df: pd.DataFrame, colonnes: list = None) -> pd.DataFrame:
        """
        Utilise Isolation Forest pour détecter les anomalies multidimensionnelles
        """
        if colonnes is None:
            colonnes = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(colonnes) < 2:
            return pd.DataFrame()
        
        df_analyse = df[colonnes].dropna()
        
        if len(df_analyse) < 10:
            return pd.DataFrame()
        
        # Normalisation
        X_scaled = self.scaler.fit_transform(df_analyse)
        
        # Détection
        predictions = self.isolation_forest.fit_predict(X_scaled)
        scores = self.isolation_forest.decision_function(X_scaled)
        
        resultats = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomalie détectée
                resultats.append({
                    'index': df_analyse.index[i],
                    'score_anomalie': -score,
                    'type_anomalie': 'isolation_forest',
                    'severite': 'Élevée' if score < -0.3 else 'Moyenne',
                    'valeurs': df_analyse.iloc[i].to_dict()
                })
        
        return pd.DataFrame(resultats)
    
    def detecter_ruptures_tendance(self, df: pd.DataFrame, colonne: str, fenetre: int = 3) -> pd.DataFrame:
        """
        Détecte les ruptures de tendance dans une série temporelle
        """
        if colonne not in df.columns:
            return pd.DataFrame()
        
        serie = df[colonne].dropna()
        
        if len(serie) < fenetre * 2:
            return pd.DataFrame()
        
        # Calcul de la moyenne mobile
        moyenne_mobile = serie.rolling(window=fenetre).mean()
        ecart_type_mobile = serie.rolling(window=fenetre).std()
        
        resultats = []
        
        for i in range(fenetre, len(serie)):
            if ecart_type_mobile.iloc[i-1] > 0:
                z_local = abs(serie.iloc[i] - moyenne_mobile.iloc[i-1]) / ecart_type_mobile.iloc[i-1]
                
                if z_local > 2.5:
                    variation_pct = ((serie.iloc[i] - moyenne_mobile.iloc[i-1]) / moyenne_mobile.iloc[i-1]) * 100
                    resultats.append({
                        'index': serie.index[i],
                        'colonne': colonne,
                        'valeur_actuelle': serie.iloc[i],
                        'moyenne_precedente': moyenne_mobile.iloc[i-1],
                        'variation_pct': variation_pct,
                        'type_anomalie': 'rupture_tendance',
                        'severite': 'Élevée' if z_local > 3.5 else 'Moyenne'
                    })
        
        return pd.DataFrame(resultats)
    
    def verifier_seuils_alerte(self, df: pd.DataFrame) -> list:
        """
        Vérifie les KPIs par rapport aux seuils d'alerte définis
        """
        alertes = []
        
        # Mapping des colonnes vers les seuils
        mapping_colonnes = {
            'taux_marge_brute': 'marge_brute',
            'taux_resultat': 'marge_nette',
            'taux_occupation': 'taux_occupation',
            'productivite': 'productivite',
            'rotation_stocks': 'rotation_stocks'
        }
        
        derniere_ligne = df.iloc[-1] if len(df) > 0 else None
        
        if derniere_ligne is None:
            return alertes
        
        for col_df, col_seuil in mapping_colonnes.items():
            if col_df in df.columns and col_seuil in SEUILS_ALERTE:
                valeur = derniere_ligne[col_df]
                seuil = SEUILS_ALERTE[col_seuil]
                
                if valeur < seuil['min']:
                    alertes.append({
                        'type': 'critique',
                        'indicateur': col_df,
                        'valeur': valeur,
                        'seuil': seuil['min'],
                        'unite': seuil['unite'],
                        'message': f"{col_df.replace('_', ' ').title()} est en dessous du seuil minimum ({valeur:.1f} < {seuil['min']})"
                    })
                elif valeur > seuil['max']:
                    alertes.append({
                        'type': 'avertissement',
                        'indicateur': col_df,
                        'valeur': valeur,
                        'seuil': seuil['max'],
                        'unite': seuil['unite'],
                        'message': f"{col_df.replace('_', ' ').title()} dépasse le seuil maximum ({valeur:.1f} > {seuil['max']})"
                    })
        
        return alertes
    
    def analyser_ecarts_budget(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyse les écarts par rapport au budget
        """
        if 'montant_reel' not in df.columns or 'budget' not in df.columns:
            return pd.DataFrame()
        
        df_analyse = df.copy()
        df_analyse['ecart_absolu'] = df_analyse['montant_reel'] - df_analyse['budget']
        df_analyse['ecart_pct'] = (df_analyse['ecart_absolu'] / df_analyse['budget']) * 100
        
        # Identifier les écarts significatifs (>10%)
        df_analyse['est_significatif'] = abs(df_analyse['ecart_pct']) > 10
        df_analyse['severite'] = df_analyse['ecart_pct'].apply(
            lambda x: 'Critique' if abs(x) > 20 else ('Élevée' if abs(x) > 15 else 'Moyenne')
        )
        
        ecarts_significatifs = df_analyse[df_analyse['est_significatif']]
        
        return ecarts_significatifs
    
    def generer_rapport_anomalies(self, df: pd.DataFrame, colonnes: list = None) -> dict:
        """
        Génère un rapport complet des anomalies détectées
        """
        rapport = {
            'resume': {},
            'outliers_iqr': None,
            'outliers_zscore': None,
            'anomalies_multidim': None,
            'ruptures': [],
            'alertes_seuils': []
        }
        
        # Détection par différentes méthodes
        rapport['outliers_iqr'] = self.detecter_outliers_statistiques(df, colonnes)
        rapport['outliers_zscore'] = self.detecter_outliers_zscore(df, colonnes)
        rapport['anomalies_multidim'] = self.detecter_anomalies_isolation_forest(df, colonnes)
        
        # Ruptures de tendance pour chaque colonne numérique
        if colonnes is None:
            colonnes = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in colonnes[:5]:  # Limiter pour la performance
            ruptures = self.detecter_ruptures_tendance(df, col)
            if not ruptures.empty:
                rapport['ruptures'].append({'colonne': col, 'ruptures': ruptures})
        
        # Alertes de seuils
        rapport['alertes_seuils'] = self.verifier_seuils_alerte(df)
        
        # Résumé
        rapport['resume'] = {
            'nb_outliers_iqr': len(rapport['outliers_iqr']) if rapport['outliers_iqr'] is not None else 0,
            'nb_outliers_zscore': len(rapport['outliers_zscore']) if rapport['outliers_zscore'] is not None else 0,
            'nb_anomalies_multidim': len(rapport['anomalies_multidim']) if rapport['anomalies_multidim'] is not None else 0,
            'nb_ruptures': sum(len(r['ruptures']) for r in rapport['ruptures']),
            'nb_alertes': len(rapport['alertes_seuils'])
        }
        
        return rapport


def calculer_score_sante(df: pd.DataFrame, poids: dict = None) -> float:
    """
    Calcule un score de santé global de l'entreprise (0-100)
    """
    if poids is None:
        poids = {
            'taux_marge_brute': 0.25,
            'taux_resultat': 0.25,
            'taux_occupation': 0.15,
            'productivite': 0.15,
            'taux_service': 0.10,
            'satisfaction_client': 0.10
        }
    
    scores = []
    poids_utilises = []
    
    derniere_ligne = df.iloc[-1] if len(df) > 0 else None
    
    if derniere_ligne is None:
        return 50.0
    
    for indicateur, poid in poids.items():
        if indicateur in df.columns:
            valeur = derniere_ligne[indicateur]
            
            # Normalisation selon l'indicateur
            if indicateur in ['taux_marge_brute', 'taux_resultat', 'taux_occupation', 'taux_service', 'productivite']:
                # Pour les pourcentages, normaliser sur 0-100
                score = min(100, max(0, valeur))
            elif indicateur == 'satisfaction_client':
                # Satisfaction sur 10, convertir en 0-100
                score = min(100, max(0, valeur * 10))
            else:
                score = 50  # Score neutre par défaut
            
            scores.append(score * poid)
            poids_utilises.append(poid)
    
    if not scores:
        return 50.0
    
    # Normaliser par le poids total utilisé
    score_total = sum(scores) / sum(poids_utilises) if sum(poids_utilises) > 0 else 50.0
    
    return round(score_total, 1)


def determiner_couleur_alerte(valeur: float, seuil_min: float, seuil_max: float) -> str:
    """
    Détermine la couleur d'alerte basée sur la valeur et les seuils
    """
    if valeur < seuil_min:
        return COULEURS['danger']
    elif valeur > seuil_max:
        return COULEURS['avertissement']
    else:
        return COULEURS['succes']
