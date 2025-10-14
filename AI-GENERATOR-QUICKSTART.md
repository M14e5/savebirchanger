# AI Template Generator - Quick Start

## 🚨 URGENT: Security First!

**Your API key was exposed in our conversation and must be revoked NOW:**

1. Visit: https://platform.openai.com/api-keys
2. Find key: `sk-proj-R7OU...`
3. Click **Revoke**
4. Create a new key for deployment

## What Was Built

An AI-powered template generator that:
- ✅ Asks users 3-5 personalized questions
- ✅ Generates unique, non-AI-sounding letters using GPT-4o
- ✅ Keeps your API key 100% secure (never exposed to users)
- ✅ Includes rate limiting to prevent abuse
- ✅ Works on your static Cloudflare-hosted site

## Files Created/Modified

### New Files:
- `workers/template-generator.js` - Secure Cloudflare Worker (API proxy)
- `wrangler.toml` - Worker configuration
- `workers/README.md` - Detailed setup instructions
- `AI-GENERATOR-QUICKSTART.md` - This file

### Modified Files:
- `templates.html` - Added AI generator UI at the top

## Quick Deploy (5 minutes)

### 1. Revoke Old Key
https://platform.openai.com/api-keys → Revoke `sk-proj-R7OU...`

### 2. Install Wrangler
```bash
npm install -g wrangler
wrangler login
```

### 3. Configure Account
Edit `wrangler.toml` and add your Cloudflare account ID:
```toml
account_id = "YOUR_ACCOUNT_ID"  # Get from dash.cloudflare.com
```

### 4. Set API Key (Securely!)
```bash
wrangler secret put OPENAI_API_KEY
# Paste your NEW OpenAI key when prompted
```

### 5. Deploy Worker
```bash
wrangler deploy
# Copy the URL that's displayed (e.g., https://template-generator.xxx.workers.dev)
```

### 6. Update HTML
Edit `templates.html` line ~1199:
```javascript
const WORKER_API_URL = 'https://YOUR-ACTUAL-WORKER-URL.workers.dev';
```

### 7. Deploy Site
```bash
git add .
git commit -m "Add AI template generator"
git push origin main
```

Done! Visit your templates page to test.

## How It Works

```
User Browser
    ↓
    1. User selects template type & answers questions
    ↓
Cloudflare Worker (API Proxy)
    ↓
    2. Worker adds your API key (stored securely as secret)
    ↓
OpenAI GPT-4o
    ↓
    3. Generates personalized, natural-sounding letter
    ↓
User Browser
    ↓
    4. User sees result, can copy or regenerate
```

## Template Types Available

1. **Developer Consultation** - Pre-application responses (deadline: Oct 2, 2025)
2. **Planning Objection** - Formal objections to planning applications
3. **Email Councillors/MP** - Contact local representatives
4. **Appeal Representation** - Respond to planning appeals
5. **Local Plan Response** - Object to site allocations

Each has tailored questions to gather the right personal details.

## Features

### For Users:
- Simple 3-step process (pick template → answer questions → get result)
- Personalized output based on their specific situation
- Natural-sounding letters (not obviously AI-generated)
- Copy to clipboard with one click
- Regenerate option if they want a different version

### For You:
- **Secure**: API key never exposed to users
- **Cost-effective**: ~$0.005 per generation (1000 uses = ~$5)
- **Rate limited**: Max 10 requests/user/hour prevents abuse
- **Cloudflare free tier**: 100k requests/day included
- **No server needed**: Fully serverless architecture

## Cost Estimates

| Users/Month | Cost (OpenAI) | Cloudflare Cost |
|-------------|---------------|-----------------|
| 100         | ~$0.50        | Free            |
| 500         | ~$2.50        | Free            |
| 1,000       | ~$5.00        | Free            |
| 10,000      | ~$50.00       | Free            |

Rate limiting helps control unexpected costs.

## Next Steps

### Testing
1. Visit templates page
2. Enter password
3. Try each template type
4. Verify output quality

### Customization
See `workers/README.md` for:
- Adjusting AI personality/tone
- Changing output length
- Modifying rate limits
- Adding custom questions

### Monitoring
- **Worker logs**: `wrangler tail`
- **Worker dashboard**: https://dash.cloudflare.com/ → Workers
- **OpenAI usage**: https://platform.openai.com/usage

## Troubleshooting

**"Failed to generate template"**
- Check OpenAI API key: `wrangler secret list`
- Verify you have OpenAI credits
- View logs: `wrangler tail`

**"Worker not found"**
- Ensure deployed: `wrangler deploy`
- Check URL in templates.html matches worker URL

**Rate limit issues**
- Edit `workers/template-generator.js` line 36
- Increase `requests: 10` to higher number
- Redeploy: `wrangler deploy`

## Full Documentation

See `workers/README.md` for:
- Detailed setup instructions
- Security best practices
- Advanced customization
- Troubleshooting guide
- Enhancement ideas

## Support Resources

- Cloudflare Workers: https://developers.cloudflare.com/workers/
- OpenAI API: https://platform.openai.com/docs
- Wrangler CLI: https://developers.cloudflare.com/workers/wrangler/

---

**Remember**: REVOKE THE OLD API KEY FIRST! Then follow the 7 steps above to deploy securely.
