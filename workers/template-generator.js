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
    'developer-consultation': `I am writing to object to City & Country's proposed development of 480 homes (180 in Birchanger, 300 in Stansted) on Green Belt land.

This is NOT "grey belt" under NPPF Paragraph 155 - the land STRONGLY serves Green Belt purposes by preventing coalescence between Birchanger and Stansted, safeguarding St Mary's Church 12th-century setting, and maintaining the separation gap from Bishop's Stortford.

The site FAILS the NPPF Para 155 sustainability test. It is 2.1km from Stansted station with NO continuous footway (fails DfT 800m walkability standard). Bus route 308 runs hourly Mon-Sat only (last bus 6:30pm, NO Sunday service). This is car-dependent development (~1,180 daily car trips, ~712 extra cars), NOT a sustainable location.

The "Golden Rules" are UNDELIVERABLE without legally binding Section 106 agreements. The developer offers school LAND but who funds the actual buildings, teachers, and equipment? Highway mitigation is listed as vague "s106 contribution" - how much, when, and is it legally binding before occupation? BNG relies on off-site units with delivery risk.

Infrastructure is already at capacity: Forest Hall School is oversubscribed with no sixth form, GP surgeries are overwhelmed, and B1383/Cambridge Road are gridlocked at peak times.

Please record this as a formal objection and keep me informed.`,

    'planning-objection': `I object to this application for 480 homes (180 Birchanger, 300 Stansted) because: (1) this is NOT "grey belt" under NPPF Para 155 - it strongly serves Green Belt purposes; (2) it FAILS the Para 155 sustainability test - car-dependent with inadequate public transport; (3) the "Golden Rules" are undeliverable without legally binding Section 106 agreements.

NPPF Para 155 Test 1 FAILS: Land must NOT strongly serve Green Belt - THIS FAILS. The land DOES strongly serve Green Belt: prevents Birchanger-Stansted coalescence, safeguards St Mary's Church 12th-century setting, maintains Bishop's Stortford separation gap.

NPPF Para 155 Test 2 FAILS: Must be sustainable location - THIS FAILS. Site is 2.1km from station with NO footway (fails DfT 800m standard). Bus 308: hourly Mon-Sat only, last bus 6:30pm, NO Sundays. Car-dependent: ~1,180 daily trips, ~712 cars.

"Golden Rules" Undeliverable: Developer offers school LAND but who funds buildings/teachers? Highway mitigation is vague "s106 contribution" - how much? When? Legally binding? BNG off-site with delivery risk.

Infrastructure Crisis: Forest Hall oversubscribed (no sixth form) - where will ~370 children go? GP surgeries overwhelmed. B1383/Cambridge Road gridlock - NO funded upgrades.

REFUSE. Not "grey belt" - strongly serves Green Belt, fails Para 155 sustainability. "Golden Rules" undeliverable without enforceable Section 106 requiring delivery BEFORE occupation.`,

    'email-representatives': `I am writing to ask you to oppose City & Country's application for 480 homes (180 Birchanger, 300 Stansted) on Green Belt land. This is NOT "grey belt" under NPPF Para 155:

• NPPF Para 155 test 1 FAILS: Land STRONGLY serves Green Belt purposes (prevents Birchanger-Stansted coalescence, protects St Mary's Church 12th-century setting, maintains Bishop's Stortford separation gap).
• NPPF Para 155 test 2 FAILS: Site is car-dependent (2.1km from station with NO footway, bus 308 hourly Mon-Sat only, last bus 6:30pm, NO Sundays) - NOT sustainable location.
• "Golden Rules" UNDELIVERABLE: Developer offers school LAND but not funded buildings. No legally binding Section 106 securing infrastructure delivery BEFORE occupation.
• Infrastructure CRISIS: Forest Hall School oversubscribed, GP surgeries overwhelmed, B1383/Cambridge Road gridlock - NO funded expansion. ~1,180 daily car trips, ~712 extra cars, ~370 school-age children with NO plan.

Please:
• Urge Uttlesford Council to REFUSE this application and reject "grey belt" classification
• Press City & Country to focus on brownfield alternatives
• Demand enforceable Section 106 agreements requiring infrastructure BEFORE occupation if approved
• Keep me informed of planning committee meetings and votes

Thank you for your attention to this important matter.`,

    'appeal-representation': `I am writing as a local resident to ask that this appeal for 480 homes (180 Birchanger, 300 Stansted) be dismissed.

NPPF Para 155 Test FAILS: This is NOT "grey belt" - the land STRONGLY serves Green Belt purposes (prevents Birchanger-Stansted coalescence, safeguards St Mary's Church 12th-century setting, maintains Bishop's Stortford separation gap).

Sustainability Test FAILS: Site is 2.1km from Stansted station with NO continuous footway (fails DfT 800m walkability standard). Bus 308: hourly Mon-Sat only, last bus 6:30pm, NO Sundays. This is car-dependent development (~1,180 daily trips, ~712 cars), NOT sustainable location required by NPPF Para 155.

"Golden Rules" Undeliverable: 50% affordable uplift not secured via binding Section 106; BNG dependent on off-site units with delivery risk; infrastructure (school buildings, highway upgrades) listed as vague "contributions" not legally tied to occupation triggers.

Infrastructure Capacity: Forest Hall School oversubscribed (no sixth form), GP surgeries overwhelmed, B1383/Cambridge Road gridlock - NO funded mitigation secured before development.

Planning balance: Generic benefits do not outweigh Green Belt harm, sustainability failures, and infrastructure crisis.

DISMISS the appeal. If allowed (despite these objections), apply stringent conditions/obligations requiring delivery BEFORE occupation.`,

    'local-plan': `I am writing to object to the proposed allocation of Land at Birchanger and Stansted (480 homes) in the Local Plan.

The allocation is UNSOUND - not justified, not effective, inconsistent with national policy on Green Belt and NPPF Para 155.

NPPF Para 155 "grey belt" methodology FLAWED: The council's method down-weights key Green Belt contribution factors (coalescence risk between Birchanger-Stansted, St Mary's Church historic setting, Bishop's Stortford separation gap), wrongly classing this site as "grey belt." The land STRONGLY serves Green Belt purposes - Para 155 test 1 FAILS.

Sustainability assessment FLAWED: Site is 2.1km from station with NO footway (fails DfT 800m standard), bus 308 hourly Mon-Sat only (last bus 6:30pm, NO Sundays) - this is car-dependent location, NOT sustainable as required by Para 155 test 2. Transport modelling ignores ~1,180 daily car trips, ~712 extra cars.

"Golden Rules" undeliverable: Evidence base lacks open-book viability proving 50% affordable housing is economically deliverable. No commitment to school BUILDINGS (only land offer). Highway mitigation unfunded. BNG relies on off-site units. Infrastructure Delivery Plan shows deficits/unfunded items.

Alternatives not fairly assessed: Brownfield sites within Bishop's Stortford and Stansted, densification near station, not robustly assessed as reasonable alternatives.

DELETE the allocation - replace with brownfield-first package. If retained (despite unsoundness), cap at 240 homes maximum, require permanent landscape buffer protecting Green Belt function, on-site social rent minimum 25%, BNG >20% secured on-site, school buildings funded before occupation, highway upgrades delivered before occupation.`
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
