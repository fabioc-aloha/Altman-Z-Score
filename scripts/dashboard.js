// Helper function to get Z-Score color class
function getZScoreClass(score) {
    if (score >= 8) return 'excellent';
    if (score >= 5) return 'good';
    if (score >= 3) return 'fair';
    if (score >= 1.8) return 'poor';
    return 'distress';
}

// Helper function to format market cap
function formatMarketCap(marketCap) {
    return marketCap || 'N/A';
}

// Format price with 2 decimal places and $ symbol
function formatPrice(price) {
    return price ? `$${parseFloat(price).toFixed(2)}` : 'N/A';
}

// Build table row HTML
function buildTableRow(stock) {
    // Always ensure we have a valid logo path
    const logoPath = stock.Logo && stock.Logo !== 'default_logo.png'
        ? stock.Logo
        : 'default_logo.png';

    return `
        <tr>
            <td>
                <img class="company-logo" src="${logoPath}" alt="${stock.Symbol}" 
                     onerror="this.src='default_logo.png'" loading="lazy" 
                     title="${stock.Name}">
            </td>
            <td>
                <div class="symbol">${stock.Symbol}</div>
            </td>
            <td>
                <div class="company-name">${stock.Name}</div>
            </td>
            <td>
                <div class="z-score ${getZScoreClass(stock.ZScore)}">${stock.ZScore.toFixed(2)}</div>
            </td>
            <td>
                <div class="risk-category">${stock.Risk || 'N/A'}</div>
            </td>
            <td>
                <div class="recommendation ${stock.Recommendation.toLowerCase().replace(' ', '-')}">${stock.Recommendation}</div>
            </td>
            <td>
                <div class="confidence">${stock.Confidence || 'N/A'}</div>
            </td>
            <td>
                <div class="model-type">${stock.Model || 'N/A'}</div>
            </td>
            <td>
                <div class="data-quality">${stock.Quality || 'N/A'}</div>
            </td>
            <td>
                <div class="price">${formatPrice(stock.Price)}</div>
            </td>
            <td>
                <div class="market-cap">${stock.MarketCap || 'N/A'}</div>
            </td>
            <td>
                <div class="analysis-date">${stock.AnalysisDate || 'N/A'}</div>
            </td>
        </tr>
    `;
}

// Update table with filtered data
function updateTable(data = stockData) {
    // Don't update if no data is available yet
    if (!data || data.length === 0) return;

    const tbody = document.getElementById('stockTableBody');
    if (!tbody) return; // Don't update if table body doesn't exist yet

    const rows = data.map(buildTableRow).join('');

    // Only update DOM if content has changed
    if (tbody.innerHTML !== rows) {
        tbody.innerHTML = rows;
    }
}

// Populate filter dropdowns
function populateFilters() {
    // Don't populate if no data is available yet
    if (!stockData || stockData.length === 0) return;

    const models = [...new Set(stockData.map(s => s.Model).filter(Boolean))].sort();
    const risks = [...new Set(stockData.map(s => s.Risk).filter(Boolean))].sort();
    const recommendations = [...new Set(stockData.map(s => s.Recommendation))].sort();

    const modelSelect = document.getElementById('model');
    // Clear existing options except the first one
    while (modelSelect.options.length > 1) {
        modelSelect.remove(1);
    }
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    });

    const riskSelect = document.getElementById('risk');
    // Clear existing options except the first one
    while (riskSelect.options.length > 1) {
        riskSelect.remove(1);
    }
    risks.forEach(risk => {
        const option = document.createElement('option');
        option.value = risk;
        option.textContent = risk;
        riskSelect.appendChild(option);
    });

    const recommendationSelect = document.getElementById('recommendation');
    // Clear existing options except the first one
    while (recommendationSelect.options.length > 1) {
        recommendationSelect.remove(1);
    }
    recommendations.forEach(rec => {
        const option = document.createElement('option');
        option.value = rec;
        option.textContent = rec;
        recommendationSelect.appendChild(option);
    });

    const portfolioSelect = document.getElementById('portfolio');
    // Clear existing options except the first one
    while (portfolioSelect.options.length > 1) {
        portfolioSelect.remove(1);
    }
    const portfolios = [...new Set(stockData.map(s => s.Portfolio).filter(Boolean))].sort();
    portfolios.forEach(portfolio => {
        const option = document.createElement('option');
        option.value = portfolio;
        option.textContent = portfolio;
        portfolioSelect.appendChild(option);
    });
}

// Filter data based on current filter values
function filterData() {
    const searchTerm = document.getElementById('search').value.toLowerCase();
    const sector = document.getElementById('sector').value;
    const recommendation = document.getElementById('recommendation').value;
    const portfolio = document.getElementById('portfolio').value;

    const filtered = stockData.filter(stock => {
        const matchesSearch = searchTerm === '' ||
            stock.Symbol.toLowerCase().includes(searchTerm) ||
            stock.Name.toLowerCase().includes(searchTerm);

        const matchesSector = sector === '' || stock.Sector === sector;
        const matchesRecommendation = recommendation === '' || stock.Recommendation === recommendation;
        const matchesPortfolio = portfolio === '' || stock.Portfolio === portfolio;

        return matchesSearch && matchesSector && matchesRecommendation && matchesPortfolio;
    });

    updateTable(filtered);
}

// Handle sort clicks
let currentSort = { column: 'symbol', ascending: true };

function sortData(column) {
    if (currentSort.column === column) {
        currentSort.ascending = !currentSort.ascending;
    } else {
        currentSort = { column, ascending: true };
    }

    const sortedData = [...stockData].sort((a, b) => {
        let valueA, valueB;

        switch (column) {
            case 'symbol':
                valueA = a.Symbol;
                valueB = b.Symbol;
                break;
            case 'name':
                valueA = a.Name;
                valueB = b.Name;
                break;
            case 'zscore':
                valueA = a.ZScore;
                valueB = b.ZScore;
                break;
            case 'recommendation':
                valueA = a.Recommendation;
                valueB = b.Recommendation;
                break;
            case 'sector':
                valueA = a.Sector || '';
                valueB = b.Sector || '';
                break;
            case 'price':
                valueA = a.Price || 0;
                valueB = b.Price || 0;
                break;
            case 'marketcap':
                valueA = a.MarketCap || '';
                valueB = b.MarketCap || '';
                break;
            case 'portfolio':
                valueA = a.Portfolio || '';
                valueB = b.Portfolio || '';
                break;
        }

        if (typeof valueA === 'number' && typeof valueB === 'number') {
            return currentSort.ascending ? valueA - valueB : valueB - valueA;
        }

        return currentSort.ascending ?
            valueA.toString().localeCompare(valueB.toString()) :
            valueB.toString().localeCompare(valueA.toString());
    });

    updateTable(sortedData);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded');

    // Debug: Log initial stock data
    console.log('Initial stock data:', stockData);

    // Ensure stock data is available and valid
    if (!Array.isArray(stockData)) {
        console.error('Stock data is not an array:', stockData);
        return;
    }

    if (stockData.length === 0) {
        console.warn('Stock data array is empty');
    }

    // Add event listeners
    const searchInput = document.getElementById('search');
    const sectorSelect = document.getElementById('sector');
    const recommendationSelect = document.getElementById('recommendation');
    const portfolioSelect = document.getElementById('portfolio');
    const tbody = document.getElementById('stockTableBody');

    if (!searchInput || !sectorSelect || !recommendationSelect || !portfolioSelect || !tbody) {
        console.error('Required elements not found');
        return;
    }

    // Attach event listeners
    searchInput.addEventListener('input', filterData);
    sectorSelect.addEventListener('change', filterData);
    recommendationSelect.addEventListener('change', filterData);
    portfolioSelect.addEventListener('change', filterData);

    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => sortData(th.dataset.sort));
    });

    // Initialize the table and filters
    try {
        console.log('Populating filters...');
        populateFilters();
        console.log('Updating table...');
        updateTable(stockData);
        console.log('Initial table update complete');
    } catch (error) {
        console.error('Error during initialization:', error);
    }
});
