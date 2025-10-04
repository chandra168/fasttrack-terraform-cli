# Using Existing Storage Accounts

## Overview

The CLI now supports adding containers to existing storage accounts without recreating or modifying the storage account itself. This is useful when:

- You have a pre-existing storage account that shouldn't be managed by Terraform
- You want to add new containers without risking changes to the storage account configuration
- Multiple teams share a storage account but manage their own containers
- Compliance requires storage accounts to be created through a different process

---

## How It Works

When you set `--use-existing-storage` flag (or `use_existing_storage: true` in YAML), the CLI:

1. Uses a Terraform **data source** to reference the existing storage account (read-only)
2. Creates only the **containers** you specify
3. Does **NOT** create, modify, or manage the storage account itself

This means:
- ✅ Containers will be created in the existing storage account
- ✅ Container creation will fail gracefully if they already exist
- ✅ Storage account settings remain unchanged
- ✅ No risk of Terraform trying to recreate the storage account

---

## Usage

### Command Line

```bash
fasttrack generate \
  --project-name my-project \
  --resource-group my-rg \
  --storage-account existingstorageacct \
  --use-existing-storage \
  --containers data --containers logs --containers backups \
  --output-dir ./terraform-containers
```

### YAML Configuration

```yaml
project_name: my-project
resource_group: my-rg
storage_account: existingstorageacct
use_existing_storage: true
containers:
  - data
  - logs
  - backups
```

Then run:
```bash
fasttrack generate --config-file config.yaml
```

---

## Prerequisites

The existing storage account must:
1. **Already exist** in the specified resource group
2. Be in the **same resource group** as defined in your configuration
3. Have the **exact name** you specify in `--storage-account`

If the storage account doesn't exist, Terraform will fail during the plan/apply phase with an error like:
```
Error: reading Storage Account "existingstorageacct": storage.AccountsClient#GetProperties:
Failure responding to request: StatusCode=404 -- Original Error: autorest/azure:
Service returned an error. Status=404 Code="ResourceNotFound"
Message="The Resource 'Microsoft.Storage/storageAccounts/existingstorageacct'
under resource group 'my-rg' was not found."
```

---

## Generated Terraform Configuration

### With Existing Storage Account

When `--use-existing-storage` is set:

```hcl
# Use existing storage account (data source - read only)
data "azurerm_storage_account" "existing" {
  name                = var.storage_account_name
  resource_group_name = azurerm_resource_group.main.name
}

# Create storage containers
resource "azurerm_storage_container" "container_1" {
  name                  = "data"
  storage_account_name  = data.azurerm_storage_account.existing.name
  container_access_type = "private"

  metadata = {
    environment = var.environment
    project     = var.project_name
    created_by  = "terraform"
  }
}
```

### Without Existing Storage Account (Default)

When `--use-existing-storage` is **not** set:

```hcl
# Create new storage account (managed resource)
resource "azurerm_storage_account" "main" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  min_tls_version                 = "TLS1_2"
  https_traffic_only_enabled      = true
  allow_nested_items_to_be_public = false

  tags = {
    environment = var.environment
    project     = var.project_name
    managed_by  = "terraform"
    created_by  = "fasttrack-cli"
  }
}

# Create storage containers
resource "azurerm_storage_container" "container_1" {
  name                  = "data"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}
```

---

## Common Scenarios

### Scenario 1: Add Containers to Shared Storage Account

Your organization has a centrally-managed storage account:

```yaml
# containers-only-config.yaml
project_name: team-containers
resource_group: shared-storage-rg
storage_account: companysharedstorage
use_existing_storage: true
containers:
  - team-a-data
  - team-a-logs
```

```bash
fasttrack generate --config-file containers-only-config.yaml
fasttrack apply --directory ./terraform-generated
```

### Scenario 2: Migrate Existing Infrastructure to Terraform

You have manually created resources and want to manage containers with Terraform:

```bash
# Step 1: Generate config that uses existing storage
fasttrack generate \
  --project-name migration-project \
  --resource-group prod-rg \
  --storage-account prodstorageacct \
  --use-existing-storage \
  --containers existing-container-1 --containers existing-container-2

# Step 2: Import existing containers into Terraform state
fasttrack import-resource \
  --directory ./terraform-generated \
  --resource-address azurerm_storage_container.container_1 \
  --resource-id "/subscriptions/xxxx/resourceGroups/prod-rg/providers/Microsoft.Storage/storageAccounts/prodstorageacct/blobServices/default/containers/existing-container-1"

fasttrack import-resource \
  --directory ./terraform-generated \
  --resource-address azurerm_storage_container.container_2 \
  --resource-id "/subscriptions/xxxx/resourceGroups/prod-rg/providers/Microsoft.Storage/storageAccounts/prodstorageacct/blobServices/default/containers/existing-container-2"

# Step 3: Verify with plan
cd terraform-generated && terraform plan
```

### Scenario 3: Create New Containers Without Modifying Existing Ones

You already have some containers and want to add more:

```yaml
project_name: additional-containers
resource_group: my-rg
storage_account: mystorageacct
use_existing_storage: true
containers:
  - new-container-1    # Will be created
  - new-container-2    # Will be created
  # existing-container - Not in list, won't be touched
```

**Note:** Terraform will only manage the containers you specify. Existing containers not in the configuration will be ignored.

---

## Differences Between Modes

| Feature | `use_existing_storage: false` (default) | `use_existing_storage: true` |
|---------|----------------------------------------|------------------------------|
| Storage Account | Creates new storage account | Uses existing (data source) |
| Storage Tier | Applied from config | Ignored (uses existing) |
| Replication Type | Applied from config | Ignored (uses existing) |
| Security Settings | Enforces TLS 1.2, HTTPS only | Uses existing settings |
| Tags | Adds Terraform tags | Does not modify tags |
| Terraform State | Manages storage account | Only manages containers |
| Risk | May recreate storage account if drift | Read-only, safe |

---

## Best Practices

### 1. Use for Compliance-Controlled Resources

If storage accounts must be created by a security team or governance process:

```yaml
use_existing_storage: true
```

### 2. Document Ownership

Add comments to your config:

```yaml
# Storage account managed by: Platform Team
# Contact: platform@example.com
# Ticket: INFRA-1234
storage_account: platformmanagedacct
use_existing_storage: true
```

### 3. Import Existing Containers

If containers already exist, import them first:

```bash
# Get container resource ID
CONTAINER_ID="/subscriptions/xxx/resourceGroups/my-rg/providers/Microsoft.Storage/storageAccounts/myacct/blobServices/default/containers/mycontainer"

# Import into Terraform state
fasttrack import-resource \
  --resource-address azurerm_storage_container.container_1 \
  --resource-id "$CONTAINER_ID"
```

### 4. Verify Before Apply

Always run plan first to see what will be created:

```bash
fasttrack generate --config-file config.yaml --dry-run  # Preview files
cd terraform-generated
terraform init
terraform plan  # Preview changes
```

---

## Troubleshooting

### Error: Storage Account Not Found

```
Error: reading Storage Account: storage.AccountsClient#GetProperties:
Failure responding to request: StatusCode=404
```

**Solution:** Verify the storage account exists and is in the correct resource group:

```bash
az storage account show \
  --name existingstorageacct \
  --resource-group my-rg
```

### Error: Container Already Exists

```
Error: A resource with the ID "/subscriptions/.../containers/mycontainer" already exists
```

**Solution:** Import the existing container:

```bash
fasttrack import-resource \
  --resource-address azurerm_storage_container.container_1 \
  --resource-id "/subscriptions/xxx/.../containers/mycontainer"
```

### Warning: Storage Account in Different Resource Group

The data source assumes the storage account is in the same resource group as your Terraform configuration. If it's in a different RG, you'll need to manually modify the generated `main.tf`:

```hcl
data "azurerm_storage_account" "existing" {
  name                = var.storage_account_name
  resource_group_name = "different-rg"  # Change this
}
```

---

## Migration Path: From Manual to Terraform-Managed

If you want to eventually manage the storage account with Terraform:

### Phase 1: Containers Only
```yaml
use_existing_storage: true
containers:
  - container1
  - container2
```

### Phase 2: Import Storage Account
```bash
# Import the storage account
fasttrack import-resource \
  --resource-address azurerm_storage_account.main \
  --resource-id "/subscriptions/xxx/resourceGroups/my-rg/providers/Microsoft.Storage/storageAccounts/myacct"

# Manually update main.tf to change data source to resource
```

### Phase 3: Full Management
```yaml
use_existing_storage: false  # Now Terraform manages everything
containers:
  - container1
  - container2
```

---

## See Also

- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Complete CLI usage guide
- [example-config.yaml](example-config.yaml) - Example configurations
- [PRODUCTION_FEATURES.md](PRODUCTION_FEATURES.md) - All production features

---

**Last Updated:** 2025-10-04
**Version:** 1.1.0
