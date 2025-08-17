#!/usr/bin/env python3

"""
This script prevents accidentally dropping the noarch 'python-gmsh' build.

It is invoked by the GitHub Actions workflow at `.github/workflows/ensure-python-gmsh.yml`.

This script enforces that the selected occt (parsed from the selector in the recipe)
still appears in at least one rendered CI config (.ci_support/linux_64*.yaml). If not,
it fails with a prompt to update the selector.

Context:

In order to create a single build of the 'python-gmsh' package, we need to decide
on which build matrix entry it should be built. In particular, we need to specify
a platform (currently linux-64) and an available occt version.

As we migrate to newer occt versions, we need to ensure that the selected occt
version doesn't disappear from the matrix. Otherwise we would silently stop building
the 'python-gmsh' package.
"""

from __future__ import annotations

from pathlib import Path

import yaml


def find_python_gmsh_block(recipe_text: str) -> str:
    """Extract the python-gmsh output block as text."""
    lines = recipe_text.splitlines()
    
    for i, line in enumerate(lines):
        if "- name:" in line and "python-gmsh" in line:
            indent = len(line) - len(line.lstrip())
            block_lines = []
            
            for j in range(i + 1, len(lines)):
                next_line = lines[j]
                if next_line.strip() and len(next_line) - len(next_line.lstrip()) <= indent:
                    break  # Hit same or higher level
                block_lines.append(next_line)
            
            return "\n".join(block_lines)
    
    raise ValueError("Could not find python-gmsh output block")


def extract_occt_from_skip_selector(block_text: str) -> tuple[str, str]:
    """Extract the occt version from the skip selector comment."""
    for line in block_text.splitlines():
        if "skip:" in line and "occt !=" in line:
            # Extract quoted value after "occt !="
            start = line.find('occt != "')
            if start != -1:
                start += 9  # Skip 'occt != "'
                end = line.find('"', start)
                if end != -1:
                    return line[start:end], line
    
    raise ValueError("Could not find occt version in skip selector")


def check_ci_configs_for_occt(selected_occt: str) -> tuple[Path | None, list[str]]:
    """Check if selected occt exists in linux_64 CI configs."""
    all_occt_values = []
    
    for yml_path in sorted(Path(".ci_support").glob("linux_64*.yaml")):
        data = yaml.safe_load(yml_path.read_text())
        occt_list = data.get("occt", [])
        if not isinstance(occt_list, list):
            occt_list = [occt_list]
        occt_values = [str(v) for v in occt_list if v is not None]
        all_occt_values.extend(occt_values)
        if selected_occt in occt_values:
            return yml_path, all_occt_values
    
    return None, all_occt_values


def main() -> None:
    # Find recipe and extract python-gmsh block
    recipe_path = Path("recipe/meta.yaml")
    recipe_text = recipe_path.read_text()
    block_text = find_python_gmsh_block(recipe_text)
    print(f"python-gmsh output block:\n{block_text}")

    # Extract occt version from skip selector
    selected_occt, skip_line = extract_occt_from_skip_selector(block_text)
    print(f"Detected skip line:\n{skip_line}\n")
    print(f"Selected occt for python-gmsh: {selected_occt}\n")

    # Check if occt version exists in CI configs
    found_path, all_occt_values = check_ci_configs_for_occt(selected_occt)
    
    if not found_path:
        raise ValueError(f"No CI config uses occt={selected_occt}; python-gmsh would not build. "
                        f"Update the selector. Available occt values: {sorted(set(all_occt_values))}")

    print(f"Found occt={selected_occt} in {found_path}\n")
    print("OK: CI includes the selected occt; python-gmsh will be built.")


if __name__ == "__main__":
    main()
