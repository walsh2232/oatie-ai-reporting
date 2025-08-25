# GitHub App Setup for Increased API Limits

## Why GitHub Apps?
- **15,000 requests/hour** vs 5,000 for personal tokens
- Better security with granular permissions
- Designed for automation and CI/CD

## Setup Instructions

### 1. Create GitHub App
1. Go to GitHub → Settings → Developer settings → GitHub Apps
2. Click "New GitHub App"
3. Fill in details:
   - **App name**: `Oatie AI Development Assistant`
   - **Homepage URL**: `https://github.com/walsh2232/oatie-ai-reporting`
   - **Description**: `AI-powered development assistant for Oracle BI Publisher integration`

### 2. Configure Permissions
Set these **Repository permissions**:
- **Contents**: Read & write
- **Issues**: Read & write  
- **Pull requests**: Read & write
- **Metadata**: Read
- **Actions**: Read

### 3. Install App
1. After creation, click "Install App"
2. Choose "Only select repositories"
3. Select `walsh2232/oatie-ai-reporting`

### 4. Generate Private Key
1. In app settings, scroll to "Private keys"
2. Click "Generate a private key"
3. Download the `.pem` file
4. Store securely (never commit to repo)

### 5. Get App Credentials
Note these values from your app:
- **App ID**: Found in app settings
- **Installation ID**: Found in installed apps
- **Private Key**: The downloaded `.pem` file

## Environment Variables
Create `.env` file (DO NOT COMMIT):
```env
GITHUB_APP_ID=your_app_id
GITHUB_INSTALLATION_ID=your_installation_id
GITHUB_PRIVATE_KEY_PATH=path/to/private-key.pem
```

## Usage Example
```typescript
import { App } from '@octokit/app';

const app = new App({
  appId: process.env.GITHUB_APP_ID,
  privateKey: fs.readFileSync(process.env.GITHUB_PRIVATE_KEY_PATH),
});

const octokit = await app.getInstallationOctokit(
  process.env.GITHUB_INSTALLATION_ID
);
```
