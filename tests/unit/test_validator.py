"""
Unit tests for the validation orchestrator module.
"""
import pytest
from pathlib import Path
from backend.validator import ValidationOrchestrator, ValidationResult, SteeringRulesParser


class TestSteeringRulesParser:
    """Tests for the steering rules parser."""
    
    def test_parse_steering_rules(self):
        """Test parsing steering rules document."""
        parser = SteeringRulesParser()
        rules = parser.parse()
        
        assert 'correlation_patterns' in rules
        assert 'ignore_patterns' in rules
        assert 'validation_priorities' in rules
        assert 'minimal_change_policy' in rules
    
    def test_correlation_patterns_extracted(self):
        """Test that correlation patterns are extracted correctly."""
        parser = SteeringRulesParser()
        rules = parser.parse()
        
        # Should have some correlation patterns
        assert len(rules['correlation_patterns']) > 0
    
    def test_ignore_patterns_extracted(self):
        """Test that ignore patterns are extracted correctly."""
        parser = SteeringRulesParser()
        rules = parser.parse()
        
        # Should have some ignore patterns
        assert len(rules['ignore_patterns']) > 0
        
        # Should include common patterns like __pycache__
        assert any('__pycache__' in pattern for pattern in rules['ignore_patterns'])


class TestValidationOrchestrator:
    """Tests for the validation orchestrator."""
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = ValidationOrchestrator()
        assert orchestrator.steering_parser is not None
        assert orchestrator.steering_rules is None
    
    def test_load_steering_rules(self):
        """Test loading steering rules."""
        orchestrator = ValidationOrchestrator()
        rules = orchestrator.load_steering_rules()
        
        assert rules is not None
        assert 'correlation_patterns' in rules
        assert orchestrator.steering_rules is not None
    
    def test_validate_with_empty_git_context(self):
        """Test validation with empty git context."""
        orchestrator = ValidationOrchestrator()
        
        git_context = {
            'branch': 'main',
            'stagedFiles': [],
            'diff': ''
        }
        
        result = orchestrator.validate(git_context)
        
        assert result is not None
        assert 'success' in result
        assert 'message' in result
        assert 'allowCommit' in result
        assert result['success'] is True  # No files to validate
    
    def test_validate_with_ignored_files(self):
        """Test validation with files that should be ignored."""
        orchestrator = ValidationOrchestrator()
        
        git_context = {
            'branch': 'main',
            'stagedFiles': [
                '__pycache__/test.pyc',
                'node_modules/package.json'
            ],
            'diff': ''
        }
        
        result = orchestrator.validate(git_context)
        
        assert result is not None
        assert result['success'] is True  # All files ignored
    
    def test_validate_with_backend_files(self):
        """Test validation with backend Python files."""
        orchestrator = ValidationOrchestrator()
        
        # Use actual files that exist
        git_context = {
            'branch': 'main',
            'stagedFiles': [
                'backend/models.py'
            ],
            'diff': ''
        }
        
        result = orchestrator.validate(git_context)
        
        assert result is not None
        assert 'success' in result
        assert 'message' in result
        assert 'allowCommit' in result
        assert 'drift_report' in result
        assert 'test_report' in result
        assert 'doc_report' in result
    
    def test_apply_steering_rules(self):
        """Test applying steering rules to validation context."""
        orchestrator = ValidationOrchestrator()
        orchestrator.load_steering_rules()
        
        validation_context = {
            'staged_files': ['backend/handlers/user.py', '__pycache__/test.pyc']
        }
        
        result = orchestrator.apply_steering_rules(validation_context)
        
        assert 'file_mappings' in result
        assert 'filtered_files' in result
        assert 'priorities' in result
        
        # __pycache__ should be filtered out
        assert '__pycache__/test.pyc' not in result['filtered_files']
    
    def test_matches_pattern(self):
        """Test pattern matching for file paths."""
        orchestrator = ValidationOrchestrator()
        orchestrator.load_steering_rules()
        
        # Test exact match using rule_engine
        assert orchestrator.rule_engine._matches_pattern('backend/models.py', 'backend/models.py')
        
        # Test wildcard match
        assert orchestrator.rule_engine._matches_pattern('backend/handlers/user.py', 'backend/handlers/*.py')
        
        # Test recursive wildcard
        assert orchestrator.rule_engine._matches_pattern('backend/handlers/user.py', 'backend/**/*.py')
        
        # Test no match
        assert not orchestrator.rule_engine._matches_pattern('frontend/app.js', 'backend/*.py')


class TestValidationResult:
    """Tests for the ValidationResult class."""
    
    def test_initialization(self):
        """Test ValidationResult initialization."""
        result = ValidationResult(
            success=True,
            message="All validations passed",
            allow_commit=True
        )
        
        assert result.success is True
        assert result.message == "All validations passed"
        assert result.allow_commit is True
        assert result.drift_report is None
        assert result.test_report is None
        assert result.doc_report is None
        assert result.suggestions is None
    
    def test_to_dict(self):
        """Test converting ValidationResult to dictionary."""
        result = ValidationResult(
            success=False,
            message="Validation failed",
            allow_commit=False,
            drift_report={'aligned': False},
            test_report={'has_issues': True},
            doc_report={'has_issues': False}
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['success'] is False
        assert result_dict['message'] == "Validation failed"
        assert result_dict['allowCommit'] is False
        assert result_dict['drift_report'] == {'aligned': False}
        assert result_dict['test_report'] == {'has_issues': True}
        assert result_dict['doc_report'] == {'has_issues': False}
    
    def test_format_for_display_success(self):
        """Test formatting successful validation for display."""
        result = ValidationResult(
            success=True,
            message="All validations passed",
            allow_commit=True
        )
        
        display = result.format_for_display()
        
        assert "✓ VALIDATION PASSED" in display
        assert "All validations passed" in display
    
    def test_format_for_display_failure(self):
        """Test formatting failed validation for display."""
        result = ValidationResult(
            success=False,
            message="Validation failed",
            allow_commit=False,
            drift_report={
                'aligned': False,
                'total_issues': 2,
                'issues_by_file': {
                    'backend/models.py': [{'type': 'spec', 'description': 'Test issue'}]
                }
            }
        )
        
        display = result.format_for_display()
        
        assert "✗ VALIDATION FAILED" in display
        assert "Validation failed" in display
        assert "Drift Issues" in display
        assert "Total drift issues: 2" in display
    
    def test_validation_result_with_timing(self):
        """Test ValidationResult with timing information."""
        timing_data = {
            'drift_detection': 0.5,
            'test_coverage': 0.3,
            'documentation': 0.2,
            'total': 1.0
        }
        
        result = ValidationResult(
            success=True,
            message="All validations passed",
            allow_commit=True,
            timing=timing_data
        )
        
        assert result.timing == timing_data
        assert result.timed_out is False
        assert result.partial_results is False
        
        display = result.format_for_display()
        assert "Performance" in display
        assert "1.000s" in display
    
    def test_validation_result_with_timeout(self):
        """Test ValidationResult with timeout flag."""
        result = ValidationResult(
            success=False,
            message="Validation timed out",
            allow_commit=False,
            timed_out=True,
            partial_results=True,
            timing={'total': 30.5}
        )
        
        assert result.timed_out is True
        assert result.partial_results is True
        
        display = result.format_for_display()
        assert "TIMEOUT" in display
        assert "Partial results" in display


class TestStagedChangesPreservation:
    """Tests for staged changes preservation functionality."""
    
    def test_get_staging_area_state(self):
        """Test capturing staging area state."""
        from backend.validator import get_staging_area_state
        
        # Should return a hash string (or empty string if not in git repo)
        state = get_staging_area_state()
        assert isinstance(state, str)
        
        # If we're in a git repo, should return a valid hash
        # Hash should be consistent when called multiple times without changes
        state2 = get_staging_area_state()
        assert state == state2
    
    def test_verify_staging_area_unchanged_success(self):
        """Test verification passes when staging area is unchanged."""
        from backend.validator import verify_staging_area_unchanged
        
        # Same state should pass verification
        state = "abc123"
        verify_staging_area_unchanged(state, state)  # Should not raise
    
    def test_verify_staging_area_unchanged_failure(self):
        """Test verification fails when staging area is modified."""
        from backend.validator import verify_staging_area_unchanged, StagingAreaModifiedException
        
        # Different states should raise exception
        state_before = "abc123"
        state_after = "def456"
        
        with pytest.raises(StagingAreaModifiedException) as exc_info:
            verify_staging_area_unchanged(state_before, state_after)
        
        assert "Staging area was modified" in str(exc_info.value)
        assert "read-only mode" in str(exc_info.value)
    
    def test_validation_preserves_staging_area(self):
        """Test that validation doesn't modify the staging area."""
        orchestrator = ValidationOrchestrator()
        
        git_context = {
            'branch': 'main',
            'stagedFiles': [],
            'diff': ''
        }
        
        result = orchestrator.validate(git_context)
        
        # Should include staging area preservation status
        assert 'staging_area_preserved' in result
        assert result['staging_area_preserved'] is True
    
    def test_validation_result_includes_staging_preservation(self):
        """Test that ValidationResult includes staging area preservation status."""
        from backend.validator import ValidationResult
        
        result = ValidationResult(
            success=True,
            message="Test",
            allow_commit=True,
            staging_area_preserved=True
        )
        
        assert result.staging_area_preserved is True
        assert result.staging_area_error is None
        
        result_dict = result.to_dict()
        assert result_dict['staging_area_preserved'] is True
        assert 'staging_area_error' not in result_dict
    
    def test_validation_result_with_staging_error(self):
        """Test ValidationResult with staging area modification error."""
        from backend.validator import ValidationResult
        
        result = ValidationResult(
            success=False,
            message="Staging area modified",
            allow_commit=False,
            staging_area_preserved=False,
            staging_area_error="Staging area was modified during validation"
        )
        
        assert result.staging_area_preserved is False
        assert result.staging_area_error is not None
        
        result_dict = result.to_dict()
        assert result_dict['staging_area_preserved'] is False
        assert result_dict['staging_area_error'] == "Staging area was modified during validation"
        
        # Check display format includes error
        display = result.format_for_display()
        assert "CRITICAL" in display
        assert "Staging area was modified" in display
    
    def test_validation_with_backend_files_preserves_staging(self):
        """Test that validation with actual files preserves staging area."""
        orchestrator = ValidationOrchestrator()
        
        git_context = {
            'branch': 'main',
            'stagedFiles': ['backend/models.py'],
            'diff': ''
        }
        
        result = orchestrator.validate(git_context)
        
        # Validation should complete without modifying staging area
        assert result['staging_area_preserved'] is True
        assert 'staging_area_error' not in result


class TestPerformanceMonitoring:
    """Tests for performance monitoring features."""
    
    def test_orchestrator_with_custom_timeout(self):
        """Test orchestrator initialization with custom timeout."""
        orchestrator = ValidationOrchestrator(timeout_seconds=60)
        assert orchestrator.timeout_seconds == 60
    
    def test_validation_includes_timing(self):
        """Test that validation results include timing data."""
        orchestrator = ValidationOrchestrator()
        
        git_context = {
            'branch': 'main',
            'stagedFiles': [],
            'diff': ''
        }
        
        result = orchestrator.validate(git_context)
        
        assert 'timing' in result
        assert 'total' in result['timing']
        assert result['timing']['total'] > 0
        assert result['timed_out'] is False
    
    def test_timing_data_structure(self):
        """Test that timing data has expected structure."""
        orchestrator = ValidationOrchestrator()
        
        git_context = {
            'branch': 'main',
            'stagedFiles': ['backend/models.py'],
            'diff': ''
        }
        
        result = orchestrator.validate(git_context)
        
        timing = result['timing']
        assert 'context_initialization' in timing
        assert 'steering_rules' in timing
        assert 'drift_detection' in timing
        assert 'test_coverage' in timing
        assert 'documentation' in timing
        assert 'aggregation' in timing
        assert 'total' in timing
        
        # All timing values should be non-negative
        for key, value in timing.items():
            assert value >= 0
    
    def test_get_timing_summary(self):
        """Test getting timing summary."""
        orchestrator = ValidationOrchestrator()
        
        git_context = {
            'branch': 'main',
            'stagedFiles': [],
            'diff': ''
        }
        
        orchestrator.validate(git_context)
        summary = orchestrator.get_timing_summary()
        
        assert "Validation Performance Summary" in summary
        assert "Total:" in summary
    
    def test_timing_summary_with_no_data(self):
        """Test timing summary when no validation has run."""
        orchestrator = ValidationOrchestrator()
        summary = orchestrator.get_timing_summary()
        
        assert "No timing data available" in summary
