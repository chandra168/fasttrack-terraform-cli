# Fasttrack Terraform CLI - Command Reference

Complete reference for all CLI commands, options, and usage patterns.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Command Overview](#command-overview)
3. [Generate Command](#generate-command)
4. [Apply Command](#apply-command)
5. [Output Command](#output-command)
6. [Destroy Command](#destroy-command)
7. [Check Command](#check-command)
8. [Import Commands](#import-commands)
9. [Using YAML Configuration](#using-yaml-configuration)
10. [Common Use Cases](#common-use-cases)

---

## Quick Start

```bash
# Install the CLI
pip install -e .

# Generate Terraform configuration
fasttrack generate --project-name myproject --resource-group myproject-rg --output-dir ./terraform-myproject

# Apply the configuration
fasttrack apply --directory ./terraform-myproject

# Get outputs
fasttrack output --directory ./terraform-myproject

# Destroy resources
fasttrack destroy --directory ./terraform-myproject
```

---

## Command Overview

| Command | Description |
|---------|-------------|
| `generate` | Generate Terraform configuration files |
| `apply` | Apply Terraform configuration to create resources |
| `output` | Display Terraform outputs |
| `destroy` | Destroy all resources managed by Terraform |
| `check` | Validate configuration and check prerequisites |
| `init-import` | Initialize Terraform and import existing resources |
| `import-resource` | Import a specific resource into Terraform state |

---

## Generate Command

Creates Terraform configuration files from templates.

### Syntax

```bash
fasttrack generate [OPTIONS]
```

### Required Options

| Option | Description | Example |
|--------|-------------|---------|
| `--project-name` | Project name for tagging | `--project-name myproject` |
| `--resource-group` | Azure resource group name | `--resource-group myproject-rg` |

### Optional Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--location` | string | `eastus` | Azure region |
| `--environment` | string | `development` | Environment tag |
| `--output-dir` | path | `./terraform-generated` | Output directory |
| `--config-file` | path | - | YAML configuration file |
| `--skip-validation` | flag | False | Skip config validation |
| `--app-name` | string | - | Azure AD app registration name |
| `--redirect-url` | string | - | OAuth redirect URI |
| `--storage-account` | string | - | Storage account name |
| `--containers` | list | - | Container names (repeatable) |
| `--storage-tier` | string | `Standard` | Storage tier (Standard/Premium) |
| `--storage-replication` | string | `LRS` | Replication type (LRS/GRS/RAGRS) |
| `--secret-rotation-months` | int | `12` | Secret rotation period |
| `--use-existing-storage` | flag | False | Use existing storage account |
| `--enable-remote-state` | flag | False | Enable remote state backend |
| `--state-storage-account` | string | - | Remote state storage account |
| `--state-container` | string | `tfstate` | Remote state container |
| `--state-key` | string | `terraform.tfstate` | Remote state file name |
| `--state-resource-group` | string | - | Remote state resource group |
| `--dry-run` | flag | False | Preview without creating files |

### Examples

#### 1. Basic Resource Group Only

```bash
fasttrack generate \
  --project-name myproject \
  --resource-group myproject-rg \
  --location eastus \
  --output-dir ./terraform-basic
```

**Creates:**
- Resource group: myproject-rg
- No app registration
- No storage account

---

#### 2. Resource Group + App Registration

```bash
fasttrack generate \
  --project-name myproject \
  --resource-group myproject-rg \
  --app-name myproject-app \
  --redirect-url https://myapp.example.com/callback \
  --secret-rotation-months 12 \
  --output-dir ./terraform-app
```

**Creates:**
- Resource group: myproject-rg
- App registration: myproject-app
- Service principal
- Client secret (12-month rotation)
- No storage account

---

#### 3. Resource Group + Storage Account

```bash
fasttrack generate \
  --project-name myproject \
  --resource-group myproject-rg \
  --storage-account myprojectstg123 \
  --containers data \
  --containers logs \
  --containers backup \
  --storage-tier Standard \
  --storage-replication LRS \
  --output-dir ./terraform-storage
```

**Creates:**
- Resource group: myproject-rg
- Storage account: myprojectstg123
- Containers: data, logs, backup
- No app registration

---

#### 4. Full Stack (App + Storage)

```bash
fasttrack generate \
  --project-name myproject \
  --resource-group myproject-rg \
  --app-name myproject-app \
  --redirect-url https://myapp.example.com/callback \
  --storage-account myprojectstg123 \
  --containers data \
  --containers logs \
  --output-dir ./terraform-full
```

**Creates:**
- Resource group: myproject-rg
- App registration: myproject-app
- Service principal + client secret
- Storage account: myprojectstg123
- Containers: data, logs

---

#### 5. Use Existing Storage Account

```bash
fasttrack generate \
  --project-name myproject \
  --resource-group myproject-rg \
  --use-existing-storage \
  --storage-account existingstorage123 \
  --containers newdata \
  --containers newlogs \
  --output-dir ./terraform-existing
```

**Creates:**
- Resource group: myproject-rg
- Containers in existing storage: newdata, newlogs
- Does NOT create or modify the storage account

---

#### 6. Production Setup with Remote State

```bash
fasttrack generate \
  --project-name production-app \
  --resource-group production-rg \
  --location westus2 \
  --environment production \
  --app-name production-app \
  --redirect-url https://app.production.com/callback \
  --storage-account prodappstg123 \
  --containers data \
  --enable-remote-state \
  --state-storage-account prodtfstate123 \
  --state-container tfstate \
  --state-key production.tfstate \
  --state-resource-group tfstate-rg \
  --output-dir ./terraform-production
```

**Creates:**
- Resource group: production-rg
- App registration with production settings
- Storage account: prodappstg123
- Remote state backend configuration
- All resources in westus2

---

#### 7. Dry Run (Preview Only)

```bash
fasttrack generate \
  --project-name myproject \
  --resource-group myproject-rg \
  --app-name myproject-app \
  --storage-account myprojectstg123 \
  --containers data \
  --dry-run
```

**Output:**
- Shows what files would be created
- Shows configuration preview
- Does NOT create any files

---

## Apply Command

Applies the generated Terraform configuration to create Azure resources.

### Syntax

```bash
fasttrack apply [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--directory` | Terraform configuration directory | `./terraform-generated` |
| `--auto-approve` | Skip confirmation prompt | False |
| `--timeout` | Operation timeout in seconds | 300 |

### Examples

#### 1. Interactive Apply

```bash
fasttrack apply --directory ./terraform-myproject
```

**Process:**
1. Runs `terraform validate`
2. Shows plan
3. Asks for confirmation
4. Applies changes

---

#### 2. Auto-Approve (CI/CD)

```bash
fasttrack apply --directory ./terraform-myproject --auto-approve
```

**Process:**
1. Runs `terraform validate`
2. Shows plan
3. Automatically approves and applies

---

#### 3. With Extended Timeout

```bash
fasttrack apply --directory ./terraform-myproject --timeout 600
```

Useful for large deployments or slow network connections.

---

## Output Command

Displays Terraform output values.

### Syntax

```bash
fasttrack output [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--directory` | Terraform configuration directory | `./terraform-generated` |
| `--name` | Specific output name | (all outputs) |
| `--json` | Output in JSON format | False |

### Examples

#### 1. Show All Outputs

```bash
fasttrack output --directory ./terraform-myproject
```

**Sample Output:**
```
application_id = "1d619de4-808f-43b1-bf1f-22c33454c2ff"
resource_group_name = "myproject-rg"
storage_account_name = "myprojectstg123"
storage_account_primary_blob_endpoint = "https://myprojectstg123.blob.core.windows.net/"
tenant_id = "32c7586a-893b-4d00-9d24-d3644c3b1653"
client_secret = <sensitive>
```

---

#### 2. Get Specific Output

```bash
fasttrack output --directory ./terraform-myproject --name application_id
```

**Output:**
```
1d619de4-808f-43b1-bf1f-22c33454c2ff
```

---

#### 3. JSON Format

```bash
fasttrack output --directory ./terraform-myproject --json
```

**Output:**
```json
{
  "application_id": {
    "value": "1d619de4-808f-43b1-bf1f-22c33454c2ff",
    "type": "string"
  },
  "resource_group_name": {
    "value": "myproject-rg",
    "type": "string"
  }
}
```

---

#### 4. Get Client Secret

```bash
# Get the sensitive client secret value
terraform output -raw client_secret
```

---

## Destroy Command

Destroys all resources managed by Terraform.

### Syntax

```bash
fasttrack destroy [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--directory` | Terraform configuration directory | `./terraform-generated` |
| `--auto-approve` | Skip confirmation prompt | False |

### Examples

#### 1. Interactive Destroy

```bash
fasttrack destroy --directory ./terraform-myproject
```

**Process:**
1. Shows resources to be destroyed
2. Asks for confirmation
3. Destroys resources

---

#### 2. Auto-Approve Destroy

```bash
fasttrack destroy --directory ./terraform-myproject --auto-approve
```

⚠️ **Warning:** This immediately destroys all resources without confirmation!

---

## Check Command

Validates configuration and checks prerequisites.

### Syntax

```bash
fasttrack check [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--directory` | Terraform configuration directory |
| `--config-file` | YAML configuration file to validate |

### Examples

#### 1. Check Terraform Configuration

```bash
fasttrack check --directory ./terraform-myproject
```

**Checks:**
- Terraform installation
- Azure CLI installation
- Azure CLI authentication
- Terraform configuration validity

---

#### 2. Validate YAML Config

```bash
fasttrack check --config-file ./config.yaml
```

**Validates:**
- YAML syntax
- Required fields
- Valid values

---

## Import Commands

Import existing Azure resources into Terraform state.

### init-import Command

Initializes Terraform and imports existing resource group and storage account.

#### Syntax

```bash
fasttrack init-import --directory <path>
```

#### Example

```bash
fasttrack init-import --directory ./terraform-myproject
```

**Process:**
1. Runs `terraform init`
2. Checks if resource group exists
3. Imports resource group if found
4. Checks if storage account exists
5. Imports storage account if found

---

### import-resource Command

Imports a specific resource into Terraform state.

#### Syntax

```bash
fasttrack import-resource --directory <path> --address <resource_address> --id <azure_resource_id>
```

#### Options

| Option | Description | Example |
|--------|-------------|---------|
| `--directory` | Terraform directory | `./terraform-myproject` |
| `--address` | Terraform resource address | `azurerm_storage_account.main` |
| `--id` | Azure resource ID | `/subscriptions/.../resourceGroups/...` |

#### Examples

##### 1. Import Storage Account

```bash
fasttrack import-resource \
  --directory ./terraform-myproject \
  --address azurerm_storage_account.main \
  --id "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/myproject-rg/providers/Microsoft.Storage/storageAccounts/myprojectstg123"
```

##### 2. Import Resource Group

```bash
fasttrack import-resource \
  --directory ./terraform-myproject \
  --address azurerm_resource_group.main \
  --id "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/myproject-rg"
```

---

## Using YAML Configuration

Instead of passing all options via command line, use a YAML configuration file.

### YAML Configuration Structure

```yaml
# config.yaml - Complete structure with all options

# Required fields
project_name: myproject
resource_group: myproject-rg

# Optional - General settings
location: eastus
environment: development
output_dir: ./terraform-myproject

# Optional - App Registration settings
app_name: myproject-app
redirect_url: https://myapp.example.com/callback
secret_rotation_months: 12

# Optional - Storage Account settings
storage_account: myprojectstg123
containers:
  - data
  - logs
  - backup
storage_tier: Standard  # Standard or Premium
storage_replication: LRS  # LRS, GRS, RAGRS, ZRS

# Optional - Use existing storage
use_existing_storage: false

# Optional - Remote State Backend
enable_remote_state: false
state_storage_account: tfstatestorage123
state_container: tfstate
state_key: myproject.tfstate
state_resource_group: tfstate-rg

# Optional - Generation options
skip_validation: false
dry_run: false
```

### Using YAML Configuration

```bash
fasttrack generate --config-file config.yaml
```

### YAML Examples

#### Example 1: Basic Configuration

```yaml
# config-basic.yaml
project_name: basic-project
resource_group: basic-rg
location: westus
environment: development
```

```bash
fasttrack generate --config-file config-basic.yaml
```

---

#### Example 2: App Registration

```yaml
# config-app.yaml
project_name: app-project
resource_group: app-rg
app_name: my-application
redirect_url: https://myapp.example.com/callback
secret_rotation_months: 6
```

```bash
fasttrack generate --config-file config-app.yaml
```

---

#### Example 3: Storage Only

```yaml
# config-storage.yaml
project_name: storage-project
resource_group: storage-rg
storage_account: mystorage123
containers:
  - data
  - logs
  - backups
  - archives
storage_tier: Standard
storage_replication: GRS
```

```bash
fasttrack generate --config-file config-storage.yaml
```

---

#### Example 4: Full Stack Production

```yaml
# config-production.yaml
project_name: production-app
resource_group: production-rg
location: westus2
environment: production

# App Registration
app_name: production-app
redirect_url: https://app.production.com/callback
secret_rotation_months: 12

# Storage Account
storage_account: prodappstorage123
containers:
  - data
  - logs
storage_tier: Standard
storage_replication: GRS

# Remote State
enable_remote_state: true
state_storage_account: prodtfstate123
state_container: tfstate
state_key: production.tfstate
state_resource_group: tfstate-rg
```

```bash
fasttrack generate --config-file config-production.yaml
fasttrack apply --directory ./terraform-production-app --auto-approve
```

---

#### Example 5: Existing Storage

```yaml
# config-existing.yaml
project_name: existing-project
resource_group: existing-rg
use_existing_storage: true
storage_account: existingstorage123
containers:
  - newdata
  - newlogs
```

```bash
fasttrack generate --config-file config-existing.yaml
```

---

#### Example 6: Multi-Environment Setup

```yaml
# config-dev.yaml
project_name: myapp-dev
resource_group: myapp-dev-rg
location: eastus
environment: development
app_name: myapp-dev
redirect_url: https://dev.myapp.com/callback
storage_account: myappdevstg123
containers: [data, logs]
```

```yaml
# config-staging.yaml
project_name: myapp-staging
resource_group: myapp-staging-rg
location: eastus
environment: staging
app_name: myapp-staging
redirect_url: https://staging.myapp.com/callback
storage_account: myappstagingstg123
containers: [data, logs]
```

```yaml
# config-prod.yaml
project_name: myapp-prod
resource_group: myapp-prod-rg
location: westus2
environment: production
app_name: myapp-prod
redirect_url: https://myapp.com/callback
storage_account: myappprodstg123
containers: [data, logs]
storage_replication: GRS
enable_remote_state: true
state_storage_account: myapptfstate123
state_container: tfstate
state_key: production.tfstate
state_resource_group: tfstate-rg
```

**Deploy All Environments:**

```bash
# Development
fasttrack generate --config-file config-dev.yaml
fasttrack apply --directory ./terraform-myapp-dev --auto-approve

# Staging
fasttrack generate --config-file config-staging.yaml
fasttrack apply --directory ./terraform-myapp-staging --auto-approve

# Production
fasttrack generate --config-file config-prod.yaml
fasttrack apply --directory ./terraform-myapp-prod
```

---

## Common Use Cases

### Use Case 1: New Project Setup

**Goal:** Create a new project with app registration and storage.

```bash
# Step 1: Generate configuration
fasttrack generate \
  --project-name newproject \
  --resource-group newproject-rg \
  --app-name newproject-app \
  --redirect-url https://newproject.example.com/callback \
  --storage-account newprojectstg123 \
  --containers data \
  --containers logs \
  --output-dir ./terraform-newproject

# Step 2: Review and apply
cd terraform-newproject
terraform init
terraform plan

# Step 3: Apply
fasttrack apply --directory ./terraform-newproject

# Step 4: Get outputs
fasttrack output --directory ./terraform-newproject

# Step 5: Save sensitive values
terraform output -raw client_secret > .secrets/client_secret.txt
```

---

### Use Case 2: Add Containers to Existing Storage

**Goal:** Add new containers to existing storage account without modifying it.

```bash
# Step 1: Generate with existing storage
fasttrack generate \
  --project-name myproject \
  --resource-group existing-rg \
  --use-existing-storage \
  --storage-account existingstorage123 \
  --containers newcontainer1 \
  --containers newcontainer2 \
  --output-dir ./terraform-add-containers

# Step 2: Import existing resources
fasttrack init-import --directory ./terraform-add-containers

# Step 3: Apply to create only containers
fasttrack apply --directory ./terraform-add-containers
```

---

### Use Case 3: Disaster Recovery / Resource Recreation

**Goal:** Recreate infrastructure from configuration.

```bash
# Step 1: Check what exists
az group show -n myproject-rg
az storage account show -n myprojectstg123 -g myproject-rg

# Step 2: Import existing resources (if any)
fasttrack init-import --directory ./terraform-myproject

# Step 3: Apply to create missing resources
fasttrack apply --directory ./terraform-myproject

# Step 4: Verify all resources exist
fasttrack check --directory ./terraform-myproject
```

---

### Use Case 4: CI/CD Pipeline Integration

**Goal:** Automated deployment in CI/CD.

```yaml
# .github/workflows/deploy.yml
name: Deploy Infrastructure

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Azure Login
        run: az login --service-principal -u ${{ secrets.AZURE_CLIENT_ID }} -p ${{ secrets.AZURE_CLIENT_SECRET }} --tenant ${{ secrets.AZURE_TENANT_ID }}

      - name: Install Fasttrack CLI
        run: pip install -e .

      - name: Generate Terraform
        run: fasttrack generate --config-file config-prod.yaml

      - name: Apply Infrastructure
        run: fasttrack apply --directory ./terraform-production-app --auto-approve --timeout 600

      - name: Save Outputs
        run: fasttrack output --directory ./terraform-production-app --json > outputs.json
```

---

### Use Case 5: Development to Production Promotion

**Goal:** Promote tested configuration from dev to prod.

```bash
# Development
fasttrack generate --config-file config-dev.yaml
fasttrack apply --directory ./terraform-myapp-dev

# Test in dev...

# Staging (identical config, different environment)
fasttrack generate --config-file config-staging.yaml
fasttrack apply --directory ./terraform-myapp-staging

# Test in staging...

# Production (with remote state)
fasttrack generate --config-file config-prod.yaml
fasttrack apply --directory ./terraform-myapp-prod

# Verify production
fasttrack output --directory ./terraform-myapp-prod
az group show -n myapp-prod-rg
```

---

### Use Case 6: Resource Cleanup

**Goal:** Remove all resources when project is complete.

```bash
# Option 1: Using Fasttrack
fasttrack destroy --directory ./terraform-myproject

# Option 2: Using Azure CLI (faster)
az group delete -n myproject-rg --yes --no-wait

# Option 3: Destroy specific resources
cd terraform-myproject
terraform destroy -target=azurerm_storage_container.container_1
terraform destroy -target=azurerm_storage_account.main
```

---

### Use Case 7: Configuration Validation

**Goal:** Validate configuration before applying.

```bash
# Step 1: Dry run
fasttrack generate \
  --project-name myproject \
  --resource-group myproject-rg \
  --app-name myproject-app \
  --storage-account myprojectstg123 \
  --containers data \
  --dry-run

# Step 2: Generate files
fasttrack generate --config-file config.yaml

# Step 3: Validate
fasttrack check --directory ./terraform-myproject

# Step 4: Plan only (don't apply)
cd terraform-myproject
terraform plan

# Step 5: Apply when ready
fasttrack apply --directory ./terraform-myproject
```

---

## Command Cheat Sheet

### Quick Reference

```bash
# Generate basic infrastructure
fasttrack generate --project-name PROJECT --resource-group RG

# Generate with app
fasttrack generate --project-name PROJECT --resource-group RG --app-name APP --redirect-url URL

# Generate with storage
fasttrack generate --project-name PROJECT --resource-group RG --storage-account STORAGE --containers CONTAINER

# Generate full stack
fasttrack generate --project-name PROJECT --resource-group RG --app-name APP --redirect-url URL --storage-account STORAGE --containers CONTAINER

# Use YAML config
fasttrack generate --config-file config.yaml

# Apply
fasttrack apply --directory DIR
fasttrack apply --directory DIR --auto-approve

# Get outputs
fasttrack output --directory DIR
fasttrack output --directory DIR --name OUTPUT_NAME
fasttrack output --directory DIR --json

# Destroy
fasttrack destroy --directory DIR
fasttrack destroy --directory DIR --auto-approve

# Check/Validate
fasttrack check --directory DIR
fasttrack check --config-file config.yaml

# Import resources
fasttrack init-import --directory DIR
fasttrack import-resource --directory DIR --address ADDRESS --id ID
```

---

## Environment Variables

The CLI respects standard Azure environment variables:

```bash
# Azure authentication
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"

# Or use Azure CLI login
az login
az account set --subscription "your-subscription-id"
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Validation error |
| 3 | Terraform error |
| 4 | Azure CLI error |

---

## Additional Resources

- [README.md](./README.md) - Project overview and getting started
- [ISSUE_RESOLUTION.md](./ISSUE_RESOLUTION.md) - Troubleshooting guide
- [SUCCESS_VALIDATION.md](./SUCCESS_VALIDATION.md) - End-to-end validation
- [HANDLING_EXISTING_RESOURCES.md](./HANDLING_EXISTING_RESOURCES.md) - Import workflow
- [EXISTING_STORAGE_GUIDE.md](./EXISTING_STORAGE_GUIDE.md) - Existing storage usage
- [PRODUCTION_FEATURES.md](./PRODUCTION_FEATURES.md) - Production features

---

**Last Updated:** 2025-10-04
**CLI Version:** 1.0.0
**Status:** Production Ready ✅
