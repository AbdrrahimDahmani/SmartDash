# 🧪 Guide de Test - Scénarios de Démonstration

## Fichiers de Test Fournis

Les fichiers suivants sont disponibles dans le dossier `donnees_test/` :

| Fichier                        | Description                    | Anomalies incluses                            |
| ------------------------------ | ------------------------------ | --------------------------------------------- |
| `donnees_financieres_test.csv` | Données financières mensuelles | Mai et Novembre : coûts anormalement élevés   |
| `couts_detailles_test.csv`     | Coûts par catégorie et centre  | Mai : dépassements budgétaires significatifs  |
| `kpis_operationnels_test.csv`  | KPIs de performance            | Mai et Novembre : dégradation des indicateurs |

---

## 📋 Scénario 1 : Détection d'Anomalies Financières

### Objectif

Tester la capacité du système à détecter des anomalies dans les données financières.

### Étapes

1. **Lancer l'application**

   ```bash
   cd /home/aboud/Desktop/2025-2026/AMIFI/projet
   source venv/bin/activate
   streamlit run app.py
   ```

2. **Charger les données de test**

   - Dans la **sidebar gauche**, section "📁 Importer des données"
   - Cliquer sur "Browse files"
   - Sélectionner `donnees_test/donnees_financieres_test.csv`
   - ✅ Message "12 lignes chargées" doit apparaître

3. **Aller à l'onglet "🔍 Détection Anomalies"**

   - Observer les métriques : des outliers devraient être détectés
   - Consulter les onglets "Outliers Statistiques" et "Ruptures de Tendance"

4. **Lancer l'analyse IA** (si clé API configurée)
   - Cliquer sur "Analyser avec Gemini AI"
   - L'IA devrait identifier les mois de **Mai** et **Novembre** comme problématiques

### Résultat Attendu

- **Mai 2025** : Coûts variables à 294 000 € (60% du CA au lieu de 45%)
- **Novembre 2025** : Coûts variables à 406 000 € (70% du CA - anomalie majeure)
- Alertes générées pour marge brute insuffisante

---

## 📋 Scénario 2 : Analyse des Écarts Budgétaires

### Objectif

Analyser les dépassements budgétaires par catégorie de coûts.

### Étapes

1. **Charger le fichier de coûts**

   - Uploader `donnees_test/couts_detailles_test.csv`

2. **Aller à l'onglet "💰 Analyse des Coûts"**

   - Observer le graphique des écarts budgétaires
   - Les barres rouges indiquent les dépassements

3. **Identifier les catégories problématiques**

   - **Matières premières** : +50% en Mai (180 000 € vs 120 000 €)
   - **Frais généraux** : Dépassements récurrents

4. **Consulter l'aide à la décision IA**
   - Onglet "🎯 Aide à la Décision IA"
   - Section "📋 Recommandations"
   - Demander une analyse des écarts

### Questions à poser au Chat IA

```
- "Quelles sont les causes possibles du dépassement des matières premières en Mai ?"
- "Comment optimiser les frais généraux de production ?"
- "Quelles actions correctives recommandes-tu pour le mois de Mai ?"
```

---

## 📋 Scénario 3 : Suivi des KPIs et Alertes

### Objectif

Tester le système d'alertes basé sur les seuils de KPIs.

### Étapes

1. **Charger les KPIs**

   - Uploader `donnees_test/kpis_operationnels_test.csv`

2. **Observer la Vue d'Ensemble**

   - Des alertes devraient apparaître pour les mois problématiques
   - Le "Score de Santé" devrait refléter la performance

3. **Aller à l'onglet "📈 KPIs Opérationnels"**

   - Observer les jauges de satisfaction client et taux de service
   - Analyser les graphiques d'évolution

4. **Identifier les dégradations**
   - **Mai** : Taux d'occupation à 65%, taux de rebut à 4.8%
   - **Novembre** : Délai livraison à 7.2 jours, taux service à 89.5%

### Résultat Attendu

- Alertes rouges pour les KPIs sous les seuils
- Corrélation visible entre les problèmes financiers et opérationnels

---

## 📋 Scénario 4 : Prévisions avec IA

### Objectif

Générer des prévisions financières et des recommandations.

### Étapes

1. **S'assurer que l'API Gemini est configurée**

   - Sidebar → Entrer la clé API
   - Vérifier le message "✅ API configurée"

2. **Aller à "🎯 Aide à la Décision IA"**

3. **Onglet "💰 Prévisions"**

   - Sélectionner "chiffre_affaires" comme indicateur
   - Définir un horizon de 3 mois
   - Cliquer sur "📈 Générer les prévisions"

4. **Analyser les résultats**

   - Tendance identifiée
   - Scénarios optimiste/réaliste/pessimiste
   - Facteurs de risque

5. **Onglet "📊 Analyse Globale"**
   - Lancer l'analyse complète
   - Obtenir une synthèse de la performance

---

## 📋 Scénario 5 : Chat Interactif

### Objectif

Tester le chat IA pour l'aide à la décision.

### Questions suggérées

```
1. "Analyse la performance du mois de Mai et explique les problèmes"

2. "Quels sont les 3 axes d'amélioration prioritaires pour cette entreprise ?"

3. "Comment améliorer le taux de marge brute ?"

4. "Prépare un plan d'action pour réduire les coûts variables"

5. "Quels KPIs devrais-je surveiller en priorité ?"

6. "Compare la performance de Novembre avec la moyenne de l'année"
```

---

## 🎯 Anomalies Cachées dans les Données

Pour vérifier que le système fonctionne, voici les anomalies intentionnellement placées :

### donnees_financieres_test.csv

| Mois          | Anomalie                             | Impact                         |
| ------------- | ------------------------------------ | ------------------------------ |
| Mai 2025      | Coûts variables à 294 000 € (60% CA) | Marge brute 40% → insuffisante |
| Novembre 2025 | Coûts variables à 406 000 € (70% CA) | Marge brute 30% → critique     |

### kpis_operationnels_test.csv

| Mois          | Anomalies                                           |
| ------------- | --------------------------------------------------- |
| Mai 2025      | Taux occupation 65%, Rebut 4.8%, Satisfaction 6.1   |
| Novembre 2025 | Délai 7.2j, Taux service 89.5%, Rotation stocks 6.0 |

### couts_detailles_test.csv

| Mois     | Dépassements majeurs                                  |
| -------- | ----------------------------------------------------- |
| Mai 2025 | Matières +50%, Main d'œuvre +19%, Frais généraux +38% |

---

## ✅ Critères de Succès

Le test est réussi si :

1. ☐ Les fichiers CSV sont correctement importés
2. ☐ Les graphiques affichent les données uploadées
3. ☐ Les anomalies de Mai et Novembre sont détectées
4. ☐ Les alertes s'affichent pour les KPIs hors seuils
5. ☐ L'IA génère des analyses pertinentes (si configurée)
6. ☐ Le chat répond aux questions sur les données
7. ☐ Les prévisions sont cohérentes avec les tendances

---

## 🔧 Dépannage

| Problème                   | Solution                                      |
| -------------------------- | --------------------------------------------- |
| "Erreur de chargement CSV" | Vérifier l'encodage UTF-8 du fichier          |
| "API non configurée"       | Entrer la clé Gemini dans la sidebar          |
| Graphiques vides           | Régénérer les données ou recharger le fichier |
| Erreur Streamlit           | Relancer avec `streamlit run app.py`          |
