"""
Report Generator for Meeting Minutes

Creates professional, formatted meeting minutes from processed data.
Supports multiple output formats and customizable templates.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    include_timestamps: bool = True
    include_speaker_attribution: bool = True
    include_confidence_scores: bool = False
    group_action_items_by_owner: bool = True
    priority_order: List[str] = None
    
    def __post_init__(self):
        if self.priority_order is None:
            self.priority_order = ["high", "medium", "low"]


class MeetingMinutesReportGenerator:
    """
    Generates formatted meeting minutes reports from processed data.
    
    Takes summarized data and creates professional documents suitable for:
    - Distribution to attendees
    - Executive summaries
    - Action item tracking
    - Meeting archives
    """
    
    def __init__(self, config: ReportConfig = None):
        self.config = config or ReportConfig()
        self.templates = self._load_templates()
    
    def generate_report(self, meeting_summary, format_type: str = "markdown") -> str:
        """
        Generate complete meeting minutes report.
        
        Args:
            meeting_summary: MeetingSummary object from summarizer
            format_type: Output format ("markdown", "text", "html")
            
        Returns:
            Formatted report as string
        """
        if format_type == "markdown":
            return self._generate_markdown_report(meeting_summary)
        elif format_type == "text":
            return self._generate_text_report(meeting_summary)
        elif format_type == "html":
            return self._generate_html_report(meeting_summary)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _generate_markdown_report(self, summary) -> str:
        """Generate markdown-formatted report."""
        report_lines = []
        
        # Header
        report_lines.extend(self._generate_header_markdown(summary))
        
        # Executive Summary
        report_lines.extend(self._generate_summary_section_markdown(summary))
        
        # Attendees
        report_lines.extend(self._generate_attendees_section_markdown(summary))
        
        # Key Decisions
        report_lines.extend(self._generate_decisions_section_markdown(summary))
        
        # Action Items
        report_lines.extend(self._generate_action_items_section_markdown(summary))
        
        # Discussion Topics
        report_lines.extend(self._generate_topics_section_markdown(summary))
        
        # Footer
        report_lines.extend(self._generate_footer_markdown())
        
        return "\n".join(report_lines)
    
    def _generate_text_report(self, summary) -> str:
        """Generate plain text report."""
        report_lines = []
        
        # Header
        report_lines.append("=" * 60)
        report_lines.append("MEETING MINUTES")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Executive Summary
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 20)
        report_lines.append(summary.overall_summary)
        report_lines.append("")
        
        # Attendees
        if summary.attendees:
            report_lines.append("ATTENDEES")
            report_lines.append("-" * 20)
            for attendee in summary.attendees:
                report_lines.append(f"• {attendee}")
            report_lines.append("")
        
        # Key Decisions
        if summary.key_decisions:
            report_lines.append("KEY DECISIONS")
            report_lines.append("-" * 20)
            for i, decision in enumerate(summary.key_decisions, 1):
                report_lines.append(f"{i}. {decision}")
            report_lines.append("")
        
        # Action Items
        if summary.action_items:
            report_lines.append("ACTION ITEMS")
            report_lines.append("-" * 20)
            
            if self.config.group_action_items_by_owner:
                grouped_actions = self._group_actions_by_owner(summary.action_items)
                for owner, actions in grouped_actions.items():
                    report_lines.append(f"\n{owner}:")
                    for action in actions:
                        deadline_str = f" (Due: {action['deadline']})" if action['deadline'] != 'TBD' else ""
                        priority_str = f" [{action.get('priority', 'medium').upper()}]" if action.get('priority') != 'medium' else ""
                        report_lines.append(f"  • {action['task']}{deadline_str}{priority_str}")
            else:
                for i, action in enumerate(summary.action_items, 1):
                    owner_str = f" - {action['owner']}" if action['owner'] != 'TBD' else ""
                    deadline_str = f" (Due: {action['deadline']})" if action['deadline'] != 'TBD' else ""
                    report_lines.append(f"{i}. {action['task']}{owner_str}{deadline_str}")
            report_lines.append("")
        
        # Topics Discussed
        if summary.main_topics:
            report_lines.append("TOPICS DISCUSSED")
            report_lines.append("-" * 20)
            for topic in summary.main_topics:
                report_lines.append(f"• {topic}")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        report_lines.append("End of Meeting Minutes")
        
        return "\n".join(report_lines)
    
    def _generate_header_markdown(self, summary) -> List[str]:
        """Generate markdown header section."""
        lines = [
            "# Meeting Minutes",
            "",
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "",
            "---",
            ""
        ]
        return lines
    
    def _generate_summary_section_markdown(self, summary) -> List[str]:
        """Generate executive summary section."""
        lines = [
            "## Executive Summary",
            "",
            summary.overall_summary,
            "",
        ]
        return lines
    
    def _generate_attendees_section_markdown(self, summary) -> List[str]:
        """Generate attendees section."""
        if not summary.attendees:
            return []
        
        lines = [
            "## Attendees",
            "",
        ]
        
        for attendee in summary.attendees:
            lines.append(f"- {attendee}")
        
        lines.append("")
        return lines
    
    def _generate_decisions_section_markdown(self, summary) -> List[str]:
        """Generate key decisions section."""
        if not summary.key_decisions:
            return []
        
        lines = [
            "## Key Decisions",
            "",
        ]
        
        for i, decision in enumerate(summary.key_decisions, 1):
            lines.append(f"{i}. {decision}")
        
        lines.append("")
        return lines
    
    def _generate_action_items_section_markdown(self, summary) -> List[str]:
        """Generate action items section."""
        if not summary.action_items:
            return []
        
        lines = [
            "## Action Items",
            "",
        ]
        
        if self.config.group_action_items_by_owner:
            grouped_actions = self._group_actions_by_owner(summary.action_items)
            
            for owner, actions in grouped_actions.items():
                lines.append(f"### {owner}")
                lines.append("")
                
                # Sort by priority
                actions_by_priority = self._sort_actions_by_priority(actions)
                
                for action in actions_by_priority:
                    deadline_str = f" **Due:** {action['deadline']}" if action['deadline'] != 'TBD' else ""
                    priority_str = f" `{action.get('priority', 'medium').upper()}`" if action.get('priority') != 'medium' else ""
                    lines.append(f"- {action['task']}{deadline_str}{priority_str}")
                
                lines.append("")
        else:
            # Simple list format
            sorted_actions = self._sort_actions_by_priority(summary.action_items)
            
            for i, action in enumerate(sorted_actions, 1):
                owner_str = f" - **Owner:** {action['owner']}" if action['owner'] != 'TBD' else ""
                deadline_str = f" - **Due:** {action['deadline']}" if action['deadline'] != 'TBD' else ""
                priority_str = f" - **Priority:** {action.get('priority', 'medium').title()}" if action.get('priority') != 'medium' else ""
                
                lines.append(f"{i}. {action['task']}")
                if owner_str or deadline_str or priority_str:
                    details = [s for s in [owner_str, deadline_str, priority_str] if s]
                    lines.append(f"   {' '.join(details)}")
                lines.append("")
        
        return lines
    
    def _generate_topics_section_markdown(self, summary) -> List[str]:
        """Generate discussion topics section."""
        if not summary.main_topics:
            return []
        
        lines = [
            "## Topics Discussed",
            "",
        ]
        
        for topic in summary.main_topics:
            lines.append(f"- {topic}")
        
        lines.append("")
        return lines
    
    def _generate_footer_markdown(self) -> List[str]:
        """Generate footer section."""
        lines = [
            "---",
            "",
            f"*Meeting minutes generated by AI Assistant on {datetime.now().strftime('%Y-%m-%d')}*"
        ]
        return lines
    
    def _generate_html_report(self, summary) -> str:
        """Generate HTML report (basic implementation)."""
        # Convert markdown to basic HTML
        markdown_report = self._generate_markdown_report(summary)
        
        # Simple markdown to HTML conversion
        html_lines = ["<html><head><title>Meeting Minutes</title></head><body>"]
        
        for line in markdown_report.split('\n'):
            if line.startswith('# '):
                html_lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith('## '):
                html_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith('### '):
                html_lines.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith('- '):
                html_lines.append(f"<li>{line[2:]}</li>")
            elif line.strip() == "---":
                html_lines.append("<hr>")
            elif line.strip():
                html_lines.append(f"<p>{line}</p>")
            else:
                html_lines.append("<br>")
        
        html_lines.append("</body></html>")
        return "\n".join(html_lines)
    
    def _group_actions_by_owner(self, action_items: List[Dict]) -> Dict[str, List[Dict]]:
        """Group action items by owner."""
        grouped = {}
        
        for action in action_items:
            owner = action.get('owner', 'TBD')
            if owner not in grouped:
                grouped[owner] = []
            grouped[owner].append(action)
        
        return grouped
    
    def _sort_actions_by_priority(self, actions: List[Dict]) -> List[Dict]:
        """Sort actions by priority."""
        priority_order = {p: i for i, p in enumerate(self.config.priority_order)}
        
        return sorted(actions, key=lambda x: priority_order.get(x.get('priority', 'medium'), 999))
    
    def _load_templates(self) -> Dict[str, str]:
        """Load report templates (placeholder for future template system)."""
        return {
            "default": "Standard meeting minutes template",
            "executive": "Executive summary focused template",
            "action_focused": "Action item focused template"
        }
    
    def export_to_file(self, report_content: str, filename: str, format_type: str = "markdown"):
        """Export report to file."""
        file_extensions = {
            "markdown": ".md",
            "text": ".txt",
            "html": ".html"
        }
        
        extension = file_extensions.get(format_type, ".txt")
        full_filename = f"{filename}{extension}"
        
        with open(full_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return full_filename


# Example usage
if __name__ == "__main__":
    # Mock meeting summary for testing
    from types import SimpleNamespace
    
    mock_summary = SimpleNamespace(
        overall_summary="Team discussed Q4 planning and resource allocation. Key decisions made regarding budget and timeline.",
        attendees=["John Smith", "Sarah Johnson", "Mike Davis"],
        key_decisions=["Increase marketing budget by 20%", "Launch new feature in Q1 2024"],
        action_items=[
            {"task": "Prepare budget proposal", "owner": "Sarah Johnson", "deadline": "Friday", "priority": "high"},
            {"task": "Schedule QA review", "owner": "Mike Davis", "deadline": "Next week", "priority": "medium"},
            {"task": "Update project timeline", "owner": "John Smith", "deadline": "TBD", "priority": "low"}
        ],
        main_topics=["Budget Planning", "Product Development", "QA Process"]
    )
    
    config = ReportConfig(group_action_items_by_owner=True)
    generator = MeetingMinutesReportGenerator(config)
    
    # Generate markdown report
    markdown_report = generator.generate_report(mock_summary, "markdown")
    print("Markdown Report:")
    print(markdown_report[:500] + "...")
    
    # Generate text report
    text_report = generator.generate_report(mock_summary, "text")
    print("\nText Report:")
    print(text_report[:500] + "...")