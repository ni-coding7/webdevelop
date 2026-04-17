"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           GEO Score™ Content Generator — by Nico Fioretti                  ║
║           Senior Python Developer & AI Cost Strategist Build               ║
╚══════════════════════════════════════════════════════════════════════════════╝

TOKEN SAVINGS STRATEGY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. GEO_CRITERIA_CONSTANT: I criteri delle 8 dimensioni del file Excel sono
   estratti UNA VOLTA e memorizzati come costante Python. Nessuna lettura
   runtime del file, nessun token sprecato a rileggere l'Excel ogni call.

2. ONE-SHOT GENERATION: Un'unica chiamata API genera Home + Servizio + FAQ
   + Schema Markup in JSON strutturato. Invece di 4 chiamate separate
   (~4× overhead di contesto), ne facciamo UNA con output delimitato.
   Risparmio stimato: ~60-70% di token vs approccio multi-call.

3. SYSTEM PROMPT CONCENTRATO: Il system prompt inietta i criteri GEO come
   regole imperative dense (~400 token fissi), non come prosa descrittiva.
   Nessun testo "di cortesia" nel prompt.

4. temperature=0.7: Creatività controllata senza degenerazioni verbose.
   Istruzione esplicita: "NO intro, NO conclusioni, NO commenti fuori JSON".
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import streamlit as st
import json
import re
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 1: GEO CRITERIA CONSTANT
# Estratto dal file GEO_Score_Nico_Fioretti.xlsx una tantum.
# NON viene passato l'Excel all'API → risparmio massiccio di token.
# Ogni run dell'app usa questa costante già compilata → 0 chiamate extra.
# ─────────────────────────────────────────────────────────────────────────────
GEO_CRITERIA = """
GEO SCORE™ — 8 DIMENSIONI DI VISIBILITÀ AI (Nico Fioretti Framework):

1. TECNICA: Crawlabilità AI bot (GPTBot/ClaudeBot non bloccati in robots.txt),
   HTML rendering senza JS, link <a href> standard, Schema Markup JSON-LD
   validato, velocità <3s (PageSpeed >70), HTTPS attivo.

2. CONTENUTO: Risposta diretta entro i primi 2 paragrafi, valore originale
   (non duplicato), prove ed evidenze numeriche (≥1 dato ogni 2 paragrafi),
   cluster tematici collegati, copertura customer journey completa
   (awareness→consideration→decision), statistiche settoriali aggiornate.

3. IDENTITÀ: Nome brand consistente su tutti i canali, Organization Schema
   con sameAs a LinkedIn/Wikipedia/Wikidata, allineamento descrizioni
   cross-platform, associazione topic-brand nei motori AI, distinzione
   da omonimi, profili autore collegati e verificabili.

4. LEGGIBILITÀ: Incipit con risposta diretta (AI estrae chunk iniziali),
   heading H2/H3 descrittivi (non creativi/vaghi), un'idea per paragrafo
   (max 5 righe), claim autonomi comprensibili out-of-context, formati
   strutturati (tabelle/FAQ/liste — citati 3× più spesso dall'AI),
   sezioni indipendenti che non richiedono contesto precedente.

5. AUTORITÀ: Menzioni su siti terzi del settore (ultimi 12 mesi),
   claim supportati da fonti esterne verificabili, presenza su directory
   e review platform (Trustpilot/Google Reviews), link a fonti
   istituzionali (.gov/.edu), Digital PR attiva (guest post/interviste),
   menzioni ripetute per topic target (≥5 risultati indipendenti).

6. CREDIBILITÀ: Autori con bio+foto+LinkedIn visibili, claim con fonti
   primarie citate (≥2-3/pagina), ricerca originale pubblicata
   (survey/report/case study con numeri reali), sentiment online positivo,
   trust signals on-site (Chi siamo, P.IVA, team reale, certificazioni),
   dati originali citati da altri siti o risposte AI.

7. UNICITÀ: Framework/metodo proprietario con nome proprio, differenziazione
   in una frase chiara e coerente, zero cliché ("leader del settore",
   "qualità eccellente", "soluzioni innovative") → sostituire con dati
   concreti, differenziazione ripetuta ovunque (homepage/about/servizi/
   profili esterni), concetti branded originali attribuiti al brand.

8. FRESCHEZZA: Pagine chiave revisionate ogni 6 mesi, date visibili e
   accurate (non manipolate), statistiche degli ultimi 12-18 mesi,
   aggiornamento frequente su temi time-sensitive (AI/normative/prezzi),
   gestione contenuti obsoleti (refresh/merge/redirect).

SCORING: 0-2=Assente, 3-4=Parziale, 5-6=In sviluppo, 7-8=Buono, 9-10=Eccellente
LIVELLI: 0-39%=AI-Invisible | 40-59%=AI-Emerging | 60-79%=AI-Visible | 80-100%=AI-Ready Leader
"""

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 2: PRICING MODELS
# Prezzi per 1K token (input/output) per stimare i costi prima di generare.
# Aggiorna questi valori se i prezzi cambiano — sono hardcoded per rapidità.
# ─────────────────────────────────────────────────────────────────────────────
PRICING = {
    "openai": {
        "gpt-4o-mini":        {"input": 0.00015,  "output": 0.00060},
        "gpt-4o":             {"input": 0.00250,  "output": 0.01000},
        "gpt-4.1-mini":       {"input": 0.00040,  "output": 0.00160},
        "gpt-4.1":            {"input": 0.00200,  "output": 0.00800},
    },
    "anthropic": {
        "claude-haiku-4-5-20251001":   {"input": 0.00025,  "output": 0.00125},
        "claude-sonnet-4-6": {"input": 0.00300,  "output": 0.01500},
        "claude-opus-4-6":   {"input": 0.01500,  "output": 0.07500},
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 3: TOKEN ESTIMATION
# Stima tokens prima della chiamata per mostrare costo atteso.
# Regola empirica: ~4 caratteri ≈ 1 token (buona approssimazione per italiano)
# ─────────────────────────────────────────────────────────────────────────────
def estimate_tokens(text: str) -> int:
    """Stima token count: ~4 caratteri per token per testo italiano."""
    return max(1, len(text) // 4)

def estimate_cost(input_tokens: int, output_tokens: int, provider: str, model: str) -> float:
    """Calcola costo stimato in USD dato input/output tokens."""
    try:
        p = PRICING[provider][model]
        return (input_tokens / 1000 * p["input"]) + (output_tokens / 1000 * p["output"])
    except KeyError:
        return 0.0

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 4: SYSTEM PROMPT BUILDER
# Il system prompt è DENSO e imperativo — nessuna prosa, solo regole.
# Inietta i GEO_CRITERIA dalla costante (mai dal file runtime).
# Output_format specifica la struttura JSON esatta → parsing affidabile.
# ─────────────────────────────────────────────────────────────────────────────
def build_system_prompt() -> str:
    """
    TOKEN SAVING: Il system prompt usa GEO_CRITERIA dalla costante locale.
    Nessuna chiamata extra per leggere il file. Lunghezza ~600 token fissi
    che si ammortizzano su ogni generazione successiva (API stateless).
    """
    return f"""Sei un copywriter GEO/SEO esperto. Generi testi web in italiano ottimizzati per visibilità AI.

FRAMEWORK OBBLIGATORIO — GEO SCORE™:
{GEO_CRITERIA}

REGOLE DI OUTPUT (OBBLIGATORIE, NESSUNA ECCEZIONE):
- Rispondi ESCLUSIVAMENTE con un oggetto JSON valido. Zero testo fuori dal JSON.
- NO introduzioni, NO conclusioni, NO commenti, NO "Ecco il testo:", NO markdown.
- Ogni sezione deve rispettare attivamente le 8 dimensioni GEO Score™.
- Usa H1/H2/H3 come prefissi testuali: # Titolo H1 / ## Titolo H2 / ### Titolo H3
- Includi SEMPRE almeno 1 dato numerico citabile per sezione (citabilità AI).
- Le FAQ devono rispondere a domande reali che un utente cercherebbe su un motore AI.
- Schema Markup: JSON-LD valido, Organization + FAQPage, pronto per <script type="application/ld+json">.
- Frasi autonome: ogni affermazione importante deve avere senso FUORI CONTESTO (l'AI estrae chunk).
- Evita cliché: "leader del settore", "qualità eccellente", "soluzioni innovative" → usa dati concreti.
- Struttura output JSON ESATTA richiesta (vedi user prompt).
"""

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 5: USER PROMPT BUILDER (ONE-SHOT)
# UN solo user prompt genera TUTTO il pacchetto in un'unica chiamata API.
# Risparmio: ~65% vs chiamate separate (ogni call ha overhead fisso di
# contesto + system prompt). Il formato JSON garantisce parsing affidabile.
# ─────────────────────────────────────────────────────────────────────────────
def build_user_prompt(azienda: str, servizi: str, target: str, fatti: str, lingua: str = "italiano") -> str:
    """
    ONE-SHOT PROMPT: Genera Home + Servizio + FAQ + Schema in una sola call.
    Il formato JSON delimitato elimina parsing ambigui e riduce token di output.
    """
    return f"""Genera il pacchetto completo GEO-ottimizzato per:

AZIENDA: {azienda}
SERVIZI: {servizi}
TARGET: {target}
FATTI UNICI/CITABILI: {fatti}
LINGUA OUTPUT: {lingua}

Restituisci SOLO questo JSON (nessun testo prima o dopo):
{{
  "home": {{
    "h1": "Titolo H1 homepage (max 60 caratteri, keyword principale inclusa)",
    "intro": "Paragrafo introduttivo (150-200 parole). Prima frase = risposta diretta alla query principale dell'utente. Includi 1 dato numerico citabile. Nessun cliché.",
    "sezione_1": {{
      "h2": "Titolo H2 della prima sezione valore",
      "body": "Corpo sezione (100-150 parole). Formattazione: usa ### per sottotitoli interni se utile. Inserisci dato numerico o fatto unico dal debrief."
    }},
    "sezione_2": {{
      "h2": "Titolo H2 della seconda sezione differenziazione",
      "body": "Corpo sezione (100-150 parole). Spiega l'unicità del brand con dati concreti, non aggettivi vuoti."
    }},
    "cta": "Testo call-to-action finale (1 frase, imperativo, specifico)"
  }},
  "pagina_servizio": {{
    "h1": "Titolo H1 pagina servizio (keyword long-tail inclusa)",
    "intro": "Paragrafo introduttivo servizio (100-150 parole). Risposta diretta: cosa ottiene il cliente, non cosa fa l'azienda.",
    "come_funziona": {{
      "h2": "Come funziona [Servizio] — titolo descrittivo",
      "steps": [
        "Step 1: descrizione concreta (max 2 righe)",
        "Step 2: descrizione concreta (max 2 righe)",
        "Step 3: descrizione concreta (max 2 righe)",
        "Step 4: descrizione concreta (max 2 righe)"
      ]
    }},
    "benefici": {{
      "h2": "Cosa ottieni: titolo con numero specifico (es. '5 risultati garantiti')",
      "lista": [
        "Beneficio 1 con dato numerico o fatto verificabile",
        "Beneficio 2 con dato numerico o fatto verificabile",
        "Beneficio 3 con dato numerico o fatto verificabile",
        "Beneficio 4 con dato numerico o fatto verificabile"
      ]
    }},
    "cta": "Testo CTA pagina servizio (1 frase, specifica al servizio)"
  }},
  "faq": [
    {{
      "domanda": "Domanda 1 — reale query AI (inizia con Come/Cosa/Quanto/Perché/Chi)",
      "risposta": "Risposta completa autonoma (80-120 parole). Deve avere senso estratta fuori contesto. Include dato concreto."
    }},
    {{
      "domanda": "Domanda 2",
      "risposta": "Risposta 2"
    }},
    {{
      "domanda": "Domanda 3",
      "risposta": "Risposta 3"
    }},
    {{
      "domanda": "Domanda 4",
      "risposta": "Risposta 4"
    }},
    {{
      "domanda": "Domanda 5",
      "risposta": "Risposta 5"
    }}
  ],
  "schema_markup": {{
    "organization": {{
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "{azienda}",
      "description": "Descrizione brand 160 caratteri max, keyword principale inclusa",
      "url": "https://www.esempio.it",
      "sameAs": ["https://www.linkedin.com/company/esempio"],
      "knowsAbout": ["Topic 1", "Topic 2", "Topic 3"]
    }},
    "faq_schema": {{
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": "PLACEHOLDER — verrà popolato con le FAQ generate"
    }}
  }}
}}"""

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6: API CALL HANDLERS
# Due handler separati (OpenAI / Anthropic) per massima compatibilità.
# Entrambi usano lo stesso system prompt concentrato e temperature=0.7.
# ─────────────────────────────────────────────────────────────────────────────
def call_openai(api_key: str, model: str, system: str, user: str, max_tokens: int = 4000) -> tuple[Optional[str], int, int]:
    """
    Chiama OpenAI API. Restituisce (risposta, input_tokens, output_tokens).
    Usa max_tokens=4000 per accomodare tutto il JSON one-shot.
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user}
            ],
            temperature=0.7,        # Creatività controllata, output non verboso
            max_tokens=max_tokens,
            response_format={"type": "json_object"}  # Forza JSON puro → meno token sprecati
        )
        content = response.choices[0].message.content
        usage = response.usage
        return content, usage.prompt_tokens, usage.completion_tokens
    except ImportError:
        return None, 0, 0
    except Exception as e:
        raise e

def call_anthropic(api_key: str, model: str, system: str, user: str, max_tokens: int = 4000) -> tuple[Optional[str], int, int]:
    """
    Chiama Anthropic API. Restituisce (risposta, input_tokens, output_tokens).
    Prefill con "{" per forzare output JSON diretto → risparmio ~10-20 token.
    """
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[
                {"role": "user",      "content": user},
                {"role": "assistant", "content": "{"}   # PREFILL TRICK: forza JSON, elimina preamble
            ],
            temperature=0.7
        )
        content = "{" + response.content[0].text  # Reintegra il prefill
        usage = response.usage
        return content, usage.input_tokens, usage.output_tokens
    except ImportError:
        return None, 0, 0
    except Exception as e:
        raise e

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 7: JSON PARSER ROBUSTO
# Gestisce edge cases: markdown code blocks, trailing commas, testo extra.
# ─────────────────────────────────────────────────────────────────────────────
def parse_json_response(raw: str) -> Optional[dict]:
    """
    Parser robusto: rimuove markdown, cerca il primo oggetto JSON valido.
    Usato perché alcuni modelli ignorano le istruzioni "solo JSON".
    """
    if not raw:
        return None
    # Rimuovi code fences markdown
    raw = re.sub(r"```(?:json)?", "", raw).strip()
    # Cerca il primo { ... } valido
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: trova la prima { e l'ultima }
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(raw[start:end])
            except:
                pass
    return None

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 8: SCHEMA MARKUP BUILDER
# Costruisce il JSON-LD finale combinando Organization + FAQPage.
# Pronto per copia/incolla in WordPress (widget HTML o header).
# ─────────────────────────────────────────────────────────────────────────────
def build_final_schema(data: dict) -> str:
    """
    Assembla Schema Markup JSON-LD completo (Organization + FAQPage).
    Popola FAQPage con le FAQ generate, non con placeholder.
    """
    schema = data.get("schema_markup", {})
    org    = schema.get("organization", {})
    faqs   = data.get("faq", [])

    # FAQPage con le domande reali generate
    faq_schema = {
        "@context": "https://schema.org",
        "@type":    "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name":  faq["domanda"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text":  faq["risposta"]
                }
            }
            for faq in faqs
        ]
    }

    combined = {
        "@context": "https://schema.org",
        "@graph": [org, faq_schema]
    }
    return json.dumps(combined, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 9: UI HELPERS
# Funzioni per rendering pulito dei blocchi di contenuto.
# ─────────────────────────────────────────────────────────────────────────────
def copy_button(label: str, text: str, key: str):
    """Mostra testo in text_area con key univoca per facile selezione/copia."""
    st.text_area(label, value=text, height=200, key=key,
                 help="Seleziona tutto (Ctrl+A) e copia (Ctrl+C)")

def render_home(home: dict):
    st.markdown(f"### `# {home.get('h1', '')}`")
    st.markdown(f"**Intro:** {home.get('intro', '')}")
    s1 = home.get("sezione_1", {})
    if s1:
        st.markdown(f"**## {s1.get('h2', '')}**")
        st.markdown(s1.get("body", ""))
    s2 = home.get("sezione_2", {})
    if s2:
        st.markdown(f"**## {s2.get('h2', '')}**")
        st.markdown(s2.get("body", ""))
    st.markdown(f"**CTA:** _{home.get('cta', '')}_")

def render_service(page: dict):
    st.markdown(f"### `# {page.get('h1', '')}`")
    st.markdown(f"**Intro:** {page.get('intro', '')}")
    cf = page.get("come_funziona", {})
    if cf:
        st.markdown(f"**## {cf.get('h2', '')}**")
        for step in cf.get("steps", []):
            st.markdown(f"- {step}")
    ben = page.get("benefici", {})
    if ben:
        st.markdown(f"**## {ben.get('h2', '')}**")
        for b in ben.get("lista", []):
            st.markdown(f"✅ {b}")
    st.markdown(f"**CTA:** _{page.get('cta', '')}_")

def render_faq(faqs: list):
    for i, faq in enumerate(faqs, 1):
        with st.expander(f"❓ {faq.get('domanda', f'FAQ {i}')}"):
            st.markdown(faq.get("risposta", ""))

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 10: MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="GEO Score™ Content Generator",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # ── CSS CUSTOM ──────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .geo-header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                  color: white; padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem; }
    .geo-header h1 { margin: 0; font-size: 2rem; }
    .geo-header p  { margin: 0.3rem 0 0; opacity: 0.8; font-size: 0.95rem; }
    .cost-box { background: #f0f9ff; border-left: 4px solid #0ea5e9;
                padding: 0.8rem 1rem; border-radius: 6px; margin: 0.5rem 0; }
    .stTabs [data-baseweb="tab"] { font-size: 1rem; padding: 0.5rem 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

    # ── HEADER ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="geo-header">
        <h1>🤖 GEO Score™ Content Generator</h1>
        <p>Genera contenuti ottimizzati per visibilità AI · Framework by Nico Fioretti · Cost-optimized build</p>
    </div>
    """, unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # SIDEBAR — Configurazione API & Stima Costi
    # ────────────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Configurazione API")
        st.caption("Scegli provider, modello e inserisci la tua API key.")

        provider = st.selectbox(
            "Provider AI",
            ["openai", "anthropic"],
            format_func=lambda x: "🟢 OpenAI" if x == "openai" else "🟠 Anthropic"
        )

        # Modelli per provider — default ai più economici per risparmio massimo
        if provider == "openai":
            model_options = list(PRICING["openai"].keys())
            default_model = "gpt-4o-mini"
        else:
            model_options = list(PRICING["anthropic"].keys())
            default_model = "claude-haiku-4-5-20251001"

        default_idx = model_options.index(default_model) if default_model in model_options else 0
        model = st.selectbox("Modello", model_options, index=default_idx)

        # Etichette user-friendly per i modelli
        model_labels = {
            "gpt-4o-mini":              "gpt-4o-mini 💰 (consigliato)",
            "gpt-4o":                   "gpt-4o 🔋",
            "gpt-4.1-mini":             "gpt-4.1-mini 💰",
            "gpt-4.1":                  "gpt-4.1 🔋",
            "claude-haiku-4-5-20251001":       "Claude Haiku 💰 (consigliato)",
            "claude-sonnet-4-6":        "Claude Sonnet 3.5 🔋",
            "claude-opus-4-6":          "Claude Opus 3 💎",
        }
        st.caption(f"Selezionato: **{model_labels.get(model, model)}**")

        api_key = st.text_input(
            "🔑 API Key",
            type="password",
            placeholder="sk-... oppure sk-ant-...",
            help="La key non viene salvata né loggata."
        )

        st.divider()

        # ── STIMA COSTI IN TEMPO REALE ──────────────────────────────────
        # TOKEN SAVING: La stima avviene PRIMA della chiamata, così l'utente
        # può scegliere il modello più economico consapevolmente.
        st.subheader("💰 Stima Costi")
        st.caption("Calcolata sul prompt sistema + input stimato output")

        system_tokens  = estimate_tokens(build_system_prompt())
        base_user_est  = 500  # tokens medi per un user prompt compilato
        output_est     = 1800 # stima output JSON completo (~7200 caratteri)
        total_in       = system_tokens + base_user_est

        cost_est = estimate_cost(total_in, output_est, provider, model)

        st.markdown(f"""
        <div class="cost-box">
            <b>Token stimati:</b> {total_in + output_est:,}<br>
            &nbsp;&nbsp;• Input: ~{total_in:,} token<br>
            &nbsp;&nbsp;• Output: ~{output_est:,} token<br>
            <b>Costo stimato: ${cost_est:.5f}</b>
        </div>
        """, unsafe_allow_html=True)

        st.caption("⚠️ Stima. Il costo reale dipende dall'input effettivo.")

        st.divider()
        st.markdown("**📖 GEO Score™ Framework**")
        with st.expander("Dimensioni caricate (da Excel)"):
            st.markdown("""
            Le 8 dimensioni sono **hardcoded** come costante Python,
            estratte dal file Excel `GEO_Score_Nico_Fioretti.xlsx`.
            Nessun token sprecato a rileggerle ogni chiamata.

            1. ⚙️ Tecnica
            2. 📝 Contenuto
            3. 🏷️ Identità
            4. 🔍 Leggibilità
            5. 🌐 Autorità
            6. 🏅 Credibilità
            7. 💎 Unicità
            8. 🔄 Freschezza
            """)

    # ────────────────────────────────────────────────────────────────────────
    # MAIN CONTENT — 3 TAB
    # ────────────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📋 Debrief", "🛠️ Generatore", "📄 Risultati"])

    # ── TAB 1: DEBRIEF ──────────────────────────────────────────────────────
    with tab1:
        st.subheader("📋 Debrief Azienda")
        st.markdown("Compila questi campi. Più dettagli = migliore citabilità AI nei testi generati.")

        col1, col2 = st.columns(2)

        with col1:
            azienda = st.text_input(
                "🏢 Nome Azienda *",
                placeholder="es. Studio Legale Bianchi & Partners",
                key="azienda"
            )
            servizi = st.text_area(
                "🛠️ Servizi Principali *",
                placeholder="es. Consulenza giuslavoristica, contrattualistica, contenzioso lavoro",
                height=120,
                key="servizi"
            )

        with col2:
            target = st.text_area(
                "🎯 Target / Clienti Ideali *",
                placeholder="es. PMI italiane 10-50 dipendenti, HR Manager, imprenditori nel manifatturiero",
                height=120,
                key="target"
            )
            lingua = st.selectbox(
                "🌍 Lingua Output",
                ["italiano", "inglese", "francese", "spagnolo", "tedesco"],
                key="lingua"
            )

        fatti = st.text_area(
            "💡 Fatti Unici & Citabili (il carburante della citabilità AI)",
            placeholder="""Esempi di fatti ad alto impatto:
• "Assistiamo 200+ aziende ogni anno con tasso successo contenziosi del 94%"
• "Unici in Italia certificati ISO 9001 per la consulenza HR"  
• "Framework proprietario 'Contratto Zero-Risk' applicato in 15 settori"
• "Fondatori con 20+ anni esperienza, ex-docenti Università Bocconi"
• "Costi trasparenti: preventivo fisso in 24h, no sorprese in fattura" """,
            height=200,
            key="fatti"
        )

        if azienda and servizi and target and fatti:
            # Anteprima costo con dati reali
            user_prompt_preview = build_user_prompt(azienda, servizi, target, fatti, lingua)
            real_input_tokens   = estimate_tokens(build_system_prompt() + user_prompt_preview)
            real_cost           = estimate_cost(real_input_tokens, output_est, provider, model)

            st.success(f"✅ Debrief completo! Token input reali stimati: **{real_input_tokens:,}** | Costo stimato: **${real_cost:.5f}**")
        else:
            st.info("💡 Compila tutti i campi obbligatori (*) per procedere al Generatore.")

    # ── TAB 2: GENERATORE ───────────────────────────────────────────────────
    with tab2:
        st.subheader("🛠️ Generatore One-Shot GEO")

        # Recupera valori dal session state / tab 1
        _azienda = st.session_state.get("azienda", "")
        _servizi = st.session_state.get("servizi", "")
        _target  = st.session_state.get("target",  "")
        _fatti   = st.session_state.get("fatti",   "")
        _lingua  = st.session_state.get("lingua",  "italiano")

        ready = bool(_azienda and _servizi and _target and _fatti and api_key)

        if not ready:
            missing = []
            if not _azienda: missing.append("Nome Azienda")
            if not _servizi: missing.append("Servizi")
            if not _target:  missing.append("Target")
            if not _fatti:   missing.append("Fatti Unici")
            if not api_key:  missing.append("API Key (sidebar)")
            st.warning(f"⚠️ Mancano: **{', '.join(missing)}**. Torna al tab Debrief.")

        st.markdown("""
        **Cosa verrà generato in una sola chiamata API:**

        | Sezione | Descrizione |
        |---------|-------------|
        | 🏠 Homepage | H1 + intro citabile + 2 sezioni value + CTA |
        | 📄 Pagina Servizio | H1 + intro + come funziona + benefici + CTA |
        | ❓ FAQ (5 domande) | Domande reali che AI citerebbe, risposte autonome |
        | 🔗 Schema Markup | JSON-LD Organization + FAQPage WordPress-ready |
        """)

        col_btn, col_info = st.columns([1, 2])

        with col_btn:
            generate_btn = st.button(
                "🚀 Genera Contenuti GEO",
                disabled=not ready,
                type="primary",
                use_container_width=True
            )

        with col_info:
            if ready:
                user_p  = build_user_prompt(_azienda, _servizi, _target, _fatti, _lingua)
                sys_p   = build_system_prompt()
                in_tok  = estimate_tokens(sys_p + user_p)
                cost_pr = estimate_cost(in_tok, output_est, provider, model)
                st.info(f"📊 Stima pre-generazione: **{in_tok + output_est:,} token** | **${cost_pr:.5f}**")

        if generate_btn and ready:
            # ── CHIAMATA API ─────────────────────────────────────────────
            system_p = build_system_prompt()
            user_p   = build_user_prompt(_azienda, _servizi, _target, _fatti, _lingua)

            with st.spinner("🧠 Generazione in corso (chiamata API singola)..."):
                try:
                    if provider == "openai":
                        raw, in_t, out_t = call_openai(api_key, model, system_p, user_p)
                    else:
                        raw, in_t, out_t = call_anthropic(api_key, model, system_p, user_p)

                    if raw is None:
                        st.error("❌ Libreria non installata. Esegui: pip install openai anthropic")
                        st.stop()

                    parsed = parse_json_response(raw)

                    if parsed:
                        # Salva in session state per tab Risultati
                        st.session_state["generated"] = parsed
                        st.session_state["raw_json"]  = raw
                        st.session_state["in_tokens"]  = in_t
                        st.session_state["out_tokens"] = out_t

                        real_cost = estimate_cost(in_t, out_t, provider, model)
                        st.session_state["real_cost"] = real_cost

                        st.success(f"✅ Generazione completata! Token reali: **{in_t + out_t:,}** | Costo reale: **${real_cost:.5f}**")
                        st.balloons()
                        st.info("👉 Vai al tab **📄 Risultati** per copiare i contenuti.")
                    else:
                        st.error("❌ Parsing JSON fallito. Risposta raw mostrata sotto:")
                        st.code(raw, language="text")

                except Exception as e:
                    st.error(f"❌ Errore API: {str(e)}")
                    if "api_key" in str(e).lower() or "auth" in str(e).lower():
                        st.error("🔑 Controlla la API key nella sidebar.")

    # ── TAB 3: RISULTATI ────────────────────────────────────────────────────
    with tab3:
        st.subheader("📄 Risultati — Pronto per WordPress")

        if "generated" not in st.session_state:
            st.info("🔄 Nessun contenuto ancora generato. Vai al tab **🛠️ Generatore**.")
            st.stop()

        data     = st.session_state["generated"]
        in_t     = st.session_state.get("in_tokens", 0)
        out_t    = st.session_state.get("out_tokens", 0)
        cost_r   = st.session_state.get("real_cost", 0.0)

        # ── METRICHE REALI ───────────────────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Token Input",  f"{in_t:,}")
        m2.metric("Token Output", f"{out_t:,}")
        m3.metric("Token Totali", f"{in_t + out_t:,}")
        m4.metric("Costo Reale",  f"${cost_r:.5f}")

        st.divider()

        # ── RISULTATI PER SEZIONE ────────────────────────────────────────
        res1, res2, res3, res4 = st.tabs(["🏠 Homepage", "📄 Servizio", "❓ FAQ", "🔗 Schema"])

        # HOME
        with res1:
            home = data.get("home", {})
            if home:
                render_home(home)
                st.divider()
                # Testo formattato per WordPress/Elementor
                home_text = f"# {home.get('h1','')}\n\n{home.get('intro','')}\n\n"
                s1 = home.get("sezione_1", {})
                if s1:
                    home_text += f"## {s1.get('h2','')}\n\n{s1.get('body','')}\n\n"
                s2 = home.get("sezione_2", {})
                if s2:
                    home_text += f"## {s2.get('h2','')}\n\n{s2.get('body','')}\n\n"
                home_text += home.get("cta", "")
                copy_button("📋 Copia testo Homepage (Markdown/Gutenberg)", home_text, "copy_home")

        # SERVIZIO
        with res2:
            page = data.get("pagina_servizio", {})
            if page:
                render_service(page)
                st.divider()
                page_text = f"# {page.get('h1','')}\n\n{page.get('intro','')}\n\n"
                cf = page.get("come_funziona", {})
                if cf:
                    page_text += f"## {cf.get('h2','')}\n\n"
                    for step in cf.get("steps", []):
                        page_text += f"- {step}\n"
                    page_text += "\n"
                ben = page.get("benefici", {})
                if ben:
                    page_text += f"## {ben.get('h2','')}\n\n"
                    for b in ben.get("lista", []):
                        page_text += f"✅ {b}\n"
                    page_text += "\n"
                page_text += page.get("cta", "")
                copy_button("📋 Copia testo Pagina Servizio (Markdown/Gutenberg)", page_text, "copy_service")

        # FAQ
        with res3:
            faqs = data.get("faq", [])
            if faqs:
                render_faq(faqs)
                st.divider()
                faq_text = "## Domande Frequenti\n\n"
                for faq in faqs:
                    faq_text += f"### {faq.get('domanda','')}\n\n{faq.get('risposta','')}\n\n"
                copy_button("📋 Copia FAQ (Markdown/Gutenberg)", faq_text, "copy_faq")

        # SCHEMA MARKUP
        with res4:
            if data:
                schema_json = build_final_schema(data)
                st.markdown("**JSON-LD Schema Markup** — incolla in WordPress > Appearance > Theme Editor > header.php oppure usa plugin 'Insert Headers and Footers'")
                st.code(f'<script type="application/ld+json">\n{schema_json}\n</script>', language="html")
                copy_button("📋 Copia Schema Markup JSON-LD", f'<script type="application/ld+json">\n{schema_json}\n</script>', "copy_schema")

        st.divider()

        # ── JSON RAW ─────────────────────────────────────────────────────
        with st.expander("🔧 JSON Raw (debug / sviluppatori)"):
            st.code(st.session_state.get("raw_json", "{}"), language="json")

        # ── EXPORT ───────────────────────────────────────────────────────
        export_data = {
            "meta": {
                "azienda":     st.session_state.get("azienda", ""),
                "provider":    provider,
                "model":       model,
                "in_tokens":   in_t,
                "out_tokens":  out_t,
                "cost_usd":    cost_r
            },
            "content": data
        }
        st.download_button(
            label="⬇️ Scarica tutto (JSON)",
            data=json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name=f"geo_content_{st.session_state.get('azienda','brand').replace(' ','_').lower()}.json",
            mime="application/json"
        )

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
