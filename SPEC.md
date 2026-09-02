
# Spécifications Logicielles & Cahier des Charges Fonctionnel
**Nom du projet :** FastLine Evry  
**Livrable :** Rendu Séance 5 (30 septembre - 13h15)  
**Cible :** Application Web Cross-platform (Mobile-First)  

---

## 1. Contexte & Cadrage Métier

* **Secteur :** Parc d'attractions (jauge max : 10 000 visiteurs simultanés).
* **Localisation :** Boulevard des Coquibus, Évry.
* **Horaires :**
  * **Parc :** 08h00 – 20h00.
  * **Attractions :** 09h00 – 21h00 (fermeture des inscriptions aux files virtuelles dès 19h00 pour éviter tout débordement).
* **Problématique :** Temps d'attente physique pouvant atteindre jusqu'à 5 heures en pic d'affluence.
* **Objectif :** Mise en place d'une file d'attente virtuelle journalière, fluide, scalable, sans sur-ingénierie (*no over-engineering*), réinitialisée chaque soir.

---

## 2. Règles Métier & Gestion des Files

### 2.1. Paramètres d'une Attraction
* **Capacité par cycle :** 50 places assises / tour (ex. *Salle du Temps*).
* **Durée d'un cycle :** 30 secondes à 1 minute de manège + temps d'embarquement / débarquement (*onboarding / offboarding*).
* **Typologie :** Extrême, Normale, Lente (avec restrictions physiques et santé associées).
* **Mode d'inscription :** *Single Rider* (file individuelle nominative).

### 2.2. Algorithme d'Ordonnancement selon la Tarification
1. **Super Sayan :** Coupe-file absolu. Insertion directe en tête de file (temps d'attente = 0 min).
2. **Sayan :** File prioritaire alternée avec temps d'attente maximum garanti $\le$ 30 minutes.
3. **Simple Mortel (Human) :** File standard traitée par ordre d'arrivée (*FIFO*).

### 2.3. Modulateurs d'Affluence
Le temps d'attente estimé applique des coefficients dynamiques calculés selon :
* Données des capteurs de flux temps réel.
* Calendrier : Vacances scolaires (Zone C) et week-ends / jours fériés.
* Conditions météorologiques (pluie, canicule, orage).

### 2.4. Présentation, Tolérance et Désistement
* **Fenêtre de présentation (*Grace Period*) :** Entre 30 secondes et 5 minutes après l'appel.
* **No-show :** En cas de non-présentation dans le délai imparti, le ticket expire, la place est libérée et la file avance.
* **Désistement volontaire :** L'utilisateur peut quitter la file à tout moment via l'interface.

### 2.5. Gestion des Incidents
* **Arrêt d'urgence :** Gel instantané de la file par l'administrateur avec saisie du motif et de la durée estimée.
* **Envoi d'une alerte :** Notification *Broadcast* envoyée à tous les inscrits de l'attraction.
* **Règle de rétention :**
  * Incident $< 1$ journée : Les positions dans la file d'attente sont conservées.
  * Incident $\ge 1$ journée : La file d'attente est purgée.

---

## 3. Parcours Utilisateurs (Flows)
[Visiteur] Achat billet (en ligne / guichet) │ ▼ [Visiteur] Création de compte & validation CGU (RGPD) │ ▼ [Visiteur] Saisie code billet unique + Selfie instantané de vérification │ ▼ [Visiteur] Sélection attraction -> Contrôle santé/taille -> Entrée en file virtuelle │ ▼ [Système] Notifications Push : T - 15 min -> Appel au tour │ ▼ [Visiteur] Présentation à la borne : Scan QR Code secret dynamique


---

## 4. Backlog Produit & Priorisation

### 4.1. Espace Client (Visiteur)

| Thème | Spécification | Valeur (1 = Max) | Effort (1 à 5) |
| :--- | :--- | :---: | :---: |
| **Authentification & RGPD** | Saisie nom, email, mot de passe, validation des CGU et capture d'un selfie instantané (uniquement pendant la saisie du code ticket pour contrôle d'accès). Code de validation envoyé par email. | 1 | 1 |
| **Notifications** | Système Push :<br>1. *Personnelle* : Alerte 15 min avant le passage et au moment de l'appel.<br>2. *Broadcast* : Alertes météo et incidents. | 1 | 2 |
| **Catalogue Attractions** | Consultation des attractions, restrictions médicales/tailles, et temps d'attente prévisionnel. | 1 | 2 |
| **Rejoindre une file** | Inscription en file virtuelle selon la catégorie du ticket, contrôle de position et bouton de désistement. | 1 | 2 |
| **Validation d'accès** | Génération d'un QR code secret dynamique lors de l'appel pour vérification sur borne. | 1 | 2 |
| **Assignation Ticket** | Champ de saisie du numéro de ticket unique pour charger les privilèges (Human, Sayan, Super Sayan). | 2 | 1 |
| **Indicateur de Flux** | Affichage de la jauge globale d'affluence du parc en temps réel. | 3 | 2 |
| **Passerelle Paiement** | Achat de billets et surclassement directement dans l'application (*Payment Gateway*). | 4 | 4 |

### 4.2. Espace Administrateur

| Thème | Spécification | Valeur (1 = Max) | Effort (1 à 5) |
| :--- | :--- | :---: | :---: |
| **Gestion des Utilisateurs** | Recherche, modification, suppression de comptes et contrôle manuel de validité des tickets. | 1 | 2 |
| **Gestion des Attractions** | CRUD complet : nom, durée du tour, temps onboarding/offboarding, capacité max par tour, catégorie (extrême, normale, lente). | 1 | 2 |
| **Déclaration d'Incident** | Déclencheur d'incident avec sélection de durée estimée, gel de file et broadcast automatique. | 1 | 1 |
| **Filtres de File** | Visualisation et réorganisation d'urgence des files d'attente par attraction. | 4 | 3 |
| **Tableaux d'Analyse (KPI)** | Tableaux de bord de supervision :<br>- Fréquentation par heure.<br>- Taux de remplissage et d'attente par attraction.<br>- Répartition démographique (tranches d'âge, genre). | 4 | 3 |

---

## 5. Spécifications Non Fonctionnelles

* **Ergonomie & Accessibilité :** Web responsive optimisé mobile (*Mobile-First*), compatible iOS et Android sans installation native obligatoire.
* **Performance & Scalabilité :** Prise en charge d'un volume de 10 000 visiteurs actifs par jour avec latence de rafraîchissement d'état $< 1$ s.
* **Sécurité & RGPD :**
  * Consentement explicite CGU dès la création de compte.
  * Chiffrement des mots de passe et données personnelles.
  * Pas de conservation des selfies au-delà de la journée d'exploitation.
* **Cycle de Vie des Données :** Purge quotidienne automatique des files et des tickets à 21h00 (validité strictement journalière).


	Seth JUNIOR
1A FISA
www.telecom-sudparis.eu
	
