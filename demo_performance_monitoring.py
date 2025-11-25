"""
Demo script to showcase performance monitoring features in SpecSync validation.

This script demonstrates:
1. Timing instrumentation for each validation step
2. Timeout handling with partial results
3. Performance summary reporting
"""
from backend.validator import ValidationOrchestrator, ValidationResult
import time


def demo_normal_validation():
    """Demonstrate normal validation with timing."""
    print("=" * 60)
    print("Demo 1: Normal Validation with Performance Monitoring")
    print("=" * 60)
    
    orchestrator = ValidationOrchestrator(timeout_seconds=30)
    
    git_context = {
        'branch': 'main',
        'stagedFiles': ['backend/models.py', 'backend/handlers/user.py'],
        'diff': '+ def new_function():\n+     pass'
    }
    
    print("\nRunning validation...")
    result = orchestrator.validate(git_context)
    
    print(f"\nValidation Result:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    print(f"  Timed Out: {result['timed_out']}")
    
    print("\n" + orchestrator.get_timing_summary())
    
    # Create ValidationResult object for formatted display
    validation_result = ValidationResult(
        success=result['success'],
        message=result['message'],
        allow_commit=result['allowCommit'],
        drift_report=result.get('drift_report'),
        test_report=result.get('test_report'),
        doc_report=result.get('doc_report'),
        suggestions=result.get('suggestions'),
        timing=result.get('timing'),
        timed_out=result.get('timed_out', False),
        partial_results=result.get('partial_results', False)
    )
    
    print("\n" + "=" * 60)
    print("Formatted Display:")
    print("=" * 60)
    print(validation_result.format_for_display())


def demo_fast_validation():
    """Demonstrate validation with no files (fast path)."""
    print("\n\n" + "=" * 60)
    print("Demo 2: Fast Validation (No Files)")
    print("=" * 60)
    
    orchestrator = ValidationOrchestrator(timeout_seconds=30)
    
    git_context = {
        'branch': 'main',
        'stagedFiles': [],
        'diff': ''
    }
    
    print("\nRunning validation with no files...")
    result = orchestrator.validate(git_context)
    
    print(f"\nValidation Result:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    
    print("\n" + orchestrator.get_timing_summary())


def demo_ignored_files():
    """Demonstrate validation with ignored files."""
    print("\n\n" + "=" * 60)
    print("Demo 3: Validation with Ignored Files")
    print("=" * 60)
    
    orchestrator = ValidationOrchestrator(timeout_seconds=30)
    
    git_context = {
        'branch': 'main',
        'stagedFiles': [
            '__pycache__/test.pyc',
            'node_modules/package.json',
            '.venv/lib/python.py'
        ],
        'diff': ''
    }
    
    print("\nRunning validation with ignored files...")
    result = orchestrator.validate(git_context)
    
    print(f"\nValidation Result:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    
    print("\n" + orchestrator.get_timing_summary())


def demo_timing_breakdown():
    """Demonstrate detailed timing breakdown."""
    print("\n\n" + "=" * 60)
    print("Demo 4: Detailed Timing Breakdown")
    print("=" * 60)
    
    orchestrator = ValidationOrchestrator(timeout_seconds=30)
    
    git_context = {
        'branch': 'feature/new-endpoint',
        'stagedFiles': [
            'backend/handlers/user.py',
            'backend/models.py',
            'docs/api/users.md'
        ],
        'diff': '+ def get_user_profile():\n+     pass'
    }
    
    print("\nRunning validation with multiple files...")
    result = orchestrator.validate(git_context)
    
    print(f"\nValidation completed in {result['timing']['total']:.3f}s")
    print("\nStep-by-step breakdown:")
    
    timing = result['timing']
    steps = [
        ('Context Initialization', timing.get('context_initialization', 0)),
        ('Steering Rules Loading', timing.get('steering_rules', 0)),
        ('Drift Detection', timing.get('drift_detection', 0)),
        ('Test Coverage Analysis', timing.get('test_coverage', 0)),
        ('Documentation Validation', timing.get('documentation', 0)),
        ('Result Aggregation', timing.get('aggregation', 0)),
    ]
    
    if 'suggestion_generation' in timing:
        steps.append(('Suggestion Generation', timing['suggestion_generation']))
    
    for step_name, duration in steps:
        percentage = (duration / timing['total'] * 100) if timing['total'] > 0 else 0
        bar_length = int(percentage / 2)
        bar = '█' * bar_length + '░' * (50 - bar_length)
        print(f"  {step_name:.<30} {duration:>6.3f}s [{bar}] {percentage:>5.1f}%")


def demo_custom_timeout():
    """Demonstrate custom timeout configuration."""
    print("\n\n" + "=" * 60)
    print("Demo 5: Custom Timeout Configuration")
    print("=" * 60)
    
    # Create orchestrator with shorter timeout for demo
    orchestrator = ValidationOrchestrator(timeout_seconds=60)
    
    print(f"\nConfigured timeout: {orchestrator.timeout_seconds}s")
    
    git_context = {
        'branch': 'main',
        'stagedFiles': ['backend/models.py'],
        'diff': ''
    }
    
    result = orchestrator.validate(git_context)
    
    total_time = result['timing']['total']
    timeout_limit = orchestrator.timeout_seconds
    
    print(f"Validation time: {total_time:.3f}s")
    print(f"Timeout limit: {timeout_limit}s")
    print(f"Time remaining: {timeout_limit - total_time:.3f}s")
    
    if total_time > timeout_limit * 0.8:
        print("⚠ Warning: Approaching timeout limit!")
    else:
        print("✓ Well within timeout limit")


if __name__ == '__main__':
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  SpecSync Performance Monitoring Demo".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    
    try:
        demo_normal_validation()
        demo_fast_validation()
        demo_ignored_files()
        demo_timing_breakdown()
        demo_custom_timeout()
        
        print("\n\n" + "=" * 60)
        print("All demos completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
