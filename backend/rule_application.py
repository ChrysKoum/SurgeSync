"""
Rule application logic for SpecSync steering rules.

This module provides functionality to apply steering rules to validation contexts,
including correlation pattern matching, minimal change policy application,
and conflict detection.
"""
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class RuleApplicationEngine:
    """Engine for applying steering rules to validation contexts."""
    
    def __init__(self, steering_rules: Dict[str, Any]):
        """
        Initialize the rule application engine.
        
        Args:
            steering_rules: Parsed steering rules dictionary
        """
        self.steering_rules = steering_rules
        self.correlation_patterns = steering_rules.get('correlation_patterns', {})
        self.ignore_patterns = steering_rules.get('ignore_patterns', [])
        self.validation_priorities = steering_rules.get('validation_priorities', {})
        self.minimal_change_policy = steering_rules.get('minimal_change_policy', {})
    
    def apply_correlation_patterns(self, staged_files: List[str]) -> Dict[str, List[str]]:
        """
        Map staged files to their corresponding spec/test/doc files using correlation patterns.
        
        Args:
            staged_files: List of staged file paths
            
        Returns:
            Dictionary mapping each file to related files
        """
        mappings = {}
        
        for file_path in staged_files:
            mappings[file_path] = []
            
            # Check each correlation pattern
            for source_pattern, targets in self.correlation_patterns.items():
                if self._matches_pattern(file_path, source_pattern):
                    for target_info in targets:
                        target_pattern = target_info['target']
                        # Expand target pattern if it contains variables
                        expanded_target = self._expand_pattern(file_path, source_pattern, target_pattern)
                        if expanded_target not in mappings[file_path]:
                            mappings[file_path].append(expanded_target)
        
        return mappings
    
    def filter_ignored_files(self, staged_files: List[str]) -> List[str]:
        """
        Filter out files that match ignore patterns.
        
        Args:
            staged_files: List of staged file paths
            
        Returns:
            Filtered list of files
        """
        filtered = []
        
        for file_path in staged_files:
            should_ignore = False
            for pattern in self.ignore_patterns:
                if self._matches_pattern(file_path, pattern):
                    should_ignore = True
                    break
            
            if not should_ignore:
                filtered.append(file_path)
        
        return filtered
    
    def apply_minimal_change_policy(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply minimal change policy to filter and refine suggestions.
        
        This ensures suggestions follow the minimal change principles:
        - Only necessary modifications
        - Preserve existing structure
        - Incremental fixes
        - No over-engineering
        
        Args:
            suggestions: List of suggestion dictionaries
            
        Returns:
            Filtered and refined list of suggestions
        """
        # For now, we don't filter suggestions, but we could add logic here
        # to detect and remove over-engineered suggestions based on policy
        
        # Add policy context to each suggestion
        for suggestion in suggestions:
            suggestion['minimal_change_policy'] = self.minimal_change_policy
        
        return suggestions
    
    def detect_rule_drift_conflicts(self, 
                                   drift_issues: List[Dict[str, Any]], 
                                   filtered_files: List[str],
                                   all_files: List[str]) -> List[Dict[str, Any]]:
        """
        Detect conflicts between steering rules and detected drift.
        
        A conflict occurs when:
        - A file is ignored by steering rules but contains drift
        - Steering rules suggest one action but drift requires another
        
        Args:
            drift_issues: List of detected drift issues
            filtered_files: Files after applying ignore patterns
            all_files: All staged files before filtering
            
        Returns:
            List of conflict notifications
        """
        conflicts = []
        
        # Find files that were filtered out but have drift
        ignored_files = set(all_files) - set(filtered_files)
        
        for issue in drift_issues:
            issue_file = issue.get('file', '')
            
            # Check if the file with drift was ignored
            if issue_file in ignored_files:
                conflicts.append({
                    'type': 'ignored_file_with_drift',
                    'file': issue_file,
                    'drift_issue': issue,
                    'message': f"Drift detected in '{issue_file}'. Note: This file matches an ignore pattern in steering rules. If this is intentional, update the spec and steering rules.",
                    'priority': 'high'
                })
        
        return conflicts
    
    def prioritize_alignment_over_rules(self, 
                                       conflicts: List[Dict[str, Any]],
                                       validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prioritize alignment over rule preferences and notify developer.
        
        When conflicts exist, alignment takes priority. This function:
        1. Flags the drift despite ignore rules
        2. Adds notifications about conflicts
        3. Suggests updating steering rules if needed
        
        Args:
            conflicts: List of detected conflicts
            validation_result: Current validation result
            
        Returns:
            Updated validation result with conflict notifications
        """
        if not conflicts:
            return validation_result
        
        # Add conflicts to validation result
        if 'conflicts' not in validation_result:
            validation_result['conflicts'] = []
        
        validation_result['conflicts'].extend(conflicts)
        
        # Add conflict notifications to message
        if conflicts:
            conflict_messages = []
            for conflict in conflicts:
                conflict_messages.append(conflict['message'])
            
            # Prepend conflict warnings to main message
            conflict_summary = "\n\n⚠️ STEERING RULE CONFLICTS:\n" + "\n".join(f"  - {msg}" for msg in conflict_messages)
            validation_result['message'] = validation_result.get('message', '') + conflict_summary
            
            # Ensure commit is blocked if there are high-priority conflicts
            high_priority_conflicts = [c for c in conflicts if c.get('priority') == 'high']
            if high_priority_conflicts:
                validation_result['success'] = False
                validation_result['allowCommit'] = False
        
        return validation_result
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """
        Check if a file path matches a glob-like pattern.
        
        Supports:
        - * (matches any characters except /)
        - ** (matches any characters including /)
        - {name} (captures a variable)
        
        Args:
            file_path: File path to check
            pattern: Glob pattern
            
        Returns:
            True if file matches pattern
        """
        # Convert glob pattern to regex
        regex_pattern = pattern
        
        # Handle ** (match any path including /)
        regex_pattern = regex_pattern.replace('**/', '.*/')
        regex_pattern = regex_pattern.replace('**', '.*')
        
        # Handle * (match any characters except /)
        regex_pattern = regex_pattern.replace('*', '[^/]*')
        
        # Handle {name} captures
        regex_pattern = regex_pattern.replace('{', '(?P<')
        regex_pattern = regex_pattern.replace('}', '>[^/]+)')
        
        # Anchor the pattern
        regex_pattern = f'^{regex_pattern}$'
        
        return bool(re.match(regex_pattern, file_path))
    
    def _expand_pattern(self, file_path: str, source_pattern: str, target_pattern: str) -> str:
        """
        Expand a target pattern by substituting captured variables from source pattern.
        
        For example:
        - source: backend/handlers/{module}.py
        - target: tests/unit/test_{module}.py
        - file: backend/handlers/user.py
        - result: tests/unit/test_user.py
        
        Args:
            file_path: Actual file path that matched source pattern
            source_pattern: Source pattern with captures
            target_pattern: Target pattern with variable references
            
        Returns:
            Expanded target pattern
        """
        # Convert source pattern to regex with named groups
        regex_pattern = source_pattern
        regex_pattern = regex_pattern.replace('**/', '.*/')
        regex_pattern = regex_pattern.replace('**', '.*')
        regex_pattern = regex_pattern.replace('*', '[^/]*')
        regex_pattern = regex_pattern.replace('{', '(?P<')
        regex_pattern = regex_pattern.replace('}', '>[^/]+)')
        regex_pattern = f'^{regex_pattern}$'
        
        # Match and extract variables
        match = re.match(regex_pattern, file_path)
        if not match:
            return target_pattern
        
        # Substitute variables in target pattern
        result = target_pattern
        for var_name, var_value in match.groupdict().items():
            result = result.replace(f'{{{var_name}}}', var_value)
        
        return result
    
    def get_priority_for_issue_type(self, issue_type: str) -> int:
        """
        Get the priority number for a given issue type based on validation priorities.
        
        Args:
            issue_type: Type of issue ('spec', 'test', 'doc', etc.)
            
        Returns:
            Priority number (lower = higher priority)
        """
        # Map issue types to priority categories
        type_to_category = {
            'spec': 'Spec Alignment',
            'test': 'Test Coverage',
            'doc': 'Documentation'
        }
        
        category = type_to_category.get(issue_type, issue_type)
        return self.validation_priorities.get(category, 999)
    
    def sort_issues_by_priority(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort issues by validation priority (spec > test > doc).
        
        Args:
            issues: List of issues to sort
            
        Returns:
            Sorted list of issues
        """
        def priority_key(issue: Dict[str, Any]) -> int:
            issue_type = issue.get('type', 'unknown')
            return self.get_priority_for_issue_type(issue_type)
        
        return sorted(issues, key=priority_key)
