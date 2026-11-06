# Défi 2 - Schéma d'infrastructure

```mermaid
flowchart LR
  subgraph VM["VM étudiant"]
    B["Navigateur / curl"] -- "HTTP 127.0.0.1:8001<br/>/api/v1/namespaces/n-grp1/services/csc8567-defi2/proxy/" --> KP["kubectl proxy"]
  end
  KP -- "HTTPS 443 + token<br/>/k8s/clusters/local/..." --> R["Rancher<br/>net4255.luxbulb.org"]
  subgraph C["Cluster Kubernetes 'local'"]
    R --> A["kube-apiserver<br/>(proxy de service)"]
    A --> S["Service ClusterIP csc8567-defi2<br/>10.43.105.73:80<br/>selector app=csc8567-defi2"]
    subgraph NS["namespace n-grp1"]
      D["Deployment csc8567-defi2<br/>replicas: 3"] --> RS["ReplicaSet"]
      RS --> P1["Pod 10.42.0.139:5000<br/>kube-master-1"]
      RS --> P2["Pod 10.42.1.4:5000<br/>kube-master-3"]
      RS --> P3["Pod 10.42.3.174:5000<br/>kube-agent-1"]
      S -- "80 → 5000" --> P1
      S --> P2
      S --> P3
    end
  end
```

Chaque Pod : requests 100m CPU / 100Mi, limits 200m CPU / 200Mi.
Réseau Pods : 10.42.0.0/16 (une plage /24 par nœud). Réseau Services : 10.43.0.0/16.
Le ClusterIP n'existe que dans le cluster (règles kube-proxy sur chaque nœud) : depuis la VM on passe par l'API server.
