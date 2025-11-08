# Facebook Cross-Posting Quick Start

This is a condensed checklist for setting up automatic blog-to-Facebook cross-posting. See `facebook-crosspost-setup.md` for detailed instructions.

## Prerequisites Checklist

- [ ] Admin/Moderator access to Facebook Group (https://www.facebook.com/groups/2568902686636114)
- [ ] Cloudflare account (already configured with account ID: 3661915b96149c595241723b8c45518d)
- [ ] Contentful access (Space ID: njsy5rg8z2nk)
- [ ] Wrangler CLI installed (`npm install -g wrangler`)

---

## Setup Checklist (30 minutes)

### 1. Facebook App Setup (10 min)

- [ ] Go to [Meta for Developers](https://developers.facebook.com/)
- [ ] Create app: **My Apps** → **Create App** → **Other** → **Business**
- [ ] Name: "Save Birchanger Blog Crossposter"
- [ ] Add product: **Facebook Login**
- [ ] Add domain: `saveourvillages.co.uk`

### 2. Get Credentials (10 min)

**Facebook Group ID:**
- [ ] Group ID: `2568902686636114` (from your group URL)

**Access Token:**
- [ ] Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [ ] Select your app
- [ ] Generate token with permissions:
  - `groups_access_member_info`
  - `publish_to_groups`
- [ ] Convert to long-lived token:

```bash
# Replace APP_ID, APP_SECRET, SHORT_LIVED_TOKEN with your values
curl "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN"
```

- [ ] Save the `access_token` from response

**Webhook Secret:**
- [ ] Generate random secret:

```bash
openssl rand -base64 32
```

- [ ] Save this secret for later

### 3. Deploy Worker (5 min)

```bash
# Login to Cloudflare
wrangler login

# Set secrets
wrangler secret put FACEBOOK_ACCESS_TOKEN --config wrangler-facebook.toml
# Paste your long-lived access token

wrangler secret put FACEBOOK_GROUP_ID --config wrangler-facebook.toml
# Paste: 2568902686636114

wrangler secret put CONTENTFUL_WEBHOOK_SECRET --config wrangler-facebook.toml
# Paste your generated secret

# Deploy
wrangler deploy --config wrangler-facebook.toml --env production
```

- [ ] Copy webhook URL from output: `https://saveourvillages.co.uk/api/facebook-webhook`

### 4. Configure Contentful (5 min)

- [ ] Go to [Contentful](https://app.contentful.com/) → Space njsy5rg8z2nk
- [ ] **Settings** → **Webhooks** → **Add Webhook**
- [ ] Configure:
  - Name: "Facebook Group Cross-Poster"
  - URL: `https://saveourvillages.co.uk/api/facebook-webhook`
  - Triggers: **Entry.publish** for **blogPost** content type only
  - Secret: Paste your `CONTENTFUL_WEBHOOK_SECRET`
- [ ] **Save**
- [ ] Click **Trigger Test** to verify

### 5. Test (5 min)

- [ ] Create test blog post in Contentful:
  - Title: "Test Post - Please Ignore"
  - Slug: "test-post"
  - Excerpt: "Testing automatic cross-posting"
  - Add any featured image
- [ ] Publish the post
- [ ] Check Facebook Group for new post
- [ ] Delete test post from Facebook

✅ **Setup Complete!**

---

## Daily Usage

### Publishing a Blog Post

1. Log into Contentful
2. Create new **Blog Post** entry
3. Fill in: title, slug, excerpt, featured image, body
4. Click **Publish**
5. ✅ Post automatically appears in Facebook Group within seconds!

**No additional steps needed!**

---

## Maintenance

### Token Refresh (Every 60 Days)

Set a calendar reminder for 55 days from today:

```bash
# 1. Generate new token in Graph API Explorer (same permissions)
# 2. Convert to long-lived token (see step 2 above)
# 3. Update secret:
wrangler secret put FACEBOOK_ACCESS_TOKEN --config wrangler-facebook.toml --env production
```

---

## Troubleshooting

### Post didn't appear in Facebook Group?

**Check Contentful Webhook Log:**
- Contentful → Settings → Webhooks → Facebook Group Cross-Poster → Activity Log
- Look for errors (red X)

**Check Cloudflare Logs:**
```bash
wrangler tail --config wrangler-facebook.toml --env production
```

Then publish another test post and watch the logs.

**Common fixes:**

| Issue | Fix |
|-------|-----|
| "Invalid signature" | Check secret matches in both Cloudflare and Contentful |
| "Token expired" | Refresh access token (see Maintenance above) |
| "Permission denied" | Regenerate token with correct permissions |

### Test Webhook Manually

```bash
curl -X POST https://saveourvillages.co.uk/api/facebook-webhook \
  -H "Content-Type: application/json" \
  -H "X-Contentful-Topic: ContentManagement.Entry.publish" \
  -d '{"sys":{"contentType":{"sys":{"id":"blogPost"}}},"fields":{"title":{"en-US":"Test"},"slug":{"en-US":"test"},"excerpt":{"en-US":"Test excerpt"}}}'
```

---

## Emergency Controls

### Pause Cross-Posting

**Option 1: Disable in Contentful**
- Settings → Webhooks → Toggle OFF

**Option 2: Delete Worker (nuclear option)**
```bash
wrangler delete --config wrangler-facebook.toml --env production
```

### Resume Cross-Posting

**Option 1: Re-enable in Contentful**
- Settings → Webhooks → Toggle ON

**Option 2: Re-deploy Worker**
```bash
wrangler deploy --config wrangler-facebook.toml --env production
```

---

## Cost

**Total monthly cost: $0** ✅

- Cloudflare Workers: Free tier (100k requests/day, you'll use ~10/month)
- Facebook Graph API: Free (200 calls/hour limit, you'll use ~5/month)
- Contentful Webhooks: Free (unlimited)

---

## Files Reference

### Created Files

- `workers/facebook-crosspost.js` - Cloudflare Worker code
- `wrangler-facebook.toml` - Worker configuration
- `docs/facebook-crosspost-setup.md` - Detailed setup guide
- `docs/facebook-crosspost-quickstart.md` - This file

### Commands Reference

```bash
# Deploy worker
wrangler deploy --config wrangler-facebook.toml --env production

# View logs
wrangler tail --config wrangler-facebook.toml --env production

# Update secret
wrangler secret put SECRET_NAME --config wrangler-facebook.toml --env production

# Test locally (before deploying)
wrangler dev --config wrangler-facebook.toml
```

---

**Need help?** See `docs/facebook-crosspost-setup.md` for detailed instructions and troubleshooting.
