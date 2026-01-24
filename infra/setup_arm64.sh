#!/bin/bash
set -e

# Update and install basic tools
echo "Updating system..."
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    vim \
    unzip \
    jq

# Install Docker (Official Docker Repo)
echo "Installing Docker..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Enable Docker for non-root user (ubuntu)
sudo usermod -aG docker ubuntu

# Install Docker Compose (Standalone) - Optional as plugin is installed above, but good for compatibility
# Note: For ARM64, we need to fetch the correct binary if not using plugin
# Using the plugin `docker compose` is recommended now, but aliasing for `docker-compose` legacy support
echo 'alias docker-compose="docker compose"' >> ~/.bashrc

# Install Python 3.10+ and pip if not present (Ubuntu 22.04 comes with 3.10)
echo "Installing Python and dependencies..."
sudo apt-get install -y python3-pip python3-venv

# OCI CLI Installation
# https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm
# usage of the raw install script which detects arch
echo "Installing OCI CLI..."
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)" -- --accept-all-defaults

echo "Setup Complete! Please logout and login again for group changes to take effect."
