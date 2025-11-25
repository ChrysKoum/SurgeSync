#!/usr/bin/env python3
"""
Standalone validation runner for SpecSync pre-commit hook.
This script runs validation on staged changes and returns appropriate exit codes.
"""

import sys
import subprocess
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.validator import ValidationOrchestrator
from backend.drift_detector import DriftDetector
from backend.test_analyzer import TestCoverageDetector
from backend.doc_analyzer import DocumentationAlignmentDetector
from backend.suggestion_generator import SuggestionGenerator


def get_git_context():
    """Get git context (staged files and diff)."""
    try:
        # Get current branch
        branch_result = subprocess.run(
            "git rev-parse --abbrev-ref HEAD",
            capture_output=True,
            text=True,
            check=True,
            shell=True
        )
        branch = branch_result.stdout.strip()
        
        # Get staged files
        files_result = subprocess.run(
            "git diff --cached --name-only",
            capture_output=True,
            text=True,
            check=True,
            shell=True
        )
        staged_files = [f.strip() for f in files_result.stdout.split('\n') if f.strip()]
        
        # Get diff
        diff_result = subprocess.run(
            "git diff --cached",
            capture_output=True,
            text=True,
            check=True,
            shell=True
        )
        diff = diff_result.stdout
        
        return {
            "branch": branch,
            "stagedFiles": staged_files,
            "diff": diff
        }
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting git context: {e}")
        return None


def main():
    """Run validation on staged changes."""
    print("Initializing SpecSync validation...")
    
    # Get git context
    git_context = get_git_context()
    if not git_context:
        print("❌ Failed to get git context")
        return 1
    
    staged_files = git_context["stagedFiles"]
    
    if not staged_files:
        print("ℹ️  No files staged for commit")
        return 0
    
    print(f"📁 Validating {len(staged_files)} staged file(s)...")
    print()
    
    # Initialize orchestrator
    orchestrator = ValidationOrchestrator()
    
    # Run validation
    result = orchestrator.validate(git_context)
    
    # Display results
    print()
    print("=" * 70)
    print("  VALIDATION RESULTS")
    print("=" * 70)
    print()
    
    # Handle both dict and object results
    if isinstance(result, dict):
        success = result.get('success', False)
        message = result.get('message', 'Unknown')
        drift_report = result.get('drift_report')
        test_report = result.get('test_report')
        doc_report = result.get('doc_report')
        suggestions = result.get('suggestions', [])
    else:
        success = result.success
        message = result.message
        drift_report = result.drift_report
        test_report = result.test_report
        doc_report = result.doc_report
        suggestions = result.suggestions
    
    if success:
        print("✅ SUCCESS: All validations passed")
        print()
        print(f"   Message: {message}")
        return 0
    else:
        print("❌ FAILURE: Validation issues detected")
        print()
        print(f"   Message: {message}")
        print()
        
        # Show drift issues
        if drift_report:
            aligned = drift_report.get('aligned', True) if isinstance(drift_report, dict) else drift_report.aligned
            if not aligned:
                issues = drift_report.get('issues', []) if isinstance(drift_report, dict) else drift_report.issues
                print("📊 Drift Issues:")
                print(f"   Total: {len(issues)}")
                for issue in issues[:5]:  # Show first 5
                    if isinstance(issue, dict):
                        print(f"   • [{issue.get('type')}] {issue.get('file')}: {issue.get('description')}")
                    else:
                        print(f"   • [{issue.type}] {issue.file}: {issue.description}")
                if len(issues) > 5:
                    print(f"   ... and {len(issues) - 5} more")
                print()
        
        # Show test coverage issues
        if test_report:
            has_issues = test_report.get('has_issues', False) if isinstance(test_report, dict) else test_report.has_issues
            if has_issues:
                issues = test_report.get('issues', []) if isinstance(test_report, dict) else test_report.issues
                print("🧪 Test Coverage Issues:")
                print(f"   Total: {len(issues)}")
                for issue in issues[:3]:  # Show first 3
                    if isinstance(issue, dict):
                        print(f"   • [{issue.get('type')}] {issue.get('description')}")
                    else:
                        print(f"   • [{issue.type}] {issue.description}")
                if len(issues) > 3:
                    print(f"   ... and {len(issues) - 3} more")
                print()
        
        # Show documentation issues
        if doc_report:
            has_issues = doc_report.get('has_issues', False) if isinstance(doc_report, dict) else doc_report.has_issues
            if has_issues:
                issues = doc_report.get('issues', []) if isinstance(doc_report, dict) else doc_report.issues
                print("📚 Documentation Issues:")
                print(f"   Total: {len(issues)}")
                for issue in issues[:3]:  # Show first 3
                    if isinstance(issue, dict):
                        print(f"   • [{issue.get('type')}] {issue.get('description')}")
                    else:
                        print(f"   • [{issue.type}] {issue.description}")
                if len(issues) > 3:
                    print(f"   ... and {len(issues) - 3} more")
                print()
        
        # Show suggestions
        if suggestions:
            # Handle both list and dict formats
            if isinstance(suggestions, dict):
                suggestions_list = suggestions.get('suggestions', [])
            elif isinstance(suggestions, list):
                suggestions_list = suggestions
            else:
                suggestions_list = []
            
            if suggestions_list:
                print("💡 Suggestions:")
                for i, suggestion in enumerate(suggestions_list[:5], 1):
                    if isinstance(suggestion, dict):
                        print(f"   {i}. [{suggestion.get('type', '').upper()}] {suggestion.get('description')}")
                    else:
                        print(f"   {i}. [{suggestion.type.upper()}] {suggestion.description}")
                if len(suggestions_list) > 5:
                    print(f"   ... and {len(suggestions_list) - 5} more suggestions")
                print()
        
        print("=" * 70)
        print()
        
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
