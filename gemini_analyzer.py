"""
Module d'intégration Gemini AI - Analyse intelligente et aide à la décision
"""
import google.generativeai as genai
from config import GEMINI_API_KEY, SEUILS_ALERTE
import pandas as pd
import json


class GeminiAnalyzer:
    """
    Classe pour l'analyse intelligente des données avec Gemini AI
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialise le client Gemini
        """
        self.api_key = api_key or GEMINI_API_KEY
        self.model = None
        self.is_configured = False
        
        if self.api_key and self.api_key != "votre_cle_api_gemini_ici":
            try:
                genai.configure(api_key=self.api_key)
                # Utiliser gemini-2.0-flash (modèle gratuit et rapide)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                self.is_configured = True
            except Exception as e:
                print(f"Erreur de configuration Gemini: {e}")
    
    def analyser_performance_globale(self, df_financier: pd.DataFrame, df_kpis: pd.DataFrame = None) -> str:
        """
        Analyse la performance globale de l'entreprise
        """
        if not self.is_configured:
            return self._analyse_sans_ia(df_financier, df_kpis)
        
        # Préparer le contexte
        contexte = self._preparer_contexte_financier(df_financier)
        if df_kpis is not None:
            contexte += "\n\nKPIs Opérationnels:\n" + self._preparer_contexte_kpis(df_kpis)
        
        prompt = f"""Tu es un expert en contrôle de gestion et pilotage de la performance. 
Analyse les données financières suivantes et fournis une analyse structurée:

{contexte}

Fournis une analyse comprenant:
1. **Synthèse de la performance** (3-4 phrases clés)
2. **Points forts** (2-3 éléments positifs)
3. **Points de vigilance** (2-3 risques ou problèmes identifiés)
4. **Tendances observées** (évolution sur la période)
5. **Recommandations prioritaires** (3 actions concrètes)

Réponds en français, de manière professionnelle et concise."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erreur lors de l'analyse IA: {str(e)}\n\n" + self._analyse_sans_ia(df_financier, df_kpis)
    
    def detecter_anomalies_ia(self, df: pd.DataFrame, colonnes_a_analyser: list = None) -> str:
        """
        Utilise l'IA pour détecter des anomalies dans les données
        """
        if not self.is_configured:
            return self._detection_anomalies_basique(df, colonnes_a_analyser)
        
        # Préparer les données
        if colonnes_a_analyser is None:
            colonnes_a_analyser = df.select_dtypes(include=['number']).columns.tolist()
        
        resume_donnees = df[colonnes_a_analyser].describe().to_string()
        dernieres_valeurs = df[colonnes_a_analyser].tail(6).to_string()
        
        prompt = f"""Tu es un expert en détection d'anomalies financières et opérationnelles.
Analyse ces données et identifie les anomalies potentielles:

Statistiques descriptives:
{resume_donnees}

Dernières valeurs:
{dernieres_valeurs}

Identifie:
1. **Valeurs aberrantes** (outliers statistiques)
2. **Ruptures de tendance** inhabituelles
3. **Incohérences** entre indicateurs
4. **Signaux d'alerte** pour le management

Pour chaque anomalie, indique:
- La nature de l'anomalie
- Le niveau de gravité (Faible/Moyen/Élevé)
- L'action recommandée

Réponds en français de manière structurée."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erreur: {str(e)}\n\n" + self._detection_anomalies_basique(df, colonnes_a_analyser)
    
    def generer_recommandations_strategiques(self, contexte_entreprise: dict) -> str:
        """
        Génère des recommandations stratégiques basées sur le contexte
        """
        if not self.is_configured:
            return self._recommandations_generiques()
        
        prompt = f"""Tu es un consultant senior en stratégie d'entreprise et contrôle de gestion.
Basé sur le contexte suivant, génère des recommandations stratégiques:

Contexte de l'entreprise:
{json.dumps(contexte_entreprise, indent=2, ensure_ascii=False)}

Fournis:
1. **Diagnostic stratégique** (forces, faiblesses, opportunités, menaces)
2. **Axes d'amélioration prioritaires** (3-5 axes)
3. **Plan d'action à court terme** (actions pour les 3 prochains mois)
4. **Plan d'action à moyen terme** (actions pour les 6-12 prochains mois)
5. **KPIs à suivre** pour mesurer les progrès

Réponds en français de manière opérationnelle et actionnable."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erreur: {str(e)}\n\n" + self._recommandations_generiques()
    
    def analyser_ecarts_budgetaires(self, df_budget: pd.DataFrame) -> str:
        """
        Analyse les écarts budgétaires et propose des actions correctives
        """
        if not self.is_configured:
            return self._analyse_ecarts_basique(df_budget)
        
        resume = df_budget.to_string()
        
        prompt = f"""Tu es un contrôleur de gestion expert en analyse budgétaire.
Analyse les écarts budgétaires suivants:

{resume}

Fournis:
1. **Synthèse des écarts** (écarts significatifs identifiés)
2. **Causes probables** pour chaque écart majeur
3. **Impact sur la performance** globale
4. **Actions correctives** prioritaires
5. **Prévisions** ajustées si les écarts persistent

Réponds en français de manière précise et opérationnelle."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erreur: {str(e)}\n\n" + self._analyse_ecarts_basique(df_budget)
    
    def prevoir_tendances(self, df: pd.DataFrame, colonne_cible: str, horizon: int = 3) -> str:
        """
        Génère des prévisions et analyses de tendances
        """
        if not self.is_configured:
            return self._prevision_basique(df, colonne_cible, horizon)
        
        # Calculer les tendances de base
        if colonne_cible in df.columns:
            valeurs = df[colonne_cible].tail(12).tolist()
            moyenne = sum(valeurs) / len(valeurs)
            tendance = (valeurs[-1] - valeurs[0]) / len(valeurs) if len(valeurs) > 1 else 0
        else:
            return "Colonne cible non trouvée dans les données."
        
        prompt = f"""Tu es un expert en analyse prévisionnelle et data science appliquée à la finance.
Analyse les données suivantes et fournis des prévisions:

Valeurs historiques (12 derniers mois): {valeurs}
Moyenne: {moyenne:.2f}
Tendance mensuelle moyenne: {tendance:.2f}
Horizon de prévision: {horizon} mois

Fournis:
1. **Analyse de la tendance** actuelle
2. **Facteurs de saisonnalité** éventuels
3. **Prévisions** pour les {horizon} prochains mois (avec intervalles de confiance)
4. **Scénarios** (optimiste, réaliste, pessimiste)
5. **Risques** potentiels affectant les prévisions
6. **Recommandations** pour améliorer la performance future

Réponds en français avec des chiffres précis."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erreur: {str(e)}\n\n" + self._prevision_basique(df, colonne_cible, horizon)
    
    def chat_controleur_gestion(self, question: str, contexte_donnees: str = "") -> str:
        """
        Chat interactif avec un assistant IA spécialisé en contrôle de gestion
        """
        if not self.is_configured:
            return "L'API Gemini n'est pas configurée. Veuillez ajouter votre clé API dans le fichier .env"
        
        prompt = f"""Tu es un assistant expert en contrôle de gestion, finance d'entreprise et pilotage de la performance.
Tu aides les managers et dirigeants à prendre des décisions éclairées basées sur les données.

Contexte des données de l'entreprise:
{contexte_donnees}

Question de l'utilisateur: {question}

Réponds de manière professionnelle, précise et actionnable. 
Si tu ne peux pas répondre avec certitude, indique-le clairement.
Réponds en français."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erreur lors de la génération de la réponse: {str(e)}"
    
    # Méthodes de fallback (sans IA)
    def _analyse_sans_ia(self, df_financier: pd.DataFrame, df_kpis: pd.DataFrame = None) -> str:
        """Analyse basique sans IA"""
        analyse = ["## Analyse de Performance (Mode basique - API IA non configurée)\n"]
        
        if 'chiffre_affaires' in df_financier.columns:
            ca_moyen = df_financier['chiffre_affaires'].mean()
            ca_dernier = df_financier['chiffre_affaires'].iloc[-1]
            evolution = ((ca_dernier - df_financier['chiffre_affaires'].iloc[0]) / df_financier['chiffre_affaires'].iloc[0]) * 100
            
            analyse.append(f"### Chiffre d'affaires")
            analyse.append(f"- Moyenne: {ca_moyen:,.0f} €")
            analyse.append(f"- Dernier mois: {ca_dernier:,.0f} €")
            analyse.append(f"- Évolution sur la période: {evolution:+.1f}%\n")
        
        if 'taux_marge_brute' in df_financier.columns:
            marge_moyenne = df_financier['taux_marge_brute'].mean()
            analyse.append(f"### Marge brute")
            analyse.append(f"- Taux moyen: {marge_moyenne:.1f}%\n")
        
        analyse.append("### Recommandation")
        analyse.append("Configurez l'API Gemini pour obtenir une analyse détaillée et des recommandations personnalisées.")
        
        return "\n".join(analyse)
    
    def _detection_anomalies_basique(self, df: pd.DataFrame, colonnes: list = None) -> str:
        """Détection d'anomalies basique avec statistiques"""
        if colonnes is None:
            colonnes = df.select_dtypes(include=['number']).columns.tolist()
        
        anomalies = ["## Détection d'anomalies (Mode basique)\n"]
        
        for col in colonnes[:5]:  # Limiter à 5 colonnes
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            borne_inf = q1 - 1.5 * iqr
            borne_sup = q3 + 1.5 * iqr
            
            outliers = df[(df[col] < borne_inf) | (df[col] > borne_sup)]
            
            if len(outliers) > 0:
                anomalies.append(f"### {col}")
                anomalies.append(f"- {len(outliers)} valeur(s) anormale(s) détectée(s)")
                anomalies.append(f"- Plage normale: [{borne_inf:.2f}, {borne_sup:.2f}]\n")
        
        if len(anomalies) == 1:
            anomalies.append("Aucune anomalie statistique majeure détectée.")
        
        return "\n".join(anomalies)
    
    def _analyse_ecarts_basique(self, df: pd.DataFrame) -> str:
        """Analyse des écarts basique"""
        analyse = ["## Analyse des écarts budgétaires (Mode basique)\n"]
        
        if 'ecart' in df.columns and 'categorie' in df.columns:
            ecarts_par_cat = df.groupby('categorie')['ecart'].sum().sort_values()
            
            analyse.append("### Écarts par catégorie")
            for cat, ecart in ecarts_par_cat.items():
                status = "🔴" if ecart > 0 else "🟢"
                analyse.append(f"- {status} {cat}: {ecart:+,.0f} €")
        
        return "\n".join(analyse)
    
    def _prevision_basique(self, df: pd.DataFrame, colonne: str, horizon: int) -> str:
        """Prévision basique par régression linéaire simple"""
        if colonne not in df.columns:
            return "Colonne non trouvée."
        
        valeurs = df[colonne].tail(12).values
        moyenne = valeurs.mean()
        tendance = (valeurs[-1] - valeurs[0]) / (len(valeurs) - 1) if len(valeurs) > 1 else 0
        
        previsions = ["## Prévisions (Mode basique)\n"]
        previsions.append(f"### {colonne}")
        previsions.append(f"- Tendance mensuelle: {tendance:+,.0f}")
        previsions.append(f"\n### Prévisions pour les {horizon} prochains mois:")
        
        for i in range(1, horizon + 1):
            prev = valeurs[-1] + (tendance * i)
            previsions.append(f"- Mois +{i}: {prev:,.0f}")
        
        return "\n".join(previsions)
    
    def _recommandations_generiques(self) -> str:
        """Recommandations génériques sans IA"""
        return """## Recommandations stratégiques (Mode basique)

### Axes d'amélioration prioritaires
1. **Optimisation des coûts**: Analyser les postes de dépenses majeurs
2. **Amélioration de la marge**: Revoir la politique tarifaire
3. **Efficacité opérationnelle**: Identifier les goulots d'étranglement

### Actions recommandées
- Mettre en place un suivi budgétaire mensuel
- Définir des indicateurs de performance clés (KPIs)
- Automatiser le reporting financier

*Configurez l'API Gemini pour des recommandations personnalisées.*"""
    
    def _preparer_contexte_financier(self, df: pd.DataFrame) -> str:
        """Prépare le contexte financier pour l'IA"""
        lignes = []
        
        # Résumé statistique
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            lignes.append(f"{col}: moyenne={df[col].mean():.2f}, min={df[col].min():.2f}, max={df[col].max():.2f}")
        
        lignes.append("\nDernières valeurs:")
        lignes.append(df.tail(3).to_string())
        
        return "\n".join(lignes)
    
    def _preparer_contexte_kpis(self, df: pd.DataFrame) -> str:
        """Prépare le contexte des KPIs pour l'IA"""
        return df.tail(6).to_string()
