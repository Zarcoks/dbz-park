#!/usr/bin/env bash
# Défi 2 - commandes exécutées (namespace par défaut du contexte : n-grp1)

# Créer/mettre à jour le Deployment (3 répliques + ressources) et le Service ClusterIP
kubectl apply -f deployment.yaml -f service.yaml

# Attendre les 3 Pods, puis vérifier Pods (IP, nœud), Service et ressources
kubectl rollout status deployment/csc8567-defi2
kubectl get pods -l app=csc8567-defi2 -o wide
kubectl get svc csc8567-defi2
kubectl get pod -l app=csc8567-defi2 -o jsonpath='{.items[0].spec.containers[0].resources}'

# Proxy local vers l'API server.
# --append-server-path : nécessaire car Rancher expose le cluster sous /k8s/clusters/local
kubectl proxy --append-server-path

# (autre terminal) Accès au site via le proxy de service de l'API
curl http://127.0.0.1:8001/api/v1/namespaces/n-grp1/services/csc8567-defi2/proxy/

# Vérifier la répartition des requêtes entre les 3 Pods
for p in $(kubectl get pods -l app=csc8567-defi2 -o name); do echo "$p: $(kubectl logs $p | grep -c 'GET /')"; done
