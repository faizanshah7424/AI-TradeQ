Write-Host "=== Running AI TradeQ Health Verification ===" -ForegroundColor Green

try {
    $backend = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "[1/2] Backend Root Health: OK ($($backend.service) v$($backend.version))" -ForegroundColor Green
} catch {
    Write-Host "[1/2] Backend Root Health: FAILED" -ForegroundColor Red
}

try {
    $apiv1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -Method Get
    Write-Host "[2/2] API v1 Database Health: OK ($($apiv1.database))" -ForegroundColor Green
} catch {
    Write-Host "[2/2] API v1 Health: FAILED" -ForegroundColor Red
}
