# Web Services Architecture Snapshot

**Date:** 2026-03-12  
**Time:** 09:00 KST (00:00 UTC)  
**Status:** All services migrated to k3s (Kubernetes). No Nginx or Docker on host.

---

## Big Picture

```
Internet
   │
   ▼
Oracle Cloud VM  (158.180.71.122 / 10.0.0.61)
   │
   ├── Port 80  → k3s Traefik  (HTTP, redirects to HTTPS)
   └── Port 443 → k3s Traefik  (HTTPS, TLS terminated here)
                      │
                      │  Routes by hostname
                      ▼
             ┌─────────────────────────────────────────┐
             │         k3s Cluster (default namespace)  │
             │                                          │
             │  Ingress → ClusterIP Service → Pod       │
             └─────────────────────────────────────────┘
```

TLS certificate: wildcard `*.bit-habit.com` managed by **cert-manager** (Let's Encrypt).

---

## Routing Table (Ingress → Service → Pod)

| Domain | Service | Pod | Image | Container Port |
|---|---|---|---|---|
| `bit-habit.com` | `static-web-svc` | `static-web` | `nginx:alpine` | 80 |
| `www.bit-habit.com` | `static-web-svc` | `static-web` | `nginx:alpine` | 80 |
| `blog.bit-habit.com` | `ghost-svc` | `ghost` | `ghost:5-alpine` | 2368 |
| `booktoss.bit-habit.com` | `booktoss-svc` | `booktoss` | `booktoss:latest` | 8000 |
| `code-server.bit-habit.com` | `code-server-svc` | `code-server` | `codercom/code-server` | 8080 |
| `daily-seongsu.bit-habit.com` | `daily-seongsu-svc` | `daily-seongsu` | custom | 8000 |
| `habit.bit-habit.com` | `static-web-svc` | `static-web` | `nginx:alpine` | 80 |
| `habit.bit-habit.com/api/` | `bithabit-api-svc` | `bithabit-api` | `bithabit-api:latest` | 8000 |
| `seoul-apt.bit-habit.com` | `seoul-apt-price` | `seoul-apt-price` | custom | 8000 |
| `startpage.bit-habit.com` | `startpage-svc` | `startpage` | `startpage:latest` | 8000 |
| `viz.bit-habit.com` | `viz-platform-svc` | `viz-platform` | `viz-bit-habit:latest` | 8501 |
| `wiki.bit-habit.com` | `wikijs-svc` | `wikijs` | `requarks/wiki:2` | 3000 |

> All ClusterIP services expose port **80** internally, regardless of the container port.  
> No host ports are used. All inter-service communication goes through Kubernetes Service names.

---

## Pod Dependency Map

```
ghost          ──relies on──▶  ghost-mysql     (MySQL 8.0, port 3306)
                               └─ Data: /home/ubuntu/workspace/ghost-data/mysql (hostPath)

wikijs         ──relies on──▶  wikijs-db       (PostgreSQL 17, port 5432)
                               └─ Data: /home/ubuntu/workspace/wikijs-data/db (hostPath)

bithabit-api   ──standalone──  SQLite DB at /home/ubuntu/workspace/bithabit_api/data/bithabit.db
                               GIF uploads at /home/ubuntu/workspace/bithabit_api/data/uploads

startpage      ──standalone──  links.json at /home/ubuntu/workspace/my-start-page/data/

booktoss       ──relies on──▶  OpenAI / Kakao API  (env from k8s Secret: booktoss-env)

code-server    ──standalone──  Workspace: /home/ubuntu/workspace (hostPath, live mount)
```

---

## All Running Pods (Snapshot)

```
NAME                              READY   STATUS    NODE
bithabit-api-658554f99c-sszrg     1/1     Running   bithabit
booktoss-67c44fd8d7-zmdzt         1/1     Running   bithabit
code-server-747675dcf9-mrhwt      1/1     Running   bithabit
daily-seongsu-5f6c5d87d7-lzwgf    1/1     Running   bithabit
ghost-656bcc8955-qtc82            1/1     Running   bithabit
ghost-mysql-67689688f6-6c88k      1/1     Running   bithabit
seoul-apt-price-5b679c6bb-622nb   1/1     Running   bithabit
startpage-7fc4579877-4skxn        1/1     Running   bithabit
static-web-7859bcfd4f-hqvq5       1/1     Running   bithabit
viz-platform-77b8974859-n8vxr     1/1     Running   bithabit
wikijs-67c496c9b8-fj46c           1/1     Running   bithabit
wikijs-db-778645dff4-rfqrz        1/1     Running   bithabit
```

---

## Ingress Resources

| Name | Hosts | Special Rule |
|---|---|---|
| `main-ingress` | All domains listed above | Standard TLS routing |
| `habit-api-ingress` | `habit.bit-habit.com/api/` | Strips `/api` prefix via Traefik Middleware before forwarding to `bithabit-api-svc` |
| `seoul-apt-price-ingress` | `seoul-apt.bit-habit.com` | Standard TLS routing |

---

## Kubernetes Config Files Location

```
/home/ubuntu/workspace/daily_seongsu/infra/k8s-global/
├── ingress.yaml              # All Ingress rules (main + habit-api)
├── bithabit-api.yaml         # Deployment + Service
├── startpage.yaml            # Deployment + Service
├── booktoss.yaml             # Deployment + Service
├── viz-platform.yaml         # Deployment + Service
├── wikijs.yaml               # Deployment + Service (wiki + postgres)
├── ghost.yaml                # Deployment + Service (ghost + mysql)
├── code-server.yaml          # Deployment + Service
└── strip-api-middleware.yaml # Traefik Middleware for /api prefix
```

---

## What Was Shut Down

All of these are now **inactive and disabled**:

| Service | Was Running As | Port Was |
|---|---|---|
| `bithabit-api` | systemd | 8002 |
| `startpage` | systemd | 8000 |
| `ghost` | systemd (ghost CLI) | 2368 |
| `code-server@ubuntu` | systemd | 8081 |
| `mysql` | systemd | 3306 |
| `docker` | systemd daemon | — |
| `wikijs` + `postgres` | Docker Compose | 3001/5432 |
| `viz-platform` | Docker container | 8503 |
| `nginx` | apt package | — (fully removed) |

---

## Disk Usage (Snapshot)

```
Filesystem: /dev/sda1  Total: 97G  Used: 60G  Free: 37G  (62%)

Major consumers:
  /var/lib/rancher/k3s/   17G   (k3s images + etcd)
  /var/lib/docker/        23G   (old Docker, can be pruned)
```

> Docker images are still on disk but the daemon is stopped.  
> Run `sudo docker system prune -af` to reclaim ~10GB if needed.

---

## How to Manage Services

```bash
# View all pods
kubectl get pods

# Restart a service (e.g. bithabit-api)
kubectl rollout restart deployment bithabit-api

# View logs
kubectl logs -f deployment/ghost

# Apply config changes
kubectl apply -f /home/ubuntu/workspace/daily_seongsu/infra/k8s-global/ghost.yaml
```
