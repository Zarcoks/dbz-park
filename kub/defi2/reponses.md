# Défi 2 - Réponses

## 1. Quel est le but d'un service ?
Les Pods sont éphémères : à chaque recréation ils changent d'IP, et un Deployment en a plusieurs.
Un Service donne un point d'accès **stable** (IP virtuelle + nom DNS `csc8567-defi2.n-grp1.svc.cluster.local`)
devant un **groupe de Pods choisi par label** (`selector`). Il suit automatiquement les Pods prêts (endpoints)
et **répartit la charge** entre eux. Les clients n'ont plus à connaître les Pods.

## 2. Différence entre ClusterIP et NodePort ?
- **ClusterIP** (par défaut) : IP virtuelle joignable **seulement depuis l'intérieur du cluster**.
  Pour y accéder de l'extérieur il faut un intermédiaire (kubectl proxy / port-forward, Ingress).
- **NodePort** : ClusterIP **+** un port fixe (30000-32767) ouvert sur **chaque nœud**.
  Le service est joignable de l'extérieur via `IP_d'un_nœud:NodePort`, puis redirigé vers les Pods.

## 3. Schéma
Voir `schema.md`.
