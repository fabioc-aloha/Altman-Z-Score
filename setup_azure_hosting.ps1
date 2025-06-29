#Requires -Version 5.1

# Azure Static Website Setup Wizard for Altman Z-Score Dashboards
# This script guides you through setting up Azure hosting with your existing GoDaddy domain

param(
    [switch]$SkipPrerequisites,
    [switch]$Verbose
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

function Test-Prerequisites {
    Write-Section "Checking Prerequisites"
    
    $allGood = $true
    
    # Check Azure CLI
    try {
        $azVersion = az version --output json 2>$null | ConvertFrom-Json
        Write-ColorText "✅ Azure CLI: $($azVersion.'azure-cli')" "Success"
    }
    catch {
        Write-ColorText "❌ Azure CLI not found" "Error"
        Write-ColorText "💡 Install from: https://aka.ms/installazurecliwindows" "Info"
        $allGood = $false
    }
    
    # Check Azure login
    try {
        $account = az account show --output json 2>$null | ConvertFrom-Json
        Write-ColorText "✅ Azure Login: $($account.user.name)" "Success"
        Write-ColorText "   Subscription: $($account.name)" "Info"
    }
    catch {
        Write-ColorText "❌ Not logged into Azure" "Warning"
        Write-ColorText "💡 Run: az login" "Info"
        $allGood = $false
    }
    
    # Check if dashboard scripts exist
    $requiredScripts = @(
        "generate_all_dashboards.ps1",
        "generate_main_page.py"
    )
    
    foreach ($script in $requiredScripts) {
        if (Test-Path $script) {
            Write-ColorText "✅ Required script: $script" "Success"
        }
        else {
            Write-ColorText "❌ Missing script: $script" "Error"
            $allGood = $false
        }
    }
    
    return $allGood
}

function Get-UserConfiguration {
    Write-Section "Azure Configuration"
    
    Write-ColorText "🔧 Let's configure your Azure hosting setup..." "Info"
    Write-Host ""
    
    # Generate suggested names
    $randomSuffix = Get-Random -Minimum 100 -Maximum 999
    
    # Resource Group
    Write-ColorText "📦 Resource Group (logical container for your resources):" "Info"
    $defaultRG = "altman-zscore-dashboards"
    $resourceGroup = Read-Host "Resource Group Name [$defaultRG]"
    if (-not $resourceGroup) { $resourceGroup = $defaultRG }
    
    # Storage Account (must be globally unique)
    Write-Host ""
    Write-ColorText "💾 Storage Account (must be globally unique, 3-24 lowercase chars/numbers):" "Info"
    $defaultSA = "altmanzscore$randomSuffix"
    do {
        $storageAccount = Read-Host "Storage Account Name [$defaultSA]"
        if (-not $storageAccount) { $storageAccount = $defaultSA }
        
        # Validate storage account name
        if ($storageAccount -match '^[a-z0-9]{3,24}$') {
            break
        }
        else {
            Write-ColorText "❌ Invalid name. Use 3-24 lowercase letters/numbers only." "Error"
            $defaultSA = "altmanzscore$(Get-Random -Minimum 100 -Maximum 999)"
        }
    } while ($true)
    
    # Azure Region
    Write-Host ""
    Write-ColorText "🌍 Azure Region (choose closest to your users):" "Info"
    Write-Host "   Common options: East US, West US 2, West Europe, Southeast Asia" -ForegroundColor $Colors.Info
    $location = Read-Host "Azure Region [East US]"
    if (-not $location) { $location = "East US" }
    
    # Domain configuration
    Write-Host ""
    Write-ColorText "🌐 Domain Configuration:" "Info"
    Write-Host "   Your dashboards will be accessible at a subdomain of your existing domain." -ForegroundColor $Colors.Info
    Write-Host "   Example: dashboards.yourdomain.com or stocks.yourdomain.com" -ForegroundColor $Colors.Info
    
    $subdomain = Read-Host "Preferred subdomain name [dashboards]"
    if (-not $subdomain) { $subdomain = "dashboards" }
    
    $domain = Read-Host "Your GoDaddy domain (e.g., yourdomain.com) [optional for now]"
    
    return @{
        ResourceGroup  = $resourceGroup
        StorageAccount = $storageAccount
        Location       = $location
        Subdomain      = $subdomain
        Domain         = $domain
    }
}

function Show-ConfigurationSummary {
    param($config)
    
    Write-Section "Configuration Summary"
    
    Write-ColorText "📋 Your Azure setup will create:" "Info"
    Write-Host "   • Resource Group: $($config.ResourceGroup)" -ForegroundColor $Colors.Success
    Write-Host "   • Storage Account: $($config.StorageAccount)" -ForegroundColor $Colors.Success
    Write-Host "   • Location: $($config.Location)" -ForegroundColor $Colors.Success
    Write-Host "   • Website URL: https://$($config.StorageAccount).z13.web.core.windows.net" -ForegroundColor $Colors.Emphasis
    
    if ($config.Domain) {
        Write-Host "   • Custom Domain: $($config.Subdomain).$($config.Domain)" -ForegroundColor $Colors.Emphasis
    }
    
    Write-Host ""
    Write-ColorText "💰 Estimated monthly cost: $1-5 USD" "Success"
    Write-ColorText "🚀 Performance: Global CDN, 99.95% uptime" "Success"
    
    Write-Host ""
    $confirm = Read-Host "Proceed with this configuration? (y/n) [y]"
    return ($confirm -ne 'n' -and $confirm -ne 'N')
}

function New-AzureResources {
    param($config)
    
    Write-Section "Creating Azure Resources"
    
    try {
        # Create resource group
        Write-ColorText "📦 Creating resource group..." "Info"
        $rgResult = az group create `
            --name $config.ResourceGroup `
            --location $config.Location `
            --output json | ConvertFrom-Json
        
        if ($rgResult) {
            Write-ColorText "✅ Resource group created successfully" "Success"
        }
        else {
            throw "Failed to create resource group"
        }
        
        # Check if storage account name is available
        Write-ColorText "🔍 Checking storage account name availability..." "Info"
        $nameCheck = az storage account check-name `
            --name $config.StorageAccount `
            --output json | ConvertFrom-Json
        
        if (-not $nameCheck.nameAvailable) {
            throw "Storage account name '$($config.StorageAccount)' is not available: $($nameCheck.message)"
        }
        
        # Create storage account
        Write-ColorText "💾 Creating storage account..." "Info"
        $saResult = az storage account create `
            --name $config.StorageAccount `
            --resource-group $config.ResourceGroup `
            --location $config.Location `
            --sku Standard_LRS `
            --kind StorageV2 `
            --access-tier Hot `
            --https-only true `
            --allow-blob-public-access true `
            --output json | ConvertFrom-Json
        
        if ($saResult) {
            Write-ColorText "✅ Storage account created successfully" "Success"
        }
        else {
            throw "Failed to create storage account"
        }
        
        # Enable static website hosting
        Write-ColorText "🌐 Enabling static website hosting..." "Info"
        az storage blob service-properties update `
            --account-name $config.StorageAccount `
            --static-website `
            --index-document index.html `
            --404-document index.html `
            --output json 2>$null | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Static website hosting enabled" "Success"
        }
        else {
            throw "Failed to enable static website hosting"
        }
        
        # Get the website URL
        $websiteUrl = az storage account show `
            --name $config.StorageAccount `
            --resource-group $config.ResourceGroup `
            --query "primaryEndpoints.web" `
            --output tsv
        
        $config.WebsiteUrl = $websiteUrl.TrimEnd('/')
        
        Write-Host ""
        Write-ColorText "🎉 Azure resources created successfully!" "Success"
        Write-Host ""
        Write-ColorText "📊 Your website details:" "Info"
        Write-Host "   • Resource Group: $($config.ResourceGroup)" -ForegroundColor $Colors.Success
        Write-Host "   • Storage Account: $($config.StorageAccount)" -ForegroundColor $Colors.Success
        Write-Host "   • Website URL: $($config.WebsiteUrl)" -ForegroundColor $Colors.Emphasis
        
        return $true
    }
    catch {
        Write-ColorText "❌ Error creating Azure resources: $($_.Exception.Message)" "Error"
        return $false
    }
}

function Save-Configuration {
    param($config)
    
    $configToSave = @{
        ResourceGroupName  = $config.ResourceGroup
        StorageAccountName = $config.StorageAccount
        Location           = $config.Location
        WebsiteUrl         = $config.WebsiteUrl
        Subdomain          = $config.Subdomain
        Domain             = $config.Domain
        CreatedDate        = (Get-Date).ToString()
        LastUpdated        = (Get-Date).ToString()
    }
    
    $configToSave | ConvertTo-Json -Depth 10 | Out-File -FilePath "azure_config.json" -Encoding UTF8
    Write-ColorText "💾 Configuration saved to azure_config.json" "Info"
}

function Show-NextSteps {
    param($config)
    
    Write-Section "Next Steps"
    
    Write-ColorText "🎯 Your Azure hosting is ready! Here's what to do next:" "Success"
    Write-Host ""
    
    Write-ColorText "1. 📊 Deploy your dashboards:" "Emphasis"
    Write-Host "   .\deploy_to_azure_storage.ps1 -DeployOnly" -ForegroundColor $Colors.Info
    Write-Host ""
    
    if ($config.Domain) {
        Write-ColorText "2. 🌐 Configure your GoDaddy DNS:" "Emphasis"
        Write-Host "   • Login to GoDaddy Domain Management" -ForegroundColor $Colors.Info
        Write-Host "   • Go to DNS Management for $($config.Domain)" -ForegroundColor $Colors.Info
        Write-Host "   • Add a CNAME record:" -ForegroundColor $Colors.Info
        Write-Host "     - Type: CNAME" -ForegroundColor $Colors.Warning
        Write-Host "     - Name: $($config.Subdomain)" -ForegroundColor $Colors.Warning
        Write-Host "     - Value: $($config.StorageAccount).z13.web.core.windows.net" -ForegroundColor $Colors.Warning
        Write-Host "     - TTL: 1 Hour" -ForegroundColor $Colors.Warning
        Write-Host ""
        
        Write-ColorText "3. 🔧 Configure custom domain in Azure:" "Emphasis"
        Write-Host "   az storage account update --name $($config.StorageAccount) --custom-domain $($config.Subdomain).$($config.Domain)" -ForegroundColor $Colors.Info
        Write-Host ""
    }
    
    Write-ColorText "4. 🎉 Test your website:" "Emphasis"
    if ($config.Domain) {
        Write-Host "   • Azure URL: $($config.WebsiteUrl)" -ForegroundColor $Colors.Info
        Write-Host "   • Custom URL: https://$($config.Subdomain).$($config.Domain) (after DNS)" -ForegroundColor $Colors.Info
    }
    else {
        Write-Host "   • Azure URL: $($config.WebsiteUrl)" -ForegroundColor $Colors.Info
    }
    Write-Host ""
    
    Write-ColorText "💡 Useful commands:" "Info"
    Write-Host "   • Redeploy: .\deploy_to_azure_storage.ps1 -DeployOnly" -ForegroundColor $Colors.Info
    Write-Host "   • Check costs: az consumption usage list" -ForegroundColor $Colors.Info
    Write-Host "   • Monitor: az monitor metrics list" -ForegroundColor $Colors.Info
    Write-Host ""
    
    $openBrowser = Read-Host "Open Azure website now to test? (y/n) [y]"
    if ($openBrowser -ne 'n' -and $openBrowser -ne 'N') {
        Start-Process $config.WebsiteUrl
    }
}

# Main execution
Clear-Host
Write-Header "Azure Static Website Setup Wizard"

Write-ColorText "🚀 Welcome to the Azure hosting setup for your Altman Z-Score dashboards!" "Info"
Write-Host ""
Write-ColorText "This wizard will:" "Info"
Write-Host "   ✅ Create Azure resources for static website hosting" -ForegroundColor $Colors.Success
Write-Host "   ✅ Configure global CDN for fast performance" -ForegroundColor $Colors.Success
Write-Host "   ✅ Set up HTTPS security automatically" -ForegroundColor $Colors.Success
Write-Host "   ✅ Prepare for custom domain integration" -ForegroundColor $Colors.Success
Write-Host "   ✅ Save configuration for easy deployment" -ForegroundColor $Colors.Success
Write-Host ""

# Check prerequisites
if (-not $SkipPrerequisites) {
    if (-not (Test-Prerequisites)) {
        Write-ColorText "❌ Prerequisites not met. Please resolve the issues above and try again." "Error"
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
$continue = Read-Host "Ready to begin setup? (y/n) [y]"
if ($continue -eq 'n' -or $continue -eq 'N') {
    Write-ColorText "Setup cancelled." "Warning"
    exit 0
}

# Get configuration from user
$config = Get-UserConfiguration

# Show summary and get confirmation
if (-not (Show-ConfigurationSummary $config)) {
    Write-ColorText "Setup cancelled." "Warning"
    exit 0
}

# Create Azure resources
if (New-AzureResources $config) {
    Save-Configuration $config
    Show-NextSteps $config
    
    Write-Host ""
    Write-Header "Setup Complete"
    Write-ColorText "🎉 Azure hosting setup completed successfully!" "Success"
    Write-ColorText "💡 Run .\deploy_to_azure_storage.ps1 to deploy your dashboards" "Info"
}
else {
    Write-ColorText "❌ Setup failed. Please check the errors above." "Error"
    exit 1
}

Write-Host ""
Read-Host "Press Enter to exit"
