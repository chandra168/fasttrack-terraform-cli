"""Terraform template generator using Jinja2"""

import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import click


class TerraformTemplateGenerator:
    """Generate Terraform configuration files from templates"""

    def __init__(self):
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate(self, output_dir: str, config: dict):
        """
        Generate Terraform files from templates.

        Args:
            output_dir: Directory to write generated files
            config: Configuration dictionary for template rendering
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate main.tf
        self._render_template("main.tf.j2", output_path / "main.tf", config)

        # Generate variables.tf
        self._render_template("variables.tf.j2", output_path / "variables.tf", config)

        # Generate data.tf
        self._render_template("data.tf.j2", output_path / "data.tf", config)

        # Generate outputs.tf
        self._render_template("outputs.tf.j2", output_path / "outputs.tf", config)

        click.secho(f"✓ Terraform configuration generated in: {output_dir}", fg="green")

    def _render_template(self, template_name: str, output_file: Path, config: dict):
        """Render a single template file"""
        template = self.env.get_template(template_name)
        content = template.render(**config)

        with open(output_file, 'w') as f:
            f.write(content)


def validate_config(config: dict) -> tuple[bool, str]:
    """
    Validate configuration dictionary.

    Args:
        config: Configuration to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = [
        "project_name",
        "resource_group_name",
        "location",
        "environment"
    ]

    for field in required_fields:
        if field not in config or not config[field]:
            return False, f"Missing required field: {field}"

    if config.get("create_storage"):
        if not config.get("storage_account_name"):
            return False, "storage_account_name is required when create_storage is True"

        # Validate storage account name (3-24 chars, lowercase alphanumeric)
        storage_name = config["storage_account_name"]
        if not (3 <= len(storage_name) <= 24):
            return False, "storage_account_name must be 3-24 characters"
        if not storage_name.isalnum() or not storage_name.islower():
            return False, "storage_account_name must be lowercase alphanumeric only"

    if config.get("create_app_registration"):
        if not config.get("azuread_app_name"):
            return False, "azuread_app_name is required when create_app_registration is True"
        if not config.get("redirect_url"):
            return False, "redirect_url is required when create_app_registration is True"

    return True, ""
