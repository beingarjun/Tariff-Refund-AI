# GitHub Pages Deployment Script for Tariff Refund AI
# This script builds and prepares the app for GitHub Pages deployment

param(
    [switch]$Deploy = $false
)

Write-Host "Building Tariff Refund AI for GitHub Pages..." -ForegroundColor Cyan

# Ensure we're in the right directory
$scriptPath = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Set-Location $scriptPath

# Create dist directory for GitHub Pages
if (!(Test-Path "dist")) {
    New-Item -ItemType Directory -Path "dist" | Out-Null
    Write-Host "Created dist directory" -ForegroundColor Green
}

# Copy static files to dist
Write-Host "Copying static files..." -ForegroundColor Yellow
Copy-Item -Path "app/static/*" -Destination "dist/" -Recurse -Force

# Create index.html with proper paths for GitHub Pages
$repoName = "Tariff-Refund-AI"
$githubPagesPath = "/$repoName"

$indexContent = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tariff Refund AI</title>
    <link rel="stylesheet" href="$githubPagesPath/styles.css">
</head>
<body>
    <div id="app"></div>
    <script src="$githubPagesPath/app.js"></script>
</body>
</html>
"@

Set-Content -Path "dist\index.html" -Value $indexContent
Write-Host "Created index.html for GitHub Pages" -ForegroundColor Green

# Create a simple CNAME file (optional - only if you have a custom domain)
# Set-Content -Path "dist\CNAME" -Value "your-custom-domain.com"

# Create .nojekyll file to prevent Jekyll processing
Set-Content -Path "dist\.nojekyll" -Value ""
Write-Host "Created .nojekyll file" -ForegroundColor Green

if ($Deploy) {
    Write-Host "`nDeploying to GitHub Pages..." -ForegroundColor Cyan
    
    # Check if git is available
    $gitAvailable = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
    
    if ($gitAvailable) {
        # Add all changes
        git add -A
        
        # Commit
        $commitMessage = "Deploy: App update $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        git commit -m $commitMessage
        
        # Push to main branch
        git push origin main
        
        Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
        Write-Host "GitHub Pages will deploy automatically. Check your repository settings." -ForegroundColor Cyan
    }
    else {
        Write-Host "Git is not available. Please commit and push manually." -ForegroundColor Yellow
    }
}
else {
    Write-Host "`nBuild complete! To deploy:" -ForegroundColor Green
    Write-Host "  1. Commit changes: git add -A && git commit -m 'Deploy: App update'" -ForegroundColor White
    Write-Host "  2. Push to GitHub: git push origin main" -ForegroundColor White
    Write-Host "  3. Or run this script with -Deploy flag: .\deploy.ps1 -Deploy" -ForegroundColor White
}

Write-Host "`nGitHub Pages will be available at: https://<username>.github.io/$repoName" -ForegroundColor Cyan
