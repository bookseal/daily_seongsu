# K3s Migration & System Architecture Guide

This guide explains how we migrated your system from a traditional Nginx web server to a K3s (lightweight Kubernetes) cluster. It details the architecture, installation process, and key configuration changes.

## 1. System Architecture: From Nginx to K3s

### Before (Nginx Native)

The traditional setup relied on `nginx` running as a system service on ports 80 and 443. It acted as a reverse proxy, forwarding requests to various applications running on `localhost` (e.g., Streamlit on 8501, Ghost on 2368).

```mermaid
graph LR
    User --> Nginx[Native Nginx :80/:443]
    Nginx --> Static[/var/www/html]
    Nginx --> App1[Streamlit :8501]
    Nginx --> App2[Ghost :2368]
```

### After (K3s Cluster)

We replaced the native Nginx service with **K3s**, a lightweight Kubernetes distribution. K3s includes **Traefik**, an Ingress Controller that handles incoming traffic on ports 80/443.

Instead of one big `nginx.conf` file, the configuration is now split into Kubernetes resources:

1.  **Ingress (Traefik)**: Replaces `server {}` blocks. Routes traffic based on domain names.
2.  **Services & Endpoints**: Act as the "bridge" to applications running on the host machine.
3.  **Deployment (Nginx Pod)**: Replaces `root /var/www/...` directives. A containerized Nginx serves static files.

```mermaid
graph LR
    User --> Traefik[Traefik Ingress :80/:443]
    Traefik --> Ingress[Ingress Rules]
    Ingress -- k8s service --> NginxPod[Static Web Pod]
    Ingress -- k8s service --> Endpoint[Host Service]
    Endpoint --> App1[Streamlit (Host) :8501]
    Endpoint --> App2[Ghost (Host) :2368]
```

---

## 2. Installation History

We performed the following steps to set up K3s:

### Step 1: Stop Native Nginx

Since K3s (Traefik) needs ports 80 and 443, we had to stop the existing web server.

```bash
sudo systemctl stop nginx
sudo systemctl disable nginx
# Also removed a conflicting docker container (nginx-proxy-manager)
```

### Step 2: Install K3s

We installed K3s using the official script. This sets up the control plane, worker node, and tools like `kubectl` and `crictl`.

```bash
curl -sfL https://get.k3s.io | sh -
```

### Step 3: Configure Access

We copied the admin config so your user (`ubuntu`) can run `kubectl` commands.

```bash
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown ubuntu:ubuntu ~/.kube/config
echo 'export KUBECONFIG=~/.kube/config' >> ~/.bashrc
```

### Step 4: Import SSL Certificates

We took your existing Let's Encrypt certificates (`/etc/letsencrypt/live/bit-habit.com-0001/`) and created a Kubernetes Secret. This allows Traefik to terminate SSL.

```bash
kubectl create secret tls tls-secret \
  --cert=/etc/letsencrypt/live/bit-habit.com-0001/fullchain.pem \
  --key=/etc/letsencrypt/live/bit-habit.com-0001/privkey.pem
```

---

## 3. Configuration Breakdown

All Kubernetes manifests are located in: `/home/ubuntu/workspace/daily_seongsu/infra/`

### A. Connectivity to Host Apps (`02-external-services.yaml`)

This is the most critical part for your setup. Since your apps (Streamlit, Ghost, Wiki) run on the host machine (outside the cluster), we created **Services** without selectors and manually defined **Endpoints** pointing to the host IP (`10.0.0.61`).

**Example:**

```yaml
kind: Service
metadata:
  name: blog-svc # The internal K8s DNS name
spec:
  ports:
    - port: 80
      targetPort: 2368 # The port Ghost listens on
---
kind: Endpoints
metadata:
  name: blog-svc
subsets:
  - addresses:
      - ip: 10.0.0.61 # The Host IP
    ports:
      - port: 2368
```

### B. Static Content Serving (`03-static-deployment.yaml`)

To serve static files (`/var/www/html`, etc.), we deployed a standard Nginx **Pod**. We used `hostPath` volumes to mount your existing directories into the container.

- **ConfigMap**: Contains the `nginx.conf` for this specific pod.
- **Deployment**: Runs the Nginx container with volume mounts.
- **Service**: Exposes the pod internally on port 80.

### C. Routing Rules (`04-ingress.yaml`)

This file defines which domain goes to which service. It replaces your `/etc/nginx/sites-enabled/*.conf` files.

- **TL/DR**: "If request matches `blog.bit-habit.com`, send to `blog-svc`."
- It uses the `tls-secret` for HTTPS.

---

## 4. The "Binding" Issue (Important!)

During migration, many services (Ghost, Startpage, Booktoss) failed to connect.
**Why?**

- **Original**: Configured to listen on `127.0.0.1` (localhost). This was fine when Nginx was also on localhost.
- **Problem**: K3s pods run in their own network namespace. They cannot reach `127.0.0.1` on the host. They reach the host via its valid IP (`10.0.0.61`).
- **Fix**: We updated all services to listen on `0.0.0.0` (all interfaces) so they accept traffic from the K3s network.

**Changes Made:**

1.  **Booktoss**: Updated `run.sh` script.
2.  **Startpage**: Updated `startpage.service` systemd file.
3.  **Wiki**: Updated `docker-compose.yml`.
4.  **Ghost**: Updated `config.production.json` (`"host": "0.0.0.0"`).
5.  **Viz**: Started missing `docker-compose` service.

---

## 5. Exploring with K9s

You now have `k9s` installed! It's an interactive terminal UI for Kubernetes.

**Launch:**

```bash
k9s
```

**Cheatsheet:**

- **`:pods`** (or just `0`): View all pods. You'll see `static-web` here.
- **`:svc`**: View services. You'll see `blog-svc`, `wiki-svc`, etc.
- **`:ing`**: View Ingress (routing) rules.
- **`/`**: Search filter (e.g., type `/blog` to find blog resources).
- **`l`**: View logs of a selected pod.
- **`s`**: Shell into a selected pod.
- **`d`**: Describe a resource (view details/events).
- **`Ctrl-c`**: Quit.

---

## 6. How to Update

### Updating Websites

- **Static Content**: Just edit files in `/var/www/html` as usual. The Nginx pod sees them instantly via volume mount.
- **Apps**: Restart them via `systemctl` or `docker` on the host as usual. K3s will just reconnect.

### Updating Routing (Ingress)

1.  Edit `/home/ubuntu/workspace/daily_seongsu/infra/k8s-global/ingress.yaml`.
2.  Apply changes:
    ```bash
    kubectl apply -f /home/ubuntu/workspace/daily_seongsu/infra/k8s-global/ingress.yaml
    ```
