# Azure Quota Increase Guide

## Understanding the Quota Error

When you see this error:
```
Operation cannot be completed without additional quota.
Additional details - Location:
Current Limit (Free VMs): 0
Current Usage: 0
Amount required for this deployment (Free VMs): 1
(Minimum) New Limit that you should request to enable this deployment: 1.
```

This means your Azure subscription has **zero quota** allocated for Virtual Machines in the region you're trying to deploy to.

## Why This Happens

1. **New Azure Subscription**: Free tier or new subscriptions often start with 0 VM quota for security/cost control
2. **Regional Restrictions**: Some regions may have quota restrictions
3. **Subscription Type**: Certain subscription types (free, student, etc.) require explicit quota requests

## Step-by-Step: Request Quota Increase

### Option 1: Azure Portal (Easiest)

1. **Login to Azure Portal**
   - Go to https://portal.azure.com
   - Sign in with your Azure account

2. **Navigate to Quotas**
   - Click on "Subscriptions" in the left menu (or search for it)
   - Select your subscription
   - Click "Usage + quotas" in the left sidebar

3. **Find the Right Quota**
   - In the search box, type: `Standard BS Family vCPUs`
   - Or search for: `Total Regional vCPUs`
   - Filter by your desired region (e.g., East US)

4. **Request Increase**
   - Click on the quota line item
   - Click "Request increase" or the pencil/edit icon
   - Enter the new limit: **1** (or higher if you plan to deploy multiple VMs)
   - Provide a reason: "Deploying free tier VM for development/testing"
   - Click "Submit"

5. **Wait for Approval**
   - Most requests are auto-approved instantly for small increases
   - Some may require manual review (1-24 hours)
   - You'll receive an email notification when approved

### Option 2: Azure CLI

```bash
# First, check current quota
az vm list-usage --location eastus --output table

# Request quota increase (requires creating a support ticket)
az support tickets create \
  --ticket-name "VM Quota Increase" \
  --title "Increase Standard BS Family vCPU Quota" \
  --description "Need 1 vCPU quota for Standard_B1s VM in East US" \
  --severity minimal \
  --contact-email your-email@example.com \
  --contact-first-name "Your" \
  --contact-last-name "Name" \
  --contact-method email \
  --contact-country "US"
```

### Option 3: Azure Support Request

1. Go to Azure Portal
2. Click on "Help + support" (? icon in top-right)
3. Click "Create a support request"
4. Select:
   - Issue type: **Service and subscription limits (quotas)**
   - Subscription: Your subscription
   - Quota type: **Compute-VM (cores-vCPUs) subscription limit increases**
5. Fill in details:
   - Region: Your desired region
   - VM Series: Standard BS Series
   - New vCPU Limit: 1 (minimum)
6. Submit the request

## Verification After Approval

Check if your quota was increased:

```bash
# Using Azure CLI
az vm list-usage --location eastus --output table | grep "Standard BS Family"

# Expected output should show:
# Standard BS Family vCPUs    0         1         Regional
```

## Alternative Solutions (If Quota Request is Denied)

### 1. Try Different Regions

Some regions have better availability. Try these popular regions:
- East US (eastus)
- West US 2 (westus2)
- West Europe (westeurope)
- Southeast Asia (southeastasia)

```bash
# Check quota in different regions
for region in eastus westus2 westeurope southeastasia; do
  echo "Checking quota for $region:"
  az vm list-usage --location $region --output table | grep "Standard BS Family"
done
```

### 2. Use Azure Free Tier Benefits

If you have an Azure free account:
- You get 750 hours/month of B1s VM for the first 12 months
- Make sure you've activated your free tier benefits
- Go to: https://azure.microsoft.com/free/

### 3. Try Different VM Sizes

If B1s isn't available, try other free-tier eligible sizes:
- Standard_B1ls (even smaller)
- Standard_A1_v2

Modify the `azuredeploy.bicep` file to use a different size:
```bicep
@allowed([
  'Standard_B1s'
  'Standard_B1ls'
  'Standard_A1_v2'
])
param vmSize string = 'Standard_B1s'
```

### 4. Use Azure Container Instances

As an alternative to VMs, consider Azure Container Instances (ACI):
- No quota limits for basic usage
- Pay-per-second billing
- Faster startup time
- Better for temporary workloads

## Common Mistakes to Avoid

1. **Wrong Region**: Make sure you're requesting quota for the region where you plan to deploy
2. **Wrong VM Family**: Request quota for "Standard BS Family" specifically for B1s VMs
3. **Insufficient Quota**: If deploying multiple VMs, request enough quota (at least 1 vCPU per VM)
4. **Not Waiting**: After requesting, wait a few minutes before attempting deployment again

## Checking Current Usage and Limits

### Via Azure Portal
1. Go to Subscriptions → Your subscription
2. Click "Usage + quotas"
3. View all quotas and current usage

### Via Azure CLI
```bash
# List all usage for a region
az vm list-usage --location eastus --output table

# Check specific VM size availability
az vm list-skus --location eastus --size Standard_B1s --output table
```

## After Quota is Approved

Once your quota request is approved:

1. **Verify the increase**:
   ```bash
   az vm list-usage --location eastus --output table | grep "Standard BS Family"
   ```

2. **Run the deployment**:
   ```bash
   ./deploy.sh
   ```
   
   Or use Azure CLI:
   ```bash
   az deployment group create \
     --resource-group myResourceGroup \
     --template-file azuredeploy.bicep \
     --parameters azuredeploy.parameters.json
   ```

3. **Monitor the deployment**:
   - Watch for any errors in the terminal
   - Check Azure Portal → Resource Groups → Your group
   - Verify VM status is "Running"

## Getting Help

If you continue to have quota issues:

1. **Azure Support**: Open a support ticket in Azure Portal
2. **Azure Community**: https://techcommunity.microsoft.com/azure
3. **Stack Overflow**: Tag your question with `azure` and `azure-quota`
4. **GitHub Issues**: Open an issue in this repository

## Cost Awareness

Remember:
- Free tier: 750 hours/month of B1s for 12 months (new accounts)
- After free tier: ~$7-10/month per B1s VM running 24/7
- Always delete resources when not in use to avoid charges

```bash
# Stop VM to avoid compute charges (storage charges still apply)
az vm deallocate --resource-group myResourceGroup --name myFreeVM

# Delete entire resource group to remove all charges
az group delete --name myResourceGroup --yes
```

## Summary Checklist

- [ ] Login to Azure Portal
- [ ] Navigate to Subscriptions → Usage + quotas
- [ ] Search for "Standard BS Family vCPUs" in your region
- [ ] Request increase to at least 1 vCPU
- [ ] Wait for approval (check email)
- [ ] Verify quota increase with Azure CLI
- [ ] Run deployment script or GitHub Actions workflow
- [ ] Verify VM is running
- [ ] Connect via SSH to test

Good luck with your deployment!
