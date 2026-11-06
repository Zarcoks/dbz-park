# Défi 1 - Schéma d'infrastructure

```mermaid
flowchart LR
  subgraph VM["VM étudiant (Ubuntu)"]
    B["Navigateur / curl<br/>localhost:8080"] --> K["kubectl port-forward<br/>127.0.0.1:8080"]
  end
  K -- "HTTPS 443 (WebSocket/SPDY)<br/>token kubeconfig" --> R["Rancher<br/>net4255.luxbulb.org<br/>/k8s/clusters/local"]
  subgraph C["Cluster Kubernetes 'local'"]
    R --> A["kube-apiserver"]
    A -- "stream port-forward" --> KL["kubelet<br/>nœud kube-master-2"]
    subgraph NS["namespace n-grp1"]
      D["Deployment csc8567-defi1"] --> RS["ReplicaSet"] --> P["Pod 10.42.2.160<br/>conteneur xhelozs/csc8567:v1<br/>Flask :5000"]
    end
    KL --> P
  end
  P -. "pull image" .-> H["Docker Hub"]
```

Chemin d'une requête : navigateur → `kubectl port-forward` (localhost:8080) → Rancher (proxy API, HTTPS) → kube-apiserver → kubelet du nœud → conteneur du Pod (port 5000).
Aucun Service n'est utilisé : le Pod n'est joignable que via ce tunnel.
