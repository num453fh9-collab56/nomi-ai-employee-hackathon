# AI Agents Structure

## Bronze Tier Agents

### Task Manager
- **Role**: Coordinates basic task automation workflows
- **Responsibilities**:
  - Manages task scheduling and execution
  - Orchestrates communication between different components
  - Handles task prioritization and delegation
- **Capabilities**:
  - Process local files for task automation
  - Coordinate with Documentation Specialist agent
  - Execute basic text summarization tasks
- **Constraints**: No external API calls, lightweight operation only

### Documentation Specialist
- **Role**: Handles all logging and documentation tasks
- **Responsibilities**:
  - Generate daily reports from local files
  - Maintain execution logs
  - Create summary documentation
- **Capabilities**:
  - Text summarization from local sources
  - Report generation in Markdown format
  - Log organization and maintenance
- **Constraints**: Limited to local file processing, no external connectivity