#!/usr/bin/env python3

"""gmsh eschews standard tooling to implement its own wheel builder:

  utils/pypi/sdktowheel.py

We can't easily produce a Python-only wheel from this script, so we implement our
own parallel conda-forge-oriented system here for staging the wheel contents into
the site-packages/ directory and generating metadata.
"""

import os
import re
from pathlib import Path
from string import Template
from typing import TypedDict, Union


class MetadataSubstitutions(TypedDict):
    """These are template variables to be substituted into the METADATA.in template."""

    GMSH_PYTHON_VERSION: str
    GMSH_LONG_DESCRIPTION: str


EXTRACT_VERSION_FROM_GMSH_PY_REGEX = r'^\s*GMSH_API_VERSION\s*=\s*"([^"]+)"'


class ResolvePaths:
    """Determine paths to the various files needed to generate the wheel."""

    def repo_root(self) -> Path:
        """Assumes execution from the Git repo root.
        
        ./
        """
        repo_root = Path.cwd()
        if not (repo_root / ".git").is_dir():
            print(
                "WARNING: Expected to find a Git repository in the current directory. "
                "Change into the Git repo root and run this script again."
            )
        return repo_root

    def site_packages(self) -> Path:
        """The target site-packages directory

        $SP_DIR/
        
        Determined from the environment variable SP_DIR, which is set by conda-build.
        """
        try:
            site_packages_dir = os.environ["SP_DIR"]
        except KeyError:
            raise RuntimeError(
                "Environment variable SP_DIR is not set. This script must run under "
                "conda-build or with SP_DIR pointing to the site-packages directory."
            )
        return Path(site_packages_dir)

    def dist_info(self, version: str) -> Path:
        """The metadata directory for the wheel
        
        $SP_DIR/gmsh-<version>.dist-info/
        """
        return self.site_packages() / f"gmsh-{version}.dist-info"

    def src_gmsh_py(self) -> Path:
        """The gmsh.py from the repository
        
        ./api/gmsh.py
        """
        return self.repo_root() / "api" / "gmsh.py"

    def src_readme(self) -> Path:
        """The README from the repository
        
        ./utils/pypi/README.gmsh.rst
        """
        return self.repo_root() / "utils" / "pypi" / "README.gmsh.rst"

    def src_metadata_template(self) -> Path:
        """The template for the metadata file"""
        return self.repo_root() / "utils" / "pypi" / "METADATA.in"

    def dest_gmsh_py(self) -> Path:
        """The gmsh.py to be created in the site-packages directory
        
        $SP_DIR/gmsh.py
        """
        return self.site_packages() / "gmsh.py"

    def dest_metadata_path(self, version: str) -> Path:
        """The METADATA file to be created in the dist-info directory
        
        $SP_DIR/gmsh-<version>.dist-info/METADATA
        """
        return self.dist_info(version) / "METADATA"


def extract_version_from_gmsh_py(src_gmsh_py: Union[Path, str]) -> str:
    """Get the version from the gmsh.py file.

    Uses a regex to extract the static value of GMSH_API_VERSION from the gmsh.py file.
    """
    src_gmsh_py = Path(src_gmsh_py)
    text = src_gmsh_py.read_text(encoding="utf-8")
    match = re.search(EXTRACT_VERSION_FROM_GMSH_PY_REGEX, text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not parse GMSH_API_VERSION from {src_gmsh_py}")
    return match.group(1)


def generate_metadata_contents_from_template(
    version: str,
    src_readme: Union[Path, str],
    src_metadata_template: Union[Path, str],
) -> str:
    """Substitute variables into METADATA.in"""
    src_readme = Path(src_readme)
    src_metadata_template = Path(src_metadata_template)

    # Read README and template
    long_desc = src_readme.read_text(encoding="utf-8")
    template_content = src_metadata_template.read_text(encoding="utf-8")

    # Prepare substitutions
    substitutions: MetadataSubstitutions = {
        "GMSH_PYTHON_VERSION": version,
        "GMSH_LONG_DESCRIPTION": long_desc,
    }

    # Substitute template variables
    try:
        return Template(template_content).substitute(substitutions)
    except KeyError as e:
        missing = e.args[0]
        raise RuntimeError(
            f"Unsupported substitution in template {src_metadata_template}: "
            f"{missing}. This likely means a new template variable was added "
            "upstream and should be implemented here."
        )


def main() -> None:
    print("Staging the wheel into the site-packages directory...")

    # Instantiate path manager to compute paths to necessary files on demand
    paths = ResolvePaths()

    # Extract version
    version = extract_version_from_gmsh_py(paths.src_gmsh_py())
    print(f"Extracted version {version} from {paths.src_gmsh_py()}.")

    # Ensure dist-info dir exists
    paths.dist_info(version).mkdir(parents=True, exist_ok=True)
    print(f"Metadata will be written to {paths.dist_info(version)}")

    # Copy gmsh.py
    paths.dest_gmsh_py().write_bytes(paths.src_gmsh_py().read_bytes())
    print(f"Copied {paths.src_gmsh_py()} to {paths.dest_gmsh_py()}")

    # Render METADATA
    metadata_contents = generate_metadata_contents_from_template(
        version, paths.src_readme(), paths.src_metadata_template()
    )

    # Write METADATA
    paths.dest_metadata_path(version).write_text(metadata_contents, encoding="utf-8")
    print(f"Wrote METADATA to {paths.dest_metadata_path(version)}")


if __name__ == "__main__":
    main()
    print("Successfully staged the wheel into the site-packages directory.")
