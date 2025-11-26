$ErrorActionPreference = "Stop"

Write-Host "--- Docker Hub Image Push Script ---" -ForegroundColor Cyan

# 1. Get Docker Hub Username
$username = Read-Host -Prompt 'Please enter your Docker Hub username'
if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "Username cannot be empty." -ForegroundColor Red
    exit 1
}

$imageName = "$username/antigravity-rag-web:latest"

# 2. Login
Write-Host "`nLogging in to Docker Hub..." -ForegroundColor Yellow
docker login
if ($LASTEXITCODE -ne 0) {
    Write-Host "Login failed." -ForegroundColor Red
    exit 1
}

# 3. Build
Write-Host "`nBuilding image: $imageName..." -ForegroundColor Yellow
docker build -t $imageName .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed." -ForegroundColor Red
    exit 1
}

# 4. Push
Write-Host "`nPushing image to Docker Hub..." -ForegroundColor Yellow
docker push $imageName
if ($LASTEXITCODE -ne 0) {
    Write-Host "Push failed." -ForegroundColor Red
    exit 1
}

Write-Host "`nSUCCESS! Image pushed to $imageName" -ForegroundColor Green
Write-Host "Note: The PostgreSQL and Qdrant services will still use their official images defined in docker-compose.yml." -ForegroundColor Gray
