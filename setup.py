from setuptools import setup, find_packages

setup(
    name="fasttrack-terraform-cli",
    version="1.0.0",
    description="CLI tool for managing Azure resources via Terraform",
    author="Fasttrack Team",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "jinja2>=3.0.0",
        "pyyaml>=6.0",
        "azure-cli-core>=2.40.0",
        "colorama>=0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "fasttrack=fasttrack_cli.cli:cli",
        ],
    },
    python_requires=">=3.8",
)
