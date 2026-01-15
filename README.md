# ACCESSMEIFYOUCAN

Azure Free Tier VM Deployment Repository

## Overview

This repository contains the necessary infrastructure-as-code (IaC) templates and scripts to deploy a Free tier Virtual Machine on Microsoft Azure. It addresses the Azure quota limit issue by providing proper deployment configuration and documentation.

## The Quota Issue

If you're encountering this error:
```
Operation cannot be completed without additional quota.
Additional details - Location:
Current Limit (Free VMs): 0
Current Usage: 0
Amount required for this deployment (Free VMs): 1
(Minimum) New Limit that you should request to enable this deployment: 1.
```

This means your Azure subscription doesn't have quota allocated for VMs in the selected region. Follow the steps below to resolve this.

## Prerequisites

1. **Azure Account**: You need an active Azure subscription
   - Sign up for free at: https://azure.microsoft.com/free/

2. **Azure CLI** (for local deployment)
   - Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

3. **Request Quota Increase**
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to **Subscriptions** → Select your subscription
   - Click **Usage + quotas** in the left menu
   - Search for "**Standard BS Family vCPUs**" or "**Total Regional vCPUs**"
   - Click on the quota and select **Request increase**
   - Request at least **1 vCPU** for your desired region (e.g., East US)
   - Submit the request and wait for approval (usually 1-24 hours)

## Repository Contents

- `azuredeploy.bicep` - Azure Bicep template for VM deployment
- `azuredeploy.parameters.json` - Parameters file for the deployment
- `deploy.sh` - Bash script for easy local deployment
- `.github/workflows/deploy-vm.yml` - GitHub Actions workflow for automated deployment

## Deployment Methods

### Method 1: Local Deployment (Recommended for First-Time Setup)

1. **Clone this repository**:
   ```bash
   git clone https://github.com/ejculp-droid/ACCESSMEIFYOUCAN.git
   cd ACCESSMEIFYOUCAN
   ```

2. **Login to Azure**:
   ```bash
   az login
   ```

3. **Run the deployment script**:
   ```bash
   ./deploy.sh
   ```

4. **Follow the prompts** to configure:
   - Resource group name
   - Azure location (region)
   - VM name
   - Admin username
   - Admin password (minimum 12 characters)

### Method 2: Manual Deployment with Azure CLI

```bash
# Login to Azure
az login

# Create a resource group
az group create --name myResourceGroup --location eastus

# Deploy the VM
az deployment group create \
  --resource-group myResourceGroup \
  --template-file azuredeploy.bicep \
  --parameters vmName=myFreeVM \
               adminUsername=azureuser \
               adminPassword='YourSecurePassword123!'
```

### Method 3: GitHub Actions Deployment

1. **Set up Azure credentials in GitHub**:
   
   a. Create a Service Principal:
   ```bash
   az ad sp create-for-rbac \
     --name "github-actions-sp" \
     --role contributor \
     --scopes /subscriptions/{subscription-id} \
     --sdk-auth
   ```

   b. Copy the entire JSON output

   c. In GitHub, go to **Settings** → **Secrets and variables** → **Actions**

   d. Create the following secrets:
      - `AZURE_CREDENTIALS`: Paste the JSON from step b
      - `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID
      - `VM_ADMIN_USERNAME`: Username for the VM (e.g., azureuser)
      - `VM_ADMIN_PASSWORD`: Strong password for the VM

2. **Trigger the workflow**:
   - Go to **Actions** tab in GitHub
   - Select "Deploy Azure VM" workflow
   - Click "Run workflow"
   - Fill in the parameters and run

## VM Specifications (Free Tier)

- **VM Size**: Standard_B1s (1 vCPU, 1 GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **Storage**: Standard LRS (Locally Redundant Storage)
- **Networking**: Basic Public IP, Virtual Network with NSG

## Security Configuration

The deployment includes:
- Network Security Group (NSG) with rules for SSH (port 22) and HTTP (port 80)
- Password authentication enabled (can be modified for SSH key auth)
- Standard tier networking components

## Connecting to Your VM

After deployment, connect via SSH:
```bash
ssh <admin-username>@<public-ip-address>
```

The public IP address will be displayed at the end of the deployment.

## Cost Considerations

- The **Standard_B1s** VM size is eligible for the Azure Free tier (750 hours/month for 12 months with new accounts)
- After free tier expires or if quota is exceeded, charges apply based on Azure pricing
- Always monitor your Azure spending in the Azure Portal

## Troubleshooting

### Issue: Quota Limit Error

**Solution**: Request quota increase as described in Prerequisites section above.

### Issue: Deployment Failed - Location Not Available

**Solution**: Try a different Azure region. Common regions with good availability:
- East US (eastus)
- West US (westus)
- West Europe (westeurope)

### Issue: Authentication Failed

**Solution**: 
- Run `az login` to re-authenticate
- Verify you have contributor permissions on the subscription

### Issue: VM Not Accessible After Deployment

**Solution**:
- Check NSG rules allow traffic on port 22 (SSH)
- Verify VM is in "Running" state in Azure Portal
- Wait a few minutes after deployment for VM to fully initialize

## Clean Up Resources

To avoid charges, delete the resource group when done:
```bash
az group delete --name myResourceGroup --yes --no-wait
```

Or via Azure Portal:
1. Go to Resource Groups
2. Select your resource group
3. Click "Delete resource group"
4. Type the resource group name to confirm

## Contributing

Feel free to open issues or submit pull requests to improve this deployment setup.

## License

This project is provided as-is for educational and deployment purposes.

## Support

For Azure-specific issues, consult:
- [Azure Documentation](https://docs.microsoft.com/azure/)
- [Azure Support](https://azure.microsoft.com/support/)

For repository issues, please open a GitHub issue.