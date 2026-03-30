import os
import sys
from datetime import datetime
from typing import Dict, List, Optional


class DocumentationSpecialist:
    """
    Documentation Specialist Agent - responsible for generating logs and reports from local files
    """

    def __init__(self):
        self.logs_dir = "logs"
        self.reports_dir = "reports"

        # Create directories if they don't exist
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

    def log_action(self, action: str, details: str = ""):
        """Log an action with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {action}: {details}\n"

        log_file = os.path.join(self.logs_dir, f"log_{datetime.now().strftime('%Y%m%d')}.txt")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        print(f"LOGGED: {action}")

    def generate_daily_report(self, summary: str, source_file: str, action_items: List[str] = None, brainstorm_ideas: List[str] = None) -> str:
        """Generate a daily report from the summary, action items, and brainstorming ideas"""
        report_date = datetime.now().strftime("%Y-%m-%d")
        report_filename = f"daily_report_{report_date}.md"
        report_path = os.path.join(self.reports_dir, report_filename)

        # Format action items section
        action_items_section = ""
        if action_items:
            action_items_section = "\n## Action Items / Next Steps\n"
            for i, item in enumerate(action_items, 1):
                action_items_section += f"{i}. {item}\n"

        # Format brainstorming ideas section (Silver Tier)
        brainstorm_section = ""
        if brainstorm_ideas:
            brainstorm_section = "\n## Brainstorming Ideas\n"
            brainstorm_section += "*Creative suggestions and improvements not in the original document:*\n\n"
            for i, idea in enumerate(brainstorm_ideas, 1):
                brainstorm_section += f"{i}. {idea}\n"

        report_content = f"""# Daily Report
Date: {report_date}

## Source File
{source_file}

## Summary
{summary}
{action_items_section}{brainstorm_section}
## Generated
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        self.log_action("REPORT_GENERATED", f"Created {report_path}")
        return report_path


class TaskManager:
    """
    Task Manager Agent - coordinates basic task automation workflows
    """

    def __init__(self, documentation_specialist: DocumentationSpecialist):
        self.doc_specialist = documentation_specialist

    def process_file(self, filepath: str) -> Optional[tuple[str, List[str], List[str]]]:
        """Process a file by reading and summarizing it, plus identifying action items and brainstorming ideas"""
        if not os.path.exists(filepath):
            self.doc_specialist.log_action("ERROR", f"File not found: {filepath}")
            return None

        try:
            self.doc_specialist.log_action("FILE_READ_STARTED", filepath)

            # Read the file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            self.doc_specialist.log_action("FILE_READ_COMPLETED", f"Read {len(content)} characters from {filepath}")

            # Summarize the content
            summary = self.summarize_text(content)

            # Identify action items
            action_items = self.identify_action_items(content)

            # Silver Tier: Generate brainstorming ideas
            brainstorm_ideas = self.brainstorm_ideas(content, summary)

            self.doc_specialist.log_action("SUMMARY_COMPLETED", f"Summary created for {filepath}")
            self.doc_specialist.log_action("ACTION_ITEMS_IDENTIFIED", f"Found {len(action_items)} action items in {filepath}")
            self.doc_specialist.log_action("BRAINSTORM_COMPLETED", f"Generated {len(brainstorm_ideas)} creative ideas for {filepath}")

            return summary, action_items, brainstorm_ideas

        except Exception as e:
            self.doc_specialist.log_action("ERROR", f"Failed to process {filepath}: {str(e)}")
            return None

    def summarize_text(self, text: str) -> str:
        """Create a summary of the provided text"""
        # Simple summarization logic for Bronze Tier
        lines = text.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]

        if len(non_empty_lines) == 0:
            return "No content to summarize."

        # Take the first few lines as a summary
        summary_lines = []

        # Add first line if it looks like a title or heading
        if len(non_empty_lines) > 0 and len(non_empty_lines[0]) < 100:
            summary_lines.append(f"Title: {non_empty_lines[0]}")

        # Add first 3-5 significant sentences/paragraphs
        content_count = 0
        for line in non_empty_lines:
            if content_count >= 5:  # Limit to 5 content lines
                break
            if len(line) > 20:  # Skip very short lines
                summary_lines.append(f"- {line[:200]}{'...' if len(line) > 200 else ''}")
                content_count += 1

        if not summary_lines:
            summary_lines.append(text[:500] + ('...' if len(text) > 500 else ''))

        return '\n'.join(summary_lines)

    def identify_action_items(self, text: str) -> List[str]:
        """Identify potential action items or next steps from the text"""
        lines = text.split('\n')
        action_items = []

        # Keywords that often indicate action items or next steps
        action_keywords = [
            'need', 'should', 'must', 'will', 'plan', 'implement', 'create', 'develop',
            'update', 'modify', 'add', 'remove', 'change', 'improve', 'enhance',
            'consider', 'ensure', 'complete', 'finish', 'start', 'begin', 'continue',
            'next step', 'action item', 'todo', 'to-do', 'task', 'assign'
        ]

        # Look for lines that contain action keywords
        for line in lines:
            line_lower = line.lower().strip()

            # Skip headings and titles (usually all caps or start with #)
            if line.startswith('#') or line.isupper():
                continue

            # Check if line contains action keywords and is substantial
            if len(line) > 10 and any(keyword in line_lower for keyword in action_keywords):
                # Clean up the line and add as action item if not already in the list
                cleaned_item = line.strip().rstrip('.!')
                if cleaned_item and cleaned_item not in action_items:
                    action_items.append(cleaned_item)

                    # Stop after collecting 3 action items
                    if len(action_items) >= 3:
                        break

        # If we don't have enough action items, look for lines that start with common task indicators
        if len(action_items) < 3:
            for line in lines:
                line_clean = line.strip()

                # Skip headings
                if line.startswith('#') or not line_clean or len(line_clean) <= 10:
                    continue

                # Look for task-like patterns (e.g., lines starting with action verbs)
                if (line_clean.lower().startswith(('add', 'update', 'create', 'implement', 'develop', 'design', 'build', 'fix', 'resolve'))
                    and line_clean not in action_items):
                    action_items.append(line_clean)

                    if len(action_items) >= 3:
                        break

        # If still don't have 3 items, add some important content lines
        if len(action_items) < 3:
            for line in lines:
                line_clean = line.strip()
                if (line_clean and len(line_clean) > 20 and
                    not line_clean.startswith('#') and
                    line_clean not in action_items):
                    action_items.append(line_clean)
                    if len(action_items) >= 3:
                        break

        return action_items[:3]  # Return maximum 3 action items

    def brainstorm_ideas(self, text: str, summary: str) -> List[str]:
        """Generate 2-3 creative ideas or improvements based on the content (Silver Tier feature)"""
        ideas = []

        # Analyze the content to understand its context
        text_lower = text.lower()
        lines = text.split('\n')

        # Detect content type and themes
        is_marketing = any(word in text_lower for word in ['marketing', 'campaign', 'customer', 'engagement', 'roi', 'social media'])
        is_technical = any(word in text_lower for word in ['code', 'function', 'api', 'database', 'implementation', 'system', 'architecture'])
        is_project = any(word in text_lower for word in ['project', 'team', 'deadline', 'milestone', 'task', 'goal'])
        is_report = any(word in text_lower for word in ['report', 'analysis', 'results', 'findings', 'data', 'metrics'])

        # Generate context-specific creative ideas
        if is_marketing:
            marketing_ideas = [
                "Consider implementing A/B testing for campaign elements to optimize conversion rates",
                "Explore partnerships with micro-influencers for more authentic audience engagement",
                "Develop an interactive content strategy (quizzes, polls, calculators) to boost user participation",
                "Create a customer loyalty program with gamification elements to increase retention",
                "Leverage user-generated content campaigns to build community and reduce content creation costs"
            ]
            ideas.extend(marketing_ideas[:2])

        if is_technical:
            technical_ideas = [
                "Implement automated testing and CI/CD pipeline to improve code quality and deployment speed",
                "Consider microservices architecture to improve scalability and maintainability",
                "Add comprehensive logging and monitoring with dashboards for better system observability",
                "Explore caching strategies (Redis, CDN) to optimize performance and reduce server load",
                "Implement API rate limiting and authentication to enhance security"
            ]
            ideas.extend(technical_ideas[:2])

        if is_project:
            project_ideas = [
                "Introduce daily stand-ups or async check-ins to improve team communication and identify blockers early",
                "Create a project dashboard with real-time metrics to increase transparency and accountability",
                "Implement retrospectives after each milestone to capture lessons learned and improve processes",
                "Use time-boxing techniques (Pomodoro, sprints) to improve focus and productivity",
                "Establish a knowledge base or wiki to document decisions and reduce onboarding time"
            ]
            ideas.extend(project_ideas[:2])

        if is_report:
            report_ideas = [
                "Create interactive visualizations or infographics to make data more accessible and engaging",
                "Develop predictive models based on historical data to forecast future trends",
                "Implement automated report generation to save time and ensure consistency",
                "Add comparative analysis with industry benchmarks to provide better context",
                "Create executive summary versions for different stakeholder audiences"
            ]
            ideas.extend(report_ideas[:2])

        # If no specific context detected, provide general improvement ideas
        if len(ideas) == 0:
            general_ideas = [
                "Automate repetitive tasks to free up time for higher-value activities",
                "Implement a feedback loop mechanism to continuously improve based on user input",
                "Create documentation or knowledge sharing sessions to improve team alignment",
                "Explore integration opportunities with existing tools to streamline workflows",
                "Develop metrics and KPIs to measure success and track progress over time"
            ]
            ideas.extend(general_ideas[:3])

        # Ensure we return exactly 2-3 ideas
        return ideas[:3]


class GeneralAgent:
    """
    General Agent implementing the Gold Tier Personal AI Employee with Project-Wide Synthesis
    """

    def __init__(self):
        self.documentation_specialist = DocumentationSpecialist()
        self.task_manager = TaskManager(self.documentation_specialist)

    def process_document(self, filepath: str) -> bool:
        """Main workflow: read file, summarize, identify action items, brainstorm ideas, and save report"""
        print(f"Starting document processing for: {filepath}")

        # Log the start of the process
        self.documentation_specialist.log_action("PROCESS_STARTED", f"Processing {filepath}")

        # Process the file and get summary, action items, and brainstorm ideas
        result = self.task_manager.process_file(filepath)

        if result is None:
            print(f"Failed to process {filepath}")
            return False

        summary, action_items, brainstorm_ideas = result

        # Have the Documentation Specialist save the report with all sections
        report_path = self.documentation_specialist.generate_daily_report(summary, filepath, action_items, brainstorm_ideas)

        print(f"Processing complete. Summary saved to: {report_path}")
        self.documentation_specialist.log_action("PROCESS_COMPLETED", f"Summary saved to {report_path}")

        return True

    def generate_master_strategy_report(self) -> str:
        """Gold Tier: Scan entire directory for .md and .txt files and generate Master Strategy Report"""
        print("Starting Project-Wide Synthesis...")

        self.documentation_specialist.log_action("SYNTHESIS_STARTED", "Scanning directory for .md and .txt files")

        # Scan for all .md and .txt files
        all_files = []
        for root, dirs, files in os.walk('.'):
            # Skip hidden directories and common non-relevant folders
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]

            for file in files:
                if file.endswith('.md') or file.endswith('.txt'):
                    filepath = os.path.join(root, file)
                    all_files.append(filepath)

        if not all_files:
            print("No .md or .txt files found in directory")
            return None

        print(f"Found {len(all_files)} files to analyze")
        self.documentation_specialist.log_action("FILES_DISCOVERED", f"Found {len(all_files)} files for synthesis")

        # Analyze each file
        file_analyses = []
        for filepath in all_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Get basic analysis
                analysis = {
                    'filepath': filepath,
                    'size': len(content),
                    'lines': len(content.split('\n')),
                    'type': self._classify_document_type(filepath, content),
                    'key_topics': self._extract_key_topics(content),
                    'summary': self.task_manager.summarize_text(content)
                }
                file_analyses.append(analysis)

            except Exception as e:
                print(f"Warning: Could not read {filepath}: {str(e)}")
                continue

        # Generate connections and gaps
        connections = self._identify_connections(file_analyses)
        gaps = self._identify_gaps(file_analyses)

        # Create Master Strategy Report
        report_path = self._create_master_report(file_analyses, connections, gaps)

        print(f"Master Strategy Report generated: {report_path}")
        self.documentation_specialist.log_action("SYNTHESIS_COMPLETED", f"Master report saved to {report_path}")

        return report_path

    def _classify_document_type(self, filepath: str, content: str) -> str:
        """Classify the type of document based on filename and content"""
        filepath_lower = filepath.lower()
        content_lower = content.lower()

        # Check filename patterns
        if 'requirement' in filepath_lower or 'req' in filepath_lower:
            return 'Requirements'
        elif 'report' in filepath_lower:
            return 'Report'
        elif 'log' in filepath_lower:
            return 'Log'
        elif 'readme' in filepath_lower:
            return 'Documentation'
        elif 'agent' in filepath_lower:
            return 'Agent Definition'

        # Check content patterns
        if any(word in content_lower for word in ['requirement', 'must', 'should', 'shall']):
            return 'Requirements'
        elif any(word in content_lower for word in ['summary', 'report', 'findings', 'results']):
            return 'Report'
        elif any(word in content_lower for word in ['error', 'warning', 'info', 'debug']):
            return 'Log'
        elif any(word in content_lower for word in ['campaign', 'marketing', 'strategy']):
            return 'Campaign Analysis'

        return 'General Document'

    def _extract_key_topics(self, content: str) -> List[str]:
        """Extract key topics/themes from content"""
        topics = []
        content_lower = content.lower()

        # Define topic keywords
        topic_map = {
            'AI/Agents': ['agent', 'ai', 'claude', 'automation', 'llm'],
            'Documentation': ['documentation', 'report', 'summary', 'log'],
            'Requirements': ['requirement', 'feature', 'functionality', 'tier'],
            'Business': ['business', 'revenue', 'client', 'payment', 'invoice'],
            'Technical': ['code', 'implementation', 'api', 'system', 'architecture'],
            'Marketing': ['marketing', 'campaign', 'social media', 'engagement'],
            'Project Management': ['task', 'project', 'milestone', 'deadline', 'goal']
        }

        for topic, keywords in topic_map.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)

        return topics if topics else ['General']

    def _identify_connections(self, file_analyses: List[Dict]) -> List[Dict]:
        """Identify connections between different files"""
        connections = []

        # Group files by type
        type_groups = {}
        for analysis in file_analyses:
            doc_type = analysis['type']
            if doc_type not in type_groups:
                type_groups[doc_type] = []
            type_groups[doc_type].append(analysis)

        # Find topic overlaps
        for i, analysis1 in enumerate(file_analyses):
            for analysis2 in file_analyses[i+1:]:
                common_topics = set(analysis1['key_topics']) & set(analysis2['key_topics'])
                if common_topics:
                    connections.append({
                        'file1': analysis1['filepath'],
                        'file2': analysis2['filepath'],
                        'type1': analysis1['type'],
                        'type2': analysis2['type'],
                        'common_topics': list(common_topics),
                        'relationship': self._describe_relationship(analysis1['type'], analysis2['type'])
                    })

        return connections

    def _describe_relationship(self, type1: str, type2: str) -> str:
        """Describe the relationship between two document types"""
        relationships = {
            ('Requirements', 'Report'): 'Reports track implementation of requirements',
            ('Requirements', 'Log'): 'Logs show execution of required features',
            ('Campaign Analysis', 'Report'): 'Reports measure campaign effectiveness',
            ('Agent Definition', 'Requirements'): 'Agents implement required functionality',
            ('Documentation', 'Requirements'): 'Documentation explains required features'
        }

        key = (type1, type2) if (type1, type2) in relationships else (type2, type1)
        return relationships.get(key, 'Related documents with shared topics')

    def _identify_gaps(self, file_analyses: List[Dict]) -> List[str]:
        """Identify missing information or gaps between files"""
        gaps = []

        # Check for document type coverage
        doc_types = set(analysis['type'] for analysis in file_analyses)

        if 'Requirements' in doc_types and 'Report' not in doc_types:
            gaps.append("Missing progress reports to track requirement implementation")

        if 'Campaign Analysis' in doc_types and 'Report' not in doc_types:
            gaps.append("Missing performance reports for campaign analysis")

        if 'Requirements' in doc_types and 'Agent Definition' not in doc_types:
            gaps.append("Missing agent definitions to implement requirements")

        # Check for topic coverage
        all_topics = set()
        for analysis in file_analyses:
            all_topics.update(analysis['key_topics'])

        if 'Requirements' in all_topics and 'Technical' not in all_topics:
            gaps.append("Requirements exist but technical implementation details are missing")

        if 'Business' in all_topics and 'Marketing' not in all_topics:
            gaps.append("Business goals present but marketing strategy is not documented")

        # Check for temporal gaps (logs vs reports)
        has_logs = any(analysis['type'] == 'Log' for analysis in file_analyses)
        has_reports = any(analysis['type'] == 'Report' for analysis in file_analyses)

        if has_logs and not has_reports:
            gaps.append("Activity logs exist but no summary reports have been generated")

        if not gaps:
            gaps.append("No significant gaps detected - documentation appears comprehensive")

        return gaps

    def _create_master_report(self, file_analyses: List[Dict], connections: List[Dict], gaps: List[str]) -> str:
        """Create the Master Strategy Report"""
        report_date = datetime.now().strftime("%Y-%m-%d")
        report_filename = f"master_strategy_report_{report_date}.md"
        report_path = os.path.join(self.documentation_specialist.reports_dir, report_filename)

        # Build file inventory section
        inventory_section = "\n## File Inventory\n\n"
        inventory_section += "| File | Type | Size | Key Topics |\n"
        inventory_section += "|------|------|------|------------|\n"
        for analysis in file_analyses:
            topics_str = ", ".join(analysis['key_topics'])
            inventory_section += f"| {analysis['filepath']} | {analysis['type']} | {analysis['lines']} lines | {topics_str} |\n"

        # Build connections section
        connections_section = "\n## Document Connections\n\n"
        if connections:
            connections_section += "*How different files relate to each other:*\n\n"
            for i, conn in enumerate(connections, 1):
                connections_section += f"{i}. **{os.path.basename(conn['file1'])}** ↔ **{os.path.basename(conn['file2'])}**\n"
                connections_section += f"   - Common topics: {', '.join(conn['common_topics'])}\n"
                connections_section += f"   - Relationship: {conn['relationship']}\n\n"
        else:
            connections_section += "*No significant connections detected between files.*\n\n"

        # Build gaps section
        gaps_section = "\n## Identified Gaps\n\n"
        gaps_section += "*Missing information or areas needing attention:*\n\n"
        for i, gap in enumerate(gaps, 1):
            gaps_section += f"{i}. {gap}\n"

        # Build document summaries section
        summaries_section = "\n## Document Summaries\n\n"
        for analysis in file_analyses:
            summaries_section += f"### {os.path.basename(analysis['filepath'])} ({analysis['type']})\n\n"
            summaries_section += f"{analysis['summary']}\n\n"

        # Build recommendations section
        recommendations_section = "\n## Strategic Recommendations\n\n"
        recommendations = self._generate_recommendations(file_analyses, gaps)
        for i, rec in enumerate(recommendations, 1):
            recommendations_section += f"{i}. {rec}\n"

        # Assemble full report
        report_content = f"""# Master Strategy Report
Date: {report_date}

## Executive Summary

This report provides a comprehensive analysis of {len(file_analyses)} documents across the project directory. It identifies connections between files, highlights gaps in documentation, and provides strategic recommendations.

**Document Types Found:** {', '.join(set(a['type'] for a in file_analyses))}

**Key Topics Covered:** {', '.join(set(topic for a in file_analyses for topic in a['key_topics']))}

{inventory_section}
{connections_section}
{gaps_section}
{summaries_section}
{recommendations_section}

## Generated
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Generated by: Gold Tier GeneralAgent with Project-Wide Synthesis
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return report_path

    def _generate_recommendations(self, file_analyses: List[Dict], gaps: List[str]) -> List[str]:
        """Generate strategic recommendations based on analysis"""
        recommendations = []

        # Analyze document types present
        doc_types = set(analysis['type'] for analysis in file_analyses)

        if 'Requirements' in doc_types:
            recommendations.append("Create regular progress reports to track requirement implementation status")

        if 'Log' in doc_types and 'Report' not in doc_types:
            recommendations.append("Generate summary reports from log files to identify trends and issues")

        if 'Campaign Analysis' in doc_types:
            recommendations.append("Develop KPI tracking reports to measure campaign effectiveness over time")

        if len(gaps) > 2:
            recommendations.append("Prioritize filling documentation gaps to ensure comprehensive project coverage")

        # Check for agent-related content
        has_agent_content = any('AI/Agents' in analysis['key_topics'] for analysis in file_analyses)
        if has_agent_content:
            recommendations.append("Consider implementing automated reporting agents to maintain documentation consistency")

        if not recommendations:
            recommendations.append("Continue maintaining current documentation practices")

        return recommendations


def main():
    """Main entry point for the application"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file_path>")
        print("       python main.py --synthesis")
        print("\nThis script implements the Gold Tier Personal AI Employee.")
        print("It reads a text file, summarizes it using the Task Manager,")
        print("identifies action items, generates creative brainstorming ideas,")
        print("and saves everything as a daily report using the Documentation Specialist.")
        print("\nGold Tier Feature:")
        print("  --synthesis: Generate Master Strategy Report by scanning all .md and .txt files")
        return

    # Initialize the General Agent
    agent = GeneralAgent()

    # Check if synthesis mode is requested
    if sys.argv[1] == "--synthesis":
        print("=" * 60)
        print("GOLD TIER: PROJECT-WIDE SYNTHESIS")
        print("=" * 60)
        report_path = agent.generate_master_strategy_report()
        if report_path:
            print("\n" + "=" * 60)
            print("Master Strategy Report generated successfully!")
            print(f"Report location: {report_path}")
            print("=" * 60)
        else:
            print("\nMaster Strategy Report generation failed!")
        return

    # Standard document processing mode
    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        return

    # Process the document
    success = agent.process_document(input_file)

    if success:
        print("\nDocument processed successfully!")
    else:
        print("\nDocument processing failed!")


if __name__ == "__main__":
    main()