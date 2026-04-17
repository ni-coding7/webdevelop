# GEO Score™ Content Generator
**Framework by Nico Fioretti · Cost-Optimized Build**

## Setup & Avvio

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Strategia Token Saving (implementata in app.py)

| Tecnica | Risparmio Stimato |
|---------|------------------|
| GEO Criteria come costante Python (no runtime Excel read) | ~100% overhead lettura file |
| One-Shot Generation (1 call → 4 sezioni) | ~65% vs 4 chiamate separate |
| System Prompt imperativo, no prosa | ~30% vs system prompt verboso |
| Anthropic Prefill trick (`{` come assistant turn) | ~10-20 token per call |
| `response_format: json_object` (OpenAI) | elimina preamble verbale |
| `temperature=0.7` | previene degenerazioni verbose |

## Modelli Consigliati

- **Massimo risparmio:** `gpt-4o-mini` (~$0.001/generazione) o `claude-haiku-4-5-20251001` (~$0.0008/generazione)
- **Qualità premium:** `gpt-4o` o `claude-sonnet-4-6`

## Output Generato (one-shot)

1. 🏠 **Homepage** — H1, intro citabile, 2 sezioni, CTA
2. 📄 **Pagina Servizio** — H1, intro, come funziona (steps), benefici, CTA
3. ❓ **FAQ (5 domande)** — query reali AI, risposte autonome
4. 🔗 **Schema Markup JSON-LD** — Organization + FAQPage, WordPress-ready
