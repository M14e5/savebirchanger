#!/usr/bin/env node

const fs = require('fs');
const https = require('https');

const WORKER_API_URL = 'https://template-generator.martinssolver.workers.dev';

// Varied synthetic answers for each question
const syntheticAnswers = {
  residency: [
    'Lived in Birchanger for 20 years',
    'Resident of Stansted for 15 years',
    'Been a local resident for over 25 years',
    'Lived here for 8 years with my family',
    'Long-time resident of 30 years',
    'Moved here 12 years ago',
    'Resident for the past 18 years',
    'Living in the area for 10 years',
    'Been here for 22 years',
    'Resident of this community for 14 years',
    'Lived locally for 17 years',
    'Been in Birchanger for 9 years',
    'Resident for 26 years',
    'Living here for the past 11 years',
    'Been a resident for 19 years',
    'Lived in the village for 16 years',
    'Resident for 13 years',
    'Been here for 23 years',
    'Living locally for 21 years',
    'Resident of 24 years'
  ],
  greenBelt: [
    'This land prevents Birchanger and Stansted from merging into one continuous urban sprawl. It safeguards the 12th-century St Mary\'s Church historic setting and maintains the crucial separation gap with Bishop\'s Stortford. These are CORE Green Belt functions under NPPF.',
    'The site maintains the essential gap between settlements that has existed for over 1,000 years. It protects the medieval church setting and prevents coalescence with Bishop\'s Stortford. This clearly serves multiple Green Belt purposes.',
    'This Green Belt prevents the villages from becoming one merged settlement. The historic St Mary\'s Church relies on this countryside setting. The gap to Bishop\'s Stortford would be eliminated. These are fundamental Green Belt purposes.',
    'The land strongly prevents Birchanger-Stansted coalescence which would destroy both communities\' distinct identities. It safeguards heritage assets including the 12th-century church. It maintains strategic separation from Bishop\'s Stortford.',
    'This site serves critical Green Belt functions: preventing settlement merger, protecting the historic church setting that dates to the 12th century, and maintaining the Bishop\'s Stortford separation gap. Without this land, continuous urban sprawl would result.',
    'The gap between Birchanger and Stansted is already narrow at just 1.2km. This land is essential to prevent coalescence. The medieval church setting depends on open countryside. The Bishop\'s Stortford gap would be breached.',
    'This land performs multiple Green Belt purposes simultaneously: prevents merging of settlements, safeguards the Grade I listed St Mary\'s Church historic setting, maintains the strategic gap to Bishop\'s Stortford preventing regional sprawl.',
    'The site prevents urban sprawl by maintaining separation between distinct communities. It protects the 900-year-old church\'s countryside setting. It keeps Bishop\'s Stortford from merging with our villages. These are textbook Green Belt purposes.',
    'This Green Belt stops Birchanger and Stansted becoming indistinguishable suburbs. The historic church would lose its rural setting. The gap to Bishop\'s Stortford is already minimal and would be eliminated. Strong Green Belt contribution.',
    'The land serves fundamental Green Belt purposes: preventing coalescence between settlements, safeguarding designated heritage assets, maintaining strategic gaps. Development would undermine all three purposes simultaneously.',
    'This site prevents the merging of two ancient villages with distinct identities. It protects the setting of a 12th-century Grade I listed church. It maintains separation from Bishop\'s Stortford. Clear Green Belt purposes.',
    'The gap between settlements would be eliminated, causing coalescence. The historic church setting relies on open countryside. Bishop\'s Stortford separation would be breached. This land strongly serves Green Belt purposes under NPPF paragraph 138.',
    'This Green Belt prevents urban sprawl between Birchanger, Stansted and Bishop\'s Stortford. It safeguards the medieval church\'s rural character. It maintains village separation that has existed since the Domesday Book. Strong Green Belt function.',
    'The land prevents merger of settlements, each with over 1,000 years of history. It protects the setting of a nationally important heritage asset. It maintains strategic separation preventing continuous development to Bishop\'s Stortford.',
    'This site serves multiple Green Belt purposes: prevents coalescence of historic villages, safeguards the 12th-century church setting, maintains the Bishop\'s Stortford gap. Development would breach all three purposes.',
    'The Green Belt prevents Birchanger-Stansted merger which would destroy community identity. The church setting depends on countryside views. The Bishop\'s Stortford gap is already under pressure. This land is essential Green Belt.',
    'This land stops villages merging into urban sprawl, protects the Grade I listed church historic setting, and maintains separation from Bishop\'s Stortford. These are core Green Belt purposes that cannot be compromised.',
    'The site prevents coalescence between two distinct medieval settlements. It safeguards the setting of a nationally designated heritage asset. It maintains the strategic gap preventing M11 corridor sprawl. Strong Green Belt contribution.',
    'This Green Belt maintains the essential gap between villages, protects the 12th-century church countryside setting, and prevents Bishop\'s Stortford merger. Development would undermine all three fundamental purposes.',
    'The land serves critical Green Belt functions: preventing settlement coalescence, safeguarding heritage asset settings, maintaining strategic gaps. NPPF paragraph 138 purposes are clearly met.'
  ],
  sustainability: [
    'The site is 2.1km from Stansted station with NO continuous footway, failing the DfT 800m walkability standard. Bus 308 runs hourly Mon-Sat only, last bus at 6:30pm, NO Sunday service. This forces car-dependency with an estimated 1,180 daily car trips.',
    'Walking to the station is 2.1km with no safe footway, steep gradients, and unlit sections. Public transport is inadequate - hourly buses weekdays only, no evening or Sunday service. Residents would be entirely car-dependent.',
    'There is no continuous footway to the station 2.1km away, making walking dangerous especially for children and elderly. The bus service is hourly at best, stops at 6:30pm, doesn\'t run Sundays. This fails basic sustainability tests.',
    'The nearest station is 2.1km via the B1383 which has no footway, a 6% gradient, and no street lighting. Bus route 308 is hourly Monday-Saturday only, last bus 6:30pm. This location is car-dependent and fails NPPF Para 155 sustainability requirements.',
    'Walking to the station requires 2.1km on roads without footways. The only bus service is hourly on weekdays, stops early evening, no Sunday service. Local shops are 1.8km away. This is a car-dependent location that fails sustainability tests.',
    'The site is too far from the station (2.1km) with no safe walking route. Public transport is inadequate - one bus per hour Mon-Sat, none on Sundays, last bus 6:30pm. Residents would need cars for commuting, shopping, healthcare.',
    'Access to the station is 2.1km with no footway, dangerous for pedestrians. Bus 308 frequency is poor (hourly), no evening or weekend service. This fails the DfT 800m walkability standard and NPPF sustainability requirements.',
    'The location is 2.1km from public transport with no safe pedestrian route. Bus service is minimal - hourly on weekdays only, stops at 6:30pm. This forces car-ownership and fails to meet sustainable location criteria.',
    'There is no walkable access to the station - 2.1km with no footway and steep hills. The bus runs once an hour weekdays, no Sundays, last service 6:30pm. This is fundamentally car-dependent and unsustainable.',
    'Walking to Stansted station is 2.1km on roads without footways, failing accessibility standards. The bus service (route 308) is hourly Mon-Sat only, no evening or Sunday service. This location fails NPPF Para 155 sustainability test.',
    'The site is 2.1km from the nearest station with no continuous footway, 6% gradient, unlit sections. Bus 308: hourly Mon-Sat, last bus 6:30pm, no Sundays. Local shops 1.8km away. Entirely car-dependent, failing sustainability tests.',
    'Access to public transport is inadequate - 2.1km to station via roads without footways. Bus route 308 runs hourly weekdays only, stops early evening. This fails the DfT 800m walkable distance standard for daily trips.',
    'The nearest station is 2.1km away with no safe walking route. Public transport is one bus per hour Mon-Sat, finishing at 6:30pm. This is a car-dependent location that cannot meet NPPF sustainable development requirements.',
    'Walking to the station is 2.1km on the B1383 with no footway, steep gradient, no lighting. Bus service is inadequate for daily needs - hourly weekdays only. This fails basic sustainability tests for accessible locations.',
    'The location is 2.1km from Stansted station with no pedestrian infrastructure. Bus route 308 operates hourly Mon-Sat only, no Sunday or evening service. Residents would be forced into car ownership, failing NPPF sustainability criteria.',
    'There is no safe walking route to the station 2.1km away - no footways, steep hills, unlit. The bus runs once per hour weekdays, last bus 6:30pm, no Sundays. This is fundamentally unsustainable and car-dependent.',
    'Access to the station requires 2.1km walk with no footway. Public transport is minimal - bus 308 hourly Mon-Sat only, stops at 6:30pm. Local services 1.8km away. This fails all sustainability tests for accessible locations.',
    'The site is 2.1km from public transport with dangerous pedestrian access (no footway, gradient, unlit). Bus service inadequate - hourly weekdays only. This location is car-dependent with estimated 1,180 daily car trips, failing NPPF Para 155.',
    'Walking to Stansted station is 2.1km via the B1383 without footways. Bus 308: hourly Mon-Sat, last bus 6:30pm, no Sundays. Nearest shops 1.8km. This is a car-dependent location failing DfT walkability standards and NPPF sustainability tests.',
    'The location is 2.1km from the station with no continuous safe walking route. Public transport is hourly buses weekdays only, no evening or Sunday service. This fails to meet accessible location requirements under NPPF Para 155.'
  ],
  goldenRules: [
    'The developer offers school LAND but not funded BUILDINGS - who pays for construction, equipment, and teachers? Highway mitigation is listed as vague "s106 contribution" without binding amounts or delivery triggers. BNG relies on off-site units with no 30-year management plan secured. No commitments are tied to occupation triggers.',
    'Affordable housing: No open-book viability assessment proves 50% is deliverable. Infrastructure: Developer offers land for school but no commitment to fund actual buildings. Highway upgrades are unfunded "contributions". BNG is off-site with delivery risk. Nothing is legally secured before occupation.',
    'The school commitment is just LAND not funded buildings - where are the millions needed for construction? GP surgery capacity is not addressed. Highway mitigation lacks specific funding commitments. BNG is off-site with no enforceable management plan. These are promises without legal backing.',
    'Developer promises 50% affordable housing but provides no viability evidence it\'s deliverable. School expansion is LAND ONLY - who funds the actual buildings, teachers, equipment? Highway upgrades are vague s106 contributions. BNG off-site creates delivery risk. No binding triggers preventing occupation.',
    'The "Golden Rules" lack enforceable Section 106 agreements: school land offered but building costs unfunded, highway mitigation is vague "contributions", affordable housing viability not proven, BNG delivery relies on off-site units. Nothing is legally tied to occupation triggers.',
    'School infrastructure: developer offers land but no funded buildings - this is meaningless without committed funding. Highway upgrades are unfunded. Affordable housing at 50% lacks viability assessment. BNG is off-site with delivery risk. No legal commitments securing delivery before occupation.',
    'The developer claims 50% affordable but provides no evidence it\'s economically viable. School commitment is land only, not funded buildings. Highway mitigation lacks binding financial commitments. BNG dependent on off-site compensation with no 30-year plan secured.',
    'Affordable housing viability is unproven at 50%. School expansion commitment is LAND not BUILDINGS - who pays construction costs? Highway contributions are vague and unfunded. BNG off-site creates delivery uncertainty. None of these promises are legally secured via enforceable Section 106.',
    'The school offer is land only - no funding commitment for buildings, staffing, or equipment. Highway upgrades are listed as s106 "contributions" without specific amounts or triggers. BNG relies on off-site units. Affordable housing at 50% has no viability evidence. No binding legal agreements.',
    'Developer promises are unenforceable: 50% affordable without viability proof, school land without building funding, highway mitigation without committed amounts, BNG off-site with delivery risk. No Section 106 agreements tying delivery to occupation triggers.',
    'School commitment is LAND ONLY - where is the £10-15 million needed for buildings? Highway capacity upgrades are unfunded "contributions". BNG is off-site without enforceable 30-year management. Affordable housing viability at 50% is not evidenced. These are vague promises.',
    'The developer offers school land but no commitment to fund construction, fit-out, or staffing. Highway mitigation lacks specific financial commitments or delivery timelines. BNG dependent on off-site units. 50% affordable housing lacks open-book viability assessment proving deliverability.',
    'Affordable housing: no evidence 50% is economically viable. Infrastructure: school land offered but building costs unfunded. Highway upgrades are vague s106 "contributions". BNG off-site with no secured management plan. Nothing legally committed before occupation.',
    'The "Golden Rules" are undeliverable promises: school land without building funding (£10m+ required), highway mitigation without binding commitments, BNG off-site with delivery risk, affordable housing without viability evidence. No enforceable Section 106 securing delivery.',
    'Developer claims 50% affordable but no viability study proves it\'s deliverable. School infrastructure is LAND not funded BUILDINGS. Highway capacity upgrades unfunded. BNG relies on off-site compensation. No legal agreements tie delivery to occupation triggers.',
    'School expansion: land offered but who funds the £10-15 million buildings? Highway mitigation is vague "s106 contribution" without amounts or timelines. BNG off-site creates delivery uncertainty. Affordable housing at 50% lacks economic viability evidence.',
    'The developer promises school land but no funded buildings, highway contributions without binding amounts, BNG off-site with no management plan, 50% affordable without viability proof. These are unenforceable promises, not legally secured commitments.',
    'Affordable housing viability at 50% is unproven. School commitment is land only - construction funding unaddressed (£10m+ cost). Highway upgrades lack specific commitments. BNG dependent on off-site delivery. No Section 106 agreements securing delivery before occupation.',
    'The "Golden Rules" lack legal enforceability: school land without building funding commitments, highway mitigation as vague "contributions", BNG off-site without 30-year plans, 50% affordable without viability evidence. Nothing tied to occupation triggers.',
    'Developer offers school LAND but not funded BUILDINGS - this is a meaningless promise without funding. Highway capacity upgrades unfunded. BNG off-site with delivery risk. Affordable housing at 50% lacks viability proof. No binding Section 106 agreements.'
  ],
  infrastructure: [
    'Forest Hall School rejected my child - already oversubscribed with no sixth form provision. GP appointments at Lower Street are 3-week waits. B1383 gridlocks daily 8-9am and 5-6pm. Birchanger Lane floods every heavy rain, making it impassable.',
    'School capacity crisis - Forest Hall is full, children being sent to schools miles away. GP surgery appointments take 2-3 weeks to get. Traffic on Cambridge Road is gridlocked morning and evening. Local flooding gets worse every year.',
    'My GP surgery (Church Road) is overwhelmed - impossible to get appointments. Forest Hall School has rejected local children due to oversubscription. B1383 traffic is at a standstill during rush hour. Drainage cannot cope with current development.',
    'Forest Hall School is oversubscribed - no places for local children, no sixth form forcing travel to Bishop\'s Stortford. GP surgeries are at breaking point - 3 week waits for appointments. Roads are gridlocked every morning and evening rush hour.',
    'Healthcare access is dire - my GP practice has 3-week wait times for routine appointments. Schools are full - Forest Hall rejected local applications. Traffic on the B1383 and Cambridge Road is gridlocked. Surface water flooding occurs regularly.',
    'School places are unavailable - Forest Hall oversubscribed, children traveling miles. GP appointments take weeks to get at both local surgeries. Morning and evening traffic is gridlocked on all main roads. Flooding on Birchanger Lane after heavy rain.',
    'Forest Hall School is full - local children being turned away. GP surgeries overwhelmed - weeks of wait for appointments. B1383 traffic is at capacity - gridlock daily during commute times. Existing drainage infrastructure cannot cope with current levels.',
    'My children couldn\'t get places at Forest Hall - already oversubscribed. Getting a GP appointment takes 2-3 weeks minimum. Traffic is gridlocked on Cambridge Road and B1383 every rush hour. Surface water flooding is a recurring problem.',
    'School capacity is exhausted - Forest Hall full, no sixth form provision. Healthcare access is critical - GP surgeries have 3-week waits. Road infrastructure is at breaking point - daily gridlock on main routes. Flooding worsens with each development.',
    'Forest Hall School has rejected local children due to capacity. GP appointment waits are 2-3 weeks at Lower Street surgery. B1383 and Cambridge Road are gridlocked morning and evening. Birchanger Lane floods making it impassable after heavy rain.',
    'Schools are oversubscribed - Forest Hall turning away local residents. GP practices overwhelmed - impossible to get timely appointments. Traffic infrastructure at capacity - gridlock on B1383 daily. Surface water drainage inadequate causing regular flooding.',
    'Healthcare crisis - my GP surgery has 3-week appointment waits. School capacity exhausted - Forest Hall full, no sixth form. Road network gridlocked every rush hour on B1383 and Cambridge Road. Flooding occurs regularly on local lanes.',
    'Forest Hall School is at capacity - local children denied places. GP surgeries oversubscribed - weeks of waiting for appointments. Traffic is gridlocked during commute times on all main routes. Drainage system cannot cope causing repeated flooding.',
    'School places unavailable - Forest Hall oversubscribed, children sent miles away. GP appointment waits are 2-3 weeks at both local practices. B1383 traffic at standstill rush hour. Birchanger Lane floods after every heavy rainfall.',
    'My GP practice (Lower Street) has 3-week wait times. Forest Hall School rejected my child due to oversubscription. Traffic gridlock on B1383 and Cambridge Road is daily occurrence. Surface water flooding gets worse with each new development.',
    'School capacity crisis - Forest Hall full, no local provision. Healthcare access dire - GP surgeries overwhelmed with 3-week waits. Road infrastructure at breaking point - gridlock morning and evening. Flooding on Birchanger Lane regularly.',
    'Forest Hall School turning away local children - oversubscribed. GP surgeries at capacity - impossible to get appointments within weeks. Traffic infrastructure failing - daily gridlock on main routes. Drainage inadequate causing regular flooding.',
    'Healthcare overwhelmed - my GP has 3-week appointment waits. Schools at capacity - Forest Hall rejected local applications. Traffic gridlocked on B1383 and Cambridge Road every rush hour. Flooding occurs regularly making lanes impassable.',
    'School places denied - Forest Hall oversubscribed, no sixth form. GP services overwhelmed - weeks to get appointments. Road network at capacity - gridlock daily during commute times. Surface water flooding worsens with every development.',
    'Forest Hall School is full - children being sent to distant schools. GP appointment waits are 3 weeks at local surgeries. B1383 and Cambridge Road gridlocked morning and evening. Birchanger Lane floods regularly after heavy rainfall.'
  ]
};

// Function to make API call
function generateTemplate(templateType, answers) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({
      templateType: templateType,
      answers: answers
    });

    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = https.request(WORKER_API_URL, options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (res.statusCode === 200) {
            resolve(result.content);
          } else {
            reject(new Error(result.error || 'API request failed'));
          }
        } catch (e) {
          reject(new Error('Failed to parse response'));
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.write(postData);
    req.end();
  });
}

// Function to get random item from array
function getRandom(arr, usedIndices) {
  let index;
  do {
    index = Math.floor(Math.random() * arr.length);
  } while (usedIndices.has(index) && usedIndices.size < arr.length);
  usedIndices.add(index);
  return arr[index];
}

// Main function
async function generateAllObjections() {
  console.log('Generating 50 synthetic planning objections...\n');

  const results = [];
  const usedCombinations = {
    residency: new Set(),
    greenBelt: new Set(),
    sustainability: new Set(),
    goldenRules: new Set(),
    infrastructure: new Set()
  };

  for (let i = 1; i <= 50; i++) {
    try {
      console.log(`Generating objection ${i}/50...`);

      // Create varied answers using different combinations
      const answers = [
        getRandom(syntheticAnswers.residency, usedCombinations.residency),
        getRandom(syntheticAnswers.greenBelt, usedCombinations.greenBelt),
        getRandom(syntheticAnswers.sustainability, usedCombinations.sustainability),
        getRandom(syntheticAnswers.goldenRules, usedCombinations.goldenRules),
        getRandom(syntheticAnswers.infrastructure, usedCombinations.infrastructure)
      ];

      // Call API
      const content = await generateTemplate('planning-objection', answers);

      results.push({
        number: i,
        answers: answers,
        content: content
      });

      console.log(`✓ Objection ${i} generated successfully`);

      // Add small delay to avoid overwhelming the API
      await new Promise(resolve => setTimeout(resolve, 1000));

    } catch (error) {
      console.error(`✗ Error generating objection ${i}:`, error.message);
      results.push({
        number: i,
        error: error.message
      });
    }
  }

  // Generate markdown document
  console.log('\nCreating markdown document...');

  let markdown = `# 50 Synthetic Planning Objections
## Generated Planning Objection Templates

This document contains 50 synthetically generated planning objection letters using the Save Our Villages template generator.

**Generated:** ${new Date().toLocaleString()}

---

`;

  results.forEach((result, index) => {
    markdown += `## Objection ${result.number}\n\n`;

    if (result.error) {
      markdown += `**Error:** ${result.error}\n\n`;
    } else {
      markdown += `### Input Answers\n\n`;
      markdown += `**How long have you lived or worked in this area?**\n${result.answers[0]}\n\n`;
      markdown += `**Why does this land STRONGLY serve Green Belt purposes?**\n${result.answers[1]}\n\n`;
      markdown += `**Why does this location FAIL the NPPF Para 155 sustainability test?**\n${result.answers[2]}\n\n`;
      markdown += `**What "Golden Rules" promises are UNDELIVERABLE?**\n${result.answers[3]}\n\n`;
      markdown += `**What infrastructure capacity problems have you observed?**\n${result.answers[4]}\n\n`;
      markdown += `---\n\n### Generated Objection Letter\n\n`;
      markdown += '```\n';
      markdown += result.content;
      markdown += '\n```\n\n';
    }

    // Page break (markdown page separator)
    if (index < results.length - 1) {
      markdown += `\n---\n\n<div style="page-break-after: always;"></div>\n\n`;
    }
  });

  // Write to file
  fs.writeFileSync('synthetic_planning_objections.md', markdown);
  console.log('\n✓ Markdown document created: synthetic_planning_objections.md');

  // Summary
  const successful = results.filter(r => !r.error).length;
  const failed = results.filter(r => r.error).length;

  console.log(`\nSummary:`);
  console.log(`  Successful: ${successful}`);
  console.log(`  Failed: ${failed}`);
  console.log(`  Total: ${results.length}`);
}

// Run
generateAllObjections().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
