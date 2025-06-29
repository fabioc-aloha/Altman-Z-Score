#Requires -Version 5.1

# Azure Cost Monitoring Script for Altman Z-Score Dashboards
# Monitors spending and provides cost alerts

param(
    [Parameter(Mandatory=$false)]
    [double]$MonthlyThreshold = 10.00,
    
    [switch]$ShowDetails,
    [switch]$ExportToCSV
)

# Define colors for output
$Colors = @{
    Header   = "Cyan"
    Success  = "Green"
    Error    = "Red"
    Warning  = "Yellow"
    Info     = "White"
    Emphasis = "Magenta"
}

function Write-ColorText {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Colors[$Color]
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "=" * 70 -ForegroundColor $Colors.Header
    Write-Host (" " * ((70 - $Title.Length) / 2)) + $Title -ForegroundColor $Colors.Header
    Write-Host "=" * 70 -ForegroundColor $Colors.Header
    Write-Host ""
}

function Get-Configuration {
    $configFile = "azure_config.json"
    
    if (Test-Path $configFile) {
        try {
            return Get-Content $configFile | ConvertFrom-Json
        }
        catch {
            Write-ColorText "⚠️  Could not load configuration file" "Warning"
            return $null
        }
    }
    else {
        Write-ColorText "❌ No Azure configuration found" "Error"
        Write-ColorText "💡 Run setup_azure_hosting.ps1 first" "Info"
        return $null
    }
}

function Test-AzureLogin {
    try {
        $account = az account show --output json 2>$null | ConvertFrom-Json
        return $account
    }
    catch {
        Write-ColorText "❌ Not logged into Azure" "Error"
        Write-ColorText "💡 Run: az login" "Info"
        return $null
    }
}

function Get-StorageAccountCosts {
    param([string]$ResourceGroupName, [string]$StorageAccountName)
    
    try {
        # Get current month date range
        $startDate = (Get-Date -Day 1).ToString("yyyy-MM-dd")
        $endDate = (Get-Date).ToString("yyyy-MM-dd")
        
        Write-ColorText "📊 Retrieving cost data for current month ($startDate to $endDate)..." "Info"
        
        # Get usage details for the resource group
        $usageData = az consumption usage list `
            --start-date $startDate `
            --end-date $endDate `
            --output json | ConvertFrom-Json
        
        if (-not $usageData) {
            Write-ColorText "⚠️  No usage data available yet" "Warning"
            Write-ColorText "💡 Cost data typically appears 24-48 hours after resource usage" "Info"
            return $null
        }
        
        # Filter for our storage account
        $storageUsage = $usageData | Where-Object { 
            $_.instanceName -like "*$StorageAccountName*" -or 
            $_.resourceGroup -eq $ResourceGroupName 
        }
        
        return $storageUsage
    }
    catch {
        Write-ColorText "❌ Error retrieving cost data: $($_.Exception.Message)" "Error"
        return $null
    }
}

function Get-ResourceGroupCosts {
    param([string]$ResourceGroupName)
    
    try {
        # Get current month date range
        $startDate = (Get-Date -Day 1).ToString("yyyy-MM-dd")
        $endDate = (Get-Date).ToString("yyyy-MM-dd")
        
        # Use cost management API for more accurate data
        $costData = az costmanagement query `
            --type "ActualCost" `
            --dataset-aggregation '{totalCost:{name:PreTaxCost,function:Sum}}' `
            --dataset-grouping name=ResourceGroupName type=Dimension `
            --timeframe "Custom" `
            --time-period from=$startDate to=$endDate `
            --scope "/subscriptions/$(az account show --query id -o tsv)" `
            --output json 2>$null | ConvertFrom-Json
        
        if ($costData -and $costData.properties.rows) {
            $rgCost = $costData.properties.rows | Where-Object { $_[0] -eq $ResourceGroupName }
            if ($rgCost) {
                return [double]$rgCost[1]
            }
        }
        
        return 0.0
    }
    catch {
        Write-ColorText "⚠️  Could not retrieve detailed cost data" "Warning"
        return 0.0
    }
}

function Get-StorageMetrics {
    param([string]$StorageAccountName, [string]$ResourceGroupName)
    
    try {
        Write-ColorText "📈 Retrieving storage metrics..." "Info"
        
        # Get storage account resource ID
        $resourceId = az storage account show `
            --name $StorageAccountName `
            --resource-group $ResourceGroupName `
            --query "id" `
            --output tsv
        
        # Get metrics for the last 30 days
        $endTime = Get-Date
        $startTime = $endTime.AddDays(-30)
        
        # Get transaction count
        $transactions = az monitor metrics list `
            --resource $resourceId `
            --metric "Transactions" `
            --start-time $startTime.ToString("yyyy-MM-ddTHH:mm:ssZ") `
            --end-time $endTime.ToString("yyyy-MM-ddTHH:mm:ssZ") `
            --aggregation "Total" `
            --output json 2>$null | ConvertFrom-Json
        
        # Get blob capacity
        $capacity = az monitor metrics list `
            --resource $resourceId `
            --metric "BlobCapacity" `
            --start-time $startTime.ToString("yyyy-MM-ddTHH:mm:ssZ") `
            --end-time $endTime.ToString("yyyy-MM-ddTHH:mm:ssZ") `
            --aggregation "Average" `
            --output json 2>$null | ConvertFrom-Json
        
        return @{
            Transactions = $transactions
            Capacity = $capacity
        }
    }
    catch {
        Write-ColorText "⚠️  Could not retrieve storage metrics" "Warning"
        return $null
    }
}

function Show-CostSummary {
    param(
        [string]$ResourceGroupName,
        [string]$StorageAccountName,
        [double]$MonthlyThreshold
    )
    
    Write-ColorText "💰 Cost Analysis for $StorageAccountName" "Emphasis"
    Write-Host ""
    
    # Get current costs
    $currentCost = Get-ResourceGroupCosts -ResourceGroupName $ResourceGroupName
    $daysInMonth = [DateTime]::DaysInMonth((Get-Date).Year, (Get-Date).Month)
    $dayOfMonth = (Get-Date).Day
    $projectedCost = if ($dayOfMonth -gt 0) { $currentCost * ($daysInMonth / $dayOfMonth) } else { 0 }
    
    Write-ColorText "📊 Current Month Summary:" "Info"
    Write-Host "   • Days elapsed: $dayOfMonth / $daysInMonth" -ForegroundColor $Colors.Info
    Write-Host "   • Current cost: `$$([math]::Round($currentCost, 2))" -ForegroundColor $Colors.Success
    Write-Host "   • Projected monthly: `$$([math]::Round($projectedCost, 2))" -ForegroundColor $Colors.Emphasis
    Write-Host "   • Monthly threshold: `$$MonthlyThreshold" -ForegroundColor $Colors.Info
    
    # Cost analysis
    if ($projectedCost -gt $MonthlyThreshold) {
        Write-Host ""
        Write-ColorText "⚠️  ALERT: Projected cost exceeds threshold!" "Warning"
        $overage = $projectedCost - $MonthlyThreshold
        Write-Host "   • Overage: `$$([math]::Round($overage, 2))" -ForegroundColor $Colors.Error
        
        Write-Host ""
        Write-ColorText "💡 Cost optimization tips:" "Info"
        Write-Host "   • Review storage access patterns" -ForegroundColor $Colors.Info
        Write-Host "   • Enable auto-deletion of old files" -ForegroundColor $Colors.Info
        Write-Host "   • Consider cool storage tier for archives" -ForegroundColor $Colors.Info
    }
    elseif ($projectedCost -gt ($MonthlyThreshold * 0.8)) {
        Write-Host ""
        Write-ColorText "⚠️  Warning: Approaching threshold (80%)" "Warning"
    }
    else {
        Write-Host ""
        Write-ColorText "✅ Costs are within expected range" "Success"
    }
    
    # Get storage metrics
    $metrics = Get-StorageMetrics -StorageAccountName $StorageAccountName -ResourceGroupName $ResourceGroupName
    
    if ($metrics) {
        Write-Host ""
        Write-ColorText "📈 Storage Usage (Last 30 Days):" "Info"
        
        if ($metrics.Capacity -and $metrics.Capacity.value) {
            $latestCapacity = $metrics.Capacity.value[-1].average
            $capacityMB = [math]::Round($latestCapacity / 1MB, 2)
            Write-Host "   • Storage used: $capacityMB MB" -ForegroundColor $Colors.Success
        }
        
        if ($metrics.Transactions -and $metrics.Transactions.value) {
            $totalTransactions = ($metrics.Transactions.value | Measure-Object -Property total -Sum).Sum
            Write-Host "   • Total transactions: $totalTransactions" -ForegroundColor $Colors.Success
        }
    }
    
    return $projectedCost
}

function Export-CostData {
    param(
        [string]$ResourceGroupName,
        [double]$CurrentCost,
        [double]$ProjectedCost,
        [double]$Threshold
    )
    
    $reportData = [PSCustomObject]@{
        Date = (Get-Date).ToString("yyyy-MM-dd")
        ResourceGroup = $ResourceGroupName
        CurrentCost = [math]::Round($CurrentCost, 2)
        ProjectedMonthlyCost = [math]::Round($ProjectedCost, 2)
        MonthlyThreshold = $Threshold
        Status = if ($ProjectedCost -gt $Threshold) { "Over Threshold" } elseif ($ProjectedCost -gt ($Threshold * 0.8)) { "Warning" } else { "Normal" }
        DaysInMonth = [DateTime]::DaysInMonth((Get-Date).Year, (Get-Date).Month)
        DayOfMonth = (Get-Date).Day
    }
    
    $csvFile = "azure_costs_$(Get-Date -Format 'yyyyMM').csv"
    
    # Check if file exists to decide on headers
    $fileExists = Test-Path $csvFile
    
    $reportData | Export-Csv -Path $csvFile -NoTypeInformation -Append:$fileExists
    
    Write-ColorText "💾 Cost data exported to: $csvFile" "Success"
}

# Main execution
Clear-Host
Write-Header "Azure Cost Monitor"

# Check configuration
$config = Get-Configuration
if (-not $config) {
    exit 1
}

# Check Azure login
$account = Test-AzureLogin
if (-not $account) {
    exit 1
}

Write-ColorText "🔍 Monitoring costs for Azure resources..." "Info"
Write-Host "   • Subscription: $($account.name)" -ForegroundColor $Colors.Info
Write-Host "   • Resource Group: $($config.ResourceGroupName)" -ForegroundColor $Colors.Info
Write-Host "   • Storage Account: $($config.StorageAccountName)" -ForegroundColor $Colors.Info
Write-Host ""

# Show cost summary
$projectedCost = Show-CostSummary -ResourceGroupName $config.ResourceGroupName -StorageAccountName $config.StorageAccountName -MonthlyThreshold $MonthlyThreshold

# Export to CSV if requested
if ($ExportToCSV) {
    $currentCost = Get-ResourceGroupCosts -ResourceGroupName $config.ResourceGroupName
    Export-CostData -ResourceGroupName $config.ResourceGroupName -CurrentCost $currentCost -ProjectedCost $projectedCost -Threshold $MonthlyThreshold
}

# Show detailed breakdown if requested
if ($ShowDetails) {
    Write-Host ""
    Write-ColorText "📋 Detailed Cost Breakdown:" "Emphasis"
    
    try {
        $startDate = (Get-Date -Day 1).ToString("yyyy-MM-dd")
        $endDate = (Get-Date).ToString("yyyy-MM-dd")
        
        $detailedUsage = az consumption usage list `
            --start-date $startDate `
            --end-date $endDate `
            --output table
        
        if ($detailedUsage) {
            Write-Host $detailedUsage -ForegroundColor $Colors.Info
        }
        else {
            Write-ColorText "📊 No detailed usage data available yet" "Info"
            Write-ColorText "💡 Data typically appears 24-48 hours after usage" "Info"
        }
    }
    catch {
        Write-ColorText "⚠️  Could not retrieve detailed usage data" "Warning"
    }
}

Write-Host ""
Write-ColorText "💡 Helpful commands:" "Info"
Write-Host "   • Monitor costs: .\monitor_azure_costs.ps1" -ForegroundColor $Colors.Info
Write-Host "   • Detailed view: .\monitor_azure_costs.ps1 -ShowDetails" -ForegroundColor $Colors.Info
Write-Host "   • Export data: .\monitor_azure_costs.ps1 -ExportToCSV" -ForegroundColor $Colors.Info
Write-Host "   • Set threshold: .\monitor_azure_costs.ps1 -MonthlyThreshold 5.00" -ForegroundColor $Colors.Info

Write-Host ""
Read-Host "Press Enter to exit"
