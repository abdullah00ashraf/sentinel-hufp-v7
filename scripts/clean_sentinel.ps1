# 🛡️ Sentinel V7.0: Tactical Environment Purge
Write-Host "⚠️  INITIATING DATA PURGE FOR FRESH TRAINING START..." -ForegroundColor Red

# 1. Remove Master Synthetic Datasets
$MasterCSV = "C:\HUFP_SENTINEL_V6\data\master_flood_intelligence_80m.csv"
if (Test-Path $MasterCSV) { 
    Remove-Item $MasterCSV -Force 
    Write-Host "   [CLEANED] Master 80M CSV Removed." -ForegroundColor Yellow 
}

# 2. Clear Neural Brain Assets (Old Models/Scalers)
$BrainDir = "C:\HUFP_SENTINEL_V6\brain\*"
if (Test-Path "C:\HUFP_SENTINEL_V6\brain") {
    Remove-Item $BrainDir -Include *.keras, *.joblib -Force
    Write-Host "   [CLEANED] Previous Neural Weights and Scalers Purged." -ForegroundColor Yellow
}

# 3. Wipe Training Logs and Step-Matrices
$LogFile = "C:\HUFP_SENTINEL_V6\data\training_step_log.csv"
if (Test-Path $LogFile) { 
    Remove-Item $LogFile -Force 
    Write-Host "   [CLEANED] Training Step Logs Wiped." -ForegroundColor Yellow
}

# 4. Remove Spatial Fusion Cache
$FusedJSON = "C:\HUFP_SENTINEL_V6\data\geospatial\fused_intelligence.json"
if (Test-Path $FusedJSON) { 
    Remove-Item $FusedJSON -Force 
    Write-Host "   [CLEANED] Spatial Fusion Cache Removed." -ForegroundColor Yellow
}

# 5. Clear Python Bytecode Cache (__pycache__)
Get-ChildItem -Path "C:\HUFP_SENTINEL_V6" -Filter "__pycache__" -Recurse | Remove-Item -Force -Recurse
Write-Host "   [CLEANED] Python Bytecode Caches Cleared." -ForegroundColor Yellow

Write-Host "`n🚀 ENVIRONMENT READY FOR V7.0 MASTER TRAINING." -ForegroundColor Green