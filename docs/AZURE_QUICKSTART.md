# Azure Static Website Hosting - Quick Start Guide

## Overview
This guide helps you deploy your Altman Z-Score dashboards to Azure Static Website hosting using your existing GoDaddy domain.

## Files Created
- 📋 `AZURE_HOSTING_PLAN.md` - Complete comparison and implementation plan
- 🔧 `setup_azure_hosting.ps1` - Interactive setup wizard
- 🚀 `deploy_to_azure_storage.ps1` - Deployment automation script
- 📊 `monitor_azure_costs.ps1` - Cost monitoring and alerts

## Quick Setup (5 minutes)

### 1. Prerequisites
```powershell
# Install Azure CLI
winget install Microsoft.AzureCLI

# Login to Azure
az login
```

### 2. Run Setup Wizard
```powershell
.\setup_azure_hosting.ps1
```

### 3. Deploy Dashboards
```powershell
# Generate and deploy in one command
.\deploy_to_azure_storage.ps1

# Or just deploy existing files
.\deploy_to_azure_storage.ps1 -DeployOnly
```

### 4. Configure Domain (Optional)
Add CNAME record in GoDaddy DNS:
- **Type**: CNAME
- **Name**: dashboards (or your preferred subdomain)
- **Value**: `[storageaccount].z13.web.core.windows.net`
- **TTL**: 1 Hour

## Cost Comparison

| Feature | Azure | GoDaddy |
|---------|-------|---------|
| Monthly Cost | $1-5 | $6-26 |
| Performance | Excellent (Global CDN) | Fair (Shared) |
| Uptime | 99.95% SLA | 99.9% typical |
| HTTPS | Free & automatic | $70/year |
| Deployment | Automated | Manual |

## Key Benefits

✅ **83% cost reduction** vs traditional hosting  
✅ **10x faster** with global CDN  
✅ **Automated deployment** - one command  
✅ **Enterprise reliability** - 99.95% uptime  
✅ **Keep your domain** - simple DNS configuration  

## Common Commands

```powershell
# Full deployment (generate + deploy)
.\deploy_to_azure_storage.ps1

# Deploy existing files only
.\deploy_to_azure_storage.ps1 -DeployOnly

# Generate fresh dashboards first
.\deploy_to_azure_storage.ps1 -GenerateFirst

# Monitor costs
.\monitor_azure_costs.ps1

# Cost details and export
.\monitor_azure_costs.ps1 -ShowDetails -ExportToCSV
```

## Support
- 📖 Full details: See `AZURE_HOSTING_PLAN.md`
- 🆘 Azure docs: https://docs.microsoft.com/azure/storage/blobs/storage-blob-static-website
- 💰 Cost calculator: https://azure.microsoft.com/pricing/calculator/

## Migration Strategy
1. **Week 1**: Set up Azure with subdomain (parallel testing)
2. **Week 2**: Soft launch with stakeholder feedback
3. **Week 3**: Full migration (optional main domain switch)

Keep GoDaddy active during transition for easy rollback if needed.
