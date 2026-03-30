# Deployment Guide - GitHub Pages

This project is configured for automatic deployment to GitHub Pages.

## Automatic Deployment (GitHub Actions)

The project includes a GitHub Actions workflow that automatically deploys your app when you push to the `main` branch.

**Setup:**
1. Go to your repository settings
2. Navigate to "Pages" section
3. Select "Deploy from a branch"
4. Choose `gh-pages` branch and `/root` folder
5. Save

The workflow will automatically:
- Build the application
- Run tests
- Deploy to GitHub Pages on every push to `main`

## Manual Deployment (Local)

If you prefer to deploy manually from your machine:

### Windows PowerShell:
```powershell
# Build only
.\deploy.ps1

# Build and deploy
.\deploy.ps1 -Deploy
```

### Bash/Linux/Mac:
```bash
# Build the app
python -m app.main --build

# Manually commit and push
git add -A
git commit -m "Deploy: App update"
git push origin main
```

## GitHub Pages Settings

After first deployment, configure your repository:

1. Go to Settings → Pages
2. **Source**: Deploy from a branch (or GitHub Actions if available)
3. **Branch**: Select `gh-pages` 
4. **Folder**: `/root`
5. Save

Your app will be available at: `https://[username].github.io/Tariff-Refund-AI`

## Troubleshooting

- **Pages not updating**: Check the GitHub Actions tab for workflow errors
- **Blank page**: Ensure the `.nojekyll` file exists in dist folder
- **Asset paths wrong**: Verify the repository name in deploy.ps1 matches your GitHub repo

## Preview Locally

To test the built app locally:
```bash
cd dist
python -m http.server 8000
```

Then visit: `http://localhost:8000`
