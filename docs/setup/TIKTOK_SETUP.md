# TikTok Integration Setup Guide for Clippy

This guide will help you set up TikTok authentication and upload functionality in Clippy.

## Prerequisites

1. A TikTok Developer Account
2. A registered app on TikTok for Developers
3. Your app's Client Key and Client Secret

## Step 1: Create a TikTok Developer Account

1. Go to [TikTok for Developers](https://developers.tiktok.com/)
2. Click "Login" and sign in with your TikTok account
3. Complete the developer registration process

## Step 2: Create an App

1. Navigate to "Manage apps" in your developer dashboard
2. Click "Create app"
3. Fill in the required information:
   - **App name**: Clippy (or your preferred name)
   - **App description**: AI-powered viral clip generator with direct TikTok upload
   - **Category**: Select appropriate category (e.g., "Creator Tools")
   - **Platform**: Select "Web"
   - **Website URL**: Your Clippy instance URL

## Step 3: Configure OAuth Settings

1. In your app settings, navigate to "Login Kit"
2. Enable "Configure for Web"
3. Add redirect URIs:
   - For local development: `http://localhost:5000/api/auth/tiktok/callback`
   - For production: `https://yourdomain.com/api/auth/tiktok/callback`

## Step 4: Add Required Scopes

1. Navigate to "Manage apps" > Your App > "Scopes"
2. Request the following scopes:
   - `user.info.basic` - Basic user information
   - `video.upload` - Upload videos
   - `video.publish` - Publish videos
   - `video.list` - List user's videos

**Note**: Some scopes require approval from TikTok. Submit your app for review with a clear use case.

## Step 5: Configure Content Posting API

1. In your app dashboard, add "Content Posting API" as a product
2. Choose your posting mode:
   - **Direct Post**: Videos post directly to TikTok
   - **Upload to Inbox**: Videos go to drafts for user review

## Step 6: Set Up Environment Variables

Add your TikTok credentials to your `.env` file:

```env
# TikTok OAuth Configuration
TIKTOK_CLIENT_KEY=your_client_key_here
TIKTOK_CLIENT_SECRET=your_client_secret_here
```

## Step 7: Run Database Migration

Run the TikTok support migration:

```bash
python migrations/003_tiktok_support.py
```

## Step 8: Test the Integration

1. Restart your Flask server
2. Sign in to Clippy with your Google account
3. Navigate to your profile/settings
4. Click "Connect TikTok Account"
5. Authorize the app on TikTok
6. You should now see TikTok as a connected platform

## Usage

### Uploading to TikTok

When you have a generated clip ready:

1. Click "Continue to Upload"
2. Select "TikTok" as the upload platform
3. Configure your post settings:
   - Title (required)
   - Description with hashtags
   - Privacy level (Public, Friends, Private)
   - Allow comments/duets/stitches
4. Choose upload type:
   - **Direct Post**: Publishes immediately
   - **Save to Drafts**: Sends to TikTok drafts for review

### API Limits and Considerations

1. **Video Requirements**:
   - Format: MP4 with H.264 codec
   - Size: 1KB to 4GB
   - Duration: 3 seconds to 10 minutes
   - Aspect ratio: 9:16 recommended for best results

2. **Upload Limits**:
   - TikTok may impose daily upload limits
   - Respect rate limits to avoid API throttling

3. **Sandbox vs Production**:
   - Sandbox mode has limited functionality
   - Apply for production access for full features

## Troubleshooting

### Common Issues

1. **"Scope not approved" error**:
   - Ensure your app has been approved for required scopes
   - Check your app's approval status in the developer dashboard

2. **Upload fails with "invalid video" error**:
   - Verify video meets TikTok's requirements
   - Check video codec and format

3. **OAuth callback error**:
   - Verify redirect URI matches exactly in app settings
   - Check that client key and secret are correct

### Debug Mode

Enable debug logging for TikTok operations:

```python
import logging
logging.getLogger('auth.tiktok').setLevel(logging.DEBUG)
```

## Security Notes

1. Never commit your TikTok credentials to version control
2. Use environment variables for all sensitive data
3. Implement proper token refresh logic
4. Store tokens encrypted in the database

## Additional Resources

- [TikTok API Documentation](https://developers.tiktok.com/doc/getting-started)
- [Content Posting API Guide](https://developers.tiktok.com/doc/content-posting-api-get-started)
- [OAuth 2.0 Implementation](https://developers.tiktok.com/doc/login-kit-web)
