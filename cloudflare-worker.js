// PostHog Cloudflare Worker Proxy
// This worker proxies PostHog analytics requests to prevent ad-blocker blocking
// Deploy this to Cloudflare Workers and route to ph.saveourvillages.co.uk

const API_HOST = "eu.i.posthog.com";
const ASSET_HOST = "eu-assets.i.posthog.com";

export default {
  async fetch(request) {
    const url = new URL(request.url);

    // Handle OPTIONS request for CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
          "Access-Control-Max-Age": "86400",
        },
      });
    }

    // Route asset requests (JavaScript files, etc.) to the asset host
    if (url.pathname.startsWith('/static/')) {
      url.hostname = ASSET_HOST;
    } else {
      // All other requests go to the API host
      url.hostname = API_HOST;
    }

    url.protocol = "https";

    // Create new request with the modified URL
    const newRequest = new Request(url.toString(), {
      method: request.method,
      headers: request.headers,
      body: request.body,
    });

    // Fetch from PostHog servers
    const response = await fetch(newRequest);

    // Clone response and add CORS headers
    const newResponse = new Response(response.body, response);
    newResponse.headers.set("Access-Control-Allow-Origin", "*");

    return newResponse;
  },
};
