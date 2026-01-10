#!/usr/bin/env python3
"""Validate environment configuration."""
import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from typing import List, Tuple


def check_required_vars() -> List[Tuple[str, bool, str]]:
    """Check required environment variables."""
    required_vars = [
        ("SECRET_KEY", True, "Application secret key"),
        ("ENCRYPTION_KEY", True, "PII encryption key (32 bytes or will be hashed)"),
        ("JWT_SECRET", True, "JWT token secret"),
        ("DATABASE_URL", True, "PostgreSQL database URL"),
        ("REDIS_URL", False, "Redis URL (optional, uses in-memory fallback)"),
        ("OPENAI_API_KEY", False, "OpenAI API key (optional, for LLM features)"),
        ("ANTHROPIC_API_KEY", False, "Anthropic API key (optional, for LLM features)"),
    ]
    
    results = []
    for var_name, required, description in required_vars:
        value = os.getenv(var_name) or getattr(settings, var_name.lower(), None)
        is_set = value is not None and value != ""
        
        if required and not is_set:
            results.append((var_name, False, description))
        else:
            results.append((var_name, is_set, description))
    
    return results


def check_optional_config() -> List[Tuple[str, bool, str]]:
    """Check optional but recommended configuration."""
    optional_vars = [
        ("FRONTEND_URL", "Frontend URL for CORS"),
        ("API_URL", "API URL for documentation"),
        ("LLM_MODEL", "LLM model name"),
        ("LEGACY_DB_HOST", "Legacy database host"),
        ("SOAP_API_URL", "SOAP API URL"),
        ("SHAREPOINT_URL", "SharePoint URL"),
    ]
    
    results = []
    for var_name, description in optional_vars:
        value = os.getenv(var_name) or getattr(settings, var_name.lower(), None)
        is_set = value is not None and value != ""
        results.append((var_name, is_set, description))
    
    return results


def main():
    """Main validation function."""
    print("=" * 60)
    print("Environment Configuration Validation")
    print("=" * 60)
    print()
    
    # Check required variables
    print("Required Variables:")
    print("-" * 60)
    required_results = check_required_vars()
    all_required_ok = True
    
    for var_name, is_set, description in required_results:
        status = "✓" if is_set else "✗"
        required_mark = "[REQUIRED]" if required_results.index((var_name, is_set, description)) < len([r for r in required_results if r[1] is False]) else ""
        print(f"{status} {var_name:25s} {description} {required_mark}")
        if not is_set and required_results.index((var_name, is_set, description)) < len(required_results):
            all_required_ok = False
    
    print()
    
    # Check optional variables
    print("Optional Variables:")
    print("-" * 60)
    optional_results = check_optional_config()
    
    for var_name, is_set, description in optional_results:
        status = "✓" if is_set else "○"
        print(f"{status} {var_name:25s} {description}")
    
    print()
    print("=" * 60)
    
    # Summary
    required_count = sum(1 for _, is_set, _ in required_results if is_set)
    required_total = len(required_results)
    optional_count = sum(1 for _, is_set, _ in optional_results if is_set)
    optional_total = len(optional_results)
    
    print(f"Required: {required_count}/{required_total} configured")
    print(f"Optional: {optional_count}/{optional_total} configured")
    print()
    
    if all_required_ok:
        print("✓ All required variables are configured!")
        print("  System is ready for deployment.")
        return 0
    else:
        print("✗ Some required variables are missing!")
        print("  Please configure all required variables before deployment.")
        print()
        print("  Copy .env.example to .env and fill in the values:")
        print("  cp .env.example .env")
        return 1


if __name__ == "__main__":
    sys.exit(main())

