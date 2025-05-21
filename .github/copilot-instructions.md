# GitHub Copilot Instructions

This file contains algorithmic instructions for GitHub Copilot to follow when working with this codebase.

## Action Priority

1. **Before Making Any Changes**
   - Check `DECISIONS.md` for architectural decisions
   - Review `LEARNINGS.md` for past solutions and issues
   - Validate against TODO.md for current priorities
   - Ensure GitHub Codespaces compatibility

2. **After Making Changes**
   - Update TODO.md with completed items (change `[ ]` to `[x]`)
   - Document significant learnings in `LEARNINGS.md`
   - Record any architectural decisions in `DECISIONS.md`
   - Validate Codespaces compatibility

## Project Context

This is an Altman Z-Score analysis tool for analyzing financial health of companies, particularly focused on AI and tech companies. The tool fetches financial data from SEC EDGAR and market data from Yahoo Finance.

## Development Workflow

1. **Initial Assessment**
   - Review todo.md for context and priorities
   - Check if task affects architectural decisions
   - Review relevant sections in `LEARNINGS.md`

2. **Implementation Process**
   - Follow code style and standards below
   - Use appropriate project conventions
   - Implement with Codespaces compatibility
   - Document as you go

3. **Post-Implementation**
   - Update todo.md status
   - Document learnings
   - Validate against standards
   - Test in Codespaces

4. **Documentation Updates**
   - Update `LEARNINGS.md` for:
     * Major breakthroughs
     * Implementation insights
     * Optimization techniques
     * Failure scenarios and solutions
   - Update todo.md status
   - Never modify `PAPER.md` without user consent

## Implementation Guidelines

1. **Code Structure**
   - Use src/altman_zscore/ for source code
   - Keep tests in tests/ directory
   - Store configuration in config.py
   - Place documentation in docs/
   
2. **Code Style**
   - Follow PEP 8 guidelines
   - Use type hints consistently
   - Implement error handling
   - Write clear docstrings

3. **Type System**
   - Use type hints for all functions
   - Prefer concrete types over Any
   - Use typing module collections
   - Validate type consistency

4. **Error Management**
   - Use specific exception types
   - Implement structured logging
   - Add retries for API calls
   - Include context in errors

5. **Configuration**
   - Use config.py for constants
   - Use env vars for secrets
   - Document all parameters
   - Validate all inputs

## Domain-Specific Requirements

1. **Financial Processing**
   - Validate all metrics before use
   - Use Decimal for currency values
   - Implement ratio sanity checks
   - Support trend analysis
   - Enable multi-period analysis
   - Add visualization support

2. **Data Pipeline**
   - Validate all input data
   - Use pandas for analysis
   - Enable parallel processing
   - Implement proper caching
   - Handle API rate limits
   - Add robust error recovery

3. **API Integration**
   - Use proper authentication
   - Respect rate limitations
   - Cache API responses
   - Implement async calls
   - Handle timeouts gracefully

4. **Output Generation**
   - Use structured logging
   - Format numbers precisely
   - Include proper dates
   - Generate clear reports
   - Support multiple formats

## Architectural and Strategic Guidelines

1. **Decision Management**
   - Must consult `DECISIONS.md` before proposing or making any architectural or strategic changes
   - Do not suggest changes that contradict `DECISIONS.md` unless explicitly instructed by a human contributor
   - Treat `DECISIONS.md` as the authoritative record of architectural decisions
   - Do not make changes to `PAPER.md` without explicit user consent

2. **Development Environment**
   - Ensure all code is compatible with GitHub Codespaces
   - Test functionality in Codespaces environment when possible
   - Consider container-based development workflows

## Knowledge Management and Learning

1. **Documentation Requirements**
   - Record all significant implementation learnings in `LEARNINGS.md`
   - Document optimizations and their rationale
   - Record encountered failures and solutions
   - Use `LEARNINGS.md` as reference to inform future decisions

2. **Continuous Documentation**
   - Automatically record major breakthroughs in `LEARNINGS.md`
   - Document key implementation ideas
   - Record tool development and refinement insights
   - Capture significant optimizations
   - Document failure scenarios and resolutions

3. **Knowledge Application**
   - Reference `LEARNINGS.md` when making suggestions
   - Avoid repeating previously documented issues
   - Build upon existing documented solutions
   - Use past learnings to inform new implementations

## Documentation Requirements

1. **Code Documentation**
   - Include docstrings for all public functions and classes
   - Document parameters and return values
   - Include examples in docstrings where helpful

2. **Comments**
   - Explain complex financial calculations
   - Document assumptions and limitations
   - Include references to financial formulas or methodologies

## Testing Guidelines

1. **Test Coverage**
   - Include unit tests for all calculations
   - Mock external API calls in tests
   - Include validation tests for financial metrics
   - Test edge cases and boundary conditions

## Security Considerations

1. **Data Security**
   - Use proper authentication for APIs
   - Don't commit sensitive credentials
   - Validate and sanitize all inputs

## Performance Guidelines

1. **Optimization**
   - Use caching where appropriate
   - Implement parallel processing for batch operations
   - Consider memory usage with large datasets

## Dependencies

1. **Package Management**
   - Keep dependencies in pyproject.toml/requirements.txt
   - Specify version constraints
   - Document purpose of each dependency

## File Organization

1. **Project Structure**
   - Keep source code in src/altman_zscore/
   - Tests in tests/ directory
   - Configuration in config.py
   - Documentation in docs/

## Best Practices

1. **Code Generation**
   - Prefer class-based structure over functions
   - Use type hints consistently
   - Include proper error handling
   - Follow PEP 8 style guidelines

2. **Financial Analysis**
   - Validate all financial metrics
   - Include trend analysis capabilities
   - Support multiple time periods
   - Include visualization options
