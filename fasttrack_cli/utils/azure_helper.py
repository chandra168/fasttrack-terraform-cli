"""Azure helper functions for CLI operations"""

import subprocess
import json
import click
from typing import Optional, Dict, Any


def run_az_command(command: list) -> tuple[bool, Optional[Dict[Any, Any]], Optional[str]]:
    """
    Execute Azure CLI command and return result.

    Args:
        command: List of command arguments

    Returns:
        Tuple of (success, result_dict, error_message)
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        if result.stdout:
            try:
                return True, json.loads(result.stdout), None
            except json.JSONDecodeError:
                return True, {"output": result.stdout}, None
        return True, {}, None

    except subprocess.CalledProcessError as e:
        return False, None, e.stderr or str(e)
    except Exception as e:
        return False, None, str(e)


def check_az_login() -> bool:
    """Check if user is logged into Azure CLI"""
    success, result, _ = run_az_command(["az", "account", "show"])
    return success


def get_current_subscription() -> Optional[Dict[str, Any]]:
    """Get current Azure subscription details"""
    success, result, _ = run_az_command(["az", "account", "show"])
    if success:
        return result
    return None


def get_tenant_id() -> Optional[str]:
    """Get current Azure tenant ID"""
    sub = get_current_subscription()
    if sub:
        return sub.get("tenantId")
    return None


def resource_group_exists(name: str) -> bool:
    """Check if resource group exists"""
    success, _, _ = run_az_command(["az", "group", "show", "--name", name])
    return success


def storage_account_exists(name: str, resource_group: str) -> bool:
    """Check if storage account exists"""
    success, _, _ = run_az_command([
        "az", "storage", "account", "show",
        "--name", name,
        "--resource-group", resource_group
    ])
    return success


def app_registration_exists(name: str) -> tuple[bool, Optional[str]]:
    """
    Check if app registration exists.

    Returns:
        Tuple of (exists, app_id)
    """
    success, result, _ = run_az_command([
        "az", "ad", "app", "list",
        "--filter", f"displayName eq '{name}'",
        "--query", "[].{{id:id,appId:appId}}"
    ])

    if success and result and len(result) > 0:
        return True, result[0].get("appId")
    return False, None


def validate_azure_login():
    """Validate Azure login and raise click exception if not logged in"""
    if not check_az_login():
        raise click.ClickException(
            "Not logged into Azure. Please run 'az login' first."
        )
