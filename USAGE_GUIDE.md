# Fasttrack Terraform CLI - Complete Usage Guide

## Table of Contents
1. [Installation](#installation)
2. [Basic Workflow](#basic-workflow)
3. [Common Use Cases](#common-use-cases)
4. [Command Reference](#command-reference)
5. [Examples](#examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Installation

### Step 1: Navigate to CLI Directory
```bash
cd fasttrack-terraform-cli
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install CLI
```bash
pip install -e .
```

### Step 4: Verify Installation
```bash
fasttrack --version
fasttrack check
```

---

## Basic Workflow

### 1. Prerequisites Check
```bash
# Verify Azure login and Terraform installation
fasttrack check
```

### 2. Generate Configuration
```bash
fasttrack generate \
  --project-name YOUR_PROJECT \
  --resource-group YOUR_RG \
  [OPTIONS]
```

### 3. Apply Configuration
```bash
fasttrack apply --directory ./terraform-generated
```

### 4. View Outputs
```bash
fasttrack output --directory ./terraform-generated
```

### 5. Cleanup (when done)
```bash
fasttrack destroy --directory ./terraform-generated
```

---

## Common Use Cases

### Use Case 1: Create Storage Account with Containers

**Scenario:** Need blob storage for data lake with multiple containers.

```bash
fasttrack generate \
  --project-name datalake \
  --resource-group datalake-rg \
  --location eastus \
  --storage-account datalakestg001 \
  --containers raw \
  --containers processed \
  --containers archived \
  --output-dir ./datalake-terraform

fasttrack apply --directory ./datalake-terraform
```

**What gets created:**
- Resource group: `datalake-rg`
- Storage account: `datalakestg001`
- Containers: `raw`, `processed`, `archived`

---

### Use Case 2: Create Azure AD App Registration

**Scenario:** Need OAuth app for authentication.

```bash
fasttrack generate \
  --project-name webapp \
  --resource-group webapp-rg \
  --app-name webapp-oauth \
  --redirect-url https://webapp.company.com/auth/callback \
  --output-dir ./webapp-terraform

fasttrack apply --directory ./webapp-terraform

# Get credentials
APP_ID=$(fasttrack output --directory ./webapp-terraform --output-name application_id | jq -r .value)
CLIENT_SECRET=$(fasttrack output --directory ./webapp-terraform --output-name client_secret | jq -r .value)
TENANT_ID=$(fasttrack output --directory ./webapp-terraform --output-name tenant_id | jq -r .value)

echo "App ID: $APP_ID"
echo "Client Secret: $CLIENT_SECRET"
echo "Tenant ID: $TENANT_ID"
```

**What gets created:**
- Resource group: `webapp-rg`
- Azure AD application: `webapp-oauth`
- Service principal
- Client secret (12-month rotation)

---

### Use Case 3: Complete Infrastructure (App + Storage)

**Scenario:** Full-stack application with authentication and storage.

```bash
fasttrack generate \
  --project-name fullstack \
  --resource-group fullstack-prod-rg \
  --location westus2 \
  --environment production \
  --app-name fullstack-app \
  --redirect-url https://app.company.com/callback \
  --storage-account fullstackprodstg \
  --containers uploads \
  --containers assets \
  --containers backups \
  --storage-tier Standard \
  --storage-replication GRS \
  --output-dir ./fullstack-terraform

fasttrack apply --directory ./fullstack-terraform
```

**What gets created:**
- Resource group: `fullstack-prod-rg`
- Azure AD application with OAuth
- Storage account with 3 containers
- All resources properly tagged

---

## Command Reference

### `fasttrack check`

Verify prerequisites.

```bash
fasttrack check
```

**Output:**
```
✓ Azure CLI authenticated
  Subscription: Microsoft Azure Sponsorship
  Tenant ID: xxx-xxx-xxx
  User: user@example.com

✓ Terraform installed
  Terraform v1.5.7
```

---

### `fasttrack generate`

Generate Terraform configuration files.

**Syntax:**
```bash
fasttrack generate [OPTIONS]
```

**Required Options:**
- `--project-name TEXT` - Project name
- `--resource-group TEXT` - Resource group name

**Optional Options:**
- `--location TEXT` - Azure region (default: eastus)
- `--environment TEXT` - Environment (default: development)
- `--app-name TEXT` - App registration name
- `--redirect-url TEXT` - OAuth redirect URL
- `--storage-account TEXT` - Storage account name
- `--containers TEXT` - Container names (repeatable)
- `--storage-tier [Standard|Premium]` - Storage tier
- `--storage-replication [LRS|GRS|RAGRS|ZRS]` - Replication
- `--secret-rotation-months INTEGER` - Secret rotation period (default: 12)
- `--output-dir TEXT` - Output directory (default: ./terraform-generated)
- `--skip-validation` - Skip Azure login validation

**Examples:**

```bash
# Storage only
fasttrack generate \
  --project-name myproject \
  --resource-group myproject-rg \
  --storage-account myprojectstg001 \
  --containers data

# App registration only
fasttrack generate \
  --project-name myproject \
  --resource-group myproject-rg \
  --app-name myproject-app \
  --redirect-url https://app.example.com/callback

# Both with custom settings
fasttrack generate \
  --project-name myproject \
  --resource-group myproject-rg \
  --location westeurope \
  --environment staging \
  --app-name myproject-app \
  --storage-account myprojectstg001 \
  --containers data --containers logs \
  --storage-replication GRS \
  --secret-rotation-months 6
```

---

### `fasttrack apply`

Apply Terraform configuration.

**Syntax:**
```bash
fasttrack apply [OPTIONS]
```

**Options:**
- `--directory TEXT` - Terraform directory (default: ./terraform-generated)
- `--auto-approve` - Skip interactive confirmation

**Examples:**

```bash
# Interactive apply (asks for confirmation)
fasttrack apply --directory ./my-terraform

# Auto-approve (for CI/CD)
fasttrack apply --directory ./my-terraform --auto-approve
```

**Process:**
1. Validates Azure login
2. Runs `terraform init`
3. Runs `terraform plan`
4. Asks for confirmation (unless --auto-approve)
5. Runs `terraform apply`

---

### `fasttrack output`

Show Terraform outputs.

**Syntax:**
```bash
fasttrack output [OPTIONS]
```

**Options:**
- `--directory TEXT` - Terraform directory (default: ./terraform-generated)
- `--output-name TEXT` - Specific output to retrieve

**Examples:**

```bash
# Show all outputs (JSON format)
fasttrack output --directory ./my-terraform

# Get specific output (raw value)
fasttrack output --directory ./my-terraform --output-name application_id
fasttrack output --directory ./my-terraform --output-name client_secret
fasttrack output --directory ./my-terraform --output-name storage_account_name
```

**Common Outputs:**
- `application_id` - Azure AD app client ID
- `client_secret` - Client secret (sensitive)
- `tenant_id` - Azure AD tenant ID
- `object_id` - App object ID
- `service_principal_object_id` - Service principal object ID
- `resource_group_name` - Resource group name
- `resource_group_location` - Resource group location
- `storage_account_name` - Storage account name
- `storage_account_primary_blob_endpoint` - Blob endpoint URL
- `storage_container_1_name`, `storage_container_2_name`, etc. - Container names
- `storage_container_1_url`, `storage_container_2_url`, etc. - Container URLs

---

### `fasttrack destroy`

Destroy all Terraform-managed resources.

**Syntax:**
```bash
fasttrack destroy [OPTIONS]
```

**Options:**
- `--directory TEXT` - Terraform directory (default: ./terraform-generated)
- `--auto-approve` - Skip interactive confirmation

**Examples:**

```bash
# Interactive destroy (asks for confirmation)
fasttrack destroy --directory ./my-terraform

# Auto-approve (use with caution!)
fasttrack destroy --directory ./my-terraform --auto-approve
```

⚠️ **Warning:** This permanently deletes all resources managed by the Terraform state!

---

## Examples

### Example 1: ArgoCD with Storage

```bash
# Generate configuration
fasttrack generate \
  --project-name argocd-prod \
  --resource-group argocd-rg \
  --environment production \
  --app-name argocd-sso \
  --redirect-url https://argocd.company.com/auth/callback \
  --storage-account argocdprodstg \
  --containers helm-charts \
  --containers manifests \
  --output-dir ./argocd-terraform

# Apply
fasttrack apply --directory ./argocd-terraform

# Get ArgoCD configuration values
echo "=== ArgoCD Azure AD Configuration ==="
echo "Client ID: $(fasttrack output --directory ./argocd-terraform --output-name application_id | jq -r .value)"
echo "Client Secret: $(fasttrack output --directory ./argocd-terraform --output-name client_secret | jq -r .value)"
echo "Tenant ID: $(fasttrack output --directory ./argocd-terraform --output-name tenant_id | jq -r .value)"
echo "Storage Account: $(fasttrack output --directory ./argocd-terraform --output-name storage_account_name | jq -r .value)"
```

---

### Example 2: Multi-Environment Setup

```bash
# Development
fasttrack generate \
  --project-name myapp \
  --resource-group myapp-dev-rg \
  --environment development \
  --app-name myapp-dev \
  --storage-account myappdevstg001 \
  --containers data \
  --output-dir ./dev-terraform

# Production
fasttrack generate \
  --project-name myapp \
  --resource-group myapp-prod-rg \
  --environment production \
  --app-name myapp-prod \
  --storage-account myappprodstg \
  --containers data \
  --storage-replication GRS \
  --output-dir ./prod-terraform

# Apply both
fasttrack apply --directory ./dev-terraform --auto-approve
fasttrack apply --directory ./prod-terraform
```

---

### Example 3: CI/CD Pipeline Integration

```bash
#!/bin/bash
# deploy.sh

set -e

PROJECT_NAME="webapp"
ENVIRONMENT="${1:-dev}"  # dev, staging, prod
RG_NAME="${PROJECT_NAME}-${ENVIRONMENT}-rg"

# Generate
fasttrack generate \
  --project-name "$PROJECT_NAME" \
  --resource-group "$RG_NAME" \
  --environment "$ENVIRONMENT" \
  --app-name "${PROJECT_NAME}-${ENVIRONMENT}-app" \
  --storage-account "${PROJECT_NAME}${ENVIRONMENT}stg" \
  --containers uploads \
  --skip-validation \
  --output-dir "./terraform-${ENVIRONMENT}"

# Apply
fasttrack apply \
  --directory "./terraform-${ENVIRONMENT}" \
  --auto-approve

# Save outputs to file
fasttrack output --directory "./terraform-${ENVIRONMENT}" > "outputs-${ENVIRONMENT}.json"

echo "Deployment complete!"
```

---

## Best Practices

### 1. Naming Conventions

**Storage Accounts:**
- 3-24 characters
- Lowercase letters and numbers only
- Must be globally unique
- Example: `companyprojectenv` → `acmeprodstg001`

**Resource Groups:**
- Use descriptive names
- Include project and environment
- Example: `projectname-environment-rg` → `webapp-prod-rg`

**App Registrations:**
- Use descriptive names
- Include purpose
- Example: `projectname-purpose` → `webapp-oauth-app`

---

### 2. Environment Strategy

```bash
# Use consistent patterns across environments
# Development
--environment development --storage-account projectdevstg

# Staging
--environment staging --storage-account projectstgstg

# Production
--environment production --storage-account projectprodstg --storage-replication GRS
```

---

### 3. Storage Configuration

**Development/Testing:**
- Standard tier
- LRS replication
- Minimal containers

**Production:**
- Standard or Premium tier
- GRS or RAGRS replication
- Organized containers

```bash
# Production example
--storage-tier Standard \
--storage-replication GRS \
--containers data \
--containers logs \
--containers backups
```

---

### 4. Security Best Practices

1. **Client Secrets:**
   - Use short rotation periods in production (6 months)
   - Store secrets in Azure Key Vault
   - Never commit to source control

2. **Permissions:**
   - Grant minimal required permissions
   - Use service principals for automation

3. **Outputs:**
   - Be careful with sensitive outputs
   - Use `jq` to extract specific values
   - Don't log client secrets in CI/CD

```bash
# Good: Extract specific value
CLIENT_SECRET=$(fasttrack output --directory ./tf --output-name client_secret | jq -r .value)

# Bad: Log entire output (contains secrets)
fasttrack output --directory ./tf | tee output.log
```

---

### 5. State Management

For production, configure remote backend:

```hcl
# Add to generated main.tf
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstateaccount"
    container_name       = "tfstate"
    key                  = "project.tfstate"
  }
}
```

---

## Troubleshooting

### Issue: "Not logged into Azure"

**Solution:**
```bash
az login
az account show
fasttrack check
```

---

### Issue: "Storage account name already exists"

**Cause:** Storage account names are globally unique across all of Azure.

**Solution:** Try a different name with random suffix:
```bash
--storage-account myapp$RANDOM
```

---

### Issue: "Permission denied" during apply

**Cause:** Insufficient Azure permissions.

**Solution:**
1. Check your role: `az role assignment list --assignee $(az account show --query user.name -o tsv)`
2. Need at least "Contributor" role on subscription
3. Contact Azure administrator

---

### Issue: Terraform state locked

**Cause:** Previous operation didn't complete cleanly.

**Solution:**
```bash
cd ./terraform-generated
terraform force-unlock <LOCK_ID>
```

---

### Issue: Resources already exist (not managed by Terraform)

**Solution:** Import existing resources:
```bash
cd ./terraform-generated
terraform import azurerm_resource_group.main /subscriptions/{sub-id}/resourceGroups/{rg-name}
```

---

### Debug Mode

Enable detailed Terraform logging:
```bash
export TF_LOG=DEBUG
fasttrack apply --directory ./terraform-generated
```

---

## Quick Reference Card

```bash
# Check prerequisites
fasttrack check

# Generate storage only
fasttrack generate --project-name X --resource-group Y --storage-account Z --containers data

# Generate app only
fasttrack generate --project-name X --resource-group Y --app-name Z --redirect-url URL

# Generate both
fasttrack generate --project-name X --resource-group Y --app-name Z --storage-account W --containers data

# Apply
fasttrack apply --directory ./terraform-generated

# View all outputs
fasttrack output --directory ./terraform-generated

# Get specific output
fasttrack output --directory ./terraform-generated --output-name application_id

# Destroy
fasttrack destroy --directory ./terraform-generated
```

---

## Support

For issues:
1. Check this usage guide
2. Review [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md)
3. Run `fasttrack check` to verify prerequisites
4. Check generated Terraform files for errors
5. Enable debug logging: `export TF_LOG=DEBUG`

---

**Version:** 1.0.0
**Last Updated:** 2025-10-04
