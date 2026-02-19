# Deployment Guide

## Deploy to Streamlit Cloud

### Prerequisites
- GitHub account
- GitHub Personal Access Token (classic) with `repo` scope

### Steps

#### 1. Create GitHub Repository

```bash
# Option A: Using GitHub CLI (if installed)
gh auth login
gh repo create repo-intelligence --public --source=. --remote=origin --push

# Option B: Manually
# 1. Go to https://github.com/new
# 2. Create a new repository named "repo-intelligence"
# 3. Don't initialize with README (we already have files)
# 4. Copy the repository URL
```

#### 2. Push Code to GitHub

If you created the repo manually:

```bash
git remote add origin https://github.com/YOUR_USERNAME/repo-intelligence.git
git branch -M main
git push -u origin main
```

#### 3. Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `YOUR_USERNAME/repo-intelligence`
5. Set main file path: `app.py`
6. Click "Deploy"

#### 4. Add GitHub Token in Streamlit Cloud

1. In your deployed app dashboard, click "Settings" → "Secrets"
2. Add your GitHub token:

```toml
GITHUB_TOKEN = "ghp_your_token_here"
```

3. Save and the app will restart automatically

### Alternative: Deploy with Hugging Face Token (Optional)

If you want to enable AI features later:

```toml
GITHUB_TOKEN = "ghp_your_github_token"
HF_TOKEN = "hf_your_huggingface_token"
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.streamlit/secrets.toml`:
```toml
GITHUB_TOKEN = "your_token_here"
```

3. Run the app:
```bash
streamlit run app.py
```

## Environment Variables

The app supports these configurations:

- `GITHUB_TOKEN` - **Required**: GitHub Personal Access Token
- `HF_TOKEN` - *Optional*: Hugging Face API token (for AI features, currently disabled)

## Troubleshooting

### GitHub API Rate Limits
- Without authentication: 60 requests/hour
- With authentication: 5,000 requests/hour

### Streamlit Cloud Issues
- Check deployment logs in Streamlit Cloud dashboard
- Verify secrets are properly configured
- Ensure requirements.txt is up to date

### AI Features Not Working
- AI features are currently disabled due to Hugging Face infrastructure changes
- The app works perfectly with static semantic analysis
- Future updates may add Google Gemini or OpenAI integration
