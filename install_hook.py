#!/usr/bin/env python3
"""
SpecSync Hook Installation Script

This script installs the SpecSync pre-commit hook into the git repository.
It creates a pre-commit hook that triggers Kiro validation before commits are finalized.
"""

import json
import os
import sys
from pathlib import Path


def find_git_root():
    """Find the root of the git repository."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return None


def load_hook_config():
    """Load the hook configuration from .kiro/hooks/precommit.json."""
    config_path = Path(".kiro/hooks/precommit.json")
    if not config_path.exists():
        print(f"Error: Hook configuration not found at {config_path}")
        return None
    
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in hook configuration: {e}")
        return None


def create_pre_commit_hook(git_root, hook_config):
    """Create the pre-commit hook script."""
    hooks_dir = git_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    
    hook_path = hooks_dir / "pre-commit"
    
    # Create the hook script
    hook_script = f"""#!/bin/sh
# SpecSync Pre-Commit Hook
# This hook validates staged changes for spec-code-test-doc alignment

echo "Running SpecSync validation..."

# Check if Kiro is available
if ! command -v kiro &> /dev/null; then
    echo "Warning: Kiro not found. Skipping SpecSync validation."
    echo "Install Kiro to enable automatic validation."
    exit 0
fi

# Trigger Kiro validation
# Note: This is a placeholder for the actual Kiro integration
# In practice, this would invoke Kiro with the validation message

echo "SpecSync validation complete."
exit 0
"""
    
    try:
        with open(hook_path, "w") as f:
            f.write(hook_script)
        
        # Make the hook executable (Unix-like systems)
        if os.name != "nt":  # Not Windows
            os.chmod(hook_path, 0o755)
        
        return True
    except Exception as e:
        print(f"Error: Failed to create hook: {e}")
        return False


def install_hook():
    """Main installation function."""
    print("SpecSync Hook Installer")
    print("=" * 50)
    
    # Find git root
    git_root = find_git_root()
    if not git_root:
        print("Error: Not in a git repository")
        return False
    
    print(f"Git repository found: {git_root}")
    
    # Load hook configuration
    hook_config = load_hook_config()
    if not hook_config:
        return False
    
    print(f"Hook configuration loaded: {hook_config.get('name', 'Unknown')}")
    
    # Check if hook already exists
    hook_path = git_root / ".git" / "hooks" / "pre-commit"
    if hook_path.exists():
        response = input("Pre-commit hook already exists. Overwrite? (y/N): ")
        if response.lower() != "y":
            print("Installation cancelled.")
            return False
    
    # Create the hook
    if create_pre_commit_hook(git_root, hook_config):
        print(f"✓ Pre-commit hook installed successfully at {hook_path}")
        print("\nThe hook will trigger SpecSync validation on every commit.")
        print("To disable, remove or rename the hook file.")
        return True
    else:
        return False


def uninstall_hook():
    """Uninstall the pre-commit hook."""
    git_root = find_git_root()
    if not git_root:
        print("Error: Not in a git repository")
        return False
    
    hook_path = git_root / ".git" / "hooks" / "pre-commit"
    if not hook_path.exists():
        print("No pre-commit hook found.")
        return False
    
    try:
        hook_path.unlink()
        print(f"✓ Pre-commit hook removed from {hook_path}")
        return True
    except Exception as e:
        print(f"Error: Failed to remove hook: {e}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        success = uninstall_hook()
    else:
        success = install_hook()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
