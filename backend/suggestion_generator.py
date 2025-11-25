"""
Suggestion generation module for SpecSync.

This module provides functionality to generate actionable suggestions for
resolving drift between specifications, code, tests, and documentation.
"""
from typing import Dict, List, Any, Optional
from pathlib import Path


class Suggestion:
    """Represents a single actionable suggestion for resolving drift."""
    
    def __init__(self, suggestion_type: str, priority: int, file: str,
                 description: str, action: str, rationale: str):
        """
        Initialize a suggestion.
        
        Args:
            suggestion_type: Type of suggestion ('spec', 'test', 'doc')
            priority: Priority score (higher = more important)
            file: File that needs to be modified
            description: Human-readable description of what needs to be done
            action: Specific action to take
            rationale: Why this suggestion is being made
        """
        self.type = suggestion_type
        self.priority = priority
        self.file = file
        self.description = description
        self.action = action
        self.rationale = rationale
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the suggestion to a dictionary."""
        return {
            'type': self.type,
            'priority': self.priority,
            'file': self.file,
            'description': self.description,
            'action': self.action,
            'rationale': self.rationale
        }


class SuggestionGenerator:
    """Generates actionable suggestions from drift detection results."""
    
    def __init__(self, spec_path: Optional[str] = None):
        """
        Initialize the suggestion generator.
        
        Args:
            spec_path: Optional path to spec file
        """
        self.spec_path = spec_path
    
    def generate_spec_update_suggestions(self, drift_issues: List[Dict[str, Any]]) -> List[Suggestion]:
        """
        Generate suggestions for updating specifications based on drift.
        
        Args:
            drift_issues: List of drift issues from drift detector
            
        Returns:
            List of suggestions for spec updates
        """
        suggestions = []
        
        for issue in drift_issues:
            issue_type = issue.get('type')
            description = issue.get('description', '')
            file = issue.get('file', '')
            
            # Handle new functionality not in spec
            if 'not defined in spec' in description or 'not in spec' in description:
                if 'endpoint' in description.lower():
                    # Extract endpoint details from description
                    suggestion = Suggestion(
                        suggestion_type='spec',
                        priority=10,  # High priority - spec drift is critical
                        file=self.spec_path or '.kiro/specs/app.yaml',
                        description=f"Add endpoint definition to spec",
                        action=self._generate_endpoint_spec_action(description),
                        rationale=f"Code implements endpoint not defined in spec: {description}"
                    )
                    suggestions.append(suggestion)
                
                elif 'model' in description.lower():
                    suggestion = Suggestion(
                        suggestion_type='spec',
                        priority=10,
                        file=self.spec_path or '.kiro/specs/app.yaml',
                        description=f"Add model definition to spec",
                        action=self._generate_model_spec_action(description),
                        rationale=f"Code implements model not defined in spec: {description}"
                    )
                    suggestions.append(suggestion)
            
            # Handle functionality in spec but not in code
            elif 'not found in code' in description or 'missing from code' in description:
                if 'endpoint' in description.lower():
                    suggestion = Suggestion(
                        suggestion_type='spec',
                        priority=9,
                        file=file,
                        description=f"Implement missing endpoint or remove from spec",
                        action=self._generate_missing_endpoint_action(description),
                        rationale=f"Spec defines endpoint not implemented in code: {description}"
                    )
                    suggestions.append(suggestion)
                
                elif 'model' in description.lower():
                    suggestion = Suggestion(
                        suggestion_type='spec',
                        priority=9,
                        file=file,
                        description=f"Implement missing model or remove from spec",
                        action=self._generate_missing_model_action(description),
                        rationale=f"Spec defines model not implemented in code: {description}"
                    )
                    suggestions.append(suggestion)
            
            # Handle field mismatches in models
            elif 'missing fields' in description or 'extra fields' in description:
                suggestion = Suggestion(
                    suggestion_type='spec',
                    priority=8,
                    file=self.spec_path or '.kiro/specs/app.yaml',
                    description=f"Align model fields between spec and code",
                    action=self._generate_field_alignment_action(description),
                    rationale=f"Model fields don't match between spec and code: {description}"
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def generate_test_addition_suggestions(self, test_issues: List[Dict[str, Any]]) -> List[Suggestion]:
        """
        Generate suggestions for adding or updating tests.
        
        Args:
            test_issues: List of test coverage issues from test analyzer
            
        Returns:
            List of suggestions for test additions/updates
        """
        suggestions = []
        
        for issue in test_issues:
            issue_type = issue.get('type')
            description = issue.get('description', '')
            file = issue.get('file', '')
            suggestion_text = issue.get('suggestion', '')
            
            # Handle missing test files
            if issue_type == 'missing_tests':
                # Extract module name from file path
                module_name = Path(file).stem
                test_file = f"tests/unit/test_{module_name}.py"
                
                suggestion = Suggestion(
                    suggestion_type='test',
                    priority=7,  # Medium-high priority
                    file=test_file,
                    description=f"Create test file for {file}",
                    action=f"Create {test_file} with tests for all public functions in {file}",
                    rationale=f"Code file has no corresponding test file: {description}"
                )
                suggestions.append(suggestion)
            
            # Handle insufficient coverage
            elif issue_type == 'insufficient_coverage':
                # Extract test file from suggestion if available
                test_file = self._extract_test_file_from_suggestion(suggestion_text)
                
                if 'no test functions' in description.lower():
                    suggestion = Suggestion(
                        suggestion_type='test',
                        priority=8,
                        file=test_file or file,
                        description=f"Add test functions to empty test file",
                        action=f"Add test functions to {test_file} to cover functionality in {file}",
                        rationale=f"Test file exists but contains no tests: {description}"
                    )
                    suggestions.append(suggestion)
                else:
                    # Untested functions
                    suggestion = Suggestion(
                        suggestion_type='test',
                        priority=6,
                        file=test_file or file,
                        description=f"Add tests for untested functions",
                        action=self._generate_test_coverage_action(description, suggestion_text),
                        rationale=f"Some functions lack test coverage: {description}"
                    )
                    suggestions.append(suggestion)
            
            # Handle test-code-spec misalignment
            elif issue_type == 'misalignment':
                if 'no corresponding code file' in description:
                    suggestion = Suggestion(
                        suggestion_type='test',
                        priority=5,
                        file=file,
                        description=f"Fix test file naming or create corresponding code",
                        action=f"Rename test file to match code file naming conventions or create the missing code file",
                        rationale=f"Test file has no corresponding code file: {description}"
                    )
                    suggestions.append(suggestion)
                
                elif "don't exist" in description or 'non-existent' in description:
                    suggestion = Suggestion(
                        suggestion_type='test',
                        priority=7,
                        file=file,
                        description=f"Update tests to match current code",
                        action=f"Remove or update tests that reference non-existent functions",
                        rationale=f"Tests reference functions that don't exist: {description}"
                    )
                    suggestions.append(suggestion)
                
                elif 'spec requires tests' in description:
                    suggestion = Suggestion(
                        suggestion_type='test',
                        priority=8,
                        file=file,
                        description=f"Add tests required by spec",
                        action=self._generate_spec_required_test_action(description),
                        rationale=f"Spec requires tests that are missing: {description}"
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    def generate_documentation_update_suggestions(self, doc_issues: List[Dict[str, Any]]) -> List[Suggestion]:
        """
        Generate suggestions for updating documentation.
        
        Args:
            doc_issues: List of documentation issues from doc analyzer
            
        Returns:
            List of suggestions for documentation updates
        """
        suggestions = []
        
        for issue in doc_issues:
            issue_type = issue.get('type')
            description = issue.get('description', '')
            file = issue.get('file', '')
            suggestion_text = issue.get('suggestion', '')
            
            # Handle missing documentation
            if issue_type == 'missing_docs':
                if 'endpoint' in description.lower():
                    # Extract endpoint details
                    doc_file = self._extract_doc_file_from_suggestion(suggestion_text) or 'docs/api/'
                    
                    suggestion = Suggestion(
                        suggestion_type='doc',
                        priority=5,  # Lower priority than spec and tests
                        file=doc_file,
                        description=f"Document API endpoint",
                        action=self._generate_endpoint_doc_action(description, suggestion_text),
                        rationale=f"API endpoint lacks documentation: {description}"
                    )
                    suggestions.append(suggestion)
                
                elif 'handler file' in description.lower():
                    suggestion = Suggestion(
                        suggestion_type='doc',
                        priority=6,
                        file=file,
                        description=f"Create API documentation for handler",
                        action=f"Create documentation file for endpoints in {file}",
                        rationale=f"Handler file has no documentation: {description}"
                    )
                    suggestions.append(suggestion)
            
            # Handle documentation-code mismatches
            elif issue_type == 'doc_code_mismatch':
                if 'not found in' in description:
                    suggestion = Suggestion(
                        suggestion_type='doc',
                        priority=6,
                        file=file,
                        description=f"Remove or update outdated documentation",
                        action=self._generate_doc_removal_action(description, suggestion_text),
                        rationale=f"Documentation describes non-existent functionality: {description}"
                    )
                    suggestions.append(suggestion)
            
            # Handle outdated documentation
            elif issue_type == 'outdated_docs':
                suggestion = Suggestion(
                    suggestion_type='doc',
                    priority=5,
                    file=file,
                    description=f"Remove documentation for removed features",
                    action=self._generate_outdated_doc_action(description, suggestion_text),
                    rationale=f"Documentation describes removed functionality: {description}"
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_endpoint_spec_action(self, description: str) -> str:
        """Generate specific action for adding endpoint to spec."""
        # Try to extract endpoint details from description
        import re
        match = re.search(r'(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s]+)', description)
        if match:
            method = match.group(1)
            path = match.group(2)
            return f"Add endpoint definition to spec:\n  - path: \"{path}\"\n    method: \"{method}\"\n    description: \"[Add description]\"\n    response:\n      type: \"[Add type]\""
        return "Add the endpoint definition to the spec file with path, method, description, and response schema"
    
    def _generate_model_spec_action(self, description: str) -> str:
        """Generate specific action for adding model to spec."""
        # Try to extract model name from description
        import re
        match = re.search(r"model '([^']+)'", description, re.IGNORECASE)
        if match:
            model_name = match.group(1)
            return f"Add model definition to spec:\n  {model_name}:\n    fields:\n      - name: \"[field_name]\"\n        type: \"[field_type]\""
        return "Add the model definition to the spec file with all fields and their types"
    
    def _generate_missing_endpoint_action(self, description: str) -> str:
        """Generate specific action for missing endpoint."""
        import re
        match = re.search(r'(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s]+)', description)
        if match:
            method = match.group(1)
            path = match.group(2)
            return f"Either:\n  1. Implement the {method} {path} endpoint in code, OR\n  2. Remove the endpoint definition from the spec if it's no longer needed"
        return "Either implement the endpoint in code or remove it from the spec"
    
    def _generate_missing_model_action(self, description: str) -> str:
        """Generate specific action for missing model."""
        import re
        match = re.search(r"model '([^']+)'", description, re.IGNORECASE)
        if match:
            model_name = match.group(1)
            return f"Either:\n  1. Implement the {model_name} model in code, OR\n  2. Remove the model definition from the spec if it's no longer needed"
        return "Either implement the model in code or remove it from the spec"
    
    def _generate_field_alignment_action(self, description: str) -> str:
        """Generate specific action for field alignment."""
        if 'missing fields' in description.lower():
            return "Add the missing fields to the model implementation in code, or remove them from the spec if they're not needed"
        elif 'extra fields' in description.lower():
            return "Either add the extra fields to the spec, or remove them from the code implementation"
        return "Align the model fields between spec and code"
    
    def _extract_test_file_from_suggestion(self, suggestion: str) -> Optional[str]:
        """Extract test file path from suggestion text."""
        import re
        match = re.search(r'tests/[^\s]+\.py', suggestion)
        if match:
            return match.group(0)
        return None
    
    def _generate_test_coverage_action(self, description: str, suggestion: str) -> str:
        """Generate specific action for test coverage."""
        # Try to extract function names from description
        import re
        match = re.search(r'lack test coverage: (.+)$', description)
        if match:
            functions = match.group(1)
            test_file = self._extract_test_file_from_suggestion(suggestion)
            if test_file:
                return f"Add test functions to {test_file} to cover: {functions}"
            return f"Add test functions to cover: {functions}"
        return suggestion or "Add tests for untested functions"
    
    def _generate_spec_required_test_action(self, description: str) -> str:
        """Generate specific action for spec-required tests."""
        import re
        match = re.search(r'(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s]+)', description)
        if match:
            method = match.group(1)
            path = match.group(2)
            return f"Add test for {method} {path} endpoint as required by spec"
        return "Add tests as required by spec"
    
    def _extract_doc_file_from_suggestion(self, suggestion: str) -> Optional[str]:
        """Extract documentation file path from suggestion text."""
        import re
        match = re.search(r'docs/[^\s]+\.md', suggestion)
        if match:
            return match.group(0)
        return None
    
    def _generate_endpoint_doc_action(self, description: str, suggestion: str) -> str:
        """Generate specific action for endpoint documentation."""
        import re
        match = re.search(r'(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s]+)', description)
        doc_file = self._extract_doc_file_from_suggestion(suggestion)
        
        if match and doc_file:
            method = match.group(1)
            path = match.group(2)
            return f"Add documentation for {method} {path} to {doc_file} including:\n  - Description\n  - Request format\n  - Response format\n  - Example"
        return suggestion or "Add endpoint documentation"
    
    def _generate_doc_removal_action(self, description: str, suggestion: str) -> str:
        """Generate specific action for removing outdated docs."""
        import re
        match = re.search(r'(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s]+)', description)
        if match:
            method = match.group(1)
            path = match.group(2)
            return f"Remove documentation for {method} {path} or implement the endpoint if it should exist"
        return suggestion or "Remove or update outdated documentation"
    
    def _generate_outdated_doc_action(self, description: str, suggestion: str) -> str:
        """Generate specific action for outdated documentation."""
        return suggestion or "Remove documentation for removed functionality"



class SuggestionPrioritizer:
    """Prioritizes and orders suggestions by impact and logical sequence."""
    
    # Priority weights for different issue types
    TYPE_PRIORITIES = {
        'spec': 10,  # Highest - spec defines the contract
        'test': 7,   # Medium-high - tests verify correctness
        'doc': 5     # Lower - docs help users but don't affect correctness
    }
    
    def __init__(self):
        """Initialize the suggestion prioritizer."""
        pass
    
    def categorize_drift_by_type(self, suggestions: List[Suggestion]) -> Dict[str, List[Suggestion]]:
        """
        Categorize suggestions by type (spec, test, doc).
        
        Args:
            suggestions: List of suggestions to categorize
            
        Returns:
            Dictionary mapping types to lists of suggestions
        """
        categorized = {
            'spec': [],
            'test': [],
            'doc': []
        }
        
        for suggestion in suggestions:
            suggestion_type = suggestion.type
            if suggestion_type in categorized:
                categorized[suggestion_type].append(suggestion)
        
        return categorized
    
    def assign_impact_scores(self, suggestions: List[Suggestion]) -> List[Suggestion]:
        """
        Assign impact scores to suggestions based on type and content.
        
        The impact score is calculated based on:
        - Type priority (spec > test > doc)
        - Severity keywords in description
        - File importance
        
        Args:
            suggestions: List of suggestions to score
            
        Returns:
            List of suggestions with updated priority scores
        """
        for suggestion in suggestions:
            base_priority = suggestion.priority
            
            # Adjust based on type
            type_weight = self.TYPE_PRIORITIES.get(suggestion.type, 5)
            
            # Adjust based on severity keywords
            severity_boost = 0
            description_lower = suggestion.description.lower()
            
            if any(word in description_lower for word in ['critical', 'breaking', 'error']):
                severity_boost = 3
            elif any(word in description_lower for word in ['missing', 'required', 'must']):
                severity_boost = 2
            elif any(word in description_lower for word in ['should', 'recommended']):
                severity_boost = 1
            
            # Adjust based on file importance
            file_boost = 0
            if 'main.py' in suggestion.file or 'models.py' in suggestion.file:
                file_boost = 1
            
            # Calculate final priority
            suggestion.priority = base_priority + severity_boost + file_boost
        
        return suggestions
    
    def order_suggestions_by_impact(self, suggestions: List[Suggestion]) -> List[Suggestion]:
        """
        Order suggestions by impact and logical sequence.
        
        The ordering follows these rules:
        1. Spec suggestions first (highest priority)
        2. Test suggestions second
        3. Documentation suggestions last
        4. Within each category, order by priority score (descending)
        5. Within same priority, order by file path for consistency
        
        Args:
            suggestions: List of suggestions to order
            
        Returns:
            Ordered list of suggestions
        """
        # First, assign impact scores
        suggestions = self.assign_impact_scores(suggestions)
        
        # Sort by type priority (spec > test > doc), then by priority score, then by file
        def sort_key(s: Suggestion):
            type_priority = self.TYPE_PRIORITIES.get(s.type, 5)
            return (-type_priority, -s.priority, s.file)
        
        return sorted(suggestions, key=sort_key)
    
    def group_related_suggestions(self, suggestions: List[Suggestion]) -> List[Dict[str, Any]]:
        """
        Group related suggestions together for better presentation.
        
        Suggestions are grouped by:
        - Same file
        - Same type and related functionality
        
        Args:
            suggestions: List of suggestions to group
            
        Returns:
            List of suggestion groups with metadata
        """
        groups = []
        suggestions_by_file = {}
        
        # Group by file first
        for suggestion in suggestions:
            file = suggestion.file
            if file not in suggestions_by_file:
                suggestions_by_file[file] = []
            suggestions_by_file[file].append(suggestion)
        
        # Create groups
        for file, file_suggestions in suggestions_by_file.items():
            # Sort suggestions within file by priority
            file_suggestions.sort(key=lambda s: -s.priority)
            
            group = {
                'file': file,
                'type': file_suggestions[0].type if file_suggestions else 'unknown',
                'count': len(file_suggestions),
                'max_priority': max(s.priority for s in file_suggestions) if file_suggestions else 0,
                'suggestions': file_suggestions
            }
            groups.append(group)
        
        # Sort groups by max priority
        groups.sort(key=lambda g: -g['max_priority'])
        
        return groups
    
    def generate_prioritized_report(self, suggestions: List[Suggestion]) -> Dict[str, Any]:
        """
        Generate a comprehensive prioritized report of suggestions.
        
        Args:
            suggestions: List of suggestions to include in report
            
        Returns:
            Dictionary containing prioritized and categorized suggestions
        """
        # Order suggestions
        ordered_suggestions = self.order_suggestions_by_impact(suggestions)
        
        # Categorize by type
        categorized = self.categorize_drift_by_type(ordered_suggestions)
        
        # Group related suggestions
        groups = self.group_related_suggestions(ordered_suggestions)
        
        # Generate summary statistics
        summary = {
            'total_suggestions': len(suggestions),
            'by_type': {
                'spec': len(categorized['spec']),
                'test': len(categorized['test']),
                'doc': len(categorized['doc'])
            },
            'high_priority': len([s for s in suggestions if s.priority >= 8]),
            'medium_priority': len([s for s in suggestions if 5 <= s.priority < 8]),
            'low_priority': len([s for s in suggestions if s.priority < 5])
        }
        
        return {
            'summary': summary,
            'ordered_suggestions': [s.to_dict() for s in ordered_suggestions],
            'categorized': {k: [s.to_dict() for s in v] for k, v in categorized.items()},
            'groups': [
                {
                    'file': g['file'],
                    'type': g['type'],
                    'count': g['count'],
                    'max_priority': g['max_priority'],
                    'suggestions': [s.to_dict() for s in g['suggestions']]
                }
                for g in groups
            ]
        }


class ComprehensiveSuggestionGenerator:
    """
    Main class that combines all suggestion generation and prioritization.
    
    This is the primary interface for generating suggestions from drift reports.
    """
    
    def __init__(self, spec_path: Optional[str] = None):
        """
        Initialize the comprehensive suggestion generator.
        
        Args:
            spec_path: Optional path to spec file
        """
        self.generator = SuggestionGenerator(spec_path)
        self.prioritizer = SuggestionPrioritizer()
    
    def generate_all_suggestions(self, 
                                 drift_issues: Optional[List[Dict[str, Any]]] = None,
                                 test_issues: Optional[List[Dict[str, Any]]] = None,
                                 doc_issues: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate all suggestions from drift, test, and documentation issues.
        
        Args:
            drift_issues: List of drift issues from drift detector
            test_issues: List of test coverage issues from test analyzer
            doc_issues: List of documentation issues from doc analyzer
            
        Returns:
            Comprehensive prioritized report of all suggestions
        """
        all_suggestions = []
        
        # Generate spec update suggestions
        if drift_issues:
            spec_suggestions = self.generator.generate_spec_update_suggestions(drift_issues)
            all_suggestions.extend(spec_suggestions)
        
        # Generate test addition suggestions
        if test_issues:
            test_suggestions = self.generator.generate_test_addition_suggestions(test_issues)
            all_suggestions.extend(test_suggestions)
        
        # Generate documentation update suggestions
        if doc_issues:
            doc_suggestions = self.generator.generate_documentation_update_suggestions(doc_issues)
            all_suggestions.extend(doc_suggestions)
        
        # Generate prioritized report
        if not all_suggestions:
            return {
                'summary': {
                    'total_suggestions': 0,
                    'by_type': {'spec': 0, 'test': 0, 'doc': 0},
                    'high_priority': 0,
                    'medium_priority': 0,
                    'low_priority': 0
                },
                'ordered_suggestions': [],
                'categorized': {'spec': [], 'test': [], 'doc': []},
                'groups': []
            }
        
        return self.prioritizer.generate_prioritized_report(all_suggestions)
    
    def generate_suggestions_from_reports(self,
                                         drift_report: Optional[Dict[str, Any]] = None,
                                         test_report: Optional[Dict[str, Any]] = None,
                                         doc_report: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate suggestions from complete validation reports.
        
        This is a convenience method that extracts issues from reports
        and generates suggestions.
        
        Args:
            drift_report: Drift report from drift detector
            test_report: Test coverage report from test analyzer
            doc_report: Documentation report from doc analyzer
            
        Returns:
            Comprehensive prioritized report of all suggestions
        """
        # Extract issues from reports
        drift_issues = []
        if drift_report and 'issues' in drift_report:
            drift_issues = drift_report['issues']
        
        test_issues = []
        if test_report and 'issues' in test_report:
            test_issues = test_report['issues']
        
        doc_issues = []
        if doc_report and 'issues' in doc_report:
            doc_issues = doc_report['issues']
        
        return self.generate_all_suggestions(drift_issues, test_issues, doc_issues)
    
    def format_suggestions_for_display(self, report: Dict[str, Any]) -> str:
        """
        Format suggestions as human-readable text for display.
        
        Args:
            report: Prioritized suggestion report
            
        Returns:
            Formatted string for display
        """
        lines = []
        
        # Add summary
        summary = report['summary']
        lines.append("=== Suggestion Summary ===")
        lines.append(f"Total suggestions: {summary['total_suggestions']}")
        lines.append(f"  - Spec updates: {summary['by_type']['spec']}")
        lines.append(f"  - Test additions: {summary['by_type']['test']}")
        lines.append(f"  - Documentation updates: {summary['by_type']['doc']}")
        lines.append("")
        lines.append(f"Priority breakdown:")
        lines.append(f"  - High priority (8+): {summary['high_priority']}")
        lines.append(f"  - Medium priority (5-7): {summary['medium_priority']}")
        lines.append(f"  - Low priority (<5): {summary['low_priority']}")
        lines.append("")
        
        # Add ordered suggestions
        lines.append("=== Prioritized Suggestions ===")
        lines.append("")
        
        for i, suggestion in enumerate(report['ordered_suggestions'], 1):
            lines.append(f"{i}. [{suggestion['type'].upper()}] Priority {suggestion['priority']}")
            lines.append(f"   File: {suggestion['file']}")
            lines.append(f"   Description: {suggestion['description']}")
            lines.append(f"   Action: {suggestion['action']}")
            lines.append(f"   Rationale: {suggestion['rationale']}")
            lines.append("")
        
        return "\n".join(lines)
