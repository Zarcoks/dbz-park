
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

