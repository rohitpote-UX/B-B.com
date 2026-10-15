export interface LLMResponse {
  text: string;
  provider: string;
  model: string;
  usage?: { prompt_tokens: number; completion_tokens: number };
}

export async function generateXPost(
  findingTitle: string,
  evidenceSummary: string,
  callToAction?: string
): Promise<LLMResponse> {
  const geminiApiKey = process.env.GEMINI_API_KEY;
  const openaiApiKey = process.env.OPENAI_API_KEY;

  if (geminiApiKey) {
    try {
      const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${geminiApiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: `Write an engaging X/Twitter post for BrandBattle (brandbattle.in) based on this finding: "${findingTitle}". Evidence: "${evidenceSummary}". Call to Action: "${callToAction || 'Visit brandbattle.in'}". Keep it under 280 characters with punchy formatting and 2 hashtags.`
            }]
          }]
        })
      });
      const data = await res.json();
      const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
      if (text) {
        return { text: text.trim(), provider: 'gemini', model: 'gemini-1.5-flash' };
      }
    } catch (err) {
      console.warn('[LLM] Gemini request failed, falling back to mock generator:', err);
    }
  }

  // Smart structured mock fallback for production reliability without required external key
  const mockText = `📱 Signal Alert: ${findingTitle}\n\n` +
    `${evidenceSummary.slice(0, 160)}...\n\n` +
    `⚡ Don't overpay. Verify real price comparison before you buy:\n` +
    `👉 ${callToAction || 'https://brandbattle.in'}\n\n` +
    `#BrandBattle #SmartShopping #PriceCheck`;

  return {
    text: mockText,
    provider: 'mock_provider',
    model: 'bb-intelligence-synthesizer-v1'
  };
}

export async function generateInstagramCaption(
  findingTitle: string,
  evidenceSummary: string,
  nicheTopic: string
): Promise<LLMResponse> {
  const mockText = `✨ BRANDBATTLE INTELLIGENCE BRIEF | ${findingTitle.toUpperCase()}\n\n` +
    `What's happening in ${nicheTopic} right now:\n\n` +
    `${evidenceSummary}\n\n` +
    `💡 WHY IT MATTERS:\n` +
    `Prices change fast. Knowing the verified benchmark gives you the edge.\n\n` +
    `🔗 Tap the link in bio to compare prices live on BrandBattle!\n\n` +
    `#BrandBattle #RetailIntelligence #${nicheTopic.replace(/\s+/g, '')} #DealAlert #IndiaShopping`;

  return {
    text: mockText,
    provider: 'mock_provider',
    model: 'bb-intelligence-synthesizer-v1'
  };
}

export async function generateOpportunityBrief(
  finding: { title: string; what_happened: string; why_it_matters: string },
  evidenceSummary: string
): Promise<LLMResponse> {
  const brief = `
# Executive Intelligence Briefing
**Title:** ${finding.title}
**Date:** ${new Date().toLocaleDateString()}

## 1. Context & Signals
${finding.what_happened}

## 2. Evidence Summary
${evidenceSummary}

## 3. BrandBattle Strategic Impact
${finding.why_it_matters}

## 4. Recommended Action Plan
- Deploy targeted comparison campaign on social channels.
- Update real-time price monitoring thresholds for listed competitor products.
- Alert email subscribers on discount benchmark shifts.
  `.trim();

  return {
    text: brief,
    provider: 'mock_provider',
    model: 'bb-intelligence-synthesizer-v1'
  };
}
