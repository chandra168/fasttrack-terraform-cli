# Fasttrack Terraform CLI

A powerful Click-based CLI tool for managing Azure resources through Terraform. Simplifies the creation of Azure AD App Registrations, Storage Accounts, and Blob Containers with customizable Terraform configurations.

## Features

- 🚀 **Easy Resource Creation**: Generate Terraform configurations with simple CLI commands
- 🔐 **Azure AD Integration**: Create app registrations with OAuth configurations
- 💾 **Storage Management**: Create storage accounts and multiple blob containers
- 📝 **Template-Based**: Uses Jinja2 templates for flexible Terraform generation
- ✅ **Validation**: Built-in validation for Azure CLI authentication and Terraform installation
- 🎯 **Best Practices**: Generates secure configurations with TLS 1.2, HTTPS-only, and proper tagging

## Prerequisites

1. **Python 3.8+**
2. **Azure CLI** - [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
3. **Terraform** - [Install Terraform](https://www.terraform.io/downloads)
4. **Azure Account** - Active Azure subscription

## Installation

### Option 1: Install from source

```bash
cd fasttrack-terraform-cli

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Option 2: Install dependencies only

```bash
pip install click jinja2 pyyaml azure-cli-core colorama
```

## Quick Start

### 1. Check Prerequisites

```bash
# Verify installation and Azure connection
fasttrack check
```

### 2. Login to Azure

```bash
az login
```

### 3. Generate Terraform Configuration

Create a complete infrastructure with app registration and storage:

```bash
fasttrack generate \
  --project-name my-project \
  --resource-group my-rg \
  --location eastus \
  --app-name my-app \
  --redirect-url https://my-app.example.com/auth/callback \
  --storage-account mystorageacct001 \
  --containers data logs backups \
  --output-dir ./my-terraform
```

### 4. Apply Configuration

```bash
# Review and apply the generated Terraform
fasttrack apply --directory ./my-terraform
```

### 5. View Outputs

```bash
# Show all outputs
fasttrack output --directory ./my-terraform

# Get specific output
fasttrack output --directory ./my-terraform --output-name client_secret
```

## Commands

### `fasttrack generate`

Generate Terraform configuration files.

**Options:**

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--project-name` | Yes | - | Project name for tagging |
| `--resource-group` | Yes | - | Azure resource group name |
| `--location` | No | eastus | Azure region |
| `--environment` | No | development | Environment name |
| `--app-name` | No | - | Azure AD app registration name |
| `--redirect-url` | No | Auto-generated | OAuth redirect URL |
| `--storage-account` | No | - | Storage account name (3-24 lowercase alphanumeric) |
| `--containers` | No | - | Storage container names (multiple allowed) |
| `--storage-tier` | No | Standard | Storage tier (Standard/Premium) |
| `--storage-replication` | No | LRS | Replication type (LRS/GRS/RAGRS/ZRS) |
| `--secret-rotation-months` | No | 12 | Client secret rotation period |
| `--output-dir` | No | ./terraform-generated | Output directory |
| `--skip-validation` | No | False | Skip Azure login validation |

**Examples:**

```bash
# Generate app registration only
fasttrack generate \
  --project-name my-api \
  --resource-group api-rg \
  --app-name my-api-app \
  --redirect-url https://api.example.com/callback

# Generate storage only
fasttrack generate \
  --project-name data-lake \
  --resource-group storage-rg \
  --storage-account datalakestg001 \
  --containers raw processed archived

# Generate both
fasttrack generate \
  --project-name fullstack \
  --resource-group fullstack-rg \
  --location westus2 \
  --environment production \
  --app-name fullstack-app \
  --storage-account fullstackstg001 \
  --containers uploads assets logs
```

### `fasttrack apply`

Apply Terraform configuration to create resources.

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--directory` | ./terraform-generated | Terraform config directory |
| `--auto-approve` | False | Skip interactive approval |

**Examples:**

```bash
# Interactive apply
fasttrack apply --directory ./my-terraform

# Auto-approve (CI/CD)
fasttrack apply --directory ./my-terraform --auto-approve
```

### `fasttrack output`

Show Terraform outputs.

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--directory` | ./terraform-generated | Terraform config directory |
| `--output-name` | - | Specific output to retrieve |

**Examples:**

```bash
# Show all outputs
fasttrack output --directory ./my-terraform

# Get client secret
fasttrack output --directory ./my-terraform --output-name client_secret

# Get application ID
fasttrack output --directory ./my-terraform --output-name application_id
```

### `fasttrack destroy`

Destroy all Terraform-managed resources.

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--directory` | ./terraform-generated | Terraform config directory |
| `--auto-approve` | False | Skip interactive approval |

**Examples:**

```bash
# Interactive destroy
fasttrack destroy --directory ./my-terraform

# Auto-approve
fasttrack destroy --directory ./my-terraform --auto-approve
```

### `fasttrack check`

Check prerequisites and Azure connection.

**Examples:**

```bash
fasttrack check
```

## Usage Examples

### Example 1: ArgoCD Application with Storage

Create an Azure AD app for ArgoCD with storage for manifests:

```bash
fasttrack generate \
  --project-name argocd \
  --resource-group argocd-rg \
  --location eastus \
  --environment production \
  --app-name argocd-oauth-app \
  --redirect-url https://argocd.company.com/auth/callback \
  --storage-account argocdstg001 \
  --containers manifests configs secrets \
  --output-dir ./argocd-terraform

fasttrack apply --directory ./argocd-terraform
```

### Example 2: Data Lake Storage Only

Create multiple storage containers for a data lake:

```bash
fasttrack generate \
  --project-name data-lake \
  --resource-group datalake-rg \
  --location westus2 \
  --storage-account datalakestg001 \
  --containers raw bronze silver gold \
  --storage-tier Standard \
  --storage-replication GRS \
  --output-dir ./datalake-terraform

fasttrack apply --directory ./datalake-terraform
```

### Example 3: Multi-Tenant App Registration

Create app registration with custom secret rotation:

```bash
fasttrack generate \
  --project-name saas-app \
  --resource-group saas-rg \
  --app-name saas-multitenant-app \
  --redirect-url https://app.saas.com/auth/callback \
  --secret-rotation-months 6 \
  --output-dir ./saas-terraform

fasttrack apply --directory ./saas-terraform

# Get the credentials
fasttrack output --directory ./saas-terraform --output-name application_id
fasttrack output --directory ./saas-terraform --output-name client_secret
fasttrack output --directory ./saas-terraform --output-name tenant_id
```

## Generated Resources

### When creating App Registration:

- ✅ Azure AD Application
- ✅ Service Principal
- ✅ Client Secret (with auto-rotation)
- ✅ OAuth2 permissions (User.Read, GroupMember.Read.All)
- ✅ Web redirect URI configuration

### When creating Storage:

- ✅ Storage Account (with security best practices)
- ✅ Blob Containers (as many as specified)
- ✅ Private access by default
- ✅ TLS 1.2 minimum
- ✅ HTTPS-only traffic

### Always created:

- ✅ Resource Group (if doesn't exist)
- ✅ Proper tagging (environment, project, managed_by)
- ✅ Comprehensive Terraform outputs

## Project Structure

```
fasttrack-terraform-cli/
├── fasttrack_cli/
│   ├── __init__.py
│   ├── cli.py                    # Main CLI entry point
│   ├── templates/
│   │   ├── main.tf.j2           # Main Terraform template
│   │   ├── variables.tf.j2      # Variables template
│   │   ├── data.tf.j2           # Data sources template
│   │   └── outputs.tf.j2        # Outputs template
│   └── utils/
│       ├── __init__.py
│       ├── azure_helper.py      # Azure CLI wrapper functions
│       ├── terraform_helper.py  # Terraform command wrappers
│       └── template_generator.py # Jinja2 template renderer
├── setup.py
├── requirements.txt
└── README.md
```

## Configuration

### Storage Account Naming Rules

- 3-24 characters
- Lowercase letters and numbers only
- Must be globally unique

**Valid:** `mystorageacct001`, `datastorage2024`
**Invalid:** `MyStorage`, `storage_account`, `st` (too short)

### App Registration Best Practices

- Use descriptive names
- Specify actual redirect URLs (not example.com in production)
- Rotate secrets regularly (default: 12 months)
- Grant only required permissions

## Troubleshooting

### Error: "Not logged into Azure"

```bash
az login
az account show
```

### Error: "Terraform is not installed"

Install Terraform from: https://www.terraform.io/downloads

### Error: "Storage account name already exists"

Storage account names must be globally unique. Try a different name.

### Error: "Permission denied" during apply

Ensure your Azure account has Contributor role on the subscription.

### View detailed Terraform logs

```bash
cd ./terraform-generated
TF_LOG=DEBUG terraform apply
```

## Advanced Usage

### Custom Terraform Variables

After generating, you can create a `terraform.tfvars` file:

```hcl
resource_group_name = "custom-rg"
location           = "westeurope"
environment        = "staging"
```

Then apply:

```bash
cd ./terraform-generated
terraform apply -var-file="terraform.tfvars"
```

### CI/CD Integration

```bash
# In your CI/CD pipeline
fasttrack generate \
  --project-name $PROJECT_NAME \
  --resource-group $RG_NAME \
  --app-name $APP_NAME \
  --storage-account $STORAGE_NAME \
  --skip-validation \
  --output-dir ./tf

fasttrack apply --directory ./tf --auto-approve
```

### Import Existing Resources

If you have existing resources:

```bash
cd ./terraform-generated
terraform init
terraform import azurerm_resource_group.main /subscriptions/{sub-id}/resourceGroups/{rg-name}
```

## Security Considerations

- ✅ Client secrets are marked as sensitive in Terraform
- ✅ TLS 1.2 enforced on all connections
- ✅ HTTPS-only traffic
- ✅ Private container access by default
- ✅ No public blob access allowed
- ✅ Automatic secret rotation
- ⚠️ Store Terraform state securely (use remote backend in production)
- ⚠️ Never commit `.terraform` directory or `terraform.tfstate` to git

## Contributing

To extend the CLI:

1. Add new templates in `fasttrack_cli/templates/`
2. Update `template_generator.py` for new resource types
3. Add CLI commands in `cli.py`
4. Update this README

## Support

For issues or questions:
- Check the troubleshooting section
- Review generated Terraform files
- Run `fasttrack check` to verify prerequisites

## License

Internal tool for Fasttrack project.

## Version

1.0.0
