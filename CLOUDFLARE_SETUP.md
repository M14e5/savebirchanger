# PostHog Cloudflare Reverse Proxy Setup Guide

This guide walks you through setting up a Cloudflare Worker to proxy PostHog analytics requests through your own domain (`ph.saveourvillages.co.uk`). This prevents ad blockers from blocking your analytics.

## Why Use a Proxy?

- **Ad-blocker bypass**: Requests appear to come from your domain, not a third-party analytics service
- **Better data collection**: Capture more complete analytics data
- **Privacy-friendly**: Keep data in Europe using PostHog's EU servers

## Prerequisites

- Access to Cloudflare dashboard for `saveourvillages.co.uk`
- Cloudflare Worker code (provided in `cloudflare-worker.js`)

## Step-by-Step Setup

### 1. Create the Cloudflare Worker

1. **Log into Cloudflare Dashboard**
   - Go to https://dash.cloudflare.com
   - Select your account

2. **Navigate to Workers**
   - In the left sidebar, click **Workers & Pages**
   - Click **Create** button
   - Select **Create Worker**

3. **Create and Name Worker**
   - Click **Deploy** to create the worker with a random name (or customize if you prefer)
   - Note: You can name it something like `posthog-proxy`

4. **Edit Worker Code**
   - After deployment, click **Edit code** button
   - Delete all the default "Hello World" code
   - Copy the entire contents of `cloudflare-worker.js` from this repository
   - Paste it into the editor
   - Click **Save and Deploy**

5. **Note Your Worker URL**
   - Your worker will have a URL like: `posthog-proxy.YOUR-SUBDOMAIN.workers.dev`
   - You don't need to access this directly, but it's good to know

### 2. Configure DNS for ph.saveourvillages.co.uk

1. **Go to DNS Settings**
   - In Cloudflare dashboard, click on `saveourvillages.co.uk` domain
   - Navigate to **DNS** > **Records**

2. **Add DNS Record**
   - Click **Add record**
   - Configure as follows:
     - **Type**: `CNAME`
     - **Name**: `ph`
     - **Target**: `saveourvillages.co.uk` (or you can use `@` to reference the apex domain)
     - **Proxy status**: **Proxied** (orange cloud icon should be on)
     - **TTL**: `Auto`
   - Click **Save**

   > **Note**: We're using a dummy CNAME because the Worker route will intercept all requests. The actual target doesn't matter when proxied.

### 3. Add Worker Route

1. **Navigate to Worker Settings**
   - Go to **Workers & Pages**
   - Click on your PostHog proxy worker
   - Go to **Settings** > **Triggers** tab

2. **Add Route**
   - Under **Routes** section, click **Add route**
   - Configure as follows:
     - **Route**: `ph.saveourvillages.co.uk/*`
     - **Worker**: Select your PostHog proxy worker
     - **Zone**: `saveourvillages.co.uk`
   - Click **Save**

   > **Important**: The `/*` wildcard ensures all paths under the subdomain are proxied.

### 4. Test the Worker (Optional but Recommended)

Before updating your website, test that the worker is functioning:

1. Open your browser's Developer Tools (F12)
2. Go to the **Console** tab
3. Run this command:

```javascript
fetch('https://ph.saveourvillages.co.uk/i/v0/e/')
  .then(r => console.log('Status:', r.status))
  .catch(e => console.error('Error:', e));
```

4. You should see `Status: 400` or `Status: 401` (this is normal - PostHog needs valid data)
   - If you get a CORS error or timeout, check your worker configuration

### 5. Update Website Configuration

The `index.html` file has already been updated to use the proxy. The PostHog configuration now uses:

```javascript
posthog.init('phc_bapf3RKKWohziv8014UqPW1ySks6p6NFHLbLZRPGJfz', {
    api_host: 'https://ph.saveourvillages.co.uk',
    // ... other options
});
```

### 6. Deploy and Verify

1. **Deploy your updated website** to production
2. **Open your website** with browser DevTools (F12)
3. **Go to Network tab**
4. **Reload the page**
5. **Look for requests** to `ph.saveourvillages.co.uk`
   - You should see POST requests to paths like `/i/v0/e/` and `/decide/`
   - These should return status 200 OK
6. **Check PostHog Dashboard**
   - Log into your PostHog account at https://eu.i.posthog.com
   - Navigate to your project
   - Verify that events are coming through

## Troubleshooting

### No requests showing up

**Problem**: No requests to `ph.saveourvillages.co.uk` in Network tab

**Solutions**:
- Clear browser cache and reload
- Check that DNS record is properly proxied (orange cloud)
- Verify Worker route is correctly configured
- Wait 5-10 minutes for DNS propagation

### CORS Errors

**Problem**: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solutions**:
- Verify the Worker code includes CORS headers (it should)
- Check that the Worker is deployed (not in draft mode)
- Try clearing Cloudflare cache: Cloudflare Dashboard > Caching > Purge Everything

### 403 or 404 Errors

**Problem**: Requests to proxy subdomain return errors

**Solutions**:
- Verify the Worker route exactly matches: `ph.saveourvillages.co.uk/*`
- Check that DNS record exists for `ph` subdomain
- Ensure proxy is enabled (orange cloud) on DNS record

### Events not showing in PostHog

**Problem**: Requests succeed but no data in PostHog dashboard

**Solutions**:
- Verify your PostHog project API key is correct
- Check that user has accepted analytics cookies (check browser console for PostHog logs)
- Wait 1-2 minutes for events to process
- Check PostHog's live events feed for real-time data

## Monitoring

### Cloudflare Worker Analytics

Monitor your proxy usage:

1. Go to **Workers & Pages** > Your worker
2. Click **Metrics** tab
3. View:
   - Total requests
   - Success rate
   - Errors
   - CPU time

### Free Tier Limits

- **Cloudflare Workers Free Plan**: 100,000 requests/day
- Typical small website usage: 5,000-20,000 requests/day
- Monitor usage to ensure you stay within limits

## Security Notes

- The worker only proxies to PostHog EU servers (hardcoded in the script)
- No sensitive data is logged or stored by the worker
- All requests are forwarded as-is with no modification
- CORS headers allow requests from any origin (adjust if needed)

## Maintenance

### Updating the Worker

If you need to modify the worker code:

1. Go to **Workers & Pages** > Your worker
2. Click **Edit code**
3. Make your changes
4. Click **Save and Deploy**

### Monitoring PostHog Changes

PostHog may occasionally update their API endpoints or asset URLs. Check PostHog's changelog if you notice issues.

## Need Help?

- **PostHog Documentation**: https://posthog.com/docs/advanced/proxy/cloudflare
- **Cloudflare Workers Docs**: https://developers.cloudflare.com/workers/
- **PostHog Support**: https://posthog.com/support

## Quick Reference

```bash
# Key URLs
Worker Dashboard: https://dash.cloudflare.com → Workers & Pages
DNS Settings: https://dash.cloudflare.com → [Your Domain] → DNS
PostHog Dashboard: https://eu.i.posthog.com

# Key Configuration
Proxy Subdomain: ph.saveourvillages.co.uk
Worker Route: ph.saveourvillages.co.uk/*
PostHog EU API: eu.i.posthog.com
PostHog EU Assets: eu-assets.i.posthog.com
```

---

**Setup Complete!** Your PostHog analytics are now proxied through your own domain, making them more resistant to ad blockers while maintaining user privacy.
