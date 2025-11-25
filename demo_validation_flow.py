#!/usr/bin/env python3
"""
Demonstration script for the SpecSync validation flow.

This script shows how the validation orchestrator processes git context
and produces validation results.
"""
from backend.validator import ValidationOrchestrator, ValidationResult


def demo_successful_validation():
    """Demonstrate a successful validation with aligned code."""
    print("=" * 70)
    print("DEMO 1: Successful Validation (Aligned Code)")
    print("=" * 70)
    
    orchestrator = ValidationOrchestrator()
    
    git_context = {
        'branch': 'main',
        'stagedFiles': ['backend/models.py'],
        'diff': '+class User(BaseModel):\n+    id: int\n+    username: str\n+    email: str'
    }
    
    print(f"\nGit Context:")
    print(f"  Branch: {git_context['branch']}")
    print(f"  Staged Files: {git_context['stagedFiles']}")
    print(f"\nRunning validation...")
    
    result = orchestrator.validate(git_context)
    
    print(f"\nValidation Result:")
    print(f"  Success: {result['success']}")
    print(f"  Allow Commit: {result['allowCommit']}")
    print(f"  Message: {result['message']}")
    
    if result['drift_report']:
        print(f"\n  Drift Report:")
        print(f"    Aligned: {result['drift_report'].get('aligned', 'N/A')}")
        print(f"    Total Issues: {result['drift_report'].get('total_issues', 0)}")
    
    if result['test_report']:
        print(f"\n  Test Report:")
        print(f"    Has Issues: {result['test_report'].get('has_issues', False)}")
    
    if result['doc_report']:
        print(f"\n  Documentation Report:")
        print(f"    Has Issues: {result['doc_report'].get('has_issues', False)}")
    
    print("\n" + "=" * 70 + "\n")


def demo_validation_with_multiple_files():
    """Demonstrate validation with multiple staged files."""
    print("=" * 70)
    print("DEMO 2: Validation with Multiple Files")
    print("=" * 70)
    
    orchestrator = ValidationOrchestrator()
    
    git_context = {
        'branch': 'feature/new-endpoint',
        'stagedFiles': [
            'backend/handlers/user.py',
            'backend/models.py',
            'backend/handlers/health.py'
        ],
        'diff': 'mock diff content'
    }
    
    print(f"\nGit Context:")
    print(f"  Branch: {git_context['branch']}")
    print(f"  Staged Files:")
    for file in git_context['stagedFiles']:
        print(f"    - {file}")
    
    print(f"\nRunning validation...")
    
    result = orchestrator.validate(git_context)
    
    print(f"\nValidation Result:")
    print(f"  Success: {result['success']}")
    print(f"  Allow Commit: {result['allowCommit']}")
    print(f"  Message: {result['message']}")
    print(f"  Total Issues: {result.get('total_issues', 0)}")
    
    if result.get('suggestions'):
        print(f"\n  Suggestions Generated: Yes")
        summary = result['suggestions'].get('summary', {})
        print(f"    Total Suggestions: {summary.get('total_suggestions', 0)}")
        print(f"    By Type:")
        by_type = summary.get('by_type', {})
        print(f"      - Spec: {by_type.get('spec', 0)}")
        print(f"      - Test: {by_type.get('test', 0)}")
        print(f"      - Doc: {by_type.get('doc', 0)}")
    
    print("\n" + "=" * 70 + "\n")


def demo_validation_with_ignored_files():
    """Demonstrate validation with files that should be ignored."""
    print("=" * 70)
    print("DEMO 3: Validation with Ignored Files")
    print("=" * 70)
    
    orchestrator = ValidationOrchestrator()
    
    git_context = {
        'branch': 'main',
        'stagedFiles': [
            'backend/models.py',
            '__pycache__/models.cpython-39.pyc',
            'node_modules/package.json',
            '.venv/lib/site-packages/test.py'
        ],
        'diff': ''
    }
    
    print(f"\nGit Context:")
    print(f"  Branch: {git_context['branch']}")
    print(f"  Staged Files:")
    for file in git_context['stagedFiles']:
        print(f"    - {file}")
    
    print(f"\nRunning validation...")
    
    result = orchestrator.validate(git_context)
    
    print(f"\nValidation Result:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    print(f"\n  Note: Ignored files (__pycache__, node_modules, .venv) were filtered out")
    print(f"        Only backend/models.py was validated")
    
    print("\n" + "=" * 70 + "\n")


def demo_validation_result_formatting():
    """Demonstrate ValidationResult formatting capabilities."""
    print("=" * 70)
    print("DEMO 4: ValidationResult Formatting")
    print("=" * 70)
    
    # Create a sample validation result with issues
    result = ValidationResult(
        success=False,
        message="Validation failed with 3 issues detected",
        allow_commit=False,
        drift_report={
            'aligned': False,
            'total_issues': 2,
            'issues_by_file': {
                'backend/models.py': [
                    {
                        'type': 'spec',
                        'description': 'New field "email_verified" not in spec',
                        'severity': 'error'
                    }
                ],
                'backend/handlers/user.py': [
                    {
                        'type': 'spec',
                        'description': 'New endpoint GET /users/{id}/posts not in spec',
                        'severity': 'error'
                    }
                ]
            }
        },
        test_report={
            'has_issues': True,
            'issues': [
                {
                    'type': 'missing_tests',
                    'description': 'No test file found for backend/handlers/user.py',
                    'severity': 'error'
                }
            ]
        },
        doc_report={
            'has_issues': False,
            'issues': []
        }
    )
    
    print("\nFormatted Display Output:")
    print("-" * 70)
    print(result.format_for_display())
    print("-" * 70)
    
    print("\nDictionary Format:")
    print("-" * 70)
    result_dict = result.to_dict()
    print(f"Success: {result_dict['success']}")
    print(f"Allow Commit: {result_dict['allowCommit']}")
    print(f"Message: {result_dict['message']}")
    print(f"Drift Issues: {len(result_dict['drift_report']['issues_by_file'])}")
    print(f"Test Issues: {len(result_dict['test_report']['issues'])}")
    print(f"Doc Issues: {len(result_dict['doc_report']['issues'])}")
    
    print("\n" + "=" * 70 + "\n")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "SpecSync Validation Flow Demo" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    try:
        demo_successful_validation()
        demo_validation_with_multiple_files()
        demo_validation_with_ignored_files()
        demo_validation_result_formatting()
        
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 20 + "All Demos Completed!" + " " * 27 + "║")
        print("╚" + "=" * 68 + "╝")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
