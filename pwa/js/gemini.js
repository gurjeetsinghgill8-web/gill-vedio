/**
 * GILL VEDIO PWA — Gemini AI Module
 * Handles idea generation and caption generation via Gemini API
 */

let GEMINI_API_KEY = '';

export function setApiKey(key) {
  GEMINI_API_KEY = key;
}

export function getApiKey() {
  return GEMINI_API_KEY || localStorage.getItem('gill_gemini_key') || '';
}

const GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent';

async function callGemini(prompt) {
  const key = getApiKey();
  if (!key) throw new Error('Gemini API key not set. Please add it in Settings.');

  const res = await fetch(`${GEMINI_URL}?key=${key}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: {
        temperature: 0.9,
        maxOutputTokens: 3000,
        responseMimeType: 'application/json'
      }
    })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.error?.message || `API Error: ${res.status}`);
  }

  const data = await res.json();
  const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error('Empty response from Gemini');
  return text;
}

/**
 * Generate 10 viral video ideas
 */
export async function generateIdeas({ topic, niche, language, platform }) {
  const prompt = `You are a viral social media video expert. Generate exactly 10 viral short video ideas.

Topic: "${topic}"
Niche: ${niche}
Language: ${language}
Platform: ${platform}

For EACH idea, provide a JSON object with:
- "title": catchy, hook-based video title in ${language}
- "hook": exact first 3 seconds opening line/question that grabs attention
- "outline": array of 4 bullet points (short strings) for video structure
- "viral_score": integer 1-10 (virality potential)
- "hashtags": array of 5 trending hashtags (with #)
- "tip": one quick filming tip for this video

Respond ONLY with a valid JSON array of exactly 10 objects. No markdown, no explanation.`;

  const text = await callGemini(prompt);

  try {
    // Try parsing directly
    return JSON.parse(text);
  } catch {
    // Try extracting JSON array
    const match = text.match(/\[[\s\S]*\]/);
    if (match) return JSON.parse(match[0]);
    throw new Error('Could not parse ideas from AI response');
  }
}

/**
 * Generate caption + hashtags for a video
 */
export async function generateCaption({ topic, platform, niche }) {
  const prompt = `Generate a viral social media caption for a ${niche} video about "${topic}" for ${platform}.

Return a JSON object with:
- "caption": engaging caption (under 150 chars), with 2-3 emojis, in Hindi/English
- "hashtags": array of 8 trending hashtags
- "cta": a call-to-action phrase (e.g., "Save this for later!")

Respond ONLY with valid JSON. No markdown.`;

  const text = await callGemini(prompt);

  try {
    return JSON.parse(text);
  } catch {
    const match = text.match(/\{[\s\S]*\}/);
    if (match) return JSON.parse(match[0]);
    throw new Error('Could not parse caption from AI response');
  }
}
