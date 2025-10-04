# Quick Start Guide - Fasttrack Terraform CLI

Get up and running in 5 minutes!

## Step 1: Install (1 minute)

```bash
cd /Users/sathish/work/jj/fasttrack/fasttrack-terraform-cli

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install -e .
```

## Step 2: Verify Installation (30 seconds)

```bash
fasttrack check
```

Expected output:
```
✓ Azure CLI authenticated
  Subscription: Your Subscription Name
  Tenant ID: xxx-xxx-xxx
  User: your@email.com

✓ Terraform installed
  Terraform v1.x.x
```

## Step 3: Create Your First Resource (2 minutes)

### Example A: Storage Only

```bash
fasttrack generate \
  --project-name test-project \
  --resource-group test-storage-rg \
  --storage-account teststorage001 \
  --containers data logs

fasttrack apply --directory ./terraform-generated
```

### Example B: App Registration Only

```bash
fasttrack generate \
  --project-name test-app \
  --resource-group test-app-rg \
  --app-name test-oauth-app \
  --redirect-url https://localhost:8080/callback

fasttrack apply --directory ./terraform-generated
```

### Example C: Both Storage and App

```bash
fasttrack generate \
  --project-name fullstack-test \
  --resource-group test-fullstack-rg \
  --app-name fullstack-app \
  --storage-account fullstackstg001 \
  --containers uploads assets

fasttrack apply --directory ./terraform-generated
```

## Step 4: View Your Resources (30 seconds)

```bash
# See all outputs
fasttrack output --directory ./terraform-generated

# Get specific values
fasttrack output --directory ./terraform-generated --output-name application_id
fasttrack output --directory ./terraform-generated --output-name storage_account_name
```

## Step 5: Clean Up (1 minute)

When you're done testing:

```bash
fasttrack destroy --directory ./terraform-generated
```

---

## Common Commands Cheat Sheet

```bash
# Check prerequisites
fasttrack check

# Generate config
fasttrack generate --project-name PROJECT --resource-group RG [OPTIONS]

# Apply changes
fasttrack apply --directory DIR

# View outputs
fasttrack output --directory DIR

# Destroy resources
fasttrack destroy --directory DIR

# Get help
fasttrack --help
fasttrack generate --help
```

## Real World Example

Create an ArgoCD setup with storage:

```bash
# 1. Generate
fasttrack generate \
  --project-name argocd-prod \
  --resource-group argocd-production-rg \
  --location eastus \
  --environment production \
  --app-name argocd-sso-app \
  --redirect-url https://argocd.yourcompany.com/auth/callback \
  --storage-account argocdprodstg \
  --containers manifests helm-charts \
  --output-dir ./argocd-prod-terraform

# 2. Review generated files
ls -la ./argocd-prod-terraform/

# 3. Apply
fasttrack apply --directory ./argocd-prod-terraform

# 4. Get credentials for ArgoCD config
CLIENT_ID=$(fasttrack output --directory ./argocd-prod-terraform --output-name application_id)
CLIENT_SECRET=$(fasttrack output --directory ./argocd-prod-terraform --output-name client_secret)
TENANT_ID=$(fasttrack output --directory ./argocd-prod-terraform --output-name tenant_id)

echo "Client ID: $CLIENT_ID"
echo "Tenant ID: $TENANT_ID"
echo "Client Secret: $CLIENT_SECRET"
```

## Tips

1. **Unique Names**: Storage account names must be globally unique. Add random suffix if needed.

2. **Location**: Use `az account list-locations -o table` to see available regions.

3. **Multiple Containers**: Specify `--containers` multiple times:
   ```bash
   --containers data --containers logs --containers backups
   ```

4. **Review Before Apply**: Always review generated `.tf` files before applying.

5. **State Management**: For production, configure Terraform remote backend in `main.tf`.

## Need Help?

```bash
fasttrack --help
fasttrack generate --help
```

Or check the full [README.md](README.md) for detailed documentation.
