#!/usr/bin/env python3
"""
Assets Manager Module for Altman Z-Score Dashboards

This module provides utilities to ensure the web/assets folder exists with all required
template files for dashboard generation. It can be imported by any dashboard generator
to ensure consistent assets availability.
"""

import os
import sys
import shutil
from pathlib import Path

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
sys.path.append(PROJECT_ROOT)

def get_common_paths():
    """Get common paths used across all dashboard generators."""
    project_root = Path(PROJECT_ROOT)
    web_dir = project_root / "web"
    assets_dir = web_dir / "assets"
    template_path = assets_dir / "dashboard_template.html"
    
    return {
        "project_root": project_root,
        "web_dir": web_dir,
        "assets_dir": assets_dir,
        "template_path": template_path
    }

def ensure_assets_folder():
    """
    Ensures that the web/assets/ folder exists with all required template files.
    Creates the folder and files if they don't exist.
    
    Returns:
        str: Path to the assets directory
    """
    paths = get_common_paths()
    web_dir = paths["web_dir"]
    assets_dir = paths["assets_dir"]
    
    # Create web and assets directories if they don't exist
    os.makedirs(web_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)
    
    # Define required asset files
    asset_files = {
        "dashboard_common.css": """/* 
 * Altman Z-Score Dashboard Common Styles
 * Standardized styles for all dashboard types
 */

body {
    font-family: 'Segoe UI', Arial, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    color: #333;
    line-height: 1.6;
    background-color: #f9f9f9;
}

h1,
h2 {
    color: #1a5276;
    margin-top: 30px;
}

h1 {
    text-align: center;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}

.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.date {
    text-align: right;
    font-size: 1.1em;
    color: #666;
}

.subtitle {
    font-size: 1.2em;
    color: #555;
    text-align: center;
    margin-top: -10px;
    margin-bottom: 30px;
}

/* Stats section styling */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin: 30px 0;
}

.stat-card {
    background-color: white;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
}

.stat-number {
    font-size: 2.2em;
    font-weight: bold;
    color: #2980b9;
    margin-bottom: 5px;
}

.stat-label {
    color: #7f8c8d;
    text-transform: uppercase;
    font-size: 0.9em;
    letter-spacing: 1px;
}

/* Summary section styling */
.summary-section {
    background: white;
    border-radius: 10px;
    padding: 25px;
    margin: 30px 0;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.summary-text {
    margin-top: 25px;
    line-height: 1.8;
}

.summary-text p {
    margin-bottom: 15px;
}

.summary-text strong {
    color: #2c3e50;
}

/* Company grid styling */
.company-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 30px;
}

.company-card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    position: relative;
    display: flex;
    flex-direction: column;
    height: 100%;
}

.company-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.company-header {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
    border-bottom: 1px solid #eee;
    padding-bottom: 15px;
}

.company-logo {
    width: 60px;
    height: 60px;
    object-fit: contain;
    margin-right: 15px;
}

.company-name {
    flex-grow: 1;
}

.company-name h3 {
    margin: 0 0 5px 0;
    font-size: 1.2em;
    color: #2c3e50;
}

.company-ticker {
    font-size: 0.9em;
    color: #7f8c8d;
    font-weight: normal;
}

.company-metrics {
    margin: 15px 0;
    flex-grow: 1;
}

.metric {
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
}

.metric-name {
    color: #7f8c8d;
}

.metric-value {
    font-weight: bold;
    color: #2c3e50;
}

.z-score {
    margin-top: 15px;
    padding: 10px;
    border-radius: 5px;
    text-align: center;
    font-weight: bold;
    margin-top: auto;
}

.safe {
    background-color: #d5f5e3;
    color: #27ae60;
}

.gray {
    background-color: #f8f9fa;
    color: #7f8c8d;
}

.distress {
    background-color: #fadbd8;
    color: #c0392b;
}

.model-info {
    background: rgba(52, 152, 219, 0.1);
    border-left: 4px solid #3498db;
    padding: 20px;
    margin: 20px 0;
    border-radius: 8px;
}

.back-link {
    display: inline-block;
    margin: 20px 0;
    color: #3498db;
    text-decoration: none;
    font-weight: bold;
}

.back-link:hover {
    text-decoration: underline;
}

/* Media queries for responsiveness */
@media (max-width: 768px) {
    .company-grid {
        grid-template-columns: 1fr;
    }

    .header-container {
        flex-direction: column;
        text-align: center;
    }

    .date {
        text-align: center;
        margin-top: 10px;
    }
}""",
        "dashboard_template.html": """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{DASHBOARD_TITLE}} - Altman Z-Score</title>
    <link rel="stylesheet" href="assets/dashboard_common.css">
    {{ADDITIONAL_CSS}}
</head>

<body>
    <a href="index.html" class="back-link">← Back to Dashboard Home</a>

    <div class="header-container">
        <div>
            <h1>{{DASHBOARD_TITLE}}</h1>
            {{SUBTITLE_PLACEHOLDER}}
        </div>
        <div class="date">Generated: {{GENERATION_DATE}}</div>
    </div>

    <div class="summary-section">
        <h2>Portfolio Summary</h2>
        <div class="stats-grid">
            {{STATS_GRID}}
        </div>
        <div class="summary-text">
            {{SUMMARY_TEXT}}
        </div>
    </div>

    {{MODEL_INFO_PLACEHOLDER}}

    <h2>Companies</h2>
    <div class="company-grid">
        {{COMPANY_GRID}}
    </div>

    <a href="index.html" class="back-link">← Back to Dashboard Home</a>

    <script>
        // Add interactive elements, sorting, filtering
        document.addEventListener('DOMContentLoaded', function () {
            // Add hover effects to company cards
            const companyCards = document.querySelectorAll('.company-card');
            companyCards.forEach(card => {
                card.addEventListener('mouseenter', function () {
                    this.style.transform = 'translateY(-5px)';
                    this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.2)';
                });

                card.addEventListener('mouseleave', function () {
                    this.style.transform = 'translateY(0)';
                    this.style.boxShadow = '0 3px 10px rgba(0,0,0,0.1)';
                });
            });

            {{ADDITIONAL_SCRIPTS}}
        });
    </script>
</body>

</html>""",
        "dashboard_styles.css": """/* 
 * Altman Z-Score Dashboard Navigation Styles
 * Styles for the main dashboard navigation page
 */

body {
    font-family: 'Segoe UI', Arial, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    color: #333;
    line-height: 1.6;
    background-color: #f9f9f9;
}

.header {
    text-align: center;
    margin-bottom: 30px;
}

h1 {
    color: #1a5276;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
    margin-bottom: 5px;
}

.subtitle {
    color: #7f8c8d;
    font-size: 1.2em;
    margin-bottom: 30px;
}

.date {
    color: #666;
    font-style: italic;
    margin-top: -10px;
    margin-bottom: 30px;
}

.section-title {
    color: #2c3e50;
    border-bottom: 1px solid #ddd;
    padding-bottom: 5px;
    margin-top: 40px;
    margin-bottom: 20px;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.dashboard-card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    display: flex;
    flex-direction: column;
    height: 100%;
}

.dashboard-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.dashboard-card-header {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
    border-bottom: 1px solid #eee;
    padding-bottom: 15px;
}

.dashboard-icon {
    font-size: 24px;
    margin-right: 15px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
}

.dashboard-title {
    flex-grow: 1;
}

.dashboard-title h3 {
    margin: 0 0 5px 0;
    font-size: 1.2em;
    color: #2c3e50;
}

.dashboard-description {
    color: #7f8c8d;
    margin-bottom: 20px;
    flex-grow: 1;
}

.dashboard-link {
    background-color: #3498db;
    color: white;
    text-decoration: none;
    padding: 10px 15px;
    border-radius: 4px;
    text-align: center;
    font-weight: bold;
    transition: background-color 0.3s;
    margin-top: auto;
    display: block;
}

.dashboard-link:hover {
    background-color: #2980b9;
}

.buy-section .dashboard-icon {
    background-color: #27ae60;
    color: white;
}

.profile-section .dashboard-icon {
    background-color: #3498db;
    color: white;
}

.sell-section .dashboard-icon {
    background-color: #e74c3c;
    color: white;
}

.industry-section .dashboard-icon {
    background-color: #9b59b6;
    color: white;
}

.footer {
    margin-top: 50px;
    text-align: center;
    color: #7f8c8d;
    font-size: 0.9em;
    border-top: 1px solid #ddd;
    padding-top: 20px;
}

/* Media queries for responsiveness */
@media (max-width: 768px) {
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
}""",
        "index_template.html": """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Altman Z-Score Dashboard Navigator</title>
    <link rel="stylesheet" href="assets/dashboard_styles.css">
</head>

<body>
    <div class="header">
        <h1>Altman Z-Score Dashboard Navigator</h1>
        <p class="subtitle">Stock Picks Based on Financial Health Analysis</p>
        <p class="date">Generated: {{GENERATION_DATE}}</p>
    </div>

    <!-- Buy Recommendations Section -->
    <h2 class="section-title">Buy Recommendations</h2>
    <div class="dashboard-grid buy-section">
        {{BUY_DASHBOARDS}}
    </div>

    <!-- Investor Profile Dashboards Section -->
    <h2 class="section-title">Investor Profile Dashboards</h2>
    <div class="dashboard-grid profile-section">
        {{PROFILE_DASHBOARDS}}
    </div>

    <!-- Sell Recommendations Section -->
    <h2 class="section-title">Sell Recommendations</h2>
    <div class="dashboard-grid sell-section">
        {{SELL_DASHBOARDS}}
    </div>

    <!-- Industry Specific Dashboards Section -->
    <h2 class="section-title">Industry-Specific Dashboards</h2>
    <div class="dashboard-grid industry-section">
        {{INDUSTRY_DASHBOARDS}}
    </div>

    <div class="footer">
        <p>Altman Z-Score Analysis &copy; 2025 | Version {{VERSION}}</p>
    </div>
</body>

</html>"""
    }
    
    # Check if files exist and create them if they don't
    for filename, content in asset_files.items():
        file_path = os.path.join(assets_dir, filename)
        if not os.path.exists(file_path):
            print(f"Creating missing asset file: {filename}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    # Create default logo if it doesn't exist
    default_logo_path = os.path.join(assets_dir, "default_logo.png")
    if not os.path.exists(default_logo_path):
        # Copy from project root if available
        project_default_logo = os.path.join(PROJECT_ROOT, "default_logo.png")
        if os.path.exists(project_default_logo):
            try:
                shutil.copy(project_default_logo, default_logo_path)
                print(f"Copied default logo to: {default_logo_path}")
            except Exception as e:
                print(f"Failed to copy default logo: {e}")
        else:
            print(f"Warning: Default logo not found at {project_default_logo}")
    
    # Create web/output directory for company logos
    web_output_dir = os.path.join(web_dir, "output")
    web_logos_dir = os.path.join(web_output_dir, "logos")
    os.makedirs(web_logos_dir, exist_ok=True)
    print(f"Ensured logos directory exists at: {web_logos_dir}")
    
    return assets_dir

if __name__ == "__main__":
    # If run directly, this will ensure the assets folder exists
    ensure_assets_folder()
    print("Assets folder check completed.")
