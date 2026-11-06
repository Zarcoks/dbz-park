#!/usr/bin/env bash
# Défi 1 - Premiers pas sur Kubernetes
# Commandes exécutées ligne par ligne (VM Ubuntu arm64, cluster net4255.luxbulb.org)

# --- Préparation du poste ---
# Installer kubectl (binaire officiel arm64) dans ~/.local/bin
V=$(wget -qO- https://dl.k8s.io/release/stable.txt)
wget https://dl.k8s.io/release/$V/bin/linux/arm64/kubectl -P ~/.local/bin && chmod +x ~/.local/bin/kubectl

# Kubeconfig téléchargé depuis Rancher (Cluster Management > local > Download KubeConfig)
mkdir -p ~/.kube
cp ~/Downloads/local.yaml ~/.kube/config
chmod 600 ~/.kube/config

# Le serveur présente le certificat auto-signé par défaut d'ingress-nginx (CN ingress.local) :
# on épingle ce certificat comme CA de confiance (TLS reste vérifié)
echo | openssl s_client -connect net4255.luxbulb.org:443 -servername net4255.luxbulb.org 2>/dev/null | openssl x509 > ~/.kube/luxbulb.crt
kubectl config set-cluster local --certificate-authority=$HOME/.kube/luxbulb.crt --embed-certs=true --tls-server-name=ingress.local

# Notre espace de noms est n-grp1 : on le met par défaut dans le contexte
kubectl config set-context --current --namespace=n-grp1

# --- Défi 1 ---
# Créer le Deployment (-> ReplicaSet -> 1 Pod) avec l'image du cours
kubectl create deployment csc8567-defi1 --image=xhelozs/csc8567:v1

# Attendre que le Pod soit prêt, puis l'afficher (nom, IP, nœud)
kubectl rollout status deployment/csc8567-defi1
kubectl get pods -l app=csc8567-defi1 -o wide

# Récupérer le nom du Pod
POD=$(kubectl get pods -l app=csc8567-defi1 -o jsonpath='{.items[0].metadata.name}')

# Tunnel localhost:8080 -> port 5000 du Pod (Flask), via l'API server
kubectl port-forward pods/$POD 8080:5000

# (autre terminal) Tester le site, puis lire les logs Flask
curl http://localhost:8080/
kubectl logs $POD
