"""
Demo script to demonstrate staged changes preservation during validation.

This script shows how SpecSync ensures that validation runs in read-only mode
and never modifies the git staging area.
"""
from backend.validator import (
    ValidationOrchestrator,
    get_staging_area_state,
    verify_staging_area_unchanged,
    StagingAreaModifiedException
)


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_staging_state_capture():
    """Demonstrate capturing staging area state."""
    print_header("DEMO 1: Capturing Staging Area State")
    
    print("Capturing current staging area state...")
    state1 = get_staging_area_state()
    print(f"State hash: {state1[:16]}..." if state1 else "State hash: (empty - not in git repo)")
    
    print("\nCapturing state again (should be identical)...")
    state2 = get_staging_area_state()
    print(f"State hash: {state2[:16]}..." if state2 else "State hash: (empty - not in git repo)")
    
    if state1 == state2:
        print("\n✓ States match - staging area is unchanged")
    else:
        print("\n✗ States differ - staging area was modified")


def demo_staging_verification():
    """Demonstrate staging area verification."""
    print_header("DEMO 2: Verifying Staging Area Unchanged")
    
    print("Test 1: Verifying identical states (should pass)...")
    state = "abc123def456"
    try:
        verify_staging_area_unchanged(state, state)
        print("✓ Verification passed - staging area unchanged")
    except StagingAreaModifiedException as e:
        print(f"✗ Verification failed: {e}")
    
    print("\nTest 2: Verifying different states (should fail)...")
    state_before = "abc123def456"
    state_after = "xyz789ghi012"
    try:
        verify_staging_area_unchanged(state_before, state_after)
        print("✓ Verification passed - staging area unchanged")
    except StagingAreaModifiedException as e:
        print(f"✗ Verification failed (expected): {e}")


def demo_validation_preserves_staging():
    """Demonstrate that validation preserves staging area."""
    print_header("DEMO 3: Validation Preserves Staging Area")
    
    print("Capturing staging area state before validation...")
    state_before = get_staging_area_state()
    print(f"Before: {state_before[:16]}..." if state_before else "Before: (empty)")
    
    print("\nRunning validation...")
    orchestrator = ValidationOrchestrator()
    
    git_context = {
        'branch': 'main',
        'stagedFiles': ['backend/models.py'],
        'diff': ''
    }
    
    result = orchestrator.validate(git_context)
    
    print(f"Validation completed: {result['message']}")
    print(f"Staging area preserved: {result['staging_area_preserved']}")
    
    print("\nCapturing staging area state after validation...")
    state_after = get_staging_area_state()
    print(f"After: {state_after[:16]}..." if state_after else "After: (empty)")
    
    if state_before == state_after:
        print("\n✓ SUCCESS: Staging area unchanged after validation")
        print("   Validation ran in read-only mode as required")
    else:
        print("\n✗ ERROR: Staging area was modified during validation")
        print("   This should never happen!")


def demo_validation_result_includes_preservation_status():
    """Demonstrate that validation results include preservation status."""
    print_header("DEMO 4: Validation Result Includes Preservation Status")
    
    orchestrator = ValidationOrchestrator()
    
    git_context = {
        'branch': 'main',
        'stagedFiles': [],
        'diff': ''
    }
    
    print("Running validation with no staged files...")
    result = orchestrator.validate(git_context)
    
    print("\nValidation Result Fields:")
    print(f"  - success: {result['success']}")
    print(f"  - allowCommit: {result['allowCommit']}")
    print(f"  - staging_area_preserved: {result['staging_area_preserved']}")
    
    if 'staging_area_error' in result:
        print(f"  - staging_area_error: {result['staging_area_error']}")
    else:
        print("  - staging_area_error: (none)")
    
    print("\n✓ Validation result includes staging area preservation status")


def main():
    """Run all demos."""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Staged Changes Preservation Demo" + " " * 21 + "║")
    print("╚" + "=" * 68 + "╝")
    
    demo_staging_state_capture()
    demo_staging_verification()
    demo_validation_preserves_staging()
    demo_validation_result_includes_preservation_status()
    
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 22 + "All Demos Completed!" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝\n")


if __name__ == "__main__":
    main()
