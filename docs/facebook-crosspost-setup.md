# Facebook Cross-Posting Setup Guide

This guide explains how to set up automatic cross-posting from your Contentful blog to the Save Birchanger Facebook Group.

## Architecture Overview

When you publish a new blog post in Contentful:
1. **Contentful** sends a webhook to your Cloudflare Worker
2. **Cloudflare Worker** (`facebook-crosspost.js`) verifies the webhook, extracts post data, and formats it
3. **Facebook Graph API** receives the formatted post and publishes it to your Facebook Group
4. Your community sees the new post instantly in the Facebook Group!

---

## Setup Steps

### 1. Create Facebook App (One-Time Setup)

You need a Facebook App to get API access credentials.

#### A. Create the App

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click **"My Apps"** → **"Create App"**
3. Choose **"Other"** as use case
4. Choose **"Business"** as app type
5. Fill in:
   - **App Name**: "Save Birchanger Blog Crossposter" (or similar)
   - **App Contact Email**: Your email
6. Click **"Create App"**

#### B. Configure App Permissions

1. In your app dashboard, go to **"Add Products"**
2. Find **"Facebook Login"** and click **"Set Up"**
3. In the left sidebar, go to **Settings → Basic**
4. Add your domain: `saveourvillages.co.uk`
5. Save changes

---

### 2. Get Facebook Group ID

You need the numeric ID of your Facebook Group.

#### Option A: From Group URL
If your group URL is `facebook.com/groups/2568902686636114`, the ID is `2568902686636114`.

#### Option B: Using Graph API Explorer
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. In the query field, enter: `/me/groups`
4. Click **"Generate Access Token"** and grant permissions
5. Click **"Submit"**
6. Find your group in the results and copy its `id`

**Save this ID** - you'll need it later as `FACEBOOK_GROUP_ID`.

---

### 3. Generate Access Token

You need a long-lived access token to post to the group.

#### A. Get User Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your Facebook App from the dropdown
3. Click **"Generate Access Token"**
4. In the permissions dialog, add these permissions:
   - `groups_access_member_info`
   - `publish_to_groups`
5. Click **"Generate Access Token"** and authorize

#### B. Convert to Long-Lived Token (60 days)

**Important**: User tokens expire quickly. Convert to long-lived token:

```bash
# Replace with your values:
# - APP_ID: Your app ID (from app dashboard)
# - APP_SECRET: Your app secret (Settings → Basic → App Secret)
# - SHORT_LIVED_TOKEN: The token from Graph API Explorer

curl "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN"
```

Response will include `access_token` - **save this!**

#### C. Verify Token Permissions

```bash
# Check token validity and permissions
curl "https://graph.facebook.com/v21.0/me/permissions?access_token=YOUR_ACCESS_TOKEN"
```

Ensure `publish_to_groups` and `groups_access_member_info` are granted.

---

### 4. Deploy Cloudflare Worker

#### A. Install Wrangler CLI (if not already installed)

```bash
npm install -g wrangler
```

#### B. Login to Cloudflare

```bash
wrangler login
```

#### C. Set Environment Secrets

Store your sensitive credentials securely:

```bash
# Set Facebook Access Token
wrangler secret put FACEBOOK_ACCESS_TOKEN --config wrangler-facebook.toml
# Paste your long-lived token when prompted

# Set Facebook Group ID
wrangler secret put FACEBOOK_GROUP_ID --config wrangler-facebook.toml
# Paste your group ID (e.g., 2568902686636114)

# Set Contentful Webhook Secret (generate a random string)
wrangler secret put CONTENTFUL_WEBHOOK_SECRET --config wrangler-facebook.toml
# Paste a random secret (e.g., openssl rand -base64 32)
```

#### D. Deploy the Worker

```bash
# Deploy to production
wrangler deploy --config wrangler-facebook.toml --env production
```

You'll see output like:
```
Published facebook-crosspost
  https://facebook-crosspost.YOUR_ACCOUNT.workers.dev
  saveourvillages.co.uk/api/facebook-webhook
```

**Copy the webhook URL** - you'll need it for Contentful configuration.

---

### 5. Configure Contentful Webhook

Connect Contentful to your Cloudflare Worker.

#### A. Create Webhook in Contentful

1. Log into [Contentful](https://app.contentful.com/)
2. Go to your space: **njsy5rg8z2nk**
3. Click **Settings** → **Webhooks**
4. Click **"Add Webhook"**

#### B. Configure Webhook Settings

Fill in:

- **Name**: "Facebook Group Cross-Poster"
- **URL**: `https://saveourvillages.co.uk/api/facebook-webhook`
- **Triggers**:
  - ✅ **Select specific triggering events**
  - ✅ **Publish** (under Entry)
  - ✅ Only select `blogPost` content type
- **Headers**:
  - Add custom header (optional, for debugging):
    - Key: `X-Custom-Source`
    - Value: `Contentful`
- **Content type**: Select **"blogPost"**
- **Secret**: Paste the same secret you used in `CONTENTFUL_WEBHOOK_SECRET`

#### C. Save and Test

1. Click **"Save"**
2. In the webhook list, click your webhook
3. Scroll down to **"Activity Log"**
4. Click **"Trigger Test"** to send a test webhook
5. Check if it shows success (green checkmark)

---

## Testing

### Test the Complete Flow

1. **Create a test blog post** in Contentful:
   - Go to **Content** → **Add Entry** → **Blog Post**
   - Fill in:
     - Title: "Test Post - Please Ignore"
     - Slug: "test-post"
     - Excerpt: "This is a test of the automated cross-posting system."
     - Featured Image: Upload any image
   - Click **"Publish"**

2. **Check Facebook Group**:
   - Go to your Facebook Group
   - You should see a new post with:
     - Title
     - Excerpt
     - Link to blog post
     - Featured image (preview)

3. **Check Cloudflare Logs** (if issues):
   ```bash
   wrangler tail --config wrangler-facebook.toml --env production
   ```

4. **Check Contentful Activity Log**:
   - Settings → Webhooks → Your webhook → Activity Log
   - Should show successful delivery (HTTP 200)

---

## Token Maintenance

### Token Expiration

Facebook User Access Tokens expire after **60 days**. You'll need to refresh them periodically.

#### Set a Calendar Reminder

Set a reminder for **55 days from today** to refresh your token.

#### Refresh Token Process

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Click **"Generate Access Token"** (same permissions: `groups_access_member_info`, `publish_to_groups`)
4. Convert to long-lived token (see Step 3B above)
5. Update the secret:
   ```bash
   wrangler secret put FACEBOOK_ACCESS_TOKEN --config wrangler-facebook.toml --env production
   ```

#### Automation Alternative (Advanced)

For a permanent solution, you can:
- Use a **Page Access Token** instead (never expires, but requires a Facebook Page)
- Use **Business Integration** with permanent tokens
- Set up a **refresh automation** using Cloudflare Scheduled Workers

---

## Troubleshooting

### Post Not Appearing in Facebook Group

**Check Contentful Webhook Activity Log**:
1. Settings → Webhooks → Facebook Group Cross-Poster → Activity Log
2. Look for errors (red X)
3. Click **"View Details"** to see error message

**Check Cloudflare Logs**:
```bash
wrangler tail --config wrangler-facebook.toml --env production
```

Publish a test post and watch the logs in real-time.

**Common Issues**:

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid webhook signature` | Secret mismatch | Ensure same secret in Cloudflare and Contentful |
| `FACEBOOK_ACCESS_TOKEN not configured` | Token not set | Run `wrangler secret put FACEBOOK_ACCESS_TOKEN ...` |
| `OAuthException` | Token expired or invalid | Refresh token (see Token Maintenance) |
| `Insufficient permissions` | Missing Graph API permissions | Regenerate token with correct permissions |
| `Group not found` | Wrong Group ID | Verify Group ID (see Step 2) |

### Test Webhook Manually

Send a test webhook using `curl`:

```bash
curl -X POST https://saveourvillages.co.uk/api/facebook-webhook \
  -H "Content-Type: application/json" \
  -H "X-Contentful-Topic: ContentManagement.Entry.publish" \
  -d '{
    "sys": {
      "contentType": {
        "sys": {
          "id": "blogPost"
        }
      }
    },
    "fields": {
      "title": {
        "en-US": "Test Post"
      },
      "slug": {
        "en-US": "test-post"
      },
      "excerpt": {
        "en-US": "This is a test excerpt."
      }
    }
  }'
```

### Verify Facebook API Permissions

Check if your token has the right permissions:

```bash
curl "https://graph.facebook.com/v21.0/me/permissions?access_token=YOUR_TOKEN"
```

Should return:
```json
{
  "data": [
    {
      "permission": "groups_access_member_info",
      "status": "granted"
    },
    {
      "permission": "publish_to_groups",
      "status": "granted"
    }
  ]
}
```

---

## Pausing/Resuming Cross-Posting

### Pause Cross-Posting

**Option 1: Disable Contentful Webhook**
1. Go to Contentful: Settings → Webhooks
2. Find "Facebook Group Cross-Poster"
3. Toggle it **OFF** (disable)

**Option 2: Delete Worker Route**
```bash
# Temporarily remove the route
wrangler deploy --config wrangler-facebook.toml --env production --routes=[]
```

### Resume Cross-Posting

**Option 1: Re-enable Webhook**
1. Go to Contentful: Settings → Webhooks
2. Toggle webhook back **ON**

**Option 2: Restore Worker Route**
```bash
# Re-deploy with routes
wrangler deploy --config wrangler-facebook.toml --env production
```

---

## Cost & Limits

### Cloudflare Workers

- **Free Tier**: 100,000 requests/day
- **Typical Usage**: ~1 request per blog post published
- **Cost**: **FREE** for typical usage

### Facebook Graph API

- **Rate Limits**: 200 calls/hour (user token), 4800 calls/hour (app token)
- **Typical Usage**: ~1 call per blog post published
- **Cost**: **FREE**

### Contentful Webhooks

- **Webhooks**: Unlimited on all plans
- **Cost**: **FREE**

**Total Cost**: **$0/month** 🎉

---

## Security Considerations

### Secrets Management

✅ **DO**:
- Store secrets using `wrangler secret put`
- Use webhook signature verification
- Use HTTPS for all communications

❌ **DON'T**:
- Commit secrets to git
- Share access tokens publicly
- Disable webhook signature verification in production

### Access Control

- Only grant `publish_to_groups` permission (not admin permissions)
- Use a Facebook account with **Admin** or **Moderator** role in the group
- Regularly rotate access tokens

---

## Support & Resources

- [Facebook Graph API Documentation](https://developers.facebook.com/docs/graph-api/)
- [Contentful Webhooks Documentation](https://www.contentful.com/developers/docs/webhooks/)
- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)

---

**Questions?** Check the troubleshooting section or consult the documentation links above.
