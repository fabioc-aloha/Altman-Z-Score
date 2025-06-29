# Complete Flow Analysis: prompt_fin_analysis.md Usage

## EXECUTION FLOW

### 1. MAIN PIPELINE ENTRY
**File:** `altman_zscore/main_pipeline.py:254`
```python
comprehensive_ai_analysis = await self.ai_orchestrator.perform_comprehensive_analysis(
    financial_data_for_ai,
    include_data_quality=True,
    include_peer_analysis=True,
    include_sentiment=True,
    include_risk_analysis=True,
    generate_final_commentary=True  # <-- This triggers the prompt usage
)
```

### 2. AI ORCHESTRATOR PROCESSING
**File:** `altman_zscore/layers/ai_analysis/ai_orchestrator.py:177`
```python
# Generate LLM final commentary
if generate_final_commentary:
    analysis_results.llm_final_commentary = await self._generate_final_commentary(analysis_results, financial_data)
```

### 3. PROMPT LOADING AND EXECUTION
**File:** `altman_zscore/layers/ai_analysis/ai_orchestrator.py:318`
```python
async def _generate_final_commentary(self, analysis: ComprehensiveAIAnalysis, 
                                   financial_data: MergedFinancialData) -> Optional[str]:
    try:
        # Load the comprehensive financial analysis prompt
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "prompt_fin_analysis.md"
        
        if not prompt_path.exists():
            logger.warning(f"Financial analysis prompt not found at {prompt_path}")
            return self._generate_fallback_commentary(analysis)
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            base_prompt = f.read()  # <-- LOADS THE ENTIRE prompt_fin_analysis.md
        
        # Prepare comprehensive analysis data for injection
        analysis_data = self._prepare_data_injection_for_prompt(analysis, financial_data)
        
        # Combine the prompt with the data injection
        full_prompt = f"""
{base_prompt}

## INJECTED DATA FOR ANALYSIS

{analysis_data}

---

## ANALYSIS EXECUTION

Based on the comprehensive data injection above, provide a complete AI-Powered Altman Z-Score Investment Analysis following the 10-section structure outlined in the prompt. Focus on synthesizing insights across all data sources for actionable investment intelligence.
"""
        
        # Format prompt as messages for chat completion
        messages = [
            {"role": "user", "content": full_prompt}
        ]
        
        commentary = await asyncio.to_thread(
            self.llm_client.chat_completion,  # <-- SENDS TO LLM
            analysis.ticker,
            messages,
            "comprehensive_financial_analysis"
        )
        return commentary.strip()
```

### 4. RESULT USAGE IN MAIN PIPELINE
**File:** `altman_zscore/main_pipeline.py:397-399`
```python
# Use comprehensive analysis if available, otherwise fall back to original method
if comprehensive_ai_analysis and comprehensive_ai_analysis.llm_final_commentary:
    logger.info(f"Using comprehensive AI analysis final commentary for {latest_result.ticker}")
    insights = comprehensive_ai_analysis.llm_final_commentary  # <-- FINAL REPORT CONTENT
```

### 5. REPORT GENERATION
**File:** `altman_zscore/layers/output_generation/report_generator.py` (inferred)
The `insights` variable containing the LLM-generated report using `prompt_fin_analysis.md` is then written to:
- HTML dashboards
- Text reports
- JSON outputs

## KEY POINTS

1. **Single Source of Truth**: `prompt_fin_analysis.md` is the ONLY prompt used for comprehensive final reports
2. **Complete Data Injection**: All AI analysis results + financial data are injected into the prompt
3. **10-Section Structure**: The prompt enforces the exact 10-section report structure
4. **Conditional Usage**: Only used when `generate_final_commentary=True` in the pipeline
5. **Fallback Protection**: If prompt file is missing, falls back to basic commentary

## VERIFICATION COMMANDS

To verify this flow is active:
```bash
# Check if prompt file exists
ls -la altman_zscore/prompts/prompt_fin_analysis.md

# Test the complete flow
python main.py AAPL --enhanced-analysis

# Check log output for confirmation
grep "comprehensive AI analysis final commentary" logs/altman_zscore.log
```

## DATA FLOW SUMMARY

```
User Request → Main Pipeline → AI Orchestrator → Prompt Loader → LLM Client → Final Report
     ↓              ↓              ↓              ↓              ↓           ↓
   AAPL    financial_data    analysis_data    prompt_fin_   Azure OpenAI   10-section
           + ai_analysis     + full_prompt    analysis.md   + full_prompt   report
```
