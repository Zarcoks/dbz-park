# Défi 2 - Deployment 3 répliques + Service ClusterIP + kubectl proxy

- `deployment.yaml` : 3 Pods `xhelozs/csc8567:v1`, requests 100m/100Mi, limits 200m/200Mi.
- `service.yaml` : Service ClusterIP port 80 → 5000.
- `commandes.sh` : commandes de vérification et d'accès.
- `schema.md` : schéma de l'infrastructure.
- `reponses.md` : réponses aux questions.

Accès : `kubectl proxy --append-server-path`, puis
http://127.0.0.1:8001/api/v1/namespaces/n-grp1/services/csc8567-defi2/proxy/
