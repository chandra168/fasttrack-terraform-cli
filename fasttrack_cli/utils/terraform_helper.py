"""Terraform helper functions"""

import subprocess
import os
import click
from pathlib import Path
from typing import Optional


def run_terraform_command(command: list, cwd: str) -> tuple[bool, str]:
    """
    Execute Terraform command.

    Args:
        command: List of command arguments
        cwd: Working directory

    Returns:
        Tuple of (success, output)
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=True
        )
        return True, result.stdout + result.stderr

    except subprocess.CalledProcessError as e:
        return False, e.stderr or str(e)
    except Exception as e:
        return False, str(e)


def terraform_init(directory: str) -> bool:
    """Initialize Terraform in directory"""
    click.echo("Initializing Terraform...")
    success, output = run_terraform_command(["terraform", "init"], directory)

    if success:
        click.secho("✓ Terraform initialized successfully", fg="green")
    else:
        click.secho(f"✗ Terraform init failed: {output}", fg="red")

    return success


def terraform_validate(directory: str) -> bool:
    """Run terraform validate"""
    click.echo("Validating Terraform configuration...")
    success, output = run_terraform_command(["terraform", "validate"], directory)

    click.echo(output)

    if success:
        click.secho("✓ Terraform configuration is valid", fg="green")
    else:
        click.secho("✗ Terraform validation failed", fg="red")

    return success


def terraform_plan(directory: str) -> bool:
    """Run terraform plan"""
    click.echo("Running Terraform plan...")
    success, output = run_terraform_command(["terraform", "plan"], directory)

    click.echo(output)

    if success:
        click.secho("✓ Terraform plan completed", fg="green")
    else:
        click.secho("✗ Terraform plan failed", fg="red")

    return success


def terraform_apply(directory: str, auto_approve: bool = False) -> bool:
    """Run terraform apply"""
    click.echo("Applying Terraform configuration...")

    command = ["terraform", "apply"]
    if auto_approve:
        command.append("-auto-approve")

    success, output = run_terraform_command(command, directory)

    click.echo(output)

    if success:
        click.secho("✓ Terraform apply completed successfully", fg="green")
    else:
        click.secho("✗ Terraform apply failed", fg="red")

    return success


def terraform_destroy(directory: str, auto_approve: bool = False) -> bool:
    """Run terraform destroy"""
    click.echo("Destroying Terraform-managed resources...")

    command = ["terraform", "destroy"]
    if auto_approve:
        command.append("-auto-approve")

    success, output = run_terraform_command(command, directory)

    click.echo(output)

    if success:
        click.secho("✓ Terraform destroy completed", fg="green")
    else:
        click.secho("✗ Terraform destroy failed", fg="red")

    return success


def terraform_output(directory: str, output_name: Optional[str] = None) -> tuple[bool, str]:
    """Get terraform output"""
    command = ["terraform", "output"]
    if output_name:
        command.extend(["-raw", output_name])
    else:
        command.append("-json")

    return run_terraform_command(command, directory)


def check_terraform_installed() -> bool:
    """Check if Terraform is installed"""
    try:
        result = subprocess.run(
            ["terraform", "version"],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def terraform_import(directory: str, resource_address: str, resource_id: str) -> bool:
    """Import existing resource into Terraform state"""
    click.echo(f"Importing {resource_address}...")

    command = ["terraform", "import", resource_address, resource_id]
    success, output = run_terraform_command(command, directory)

    click.echo(output)

    if success:
        click.secho(f"✓ Resource imported successfully", fg="green")
    else:
        click.secho(f"✗ Import failed", fg="red")

    return success


def validate_terraform_installation():
    """Validate Terraform installation and raise exception if not found"""
    if not check_terraform_installed():
        raise click.ClickException(
            "Terraform is not installed. Please install Terraform first.\n"
            "Visit: https://www.terraform.io/downloads"
        )
