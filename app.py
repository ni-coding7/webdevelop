"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     GEO Score™ Content Generator v2 — Alligator Edition                    ║
║     Senior Python Developer & Prompt Engineer Build                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

CHANGELOG v2:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OBJ 1 — BUG FIX JSON & OUTPUT TRONCATO
  • max_tokens esplicito per modello (MODEL_MAX_TOKENS dict)
  • Generazione Modulare: checkbox per sezione → 1 call per sezione
    → output ~1200 tok max → nessun troncamento su Haiku/mini
  • repair_json(): stack-based closer per { [ mancanti → salva output parziali

OBJ 2 — LOCAL SEO / SCHEMA
  • Nuovi campi: Via/CAP/Città/Prov, GPS, griglia orari Lun-Dom
  • build_final_schema() inietta tutto in LocalBusiness JSON-LD
  • Auto-detect: LocalBusiness se indirizzo presente, Organization altrimenti

OBJ 3 — STYLE BRAND ALLIGATOR
  • Campo "Esempi di Stile/Copy" nel debrief
  • System prompt: regole Alligator (diretto, risultati, no trend vuoti)
  • Analisi tono dagli esempi → replicato nei testi generati

OBJ 4 — EFFICIENZA & COSTI
  • claude-haiku-4-5-20251001 default (💰), claude-sonnet-4-6 premium (🔋)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import streamlit as st
import json
import re
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 1: GEO CRITERIA CONSTANT
# Estratto da GEO_Score_Nico_Fioretti.xlsx — hardcoded per 0 token overhead.
# ─────────────────────────────────────────────────────────────────────────────
GEO_CRITERIA = """GEO SCORE™ — 8 DIMENSIONI (Nico Fioretti):
1.TECNICA: AI bot non bloccati in robots.txt, HTML senza JS, Schema JSON-LD valido, velocità<3s, HTTPS.
2.CONTENUTO: Risposta diretta entro 2 paragrafi, dati originali, ≥1 numero ogni 2 paragrafi, cluster tematici, journey completo.
3.IDENTITÀ: Nome brand consistente, sameAs schema, allineamento cross-platform, associazione topic-brand nei motori AI.
4.LEGGIBILITÀ: Incipit con risposta, H2/H3 descrittivi, 1 idea/paragrafo, claim autonomi out-of-context, formati strutturati (3x citati).
5.AUTORITÀ: Menzioni siti terzi, claim con fonti esterne, directory/review, link .gov/.edu, Digital PR attiva.
6.CREDIBILITÀ: Autori con bio+LinkedIn, fonti citate ≥2-3/pagina, ricerca originale, trust signals on-site (P.IVA, team, cert.).
7.UNICITÀ: Framework proprietario con nome, differenziazione in 1 frase, zero cliché→dati concreti, concetti branded attributi.
8.FRESCHEZZA: Pagine chiave revisionate ogni 6 mesi, date accurate, statistiche ≤18 mesi, gestione contenuti obsoleti."""

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 2: PRICING & MODEL CONFIG
# OBJ 4: haiku = default economico, sonnet = premium
# ─────────────────────────────────────────────────────────────────────────────
PRICING = {
    "openai": {
        "gpt-4o-mini":  {"input": 0.00015, "output": 0.00060},
        "gpt-4o":       {"input": 0.00250, "output": 0.01000},
        "gpt-4.1-mini": {"input": 0.00040, "output": 0.00160},
        "gpt-4.1":      {"input": 0.00200, "output": 0.00800},
    },
    "anthropic": {
        "claude-haiku-4-5-20251001":  {"input": 0.00025, "output": 0.00125},
        "claude-sonnet-4-6":          {"input": 0.00300, "output": 0.01500},
        "claude-opus-4-6":            {"input": 0.01500, "output": 0.07500},
    }
}

MODEL_LABELS = {
    "claude-haiku-4-5-20251001":  "Claude Haiku 💰 (default economico)",
    "claude-sonnet-4-6": "Claude Sonnet 3.5 🔋 (premium)",
    "claude-opus-4-6":   "Claude Opus 3 💎 (massima qualità)",
    "gpt-4o-mini":       "GPT-4o Mini 💰 (default economico)",
    "gpt-4o":            "GPT-4o 🔋 (premium)",
    "gpt-4.1-mini":      "GPT-4.1 Mini 💰",
    "gpt-4.1":           "GPT-4.1 🔋",
}

# OBJ 1: max_tokens esplicito per modello — evita troncature silenziose
MODEL_MAX_TOKENS = {
    "gpt-4o-mini":              4096,
    "gpt-4o":                   4096,
    "gpt-4.1-mini":             4096,
    "gpt-4.1":                  4096,
    "claude-haiku-4-5-20251001":       4096,
    "claude-sonnet-4-6":        8192,
    "claude-opus-4-6":          4096,
}

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 3: TOKEN UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def estimate_cost(input_tokens: int, output_tokens: int, provider: str, model: str) -> float:
    try:
        p = PRICING[provider][model]
        return (input_tokens / 1000 * p["input"]) + (output_tokens / 1000 * p["output"])
    except KeyError:
        return 0.0

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 4: REPAIR JSON (OBJ 1)
# Stack-based: traccia parentesi aperte ignorando quelle in stringhe.
# Chiude nella sequenza inversa corretta → salva output parziali da troncatura.
# ─────────────────────────────────────────────────────────────────────────────
def repair_json(text: str) -> str:
    if not text:
        return text

    text = re.sub(r"```(?:json)?", "", text).strip()
    if text.endswith(","):
        text = text[:-1]

    stack = []
    in_string = False
    escape_next = False

    for char in text:
        if escape_next:
            escape_next = False
            continue
        if char == "\\" and in_string:
            escape_next = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char in "{[":
            stack.append(char)
        elif char in "}]":
            if stack:
                stack.pop()

    closers = {"{": "}", "[": "]"}
    for opener in reversed(stack):
        text += closers[opener]

    return text

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 5: SYSTEM PROMPT BUILDER (OBJ 3 — Alligator Style)
# ─────────────────────────────────────────────────────────────────────────────
def build_system_prompt(stile_esempi: str = "") -> str:
    alligator_rules = """APPROCCIO ALLIGATOR (OBBLIGATORIO):
- DIRETTO: Frasi brevi. Soggetto + Verbo + Oggetto. Zero giri di parole.
- RISULTATI: Ogni affermazione ha una conseguenza misurabile per il cliente.
- NO TREND VUOTI: Vietato "digital transformation", "ecosistema", "sinergie", "paradigma". Sostituisci con un dato.
- AUTOREVOLE TECNICO: Terminologia di settore. Il lettore è esperto.
- LEGGIBILE: Periodi max 20 parole. Sottotitoli ogni 100 parole."""

    style_section = ""
    if stile_esempi and stile_esempi.strip():
        style_section = f"""
ANALISI TONO DI VOCE — ESEMPI REALI DEL BRAND:
---
{stile_esempi.strip()}
---
ISTRUZIONE STILE: Analizza i testi sopra. Identifica lunghezza media frasi, vocabolario ricorrente, struttura titoli, uso numeri. Replica ESATTAMENTE quel tono. Non interpretare, non migliorare: replica."""

    return f"""Sei il copywriter GEO/SEO senior di Alligator. Generi contenuti web ad alta citabilità AI.

{alligator_rules}
{style_section}

FRAMEWORK GEO SCORE:
{GEO_CRITERIA}

REGOLE OUTPUT (ASSOLUTE):
- Rispondi SOLO con JSON valido. Zero testo fuori dal JSON.
- NO introduzioni, NO conclusioni, NO commenti, NO markdown fuori JSON.
- Ogni sezione: minimo 1 dato numerico citabile.
- Claim autonomi: ogni frase chiave ha senso estratta fuori contesto.
- Zero cliché: sostituisci "leader/eccellente/innovativo/qualità" con dati."""

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6: PROMPT MODULARI (OBJ 1)
# Una funzione per sezione → output ~800-1200 token max → no troncature.
# ─────────────────────────────────────────────────────────────────────────────
def build_ctx(azienda, servizi, target, fatti, local_seo, lingua) -> str:
    addr = local_seo.get("indirizzo", "")
    return f"""AZIENDA: {azienda}
SERVIZI: {servizi}
TARGET: {target}
FATTI CITABILI: {fatti}
INDIRIZZO: {addr if addr else "Non specificato"}
LINGUA: {lingua}"""


def prompt_home(ctx: str) -> str:
    return f"""{ctx}

Genera SOLO il blocco "home". Rispondi ESCLUSIVAMENTE con questo JSON:
{{
  "home": {{
    "h1": "Titolo H1 max 60 char, keyword principale",
    "intro": "150-200 parole. Prima frase = risposta diretta. 1 dato numerico. Stile Alligator.",
    "sezione_1": {{
      "h2": "H2 valore concreto non generico",
      "body": "100-150 parole. Dato numerico o fatto unico dal debrief."
    }},
    "sezione_2": {{
      "h2": "H2 differenziazione specifica",
      "body": "100-150 parole. Unicità con dati concreti, zero cliché."
    }},
    "cta": "1 frase imperativa e specifica"
  }}
}}"""


def prompt_servizio(ctx: str) -> str:
    return f"""{ctx}

Genera SOLO il blocco "pagina_servizio". Rispondi ESCLUSIVAMENTE con questo JSON:
{{
  "pagina_servizio": {{
    "h1": "H1 pagina servizio con keyword long-tail",
    "intro": "100-150 parole. Cosa ottiene il cliente, non cosa fa l'azienda.",
    "come_funziona": {{
      "h2": "Come funziona [Servizio] — titolo descrittivo",
      "steps": [
        "Step 1: azione concreta max 2 righe",
        "Step 2: azione concreta max 2 righe",
        "Step 3: azione concreta max 2 righe",
        "Step 4: azione concreta max 2 righe"
      ]
    }},
    "benefici": {{
      "h2": "Titolo con numero specifico es. 4 risultati che ottieni",
      "lista": [
        "Beneficio 1 + dato numerico verificabile",
        "Beneficio 2 + dato numerico verificabile",
        "Beneficio 3 + dato numerico verificabile",
        "Beneficio 4 + dato numerico verificabile"
      ]
    }},
    "cta": "CTA specifica al servizio, imperativa"
  }}
}}"""


def prompt_faq(ctx: str) -> str:
    return f"""{ctx}

Genera SOLO il blocco "faq" con 5 domande. Rispondi ESCLUSIVAMENTE con questo JSON:
{{
  "faq": [
    {{
      "domanda": "Query reale motore AI — inizia con Come/Cosa/Quanto/Perche/Chi",
      "risposta": "80-120 parole. Autonoma fuori contesto. Include dato concreto."
    }},
    {{"domanda": "Domanda 2", "risposta": "Risposta 2 80-120 parole"}},
    {{"domanda": "Domanda 3", "risposta": "Risposta 3 80-120 parole"}},
    {{"domanda": "Domanda 4", "risposta": "Risposta 4 80-120 parole"}},
    {{"domanda": "Domanda 5", "risposta": "Risposta 5 80-120 parole"}}
  ]
}}"""


def prompt_schema(ctx: str, azienda: str, local_seo: dict, faq_data: list) -> str:
    """OBJ 2: Inietta dati Local SEO nel prompt → modello genera schema base."""
    indirizzo = local_seo.get("indirizzo", "")
    url_sito  = local_seo.get("url", "https://www.esempio.it")
    linkedin  = local_seo.get("linkedin", "")
    schema_type = "LocalBusiness" if indirizzo.strip() else "Organization"

    orari = local_seo.get("orari", {})
    orari_str = ""
    giorni_map = {"Lunedi":"Monday","Martedi":"Tuesday","Mercoledi":"Wednesday",
                  "Giovedi":"Thursday","Venerdi":"Friday","Sabato":"Saturday","Domenica":"Sunday"}
    for g, (ap, ch) in orari.items():
        if ap and ch:
            g_clean = g.replace("ì","i").replace("è","e").replace("é","e")
            orari_str += f"{giorni_map.get(g_clean, g)}: {ap}-{ch} | "

    return f"""{ctx}
SCHEMA TYPE: {schema_type}
URL: {url_sito}
LINKEDIN: {linkedin if linkedin else "da compilare"}
ORARI: {orari_str if orari_str else "non specificati"}

Genera SOLO il blocco "schema_markup". Rispondi ESCLUSIVAMENTE con questo JSON:
{{
  "schema_markup": {{
    "organization": {{
      "@context": "https://schema.org",
      "@type": "{schema_type}",
      "name": "{azienda}",
      "description": "Descrizione 160 char max con keyword principale",
      "url": "{url_sito}",
      "sameAs": ["{linkedin if linkedin else 'https://www.linkedin.com/company/esempio'}"],
      "knowsAbout": ["Topic specifico 1", "Topic specifico 2", "Topic specifico 3"]
    }}
  }}
}}"""

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 7: API CALL HANDLERS
# OBJ 1: max_tokens esplicito, prefill Anthropic
# ─────────────────────────────────────────────────────────────────────────────
def call_openai(api_key: str, model: str, system: str, user: str) -> tuple:
    try:
        from openai import OpenAI
        client  = OpenAI(api_key=api_key)
        max_tok = MODEL_MAX_TOKENS.get(model, 4000)
        resp    = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.7,
            max_tokens=max_tok,
            response_format={"type": "json_object"}
        )
        return resp.choices[0].message.content, resp.usage.prompt_tokens, resp.usage.completion_tokens
    except ImportError:
        return None, 0, 0
    except Exception as e:
        raise e


def call_anthropic(api_key: str, model: str, system: str, user: str) -> tuple:
    try:
        import anthropic
        client  = anthropic.Anthropic(api_key=api_key)
        max_tok = MODEL_MAX_TOKENS.get(model, 4000)
        resp    = client.messages.create(
            model=model,
            max_tokens=max_tok,
            system=system,
            messages=[
                {"role": "user",      "content": user},
                {"role": "assistant", "content": "{"}  # Prefill: forza JSON, elimina preamble
            ],
            temperature=0.7
        )
        content = "{" + resp.content[0].text
        return content, resp.usage.input_tokens, resp.usage.output_tokens
    except ImportError:
        return None, 0, 0
    except Exception as e:
        raise e


def call_api(provider, api_key, model, system, user):
    if provider == "openai":
        return call_openai(api_key, model, system, user)
    return call_anthropic(api_key, model, system, user)

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 8: JSON PARSER ROBUSTO (OBJ 1)
# Cascata: parsing diretto → estrazione blocco → repair_json
# ─────────────────────────────────────────────────────────────────────────────
def parse_json_response(raw: str) -> Optional[dict]:
    if not raw:
        return None
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    # Tentativo 1: parsing diretto
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Tentativo 2: estrai primo blocco JSON
    start = cleaned.find("{")
    end   = cleaned.rfind("}") + 1
    if start != -1 and end > start:
        chunk = cleaned[start:end]
        try:
            return json.loads(chunk)
        except json.JSONDecodeError:
            pass
        # Tentativo 3: repair_json su chunk parziale
        repaired = repair_json(chunk)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass
    return None

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 9: SCHEMA MARKUP BUILDER (OBJ 2)
# Sovrascrive in Python i campi Local SEO — più affidabile che aspettarsi
# che il modello abbia compilato correttamente indirizzi/coordinate/orari.
# ─────────────────────────────────────────────────────────────────────────────
def build_final_schema(data: dict, local_seo: dict, azienda: str) -> str:
    schema_raw = data.get("schema_markup", {})
    org        = dict(schema_raw.get("organization", {}))
    faqs       = data.get("faq", [])

    indirizzo = local_seo.get("indirizzo", "").strip()
    gps_lat   = local_seo.get("gps_lat",   "").strip()
    gps_lon   = local_seo.get("gps_lon",   "").strip()
    orari     = local_seo.get("orari",     {})
    url_sito  = local_seo.get("url",       "https://www.esempio.it").strip()
    linkedin  = local_seo.get("linkedin",  "").strip()

    schema_type    = "LocalBusiness" if indirizzo else "Organization"
    org["@type"]   = schema_type
    org["@context"] = "https://schema.org"
    org["name"]    = azienda
    if url_sito:    org["url"]     = url_sito
    if linkedin:    org["sameAs"]  = [linkedin]

    # Indirizzo strutturato (OBJ 2)
    if indirizzo:
        parts  = [p.strip() for p in indirizzo.split(",")]
        org["address"] = {
            "@type":           "PostalAddress",
            "streetAddress":   parts[0] if len(parts) > 0 else "",
            "addressLocality": parts[1] if len(parts) > 1 else "",
            "postalCode":      parts[2] if len(parts) > 2 else "",
            "addressRegion":   parts[3] if len(parts) > 3 else "",
            "addressCountry":  "IT"
        }

    # Coordinate GPS (OBJ 2)
    if gps_lat and gps_lon:
        try:
            org["geo"] = {
                "@type":     "GeoCoordinates",
                "latitude":  float(gps_lat),
                "longitude": float(gps_lon)
            }
        except ValueError:
            pass

    # openingHoursSpecification dalla griglia (OBJ 2)
    giorni_map = {
        "Lunedì": "Monday", "Martedì": "Tuesday", "Mercoledì": "Wednesday",
        "Giovedì": "Thursday", "Venerdì": "Friday", "Sabato": "Saturday", "Domenica": "Sunday"
    }
    oh = []
    for g_it, (apertura, chiusura) in orari.items():
        if apertura and chiusura:
            oh.append({
                "@type":     "OpeningHoursSpecification",
                "dayOfWeek": f"https://schema.org/{giorni_map.get(g_it, g_it)}",
                "opens":     apertura,
                "closes":    chiusura
            })
    if oh:
        org["openingHoursSpecification"] = oh

    # FAQPage con FAQ reali
    faq_schema = {
        "@context": "https://schema.org",
        "@type":    "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name":  f.get("domanda", ""),
                "acceptedAnswer": {"@type": "Answer", "text": f.get("risposta", "")}
            }
            for f in faqs
        ]
    }

    return json.dumps({"@context": "https://schema.org", "@graph": [org, faq_schema]},
                      ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 10: UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def copy_box(label, text, key):
    st.text_area(label, value=text, height=200, key=key,
                 help="Ctrl+A per selezionare tutto → Ctrl+C per copiare")

def render_home(home):
    st.markdown(f"**H1:** `{home.get('h1','')}`")
    st.markdown(f"**Intro:**\n\n{home.get('intro','')}")
    for k, lbl in [("sezione_1","Sezione 1"),("sezione_2","Sezione 2")]:
        s = home.get(k,{})
        if s:
            st.markdown(f"**H2 {lbl}:** `{s.get('h2','')}`")
            st.markdown(s.get("body",""))
    st.markdown(f"**CTA:** _{home.get('cta','')}_")

def render_service(page):
    st.markdown(f"**H1:** `{page.get('h1','')}`")
    st.markdown(f"**Intro:**\n\n{page.get('intro','')}")
    cf = page.get("come_funziona",{})
    if cf:
        st.markdown(f"**H2:** `{cf.get('h2','')}`")
        for step in cf.get("steps",[]):
            st.markdown(f"- {step}")
    ben = page.get("benefici",{})
    if ben:
        st.markdown(f"**H2:** `{ben.get('h2','')}`")
        for b in ben.get("lista",[]):
            st.markdown(f"✅ {b}")
    st.markdown(f"**CTA:** _{page.get('cta','')}_")

def render_faq(faqs):
    for i, faq in enumerate(faqs, 1):
        with st.expander(f"❓ {faq.get('domanda', f'FAQ {i}')}"):
            st.markdown(faq.get("risposta",""))

def home_to_md(h):
    t = f"# {h.get('h1','')}\n\n{h.get('intro','')}\n\n"
    for k in ["sezione_1","sezione_2"]:
        s = h.get(k,{})
        if s: t += f"## {s.get('h2','')}\n\n{s.get('body','')}\n\n"
    t += h.get("cta","")
    return t

def service_to_md(p):
    t = f"# {p.get('h1','')}\n\n{p.get('intro','')}\n\n"
    cf = p.get("come_funziona",{})
    if cf:
        t += f"## {cf.get('h2','')}\n\n"
        for s in cf.get("steps",[]): t += f"- {s}\n"
        t += "\n"
    ben = p.get("benefici",{})
    if ben:
        t += f"## {ben.get('h2','')}\n\n"
        for b in ben.get("lista",[]): t += f"✅ {b}\n"
        t += "\n"
    t += p.get("cta","")
    return t

def faq_to_md(faqs):
    t = "## Domande Frequenti\n\n"
    for f in faqs:
        t += f"### {f.get('domanda','')}\n\n{f.get('risposta','')}\n\n"
    return t

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 11: MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="GEO Score™ v2 — Alligator",
        page_icon="🐊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    <style>
    .geo-header {
        background: linear-gradient(135deg, #0d1117 0%, #1a2332 50%, #0f3460 100%);
        color: white; padding: 1.4rem 2rem; border-radius: 10px; margin-bottom: 1.2rem;
    }
    .geo-header h1 { margin: 0; font-size: 1.8rem; }
    .geo-header p  { margin: 0.3rem 0 0; opacity: 0.75; font-size: 0.9rem; }
    .cost-box {
        background: #f0f9ff; border-left: 4px solid #0ea5e9;
        padding: 0.7rem 1rem; border-radius: 6px; margin: 0.4rem 0; font-size: 0.88rem;
    }
    .module-card {
        border: 1px solid #e2e8f0; border-radius: 8px;
        padding: 0.75rem 1rem; margin: 0.3rem 0; background: #fafafa;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="geo-header">
        <h1>🐊 GEO Score™ Content Generator v2 — Alligator Edition</h1>
        <p>Generazione Modulare · Local SEO · Style Replication · Framework GEO Score™ by Nico Fioretti</p>
    </div>
    """, unsafe_allow_html=True)

    # ── SIDEBAR ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Configurazione API")

        provider = st.selectbox("Provider AI", ["anthropic", "openai"],
                                format_func=lambda x: "🟠 Anthropic" if x=="anthropic" else "🟢 OpenAI")

        if provider == "openai":
            opts, dflt = list(PRICING["openai"].keys()), "gpt-4o-mini"
        else:
            opts, dflt = list(PRICING["anthropic"].keys()), "claude-haiku-4-5-20251001"

        model = st.selectbox("Modello", opts,
                             index=opts.index(dflt) if dflt in opts else 0,
                             format_func=lambda m: MODEL_LABELS.get(m, m))

        api_key = st.text_input("🔑 API Key", type="password",
                                placeholder="sk-... oppure sk-ant-...")

        st.divider()
        st.subheader("💰 Stima Costi")
        sys_tok = estimate_tokens(build_system_prompt())
        in_est  = sys_tok + 300
        out_est = 1200
        cpp     = estimate_cost(in_est, out_est, provider, model)
        st.markdown(f"""
        <div class="cost-box">
            <b>Per sezione (modulare):</b><br>
            Input ~{in_est:,} tok · Output ~{out_est:,} tok<br>
            <b>Costo/sezione: ${cpp:.5f}</b><br>
            4 sezioni totali: <b>~${cpp*4:.5f}</b>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        with st.expander("📖 GEO 8 Dimensioni (hardcoded)"):
            st.markdown("1.⚙️Tecnica · 2.📝Contenuto · 3.🏷️Identità · 4.🔍Leggibilità\n5.🌐Autorità · 6.🏅Credibilità · 7.💎Unicità · 8.🔄Freschezza\n\n*0 token overhead — costante Python*")

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📋 Debrief", "🛠️ Generatore", "📄 Risultati"])

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 1: DEBRIEF
    # ═══════════════════════════════════════════════════════════════════════
    with tab1:
        st.subheader("📋 Debrief Azienda")

        st.markdown("#### 🏢 Identità Brand")
        c1, c2 = st.columns(2)
        with c1:
            azienda = st.text_input("Nome Azienda *", key="azienda",
                                    placeholder="es. Alligator Digital")
            servizi = st.text_area("Servizi Principali *", key="servizi", height=100,
                                   placeholder="es. GEO Optimization, Content Strategy, SEO Tecnico")
        with c2:
            target  = st.text_area("Target / Clienti Ideali *", key="target", height=100,
                                   placeholder="es. PMI italiane, Marketing Manager, e-commerce B2B")
            lingua  = st.selectbox("Lingua Output", ["italiano","inglese","francese","spagnolo"],
                                   key="lingua")

        fatti = st.text_area("💡 Fatti Unici & Citabili *", key="fatti", height=130,
                              placeholder='"94% tasso citazione AI dopo 90gg" · "Unici in Italia con GEO Score™" · "200+ brand ottimizzati"')

        st.divider()

        # OBJ 3: STYLE BRAND ────────────────────────────────────────────
        st.markdown("#### 🐊 Tono di Voce — Esempi Reali di Copy")
        st.caption("Il modello analizza questi testi e replica esattamente il tono nei contenuti generati.")
        stile_esempi = st.text_area(
            "Esempi di Stile/Copy (opzionale — fortemente consigliato)",
            key="stile_esempi", height=150,
            placeholder='"Non vendiamo visibilità. Costruiamo autorità che dura."\n"Il tuo brand esiste per i motori AI? Scoprilo in 48h con il GEO Audit."\n"Meno traffico inutile. Più richieste qualificate. Dati alla mano."'
        )

        st.divider()

        # OBJ 2: LOCAL SEO DATA ─────────────────────────────────────────
        st.markdown("#### 📍 Dati Local SEO (Schema Markup)")
        st.caption("Compilati automaticamente in JSON-LD LocalBusiness se l'indirizzo è presente.")

        col_a, col_b = st.columns(2)
        with col_a:
            via_civico = st.text_input("Via e Numero Civico", key="via",
                                       placeholder="es. Via Roma 42")
            cap        = st.text_input("CAP",      key="cap",  placeholder="20121")
            citta      = st.text_input("Città",    key="citta",placeholder="Milano")
            provincia  = st.text_input("Provincia",key="prov", placeholder="MI")
        with col_b:
            url_sito = st.text_input("URL Sito Web",         key="url_sito",
                                      placeholder="https://www.alligator.it")
            linkedin = st.text_input("URL LinkedIn Company", key="linkedin",
                                      placeholder="https://www.linkedin.com/company/alligator")
            gps_lat  = st.text_input("Latitudine GPS (opz.)",key="gps_lat",
                                      placeholder="45.4654219")
            gps_lon  = st.text_input("Longitudine GPS (opz.)",key="gps_lon",
                                      placeholder="9.1859243")

        # GRIGLIA ORARI ─────────────────────────────────────────────────
        st.markdown("**🕐 Orari di Apertura** *(lascia vuoto = chiuso)*")
        giorni = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
        orari_dict = {}

        h_cols = st.columns([2,2,2])
        h_cols[0].markdown("**Giorno**")
        h_cols[1].markdown("**Apertura**")
        h_cols[2].markdown("**Chiusura**")

        for giorno in giorni:
            row = st.columns([2,2,2])
            row[0].markdown(f"*{giorno}*")
            ap = row[1].text_input("", key=f"ap_{giorno}", placeholder="09:00",
                                    label_visibility="collapsed")
            ch = row[2].text_input("", key=f"ch_{giorno}", placeholder="18:00",
                                    label_visibility="collapsed")
            orari_dict[giorno] = (ap, ch)

        # Componi indirizzo e salva
        indirizzo_completo = ", ".join(filter(None, [
            st.session_state.get("via",""),
            st.session_state.get("citta",""),
            st.session_state.get("cap",""),
            st.session_state.get("prov","")
        ]))

        local_seo = {
            "indirizzo": indirizzo_completo,
            "gps_lat":   st.session_state.get("gps_lat",""),
            "gps_lon":   st.session_state.get("gps_lon",""),
            "orari":     orari_dict,
            "url":       st.session_state.get("url_sito",""),
            "linkedin":  st.session_state.get("linkedin",""),
        }
        st.session_state["local_seo"] = local_seo

        fields_ok = all([
            st.session_state.get("azienda"),
            st.session_state.get("servizi"),
            st.session_state.get("target"),
            st.session_state.get("fatti"),
        ])
        if fields_ok:
            stype = "LocalBusiness 📍" if indirizzo_completo.strip() else "Organization 🌐"
            st.success(f"✅ Debrief completo · Schema: **{stype}**")
        else:
            st.info("💡 Compila i campi obbligatori (*) per sbloccare il Generatore.")

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 2: GENERATORE MODULARE
    # ═══════════════════════════════════════════════════════════════════════
    with tab2:
        st.subheader("🛠️ Generatore Modulare")

        _az   = st.session_state.get("azienda","")
        _sv   = st.session_state.get("servizi","")
        _tg   = st.session_state.get("target","")
        _ft   = st.session_state.get("fatti","")
        _ln   = st.session_state.get("lingua","italiano")
        _st   = st.session_state.get("stile_esempi","")
        _loc  = st.session_state.get("local_seo",{})

        ready = bool(_az and _sv and _tg and _ft and api_key)

        if not ready:
            missing = [x for x,v in [
                ("Nome Azienda",_az),("Servizi",_sv),("Target",_tg),
                ("Fatti",_ft),("API Key (sidebar)",api_key)
            ] if not v]
            st.warning(f"⚠️ Mancano: **{', '.join(missing)}**")

        st.markdown("#### Seleziona le sezioni da generare")
        st.caption("1 sezione = 1 chiamata API (~1200 token output) → nessun troncamento JSON.")

        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            gen_home    = st.checkbox("🏠 Homepage",        value=True, key="gen_home")
            st.caption("H1, intro, 2 sezioni, CTA")
        with mc2:
            gen_service = st.checkbox("📄 Pagina Servizio", value=True, key="gen_service")
            st.caption("H1, come funziona, benefici, CTA")
        with mc3:
            gen_faq     = st.checkbox("❓ FAQ (5 domande)",  value=True, key="gen_faq")
            st.caption("Query AI reali, risposte autonome")
        with mc4:
            gen_schema  = st.checkbox("🔗 Schema Markup",   value=True, key="gen_schema")
            st.caption("JSON-LD LocalBusiness/Org + FAQ")

        n_sel = sum([gen_home, gen_service, gen_faq, gen_schema])

        if n_sel == 0:
            st.warning("Seleziona almeno una sezione.")

        st.divider()

        if ready and n_sel > 0:
            sp_preview = build_system_prompt(_st)
            in_est_r   = estimate_tokens(sp_preview) + 300
            tot_est    = estimate_cost(in_est_r, 1200, provider, model) * n_sel
            st.info(f"📊 **{n_sel} chiamate pianificate** · Costo totale stimato: **${tot_est:.5f}**")

        gen_btn = st.button(
            f"🚀 Genera {n_sel} sezione{'i' if n_sel!=1 else ''}",
            disabled=(not ready or n_sel==0),
            type="primary"
        )

        if gen_btn and ready and n_sel > 0:
            sys_p  = build_system_prompt(_st)
            ctx    = build_ctx(_az, _sv, _tg, _ft, _loc, _ln)

            total_in  = 0
            total_out = 0
            generated = dict(st.session_state.get("generated", {}))
            call_log  = []

            sections = []
            if gen_home:    sections.append("home")
            if gen_service: sections.append("servizio")
            if gen_faq:     sections.append("faq")
            if gen_schema:  sections.append("schema")

            progress = st.progress(0, text="Avvio generazione modulare...")

            for i, section in enumerate(sections):
                progress.progress(int(i/len(sections)*100), text=f"⏳ Generando: **{section}**...")

                try:
                    if section == "home":
                        user_p = prompt_home(ctx)
                    elif section == "servizio":
                        user_p = prompt_servizio(ctx)
                    elif section == "faq":
                        user_p = prompt_faq(ctx)
                    else:
                        faq_data = generated.get("faq", [])
                        user_p   = prompt_schema(ctx, _az, _loc, faq_data)

                    raw, in_t, out_t = call_api(provider, api_key, model, sys_p, user_p)

                    if raw is None:
                        call_log.append((section, False, "❌ Libreria non installata: pip install openai anthropic"))
                        continue

                    parsed = parse_json_response(raw)

                    if parsed:
                        generated.update(parsed)
                        total_in  += in_t
                        total_out += out_t
                        cst = estimate_cost(in_t, out_t, provider, model)
                        call_log.append((section, True, f"{in_t+out_t:,} token · ${cst:.5f}"))
                    else:
                        call_log.append((section, False, f"Parsing fallito · Anteprima: {raw[:80] if raw else 'vuoto'}"))

                except Exception as e:
                    err_msg = str(e)
                    call_log.append((section, False, err_msg[:120]))
                    if "api_key" in err_msg.lower() or "auth" in err_msg.lower():
                        st.error("🔑 API Key non valida — controlla nella sidebar.")
                        break

            progress.progress(100, text="✅ Generazione completata!")

            st.session_state["generated"]  = generated
            st.session_state["in_tokens"]  = total_in
            st.session_state["out_tokens"] = total_out
            real_tot = estimate_cost(total_in, total_out, provider, model)
            st.session_state["real_cost"]  = real_tot

            st.markdown("#### 📊 Report per Sezione")
            for sec, ok, info in call_log:
                icon = "✅" if ok else "❌"
                st.markdown(f"{icon} **{sec}** — {info}")

            if any(ok for _,ok,_ in call_log):
                st.success(f"Token totali: **{total_in+total_out:,}** · Costo reale: **${real_tot:.5f}**")
                st.info("👉 Vai al tab **📄 Risultati**")

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 3: RISULTATI
    # ═══════════════════════════════════════════════════════════════════════
    with tab3:
        st.subheader("📄 Risultati — Pronto per WordPress / Elementor")

        if not st.session_state.get("generated"):
            st.info("🔄 Vai al tab **🛠️ Generatore** per creare i contenuti.")
            st.stop()

        data   = st.session_state["generated"]
        in_t   = st.session_state.get("in_tokens",  0)
        out_t  = st.session_state.get("out_tokens", 0)
        cost_r = st.session_state.get("real_cost",  0.0)
        _loc   = st.session_state.get("local_seo",  {})
        _az    = st.session_state.get("azienda",    "Brand")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Token Input",  f"{in_t:,}")
        m2.metric("Token Output", f"{out_t:,}")
        m3.metric("Totale Token", f"{in_t+out_t:,}")
        m4.metric("Costo Reale",  f"${cost_r:.5f}")

        st.divider()

        # Costruisci tab solo per sezioni disponibili
        avail = []
        if data.get("home"):            avail.append(("🏠 Homepage","home"))
        if data.get("pagina_servizio"): avail.append(("📄 Servizio","servizio"))
        if data.get("faq"):             avail.append(("❓ FAQ","faq"))
        if data.get("schema_markup") or data.get("faq"): avail.append(("🔗 Schema","schema"))

        if not avail:
            st.warning("Nessuna sezione trovata. Ritorna al Generatore.")
            st.stop()

        rtabs = st.tabs([a[0] for a in avail])

        for rtab, (lbl, key) in zip(rtabs, avail):
            with rtab:
                if key == "home":
                    home = data.get("home",{})
                    render_home(home)
                    st.divider()
                    copy_box("📋 Copia Homepage (Markdown/Gutenberg)", home_to_md(home), "cp_home")

                elif key == "servizio":
                    page = data.get("pagina_servizio",{})
                    render_service(page)
                    st.divider()
                    copy_box("📋 Copia Pagina Servizio", service_to_md(page), "cp_serv")

                elif key == "faq":
                    faqs = data.get("faq",[])
                    render_faq(faqs)
                    st.divider()
                    copy_box("📋 Copia FAQ (Markdown/Gutenberg)", faq_to_md(faqs), "cp_faq")

                elif key == "schema":
                    schema_json = build_final_schema(data, _loc, _az)
                    stype = "LocalBusiness 📍" if _loc.get("indirizzo","").strip() else "Organization 🌐"
                    st.caption(f"Schema: **{stype}** · Usa plugin WordPress 'Insert Headers and Footers'")
                    script_block = f'<script type="application/ld+json">\n{schema_json}\n</script>'
                    st.code(script_block, language="html")
                    copy_box("📋 Copia Schema JSON-LD", script_block, "cp_schema")

        st.divider()

        with st.expander("🔧 JSON Raw completo (debug / sviluppatori)"):
            st.code(json.dumps(data, ensure_ascii=False, indent=2), language="json")

        export = {
            "meta": {
                "azienda": _az, "provider": provider, "model": model,
                "in_tokens": in_t, "out_tokens": out_t, "cost_usd": cost_r,
                "local_seo": _loc
            },
            "content": data
        }
        st.download_button(
            "⬇️ Scarica pacchetto completo (JSON)",
            data=json.dumps(export, ensure_ascii=False, indent=2),
            file_name=f"geo_alligator_{_az.replace(' ','_').lower()}.json",
            mime="application/json"
        )

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
