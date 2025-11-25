"""
Demo script to showcase the steering rule system functionality.

This script demonstrates:
1. Parsing steering rules from markdown
2. Applying correlation patterns to map files
3. Filtering ignored files
4. Detecting rule-drift conflicts
5. Hot-reloading rules when the file changes
"""
from backend.steering_parser import SteeringRulesParser
from backend.rule_application import RuleApplicationEngine
from backend.validator import ValidationOrchestrator


def demo_steering_parser():
    """Demonstrate steering rules parsing."""
    print("=" * 60)
    print("DEMO: Steering Rules Parser")
    print("=" * 60)
    
    parser = SteeringRulesParser(".kiro/steering/rules.md")
    rules = parser.parse()
    
    print("\n1. Correlation Patterns:")
    print("-" * 40)
    for source, targets in rules['correlation_patterns'].items():
        print(f"  {source}")
        for target in targets:
            print(f"    → {target['target']}")
    
    print("\n2. Ignore Patterns:")
    print("-" * 40)
    for pattern in rules['ignore_patterns'][:5]:  # Show first 5
        print(f"  - {pattern}")
    print(f"  ... and {len(rules['ignore_patterns']) - 5} more")
    
    print("\n3. Validation Priorities:")
    print("-" * 40)
    for category, priority in rules['validation_priorities'].items():
        print(f"  {priority}. {category}")
    
    print("\n4. Minimal Change Policy:")
    print("-" * 40)
    for key, value in rules['minimal_change_policy'].items():
        print(f"  - {value}")


def demo_rule_application():
    """Demonstrate rule application logic."""
    print("\n" + "=" * 60)
    print("DEMO: Rule Application Engine")
    print("=" * 60)
    
    parser = SteeringRulesParser(".kiro/steering/rules.md")
    rules = parser.parse()
    engine = RuleApplicationEngine(rules)
    
    # Test files
    test_files = [
        "backend/handlers/user.py",
        "backend/models.py",
        "backend/__pycache__/models.cpython-39.pyc",
        "tests/unit/test_user.py",
        ".gitignore"
    ]
    
    print("\n1. File Correlation Mapping:")
    print("-" * 40)
    mappings = engine.apply_correlation_patterns(test_files)
    for file, related in mappings.items():
        if related:
            print(f"  {file}")
            for rel in related:
                print(f"    → {rel}")
    
    print("\n2. Filtering Ignored Files:")
    print("-" * 40)
    print(f"  Original files: {len(test_files)}")
    filtered = engine.filter_ignored_files(test_files)
    print(f"  After filtering: {len(filtered)}")
    print(f"  Filtered files:")
    for f in filtered:
        print(f"    - {f}")
    print(f"  Ignored files:")
    for f in set(test_files) - set(filtered):
        print(f"    - {f}")


def demo_conflict_detection():
    """Demonstrate rule-drift conflict detection."""
    print("\n" + "=" * 60)
    print("DEMO: Rule-Drift Conflict Detection")
    print("=" * 60)
    
    parser = SteeringRulesParser(".kiro/steering/rules.md")
    rules = parser.parse()
    engine = RuleApplicationEngine(rules)
    
    # Simulate drift issues
    drift_issues = [
        {
            'type': 'spec',
            'file': 'backend/__pycache__/models.cpython-39.pyc',
            'description': 'New endpoint not in spec'
        }
    ]
    
    all_files = [
        "backend/handlers/user.py",
        "backend/__pycache__/models.cpython-39.pyc"
    ]
    
    filtered_files = engine.filter_ignored_files(all_files)
    
    print("\n1. Detecting Conflicts:")
    print("-" * 40)
    conflicts = engine.detect_rule_drift_conflicts(drift_issues, filtered_files, all_files)
    
    if conflicts:
        print(f"  Found {len(conflicts)} conflict(s):")
        for conflict in conflicts:
            print(f"\n  Type: {conflict['type']}")
            print(f"  File: {conflict['file']}")
            print(f"  Priority: {conflict['priority']}")
            print(f"  Message: {conflict['message']}")
    else:
        print("  No conflicts detected")


def demo_hot_reload():
    """Demonstrate hot-reload functionality."""
    print("\n" + "=" * 60)
    print("DEMO: Hot-Reload Functionality")
    print("=" * 60)
    
    orchestrator = ValidationOrchestrator()
    
    print("\n1. Initial Load:")
    print("-" * 40)
    rules1 = orchestrator.load_steering_rules()
    print(f"  Loaded {len(rules1['correlation_patterns'])} correlation patterns")
    print(f"  Loaded {len(rules1['ignore_patterns'])} ignore patterns")
    
    print("\n2. Check for Changes (no changes):")
    print("-" * 40)
    reloaded = orchestrator.check_and_reload_steering_rules()
    print(f"  Rules reloaded: {reloaded}")
    
    print("\n3. Cached Rules:")
    print("-" * 40)
    print(f"  Parser has cached rules: {orchestrator.steering_parser._cached_rules is not None}")
    print(f"  Last modified time: {orchestrator.steering_parser._last_modified}")


def demo_pattern_matching():
    """Demonstrate pattern matching capabilities."""
    print("\n" + "=" * 60)
    print("DEMO: Pattern Matching")
    print("=" * 60)
    
    parser = SteeringRulesParser(".kiro/steering/rules.md")
    rules = parser.parse()
    engine = RuleApplicationEngine(rules)
    
    test_cases = [
        ("backend/handlers/user.py", "backend/handlers/*.py", True),
        ("backend/handlers/user.py", "backend/**/*.py", True),
        ("backend/models.py", "backend/models.py", True),
        ("frontend/app.js", "backend/*.py", False),
        ("tests/unit/test_user.py", "tests/unit/test_*.py", True),
        ("backend/__pycache__/models.pyc", "**/__pycache__/**", True),
    ]
    
    print("\n1. Pattern Matching Tests:")
    print("-" * 40)
    for file_path, pattern, expected in test_cases:
        result = engine._matches_pattern(file_path, pattern)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{file_path}' vs '{pattern}': {result}")


def demo_pattern_expansion():
    """Demonstrate pattern expansion with variables."""
    print("\n" + "=" * 60)
    print("DEMO: Pattern Expansion")
    print("=" * 60)
    
    parser = SteeringRulesParser(".kiro/steering/rules.md")
    rules = parser.parse()
    engine = RuleApplicationEngine(rules)
    
    test_cases = [
        ("backend/handlers/user.py", "backend/handlers/{module}.py", "tests/unit/test_{module}.py"),
        ("backend/handlers/auth.py", "backend/handlers/{module}.py", "tests/unit/test_{module}.py"),
    ]
    
    print("\n1. Pattern Expansion Tests:")
    print("-" * 40)
    for file_path, source_pattern, target_pattern in test_cases:
        result = engine._expand_pattern(file_path, source_pattern, target_pattern)
        print(f"  File: {file_path}")
        print(f"  Source: {source_pattern}")
        print(f"  Target: {target_pattern}")
        print(f"  Result: {result}")
        print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("STEERING RULE SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    try:
        demo_steering_parser()
        demo_rule_application()
        demo_conflict_detection()
        demo_hot_reload()
        demo_pattern_matching()
        demo_pattern_expansion()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
