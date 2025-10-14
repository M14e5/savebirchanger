/**
 * Cloudflare Worker: AI Template Generator Proxy
 * Securely proxies requests to OpenAI API for generating personalized campaign templates
 */

// Template-specific question sets and prompts
const TEMPLATE_QUESTIONS = {
  'developer-consultation': {
    name: 'Developer Consultation Response',
    questions: [
      'What is your relationship to the area? (e.g., resident for X years, work nearby, use local paths)',
      'What specific views, landmarks, or features of this Green Belt land matter to you?',
      'What is your main concern about this development?',
      'How do you currently use or value this space?',
      'Do you have any specific evidence to share? (e.g., wildlife sightings, photos, route timings)'
    ]
  },
  'planning-objection': {
    name: 'Planning Objection',
    questions: [
      'How long have you lived or worked in this area?',
      'What specific Green Belt purposes does this land serve in your view?',
      'What are your main concerns about the impact? (transport, heritage, ecology, infrastructure)',
      'Have you observed any specific issues with local infrastructure or services?',
      'What makes this location unsuitable for development in your experience?'
    ]
  },
  'email-representatives': {
    name: 'Email to Councillors/MP',
    questions: [
      'How long have you been a resident or worked in this area?',
      'What does this Green Belt land personally mean to you?',
      'What is your top concern about the proposed development?',
      'What would you like your representative to do?'
    ]
  },
  'appeal-representation': {
    name: 'Appeal Representation',
    questions: [
      'How long have you lived in or used this area?',
      'What specific views or paths do you regularly use that would be affected?',
      'What evidence can you provide about the site\'s Green Belt contribution?',
      'What are your concerns about the claimed "sustainability" of this location?'
    ]
  },
  'local-plan': {
    name: 'Local Plan Representation',
    questions: [
      'What is your connection to this area?',
      'Why do you believe this site should not be classified as "grey belt"?',
      'What alternative sites or approaches should the council consider?',
      'What specific policy concerns do you have about this allocation?'
    ]
  }
};

// Rate limiting configuration
const RATE_LIMIT = {
  requests: 10,
  window: 3600000 // 1 hour in milliseconds
};

// In-memory rate limiting (resets when worker restarts - for production use KV or Durable Objects)
const rateLimitMap = new Map();

/**
 * Check rate limit for an IP address
 */
function checkRateLimit(ip) {
  const now = Date.now();
  const userRequests = rateLimitMap.get(ip) || [];

  // Remove old requests outside the time window
  const recentRequests = userRequests.filter(timestamp => now - timestamp < RATE_LIMIT.window);

  if (recentRequests.length >= RATE_LIMIT.requests) {
    return false;
  }

  recentRequests.push(now);
  rateLimitMap.set(ip, recentRequests);
  return true;
}

/**
 * Build the prompt for OpenAI based on template type and user answers
 */
function buildPrompt(templateType, answers, baseTemplate) {
  const templateInfo = TEMPLATE_QUESTIONS[templateType];

  // Build user details from answers
  let userDetails = '';
  templateInfo.questions.forEach((question, index) => {
    if (answers[index] && answers[index].trim()) {
      userDetails += `• ${question}\n  Answer: ${answers[index]}\n`;
    }
  });

  const systemPrompt = `You are helping a local resident write a ${templateInfo.name} for official submission to planning authorities. Your task is to create a personalized, professionally-written representation that sounds authentic and credible.

CRITICAL STYLE REQUIREMENTS:
- Write in a formal but sincere voice appropriate for official planning submissions
- Use clear, direct language - be professional but not overly legalistic
- Vary sentence structure naturally while maintaining formality
- DO NOT use AI clichés: avoid "delve", "moreover", "it is important to note", "in conclusion", "stakeholders"
- DO NOT use flowery or elaborate descriptions
- DO maintain a respectful, factual tone throughout
- DO use the person's specific details naturally woven into the formal structure
- DO keep paragraphs focused and well-organized
- DO use appropriate planning terminology when relevant (e.g., "Green Belt purposes", "openness", "material considerations")

Think of this as a resident making a serious, well-reasoned representation to planning authorities - professional, credible, and grounded in their genuine concerns.`;

  const userPrompt = `Write a personalized ${templateInfo.name} for someone with these details:

${userDetails}

Use this template as a STYLE GUIDE for structure and tone, but make the final output unique and personalized:

${baseTemplate}

CRITICAL REQUIREMENTS:
- Follow the formal, professional tone of the template above
- Incorporate their specific details naturally throughout (NOT just at the start)
- Use their answers to add substance and credibility - these are their genuine observations
- Replace generic placeholder text with contextually appropriate references:
  - Instead of [SITE NAME]: "this Green Belt land", "the proposed site", "the land in question"
  - Instead of [AREA]: "our village", "this area", "the local community"
  - Be specific where they gave specifics, general where appropriate
- Maintain the template's logical structure (opening, substantive points, conclusion)
- Keep the same level of formality and professionalism as the template
- Make each sentence unique - do not copy template sentences verbatim
- Aim for 250-400 words for formal letters/objections, 150-250 for consultation responses
- DO NOT include placeholder text like [NAME], [ADDRESS] - omit signature blocks entirely
- DO NOT add a subject line - start directly with the letter content

Write only the body of the letter/response. Make it professional, credible, and grounded in their specific situation.`;

  return { systemPrompt, userPrompt };
}

/**
 * Get base template content
 */
function getBaseTemplate(templateType) {
  // Base templates - simplified versions for the AI to adapt
  const templates = {
    'developer-consultation': `I am writing to object to the proposed development at this Green Belt site.

This land is not "grey belt" - it strongly serves Green Belt purposes by preventing sprawl, maintaining settlement separation, and contributing to the local landscape and setting.

The development would harm the openness and character of this area. The site is car-dependent with inadequate public transport and walking/cycling routes.

The claimed "Golden Rules" benefits are not transparently secured - the affordable housing uplift lacks clear evidence, and the green space and biodiversity measures appear uncertain.

Please record this as a formal objection and keep me informed.`,

    'planning-objection': `I am writing to object to this planning application.

The site is not "grey belt" and the proposal causes unacceptable harm to Green Belt openness and local character.

Green Belt concerns: This land serves important Green Belt purposes. The development would harm both spatial and visual openness.

Location and transport: The site is car-dependent with poor public transport and inadequate walking/cycling infrastructure.

"Golden Rules" concerns: The claimed benefits are not evidenced or secured through enforceable conditions.

Please refuse this application.`,

    'email-representatives': `I am writing to ask you to oppose the proposed housing development on Green Belt land at this site.

This is not "grey belt" - the land prevents sprawl, maintains settlement separation, and contributes to our local landscape and heritage.

The development is car-dependent and the "Golden Rules" benefits are not transparently secured.

Please:
- Urge the council to refuse this proposal
- Press the developer to focus on brownfield sites
- Keep me informed of meetings and votes

Thank you for your attention to this important matter.`,

    'appeal-representation': `I am writing as a local resident to ask that this appeal be dismissed.

This is not a "grey belt" site - it makes a strong contribution to Green Belt purposes including preventing sprawl and maintaining settlement separation.

The development would harm openness through its scale and visual impact. The location is car-dependent despite claims of sustainability.

The "Golden Rules" benefits are not secured or evidenced adequately.

The planning harm significantly outweighs any claimed benefits. Please dismiss this appeal.`,

    'local-plan': `I am writing to object to the proposed allocation of this site in the Local Plan.

The allocation is unsound - it is not justified and is inconsistent with national Green Belt policy.

The council's "grey belt" methodology incorrectly classifies this site, underweighting its contribution to preventing coalescence and protecting local character.

Reasonable alternatives including brownfield sites have not been fairly assessed.

Please delete this allocation and prioritize brownfield development.`
  };

  return templates[templateType] || templates['email-representatives'];
}

/**
 * Call OpenAI API
 */
async function generateTemplate(templateType, answers, apiKey) {
  const baseTemplate = getBaseTemplate(templateType);
  const { systemPrompt, userPrompt } = buildPrompt(templateType, answers, baseTemplate);

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'gpt-4o', // Using GPT-4o (latest available model)
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        temperature: 0.7, // Balanced - unique but consistent with formal tone
        max_tokens: 1000,
        presence_penalty: 0.5, // Reduce repetition while maintaining coherence
        frequency_penalty: 0.4
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'OpenAI API request failed');
    }

    const data = await response.json();
    return data.choices[0].message.content.trim();
  } catch (error) {
    console.error('OpenAI API Error:', error);
    throw error;
  }
}

/**
 * Main request handler
 */
export default {
  async fetch(request, env) {
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*', // In production, restrict to your domain
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
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
      // Get API key from environment variable
      const apiKey = env.OPENAI_API_KEY;
      if (!apiKey) {
        throw new Error('OpenAI API key not configured');
      }

      // Rate limiting
      const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
      if (!checkRateLimit(ip)) {
        return new Response(JSON.stringify({
          error: 'Rate limit exceeded. Please try again later.'
        }), {
          status: 429,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // Parse request
      const body = await request.json();
      const { templateType, answers } = body;

      // Validate input
      if (!templateType || !TEMPLATE_QUESTIONS[templateType]) {
        return new Response(JSON.stringify({ error: 'Invalid template type' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      if (!answers || !Array.isArray(answers) || answers.length === 0) {
        return new Response(JSON.stringify({ error: 'Answers are required' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // Generate template
      const generatedContent = await generateTemplate(templateType, answers, apiKey);

      return new Response(JSON.stringify({
        content: generatedContent,
        templateType: TEMPLATE_QUESTIONS[templateType].name
      }), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });

    } catch (error) {
      console.error('Worker error:', error);
      return new Response(JSON.stringify({
        error: 'Failed to generate template. Please try again.'
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
  }
};
