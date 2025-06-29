#Requires -Version 5.1

# Azure Storage Deployment Script for Altman Z-Score Dashboards
# Deploys dashboards to Azure Static Website hosting

param(
    [Parameter(Mandatory = $false)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $false)]
    [string]$StorageAccountName,
    
    [Parameter(Mandatory = $false)]
    [string]$Location = "East US",
    
    [switch]$SetupOnly,
    [switch]$DeployOnly,
    [switch]$GenerateFirst,
    [switch]$OpenBrowser,
    [switch]$Verbose,
    [switch]$NoPause
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
    Write-Host "=" * 80 -ForegroundColor $Colors.Header
    Write-Host (" " * ((80 - $Title.Length) / 2)) + $Title -ForegroundColor $Colors.Header
    Write-Host "=" * 80 -ForegroundColor $Colors.Header
    Write-Host ""
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "-" * 60 -ForegroundColor $Colors.Info
    Write-Host $Title -ForegroundColor $Colors.Emphasis
    Write-Host "-" * 60 -ForegroundColor $Colors.Info
}

function Test-AzurePrerequisites {
    $issues = @()
    
    # Check Azure CLI
    try {
        $azVersion = az version --output json 2>$null | ConvertFrom-Json
        Write-ColorText "✅ Azure CLI: $($azVersion.'azure-cli')" "Success"
    }
    catch {
        $issues += "Azure CLI not installed"
        Write-ColorText "❌ Azure CLI not found" "Error"
    }
    
    # Check Azure login
    try {
        $account = az account show --output json 2>$null | ConvertFrom-Json
        Write-ColorText "✅ Azure Login: $($account.user.name)" "Success"
    }
    catch {
        $issues += "Not logged into Azure"
        Write-ColorText "❌ Not logged into Azure" "Error"
    }
    
    return $issues
}

function Get-Configuration {
    $configFile = "azure_config.json"
    
    if (Test-Path $configFile) {
        try {
            $config = Get-Content $configFile | ConvertFrom-Json
            Write-ColorText "📄 Loaded existing Azure configuration" "Success"
            Write-Host "   • Resource Group: $($config.ResourceGroupName)" -ForegroundColor $Colors.Info
            Write-Host "   • Storage Account: $($config.StorageAccountName)" -ForegroundColor $Colors.Info
            Write-Host "   • Website URL: $($config.WebsiteUrl)" -ForegroundColor $Colors.Info
            return $config
        }
        catch {
            Write-ColorText "⚠️  Could not load configuration file" "Warning"
            return $null
        }
    }
    else {
        Write-ColorText "📄 No existing configuration found" "Info"
        return $null
    }
}

function New-AzureStaticWebsite {
    param(
        [string]$ResourceGroupName,
        [string]$StorageAccountName,
        [string]$Location
    )
    
    Write-Section "Creating Azure Resources"
    
    try {
        # Create resource group
        Write-ColorText "📦 Creating resource group: $ResourceGroupName" "Info"
        az group create --name $ResourceGroupName --location $Location --output none
        Write-ColorText "✅ Resource group created" "Success"
        
        # Create storage account
        Write-ColorText "💾 Creating storage account: $StorageAccountName" "Info"
        az storage account create `
            --name $StorageAccountName `
            --resource-group $ResourceGroupName `
            --location $Location `
            --sku Standard_LRS `
            --kind StorageV2 `
            --access-tier Hot `
            --https-only true `
            --allow-blob-public-access true `
            --output none
        Write-ColorText "✅ Storage account created" "Success"
        
        # Enable static website hosting
        Write-ColorText "🌐 Enabling static website hosting..." "Info"
        az storage blob service-properties update `
            --account-name $StorageAccountName `
            --static-website `
            --index-document index.html `
            --404-document index.html `
            --output none
        Write-ColorText "✅ Static website hosting enabled" "Success"
        
        # Get the website URL
        $webUrl = az storage account show `
            --name $StorageAccountName `
            --resource-group $ResourceGroupName `
            --query "primaryEndpoints.web" `
            --output tsv
        
        $webUrl = $webUrl.TrimEnd('/')
        
        # Save configuration
        $config = @{
            ResourceGroupName  = $ResourceGroupName
            StorageAccountName = $StorageAccountName
            Location           = $Location
            WebsiteUrl         = $webUrl
            LastUpdated        = (Get-Date).ToString()
        }
        
        $config | ConvertTo-Json | Out-File -FilePath "azure_config.json" -Encoding UTF8
        
        Write-Host ""
        Write-ColorText "🎉 Azure Static Website Setup Complete!" "Success"
        Write-Host ""
        Write-ColorText "📊 Your website details:" "Info"
        Write-Host "   • Resource Group: $ResourceGroupName" -ForegroundColor $Colors.Success
        Write-Host "   • Storage Account: $StorageAccountName" -ForegroundColor $Colors.Success
        Write-Host "   • Website URL: $webUrl" -ForegroundColor $Colors.Emphasis
        
        return $webUrl
    }
    catch {
        Write-ColorText "❌ Failed to create Azure resources: $($_.Exception.Message)" "Error"
        return $null
    }
}

function Invoke-DashboardGeneration {
    Write-Section "Generating Dashboards"
    
    if (Test-Path "generate_all_dashboards.ps1") {
        Write-ColorText "🔄 Generating fresh dashboards..." "Info"
        
        try {
            & .\generate_all_dashboards.ps1 -NoPause -OpenBrowser:$false
            
            if ($LASTEXITCODE -eq 0) {
                Write-ColorText "✅ Dashboards generated successfully" "Success"
                return $true
            }
            else {
                Write-ColorText "❌ Dashboard generation failed" "Error"
                return $false
            }
        }
        catch {
            Write-ColorText "❌ Error running dashboard generation: $($_.Exception.Message)" "Error"
            return $false
        }
    }
    else {
        Write-ColorText "❌ Dashboard generation script not found" "Error"
        Write-ColorText "💡 Please ensure generate_all_dashboards.ps1 exists" "Info"
        return $false
    }
}

function Deploy-FilesToAzure {
    param(
        [string]$StorageAccountName,
        [string]$ResourceGroupName
    )
    
    Write-Section "Deploying Files to Azure"
    
    # Define files to upload
    $filesToUpload = @(
        "index.html",
        "strong_buys.html",
        "conservative_picks.html",
        "dividend_picks.html",
        "value_picks.html",
        "growth_picks.html",
        "aggressive_picks.html",
        "sell_picks.html",
        "strong_sell_picks.html"
    )
    
    Write-ColorText "📂 Checking files to deploy..." "Info"
    
    $existingFiles = @()
    $totalSize = 0
    
    foreach ($file in $filesToUpload) {
        if (Test-Path $file) {
            $fileInfo = Get-Item $file
            $size = [math]::Round($fileInfo.Length / 1KB, 1)
            $totalSize += $fileInfo.Length
            Write-Host "   ✅ $file ($size KB)" -ForegroundColor $Colors.Success
            $existingFiles += $file
        }
        else {
            Write-Host "   ❌ $file (not found)" -ForegroundColor $Colors.Error
        }
    }
    
    if ($existingFiles.Count -eq 0) {
        Write-ColorText "❌ No files to deploy" "Error"
        Write-ColorText "💡 Run generate_all_dashboards.ps1 first" "Info"
        return $false
    }
    
    $totalSizeMB = [math]::Round($totalSize / 1MB, 2)
    Write-Host ""
    Write-ColorText "📊 Deployment Summary:" "Info"
    Write-Host "   • Files to upload: $($existingFiles.Count)" -ForegroundColor $Colors.Info
    Write-Host "   • Total size: $totalSizeMB MB" -ForegroundColor $Colors.Info
    
    Write-Host ""
    Write-ColorText "🚀 Uploading files to Azure Storage..." "Info"
    
    $successCount = 0
    $uploadStart = Get-Date
    
    foreach ($file in $existingFiles) {
        Write-Host "   📤 Uploading: " -NoNewline -ForegroundColor $Colors.Info
        Write-Host $file -ForegroundColor $Colors.Emphasis
        
        try {
            az storage blob upload `
                --account-name $StorageAccountName `
                --container-name '$web' `
                --name $file `
                --file $file `
                --content-type "text/html" `
                --overwrite `
                --output none
            
            Write-Host "      ✅ Success!" -ForegroundColor $Colors.Success
            $successCount++
        }
        catch {
            Write-Host "      ❌ Failed: $($_.Exception.Message)" -ForegroundColor $Colors.Error
        }
    }
    
    $uploadDuration = ((Get-Date) - $uploadStart).TotalSeconds
    
    Write-Host ""
    Write-ColorText "📊 Upload Results:" "Info"
    Write-Host "   • Successful: $successCount/$($existingFiles.Count)" -ForegroundColor $Colors.Success
    Write-Host "   • Duration: $([math]::Round($uploadDuration, 1)) seconds" -ForegroundColor $Colors.Info
    
    if ($successCount -eq $existingFiles.Count) {
        Write-ColorText "🎉 All files uploaded successfully!" "Success"
        return $true
    }
    else {
        Write-ColorText "⚠️  Some files failed to upload" "Warning"
        return $false
    }
}

function Show-DeploymentResults {
    param(
        [string]$WebsiteUrl,
        [bool]$Success
    )
    
    Write-Section "Deployment Results"
    
    if ($Success) {
        Write-ColorText "🎉 Deployment completed successfully!" "Success"
        Write-Host ""
        
        Write-ColorText "🌐 Your dashboards are now live at:" "Emphasis"
        Write-Host "   $WebsiteUrl" -ForegroundColor $Colors.Emphasis
        Write-Host ""
        
        Write-ColorText "📊 Available dashboards:" "Info"
        $dashboards = @(
            @{ Name = "Main Dashboard"; File = "" },
            @{ Name = "Strong Buys"; File = "strong_buys.html" },
            @{ Name = "Conservative Picks"; File = "conservative_picks.html" },
            @{ Name = "Dividend Picks"; File = "dividend_picks.html" },
            @{ Name = "Value Picks"; File = "value_picks.html" },
            @{ Name = "Growth Picks"; File = "growth_picks.html" },
            @{ Name = "Aggressive Picks"; File = "aggressive_picks.html" },
            @{ Name = "Sell Recommendations"; File = "sell_picks.html" },
            @{ Name = "Strong Sell"; File = "strong_sell_picks.html" }
        )
        
        foreach ($dashboard in $dashboards) {
            $url = if ($dashboard.File) { "$WebsiteUrl/$($dashboard.File)" } else { $WebsiteUrl }
            Write-Host "   • $($dashboard.Name): $url" -ForegroundColor $Colors.Success
        }
        
        Write-Host ""
        Write-ColorText "💡 Tips:" "Info"
        Write-Host "   • Redeploy anytime: .\deploy_to_azure_storage.ps1 -DeployOnly" -ForegroundColor $Colors.Info
        Write-Host "   • Generate + Deploy: .\deploy_to_azure_storage.ps1" -ForegroundColor $Colors.Info
        Write-Host "   • Check costs: az consumption usage list" -ForegroundColor $Colors.Info
        
        if ($OpenBrowser) {
            Write-Host ""
            Write-ColorText "🌐 Opening website in browser..." "Info"
            try {
                Start-Process $WebsiteUrl
                Write-ColorText "✅ Browser opened successfully!" "Success"
            }
            catch {
                Write-ColorText "❌ Failed to open browser: $($_.Exception.Message)" "Error"
                Write-ColorText "💡 You can manually visit: $WebsiteUrl" "Info"
            }
        }
    }
    else {
        Write-ColorText "❌ Deployment failed!" "Error"
        Write-ColorText "💡 Please check the errors above and try again" "Warning"
    }
}

# Main execution
Clear-Host
Write-Header "Azure Static Website Deployment"

# Set default for OpenBrowser if not specified
if (-not $PSBoundParameters.ContainsKey('OpenBrowser')) {
    $OpenBrowser = $true
}

Write-ColorText "🚀 Azure deployment for Altman Z-Score dashboards" "Info"
Write-Host ""

# Check prerequisites
Write-Section "Checking Prerequisites"
$prereqIssues = Test-AzurePrerequisites

if ($prereqIssues.Count -gt 0) {
    Write-ColorText "❌ Prerequisites not met:" "Error"
    foreach ($issue in $prereqIssues) {
        Write-Host "   • $issue" -ForegroundColor $Colors.Error
    }
    Write-Host ""
    Write-ColorText "💡 Please resolve these issues and try again:" "Info"
    Write-Host "   • Install Azure CLI: https://aka.ms/installazurecliwindows" -ForegroundColor $Colors.Info
    Write-Host "   • Login to Azure: az login" -ForegroundColor $Colors.Info
    
    if (-not $NoPause) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# Load existing configuration
$existingConfig = Get-Configuration

# Determine operation mode
if ($SetupOnly -or (-not $existingConfig -and -not $DeployOnly)) {
    # Setup new Azure resources
    if (-not $ResourceGroupName) {
        $defaultRG = if ($existingConfig) { $existingConfig.ResourceGroupName } else { "altman-zscore-dashboards" }
        if ($NoPause) {
            $ResourceGroupName = $defaultRG
        }
        else {
            $ResourceGroupName = Read-Host "Resource Group Name [$defaultRG]"
            if (-not $ResourceGroupName) { $ResourceGroupName = $defaultRG }
        }
    }
    
    if (-not $StorageAccountName) {
        $defaultSA = if ($existingConfig) { $existingConfig.StorageAccountName } else { "altmanzscore$(Get-Random -Minimum 1000 -Maximum 9999)" }
        if ($NoPause) {
            $StorageAccountName = $defaultSA
        }
        else {
            $StorageAccountName = Read-Host "Storage Account Name [$defaultSA]"
            if (-not $StorageAccountName) { $StorageAccountName = $defaultSA }
        }
    }
    
    Write-Host ""
    Write-ColorText "🔧 Setting up Azure Static Website..." "Info"
    $websiteUrl = New-AzureStaticWebsite -ResourceGroupName $ResourceGroupName -StorageAccountName $StorageAccountName -Location $Location
    
    if (-not $websiteUrl) {
        Write-ColorText "❌ Setup failed" "Error"
        exit 1
    }
}

if ($DeployOnly -or (-not $SetupOnly)) {
    # Deploy files
    if ($existingConfig) {
        $ResourceGroupName = $existingConfig.ResourceGroupName
        $StorageAccountName = $existingConfig.StorageAccountName
        $websiteUrl = $existingConfig.WebsiteUrl
    }
    
    if (-not $ResourceGroupName -or -not $StorageAccountName) {
        Write-ColorText "❌ Missing configuration" "Error"
        Write-ColorText "💡 Run setup first: .\deploy_to_azure_storage.ps1 -SetupOnly" "Info"
        Write-ColorText "💡 Or use setup wizard: .\setup_azure_hosting.ps1" "Info"
        exit 1
    }
    
    # Generate dashboards if requested or if files don't exist
    $shouldGenerate = $GenerateFirst -or -not (Test-Path "index.html")
    
    if ($shouldGenerate) {
        if (-not (Invoke-DashboardGeneration)) {
            Write-ColorText "❌ Dashboard generation failed" "Error"
            exit 1
        }
    }
    else {
        Write-ColorText "📊 Using existing dashboard files" "Info"
    }
    
    # Deploy to Azure
    $deploySuccess = Deploy-FilesToAzure -StorageAccountName $StorageAccountName -ResourceGroupName $ResourceGroupName
    
    # Show results
    Show-DeploymentResults -WebsiteUrl $websiteUrl -Success $deploySuccess
    
    if (-not $deploySuccess) {
        exit 1
    }
}

Write-Host ""
Write-Header "Deployment Complete"

if (-not $NoPause) {
    Write-ColorText "Press any key to exit..." "Info"
    if ($Host.UI.RawUI) {
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    else {
        Read-Host "Press Enter to exit"
    }
}

exit 0
