"""
Auto-remediation module for SpecSync.
Automatically creates tasks to fix detected drift.
"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class RemediationTask:
    """Represents a task to fix drift."""
    
    def __init__(self, task_type: str, description: str, file: str, details: str, priority: int = 5):
        self.task_type = task_type  # 'spec', 'test', 'doc', 'code'
        self.description = description
        self.file = file
        self.details = details
        self.priority = priority
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'type': self.task_type,
            'description': self.description,
            'file': self.file,
            'details': self.details,
            'priority': self.priority,
            'created_at': self.created_at
        }


class AutoRemediationEngine:
    """Generates remediation tasks from validation results."""
    
    def __init__(self, feature_name: str = "app"):
        self.feature_name = feature_name
        self.tasks_file = Path(f".kiro/specs/{feature_name}/remediation-tasks.md")
    
    def generate_tasks_from_validation(self, validation_result: Dict[str, Any]) -> List[RemediationTask]:
        """Generate remediation tasks from validation results."""
        tasks = []
        
        # Extract reports
        drift_report = validation_result.get('drift_report')
        test_report = validation_result.get('test_report')
        doc_report = validation_result.get('doc_report')
        
        # Generate tasks from drift issues
        if drift_report:
            tasks.extend(self._generate_drift_tasks(drift_report))
        
        # Generate tasks from test coverage issues
        if test_report:
            tasks.extend(self._generate_test_tasks(test_report))
        
        # Generate tasks from documentation issues
        if doc_report:
            tasks.extend(self._generate_doc_tasks(doc_report))
        
        return tasks
    
    def _generate_drift_tasks(self, drift_report: Dict[str, Any]) -> List[RemediationTask]:
        """Generate tasks from drift issues."""
        tasks = []
        
        aligned = drift_report.get('aligned', True)
        if aligned:
            return tasks
        
        issues = drift_report.get('issues', [])
        
        for issue in issues:
            if isinstance(issue, dict):
                issue_type = issue.get('type', 'unknown')
                file = issue.get('file', 'unknown')
                description = issue.get('description', '')
                
                if 'new_endpoint' in issue_type or 'new_function' in issue_type:
                    task = RemediationTask(
                        task_type='spec',
                        description=f"Add missing endpoint/function to spec",
                        file='.kiro/specs/app.yaml',
                        details=f"Add definition for {description} found in {file}",
                        priority=9
                    )
                    tasks.append(task)
                
                elif 'removed' in issue_type:
                    task = RemediationTask(
                        task_type='spec',
                        description=f"Remove deleted functionality from spec",
                        file='.kiro/specs/app.yaml',
                        details=f"Remove definition for {description}",
                        priority=8
                    )
                    tasks.append(task)
        
        return tasks
    
    def _generate_test_tasks(self, test_report: Dict[str, Any]) -> List[RemediationTask]:
        """Generate tasks from test coverage issues."""
        tasks = []
        
        has_issues = test_report.get('has_issues', False)
        if not has_issues:
            return tasks
        
        issues = test_report.get('issues', [])
        
        for issue in issues:
            if isinstance(issue, dict):
                issue_type = issue.get('type', 'unknown')
                description = issue.get('description', '')
                file = issue.get('file', '')
                
                if 'missing_tests' in issue_type:
                    # Extract the code file from description
                    code_file = description.split('for ')[-1] if 'for ' in description else file
                    test_file = code_file.replace('backend/', 'tests/unit/test_').replace('.py', '.py')
                    
                    task = RemediationTask(
                        task_type='test',
                        description=f"Create tests for {code_file}",
                        file=test_file,
                        details=f"Add unit tests covering all functions in {code_file}",
                        priority=7
                    )
                    tasks.append(task)
                
                elif 'insufficient_coverage' in issue_type:
                    task = RemediationTask(
                        task_type='test',
                        description=f"Improve test coverage",
                        file=file,
                        details=description,
                        priority=6
                    )
                    tasks.append(task)
        
        return tasks
    
    def _generate_doc_tasks(self, doc_report: Dict[str, Any]) -> List[RemediationTask]:
        """Generate tasks from documentation issues."""
        tasks = []
        
        has_issues = doc_report.get('has_issues', False)
        if not has_issues:
            return tasks
        
        issues = doc_report.get('issues', [])
        
        for issue in issues:
            if isinstance(issue, dict):
                issue_type = issue.get('type', 'unknown')
                description = issue.get('description', '')
                file = issue.get('file', 'docs/api/')
                
                if 'missing_docs' in issue_type:
                    task = RemediationTask(
                        task_type='doc',
                        description=f"Document new API endpoint",
                        file=file if file else 'docs/api/users.md',
                        details=description,
                        priority=5
                    )
                    tasks.append(task)
                
                elif 'outdated' in issue_type:
                    task = RemediationTask(
                        task_type='doc',
                        description=f"Update outdated documentation",
                        file=file,
                        details=description,
                        priority=6
                    )
                    tasks.append(task)
        
        return tasks
    
    def write_tasks_to_file(self, tasks: List[RemediationTask]) -> str:
        """Write remediation tasks to a markdown file."""
        if not tasks:
            return "No remediation tasks needed."
        
        # Ensure directory exists
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Sort tasks by priority (highest first)
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)
        
        # Generate markdown content
        content = f"""# Remediation Tasks

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Feature:** {self.feature_name}  
**Total Tasks:** {len(tasks)}

These tasks were automatically generated by SpecSync to fix detected drift.

---

## Tasks by Priority

"""
        
        # Group by type
        by_type = {}
        for task in sorted_tasks:
            if task.task_type not in by_type:
                by_type[task.task_type] = []
            by_type[task.task_type].append(task)
        
        # Write tasks by type
        type_names = {
            'spec': '📋 Specification Updates',
            'test': '🧪 Test Coverage',
            'doc': '📚 Documentation',
            'code': '💻 Code Fixes'
        }
        
        for task_type in ['spec', 'test', 'doc', 'code']:
            if task_type in by_type:
                content += f"\n### {type_names.get(task_type, task_type.title())}\n\n"
                
                for i, task in enumerate(by_type[task_type], 1):
                    content += f"- [ ] **{task.description}**\n"
                    content += f"  - **File:** `{task.file}`\n"
                    content += f"  - **Priority:** {task.priority}/10\n"
                    content += f"  - **Details:** {task.details}\n"
                    content += f"  - **Created:** {task.created_at}\n"
                    content += "\n"
        
        content += """
---

## How to Use These Tasks

1. **Review each task** - Understand what needs to be fixed
2. **Implement the changes** - Update specs, add tests, write docs
3. **Check off completed tasks** - Mark with `[x]` when done
4. **Re-run validation** - Verify all drift is resolved
5. **Commit together** - Stage all changes and commit

---

## Auto-Generated by SpecSync

This file was automatically created by SpecSync's auto-remediation engine.
You can edit or delete tasks as needed.
"""
        
        # Write to file
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(self.tasks_file)
    
    def create_remediation_tasks(self, validation_result: Dict[str, Any]) -> str:
        """Main entry point: generate and write remediation tasks."""
        tasks = self.generate_tasks_from_validation(validation_result)
        
        if not tasks:
            return "✅ No remediation tasks needed - all validations passed!"
        
        file_path = self.write_tasks_to_file(tasks)
        
        return f"""
🔧 Auto-Remediation Tasks Generated!

📁 Tasks file created: {file_path}
📊 Total tasks: {len(tasks)}

Task breakdown:
  - Spec updates: {len([t for t in tasks if t.task_type == 'spec'])}
  - Test additions: {len([t for t in tasks if t.task_type == 'test'])}
  - Documentation: {len([t for t in tasks if t.task_type == 'doc'])}
  - Code fixes: {len([t for t in tasks if t.task_type == 'code'])}

Open the tasks file to see detailed remediation steps!
"""


def enable_auto_remediation(validation_result: Dict[str, Any], feature_name: str = "app") -> str:
    """
    Enable auto-remediation mode.
    Generates tasks file instead of just blocking commit.
    """
    engine = AutoRemediationEngine(feature_name)
    return engine.create_remediation_tasks(validation_result)
