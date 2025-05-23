# LEARNINGS.md

This file is for documenting key technical and project learnings during the 2025+ refactor of the Altman Z-Score project.

- Capture lessons from new library integrations, API quirks, and data validation challenges.
- Summarize what worked, what didn’t, and why decisions were made.
- Use this as a living document to inform future contributors and avoid repeating past mistakes.
- When fetching market cap or price data for a specific date, always check if the date is a weekend, holiday, or non-trading day. Fallback to the most recent previous trading day and warn the user. This is now implemented in YahooFinanceClient and should be standard for all future data fetchers. Consider using a trading calendar for even more robust handling.

---
For architectural decisions, see `DECISIONS.md`. For the old codebase’s learnings, see `OLD/LEARNINGS.md`.
