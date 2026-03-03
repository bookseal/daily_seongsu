#!/bin/bash
set -e

echo "Stopping Nginx..."
sudo systemctl stop nginx
sudo systemctl disable nginx

echo "Installing K3s..."
# Install with default settings (Traefik enabled)
curl -sfL https://get.k3s.io | sh -

echo "Waiting for K3s to start..."
sleep 30

echo "Configuring kubectl for user..."
mkdir -p /home/ubuntu/.kube
sudo cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
sudo chown ubuntu:ubuntu /home/ubuntu/.kube/config
export KUBECONFIG=/home/ubuntu/.kube/config

echo "Waiting for node to be ready..."
timeout 60s bash -c 'until kubectl get nodes | grep -q "Ready"; do sleep 2; done'

echo "Creating TLS Secret..."
# We use sudo to read the certs, passing content to kubectl
sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml create secret tls tls-secret \
  --cert=/etc/letsencrypt/live/bit-habit.com-0001/fullchain.pem \
  --key=/etc/letsencrypt/live/bit-habit.com-0001/privkey.pem \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Applying manifests..."
kubectl apply -f /home/ubuntu/workspace/daily_seongsu/k3s_migration/

echo "Waiting for pods..."
kubectl wait --for=condition=ready pod -l app=static-web --timeout=60s

echo "Migration completed successfully!"
kubectl get ing
