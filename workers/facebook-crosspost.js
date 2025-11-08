/**
 * Cloudflare Worker: Facebook Group Cross-Poster
 * Automatically posts new blog posts to Facebook Group when published in Contentful
 */

/**
 * Verify Contentful webhook signature for security
 * https://www.contentful.com/developers/docs/webhooks/webhook-signatures/
 */
async function verifyWebhookSignature(request, secret) {
  if (!secret) {
    console.warn('CONTENTFUL_WEBHOOK_SECRET not configured - skipping signature verification');
    return true; // Allow during setup, but log warning
  }

  const signature = request.headers.get('X-Contentful-Webhook-Signature');
  if (!signature) {
    console.error('Missing X-Contentful-Webhook-Signature header');
    return false;
  }

  const body = await request.clone().text();

  // Create HMAC SHA-256 signature
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );

  const signatureBuffer = await crypto.subtle.sign(
    'HMAC',
    key,
    encoder.encode(body)
  );

  // Convert to base64
  const hashArray = Array.from(new Uint8Array(signatureBuffer));
  const hashBase64 = btoa(String.fromCharCode.apply(null, hashArray));

  return hashBase64 === signature;
}

/**
 * Extract blog post data from Contentful webhook payload
 */
function extractBlogPostData(webhookPayload) {
  try {
    const { fields, sys } = webhookPayload;

    // Extract key fields
    const title = fields.title?.['en-US'] || 'New Blog Post';
    const slug = fields.slug?.['en-US'] || '';
    const excerpt = fields.excerpt?.['en-US'] || '';

    // Extract featured image URL if available
    let imageUrl = null;
    const featuredImage = fields.featuredImage?.['en-US'];
    if (featuredImage?.fields?.file) {
      const file = featuredImage.fields.file['en-US'];
      imageUrl = file.url ? `https:${file.url}` : null;
    }

    // Build blog post URL
    const blogUrl = `https://saveourvillages.co.uk/blog.html?post=${slug}`;

    return {
      title,
      slug,
      excerpt,
      imageUrl,
      blogUrl,
      publishDate: sys.createdAt
    };
  } catch (error) {
    console.error('Error extracting blog post data:', error);
    throw new Error('Failed to parse Contentful webhook payload');
  }
}

/**
 * Format the Facebook post message
 */
function formatFacebookMessage(postData) {
  const { title, excerpt, blogUrl } = postData;

  // Format: Title + Excerpt + Link
  let message = `${title}\n\n`;

  if (excerpt) {
    message += `${excerpt}\n\n`;
  }

  message += `Read more: ${blogUrl}`;

  return message;
}

/**
 * Post to Facebook Group using Graph API
 * https://developers.facebook.com/docs/graph-api/reference/group/feed/
 */
async function postToFacebookGroup(postData, accessToken, groupId) {
  const message = formatFacebookMessage(postData);
  const { imageUrl } = postData;

  try {
    // Prepare API endpoint
    const apiUrl = `https://graph.facebook.com/v21.0/${groupId}/feed`;

    // Prepare post data
    const formData = new URLSearchParams();
    formData.append('message', message);
    formData.append('access_token', accessToken);

    // Add image if available
    if (imageUrl) {
      formData.append('link', imageUrl); // Facebook will preview the image
    }

    // Make API request
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString()
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Facebook API error:', errorData);
      throw new Error(errorData.error?.message || 'Facebook API request failed');
    }

    const result = await response.json();
    console.log('Successfully posted to Facebook:', result.id);

    return {
      success: true,
      postId: result.id,
      message: 'Successfully cross-posted to Facebook Group'
    };

  } catch (error) {
    console.error('Facebook posting error:', error);
    throw error;
  }
}

/**
 * Main request handler
 */
export default {
  async fetch(request, env) {
    // CORS headers (for testing/debugging)
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, X-Contentful-Webhook-Signature',
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Only allow POST
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    try {
      // Get configuration from environment variables
      const accessToken = env.FACEBOOK_ACCESS_TOKEN;
      const groupId = env.FACEBOOK_GROUP_ID;
      const webhookSecret = env.CONTENTFUL_WEBHOOK_SECRET;

      // Validate configuration
      if (!accessToken) {
        throw new Error('FACEBOOK_ACCESS_TOKEN not configured');
      }
      if (!groupId) {
        throw new Error('FACEBOOK_GROUP_ID not configured');
      }

      // Verify webhook signature (security)
      const isValid = await verifyWebhookSignature(request, webhookSecret);
      if (!isValid) {
        return new Response(JSON.stringify({
          error: 'Invalid webhook signature'
        }), {
          status: 401,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // Parse webhook payload
      const webhookPayload = await request.json();

      // Check if this is a publish event for a blog post
      const topic = request.headers.get('X-Contentful-Topic');
      console.log('Contentful webhook topic:', topic);

      // Only process ContentManagement.Entry.publish events
      if (!topic?.includes('Entry.publish')) {
        return new Response(JSON.stringify({
          message: 'Ignored: Not a publish event',
          topic
        }), {
          status: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // Verify it's a blog post (content type: blogPost)
      const contentType = webhookPayload.sys?.contentType?.sys?.id;
      if (contentType !== 'blogPost') {
        return new Response(JSON.stringify({
          message: 'Ignored: Not a blog post',
          contentType
        }), {
          status: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // Extract blog post data
      const postData = extractBlogPostData(webhookPayload);
      console.log('Processing blog post:', postData.title);

      // Post to Facebook Group
      const result = await postToFacebookGroup(postData, accessToken, groupId);

      return new Response(JSON.stringify({
        success: true,
        message: result.message,
        postId: result.postId,
        blogPost: {
          title: postData.title,
          url: postData.blogUrl
        }
      }), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });

    } catch (error) {
      console.error('Worker error:', error);
      return new Response(JSON.stringify({
        error: error.message || 'Failed to process webhook',
        details: error.stack
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
  }
};
