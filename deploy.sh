#!/bin/bash

# Azure VM Deployment Script
# This script helps deploy the VM to Azure

set -e

echo "==================================="
echo "Azure Free Tier VM Deployment"
echo "==================================="
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed."
    echo "Please install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

echo "✓ Azure CLI is installed"

# Check if logged in to Azure
echo "Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure."
    echo "Please run: az login"
    exit 1
fi

echo "✓ Logged in to Azure"

# Get current subscription
SUBSCRIPTION=$(az account show --query name -o tsv)
echo "Using subscription: $SUBSCRIPTION"
echo ""

# Prompt for resource group name
read -p "Enter resource group name (or press Enter for 'myResourceGroup'): " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-myResourceGroup}

# Prompt for location
read -p "Enter Azure location (or press Enter for 'eastus'): " LOCATION
LOCATION=${LOCATION:-eastus}

# Prompt for VM name
read -p "Enter VM name (or press Enter for 'myFreeVM'): " VM_NAME
VM_NAME=${VM_NAME:-myFreeVM}

# Prompt for admin username
read -p "Enter admin username (or press Enter for 'azureuser'): " ADMIN_USERNAME
ADMIN_USERNAME=${ADMIN_USERNAME:-azureuser}

# Prompt for admin password
echo "Enter admin password (min 12 characters, must include uppercase, lowercase, number, and special character):"
echo "NOTE: Password will not be displayed for security. It's stored temporarily in memory during deployment."
read -s ADMIN_PASSWORD
echo ""

if [ ${#ADMIN_PASSWORD} -lt 12 ]; then
    echo "❌ Password must be at least 12 characters long"
    exit 1
fi

echo ""
echo "==================================="
echo "Deployment Configuration:"
echo "==================================="
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "VM Name: $VM_NAME"
echo "Admin Username: $ADMIN_USERNAME"
echo "VM Size: Standard_B1s (Free tier eligible)"
echo ""

read -p "Do you want to proceed with deployment? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo "Creating resource group..."
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION"

echo ""
echo "Deploying VM... This may take several minutes."
echo ""

# Deploy using Bicep
az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file azuredeploy.bicep \
    --parameters vmName="$VM_NAME" \
                 adminUsername="$ADMIN_USERNAME" \
                 adminPassword="$ADMIN_PASSWORD" \
                 location="$LOCATION"

echo ""
echo "==================================="
echo "Deployment Complete!"
echo "==================================="
echo ""
echo "Getting VM information..."

# Get public IP
PUBLIC_IP=$(az vm show -d \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --query publicIps -o tsv)

echo ""
echo "VM Details:"
echo "  Name: $VM_NAME"
echo "  Public IP: $PUBLIC_IP"
echo "  Username: $ADMIN_USERNAME"
echo ""
echo "To connect via SSH, run:"
echo "  ssh $ADMIN_USERNAME@$PUBLIC_IP"
echo ""
echo "Note: If you encounter quota limit errors, you need to:"
echo "1. Go to Azure Portal -> Subscriptions -> Usage + quotas"
echo "2. Search for 'Standard BS Family vCPUs' or 'Total Regional vCPUs'"
echo "3. Request a quota increase to at least 1 vCPU for your region"
echo "4. Wait for approval (usually takes a few hours to a day)"
echo "5. Re-run this deployment script"
echo ""
