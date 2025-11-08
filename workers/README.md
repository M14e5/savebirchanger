# Cloudflare Workers - Setup Guide

This directory contains two Cloudflare Workers for the Save Birchanger campaign:

1. **Template Generator** - AI-powered campaign letter generation
2. **Facebook Cross-Poster** - Automatic blog-to-Facebook Group posting

Choose the section relevant to your setup needs.

## 🚨 Critical Security Steps

### 1. Revoke the Exposed API Key **IMMEDIATELY**

The OpenAI API key you shared has been exposed and **must be revoked now**:

1. Go to: https://platform.openai.com/api-keys
2. Find the key starting with `sk-proj-R7OU...`
3. Click the **Revoke** button
4. Confirm revocation

**Do this before anything else!**

### 2. Create a New API Key

After revoking the old key:

1. Go to: https://platform.openai.com/api-keys
2. Click **"+ Create new secret key"**
3. Name it something like "Save Birchanger Templates"
4. Copy the new key (starts with `sk-proj-...`)
5. **Store it securely** - you'll need it for deployment

## Prerequisites

Before you begin, make sure you have:

- [Node.js](https://nodejs.org/) installed (v16 or later)
- A [Cloudflare account](https://dash.cloudflare.com/sign-up) (free tier is fine)
- Your new OpenAI API key from step 2 above

## Installation Steps

### Step 1: Install Wrangler (Cloudflare CLI)

Open your terminal and run:

```bash
npm install -g wrangler
```

Verify installation:

```bash
wrangler --version
```

### Step 2: Login to Cloudflare

```bash
wrangler login
```

This will open your browser to authenticate with Cloudflare.

### Step 3: Configure Your Account ID

1. Go to: https://dash.cloudflare.com/
2. Copy your **Account ID** (shown in the sidebar or URL)
3. Edit `wrangler.toml` and uncomment the account_id line:

```toml
account_id = "your-account-id-here"
```

### Step 4: Set Your OpenAI API Key Securely

**IMPORTANT:** Never put your API key directly in code or configuration files!

Run this command to store it securely:

```bash
cd /home/mike/fixrepo/savebirchanger
wrangler secret put OPENAI_API_KEY
```

When prompted, paste your **new** OpenAI API key and press Enter.

### Step 5: Deploy the Worker

From your project directory:

```bash
wrangler deploy
```

You should see output like:

```
Total Upload: XX.XX KiB / gzip: XX.XX KiB
Uploaded template-generator (X.XX sec)
Published template-generator (X.XX sec)
  https://template-generator.YOUR-SUBDOMAIN.workers.dev
```

**Copy this URL** - you'll need it in the next step!

### Step 6: Update the HTML File

1. Open `templates.html`
2. Find this line (around line 1199):

```javascript
const WORKER_API_URL = 'https://template-generator.YOUR-SUBDOMAIN.workers.dev';
```

3. Replace it with your actual Worker URL from Step 5:

```javascript
const WORKER_API_URL = 'https://template-generator.YOUR-SUBDOMAIN.workers.dev';
```

### Step 7: Deploy to Cloudflare Pages

Now that the worker is set up, deploy your updated `templates.html`:

1. Commit your changes:

```bash
git add templates.html
git commit -m "Add AI template generator feature"
git push origin main
```

2. Your site should auto-deploy via Cloudflare Pages (if already set up)
3. If not, manually upload via Cloudflare Pages dashboard

### Step 8: Test the Feature

1. Visit your templates page: `https://your-site.pages.dev/templates.html`
2. Enter the password to unlock the templates
3. Scroll to the top - you should see the "🤖 AI Template Generator" section
4. Select a template type
5. Answer the questions
6. Click "Generate My Template"
7. Verify you get a personalized response!

## Security Features Included

✅ **API Key Protection**: Your OpenAI key is stored as an encrypted Cloudflare secret, never exposed to users

✅ **Rate Limiting**: Built-in protection limiting users to 10 requests per hour

✅ **CORS Protection**: Can be restricted to your domain only (see customization below)

✅ **Input Validation**: Prevents malicious or empty requests

## Optional: Restrict to Your Domain Only

For extra security, you can restrict the API to only work from your domain.

Edit `workers/template-generator.js` and change this line:

```javascript
'Access-Control-Allow-Origin': '*',
```

To:

```javascript
'Access-Control-Allow-Origin': 'https://your-actual-domain.pages.dev',
```

Then redeploy:

```bash
wrangler deploy
```

## Monitoring & Costs

### Check Worker Usage

View your worker's usage and logs:

```bash
wrangler tail
```

Or visit: https://dash.cloudflare.com/ → Workers & Pages → template-generator

### OpenAI Costs

Monitor your OpenAI usage at: https://platform.openai.com/usage

**Estimated costs:**
- GPT-4o: ~$0.005 per template generation
- 100 generations = ~$0.50
- 1000 generations = ~$5.00

The built-in rate limiting helps control costs.

### Cloudflare Costs

Free tier includes:
- 100,000 requests per day
- More than enough for this use case!

## Troubleshooting

### "Worker not found" error

- Make sure you deployed: `wrangler deploy`
- Check the URL in `templates.html` matches your worker URL

### "Failed to generate template" error

- Verify your OpenAI API key is set: `wrangler secret list`
- Check you have credits on your OpenAI account
- View logs: `wrangler tail`

### Rate limit issues

If legitimate users are being rate-limited, you can adjust the limits in `workers/template-generator.js`:

```javascript
const RATE_LIMIT = {
  requests: 20,  // Increase from 10 to 20
  window: 3600000
};
```

Then redeploy: `wrangler deploy`

### CORS errors

If you see CORS errors in the browser console:

1. Check that `WORKER_API_URL` in templates.html is correct
2. Verify the worker is deployed: `wrangler deploy`
3. Check browser console for specific error messages

## Updating the Worker

To make changes to the worker:

1. Edit `workers/template-generator.js`
2. Test locally (optional): `wrangler dev`
3. Deploy: `wrangler deploy`

Changes are live immediately!

## Improving the AI Output

To adjust how the AI generates templates:

### Make it more/less formal

Edit the system prompt in `workers/template-generator.js` (around line 87):

```javascript
const systemPrompt = `You are helping a local resident write a ${templateInfo.name}...
- DO sound passionate but respectful and factual
- ADJUST THIS TO YOUR PREFERENCE
`;
```

### Adjust length

In the OpenAI API call (around line 172):

```javascript
max_tokens: 1000,  // Increase for longer responses
```

### Change creativity level

```javascript
temperature: 0.8,  // Lower (0.3-0.5) = more consistent, Higher (0.8-1.0) = more creative
```

After changes, redeploy: `wrangler deploy`

## Support & Next Steps

### Getting Help

- **Cloudflare Workers Docs**: https://developers.cloudflare.com/workers/
- **OpenAI API Docs**: https://platform.openai.com/docs
- **Wrangler CLI Docs**: https://developers.cloudflare.com/workers/wrangler/

### Enhancements You Could Add

1. **Save templates**: Store generated templates in Cloudflare KV for users to retrieve later
2. **Email integration**: Send generated templates directly to users via email
3. **Analytics**: Track which template types are most popular
4. **A/B testing**: Test different prompts to see which generate better results

---

## Quick Reference Commands

```bash
# Deploy worker
wrangler deploy

# View logs
wrangler tail

# Update API key
wrangler secret put OPENAI_API_KEY

# Test locally
wrangler dev

# Check secrets
wrangler secret list
```

---

**Questions?** Check the troubleshooting section above or review the Cloudflare Workers documentation.

---

# Facebook Cross-Poster - Setup Guide

## Overview

The Facebook Cross-Poster automatically posts new blog posts to your Facebook Group when they're published in Contentful CMS.

**Flow:**
1. Publish blog post in Contentful
2. Contentful sends webhook to Cloudflare Worker
3. Worker formats and posts to Facebook Group
4. Done! ✅

## Quick Start

See **`docs/facebook-crosspost-quickstart.md`** for a step-by-step checklist.

See **`docs/facebook-crosspost-setup.md`** for detailed instructions.

## Prerequisites

- Admin/Moderator access to Facebook Group
- Cloudflare account (already configured)
- Contentful access (Space ID: njsy5rg8z2nk)
- Wrangler CLI installed (`npm install -g wrangler`)

## Setup Summary

### 1. Create Facebook App & Get Credentials

1. Create app at [Meta for Developers](https://developers.facebook.com/)
2. Get Facebook Group ID: `2568902686636114`
3. Generate access token with `publish_to_groups` permission
4. Convert to long-lived token (60 days)

### 2. Deploy Worker

```bash
# Set secrets
wrangler secret put FACEBOOK_ACCESS_TOKEN --config wrangler-facebook.toml
wrangler secret put FACEBOOK_GROUP_ID --config wrangler-facebook.toml
wrangler secret put CONTENTFUL_WEBHOOK_SECRET --config wrangler-facebook.toml

# Deploy
wrangler deploy --config wrangler-facebook.toml --env production
```

### 3. Configure Contentful Webhook

1. Go to Contentful → Settings → Webhooks
2. Add webhook:
   - URL: `https://saveourvillages.co.uk/api/facebook-webhook`
   - Triggers: **Entry.publish** for **blogPost** content type
   - Secret: Same as `CONTENTFUL_WEBHOOK_SECRET`

### 4. Test

1. Create test blog post in Contentful
2. Publish it
3. Check Facebook Group for new post
4. ✅ Done!

## Monitoring

```bash
# View live logs
wrangler tail --config wrangler-facebook.toml --env production

# Test webhook manually
curl -X POST https://saveourvillages.co.uk/api/facebook-webhook \
  -H "Content-Type: application/json" \
  -H "X-Contentful-Topic: ContentManagement.Entry.publish" \
  -d '{"sys":{"contentType":{"sys":{"id":"blogPost"}}},"fields":{"title":{"en-US":"Test"},"slug":{"en-US":"test"},"excerpt":{"en-US":"Test excerpt"}}}'
```

## Maintenance

### Token Refresh (Every 60 Days)

Facebook tokens expire after 60 days. Set a calendar reminder:

```bash
# 1. Generate new token in Graph API Explorer
# 2. Convert to long-lived token
# 3. Update secret:
wrangler secret put FACEBOOK_ACCESS_TOKEN --config wrangler-facebook.toml --env production
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Post not appearing | Check Contentful webhook activity log |
| "Invalid signature" | Verify secret matches in both systems |
| "Token expired" | Refresh access token |
| "Permission denied" | Regenerate token with `publish_to_groups` permission |

**View logs:**
```bash
wrangler tail --config wrangler-facebook.toml --env production
```

## Cost

**Total: $0/month** ✅
- Cloudflare Workers: Free tier
- Facebook Graph API: Free
- Contentful Webhooks: Free

## Files

- `facebook-crosspost.js` - Worker code
- `wrangler-facebook.toml` - Worker configuration
- `docs/facebook-crosspost-setup.md` - Detailed setup guide
- `docs/facebook-crosspost-quickstart.md` - Quick reference

---

## Both Workers - Common Commands

```bash
# Template Generator
wrangler deploy                                    # Deploy
wrangler tail                                      # View logs
wrangler secret put OPENAI_API_KEY                 # Update API key

# Facebook Cross-Poster
wrangler deploy --config wrangler-facebook.toml --env production    # Deploy
wrangler tail --config wrangler-facebook.toml --env production      # View logs
wrangler secret put FACEBOOK_ACCESS_TOKEN --config wrangler-facebook.toml  # Update token
```

---

**Need help?** See the detailed documentation in the `docs/` directory.
