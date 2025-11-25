"""
Documentation validation module for SpecSync.

This module provides functionality to validate documentation alignment with
code changes and specifications.
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Any


class MarkdownParser:
    """Parser for markdown documentation files."""
    
    def __init__(self, doc_path: str):
        """
        Initialize the markdown parser.
        
        Args:
            doc_path: Path to the markdown documentation file
        """
        self.doc_path = Path(doc_path)
        self.content: Optional[str] = None
        self.sections: Dict[str, str] = {}
    
    def parse(self) -> str:
        """
        Parse the markdown file and return its content.
        
        Returns:
            String containing the markdown content
            
        Raises:
            FileNotFoundError: If documentation file doesn't exist
        """
        if not self.doc_path.exists():
            raise FileNotFoundError(f"Documentation file not found: {self.doc_path}")
        
        with open(self.doc_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        
        # Parse sections
        self._parse_sections()
        
        return self.content
    
    def _parse_sections(self):
        """Parse markdown into sections based on headers."""
        if self.content is None:
            return
        
        # Split by headers (## or ###)
        lines = self.content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Check for headers
            if line.startswith('## '):
                # Save previous section
                if current_section:
                    self.sections[current_section] = '\n'.join(current_content)
                # Start new section
                current_section = line[3:].strip()
                current_content = [line]
            elif line.startswith('### '):
                # Save previous section
                if current_section:
                    self.sections[current_section] = '\n'.join(current_content)
                # Start new section
                current_section = line[4:].strip()
                current_content = [line]
            else:
                current_content.append(line)
        
        # Save last section
        if current_section:
            self.sections[current_section] = '\n'.join(current_content)
    
    def extract_api_descriptions(self) -> List[Dict[str, Any]]:
        """
        Extract API endpoint descriptions from the documentation.
        
        Returns:
            List of API endpoint descriptions with method, path, and description
        """
        if self.content is None:
            self.parse()
        
        api_endpoints = []
        
        # Pattern to match endpoint headers like "GET /users" or "POST /users/{id}"
        endpoint_pattern = r'^##\s+(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s]*)'
        
        lines = self.content.split('\n')
        for i, line in enumerate(lines):
            match = re.match(endpoint_pattern, line)
            if match:
                method = match.group(1)
                path = match.group(2)
                
                # Extract description from following lines
                description = ""
                for j in range(i + 1, min(i + 10, len(lines))):
                    if lines[j].startswith('##'):
                        break
                    if lines[j].strip() and not lines[j].startswith('#'):
                        description = lines[j].strip()
                        break
                
                api_endpoints.append({
                    'method': method,
                    'path': path,
                    'description': description,
                    'line': i + 1
                })
        
        return api_endpoints
    
    def get_sections(self) -> Dict[str, str]:
        """
        Get all sections from the markdown document.
        
        Returns:
            Dictionary mapping section names to their content
        """
        if not self.sections:
            self.parse()
        
        return self.sections
    
    def contains_text(self, text: str, case_sensitive: bool = False) -> bool:
        """
        Check if the documentation contains specific text.
        
        Args:
            text: Text to search for
            case_sensitive: Whether to perform case-sensitive search
            
        Returns:
            True if text is found, False otherwise
        """
        if self.content is None:
            self.parse()
        
        if case_sensitive:
            return text in self.content
        else:
            return text.lower() in self.content.lower()
    
    def extract_code_references(self) -> List[str]:
        """
        Extract code references from the documentation.
        
        This includes:
        - Function names in code blocks
        - File paths mentioned
        - API endpoints
        
        Returns:
            List of code references found in the documentation
        """
        if self.content is None:
            self.parse()
        
        references = []
        
        # Extract code blocks
        code_block_pattern = r'```[\w]*\n(.*?)```'
        code_blocks = re.findall(code_block_pattern, self.content, re.DOTALL)
        
        for block in code_blocks:
            # Extract function-like patterns
            function_pattern = r'\b([a-z_][a-z0-9_]*)\s*\('
            functions = re.findall(function_pattern, block, re.IGNORECASE)
            references.extend(functions)
        
        # Extract file paths
        file_pattern = r'`([a-zA-Z0-9_/.-]+\.(py|yaml|md|json))`'
        files = re.findall(file_pattern, self.content)
        references.extend([f[0] for f in files])
        
        # Extract API endpoints
        endpoint_pattern = r'`?(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s`]*)`?'
        endpoints = re.findall(endpoint_pattern, self.content)
        references.extend([f"{method} {path}" for method, path in endpoints])
        
        return list(set(references))  # Remove duplicates


class DocumentationMapper:
    """Maps code changes to corresponding documentation sections."""
    
    def __init__(self, project_root: str = "."):
        """
        Initialize the documentation mapper.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
    
    def map_code_to_docs(self, code_file: str) -> List[str]:
        """
        Map a code file to its corresponding documentation files.
        
        Uses conventions:
        - backend/handlers/user.py -> docs/api/users.md
        - backend/handlers/health.py -> docs/api/health.md
        - backend/main.py -> docs/architecture.md
        
        Args:
            code_file: Path to the code file
            
        Returns:
            List of documentation file paths that should document this code
        """
        code_path = Path(code_file)
        doc_files = []
        
        # Map handlers to API documentation
        if code_path.match('backend/handlers/*.py'):
            module_name = code_path.stem
            # Pluralize common names (user -> users, but health stays health)
            if module_name in ['user', 'item', 'product', 'order']:
                doc_name = f"{module_name}s.md"
            else:
                doc_name = f"{module_name}.md"
            
            doc_file = self.docs_dir / "api" / doc_name
            if doc_file.exists():
                doc_files.append(str(doc_file))
        
        # Map main.py to architecture docs
        elif code_path.match('backend/main.py'):
            doc_file = self.docs_dir / "architecture.md"
            if doc_file.exists():
                doc_files.append(str(doc_file))
        
        # Map models to API docs (they might be referenced in multiple docs)
        elif code_path.match('backend/models.py'):
            # Check all API docs
            api_dir = self.docs_dir / "api"
            if api_dir.exists():
                for doc_file in api_dir.glob("*.md"):
                    doc_files.append(str(doc_file))
        
        return doc_files
    
    def map_endpoint_to_docs(self, method: str, path: str) -> List[str]:
        """
        Map an API endpoint to its documentation file.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Endpoint path (e.g., "/users")
            
        Returns:
            List of documentation files that should document this endpoint
        """
        doc_files = []
        
        # Extract the resource name from the path
        # /users -> users, /users/{id} -> users, /health -> health
        path_parts = path.strip('/').split('/')
        if path_parts and path_parts[0]:
            resource = path_parts[0]
            
            # Check for corresponding doc file
            doc_file = self.docs_dir / "api" / f"{resource}.md"
            if doc_file.exists():
                doc_files.append(str(doc_file))
        
        return doc_files
    
    def find_all_doc_files(self) -> List[str]:
        """
        Find all documentation files in the project.
        
        Returns:
            List of all documentation file paths
        """
        doc_files = []
        
        if not self.docs_dir.exists():
            return doc_files
        
        # Find all markdown files recursively
        for doc_file in self.docs_dir.rglob("*.md"):
            doc_files.append(str(doc_file))
        
        return doc_files
    
    def get_public_api_files(self) -> List[str]:
        """
        Get documentation files for public APIs.
        
        Returns:
            List of API documentation file paths
        """
        api_dir = self.docs_dir / "api"
        if not api_dir.exists():
            return []
        
        return [str(f) for f in api_dir.glob("*.md")]


class DocumentationAnalyzer:
    """Main analyzer that combines parsing and mapping for documentation validation."""
    
    def __init__(self, project_root: str = ".", spec_path: Optional[str] = None):
        """
        Initialize the documentation analyzer.
        
        Args:
            project_root: Root directory of the project
            spec_path: Optional path to spec file for alignment checks
        """
        self.project_root = Path(project_root)
        self.mapper = DocumentationMapper(project_root)
        self.spec_path = spec_path
        
        # Import spec parser if spec path provided
        if spec_path:
            from backend.drift_detector import SpecParser
            self.spec_parser = SpecParser(spec_path)
            self.spec_parser.parse()
        else:
            self.spec_parser = None
    
    def analyze_doc_file(self, doc_file: str) -> Dict[str, Any]:
        """
        Analyze a documentation file and extract information.
        
        Args:
            doc_file: Path to the documentation file
            
        Returns:
            Dictionary containing analysis results
        """
        parser = MarkdownParser(doc_file)
        parser.parse()
        
        return {
            'file': doc_file,
            'sections': parser.get_sections(),
            'api_endpoints': parser.extract_api_descriptions(),
            'code_references': parser.extract_code_references()
        }
    
    def check_endpoint_documented(self, method: str, path: str) -> Dict[str, Any]:
        """
        Check if an API endpoint is documented.
        
        Args:
            method: HTTP method
            path: Endpoint path
            
        Returns:
            Dictionary with documentation status
        """
        doc_files = self.mapper.map_endpoint_to_docs(method, path)
        
        if not doc_files:
            return {
                'documented': False,
                'reason': 'No documentation file found for this endpoint',
                'expected_file': None
            }
        
        # Check each doc file for the endpoint
        for doc_file in doc_files:
            parser = MarkdownParser(doc_file)
            api_endpoints = parser.extract_api_descriptions()
            
            # Check if endpoint is documented
            for endpoint in api_endpoints:
                if endpoint['method'] == method and endpoint['path'] == path:
                    return {
                        'documented': True,
                        'file': doc_file,
                        'description': endpoint['description']
                    }
        
        return {
            'documented': False,
            'reason': 'Endpoint not found in documentation',
            'expected_file': doc_files[0] if doc_files else None
        }
    
    def check_code_file_documented(self, code_file: str) -> Dict[str, Any]:
        """
        Check if a code file has corresponding documentation.
        
        Args:
            code_file: Path to the code file
            
        Returns:
            Dictionary with documentation status
        """
        doc_files = self.mapper.map_code_to_docs(code_file)
        
        if not doc_files:
            return {
                'has_docs': False,
                'reason': 'No documentation mapping for this code file',
                'doc_files': []
            }
        
        # Check if doc files exist and contain relevant content
        existing_docs = [f for f in doc_files if Path(f).exists()]
        
        return {
            'has_docs': len(existing_docs) > 0,
            'doc_files': existing_docs,
            'missing_docs': [f for f in doc_files if f not in existing_docs]
        }
    
    def extract_endpoints_from_code(self, code_file: str) -> List[Dict[str, Any]]:
        """
        Extract API endpoints from a code file.
        
        Args:
            code_file: Path to the code file
            
        Returns:
            List of endpoints found in the code
        """
        from backend.drift_detector import CodeParser
        
        parser = CodeParser(code_file)
        parser.parse()
        return parser.extract_endpoints()



class DocumentationIssue:
    """Represents a documentation alignment issue detected during validation."""
    
    def __init__(self, issue_type: str, severity: str, file: str, 
                 description: str, suggestion: str):
        """
        Initialize a documentation issue.
        
        Args:
            issue_type: Type of issue ('missing_docs', 'outdated_docs', 'doc_code_mismatch')
            severity: Severity level ('error', 'warning')
            file: File where issue was detected
            description: Human-readable description of the issue
            suggestion: Suggested fix for the issue
        """
        self.type = issue_type
        self.severity = severity
        self.file = file
        self.description = description
        self.suggestion = suggestion
    
    def to_dict(self) -> Dict[str, str]:
        """Convert the issue to a dictionary."""
        return {
            'type': self.type,
            'severity': self.severity,
            'file': self.file,
            'description': self.description,
            'suggestion': self.suggestion
        }


class DocumentationReport:
    """Structured report of documentation alignment issues."""
    
    def __init__(self):
        """Initialize an empty documentation report."""
        self.issues: List[DocumentationIssue] = []
        self.summary: Dict[str, Any] = {}
    
    def add_issue(self, issue: DocumentationIssue):
        """Add a documentation issue to the report."""
        self.issues.append(issue)
    
    def has_issues(self) -> bool:
        """Check if there are any documentation issues."""
        return len(self.issues) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the report to a dictionary."""
        return {
            'has_issues': self.has_issues(),
            'issues': [issue.to_dict() for issue in self.issues],
            'summary': self.summary
        }


class DocumentationAlignmentDetector:
    """Detects documentation alignment issues with code and specs."""
    
    def __init__(self, project_root: str = ".", spec_path: Optional[str] = None):
        """
        Initialize the documentation alignment detector.
        
        Args:
            project_root: Root directory of the project
            spec_path: Optional path to spec file for alignment checks
        """
        self.project_root = Path(project_root)
        self.analyzer = DocumentationAnalyzer(project_root, spec_path)
        self.mapper = DocumentationMapper(project_root)
        self.spec_path = spec_path
        
        # Import spec parser if spec path provided
        if spec_path:
            from backend.drift_detector import SpecParser
            self.spec_parser = SpecParser(spec_path)
            self.spec_parser.parse()
        else:
            self.spec_parser = None
    
    def detect_api_changes_requiring_docs(self, code_file: str) -> List[DocumentationIssue]:
        """
        Detect API changes in code that require documentation updates.
        
        This checks if:
        - New endpoints are added without documentation
        - Endpoints are modified but docs not updated
        - Public APIs lack documentation
        
        Args:
            code_file: Path to the code file
            
        Returns:
            List of documentation issues for API changes
        """
        issues = []
        
        # Extract endpoints from code
        endpoints = self.analyzer.extract_endpoints_from_code(code_file)
        
        if not endpoints:
            # No endpoints in this file, no API documentation required
            return issues
        
        # Check each endpoint for documentation
        for endpoint in endpoints:
            method = endpoint['method']
            path = endpoint['path']
            
            doc_status = self.analyzer.check_endpoint_documented(method, path)
            
            if not doc_status['documented']:
                issue = DocumentationIssue(
                    issue_type='missing_docs',
                    severity='error',
                    file=code_file,
                    description=f"API endpoint {method} {path} is not documented",
                    suggestion=f"Add documentation for {method} {path} in {doc_status.get('expected_file', 'docs/api/')}"
                )
                issues.append(issue)
        
        return issues
    
    def detect_doc_code_mismatches(self, code_file: str) -> List[DocumentationIssue]:
        """
        Detect mismatches between documentation and code implementation.
        
        This checks if:
        - Documentation describes endpoints that don't exist in code
        - Documentation describes different behavior than code implements
        - Parameter descriptions don't match code
        
        Args:
            code_file: Path to the code file
            
        Returns:
            List of documentation issues for mismatches
        """
        issues = []
        
        # Get documentation files for this code file
        doc_files = self.mapper.map_code_to_docs(code_file)
        
        if not doc_files:
            return issues
        
        # Extract endpoints from code
        code_endpoints = self.analyzer.extract_endpoints_from_code(code_file)
        code_endpoint_set = {(ep['method'], ep['path']) for ep in code_endpoints}
        
        # Check each doc file
        for doc_file in doc_files:
            if not Path(doc_file).exists():
                continue
            
            parser = MarkdownParser(doc_file)
            doc_endpoints = parser.extract_api_descriptions()
            
            # Check for documented endpoints that don't exist in code
            for doc_endpoint in doc_endpoints:
                method = doc_endpoint['method']
                path = doc_endpoint['path']
                
                if (method, path) not in code_endpoint_set:
                    issue = DocumentationIssue(
                        issue_type='doc_code_mismatch',
                        severity='warning',
                        file=doc_file,
                        description=f"Documentation describes {method} {path} but endpoint not found in {code_file}",
                        suggestion=f"Remove documentation for {method} {path} or implement the endpoint in code"
                    )
                    issues.append(issue)
        
        return issues
    
    def detect_missing_docs_for_new_features(self, code_file: str) -> List[DocumentationIssue]:
        """
        Detect new features in code that lack documentation.
        
        This checks if:
        - New public functions are added without docs
        - New models are added without schema documentation
        - New endpoints are added without API docs
        
        Args:
            code_file: Path to the code file
            
        Returns:
            List of documentation issues for missing feature docs
        """
        issues = []
        
        # Check if code file has corresponding documentation
        doc_status = self.analyzer.check_code_file_documented(code_file)
        
        if not doc_status['has_docs']:
            # Check if this is a public API file that should have docs
            if code_file.startswith('backend/handlers/'):
                issue = DocumentationIssue(
                    issue_type='missing_docs',
                    severity='error',
                    file=code_file,
                    description=f"Handler file {code_file} has no corresponding documentation",
                    suggestion=f"Create API documentation for endpoints in {code_file}"
                )
                issues.append(issue)
        
        # Check for new endpoints without documentation
        api_issues = self.detect_api_changes_requiring_docs(code_file)
        issues.extend(api_issues)
        
        return issues
    
    def detect_outdated_docs_for_removed_features(self, code_file: str) -> List[DocumentationIssue]:
        """
        Detect documentation for features that have been removed from code.
        
        This checks if:
        - Documentation describes endpoints that no longer exist
        - Documentation references removed functions
        - Documentation describes removed models
        
        Args:
            code_file: Path to the code file
            
        Returns:
            List of documentation issues for outdated docs
        """
        issues = []
        
        # Get documentation files for this code file
        doc_files = self.mapper.map_code_to_docs(code_file)
        
        if not doc_files:
            return issues
        
        # Extract endpoints from code
        code_endpoints = self.analyzer.extract_endpoints_from_code(code_file)
        code_endpoint_set = {(ep['method'], ep['path']) for ep in code_endpoints}
        
        # If spec is available, check against spec too
        if self.spec_parser:
            spec_endpoints = self.spec_parser.get_endpoints()
            spec_endpoint_set = {(ep['method'], ep['path']) for ep in spec_endpoints}
        else:
            spec_endpoint_set = set()
        
        # Check each doc file for outdated content
        for doc_file in doc_files:
            if not Path(doc_file).exists():
                continue
            
            parser = MarkdownParser(doc_file)
            doc_endpoints = parser.extract_api_descriptions()
            
            # Check for documented endpoints that don't exist in code or spec
            for doc_endpoint in doc_endpoints:
                method = doc_endpoint['method']
                path = doc_endpoint['path']
                
                in_code = (method, path) in code_endpoint_set
                in_spec = (method, path) in spec_endpoint_set if spec_endpoint_set else True
                
                if not in_code and not in_spec:
                    issue = DocumentationIssue(
                        issue_type='outdated_docs',
                        severity='warning',
                        file=doc_file,
                        description=f"Documentation describes {method} {path} but endpoint no longer exists in code or spec",
                        suggestion=f"Remove documentation for {method} {path} from {doc_file}"
                    )
                    issues.append(issue)
        
        return issues
    
    def generate_documentation_report(self, code_files: List[str]) -> DocumentationReport:
        """
        Generate a comprehensive documentation alignment report.
        
        Args:
            code_files: List of code files to check
            
        Returns:
            DocumentationReport with all detected issues
        """
        report = DocumentationReport()
        
        # Track summary statistics
        files_checked = 0
        files_with_issues = 0
        
        for code_file in code_files:
            files_checked += 1
            file_issues = []
            
            # Detect all types of documentation issues
            api_changes = self.detect_api_changes_requiring_docs(code_file)
            mismatches = self.detect_doc_code_mismatches(code_file)
            missing_docs = self.detect_missing_docs_for_new_features(code_file)
            outdated_docs = self.detect_outdated_docs_for_removed_features(code_file)
            
            # Combine all issues
            file_issues.extend(api_changes)
            file_issues.extend(mismatches)
            file_issues.extend(missing_docs)
            file_issues.extend(outdated_docs)
            
            # Deduplicate issues
            seen = set()
            for issue in file_issues:
                issue_key = (issue.type, issue.file, issue.description)
                if issue_key not in seen:
                    seen.add(issue_key)
                    report.add_issue(issue)
            
            if file_issues:
                files_with_issues += 1
        
        # Set summary
        report.summary = {
            'files_checked': files_checked,
            'files_with_issues': files_with_issues,
            'total_issues': len(report.issues)
        }
        
        return report
    
    def validate_staged_changes(self, staged_files: List[str]) -> DocumentationReport:
        """
        Validate documentation alignment for staged changes.
        
        This is the main entry point for commit-time documentation validation.
        
        Args:
            staged_files: List of staged file paths
            
        Returns:
            DocumentationReport with validation results
        """
        # Filter to only Python files in backend that might have public APIs
        code_files = [
            f for f in staged_files 
            if f.endswith('.py') and f.startswith('backend/') and not 'test' in f
        ]
        
        if not code_files:
            report = DocumentationReport()
            report.summary = {
                'files_checked': 0,
                'files_with_issues': 0,
                'total_issues': 0,
                'message': 'No backend code files to validate for documentation'
            }
            return report
        
        # Generate comprehensive report
        report = self.generate_documentation_report(code_files)
        
        # Add message to summary
        if report.has_issues():
            report.summary['message'] = f"Documentation issues found in {report.summary['files_with_issues']} of {report.summary['files_checked']} files"
        else:
            report.summary['message'] = f"All {report.summary['files_checked']} files have aligned documentation"
        
        return report
