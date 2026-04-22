#!/usr/bin/env node
/**
 * Flashcard Prompt Generator
 * 
 * Generates visual prompts for flashcards using AI (OpenRouter API).
 * Features:
 * - SGR (Subject-Guided Rewriting)
 * - Age rating (2-18+)
 * - Proportional batching (nouns, adjectives, verbs)
 * - Russian translation
 * - Mascot injection (7yo/15yo/25yo character)
 * 
 * Requirements:
 * - Node.js 18+
 * - export OPENROUTER_API_KEY="sk-or-..."
 */

import { readFileSync, writeFileSync, appendFileSync, existsSync, mkdirSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CONFIG = {
    // ========== DATA SOURCE ==========
    // Change provider name and its config to switch data source
    DATA_PROVIDER: 'txt_dicts',

    PROVIDER_CONFIGS: {
        csv_simple: {
            source: path.join(__dirname, 'Dale-Chall', 'flashcards_Dale-Chall_final_v2.csv'),
            column: 0,  // column index to extract words from
        },
        txt_dicts: {
            nouns: path.join(__dirname, 'dicts', 'nouns_all_final.txt'),
            adjs: path.join(__dirname, 'dicts', 'adjs_all_final.txt'),
            verbs: path.join(__dirname, 'dicts', 'verbs_all_final.txt'),
            excludeProvider: 'csv_simple',  // will exclude all words loaded by csv_simple provider
        },
    },

    // ========== GENERATOR CONFIG ==========
    BATCH_SIZE: 15,
    OUTPUT_CSV: path.join(__dirname, 'flashcards_final.csv'),
    OUTPUT_JSON: path.join(__dirname, 'sgr_reasoning.json'),
    DEBUG_DIR: path.join(__dirname, 'debug'),
    RAW_LOG_FILE: path.join(__dirname, 'debug', 'raw_interactions.jsonl'),
    SKIPPED_LOG: path.join(__dirname, 'debug', 'skipped_words.jsonl'),
    OPENROUTER_API_KEY: process.env.OPENROUTER_API_KEY || '',
    MODEL: 'arcee-ai/trinity-large-preview:free',
    API_URL: 'https://openrouter.ai/api/v1/chat/completions',
    MAX_SAVING_AGE: 8,
    JSON_SCHEMA: {
        name: "FlashcardSGR_Production_Cascade",
        strict: true,
        schema: {
            type: "array",
            items: {
                type: "object",
                properties: {
                    "a_word": { type: "string", description: "Input English word" },
                    "b_category": { type: "string", enum: ["concrete_object", "abstract_concept", "action_verb", "time_unit", "letter_number", "role", "family_role"] },
                    "c_analysis": { type: "string", description: "Reasoning for category and visual anchor" },
                    "d_risks": { type: "array", items: { type: "string" }, maxItems: 2, description: "Risks of confusion" },
                    "e_rus_word": { type: "string", description: "Single Russian translation" },
                    "f_prompt": { type: "string", maxLength: 120, description: "Visual description ONLY. No style words." },
                    "g_confidence": { type: "integer", minimum: 0, maximum: 100, description: "Confidence 0-100" },
                    "h_min_age": { type: "integer", enum: [2, 4, 6, 8, 10, 13, 16, 18], description: "Minimum age to understand" },
                    "i_content_tags": { type: "array", items: { type: "string" }, description: "Tags: animal, color, safe, adult_theme, etc." },
                    "j_selected_mascot": { type: "string", enum: ["7yo_girl", "15yo_girl", "25yo_woman", "none"] }
                },
                required: ["a_word", "b_category", "c_analysis", "d_risks", "e_rus_word", "f_prompt", "g_confidence", "h_min_age", "i_content_tags", "j_selected_mascot"],
                additionalProperties: false
            }
        }
    },
    TIMEOUT_MS: 120_000,
    MAX_RETRIES: 10,
    BASE_DELAY: 3000,
    MAX_DELAY: 45_000,
    MIN_429_WAIT: 18_000,
    LOG_RAW_INTERACTIONS: true,
};

if (!CONFIG.OPENROUTER_API_KEY) {
    console.error('Set OPENROUTER_API_KEY environment variable');
    process.exit(1);
}

if (!existsSync(CONFIG.DEBUG_DIR)) mkdirSync(CONFIG.DEBUG_DIR, { recursive: true });

function log(level, msg, data = null) {
    const ts = new Date().toLocaleTimeString();
    const prefix = { debug: '[DEBUG]', info: '[INFO]', warn: '[WARN]', error: '[ERROR]', success: '[OK]' }[level] || '[INFO]';
    console.log(`${prefix} [${ts}] ${msg}`);
    if (data) console.dir(data, { depth: 2, colors: true });
}

function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

function logRawInteraction(request, response, metadata = {}) {
    if (!CONFIG.LOG_RAW_INTERACTIONS) return;
    const entry = {
        timestamp: new Date().toISOString(),
        request: { model: CONFIG.MODEL, response_format: request.response_format?.type },
        response: { status: response.status, usage: response.usage, error: response.error },
        metadata,
    };
    appendFileSync(CONFIG.RAW_LOG_FILE, JSON.stringify(entry) + '\n', 'utf-8');
}

function logSkippedWord(word, reason) {
    const entry = { word, reason, timestamp: new Date().toISOString() };
    appendFileSync(CONFIG.SKIPPED_LOG, JSON.stringify(entry) + '\n', 'utf-8');
}

// ========== DATA PROVIDERS (Simple Iterators) ==========

// CSV Provider: reads words sequentially from CSV column
function createCsvProvider(config) {
    const { source, column } = config;
    let words = [];
    let idx = 0;

    function init() {
        if (!existsSync(source)) {
            log('warn', `CSV not found: ${source}`);
            return;
        }
        const text = readFileSync(source, 'utf-8');
        const lines = text.split('\n').filter(l => l.trim());
        const header = lines[0].split(',');
        log('info', `CSV Provider: column "${header[column]}" from ${source}`);

        for (let i = 1; i < lines.length; i++) {
            const cols = lines[i].split(',');
            const word = (cols[column] || '').trim().toLowerCase();
            if (word) words.push(word);
        }
        log('info', `CSV Provider: ${words.length} words total`);
    }

    return {
        init,
        next(batchSize) {
            if (idx >= words.length) return [];
            const batch = words.slice(idx, idx + batchSize);
            idx += batchSize;
            return batch;
        },
        reset() { idx = 0; },
        remaining() { return words.length - idx; }
    };
}

// TXT Dicts Provider: round-robin from noun/adj/verb files
function createTxtDictsProvider(config) {
    const { nouns, adjs, verbs, excludeProvider } = config;
    let allWords = [];
    let idx = 0;

    function init() {
        // Load exclude words from another provider
        let excludeSet = new Set();
        if (excludeProvider && CONFIG.PROVIDER_CONFIGS[excludeProvider]) {
            const excludeProv = createProvider(excludeProvider);
            excludeProv.init();
            let batch = excludeProv.next(10000);
            while (batch.length > 0) {
                batch.forEach(w => excludeSet.add(w));
                batch = excludeProv.next(10000);
            }
            log('info', `TXT Provider: excluding ${excludeSet.size} words from ${excludeProvider}`);
        }

        const load = (path) => existsSync(path)
            ? readFileSync(path, 'utf-8')
                .split('\n')
                .map(w => w.trim().toLowerCase())
                .filter(w => w && !excludeSet.has(w))
            : [];

        const pools = {
            nouns: load(nouns),
            adjs: load(adjs),
            verbs: load(verbs),
        };

        // Calculate real ratios
        const total = pools.nouns.length + pools.adjs.length + pools.verbs.length;
        const ratios = {
            nouns: pools.nouns.length / total,
            adjs: pools.adjs.length / total,
            verbs: pools.verbs.length / total,
        };
        log('info', `TXT Provider: nouns:${pools.nouns.length}, adjs:${pools.adjs.length}, verbs:${pools.verbs.length}`);
        log('info', `TXT Provider: ratios - nouns:${ratios.nouns.toFixed(2)}, adjs:${ratios.adjs.toFixed(2)}, verbs:${ratios.verbs.toFixed(2)}`);

        // Round-robin into single array
        allWords = [];
        const counts = { nouns: 0, adjs: 0, verbs: 0 };
        const targets = {
            nouns: Math.round(CONFIG.BATCH_SIZE * ratios.nouns),
            adjs: Math.round(CONFIG.BATCH_SIZE * ratios.adjs),
            verbs: Math.round(CONFIG.BATCH_SIZE * ratios.verbs),
        };

        while (counts.nouns < pools.nouns.length ||
               counts.adjs < pools.adjs.length ||
               counts.verbs < pools.verbs.length) {
            for (const key of ['nouns', 'adjs', 'verbs']) {
                const target = targets[key];
                const pool = pools[key];
                for (let i = 0; i < target && counts[key] < pool.length; i++) {
                    allWords.push(pool[counts[key]++]);
                }
            }
        }
        log('info', `TXT Provider: ${allWords.length} words total`);
    }

    return {
        init,
        next(batchSize) {
            if (idx >= allWords.length) return [];
            const batch = allWords.slice(idx, idx + batchSize);
            idx += batchSize;
            return batch;
        },
        reset() { idx = 0; },
        remaining() { return allWords.length - idx; }
    };
}

// Provider factory
function createProvider(providerName = CONFIG.DATA_PROVIDER) {
    const providerConfig = CONFIG.PROVIDER_CONFIGS[providerName];
    switch (providerName) {
        case 'csv_simple':
            return createCsvProvider(providerConfig);
        case 'txt_dicts':
            return createTxtDictsProvider(providerConfig);
        default:
            throw new Error(`Unknown provider: ${providerName}`);
    }
}

function loadCheckpoint(csvPath) {
    if (!existsSync(csvPath)) return new Set();
    const text = readFileSync(csvPath, 'utf-8').trim();
    if (!text) return new Set();
    return new Set(text.split('\n').slice(1).map(l => l.split(',')[0]?.trim()).filter(Boolean));
}

function buildSgrSystemPrompt() {
    const MASCOTS = {
        "7yo_girl": "7yo girl, curly red hair, freckles",
        "15yo_girl": "15yo girl, curly red hair, freckles, teen style",
        "25yo_woman": "25yo woman, curly red hair, freckles, adult style"
    };

    const FINAL_TEMPLATE = `one {YOUR_PROMPT_HERE}, flat vector, natural colors, accents from coral red, sandy yellow, mint green, teal blue, thick outline, centered, simple, flashcard, white background, isolated, no frame`;

    return `
You are an expert in visual learning datasets for ages 2–18+.
Task: Generate precise visual prompts for flashcards based on English words.

=== AGE & SAFETY PROTOCOL (STEP 1) ===
1. Assign 'h_min_age' (2, 4, 6, 8, 10, 13, 16, 18):
   • 2: Colors, sounds, basic objects (red, cat, ball)
   • 4: Concrete nouns, simple actions (apple, run, happy)
   • 6: Emotions, simple abstractions (friendship, brave)
   • 8: Social concepts, school (justice, environment)
   • 10+: Complex abstractions, adult topics (democracy, economy)
   • 18: EXPLICIT (sex, drugs, gore) → Set 'f_prompt': "", 'h_min_age': 18

2. Assign 'i_content_tags': [animal, color, shape, food, emotion, action, nature, household, technology, geography, etc.]
   • DO NOT use "safe" tag.
   • If h_min_age >= 18 → add "adult_theme".

3. SKIP PROPER NOUNS:
   If the word is a specific name of a person (Lee, Jones) or obscure place → Set h_min_age: 18, f_prompt: "" (Skip it).
   Common nouns (teacher, city) are OK.

=== MASCOT INJECTION RULE (CRITICAL - STEP 2) ===
Based on 'h_min_age', select 'j_selected_mascot':
• h_min_age 2–8 → "7yo_girl" → USE STRING: "${MASCOTS['7yo_girl']}"
• h_min_age 10–16 → "15yo_girl" → USE STRING: "${MASCOTS['15yo_girl']}"
• h_min_age 16+ → "25yo_woman" → USE STRING: "${MASCOTS['25yo_woman']}"
• Concrete objects, letters → "none"

❗ IF selected_mascot IS NOT "none":
You MUST insert the EXACT mascot string into 'f_prompt'.
❌ FORBIDDEN generic words: "girl", "child", "woman", "person", "teenager".
✅ REQUIRED exact string: "${MASCOTS['7yo_girl']}" (for example).

Placement: Place the mascot naturally.
Example: "${MASCOTS['7yo_girl']}, jumping with joy" (Correct)
Example: "girl jumping" (WRONG - generic)
Example: "ball held by ${MASCOTS['7yo_girl']}" (Correct - object focus)

=== COMPOSITIONAL HIERARCHY (CRITICAL - FIX "MASKOT DOMINANCE" PROBLEM) ===
The Concept must be the HERO, the Mascot is the GUIDE.
For words like "behind", "big", "under", "small":
1. SCALE CUES: You MUST use words like "GIGANTIC", "TINY", "OVERSIZED", "MASSIVE".
   ❌ "girl next to bear" → ✅ "GIANT teddy bear, tiny ${MASCOTS['7yo_girl']} hugging its leg"
   ❌ "girl behind tree" → ✅ "MASSIVE oak tree filling frame, tiny ${MASCOTS['7yo_girl']} peeking from behind trunk"
2. CONTEXT FIRST: Describe the large object BEFORE the mascot.
   ❌ "Girl pointing at clock" → ✅ "Large wall clock showing 5 o'clock, ${MASCOTS['7yo_girl']} pointing at it"

=== VISUAL HEURISTICS (STEP 3: ANALYSIS & PROMPT) ===
1. CONCRETE > ABSTRACT: ❌ "concept" → ✅ "pile of apples"
2. ACTION > STATE: ❌ "happy" → ✅ "mascot laughing, hands clapping"
3. NO SYMBOLS/TEXT: ❌ "checkmark", "question mark", "sign with text" → ✅ "thumbs up", "shrugging", "pointing finger"
4. CAUSE + REACTION: Show the object causing the emotion. ❌ "girl scared" → ✅ "girl hiding behind hands, large spider visible"
5. DYNAMIC POSES: Ban generic "standing". Use "crouching", "climbing", "peeking", "hugging".
6. ROLE DISTINCTNESS: Roles (Chef, Mom) need props (Chef hat, hugging baby).
7. The "Finger Test": Will a child say the target word instantly? If not, simplify.

=== GENERATION CONTEXT ===
Fill 'f_prompt' to replace {YOUR_PROMPT_HERE} in:
"${FINAL_TEMPLATE}"

❗ YOU FILL ONLY 'f_prompt'.
❗ DO NOT duplicate style words (flat vector, white background, simple...). They are in the template.
❗ Max 120 chars. Max 2 visual elements.

=== OUTPUT FORMAT (STRICT JSON ARRAY) ===
[
  {
    "a_word": "apple",
    "b_category": "concrete_object",
    "c_analysis": "Common fruit. Anchor: Red apple with leaf.",
    "d_risks": [],
    "e_rus_word": "яблоко",
    "f_prompt": "apple, with leaf and stem",
    "g_confidence": 100,
    "h_min_age": 4,
    "i_content_tags": ["food", "nature"],
    "j_selected_mascot": "none"
  },
  {
    "a_word": "brave",
    "b_category": "abstract_concept",
    "c_analysis": "Feeling of courage. Anchor: Mascot standing tall.",
    "d_risks": ["Might be confused with just standing"],
    "e_rus_word": "смелый",
    "f_prompt": "${MASCOTS['7yo_girl']}, standing tall, chest out, smiling confidently",
    "g_confidence": 90,
    "h_min_age": 6,
    "i_content_tags": ["emotion"],
    "j_selected_mascot": "7yo_girl"
  },
  {
    "a_word": "big",
    "b_category": "abstract_concept",
    "c_analysis": "Scale concept. Anchor: Giant bear vs tiny girl.",
    "d_risks": ["Without 'GIANT', objects look same size"],
    "e_rus_word": "большой",
    "f_prompt": "GIANT teddy bear, tiny ${MASCOTS['7yo_girl']} hugging its leg",
    "g_confidence": 95,
    "h_min_age": 4,
    "i_content_tags": ["abstract", "size"],
    "j_selected_mascot": "7yo_girl"
  },
  {
    "a_word": "behind",
    "b_category": "abstract_concept",
    "c_analysis": "Spatial concept. Anchor: Massive tree, tiny girl peeking.",
    "d_risks": ["Girl might cover the tree if not 'TINY'"],
    "e_rus_word": "позади",
    "f_prompt": "MASSIVE oak tree filling frame, tiny ${MASCOTS['7yo_girl']} peeking from behind trunk",
    "g_confidence": 95,
    "h_min_age": 4,
    "i_content_tags": ["abstract", "spatial"],
    "j_selected_mascot": "7yo_girl"
  }
]
Return an array of objects in JSON format. No text before or after.
`.trim();
}

function buildBatchPrompt(words) {
    return `Process words: ${words.map(w => `"${w}"`).join(', ')}. Return JSON Array.`;
}

async function callOpenRouter(messages, maxTokens = 4000, batchContext = '') {
    let delay = CONFIG.BASE_DELAY;
    for (let attempt = 1; attempt <= CONFIG.MAX_RETRIES; attempt++) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT_MS);
        try {
            const body = {
                model: CONFIG.MODEL,
                messages,
                temperature: 0.2,
                max_tokens: maxTokens,
                response_format: { type: "json_schema", json_schema: CONFIG.JSON_SCHEMA }
            };
            const res = await fetch(CONFIG.API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${CONFIG.OPENROUTER_API_KEY}`,
                    'HTTP-Referer': 'http://localhost',
                    'X-Title': 'MindGym-Flashcards-Pro',
                },
                body: JSON.stringify(body),
                signal: controller.signal,
            });
            const responseText = await res.text();
            let data;
            try { data = JSON.parse(responseText); }
            catch { data = { error: { message: 'Invalid JSON response' }, raw: responseText }; }

            logRawInteraction({ response_format: body.response_format }, { status: res.status, usage: data.usage, error: data.error }, { batchContext, attempt });

            if (res.status === 429) {
                const resetHeader = res.headers.get('x-ratelimit-reset-requests');
                let waitMs = CONFIG.MIN_429_WAIT;
                if (resetHeader) {
                    const resetTime = parseInt(resetHeader, 10) * 1000;
                    waitMs = Math.max(CONFIG.MIN_429_WAIT, resetTime - Date.now() + 1000);
                }
                log('warn', `429 Rate Limited. Wait: ${waitMs}ms`);
                throw { type: 'rate_limit', waitMs };
            }
            if (!res.ok || data.error) {
                const errText = data.error?.message || responseText.substring(0, 200);
                throw { type: 'http_error', status: res.status, text: errText };
            }
            const raw = data.choices?.[0]?.message?.content?.trim();
            try {
                const parsed = JSON.parse(raw);
                if (!Array.isArray(parsed)) throw { type: 'not_array', got: typeof parsed };
                return parsed;
            } catch { throw { type: 'parse_error', raw: raw?.substring(0, 300) }; }
        } catch (err) {
            clearTimeout(timeoutId);
            if (attempt === CONFIG.MAX_RETRIES) throw err;
            let waitMs = err.type === 'rate_limit' ? err.waitMs : Math.min(delay * Math.pow(2, attempt), CONFIG.MAX_DELAY);
            await sleep(waitMs);
            delay *= 1.3;
        }
    }
    return [];
}

async function processBatchWithCarryover(words, batchNum) {
    log('info', `Batch #${batchNum} | ${words.length} words`);
    const results = await callOpenRouter([
        { role: 'system', content: buildSgrSystemPrompt() },
        { role: 'user', content: buildBatchPrompt(words) }
    ], 4000, `batch_${batchNum}`);

    if (!Array.isArray(results) || results.length === 0) {
        log('warn', `Empty response for batch #${batchNum}`);
        return { results: [], unprocessed: words };
    }

    const processedMap = new Map();
    for (const item of results) {
        const cleanItem = {
            word: (item.a_word || "").toLowerCase(),
            rus_word: item.e_rus_word || "",
            prompt: item.f_prompt || "",
            _sgr: {
                category: item.b_category || "",
                analysis: item.c_analysis || "",
                risks: item.d_risks || [],
                confidence: item.g_confidence || 50,
                min_age: item.h_min_age || 4,
                content_tags: item.i_content_tags || [],
                selected_mascot: item.j_selected_mascot || "none",
            }
        };
        if (cleanItem.word) processedMap.set(cleanItem.word, cleanItem);
    }

    const validResults = [];
    const unprocessed = [];

    for (const word of words) {
        const item = processedMap.get(word);
        if (!item) {
            unprocessed.push(word);
            continue;
        }

        const isForbidden = item._sgr.min_age === 18 || item.prompt.trim() === "" || item._sgr.content_tags.includes('adult_theme');

        if (isForbidden) {
            logSkippedWord(word, `Forbidden content (Age: ${item._sgr.min_age})`);
        } else {
            validResults.push(item);
        }
    }

    log('success', `Batch #${batchNum}: ${validResults.length} saved, ${unprocessed.length} unprocessed`);
    return { results: validResults, unprocessed };
}

function appendToCSV(csvPath, rows) {
    const fileExists = existsSync(csvPath);
    const header = 'word,rus_word,prompt,confidence,min_age,content_tags,selected_mascot\n';
    let content = '';
    if (!fileExists) content += header;

    for (const row of rows) {
        const escape = (str) => (str || '').replace(/"/g, '""');
        const tagsStr = (row._sgr.content_tags || []).join('|');
        content += `${row.word},${row.rus_word},"${escape(row.prompt)}",${row._sgr.confidence},${row._sgr.min_age},"${tagsStr}",${row._sgr.selected_mascot}\n`;
    }
    appendFileSync(csvPath, content, 'utf-8');
}

function appendToSGRJson(jsonPath, rows) {
    let existing = [];
    if (existsSync(jsonPath)) { try { existing = JSON.parse(readFileSync(jsonPath, 'utf-8')); } catch {} }
    writeFileSync(jsonPath, JSON.stringify([...existing, ...rows], null, 2), 'utf-8');
}

// Find batch starting after lastProcessed word
function findResumeBatch(provider, lastProcessed) {
    while (true) {
        const batch = provider.next(CONFIG.BATCH_SIZE);
        if (batch.length === 0) return batch;

        const idx = batch.indexOf(lastProcessed);
        if (idx === -1) continue;  // word not in this batch, try next

        // Found - truncate or skip to next
        if (idx >= batch.length - 1) {
            // lastProcessed is last word - return next batch
            return provider.next(CONFIG.BATCH_SIZE);
        } else {
            // Truncate to words after lastProcessed
            return batch.slice(idx + 1);
        }
    }
}

async function main() {
    log('info', 'Flashcard Prompt Generator');
    log('info', `Provider: ${CONFIG.DATA_PROVIDER}`);

    try {
        const processed = loadCheckpoint(CONFIG.OUTPUT_CSV);
        log('info', `Loaded checkpoint: ${processed.size} words processed.`);

        const provider = createProvider();
        provider.init();
        log('info', `Provider ready: ${provider.remaining()} words total`);

        // Resume from checkpoint: find batch with first unprocessed word
        let batch = null;
        const lastProcessed = processed.size > 0 ? [...processed][processed.size - 1] : null;
        if (lastProcessed) {
            log('info', `Resuming from after: ${lastProcessed}`);
            batch = findResumeBatch(provider, lastProcessed);
        } else {
            batch = provider.next(CONFIG.BATCH_SIZE);
        }

        let totalSaved = 0;
        let batchNum = 0;

        do {
            batchNum++;
            log('info', `Batch #${batchNum} | Size: ${batch.length}`);

            try {
                const { results, unprocessed } = await processBatchWithCarryover(batch, batchNum);

                if (results.length > 0) {
                    appendToCSV(CONFIG.OUTPUT_CSV, results);
                    appendToSGRJson(CONFIG.OUTPUT_JSON, results);
                    totalSaved += results.length;
                    results.forEach(r => processed.add(r.word));
                }

                log('info', `Total Saved: ${totalSaved} words`);
                await sleep(3000 + Math.random() * 2000);

            } catch (err) {
                log('error', `Batch #${batchNum} Failed: ${err.message}`);
                await sleep(15000);
            }

            batch = provider.next(CONFIG.BATCH_SIZE);
        } while (batch.length > 0);

        log('success', 'Generation Complete!');
        log('info', `CSV: ${CONFIG.OUTPUT_CSV}`);
        log('info', `Reasoning: ${CONFIG.OUTPUT_JSON}`);
        log('info', `Skipped: ${CONFIG.SKIPPED_LOG}`);

    } catch (err) {
        log('error', `Fatal Error: ${err.message}`);
        console.error(err.stack);
    }
}

main();
