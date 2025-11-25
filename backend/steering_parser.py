"""
Steering rules parser module for SpecSync.

This module provides functionality to parse steering rules markdown documents
and extract correlation patterns, ignore patterns, validation priorities,
and minimal change policies.
"""
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


class SteeringRulesParser:
    """Parser for steering rules markdown document."""
    
    def __init__(self, rules_path: str = ".kiro/steering/rules.md"):
        """
        Initialize the steering rules parser.
        
        Args:
            rules_path: Path to the steering rules markdown file
        """
        self.rules_path = Path(rules_path)
        self.content: Optional[str] = None
        self.correlation_patterns: Dict[str, List[Dict[str, str]]] = {}
        self.ignore_patterns: List[str] = []
        self.validation_priorities: Dict[str, int] = {}
        self.minimal_change_policy: Dict[str, str] = {}
        self._last_modified: Optional[float] = None
        self._cached_rules: Optional[Dict[str, Any]] = None
    
    def parse(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Parse the steering rules document and extract all rules.
        
        Args:
            force_reload: If True, bypass cache and reload from file
        
        Returns:
            Dictionary containing all parsed rules
            
        Raises:
            FileNotFoundError: If steering rules file doesn't exist
        """
        # Check if we can use cached rules
        if not force_reload and self._cached_rules is not None:
            current_mtime = self._get_file_mtime()
            if current_mtime == self._last_modified:
                return self._cached_rules
        
        # File doesn't exist or has been modified, parse it
        if not self.rules_path.exists():
            raise FileNotFoundError(f"Steering rules file not found: {self.rules_path}")
        
        self.content = self.rules_path.read_text(encoding='utf-8')
        self._last_modified = self._get_file_mtime()
        
        # Extract correlation patterns
        self._parse_correlation_patterns()
        
        # Extract ignore patterns
        self._parse_ignore_patterns()
        
        # Extract validation priorities
        self._parse_validation_priorities()
        
        # Extract minimal change policy
        self._parse_minimal_change_policy()
        
        # Cache the results
        self._cached_rules = {
            'correlation_patterns': self.correlation_patterns,
            'ignore_patterns': self.ignore_patterns,
            'validation_priorities': self.validation_priorities,
            'minimal_change_policy': self.minimal_change_policy
        }
        
        return self._cached_rules
    
    def _get_file_mtime(self) -> Optional[float]:
        """
        Get the last modification time of the steering rules file.
        
        Returns:
            Modification time as float, or None if file doesn't exist
        """
        try:
            return os.path.getmtime(self.rules_path)
        except (OSError, FileNotFoundError):
            return None
    
    def invalidate_cache(self) -> None:
        """Invalidate the cached rules, forcing a reload on next parse."""
        self._cached_rules = None
        self._last_modified = None
    
    def _parse_correlation_patterns(self) -> None:
        """Extract file correlation patterns from the rules document."""
        # Pattern: source_pattern → target_pattern
        pattern = r'- `([^`]+)` → `([^`]+)`'
        matches = re.findall(pattern, self.content)
        
        # Clear existing patterns
        self.correlation_patterns = {}
        
        for source, target in matches:
            if source not in self.correlation_patterns:
                self.correlation_patterns[source] = []
            self.correlation_patterns[source].append({
                'source': source,
                'target': target
            })
    
    def _parse_ignore_patterns(self) -> None:
        """Extract ignore patterns from the rules document."""
        # Clear existing patterns
        self.ignore_patterns = []
        
        # Look for patterns under "Generated Files", "Vendor Code", etc.
        in_ignore_section = False
        for line in self.content.split('\n'):
            if '### Generated Files' in line or '### Vendor Code' in line or \
               '### Configuration Files' in line or '### Non-Functional Changes' in line or \
               '### Test Fixtures and Utilities' in line:
                in_ignore_section = True
                continue
            
            if in_ignore_section:
                if line.startswith('###') or line.startswith('##'):
                    in_ignore_section = False
                    continue
                
                # Extract patterns from list items
                if line.strip().startswith('- `'):
                    pattern_match = re.search(r'`([^`]+)`', line)
                    if pattern_match:
                        self.ignore_patterns.append(pattern_match.group(1))
    
    def _parse_validation_priorities(self) -> None:
        """Extract validation priorities from the rules document."""
        # Clear existing priorities
        self.validation_priorities = {}
        
        # Look for numbered priority list
        priority_pattern = r'(\d+)\.\s+\*\*([^*]+)\*\*\s+\(([^)]+)\)'
        matches = re.findall(priority_pattern, self.content)
        
        for priority, category, level in matches:
            self.validation_priorities[category.strip()] = int(priority)
    
    def _parse_minimal_change_policy(self) -> None:
        """Extract minimal change policy guidelines from the rules document."""
        # Clear existing policy
        self.minimal_change_policy = {}
        
        in_policy_section = False
        for line in self.content.split('\n'):
            if '## Minimal Change Policy' in line:
                in_policy_section = True
                continue
            
            if in_policy_section:
                if line.startswith('##'):
                    break
                
                # Extract numbered policy items
                if re.match(r'^\d+\.', line.strip()):
                    parts = line.split('-', 1)
                    if len(parts) == 2:
                        key = parts[0].strip().strip('0123456789.')
                        value = parts[1].strip()
                        self.minimal_change_policy[key] = value
    
    def get_correlation_patterns(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get correlation patterns from parsed rules.
        
        Returns:
            Dictionary mapping source patterns to target patterns
        """
        if self._cached_rules is None:
            self.parse()
        return self.correlation_patterns
    
    def get_ignore_patterns(self) -> List[str]:
        """
        Get ignore patterns from parsed rules.
        
        Returns:
            List of glob patterns to ignore
        """
        if self._cached_rules is None:
            self.parse()
        return self.ignore_patterns
    
    def get_validation_priorities(self) -> Dict[str, int]:
        """
        Get validation priorities from parsed rules.
        
        Returns:
            Dictionary mapping categories to priority numbers
        """
        if self._cached_rules is None:
            self.parse()
        return self.validation_priorities
    
    def get_minimal_change_policy(self) -> Dict[str, str]:
        """
        Get minimal change policy from parsed rules.
        
        Returns:
            Dictionary of policy guidelines
        """
        if self._cached_rules is None:
            self.parse()
        return self.minimal_change_policy
