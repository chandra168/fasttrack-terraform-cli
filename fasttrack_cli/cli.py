"""Main CLI entry point for Fasttrack Terraform CLI"""

import click
import os
import sys
from pathlib import Path
from typing import Optional

from .utils.azure_helper import (
    validate_azure_login,
    get_current_subscription,
    resource_group_exists,
    storage_account_exists,
    app_registration_exists
)
from .utils.terraform_helper import (
    validate_terraform_installation,
    terraform_init,
    terraform_validate,
    terraform_plan,
    terraform_apply,
    terraform_destroy,
    terraform_output,
    terraform_import
)
from .utils.template_generator import TerraformTemplateGenerator, validate_config


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Fasttrack Terraform CLI - Manage Azure resources with Terraform"""
    pass


@cli.command()
@click.option('--project-name', help='Project name')
@click.option('--resource-group', help='Resource group name')
@click.option('--location', default='eastus', help='Azure region (default: eastus)')
@click.option('--environment', default='development', help='Environment name (default: development)')
@click.option('--app-name', help='Azure AD app registration name')
@click.option('--redirect-url', help='OAuth redirect URL for app registration')
@click.option('--storage-account', help='Storage account name (3-24 lowercase alphanumeric chars)')
@click.option('--containers', multiple=True, help='Storage container names (can specify multiple)')
@click.option('--storage-tier', default='Standard', type=click.Choice(['Standard', 'Premium']), help='Storage tier')
@click.option('--storage-replication', default='LRS', type=click.Choice(['LRS', 'GRS', 'RAGRS', 'ZRS']), help='Storage replication type')
@click.option('--secret-rotation-months', default=12, type=int, help='Client secret rotation period in months')
@click.option('--output-dir', default='./terraform-generated', help='Output directory for Terraform files')
@click.option('--skip-validation', is_flag=True, help='Skip Azure login validation')
@click.option('--dry-run', is_flag=True, help='Show what would be generated without writing files')
@click.option('--config-file', type=click.Path(exists=True), help='Load configuration from YAML file')
@click.option('--enable-remote-state', is_flag=True, help='Add remote state backend configuration')
@click.option('--state-storage-account', help='Storage account for remote state')
@click.option('--state-container', default='tfstate', help='Container name for remote state')
@click.option('--state-key', help='State file key (default: <project-name>.tfstate)')
def generate(project_name, resource_group, location, environment, app_name, redirect_url,
             storage_account, containers, storage_tier, storage_replication,
             secret_rotation_months, output_dir, skip_validation, dry_run, config_file,
             enable_remote_state, state_storage_account, state_container, state_key):
    """Generate Terraform configuration files"""

    click.secho("\n🚀 Fasttrack Terraform CLI - Generate Configuration", fg="cyan", bold=True)
    click.echo("=" * 60)

    # Load configuration from file if provided
    if config_file:
        import yaml
        click.echo(f"📄 Loading configuration from: {config_file}")
        try:
            with open(config_file, 'r') as f:
                file_config = yaml.safe_load(f)
                # Command line args override file config
                project_name = project_name or file_config.get('project_name')
                resource_group = resource_group or file_config.get('resource_group')
                location = file_config.get('location', location)
                environment = file_config.get('environment', environment)
                app_name = app_name or file_config.get('app_name')
                redirect_url = redirect_url or file_config.get('redirect_url')
                storage_account = storage_account or file_config.get('storage_account')
                containers = containers or tuple(file_config.get('containers', []))
                storage_tier = file_config.get('storage_tier', storage_tier)
                storage_replication = file_config.get('storage_replication', storage_replication)
                secret_rotation_months = file_config.get('secret_rotation_months', secret_rotation_months)

                # Remote state config from file
                if 'remote_state' in file_config:
                    enable_remote_state = True
                    rs = file_config['remote_state']
                    state_storage_account = state_storage_account or rs.get('storage_account')
                    state_container = rs.get('container', state_container)
                    state_key = state_key or rs.get('key')

                click.secho("✓ Configuration loaded from file", fg="green")
        except Exception as e:
            click.secho(f"✗ Error loading config file: {str(e)}", fg="red")
            sys.exit(1)

    # Ensure required fields are present
    if not project_name:
        click.secho("✗ project_name is required (via --project-name or config file)", fg="red")
        sys.exit(1)
    if not resource_group:
        click.secho("✗ resource_group is required (via --resource-group or config file)", fg="red")
        sys.exit(1)

    # Validate prerequisites
    if not skip_validation and not dry_run:
        try:
            validate_azure_login()
            click.secho("✓ Azure CLI authenticated", fg="green")
        except click.ClickException as e:
            click.secho(f"✗ {str(e)}", fg="red")
            sys.exit(1)

    try:
        validate_terraform_installation()
        click.secho("✓ Terraform installed", fg="green")
    except click.ClickException as e:
        click.secho(f"✗ {str(e)}", fg="red")
        sys.exit(1)

    # Build configuration
    config = {
        "project_name": project_name,
        "resource_group_name": resource_group,
        "location": location,
        "environment": environment,
        "create_app_registration": bool(app_name),
        "create_storage": bool(storage_account),
        "storage_tier": storage_tier,
        "storage_replication": storage_replication,
        "secret_rotation_months": secret_rotation_months,
        "secret_display_name": "Generated by Fasttrack CLI",
        "enable_remote_state": enable_remote_state,
        "state_storage_account": state_storage_account,
        "state_container": state_container,
        "state_key": state_key or f"{project_name}.tfstate"
    }

    if app_name:
        config.update({
            "azuread_app_name": app_name,
            "redirect_url": redirect_url or f"https://{app_name}.example.com/auth/callback"
        })

    if storage_account:
        config.update({
            "storage_account_name": storage_account,
            "storage_containers": list(containers) if containers else []
        })

    # Validate configuration
    is_valid, error_msg = validate_config(config)
    if not is_valid:
        click.secho(f"✗ Configuration error: {error_msg}", fg="red")
        sys.exit(1)

    click.secho("✓ Configuration validated", fg="green")

    # Display configuration summary
    click.echo("\n📋 Configuration Summary:")
    click.echo(f"  Project: {project_name}")
    click.echo(f"  Resource Group: {resource_group}")
    click.echo(f"  Location: {location}")
    click.echo(f"  Environment: {environment}")

    if app_name:
        click.echo(f"  App Registration: {app_name}")
        click.echo(f"  Redirect URL: {config['redirect_url']}")

    if storage_account:
        click.echo(f"  Storage Account: {storage_account}")
        click.echo(f"  Storage Tier: {storage_tier}")
        click.echo(f"  Replication: {storage_replication}")
        if containers:
            click.echo(f"  Containers: {', '.join(containers)}")

    if enable_remote_state:
        click.echo(f"\n🔄 Remote State:")
        click.echo(f"  Storage Account: {state_storage_account}")
        click.echo(f"  Container: {state_container}")
        click.echo(f"  Key: {config['state_key']}")

    # Dry run mode
    if dry_run:
        click.echo("\n" + "=" * 60)
        click.secho("🔍 DRY RUN MODE - No files will be written", fg="yellow", bold=True)
        click.echo("\n📄 Files that would be generated:")
        click.echo(f"  {output_dir}/main.tf")
        click.echo(f"  {output_dir}/variables.tf")
        click.echo(f"  {output_dir}/data.tf")
        click.echo(f"  {output_dir}/outputs.tf")
        if enable_remote_state:
            click.echo(f"  {output_dir}/backend.tf")
        click.echo(f"\n✓ Configuration validated successfully")
        click.echo(f"\n💡 To generate files, run without --dry-run flag")
        return

    # Generate templates
    click.echo("\n📝 Generating Terraform files...")
    generator = TerraformTemplateGenerator()
    generator.generate(output_dir, config)

    click.echo("\n✅ Configuration generated successfully!")
    click.echo(f"\n📂 Next steps:")
    click.echo(f"  1. Review the generated files in: {output_dir}")
    click.echo(f"  2. Run: fasttrack apply --directory {output_dir}")
    click.echo(f"  3. Or manually run: cd {output_dir} && terraform init && terraform apply")


@cli.command()
@click.option('--directory', default='./terraform-generated', help='Terraform configuration directory')
@click.option('--auto-approve', is_flag=True, help='Skip interactive approval')
def apply(directory, auto_approve):
    """Apply Terraform configuration"""

    click.secho("\n🚀 Fasttrack Terraform CLI - Apply Configuration", fg="cyan", bold=True)
    click.echo("=" * 60)

    if not os.path.exists(directory):
        click.secho(f"✗ Directory not found: {directory}", fg="red")
        sys.exit(1)

    # Validate prerequisites
    try:
        validate_azure_login()
        validate_terraform_installation()
    except click.ClickException as e:
        click.secho(f"✗ {str(e)}", fg="red")
        sys.exit(1)

    # Show subscription info
    sub = get_current_subscription()
    if sub:
        click.echo(f"📌 Using subscription: {sub.get('name')} ({sub.get('id')})")

    # Initialize
    if not terraform_init(directory):
        sys.exit(1)

    click.echo()

    # Validate
    if not terraform_validate(directory):
        sys.exit(1)

    click.echo()

    # Plan
    if not terraform_plan(directory):
        sys.exit(1)

    click.echo()

    # Apply
    if not auto_approve:
        if not click.confirm('Do you want to apply these changes?'):
            click.echo("❌ Apply cancelled")
            sys.exit(0)

    if not terraform_apply(directory, auto_approve):
        sys.exit(1)

    click.echo("\n✅ Resources created successfully!")
    click.echo("\n📊 To view outputs, run:")
    click.echo(f"  fasttrack output --directory {directory}")


@cli.command()
@click.option('--directory', default='./terraform-generated', help='Terraform configuration directory')
@click.option('--output-name', help='Specific output to retrieve')
def output(directory, output_name):
    """Show Terraform outputs"""

    if not os.path.exists(directory):
        click.secho(f"✗ Directory not found: {directory}", fg="red")
        sys.exit(1)

    success, result = terraform_output(directory, output_name)

    if success:
        click.echo(result)
    else:
        click.secho(f"✗ Failed to get outputs: {result}", fg="red")
        sys.exit(1)


@cli.command()
@click.option('--directory', default='./terraform-generated', help='Terraform configuration directory')
@click.option('--auto-approve', is_flag=True, help='Skip interactive approval')
def destroy(directory, auto_approve):
    """Destroy Terraform-managed resources"""

    click.secho("\n🗑️  Fasttrack Terraform CLI - Destroy Resources", fg="red", bold=True)
    click.echo("=" * 60)

    if not os.path.exists(directory):
        click.secho(f"✗ Directory not found: {directory}", fg="red")
        sys.exit(1)

    # Validate prerequisites
    try:
        validate_azure_login()
        validate_terraform_installation()
    except click.ClickException as e:
        click.secho(f"✗ {str(e)}", fg="red")
        sys.exit(1)

    if not auto_approve:
        click.secho("\n⚠️  WARNING: This will destroy all resources managed by Terraform!", fg="yellow", bold=True)
        if not click.confirm('Are you sure you want to continue?'):
            click.echo("❌ Destroy cancelled")
            sys.exit(0)

    if not terraform_destroy(directory, auto_approve):
        sys.exit(1)

    click.echo("\n✅ Resources destroyed successfully!")


@cli.command()
@click.option('--directory', default='./terraform-generated', help='Terraform configuration directory')
@click.option('--resource-address', required=True, help='Terraform resource address (e.g., azurerm_resource_group.main)')
@click.option('--resource-id', required=True, help='Azure resource ID to import')
def import_resource(directory, resource_address, resource_id):
    """Import existing Azure resource into Terraform state"""

    click.secho("\n📥 Fasttrack Terraform CLI - Import Resource", fg="cyan", bold=True)
    click.echo("=" * 60)

    if not os.path.exists(directory):
        click.secho(f"✗ Directory not found: {directory}", fg="red")
        sys.exit(1)

    # Validate prerequisites
    try:
        validate_azure_login()
        validate_terraform_installation()
    except click.ClickException as e:
        click.secho(f"✗ {str(e)}", fg="red")
        sys.exit(1)

    # Initialize if needed
    terraform_dir = Path(directory)
    if not (terraform_dir / ".terraform").exists():
        click.echo("Terraform not initialized. Running init...")
        if not terraform_init(directory):
            sys.exit(1)
        click.echo()

    # Import resource
    if not terraform_import(directory, resource_address, resource_id):
        sys.exit(1)

    click.echo("\n✅ Resource imported successfully!")
    click.echo(f"\n💡 Next steps:")
    click.echo(f"  1. Review the imported resource in Terraform state")
    click.echo(f"  2. Add corresponding configuration to your .tf files")
    click.echo(f"  3. Run: terraform plan to verify the import")


@cli.command()
def check():
    """Check prerequisites and Azure connection"""

    click.secho("\n🔍 Fasttrack Terraform CLI - Prerequisites Check", fg="cyan", bold=True)
    click.echo("=" * 60)

    # Check Azure CLI
    try:
        validate_azure_login()
        click.secho("✓ Azure CLI authenticated", fg="green")

        sub = get_current_subscription()
        if sub:
            click.echo(f"  Subscription: {sub.get('name')}")
            click.echo(f"  Tenant ID: {sub.get('tenantId')}")
            click.echo(f"  User: {sub.get('user', {}).get('name')}")
    except click.ClickException as e:
        click.secho(f"✗ Azure CLI: {str(e)}", fg="red")

    click.echo()

    # Check Terraform
    try:
        validate_terraform_installation()
        click.secho("✓ Terraform installed", fg="green")

        import subprocess
        result = subprocess.run(["terraform", "version"], capture_output=True, text=True)
        version_line = result.stdout.split('\n')[0]
        click.echo(f"  {version_line}")
    except click.ClickException as e:
        click.secho(f"✗ Terraform: {str(e)}", fg="red")

    click.echo("\n" + "=" * 60)


if __name__ == '__main__':
    cli()
