#!/bin/bash

# Open ports 80, 443, 8501
PORTS=(80 443 8501)

echo "Configuring iptables..."

# Flush existing rules might be dangerous if on remote, so just appending
for PORT in "${PORTS[@]}"; do
    if ! sudo iptables -C INPUT -p tcp --dport $PORT -j ACCEPT 2>/dev/null; then
        sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport $PORT -j ACCEPT
        echo "Opened port $PORT on iptables"
    else
        echo "Port $PORT already open on iptables"
    fi
done

# Save iptables rules (Persist across reboots)
# Note: This interaction might vary by distro, assuming standard netfilter-persistent
sudo apt-get install -y iptables-persistent
sudo netfilter-persistent save

# If firewalld is active (common in Oracle Linux, less common in standard Ubuntu images on OCI but possible)
if systemctl is-active --quiet firewalld; then
    echo "Configuring firewalld..."
    for PORT in "${PORTS[@]}"; do
        sudo firewall-cmd --permanent --zone=public --add-port=${PORT}/tcp
    done
    sudo firewall-cmd --reload
fi

echo "Network configuration complete (Instance Level)."
echo "IMPORTANT: Ensure you have also added Ingress Rules in your OCI VCN Security List:"
echo "  - Source: 0.0.0.0/0"
echo "  - Protocol: TCP"
echo "  - Destination Port Range: 80, 443, 8501"
