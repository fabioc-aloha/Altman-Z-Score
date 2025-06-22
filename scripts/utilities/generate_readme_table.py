import os
import json
import re
import sys

# Add project root to Python path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

OUTPUT_DIR = "output"
LOGO_SUFFIX = "_logo.png"
REPORT_PREFIX = "zscore_"
REPORT_SUFFIX = "_zscore_full_report.md"
CHART_SUFFIX = "_trend.png"
COMPANY_INFO = "company_info.json"


def get_company_name(info_path):
    try:
        with open(info_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Try both 'name' and fallback to uppercase ticker if not present
            return data.get("name") or os.path.basename(os.path.dirname(info_path))
    except Exception:
        return os.path.basename(os.path.dirname(info_path))
        return os.path.basename(os.path.dirname(info_path))
        return os.path.basename(os.path.dirname(info_path))


def extract_investor_advice_detailed(report_path):
    """Extract detailed investor recommendations by profile from the report, including CEO and CFO recommendations."""
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
          # First, extract CEO and CFO recommendations from Internal Stakeholder Recommendations table
        ceo_recommendation = extract_ceo_recommendation(content)
        cfo_recommendation = extract_cfo_recommendation(content)
        
        # Look for the investor recommendation table
        table_pattern = r'\|\s*Investment Profile\s*\|\s*Risk Tolerance\s*\|\s*Recommendation\s*\|.*?\n(.*?)(?=\n\s*>|\n\s*###|\n\s*---|\Z)'
        table_match = re.search(table_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if table_match:
            table_content = table_match.group(1)
            recommendations = {}
            
            # Parse each table row
            lines = table_content.strip().split('\n')
            for line in lines:
                if '|' in line and 'Investment Profile' not in line and '---' not in line:
                    parts = [part.strip() for part in line.split('|') if part.strip()]
                    if len(parts) >= 3:
                        profile = parts[0]
                        recommendation = parts[2]
                        
                        # Map profile names to cleaner versions
                        profile_map = {
                            'Short-Seller (Bearish)': 'Short-Seller',
                            'Dividend Income': 'Dividend',
                            'Capital Appreciation': 'Growth',
                            'Aggressive Growth': 'Aggressive',
                            'Capital Preservation': 'Conservative',
                            'Value Investor': 'Value'
                        }
                        
                        # Find matching profile
                        clean_profile = None
                        for full_name, clean_name in profile_map.items():
                            if full_name.lower() in profile.lower():
                                clean_profile = clean_name
                                break
                        
                        if clean_profile and recommendation:
                            # Extract just the recommendation (BUY, SELL, HOLD)
                            rec_clean = recommendation.upper()
                            if 'BUY' in rec_clean:
                                icon = '📈'
                                action = 'BUY'
                            elif 'SELL' in rec_clean:
                                icon = '📉'
                                action = 'SELL'
                            elif 'HOLD' in rec_clean:
                                icon = '⚖️'
                                action = 'HOLD'
                            else:
                                icon = '❓'
                                action = '?'
                            
                            recommendations[clean_profile] = f"{icon} {action}"
            
            if recommendations:                # Create multi-line representation starting with CEO and CFO recommendations
                result_parts = []
                
                # Add CEO recommendation first if available
                if ceo_recommendation:
                    result_parts.append(f"<sub><b>CEO:</b> {ceo_recommendation}</sub>")
                
                # Add CFO recommendation second if available
                if cfo_recommendation:
                    result_parts.append(f"<sub><b>CFO:</b> {cfo_recommendation}</sub>")
                
                # Add investor profiles
                profile_order = ['Conservative', 'Dividend', 'Value', 'Growth', 'Aggressive', 'Short-Seller']
                for profile in profile_order:
                    if profile in recommendations:
                        result_parts.append(f"<sub><b>{profile}:</b> {recommendations[profile]}</sub>")
                
                if result_parts:
                    # Use a div with compact styling for better control
                    content = "<br/>".join(result_parts)
                    return f'<div style="text-align: left; line-height: 1.2;">{content}</div>'
        
        # Fallback to the original simple extraction
        return extract_investor_advice(report_path)
        
    except Exception as e:
        return "❌ Error"


def extract_cfo_recommendation(content):
    """Extract CFO recommendation from the Internal Stakeholder Recommendations table."""
    try:
        # Look for the CFO row in the stakeholder table - get the "Recommended Actions" column
        cfo_pattern = r'\|\s*CFO & Finance Team\s*\|[^|]*\|[^|]*\|\s*([^|]+)\s*\|'
        cfo_match = re.search(cfo_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if cfo_match:
            cfo_text = cfo_match.group(1).strip()
            # Extract key recommendation points and create a concise summary
            cfo_lower = cfo_text.lower()
            
            # Priority order for different types of recommendations
            if 'optimize capital structure' in cfo_lower and 'strategic invest' in cfo_lower:
                return '💰 OPTIMIZE & INVEST'
            elif 'optimize capital structure' in cfo_lower:
                return '💰 OPTIMIZE CAPITAL'
            elif 'strategic invest' in cfo_lower:
                return '📊 STRATEGIC INVEST'
            elif 'enhance investor relations' in cfo_lower:
                return '📈 ENHANCE IR'
            elif 'leverage' in cfo_lower and ('strength' in cfo_lower or 'position' in cfo_lower):
                return '💪 LEVERAGE STRENGTH'
            elif 'maintain' in cfo_lower and ('stability' in cfo_lower or 'liquidity' in cfo_lower):
                return '⚖️ MAINTAIN STABILITY'
            elif 'monitor' in cfo_lower or 'review' in cfo_lower:
                return '📊 MONITOR METRICS'
            elif 'cash management' in cfo_lower or 'cash flow' in cfo_lower:
                return '💵 MANAGE CASH'
            elif 'debt' in cfo_lower and ('reduce' in cfo_lower or 'manage' in cfo_lower):
                return '📊 MANAGE DEBT'
            elif 'dividend' in cfo_lower:
                return '💎 DIVIDEND FOCUS'
            elif 'growth' in cfo_lower or 'expansion' in cfo_lower:
                return '📈 SUPPORT GROWTH'
            else:
                # Extract first key action verb
                if 'plan' in cfo_lower:
                    return '📋 PLAN STRATEGY'
                elif 'prepare' in cfo_lower:
                    return '🛠️ PREPARE ACTION'
                else:
                    return '📊 MONITOR CAPITAL'
        
        return None
        
    except Exception:
        return None


def extract_ceo_recommendation(content):
    """Extract CEO recommendation from the Internal Stakeholder Recommendations table."""
    try:
        # Look for the CEO row in the stakeholder table - get the "Recommended Actions" column
        ceo_pattern = r'\|\s*CEO & Executive Leadership\s*\|[^|]*\|[^|]*\|\s*([^|]+)\s*\|'
        ceo_match = re.search(ceo_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if ceo_match:
            ceo_text = ceo_match.group(1).strip()
            # Extract key recommendation points and create a concise summary
            ceo_lower = ceo_text.lower()
            
            # Priority order for different types of recommendations
            if 'maintain innovation' in ceo_lower and 'monitor z-score' in ceo_lower:
                return '🚀 INNOVATE & MONITOR'
            elif 'maintain innovation' in ceo_lower or 'innovation focus' in ceo_lower:
                return '🚀 FOCUS INNOVATION'
            elif 'leverage' in ceo_lower and ('fundamentals' in ceo_lower or 'strength' in ceo_lower):
                return '💪 LEVERAGE STRENGTH'
            elif 'execution focus' in ceo_lower or 'operational execution' in ceo_lower:
                return '⚡ EXECUTION FOCUS'
            elif 'communicate' in ceo_lower and ('growth' in ceo_lower or 'strategy' in ceo_lower):
                return '📢 COMMUNICATE GROWTH'
            elif 'sustain' in ceo_lower and ('confidence' in ceo_lower or 'market' in ceo_lower):
                return '🎯 SUSTAIN CONFIDENCE'
            elif 'strategic vision' in ceo_lower:
                return '🔮 STRATEGIC VISION'
            elif 'monitor' in ceo_lower and 'indicator' in ceo_lower:
                return '📊 MONITOR INDICATORS'
            elif 'growth' in ceo_lower and 'strategy' in ceo_lower:
                return '📈 GROWTH STRATEGY'
            elif 'diversif' in ceo_lower:
                return '🌐 DIVERSIFY'
            elif 'expand' in ceo_lower or 'expansion' in ceo_lower:
                return '🔄 EXPAND OPERATIONS'
            elif 'turnaround' in ceo_lower or 'restructur' in ceo_lower:
                return '🔧 RESTRUCTURE'
            elif 'cost' in ceo_lower and ('reduction' in ceo_lower or 'control' in ceo_lower):
                return '✂️ COST CONTROL'
            else:
                # Extract first key action verb
                if 'focus' in ceo_lower:
                    return '🎯 STRATEGIC FOCUS'
                elif 'develop' in ceo_lower:
                    return '🛠️ DEVELOP STRATEGY'
                elif 'implement' in ceo_lower:
                    return '⚡ IMPLEMENT PLAN'
                else:
                    return '📊 STRATEGIC OVERSIGHT'
        
        return None
        
    except Exception:
        return None


def extract_investor_advice(report_path):
    """Extract the investor recommendation summary from the report."""
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Look for the recommendation summary pattern
        # Pattern 1: > **Recommendation: BUY across all investor profiles...
        pattern1 = r'> \*\*Recommendation(?:\s+Summary)?:\s*([^*]+?)\*\*'
        match1 = re.search(pattern1, content, re.IGNORECASE | re.DOTALL)
        
        if match1:
            advice = match1.group(1).strip()
            # Clean up the text and limit length
            advice = re.sub(r'\s+', ' ', advice)  # Replace multiple whitespace with single space
            # Extract the key recommendation (BUY, SELL, HOLD)
            if 'BUY' in advice.upper():
                if 'SELL' in advice.upper() and 'avoid' in advice.lower():
                    return "📈 BUY (Most Profiles)"
                else:
                    return "📈 BUY"
            elif 'SELL' in advice.upper():
                return "📉 SELL/HOLD"
            elif 'HOLD' in advice.upper():
                return "⚖️ HOLD"
            else:
                # Fallback: return first 50 characters
                return advice[:50] + "..." if len(advice) > 50 else advice
        
        # Pattern 2: Look for the table and extract the most common recommendation
        table_pattern = r'\|\s*Investment Profile\s*\|\s*Risk Tolerance\s*\|\s*Recommendation\s*\|.*?\n(.*?)(?=\n\s*>|\n\s*###|\n\s*---|\Z)'
        table_match = re.search(table_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if table_match:
            table_content = table_match.group(1)
            # Count recommendations
            buy_count = len(re.findall(r'\|\s*Buy\s*\|', table_content, re.IGNORECASE))
            sell_count = len(re.findall(r'\|\s*Sell\s*\|', table_content, re.IGNORECASE))
            hold_count = len(re.findall(r'\|\s*Hold\s*\|', table_content, re.IGNORECASE))
            
            total_recommendations = buy_count + sell_count + hold_count
            if total_recommendations > 0:
                if buy_count > sell_count and buy_count > hold_count:
                    return f"📈 BUY ({buy_count}/{total_recommendations})"
                elif sell_count > buy_count and sell_count > hold_count:
                    return f"📉 SELL ({sell_count}/{total_recommendations})"
                elif hold_count > buy_count and hold_count > sell_count:
                    return f"⚖️ HOLD ({hold_count}/{total_recommendations})"
                else:
                    return f"📊 MIXED ({buy_count}B/{hold_count}H/{sell_count}S)"
        
        return "❓ No Data"
        
    except Exception as e:
        return f"❌ Error"

def has_all_files(ticker_dir, ticker):
    logo = os.path.join(ticker_dir, f"{ticker}{LOGO_SUFFIX}")
    report = os.path.join(ticker_dir, f"{REPORT_PREFIX}{ticker}{REPORT_SUFFIX}")
    chart = os.path.join(ticker_dir, f"{REPORT_PREFIX}{ticker}{CHART_SUFFIX}")
    info = os.path.join(ticker_dir, COMPANY_INFO)
    return all(os.path.isfile(f) for f in [logo, report, chart, info])

def generate_table():
    rows = []
    for ticker in sorted(os.listdir(OUTPUT_DIR)):
        ticker_dir = os.path.join(OUTPUT_DIR, ticker)
        if not os.path.isdir(ticker_dir):
            continue
        if not has_all_files(ticker_dir, ticker):
            continue
        
        logo_rel = f"output/{ticker}/{ticker}{LOGO_SUFFIX}"
        report_rel = f"output/{ticker}/{REPORT_PREFIX}{ticker}{REPORT_SUFFIX}"
        chart_rel = f"output/{ticker}/{REPORT_PREFIX}{ticker}{CHART_SUFFIX}"
        info_path = os.path.join(ticker_dir, COMPANY_INFO)
        report_path = os.path.join(ticker_dir, f"{REPORT_PREFIX}{ticker}{REPORT_SUFFIX}")
        
        company_name = get_company_name(info_path)
        investor_advice = extract_investor_advice_detailed(report_path)
        # Combine logo and company name in one column
        logo_and_name = f'<div style="display: flex; align-items: center;"><img src="{logo_rel}" alt="{ticker}" width="40" style="margin-right:8px;"/> <span>{company_name}</span></div>'
        row = f'| {logo_and_name} | [Report]({report_rel}) | <a href="{chart_rel}"><img src="{chart_rel}" alt="{ticker} Chart" width="500"/></a> | {investor_advice} |'
        rows.append(row)
    return rows


def save_table_to_file(filename):
    """Save the generated table to a file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("| Logo & Name | Full Report | Trend Chart | AI Generated Advice |\n")
        f.write("|-------------|-------------|:-------------:|---------------------|\n")
        for row in generate_table():
            f.write(f"{row}\n")
    print(f"Table saved to {filename}")

def update_readme(readme_path="README.md", table_path="table.md"):
    """Update the tickers table in the README file using the markers."""
    # Read the current README content
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
    
    # Read the generated table
    with open(table_path, "r", encoding="utf-8") as f:
        table_content = f.read()
    
    # Define the markers
    start_marker = "<!-- BEGIN_TICKERS_TABLE -->"
    end_marker = "<!-- END_TICKERS_TABLE -->"
    
    # Find the positions of the markers
    start_pos = readme_content.find(start_marker)
    end_pos = readme_content.find(end_marker)
    
    if start_pos != -1 and end_pos != -1:
        # Extract the content before and after the markers
        before_table = readme_content[:start_pos + len(start_marker)]
        after_table = readme_content[end_pos:]
        
        # Create the updated README content
        updated_content = f"{before_table}\n{table_content}{after_table}"
        
        # Write the updated content back to README.md
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print(f"Successfully updated table in {readme_path}")
        return True
    else:
        print(f"Could not find markers in {readme_path}. Table not updated.")
        return False

def main():
    # Generate the table and save to file
    save_table_to_file("table.md")
    
    # Try to update the README
    update_readme()

if __name__ == "__main__":
    main()
