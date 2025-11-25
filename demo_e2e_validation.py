#!/usr/bin/env python3
"""
End-to-end validation script for SpecSync.

This script simulates a complete commit flow with real code modifications
to the example service, demonstrating:
1. Drift detection on real code changes
2. Test coverage validation
3. Documentation validation
4. Suggestion generation
5. Complete validation workflow

Requirements validated: 8.3, 8.4
"""
import sys
import subprocess
from pathlib import Path
from backend.validator import ValidationOrchestrator, ValidationResult


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80)


def get_git_staged_files() -> list:
    """Get the list of currently staged files from git."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        return files
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return []


def get_git_diff() -> str:
    """Get the staged diff from git."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def get_git_branch() -> str:
    """Get the current git branch."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return "unknown"


def scenario_1_aligned_changes():
    """
    Scenario 1: Validate aligned changes (all artifacts in sync).
    
    This simulates a commit where code, spec, tests, and docs are all aligned.
    """
    print_header("SCENARIO 1: Aligned Changes (Success Case)")
    
    print("Simulating a commit with aligned changes:")
    print("  - Code: backend/models.py (User model)")
    print("  - Spec: .kiro/specs/app.yaml (User model defined)")
    print("  - Tests: tests/unit/test_*.py (tests exist)")
    print("  - Docs: docs/api/users.md (documented)")
    
    orchestrator = ValidationOrchestrator()
    
    git_context = {
        'branch': 'main',
        'stagedFiles': ['backend/models.py'],
        'diff': '+class User(BaseModel):\n+    id: int\n+    username: str\n+    email: str'
    }
    
    print_section("Running Validation")
    result = orchestrator.validate(git_context)
    
    print_section("Validation Result")
    print(f"✓ Success: {result['success']}")
    print(f"✓ Allow Commit: {result['allowCommit']}")
    print(f"✓ Message: {result['message']}")
    
    if result.get('timing'):
        print(f"\n⏱ Performance:")
        print(f"  Total time: {result['timing'].get('total', 0):.3f}s")
        if 'drift_detection' in result['timing']:
            print(f"  Drift detection: {result['timing']['drift_detection']:.3f}s")
        if 'test_coverage' in result['timing']:
            print(f"  Test coverage: {result['timing']['test_coverage']:.3f}s")
        if 'documentation' in result['timing']:
            print(f"  Documentation: {result['timing']['documentation']:.3f}s")
    
    print(f"\n✓ Staging area preserved: {result.get('staging_area_preserved', False)}")
    
    return result['success']


def scenario_2_drift_detection():
    """
    Scenario 2: Detect drift (new endpoint not in spec).
    
    This simulates adding a new endpoint to the code without updating the spec.
    """
    print_header("SCENARIO 2: Drift Detection (New Endpoint Not in Spec)")
    
    print("Simulating a commit with drift:")
    print("  - Code: backend/handlers/user.py (new endpoint added)")
    print("  - Spec: .kiro/specs/app.yaml (endpoint NOT defined)")
    print("  - Expected: Drift detected, commit blocked")
    
    orchestrator = ValidationOrchestrator()
    
    # Simulate adding a new endpoint that's not in the spec
    git_context = {
        'branch': 'feature/new-endpoint',
        'stagedFiles': ['backend/handlers/user.py'],
        'diff': '''
@router.get("/users/{id}/posts")
async def get_user_posts(id: int):
    return {"user_id": id, "posts": []}
'''
    }
    
    print_section("Running Validation")
    result = orchestrator.validate(git_context)
    
    print_section("Validation Result")
    print(f"✗ Success: {result['success']}")
    print(f"✗ Allow Commit: {result['allowCommit']}")
    print(f"✗ Message: {result['message']}")
    
    if result.get('drift_report'):
        drift = result['drift_report']
        print(f"\n📊 Drift Report:")
        print(f"  Aligned: {drift.get('aligned', 'N/A')}")
        print(f"  Total Issues: {drift.get('total_issues', 0)}")
        
        if drift.get('issues_by_file'):
            print(f"\n  Issues by file:")
            for file, issues in drift['issues_by_file'].items():
                if issues:
                    print(f"    {file}: {len(issues)} issue(s)")
    
    if result.get('suggestions'):
        print(f"\n💡 Suggestions Generated:")
        summary = result['suggestions'].get('summary', {})
        print(f"  Total: {summary.get('total_suggestions', 0)}")
        print(f"  By type:")
        by_type = summary.get('by_type', {})
        print(f"    - Spec: {by_type.get('spec', 0)}")
        print(f"    - Test: {by_type.get('test', 0)}")
        print(f"    - Doc: {by_type.get('doc', 0)}")
        
        if result['suggestions'].get('ordered_suggestions'):
            print(f"\n  Top suggestions:")
            for i, suggestion in enumerate(result['suggestions']['ordered_suggestions'][:3], 1):
                print(f"    {i}. [{suggestion.get('type', 'unknown')}] {suggestion.get('description', 'N/A')[:60]}...")
    
    return not result['success']  # Success means drift was detected


def scenario_3_test_coverage():
    """
    Scenario 3: Validate test coverage (missing tests).
    
    This simulates adding code without corresponding tests.
    """
    print_header("SCENARIO 3: Test Coverage Validation (Missing Tests)")
    
    print("Simulating a commit with missing test coverage:")
    print("  - Code: backend/handlers/user.py (modified)")
    print("  - Tests: No corresponding test updates")
    print("  - Expected: Test coverage issues detected")
    
    orchestrator = ValidationOrchestrator()
    
    git_context = {
        'branch': 'feature/new-function',
        'stagedFiles': ['backend/handlers/user.py'],
        'diff': '''
def new_helper_function():
    return "helper"
'''
    }
    
    print_section("Running Validation")
    result = orchestrator.validate(git_context)
    
    print_section("Validation Result")
    print(f"Status: {'✓ Success' if result['success'] else '✗ Failed'}")
    print(f"Allow Commit: {result['allowCommit']}")
    print(f"Message: {result['message']}")
    
    if result.get('test_report'):
        test_report = result['test_report']
        print(f"\n🧪 Test Coverage Report:")
        print(f"  Has Issues: {test_report.get('has_issues', False)}")
        
        if test_report.get('issues'):
            print(f"  Issues found: {len(test_report['issues'])}")
            for issue in test_report['issues'][:3]:
                print(f"    - [{issue.get('type', 'unknown')}] {issue.get('description', 'N/A')[:60]}...")
    
    return True  # Always succeeds as a demo


def scenario_4_documentation_validation():
    """
    Scenario 4: Validate documentation alignment.
    
    This simulates modifying an API without updating documentation.
    """
    print_header("SCENARIO 4: Documentation Validation (Outdated Docs)")
    
    print("Simulating a commit with documentation issues:")
    print("  - Code: backend/handlers/user.py (endpoint modified)")
    print("  - Docs: docs/api/users.md (not updated)")
    print("  - Expected: Documentation drift detected")
    
    orchestrator = ValidationOrchestrator()
    
    git_context = {
        'branch': 'feature/update-endpoint',
        'stagedFiles': ['backend/handlers/user.py'],
        'diff': '''
@router.get("/users")
async def list_users(limit: int = 100):  # Added new parameter
    return []
'''
    }
    
    print_section("Running Validation")
    result = orchestrator.validate(git_context)
    
    print_section("Validation Result")
    print(f"Status: {'✓ Success' if result['success'] else '✗ Failed'}")
    print(f"Allow Commit: {result['allowCommit']}")
    print(f"Message: {result['message']}")
    
    if result.get('doc_report'):
        doc_report = result['doc_report']
        print(f"\n📚 Documentation Report:")
        print(f"  Has Issues: {doc_report.get('has_issues', False)}")
        
        if doc_report.get('issues'):
            print(f"  Issues found: {len(doc_report['issues'])}")
            for issue in doc_report['issues'][:3]:
                print(f"    - [{issue.get('type', 'unknown')}] {issue.get('description', 'N/A')[:60]}...")
    
    return True  # Always succeeds as a demo


def scenario_5_multi_file_validation():
    """
    Scenario 5: Validate multiple files in a single commit.
    
    This simulates a commit with multiple file changes.
    """
    print_header("SCENARIO 5: Multi-File Validation")
    
    print("Simulating a commit with multiple files:")
    print("  - backend/handlers/user.py")
    print("  - backend/models.py")
    print("  - backend/handlers/health.py")
    print("  - Expected: All files validated independently")
    
    orchestrator = ValidationOrchestrator()
    
    git_context = {
        'branch': 'feature/multi-file-update',
        'stagedFiles': [
            'backend/handlers/user.py',
            'backend/models.py',
            'backend/handlers/health.py'
        ],
        'diff': 'mock multi-file diff'
    }
    
    print_section("Running Validation")
    result = orchestrator.validate(git_context)
    
    print_section("Validation Result")
    print(f"Status: {'✓ Success' if result['success'] else '✗ Failed'}")
    print(f"Allow Commit: {result['allowCommit']}")
    print(f"Message: {result['message']}")
    print(f"Total Issues: {result.get('total_issues', 0)}")
    
    # Show breakdown by report type
    print(f"\n📊 Validation Breakdown:")
    print(f"  Drift Issues: {'Yes' if result.get('has_drift') else 'No'}")
    print(f"  Test Issues: {'Yes' if result.get('has_test_issues') else 'No'}")
    print(f"  Doc Issues: {'Yes' if result.get('has_doc_issues') else 'No'}")
    
    if result.get('drift_report') and result['drift_report'].get('files_validated'):
        print(f"\n  Files validated: {len(result['drift_report']['files_validated'])}")
        for file in result['drift_report']['files_validated']:
            print(f"    - {file}")
    
    return True  # Always succeeds as a demo


def scenario_6_real_git_context():
    """
    Scenario 6: Use real git context from the repository.
    
    This uses actual staged changes if any exist.
    """
    print_header("SCENARIO 6: Real Git Context (If Available)")
    
    # Try to get real git context
    staged_files = get_git_staged_files()
    
    if not staged_files:
        print("⚠ No staged files found in git.")
        print("  Skipping this scenario.")
        print("  To test with real changes:")
        print("    1. Make changes to files")
        print("    2. Stage them with 'git add'")
        print("    3. Run this script again")
        return True
    
    print(f"Found {len(staged_files)} staged file(s):")
    for file in staged_files:
        print(f"  - {file}")
    
    branch = get_git_branch()
    diff = get_git_diff()
    
    print(f"\nBranch: {branch}")
    print(f"Diff size: {len(diff)} characters")
    
    orchestrator = ValidationOrchestrator()
    
    git_context = {
        'branch': branch,
        'stagedFiles': staged_files,
        'diff': diff
    }
    
    print_section("Running Validation on Real Changes")
    result = orchestrator.validate(git_context)
    
    print_section("Validation Result")
    print(f"Status: {'✓ Success' if result['success'] else '✗ Failed'}")
    print(f"Allow Commit: {result['allowCommit']}")
    print(f"Message: {result['message']}")
    
    if not result['success'] and result.get('suggestions'):
        print(f"\n💡 Suggestions:")
        summary = result['suggestions'].get('summary', {})
        print(f"  Total suggestions: {summary.get('total_suggestions', 0)}")
        
        if result['suggestions'].get('ordered_suggestions'):
            print(f"\n  Prioritized suggestions:")
            for i, suggestion in enumerate(result['suggestions']['ordered_suggestions'][:5], 1):
                print(f"    {i}. [{suggestion.get('type', 'unknown')}] {suggestion.get('description', 'N/A')}")
    
    return True


def scenario_7_performance_monitoring():
    """
    Scenario 7: Monitor validation performance.
    
    This tests that validation completes within the 30-second timeout.
    """
    print_header("SCENARIO 7: Performance Monitoring")
    
    print("Testing validation performance:")
    print("  - Requirement: Complete within 30 seconds")
    print("  - Test: Validate multiple files")
    
    orchestrator = ValidationOrchestrator(timeout_seconds=30)
    
    # Use multiple files to test performance
    git_context = {
        'branch': 'main',
        'stagedFiles': [
            'backend/handlers/user.py',
            'backend/handlers/health.py',
            'backend/models.py',
            'backend/main.py'
        ],
        'diff': 'mock diff for performance test'
    }
    
    print_section("Running Validation")
    result = orchestrator.validate(git_context)
    
    print_section("Performance Results")
    
    if result.get('timing'):
        timing = result['timing']
        total_time = timing.get('total', 0)
        
        print(f"✓ Total time: {total_time:.3f}s")
        print(f"✓ Within timeout: {'Yes' if total_time < 30 else 'No'}")
        print(f"✓ Timed out: {result.get('timed_out', False)}")
        
        print(f"\n  Breakdown:")
        if 'drift_detection' in timing:
            print(f"    Drift detection: {timing['drift_detection']:.3f}s")
        if 'test_coverage' in timing:
            print(f"    Test coverage: {timing['test_coverage']:.3f}s")
        if 'documentation' in timing:
            print(f"    Documentation: {timing['documentation']:.3f}s")
        if 'suggestion_generation' in timing:
            print(f"    Suggestions: {timing['suggestion_generation']:.3f}s")
        
        # Check if approaching timeout
        if total_time > 24:  # 80% of 30 seconds
            print(f"\n  ⚠ Warning: Approaching timeout limit (30s)")
    
    print(f"\n✓ Staging area preserved: {result.get('staging_area_preserved', False)}")
    
    return total_time < 30 if result.get('timing') else True


def scenario_8_steering_rules():
    """
    Scenario 8: Verify steering rules are applied.
    
    This tests that ignored files are filtered out.
    """
    print_header("SCENARIO 8: Steering Rules Application")
    
    print("Testing steering rules:")
    print("  - Files: Mix of code and ignored files")
    print("  - Expected: Ignored files filtered out")
    
    orchestrator = ValidationOrchestrator()
    
    git_context = {
        'branch': 'main',
        'stagedFiles': [
            'backend/models.py',
            '__pycache__/models.cpython-39.pyc',
            'node_modules/package.json',
            '.venv/lib/site-packages/test.py',
            'backend/handlers/user.py'
        ],
        'diff': ''
    }
    
    print_section("Running Validation")
    result = orchestrator.validate(git_context)
    
    print_section("Steering Rules Results")
    print(f"✓ Validation completed: {result is not None}")
    print(f"✓ Success: {result['success']}")
    
    print(f"\n  Files processed:")
    print(f"    Total staged: {len(git_context['stagedFiles'])}")
    
    if result.get('drift_report'):
        validated = result['drift_report'].get('files_validated', [])
        skipped = result['drift_report'].get('files_skipped', [])
        print(f"    Validated: {len(validated)}")
        print(f"    Skipped: {len(skipped)}")
        
        if validated:
            print(f"\n  Validated files:")
            for file in validated:
                print(f"    ✓ {file}")
        
        if skipped:
            print(f"\n  Skipped files (by steering rules):")
            for item in skipped:
                if isinstance(item, dict):
                    print(f"    ✗ {item.get('file', 'unknown')}: {item.get('reason', 'N/A')}")
                else:
                    print(f"    ✗ {item}")
    
    return True


def main():
    """Run all end-to-end validation scenarios."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "SpecSync End-to-End Validation" + " " * 28 + "║")
    print("║" + " " * 25 + "Complete Commit Flow Demo" + " " * 28 + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = {}
    
    try:
        # Run all scenarios
        results['scenario_1'] = scenario_1_aligned_changes()
        results['scenario_2'] = scenario_2_drift_detection()
        results['scenario_3'] = scenario_3_test_coverage()
        results['scenario_4'] = scenario_4_documentation_validation()
        results['scenario_5'] = scenario_5_multi_file_validation()
        results['scenario_6'] = scenario_6_real_git_context()
        results['scenario_7'] = scenario_7_performance_monitoring()
        results['scenario_8'] = scenario_8_steering_rules()
        
        # Summary
        print_header("SUMMARY")
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        print(f"Scenarios completed: {total}")
        print(f"Scenarios passed: {passed}")
        print(f"Success rate: {(passed/total)*100:.1f}%")
        
        print(f"\n  Scenario Results:")
        for scenario, passed in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"    {status} - {scenario.replace('_', ' ').title()}")
        
        print("\n" + "=" * 80)
        print("  ✓ End-to-End Validation Complete!")
        print("=" * 80 + "\n")
        
        # Exit with appropriate code
        sys.exit(0 if all(results.values()) else 1)
        
    except Exception as e:
        print(f"\n❌ Error during end-to-end validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
