# Common Issues and Solutions

Quick reference for troubleshooting Azure VM deployment issues.

## Pre-Deployment Issues

### ❌ Azure CLI Not Found

**Error:**
```
bash: az: command not found
```

**Solution:**
1. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. Verify installation: `az version`
3. Restart your terminal

---

### ❌ Not Logged In to Azure

**Error:**
```
Please run 'az login' to setup account.
```

**Solution:**
```bash
az login
```
This opens a browser for authentication. Follow the prompts.

**Alternative (device code):**
```bash
az login --use-device-code
```

---

### ❌ No Subscription Access

**Error:**
```
No subscriptions found for {user}@{domain}
```

**Solution:**
1. Check you have an Azure subscription: https://portal.azure.com
2. Sign up for free trial: https://azure.microsoft.com/free/
3. Verify with: `az account list --output table`

---

## Quota Issues

### ❌ VM Quota Exceeded

**Error:**
```
Operation cannot be completed without additional quota.
Current Limit (Free VMs): 0
```

**Solution:**
Follow the detailed [QUOTA_INCREASE_GUIDE.md](QUOTA_INCREASE_GUIDE.md)

**Quick steps:**
1. Go to Azure Portal → Subscriptions → Usage + quotas
2. Search for "Standard BS Family vCPUs"
3. Request increase to at least 1
4. Wait for approval (usually instant for small increases)

---

### ❌ Regional Quota Limit

**Error:**
```
Quota exceeded for StandardBSFamily in region 'East US'
```

**Solution Option 1 - Try different region:**
```bash
./deploy.sh
# Choose a different location like westus2, centralus, or westeurope
```

**Solution Option 2 - Request quota for that region:**
- See [QUOTA_INCREASE_GUIDE.md](QUOTA_INCREASE_GUIDE.md)

---

## Deployment Issues

### ❌ Resource Group Already Exists

**Error:**
```
Resource group 'myResourceGroup' already exists
```

**Solution Option 1 - Use existing:**
```bash
# Skip resource group creation, just deploy
az deployment group create \
  --resource-group myResourceGroup \
  --template-file azuredeploy.bicep
```

**Solution Option 2 - Choose different name:**
```bash
./deploy.sh
# Enter a different resource group name when prompted
```

**Solution Option 3 - Delete old group:**
```bash
az group delete --name myResourceGroup --yes
# Wait for deletion to complete, then redeploy
```

---

### ❌ VM Name Already Exists

**Error:**
```
The VM name 'myFreeVM' is already in use
```

**Solution:**
Use a different VM name:
```bash
./deploy.sh
# Enter a unique VM name when prompted, e.g., myFreeVM2
```

---

### ❌ Invalid Password

**Error:**
```
Password must be at least 12 characters
```

**Requirements:**
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

**Valid example:** `MySecureP@ssw0rd!`

---

### ❌ Template Validation Failed

**Error:**
```
Template validation failed: <error details>
```

**Solutions:**

**Check template syntax:**
```bash
# For Bicep
az bicep build --file azuredeploy.bicep

# For ARM JSON
python3 -c "import json; json.load(open('azuredeploy.json'))"
```

**Ensure you have latest version:**
```bash
git pull origin main
```

---

### ❌ Deployment Timeout

**Error:**
```
Deployment timed out
```

**Solution:**
1. Check Azure Portal → Resource Groups → Deployments for status
2. VM deployments can take 5-10 minutes
3. Wait a bit longer and check status:
```bash
az deployment group show \
  --resource-group myResourceGroup \
  --name azuredeploy
```

---

## Post-Deployment Issues

### ❌ Can't Get Public IP

**Error:**
```
Public IP is empty or not assigned
```

**Solution:**
VM might still be starting. Wait 2-3 minutes, then:
```bash
az vm show -d \
  --resource-group myResourceGroup \
  --name myFreeVM \
  --query publicIps -o tsv
```

---

### ❌ SSH Connection Refused

**Error:**
```
ssh: connect to host X.X.X.X port 22: Connection refused
```

**Solutions:**

**1. VM still initializing:**
Wait 3-5 minutes after deployment completes.

**2. Check VM status:**
```bash
az vm get-instance-view \
  --resource-group myResourceGroup \
  --name myFreeVM \
  --query instanceView.statuses[1] --output table
```
Should show "PowerState/running"

**3. Check NSG rules:**
```bash
az network nsg rule list \
  --resource-group myResourceGroup \
  --nsg-name myFreeVM-nsg \
  --output table
```
Verify SSH (port 22) rule exists

**4. Verify public IP:**
```bash
az vm show -d \
  --resource-group myResourceGroup \
  --name myFreeVM \
  --query publicIps -o tsv
```

---

### ❌ SSH Permission Denied

**Error:**
```
Permission denied (publickey,password)
```

**Solutions:**

**Check username:**
- Default is `azureuser`
- Use the username you specified during deployment

**Check password:**
- Re-enter the password you set during deployment
- Password is case-sensitive

**Correct command:**
```bash
ssh azureuser@<public-ip>
# Or with the username you specified
```

---

### ❌ VM Is Slow or Unresponsive

**Possible Causes:**
- B1s is a small VM (1 vCPU, 1 GB RAM)
- High CPU/memory usage
- Network throttling

**Solutions:**

**1. Check VM metrics in Azure Portal**

**2. Restart VM:**
```bash
az vm restart --resource-group myResourceGroup --name myFreeVM
```

**3. Resize to larger VM (costs money):**
```bash
az vm resize \
  --resource-group myResourceGroup \
  --name myFreeVM \
  --size Standard_B2s
```

---

## GitHub Actions Issues

### ❌ Azure Login Failed

**Error:**
```
Error: Login failed with Error: Unable to connect to Azure
```

**Solution:**
1. Verify `AZURE_CREDENTIALS` secret is set correctly
2. Recreate service principal:
```bash
az ad sp create-for-rbac \
  --name "github-actions-sp" \
  --role contributor \
  --scopes /subscriptions/{subscription-id} \
  --sdk-auth
```
3. Update the secret in GitHub → Settings → Secrets

---

### ❌ Subscription Not Found

**Error:**
```
Subscription <id> not found
```

**Solution:**
1. Verify `AZURE_SUBSCRIPTION_ID` secret matches your subscription
2. Get your subscription ID:
```bash
az account list --output table
```
3. Update GitHub secret with correct ID

---

### ❌ Workflow Not Visible

**Issue:** Can't find "Deploy Azure VM" in Actions tab

**Solution:**
1. Ensure `.github/workflows/deploy-vm.yml` exists in your repository
2. Push the workflow file to GitHub:
```bash
git add .github/workflows/deploy-vm.yml
git commit -m "Add deployment workflow"
git push
```
3. Refresh the Actions tab

---

## Cleanup Issues

### ❌ Resource Group Won't Delete

**Error:**
```
Cannot delete resource group that has resources
```

**Solution:**

**Option 1 - Force delete:**
```bash
az group delete --name myResourceGroup --yes --no-wait
```

**Option 2 - Delete VM first:**
```bash
az vm delete --resource-group myResourceGroup --name myFreeVM --yes
az group delete --name myResourceGroup --yes
```

**Option 3 - Use Azure Portal:**
1. Go to Resource Groups
2. Select your resource group  
3. Click "Delete resource group"
4. Type the name to confirm

---

### ❌ VM Deallocated But Still Charged

**Issue:** You stopped the VM but still seeing charges

**Explanation:**
- Storage charges continue even when VM is stopped
- Only way to avoid ALL charges is to delete resources

**Solution:**
```bash
# To completely stop billing:
az group delete --name myResourceGroup --yes
```

---

## File/Script Issues

### ❌ deploy.sh Permission Denied

**Error:**
```
bash: ./deploy.sh: Permission denied
```

**Solution:**
```bash
chmod +x deploy.sh
./deploy.sh
```

---

### ❌ Line Ending Issues (Windows)

**Error:**
```
: bad interpreter: No such file or directory
```

**Solution (if using Git on Windows):**
```bash
git config core.autocrlf input
git rm --cached deploy.sh
git add deploy.sh
```

Or convert manually:
```bash
dos2unix deploy.sh
```

---

## Getting More Help

### Check Deployment Logs

**Azure Portal:**
1. Go to Resource Groups → Your group
2. Click "Deployments" in left menu
3. Click on the failed deployment
4. View error details

**Azure CLI:**
```bash
az deployment group show \
  --resource-group myResourceGroup \
  --name azuredeploy \
  --query properties.error
```

### Enable Debug Logging

```bash
# For Azure CLI
az deployment group create \
  --resource-group myResourceGroup \
  --template-file azuredeploy.bicep \
  --debug
```

### Useful Commands

**Check VM status:**
```bash
az vm list --output table
```

**Get all VM info:**
```bash
az vm show --resource-group myResourceGroup --name myFreeVM
```

**List all resources:**
```bash
az resource list --resource-group myResourceGroup --output table
```

**Check quota usage:**
```bash
az vm list-usage --location eastus --output table
```

---

## Still Need Help?

1. **Check documentation:**
   - [README.md](README.md) - Full documentation
   - [QUICKSTART.md](QUICKSTART.md) - Quick start guide
   - [QUOTA_INCREASE_GUIDE.md](QUOTA_INCREASE_GUIDE.md) - Quota help

2. **Azure Resources:**
   - [Azure Documentation](https://docs.microsoft.com/azure/)
   - [Azure Status](https://status.azure.com/) - Check for outages
   - [Azure Support](https://azure.microsoft.com/support/)

3. **Community:**
   - [Stack Overflow](https://stackoverflow.com/questions/tagged/azure) - Tag with 'azure'
   - [Azure Community](https://techcommunity.microsoft.com/azure)
   - [GitHub Issues](https://github.com/ejculp-droid/ACCESSMEIFYOUCAN/issues) - Repository issues

4. **Contact:**
   - Open an issue in this repository with:
     - Error message (full text)
     - Steps you followed
     - Your Azure region
     - Output of `az version`
