# Quick Start Guide

Get your Azure VM deployed in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:
- [ ] An Azure account (sign up at https://azure.microsoft.com/free/)
- [ ] Azure CLI installed (https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [ ] VM quota approved in your Azure subscription (see QUOTA_INCREASE_GUIDE.md)

## Fast Track Deployment

### Step 1: Clone Repository (30 seconds)

```bash
git clone https://github.com/ejculp-droid/ACCESSMEIFYOUCAN.git
cd ACCESSMEIFYOUCAN
```

### Step 2: Login to Azure (1 minute)

```bash
az login
```

This will open your browser for authentication.

### Step 3: Run Deployment (3 minutes)

```bash
chmod +x deploy.sh
./deploy.sh
```

Follow the interactive prompts:
- **Resource Group Name**: Press Enter for default (myResourceGroup) or enter your own
- **Location**: Press Enter for default (eastus) or enter your preferred region
- **VM Name**: Press Enter for default (myFreeVM) or enter your own
- **Admin Username**: Press Enter for default (azureuser) or enter your own
- **Admin Password**: Enter a secure password (min 12 chars, with uppercase, lowercase, number, and special char)
- **Confirm**: Type `yes` to proceed

### Step 4: Connect to Your VM (30 seconds)

After deployment completes, you'll see connection details:

```bash
ssh azureuser@<your-vm-public-ip>
```

## That's It!

You now have a running Azure VM. 🎉

## What's Next?

- Update packages: `sudo apt update && sudo apt upgrade -y`
- Install software: `sudo apt install <package-name>`
- Configure firewall: Modify NSG rules in Azure Portal
- Deploy your application

## Troubleshooting

### Got a quota error?

See the detailed [QUOTA_INCREASE_GUIDE.md](QUOTA_INCREASE_GUIDE.md) for step-by-step instructions on requesting quota increases.

### Deployment failed?

Check:
1. You're logged in to Azure: `az account show`
2. You have contributor permissions on the subscription
3. The location/region supports your subscription type
4. Try a different region: `--location westus2`

### Can't connect via SSH?

Wait 2-3 minutes after deployment for the VM to fully initialize, then try again.

## Clean Up (Important!)

To avoid unwanted charges, delete resources when done:

```bash
az group delete --name myResourceGroup --yes --no-wait
```

This removes all resources created by the deployment.

## Need Help?

- Full documentation: [README.md](README.md)
- Quota issues: [QUOTA_INCREASE_GUIDE.md](QUOTA_INCREASE_GUIDE.md)
- GitHub Issues: https://github.com/ejculp-droid/ACCESSMEIFYOUCAN/issues
