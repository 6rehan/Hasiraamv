// Ginger: a task-routed multi-model system. Each request is classified by task type and
// sent to whichever configured role handles that task -- "main" (general chat, meant to
// run on a Qwen model) for everyday messages, "reasoning" (meant to run on a DeepSeek
// model) for code and multi-step reasoning. "Mufasa" is this combined system's reply
// identity, independent of which underlying model actually answered.
//
// Every role is provider-agnostic: it only needs an OpenAI-compatible chat-completions
// endpoint, a bearer key and a model id, so a role can point at Groq, OpenRouter, or any
// other OpenAI-compatible host purely through env vars -- no code change to swap models.
// Not configured means the endpoint returns 501, same pattern as chatbot.js.

const PROVIDER_ENDPOINTS = {
  groq: 'https://api.groq.com/openai/v1/chat/completions',
  openrouter: 'https://openrouter.ai/api/v1/chat/completions',
};

// First matching rule wins. Kept to cheap heuristics -- routing shouldn't cost a model call.
const TASK_RULES = [
  {
    task: 'reasoning',
    test: (text) =>
      /```|\bstack ?trace\b|\btraceback\b|\bsyntax error\b|\bexception\b|\bdef\s+\w+\(|\bfunction\s*\(|\bclass\s+\w+|=>|\bstep by step\b|\bprove\b|\bcalculate\b|\bequation\b/i.test(
        text,
      ),
  },
];

function classifyTask(message) {
  for (const rule of TASK_RULES) {
    if (rule.test(message)) return rule.task;
  }
  return 'main';
}

// Roles read from GINGER_<ROLE>_PROVIDER / _MODEL / _KEY, falling back to GROQ_API_KEY
// so the existing chatbot's key covers Ginger too when a role has no key of its own.
function roleConfig(env, role) {
  const upper = role.toUpperCase();
  return {
    provider: env[`GINGER_${upper}_PROVIDER`] || 'groq',
    model: env[`GINGER_${upper}_MODEL`],
    key: env[`GINGER_${upper}_KEY`] || env.GROQ_API_KEY,
  };
}

function isConfigured(config) {
  return Boolean(config.model && config.key && PROVIDER_ENDPOINTS[config.provider]);
}

async function callRole(config, messages) {
  const res = await fetch(PROVIDER_ENDPOINTS[config.provider], {
    method: 'POST',
    headers: {
      authorization: `Bearer ${config.key}`,
      'content-type': 'application/json',
    },
    body: JSON.stringify({ model: config.model, messages, max_tokens: 600, temperature: 0.3 }),
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => '');
    throw new Error(`${config.provider} ${config.model} error ${res.status}: ${detail}`);
  }

  const data = await res.json();
  const reply = data.choices?.[0]?.message?.content?.trim();
  if (!reply) throw new Error(`${config.provider} ${config.model} returned no content`);
  return reply;
}

function systemPrompt(env) {
  return (
    env.GINGER_SYSTEM_PROMPT ||
    'You are Mufasa, the assistant persona of the Ginger system. Answer clearly and concisely.'
  );
}

export async function handleGinger(request, env) {
  const main = roleConfig(env, 'main');
  if (!isConfigured(main)) {
    return new Response(JSON.stringify({ error: 'Ginger is not set up yet.' }), {
      status: 501,
      headers: { 'content-type': 'application/json' },
    });
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Bad request.' }), { status: 400 });
  }

  const message = String(body?.message || '').trim().slice(0, 4000);
  if (!message) return new Response(JSON.stringify({ error: 'Empty message.' }), { status: 400 });

  const history = Array.isArray(body?.history)
    ? body.history
        .slice(-8)
        .filter((m) => m && (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string')
        .map((m) => ({ role: m.role, content: String(m.content).slice(0, 4000) }))
    : [];

  const messages = [
    { role: 'system', content: systemPrompt(env) },
    ...history,
    { role: 'user', content: message },
  ];

  // Caller can force a role (e.g. a UI toggle); otherwise route by content.
  const requestedTask = typeof body?.task === 'string' ? body.task : null;
  const task = requestedTask && requestedTask !== 'main' ? requestedTask : classifyTask(message);

  let config = task === 'main' ? main : roleConfig(env, task);
  let usedRole = task;
  if (task !== 'main' && !isConfigured(config)) {
    // Supporting role not configured -- fall back to main rather than failing the request.
    config = main;
    usedRole = 'main';
  }

  try {
    const reply = await callRole(config, messages);
    return new Response(JSON.stringify({ reply, role: usedRole, model: config.model }), {
      headers: { 'content-type': 'application/json' },
    });
  } catch (err) {
    console.error('Ginger role failed:', usedRole, err);
    if (usedRole !== 'main') {
      // Supporting role errored at request time -- retry once on main before giving up.
      try {
        const reply = await callRole(main, messages);
        return new Response(JSON.stringify({ reply, role: 'main', model: main.model }), {
          headers: { 'content-type': 'application/json' },
        });
      } catch (fallbackErr) {
        console.error('Ginger main fallback also failed:', fallbackErr);
      }
    }
    return new Response(
      JSON.stringify({ reply: "Sorry, Ginger couldn't reach a model just now. Try again shortly." }),
      { headers: { 'content-type': 'application/json' } },
    );
  }
}
