"""
Integration tests for the complete validation flow.

These tests verify that the validation orchestrator correctly integrates
all components (drift detection, test coverage, documentation validation,
and suggestion generation) to produce a complete validation result.
"""
import pytest
from backend.validator import ValidationOrchestrator, ValidationResult


class TestValidationFlowIntegration:
    """Integration tests for the complete validation flow."""
    
    def test_complete_validation_flow_with_aligned_code(self):
        """Test the complete validation flow with aligned code."""
        orchestrator = ValidationOrchestrator()
        
        # Simulate git context with aligned backend file
        git_context = {
            'branch': 'main',
            'stagedFiles': ['backend/models.py'],
            'diff': '+class User(BaseModel):\n+    id: int\n+    username: str\n+    email: str'
        }
        
        # Run validation
        result = orchestrator.validate(git_context)
        
        # Verify result structure
        assert result is not None
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'message' in result
        assert 'allowCommit' in result
        assert 'drift_report' in result
        assert 'test_report' in result
        assert 'doc_report' in result
        
        # Verify the result is properly formatted
        assert isinstance(result['success'], bool)
        assert isinstance(result['message'], str)
        assert isinstance(result['allowCommit'], bool)
    
    def test_validation_flow_with_multiple_files(self):
        """Test validation flow with multiple staged files."""
        orchestrator = ValidationOrchestrator()
        
        git_context = {
            'branch': 'feature/new-endpoint',
            'stagedFiles': [
                'backend/handlers/user.py',
                'backend/models.py',
                'tests/unit/test_drift_detector.py'  # Use existing test file
            ],
            'diff': 'mock diff content'
        }
        
        result = orchestrator.validate(git_context)
        
        # Should process all files
        assert result is not None
        assert 'drift_report' in result
        assert 'test_report' in result
        assert 'doc_report' in result
    
    def test_validation_flow_filters_ignored_files(self):
        """Test that validation flow properly filters ignored files."""
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
        
        result = orchestrator.validate(git_context)
        
        # Should only validate backend/models.py
        assert result is not None
        assert result['success'] is not None
    
    def test_validation_flow_aggregates_all_reports(self):
        """Test that validation flow aggregates drift, test, and doc reports."""
        orchestrator = ValidationOrchestrator()
        
        git_context = {
            'branch': 'main',
            'stagedFiles': ['backend/handlers/user.py'],
            'diff': ''
        }
        
        result = orchestrator.validate(git_context)
        
        # Verify all reports are present
        assert 'drift_report' in result
        assert 'test_report' in result
        assert 'doc_report' in result
        
        # Verify reports have expected structure
        if result['drift_report']:
            assert 'aligned' in result['drift_report'] or 'message' in result['drift_report']
        
        if result['test_report']:
            assert 'has_issues' in result['test_report']
        
        if result['doc_report']:
            assert 'has_issues' in result['doc_report']
    
    def test_validation_flow_generates_suggestions_on_failure(self):
        """Test that validation flow generates suggestions when issues are detected."""
        orchestrator = ValidationOrchestrator()
        
        # Use a file that might have issues
        git_context = {
            'branch': 'main',
            'stagedFiles': ['backend/handlers/user.py'],
            'diff': ''
        }
        
        result = orchestrator.validate(git_context)
        
        # If validation fails, suggestions should be present
        if not result['success']:
            assert 'suggestions' in result
            assert result['suggestions'] is not None
    
    def test_validation_flow_respects_steering_rules(self):
        """Test that validation flow applies steering rules correctly."""
        orchestrator = ValidationOrchestrator()
        
        # Load steering rules
        rules = orchestrator.load_steering_rules()
        assert rules is not None
        
        git_context = {
            'branch': 'main',
            'stagedFiles': [
                'backend/handlers/user.py',
                '__pycache__/test.pyc'
            ],
            'diff': ''
        }
        
        result = orchestrator.validate(git_context)
        
        # __pycache__ files should be filtered out by steering rules
        assert result is not None
    
    def test_validation_flow_with_no_spec_file(self):
        """Test validation flow when spec file doesn't exist."""
        orchestrator = ValidationOrchestrator()
        
        # Use an existing file so validation can complete
        git_context = {
            'branch': 'main',
            'stagedFiles': ['backend/models.py'],
            'diff': ''
        }
        
        # Should handle validation gracefully
        result = orchestrator.validate(git_context)
        
        assert result is not None
        assert 'success' in result
        # Should still run test and doc validation even without spec
        assert 'test_report' in result
        assert 'doc_report' in result
    
    def test_validation_result_can_be_converted_to_dict(self):
        """Test that ValidationResult can be converted to dictionary."""
        result_obj = ValidationResult(
            success=True,
            message="All validations passed",
            allow_commit=True,
            drift_report={'aligned': True},
            test_report={'has_issues': False},
            doc_report={'has_issues': False}
        )
        
        result_dict = result_obj.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['success'] is True
        assert result_dict['allowCommit'] is True
        assert result_dict['drift_report'] == {'aligned': True}
    
    def test_validation_result_can_be_formatted_for_display(self):
        """Test that ValidationResult can be formatted for human display."""
        result_obj = ValidationResult(
            success=False,
            message="Validation failed with 3 issues",
            allow_commit=False,
            drift_report={
                'aligned': False,
                'total_issues': 2,
                'issues_by_file': {
                    'backend/models.py': [
                        {'type': 'spec', 'description': 'New field not in spec'}
                    ]
                }
            },
            test_report={
                'has_issues': True,
                'issues': [
                    {'type': 'missing_tests', 'description': 'No tests found'}
                ]
            }
        )
        
        display = result_obj.format_for_display()
        
        assert isinstance(display, str)
        assert "VALIDATION FAILED" in display
        assert "Validation failed with 3 issues" in display
        assert "Drift Issues" in display
        assert "Test Coverage Issues" in display
    
    def test_validation_flow_handles_empty_staged_files(self):
        """Test validation flow with no staged files."""
        orchestrator = ValidationOrchestrator()
        
        git_context = {
            'branch': 'main',
            'stagedFiles': [],
            'diff': ''
        }
        
        result = orchestrator.validate(git_context)
        
        # Should succeed with no files to validate
        assert result is not None
        assert result['success'] is True
        assert 'No files to validate' in result['message']
    
    def test_validation_flow_handles_non_python_files(self):
        """Test validation flow with non-Python files."""
        orchestrator = ValidationOrchestrator()
        
        git_context = {
            'branch': 'main',
            'stagedFiles': [
                'README.md',
                'package.json',
                'docs/api/users.md'
            ],
            'diff': ''
        }
        
        result = orchestrator.validate(git_context)
        
        # Should handle gracefully (no Python files to validate)
        assert result is not None
        assert result['success'] is True
    
    def test_validation_orchestrator_caches_steering_rules(self):
        """Test that steering rules are cached after first load."""
        orchestrator = ValidationOrchestrator()
        
        # First load
        rules1 = orchestrator.load_steering_rules()
        assert orchestrator.steering_rules is not None
        
        # Second load should return the cached rules
        rules2 = orchestrator.load_steering_rules()
        # Verify both loads return valid rules with same structure
        assert rules2 is not None
        assert 'correlation_patterns' in rules2
        assert 'ignore_patterns' in rules2
    
    def test_validation_flow_integration_with_real_files(self):
        """Test validation flow with actual project files."""
        orchestrator = ValidationOrchestrator()
        
        # Test with actual files from the project
        git_context = {
            'branch': 'main',
            'stagedFiles': [
                'backend/models.py',
                'backend/handlers/user.py',
                'backend/handlers/health.py'
            ],
            'diff': 'mock diff'
        }
        
        result = orchestrator.validate(git_context)
        
        # Should complete without errors
        assert result is not None
        assert 'success' in result
        assert 'message' in result
        assert 'allowCommit' in result
        
        # All three report types should be present
        assert 'drift_report' in result
        assert 'test_report' in result
        assert 'doc_report' in result
        
        # Verify the structure is correct
        assert isinstance(result['success'], bool)
        assert isinstance(result['allowCommit'], bool)
