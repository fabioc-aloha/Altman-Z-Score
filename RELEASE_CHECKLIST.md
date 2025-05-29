# V2.2 Release Checklist

## Before Creating the Release
- [x] Update README.md to reflect Version 2.2 features
- [x] Update PLAN.md to mark features as completed
- [x] Update TODO.md with completed and pending items
- [x] Update outdated test scripts to work with the current codebase structure
- [x] Add new test script for visualization enhancements
- [ ] Run all tests to verify functionality

## Tests to Run
- [x] Monthly price statistics
- [x] Data validation
- [x] Main pipeline for MSFT
- [x] Plot visualizations with I-shaped whiskers

## Final Steps
1. Commit all changes:
   ```
   git add .
   git commit -m "V2.2: Updated tests and pre-release preparations"
   ```

2. Merge the branch to main:
   ```
   git checkout main
   git merge v2.2-dev
   ```

3. Create a git tag for the release:
   ```
   git tag -a v2.2.0 -m "V2.2.0: Model Selection & Calibration Overhaul with Enhanced Visualizations"
   ```

4. Push the changes and tag:
   ```
   git push origin main
   git push origin v2.2.0
   ```

5. Create GitHub Release:
   - Title: V2.2.0: Model Selection & Calibration Overhaul with Enhanced Visualizations
   - Description:

```markdown
# Altman Z-Score V2.2.0

This release includes model selection & calibration overhaul and enhanced visualizations.

## Major Features
- **Model Selection & Calibration:** 
  - Centralized all model coefficients, thresholds, and metadata in `constants.py`
  - Model selection logic using age, IPO, industry (SIC), public/private status, and region
  - Support for industry-specific and emerging market models and thresholds
  - Transparent reporting of model/threshold overrides

- **Enhanced Visualizations:** 
  - Improved Z-Score and price plotting with better label positioning
  - Implemented I-shaped whiskers with horizontal caps for price range indicators
  - Optimized y-axis scaling to prevent overlapping between Z-Score and price data
  - Enhanced color scheme with darker gray for price axis and better readability

- **Documentation:**
  - Updated README.md with "Output Examples" section
  - Added example output reports for demonstration purposes

## Coming in V2.2.x
- Warnings for size/leverage outliers in the report
- Expanded unit/integration tests for new model selection logic
- Integration of additional industry benchmark data
- Documentation and automation of calibration update process
```

6. Attach any relevant assets to the release (example reports, screenshots)
