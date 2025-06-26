# Small Batch Test - FMP Free Tier Friendly
# Run a small sample of companies to test the system without hitting API limits
# Usage: pwsh.exe -File test_small_batch.ps1

# Small test batch (5 companies from different sectors)
$test_batch = @(
    'AAPL', # Tech (should be safe zone)
    'MSFT', # Tech (should be safe zone)  
    'KO', # Consumer staples (should be safe)
    'CAT', # Industrial (moderate risk)
    'T'      # Telecom (higher risk/distressed)
)

Write-Host "🧪 Running SMALL BATCH TEST for FMP API limits" -ForegroundColor Yellow
Write-Host "📊 Testing 5 companies: $($test_batch -join ', ')" -ForegroundColor Cyan
Write-Host "⚡ Each company uses ~3-5 API calls (Total: ~15-25 calls)" -ForegroundColor Green
Write-Host "📈 Free FMP tier allows 250 calls/day" -ForegroundColor White
Write-Host ""

# Test API availability first
Write-Host "1️⃣ Testing API availability..." -ForegroundColor Yellow
python -m pytest tests/api/test_api_limit.py -v

if ($LASTEXITCODE -eq 0) {
    Write-Host "2️⃣ API is available! Running small batch analysis..." -ForegroundColor Green
    
    # Run the small batch
    $env:PYTHONUNBUFFERED = "1"
    python ../../main.py @test_batch
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Small batch completed successfully!" -ForegroundColor Green
        Write-Host "📁 Check output folders: AAPL/, MSFT/, KO/, CAT/, T/" -ForegroundColor Cyan
        
        # Generate summary table
        Write-Host "3️⃣ Generating portfolio summary..." -ForegroundColor Yellow
        python ../../generate_readme_table.py
        
        Write-Host "🎉 Test complete! You can now run larger batches if needed." -ForegroundColor Green
    }
    else {
        Write-Host "❌ Small batch failed. Check logs for details." -ForegroundColor Red
    }
}
else {
    Write-Host "❌ API test failed. Please check your FMP API status." -ForegroundColor Red
    Write-Host "💡 Solutions:" -ForegroundColor Yellow
    Write-Host "   • Wait for daily limit reset (midnight UTC)" -ForegroundColor White
    Write-Host "   • Upgrade your FMP plan" -ForegroundColor White
    Write-Host "   • Check API key in .env file" -ForegroundColor White
}
