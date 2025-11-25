"""
Unit tests for the documentation analyzer module.
"""
import pytest
from pathlib import Path
from backend.doc_analyzer import (
    MarkdownParser,
    DocumentationMapper,
    DocumentationAnalyzer,
    DocumentationAlignmentDetector,
    DocumentationIssue,
    DocumentationReport
)


class TestMarkdownParser:
    """Tests for MarkdownParser class."""
    
    def test_parse_existing_file(self):
        """Test parsing an existing markdown file."""
        parser = MarkdownParser("docs/api/users.md")
        content = parser.parse()
        
        assert content is not None
        assert len(content) > 0
        assert "User Endpoints" in content or "GET /users" in content
    
    def test_parse_nonexistent_file(self):
        """Test parsing a non-existent file raises FileNotFoundError."""
        parser = MarkdownParser("docs/nonexistent.md")
        
        with pytest.raises(FileNotFoundError):
            parser.parse()
    
    def test_extract_api_descriptions(self):
        """Test extracting API endpoint descriptions from documentation."""
        parser = MarkdownParser("docs/api/users.md")
        endpoints = parser.extract_api_descriptions()
        
        assert len(endpoints) > 0
        
        # Check that we found the GET /users endpoint
        get_users = [ep for ep in endpoints if ep['method'] == 'GET' and ep['path'] == '/users']
        assert len(get_users) > 0
        
        # Check that endpoint has required fields
        endpoint = get_users[0]
        assert 'method' in endpoint
        assert 'path' in endpoint
        assert 'description' in endpoint
    
    def test_get_sections(self):
        """Test extracting sections from markdown."""
        parser = MarkdownParser("docs/api/users.md")
        sections = parser.get_sections()
        
        assert isinstance(sections, dict)
        assert len(sections) > 0
    
    def test_contains_text(self):
        """Test checking if documentation contains specific text."""
        parser = MarkdownParser("docs/api/users.md")
        
        # Case insensitive search
        assert parser.contains_text("users")
        assert parser.contains_text("USERS")
        
        # Case sensitive search
        assert parser.contains_text("users", case_sensitive=True)
        assert not parser.contains_text("NONEXISTENT", case_sensitive=True)
    
    def test_extract_code_references(self):
        """Test extracting code references from documentation."""
        parser = MarkdownParser("docs/api/users.md")
        references = parser.extract_code_references()
        
        assert isinstance(references, list)
        # Should find endpoint references like "GET /users"
        assert any("GET" in ref or "users" in ref for ref in references)


class TestDocumentationMapper:
    """Tests for DocumentationMapper class."""
    
    def test_map_handler_to_docs(self):
        """Test mapping handler files to API documentation."""
        mapper = DocumentationMapper(".")
        
        # Map user handler to docs
        doc_files = mapper.map_code_to_docs("backend/handlers/user.py")
        
        # Should map to users.md (pluralized)
        assert any("users.md" in f for f in doc_files)
    
    def test_map_health_handler_to_docs(self):
        """Test mapping health handler to documentation."""
        mapper = DocumentationMapper(".")
        
        doc_files = mapper.map_code_to_docs("backend/handlers/health.py")
        
        # Should map to health.md (not pluralized)
        assert any("health.md" in f for f in doc_files)
    
    def test_map_main_to_docs(self):
        """Test mapping main.py to architecture docs."""
        mapper = DocumentationMapper(".")
        
        doc_files = mapper.map_code_to_docs("backend/main.py")
        
        # Should map to architecture.md
        assert any("architecture.md" in f for f in doc_files)
    
    def test_map_models_to_docs(self):
        """Test mapping models.py to API docs."""
        mapper = DocumentationMapper(".")
        
        doc_files = mapper.map_code_to_docs("backend/models.py")
        
        # Should map to multiple API docs
        assert len(doc_files) > 0
        assert all(f.endswith(".md") for f in doc_files)
    
    def test_map_endpoint_to_docs(self):
        """Test mapping an endpoint to its documentation."""
        mapper = DocumentationMapper(".")
        
        doc_files = mapper.map_endpoint_to_docs("GET", "/users")
        
        # Should find users.md
        assert any("users.md" in f for f in doc_files)
    
    def test_find_all_doc_files(self):
        """Test finding all documentation files."""
        mapper = DocumentationMapper(".")
        
        doc_files = mapper.find_all_doc_files()
        
        assert len(doc_files) > 0
        assert all(f.endswith(".md") for f in doc_files)
        assert any("users.md" in f for f in doc_files)
    
    def test_get_public_api_files(self):
        """Test getting public API documentation files."""
        mapper = DocumentationMapper(".")
        
        api_files = mapper.get_public_api_files()
        
        assert len(api_files) > 0
        # Use Path to handle both Windows and Unix path separators
        assert all(Path("docs/api") in Path(f).parents or Path(f).parent.name == "api" for f in api_files)


class TestDocumentationAnalyzer:
    """Tests for DocumentationAnalyzer class."""
    
    def test_analyze_doc_file(self):
        """Test analyzing a documentation file."""
        analyzer = DocumentationAnalyzer(".", ".kiro/specs/app.yaml")
        
        result = analyzer.analyze_doc_file("docs/api/users.md")
        
        assert 'file' in result
        assert 'sections' in result
        assert 'api_endpoints' in result
        assert 'code_references' in result
        assert len(result['api_endpoints']) > 0
    
    def test_check_endpoint_documented(self):
        """Test checking if an endpoint is documented."""
        analyzer = DocumentationAnalyzer(".", ".kiro/specs/app.yaml")
        
        # Check existing endpoint
        result = analyzer.check_endpoint_documented("GET", "/users")
        assert result['documented'] is True
        assert 'file' in result
        
        # Check non-existent endpoint
        result = analyzer.check_endpoint_documented("POST", "/nonexistent")
        assert result['documented'] is False
    
    def test_check_code_file_documented(self):
        """Test checking if a code file has documentation."""
        analyzer = DocumentationAnalyzer(".", ".kiro/specs/app.yaml")
        
        # Check handler file
        result = analyzer.check_code_file_documented("backend/handlers/user.py")
        assert result['has_docs'] is True
        assert len(result['doc_files']) > 0
    
    def test_extract_endpoints_from_code(self):
        """Test extracting endpoints from code file."""
        analyzer = DocumentationAnalyzer(".", ".kiro/specs/app.yaml")
        
        endpoints = analyzer.extract_endpoints_from_code("backend/handlers/user.py")
        
        assert len(endpoints) > 0
        assert all('method' in ep and 'path' in ep for ep in endpoints)


class TestDocumentationIssue:
    """Tests for DocumentationIssue class."""
    
    def test_create_issue(self):
        """Test creating a documentation issue."""
        issue = DocumentationIssue(
            issue_type='missing_docs',
            severity='error',
            file='backend/handlers/user.py',
            description='Missing documentation',
            suggestion='Add documentation'
        )
        
        assert issue.type == 'missing_docs'
        assert issue.severity == 'error'
        assert issue.file == 'backend/handlers/user.py'
    
    def test_issue_to_dict(self):
        """Test converting issue to dictionary."""
        issue = DocumentationIssue(
            issue_type='missing_docs',
            severity='error',
            file='backend/handlers/user.py',
            description='Missing documentation',
            suggestion='Add documentation'
        )
        
        result = issue.to_dict()
        
        assert isinstance(result, dict)
        assert result['type'] == 'missing_docs'
        assert result['severity'] == 'error'
        assert result['file'] == 'backend/handlers/user.py'


class TestDocumentationReport:
    """Tests for DocumentationReport class."""
    
    def test_empty_report(self):
        """Test creating an empty report."""
        report = DocumentationReport()
        
        assert not report.has_issues()
        assert len(report.issues) == 0
    
    def test_add_issue(self):
        """Test adding issues to report."""
        report = DocumentationReport()
        
        issue = DocumentationIssue(
            issue_type='missing_docs',
            severity='error',
            file='test.py',
            description='Test',
            suggestion='Fix it'
        )
        
        report.add_issue(issue)
        
        assert report.has_issues()
        assert len(report.issues) == 1
    
    def test_report_to_dict(self):
        """Test converting report to dictionary."""
        report = DocumentationReport()
        report.summary = {'test': 'value'}
        
        result = report.to_dict()
        
        assert isinstance(result, dict)
        assert 'has_issues' in result
        assert 'issues' in result
        assert 'summary' in result


class TestDocumentationAlignmentDetector:
    """Tests for DocumentationAlignmentDetector class."""
    
    def test_detect_api_changes_requiring_docs(self):
        """Test detecting API changes that need documentation."""
        detector = DocumentationAlignmentDetector(".", ".kiro/specs/app.yaml")
        
        # Test with user handler (should have docs)
        issues = detector.detect_api_changes_requiring_docs("backend/handlers/user.py")
        
        # Should not have issues since endpoints are documented
        assert isinstance(issues, list)
    
    def test_detect_doc_code_mismatches(self):
        """Test detecting mismatches between docs and code."""
        detector = DocumentationAlignmentDetector(".", ".kiro/specs/app.yaml")
        
        issues = detector.detect_doc_code_mismatches("backend/handlers/user.py")
        
        assert isinstance(issues, list)
    
    def test_detect_missing_docs_for_new_features(self):
        """Test detecting missing docs for new features."""
        detector = DocumentationAlignmentDetector(".", ".kiro/specs/app.yaml")
        
        issues = detector.detect_missing_docs_for_new_features("backend/handlers/user.py")
        
        assert isinstance(issues, list)
    
    def test_detect_outdated_docs_for_removed_features(self):
        """Test detecting outdated docs for removed features."""
        detector = DocumentationAlignmentDetector(".", ".kiro/specs/app.yaml")
        
        issues = detector.detect_outdated_docs_for_removed_features("backend/handlers/user.py")
        
        assert isinstance(issues, list)
    
    def test_generate_documentation_report(self):
        """Test generating a comprehensive documentation report."""
        detector = DocumentationAlignmentDetector(".", ".kiro/specs/app.yaml")
        
        code_files = ["backend/handlers/user.py", "backend/handlers/health.py"]
        report = detector.generate_documentation_report(code_files)
        
        assert isinstance(report, DocumentationReport)
        assert 'files_checked' in report.summary
        assert report.summary['files_checked'] == 2
    
    def test_validate_staged_changes(self):
        """Test validating staged changes for documentation."""
        detector = DocumentationAlignmentDetector(".", ".kiro/specs/app.yaml")
        
        staged_files = [
            "backend/handlers/user.py",
            "backend/handlers/health.py",
            "tests/unit/test_user.py"  # Should be filtered out
        ]
        
        report = detector.validate_staged_changes(staged_files)
        
        assert isinstance(report, DocumentationReport)
        assert 'message' in report.summary
        assert report.summary['files_checked'] == 2  # Only backend files
    
    def test_validate_staged_changes_no_code_files(self):
        """Test validating staged changes with no code files."""
        detector = DocumentationAlignmentDetector(".", ".kiro/specs/app.yaml")
        
        staged_files = ["README.md", "docs/index.md"]
        
        report = detector.validate_staged_changes(staged_files)
        
        assert isinstance(report, DocumentationReport)
        assert not report.has_issues()
        assert report.summary['files_checked'] == 0
