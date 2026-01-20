#!/bin/bash

# Configuration - CHANGE THESE
COMPARTMENT_ID="ocid1.compartment.oc1..example"
SUBNET_ID="ocid1.subnet.oc1..example"
SSH_KEY_PATH="~/.ssh/id_rsa.pub"
DISPLAY_NAME="daily-seongsu-instance"
IMAGE_ID="ocid1.image.oc1..example" # Ubuntu 22.04 Minimal or similar
SHAPE="VM.Standard.E2.1.Micro" # Always Free eligible example

echo "Creating OCI Instance..."
oci compute instance launch \
    --availability-domain "AuMN:AP-SEOUL-1-AD-1" \
    --compartment-id $COMPARTMENT_ID \
    --shape $SHAPE \
    --subnet-id $SUBNET_ID \
    --display-name $DISPLAY_NAME \
    --image-id $IMAGE_ID \
    --ssh-authorized-keys-file $SSH_KEY_PATH \
    --assign-public-ip true \
    --wait-for-state RUNNING

echo "Instance created. Getting IP..."
INSTANCE_ID=$(oci compute instance list --compartment-id $COMPARTMENT_ID --display-name $DISPLAY_NAME --query "data[0].id" --raw-output)
PUBLIC_IP=$(oci compute instance list-vnics --instance-id $INSTANCE_ID --query "data[0].\"public-ip\"" --raw-output)

echo "Public IP: $PUBLIC_IP"
echo "You can now SSH into the instance: ssh ubuntu@$PUBLIC_IP"
