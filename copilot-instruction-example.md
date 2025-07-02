# Project Development Guidelines Template

IMPORTANT: Update .github\copilot-instructions.md with what we learn in terms of environment, architecture, and development practices. This file serves as the primary source of truth for all development directives.
- To err once is human, to err twice is a mistake, to err three times is AI not learning from its mistakes.

## Development Directives

**Environment & Tools:**
- Define your primary shell environment (e.g., PowerShell, Bash)
- Always use shell-compatible commands and syntax for your environment

**Code Quality Principles:**
- Generate code that follows DRY (Don't Repeat Yourself) and KISS (Keep It Simple, Stupid) principles
- Be careful when inserting or making changes around docstrings - preserve existing documentation
- Do not introduce regressions - maintain backward compatibility
- Ensure all changes maintain existing functionality
- Separate concerns appropriately (e.g., separate HTML/CSS from Python code)
- Establish and follow consistent naming conventions throughout the codebase

**Terminal & Command Guidelines:**
- Do not use escape characters in terminal commands unless necessary
- When running commands in terminal, wait for user to share the output before proceeding with the next command
- Use shell-native commands where possible
- Consider terminal encoding limitations when generating output (e.g., Unicode vs ASCII)
- Use consistent status indicators in script outputs (e.g., "[OK]", "[X]", "PASSED", "FAILED")

**Documentation & Reporting:**
- Define a standard location for documentation files (e.g., `docs/` directory)
- Reference key documentation files before making architectural decisions
- Update relevant documentation when making significant changes

## Key Project Documentation

The following key documents should be created and maintained for your project:

- **FLOW.md** - Complete technical flow and architecture documentation
- **README.md** - Project overview and getting started guide
- **API.md** - API integration documentation 
- **MODELS.md** - Data models and methodology documentation
- **TODO.md** - Current development tasks and priorities
- **CHANGELOG.md** - Version history and release notes

These documents provide comprehensive understanding of the system architecture, data sources, and implementation details.

**Temporal Organization**: 
- Architecture documentation represents the **present** - current system state
- Tasks list represents the **future** - planned development and enhancements
- Changelog represents the **past** - completed work and version history

**Architecture & Data Flow Knowledge:**
- Document primary and secondary data sources
- Define data validation frameworks and methodologies
- Document caching strategies for external data sources
- Define fallback mechanisms for data retrieval

**Naming Conventions:**
- Establish consistent spelling conventions (e.g., American or British English)
- Define case conventions for different code elements:
  - Variable naming conventions (e.g., camelCase, snake_case)
  - Class naming conventions (e.g., PascalCase)
- Maintain consistent naming across all files and modules
- Define any project-specific terminology guidelines

## AI Learnings from its Mistakes

This section should be populated as the project evolves with specific guidelines derived from past errors or suboptimal implementations.

- @unicode Rule - Use ASCII Output Formats: Always use ASCII alternatives for status indicators (like "[OK]", "[X]", "PASSED", "FAILED") instead of Unicode characters in script outputs when working in environments with limited encoding support.

- @centralization Rule - Centralize Related Files: Always centralize related scripts, documentation, and data files in a logical directory structure. For example, all validation assets should be in a dedicated directory with appropriate subdirectories for scripts/, docs/, and data/.

- @fallback Rule - Implement Data Source Fallbacks: When handling data that may be unavailable from the primary source, implement appropriate fallback data sources with clear integration paths.

- @caching Rule - Implement Cache Management: Always include cache clearing functionality in long-running scripts that rely on cached data, particularly for external APIs. Ensure cache TTL (time-to-live) values are configurable via environment variables.

- @documentation Rule - Maintain Documentation Versions: When updating critical documentation that serves as an intellectual contribution, create versioned copies (v1, v2, etc.) rather than overwriting the original.

- @redirection Rule - Create Redirection Files: When moving or centralizing files, create simple redirection files in the original locations to guide users to the new locations. Include clear instructions on where to find the updated files.

---

**Note**: This is a template file. When implementing for a specific project, replace the generic guidance with project-specific details, particularly in the Key Project Documentation, Architecture & Data Flow Knowledge, and Naming Conventions sections.
