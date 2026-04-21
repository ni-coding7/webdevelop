"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     GEO Score™ Content Generator v3 — Alligator Edition                    ║
║     Senior Python Developer & Local SEO Expert Build                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

CHANGELOG v3:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OBJ 1 — FIX BUG API ANTHROPIC (ERRORE 400)
  • RIMOSSO "response_format": {"type": "json_object"} da call_anthropic()
  • Mantenuto prefill assistant con "{" → forza output JSON senza errori API

OBJ 2 — SISTEMA WEB RAG / FONTI VERIFICATE
  • get_external_evidence(): simula chiamata API (Serper/Tavily/Perplexity)
  • Risultati iniettati nel system prompt come "FONTI VERIFICATE DI TERZE PARTI"
  • Modello istruito a citare fonti in testo (Dim.5 AUTORITÀ + Dim.6 CREDIBILITÀ)

OBJ 3 — ORARI SPEZZATI (LOCAL SEO)
  • Input: "09:00-13:00, 15:00-19:00" → split per virgola
  • build_final_schema() genera array multipli OpeningHoursSpecification
  • Markup JSON-LD valido per Google Maps e Google Business Profile

OBJ 4 — LOGICA MODULARE SITO NUOVO vs OTTIMIZZAZIONE
  • Sidebar: checkbox "SITO NUOVO (Boost Semantico)"
  • Sidebar: checkbox "OTTIMIZZAZIONE ESISTENTE (Audit & RAG)"
  • analyze_existing_content(): confronta testo corrente con criteri GEO Score™

OBJ 5 — SITELINK & AUTORITÀ ESTERNA
  • Se evidence contiene Award/.gov/.edu/testate → AI suggerisce sezione
    "Riconoscimenti e Fonti" con external links per grafo di autorità

OBJ 6 — UNIVERSALITÀ DEL TOOL
  • System prompt 100% dinamico via variabili "Entità Verticali" per settore
  • Nessun riferimento hard-coded a settori specifici
  • Adattamento automatico: medico, legale, food, artigianale, SaaS, ecc.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import streamlit as st
import json
import re
import time
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 1: GEO CRITERIA CONSTANT
# Hardcoded per 0 token overhead — non chiamare API per recuperarlo.
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
# ─────────────────────────────────────────────────────────────────────────────
PRICING = {
    "openai": {
        "gpt-4o-mini":  {"input": 0.00015, "output": 0.00060},
        "gpt-4o":       {"input": 0.00250, "output": 0.01000},
        "gpt-4.1-mini": {"input": 0.00040, "output": 0.00160},
        "gpt-4.1":      {"input": 0.00200, "output": 0.00800},
    },
    "anthropic": {
        "claude-haiku-4-5-20251001": {"input": 0.00025, "output": 0.00125},
        "claude-sonnet-4-6":         {"input": 0.00300, "output": 0.01500},
        "claude-opus-4-6":           {"input": 0.01500, "output": 0.07500},
    }
}

MODEL_LABELS = {
    "claude-haiku-4-5-20251001": "Claude Haiku 💰 (default economico)",
    "claude-sonnet-4-6":         "Claude Sonnet 🔋 (premium)",
    "claude-opus-4-6":           "Claude Opus 💎 (massima qualità)",
    "gpt-4o-mini":               "GPT-4o Mini 💰 (default economico)",
    "gpt-4o":                    "GPT-4o 🔋 (premium)",
    "gpt-4.1-mini":              "GPT-4.1 Mini 💰",
    "gpt-4.1":                   "GPT-4.1 🔋",
}

# max_tokens esplicito per modello — evita troncature silenziose
MODEL_MAX_TOKENS = {
    "gpt-4o-mini":               4096,
    "gpt-4o":                    4096,
    "gpt-4.1-mini":              4096,
    "gpt-4.1":                   4096,
    "claude-haiku-4-5-20251001": 4096,
    "claude-sonnet-4-6":         8192,
    "claude-opus-4-6":           4096,
}

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 3: TOKEN UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def estimate_tokens(text: str) -> int:
    """Stima approssimativa: ~4 caratteri per token."""
    return max(1, len(text) // 4)


def estimate_cost(input_tokens: int, output_tokens: int, provider: str, model: str) -> float:
    """Calcola costo in USD per una chiamata API."""
    try:
        p = PRICING[provider][model]
        return (input_tokens / 1000 * p["input"]) + (output_tokens / 1000 * p["output"])
    except KeyError:
        return 0.0

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 4: REPAIR JSON
# Stack-based: traccia parentesi aperte ignorando quelle in stringhe.
# Chiude nella sequenza inversa corretta → salva output parziali da troncatura.
# ─────────────────────────────────────────────────────────────────────────────
def repair_json(text: str) -> str:
    """
    Ripara JSON troncato chiudendo parentesi/parentesi quadre aperte.
    Sicuro: ignora { e [ all'interno di stringhe.
    """
    if not text:
        return text

    # Rimuovi fence markdown e trailing comma
    text = re.sub(r"```(?:json)?", "", text).strip()
    if text.endswith(","):
        text = text[:-1]

    stack      = []
    in_string  = False
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
# SEZIONE 5: WEB RAG — RICERCA FONTI ESTERNE (OBJ 2 + OBJ 5)
# Funzione che simula/esegue una chiamata API di ricerca (Serper/Tavily).
# In modalità simulazione restituisce dati strutturati per testing offline.
# In produzione: fornisci una SERPER_API_KEY o TAVILY_API_KEY nella sidebar.
# ─────────────────────────────────────────────────────────────────────────────
def get_external_evidence(
    azienda: str,
    settore: str,
    localita: str,
    search_api_key: str = "",
    search_provider: str = "simulate"
) -> dict:
    """
    Cerca online evidenze verificabili sull'azienda negli ultimi 24 mesi:
    premi, certificazioni, menzioni in guide/testate, dati tecnici.

    Args:
        azienda:         Nome dell'azienda
        settore:         Settore di attività (es. "ristorante", "avvocato", "dentista")
        localita:        Città/area geografica
        search_api_key:  Chiave API Serper o Tavily (opzionale)
        search_provider: "serper" | "tavily" | "simulate"

    Returns:
        dict con keys: fonti[], awards[], certificazioni[], menzioni_autorevoli[],
                       ha_gov_edu (bool), suggerisci_sitelinks (bool)
    """
    # ── MODALITÀ SIMULAZIONE (offline / no API key) ──────────────────────────
    if search_provider == "simulate" or not search_api_key:
        # Dati placeholder realistici — utili per testing e demo
        evidence = {
            "fonti": [
                {
                    "titolo":   f"Guida {settore.title()} 2025 — Le migliori realtà di {localita}",
                    "url":      f"https://www.esempio-guida.it/{settore.lower()}-{localita.lower()}-2025",
                    "citazione": f"{azienda} figura tra i professionisti raccomandati nella guida settoriale 2025.",
                    "tipo":     "guida_settoriale",
                    "autorita": "media"
                }
            ],
            "awards":            [],
            "certificazioni":    [],
            "menzioni_autorevoli": [],
            "ha_gov_edu":        False,
            "suggerisci_sitelinks": False,
            "nota":              "Modalità simulazione attiva — inserisci una Serper o Tavily API key per dati reali."
        }
        return evidence

    # ── MODALITÀ SERPER (Google Search API) ─────────────────────────────────
    if search_provider == "serper":
        try:
            import requests
            query = f'"{azienda}" {settore} {localita} premio certificazione 2024 OR 2025'
            headers = {
                "X-API-KEY":    search_api_key,
                "Content-Type": "application/json"
            }
            payload = {"q": query, "num": 10, "hl": "it", "gl": "it"}
            resp = requests.post(
                "https://google.serper.dev/search",
                headers=headers,
                json=payload,
                timeout=10
            )
            resp.raise_for_status()
            results = resp.json().get("organic", [])
            return _parse_search_results(results, azienda)
        except Exception as e:
            return {"errore": str(e), "fonti": [], "awards": [], "certificazioni": [],
                    "menzioni_autorevoli": [], "ha_gov_edu": False, "suggerisci_sitelinks": False}

    # ── MODALITÀ TAVILY ──────────────────────────────────────────────────────
    if search_provider == "tavily":
        try:
            import requests
            query = f"{azienda} {settore} {localita} premi certificazioni recensioni 2024 2025"
            payload = {
                "api_key":        search_api_key,
                "query":          query,
                "search_depth":   "advanced",
                "include_answer": False,
                "max_results":    8
            }
            resp = requests.post(
                "https://api.tavily.com/search",
                json=payload,
                timeout=10
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
            # Tavily restituisce: title, url, content, score
            normalized = [{"title": r.get("title",""), "link": r.get("url",""),
                           "snippet": r.get("content","")} for r in results]
            return _parse_search_results(normalized, azienda)
        except Exception as e:
            return {"errore": str(e), "fonti": [], "awards": [], "certificazioni": [],
                    "menzioni_autorevoli": [], "ha_gov_edu": False, "suggerisci_sitelinks": False}

    return {"fonti": [], "awards": [], "certificazioni": [],
            "menzioni_autorevoli": [], "ha_gov_edu": False, "suggerisci_sitelinks": False}


def _parse_search_results(results: list, azienda: str) -> dict:
    """
    Classifica i risultati di ricerca in awards, certificazioni,
    menzioni autorevoli e rileva domini .gov/.edu.
    """
    fonti              = []
    awards             = []
    certificazioni     = []
    menzioni_autorevoli = []
    ha_gov_edu         = False

    # Pattern per riconoscimento tipologia fonte
    award_kw  = ["premio", "award", "riconoscimento", "vincitore", "migliore", "top", "best"]
    cert_kw   = ["certificato", "certificazione", "iso", "doc", "dop", "igp", "albo", "accreditato"]
    auth_kw   = ["gambero rosso", "michelin", "espresso", "sole 24 ore", "corriere",
                 "repubblica", "forbes", "ilsole", "touring", "veronelli"]
    gov_edu   = [".gov", ".edu", ".europa.eu", ".camera.it", ".senato.it",
                 ".istat.it", ".agcm.it", "ordine", "albo"]

    for r in results:
        title   = r.get("title", "").lower()
        link    = r.get("link",  "").lower()
        snippet = r.get("snippet", "")

        fonte_entry = {
            "titolo":   r.get("title", ""),
            "url":      r.get("link",  ""),
            "citazione": snippet[:200] if snippet else "",
            "tipo":     "generico",
            "autorita": "bassa"
        }

        # Classifica per tipologia
        if any(k in title or k in snippet.lower() for k in award_kw):
            fonte_entry["tipo"] = "award"
            fonte_entry["autorita"] = "alta"
            awards.append(fonte_entry["titolo"])

        elif any(k in title or k in snippet.lower() for k in cert_kw):
            fonte_entry["tipo"] = "certificazione"
            fonte_entry["autorita"] = "alta"
            certificazioni.append(fonte_entry["titolo"])

        elif any(k in link or k in title for k in auth_kw):
            fonte_entry["tipo"] = "testata_autorevole"
            fonte_entry["autorita"] = "alta"
            menzioni_autorevoli.append(fonte_entry)

        if any(k in link for k in gov_edu):
            ha_gov_edu = True
            fonte_entry["autorita"] = "massima"

        fonti.append(fonte_entry)

    # Suggerisci sezione Sitelinks se ci sono fonti ad alta autorità
    suggerisci_sitelinks = (
        len(awards) > 0
        or len(certificazioni) > 0
        or len(menzioni_autorevoli) > 0
        or ha_gov_edu
    )

    return {
        "fonti":               fonti,
        "awards":              awards,
        "certificazioni":      certificazioni,
        "menzioni_autorevoli": menzioni_autorevoli,
        "ha_gov_edu":          ha_gov_edu,
        "suggerisci_sitelinks": suggerisci_sitelinks
    }


def format_evidence_for_prompt(evidence: dict) -> str:
    """
    Serializza le evidenze in formato leggibile per il system prompt.
    Restituisce stringa vuota se non ci sono dati significativi.
    """
    if not evidence or not evidence.get("fonti"):
        return ""

    lines = ["FONTI VERIFICATE DI TERZE PARTI (Web RAG — ultime 24h):"]
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for f in evidence.get("fonti", []):
        autorita = f.get("autorita", "bassa").upper()
        lines.append(f"[{autorita}] {f.get('titolo','')} → {f.get('url','')}")
        if f.get("citazione"):
            lines.append(f"   Estratto: \"{f['citazione'][:150]}\"")

    if evidence.get("awards"):
        lines.append(f"\n🏆 PREMI/AWARD rilevati: {', '.join(evidence['awards'])}")
    if evidence.get("certificazioni"):
        lines.append(f"📜 CERTIFICAZIONI: {', '.join(evidence['certificazioni'])}")
    if evidence.get("ha_gov_edu"):
        lines.append("🏛️ FONTI .GOV/.EDU rilevate — massima autorità SEO")
    if evidence.get("suggerisci_sitelinks"):
        lines.append("\n➡️ SITELINKS: Suggerisci sezione 'Riconoscimenti e Fonti' con link esterni.")

    if evidence.get("nota"):
        lines.append(f"\n⚠️ Nota: {evidence['nota']}")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("ISTRUZIONE CITAZIONE: Cita queste fonti nel testo generato con formule come:")
    lines.append('  "Secondo [Nome Fonte/Anno]..." oppure "Come riportato da [Testata]..."')
    lines.append("  Questo soddisfa GEO Score™ Dim.5 (AUTORITÀ) e Dim.6 (CREDIBILITÀ).")

    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6: ANALISI CONTENUTO ESISTENTE — AUDIT GEO (OBJ 4b)
# Confronta il testo attuale con i criteri GEO Score™ e produce solo
# correzioni/integrazioni mirate (no riscrittura completa).
# ─────────────────────────────────────────────────────────────────────────────
def build_audit_prompt(testo_esistente: str, ctx: str) -> str:
    """
    Genera un prompt di audit per la modalità "OTTIMIZZAZIONE ESISTENTE".
    Analizza il contenuto fornito rispetto alle 8 dimensioni GEO Score™
    e produce esclusivamente gap analysis + patch testuali mirate.
    """
    return f"""{ctx}

CONTENUTO ESISTENTE DA ANALIZZARE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{testo_esistente.strip()[:3000]}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODALITÀ: OTTIMIZZAZIONE ESISTENTE — Audit & RAG

Analizza il testo sopra rispetto alle 8 dimensioni GEO Score™.
NON riscrivere il testo completo. Genera SOLO correzioni chirurgiche.

Rispondi ESCLUSIVAMENTE con questo JSON:
{{
  "audit": {{
    "punteggi": {{
      "tecnica": 0,
      "contenuto": 0,
      "identita": 0,
      "leggibilita": 0,
      "autorita": 0,
      "credibilita": 0,
      "unicita": 0,
      "freschezza": 0
    }},
    "gap_critici": [
      "Gap 1: dimensione - problema specifico - impatto stimato",
      "Gap 2: dimensione - problema specifico - impatto stimato",
      "Gap 3: dimensione - problema specifico - impatto stimato"
    ],
    "patch_testo": [
      {{
        "posizione": "Intro/H1/Sezione X",
        "testo_attuale": "Frase o blocco da sostituire (max 80 char)",
        "testo_ottimizzato": "Versione corretta con dato/fonte/keyword mancante",
        "dimensione_geo": "AUTORITÀ",
        "impatto": "Alto/Medio/Basso"
      }}
    ],
    "elementi_da_aggiungere": [
      "Elemento mancante 1 (es. dato numerico + fonte)",
      "Elemento mancante 2 (es. FAQ specifica per query AI)",
      "Elemento mancante 3 (es. claim verificabile con link)"
    ],
    "score_totale_attuale": 0,
    "score_potenziale_post_fix": 0
  }}
}}"""

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 7: SYSTEM PROMPT BUILDER — UNIVERSALE (OBJ 6)
# Nessun riferimento hard-coded a settori specifici.
# Usa variabili dinamiche "Entità Verticali" per adattarsi a qualsiasi business.
# ─────────────────────────────────────────────────────────────────────────────
def build_system_prompt(
    stile_esempi:  str  = "",
    evidence:      dict = None,
    settore:       str  = "",
    is_nuovo_sito: bool = False,
    is_ottimizza:  bool = False
) -> str:
    """
    Costruisce il system prompt dinamico.

    Args:
        stile_esempi:  Esempi di copy del brand per replicarne il tono
        evidence:      Dict con fonti Web RAG (da get_external_evidence)
        settore:       Settore di attività (medico, legale, food, artigianale, ecc.)
        is_nuovo_sito: Modalità Sito Nuovo → keyword LSI + entità GEO da zero
        is_ottimizza:  Modalità Ottimizzazione → solo correzioni mirate
    """

    # ── Regole Alligator (stile fisso) ────────────────────────────────────────
    alligator_rules = """APPROCCIO ALLIGATOR (OBBLIGATORIO):
- DIRETTO: Frasi brevi. Soggetto + Verbo + Oggetto. Zero giri di parole.
- RISULTATI: Ogni affermazione ha una conseguenza misurabile per il cliente.
- NO TREND VUOTI: Vietato "digital transformation", "ecosistema", "sinergie", "paradigma". Sostituisci con un dato.
- AUTOREVOLE TECNICO: Terminologia di settore. Il lettore è esperto.
- LEGGIBILE: Periodi max 20 parole. Sottotitoli ogni 100 parole."""

    # ── Sezione stile brand ───────────────────────────────────────────────────
    style_section = ""
    if stile_esempi and stile_esempi.strip():
        style_section = f"""
ANALISI TONO DI VOCE — ESEMPI REALI DEL BRAND:
---
{stile_esempi.strip()}
---
ISTRUZIONE STILE: Analizza i testi sopra. Identifica lunghezza media frasi, vocabolario ricorrente, struttura titoli, uso numeri. Replica ESATTAMENTE quel tono. Non interpretare, non migliorare: replica."""

    # ── Sezione Web RAG / Fonti esterne (OBJ 2 + OBJ 5) ─────────────────────
    evidence_section = ""
    if evidence:
        evidence_str = format_evidence_for_prompt(evidence)
        if evidence_str:
            evidence_section = f"\n{evidence_str}\n"

        # OBJ 5: istruzione sezione Sitelinks se ci sono fonti autorevoli
        if evidence.get("suggerisci_sitelinks"):
            evidence_section += """
ISTRUZIONE SITELINKS & AUTORITÀ ESTERNA (OBJ 5):
Se il testo lo permette, suggerisci una sezione "Riconoscimenti e Fonti" con:
- Link in uscita verso le fonti autorevoli trovate
- Anchor text descrittivo (es. "Premi ricevuti da [Testata]")
- Questo costruisce il grafo di autorità topica per Google e motori AI.
"""

    # ── Entità verticali dinamiche per settore (OBJ 6) ───────────────────────
    # Non si specifica un settore fisso: il modello identifica le entità
    # rilevanti del settore ricevuto come variabile e le integra nel testo.
    vertical_entities_section = ""
    if settore:
        vertical_entities_section = f"""
ENTITÀ VERTICALI DEL SETTORE "{settore.upper()}" (OBJ 6 — Universalità):
Identifica e integra nel testo le entità topiche specifiche di questo settore:
- Certificazioni e standard normativi tipici del settore
- Associazioni di categoria, ordini professionali o enti regolatori pertinenti
- Terminologia tecnica e acronimi di settore che i motori AI riconoscono
- Processi, metodi o framework specifici del settore
- KPI e metriche di performance tipiche del settore
Usa queste entità per costruire autorità topica agli occhi dei motori AI generativi.
"""

    # ── Istruzione modalità Sito Nuovo (OBJ 4a) ──────────────────────────────
    nuovo_sito_section = ""
    if is_nuovo_sito:
        nuovo_sito_section = """
MODALITÀ: SITO NUOVO — BOOST SEMANTICO (OBJ 4):
Questo brand parte da zero autorità online. Applica:
- Keyword LSI: includi almeno 5 sinonimi semantici della keyword principale
- Spiegazioni esaustive dei processi: il lettore non conosce ancora il brand
- Entità tecniche: nomina standard, certificazioni, metodi riconoscibili dai motori AI
- Generative Engine Optimization: struttura ogni paragrafo come una risposta autonoma
  che un LLM potrebbe estrarre e citare indipendentemente dal contesto
- Claim fondativi: afferma la specializzazione con dati concreti fin dall'H1
- Journey completo: copri tutte le fasi (consapevolezza → considerazione → decisione)
"""

    # ── Istruzione modalità Ottimizzazione (OBJ 4b) ──────────────────────────
    ottimizza_section = ""
    if is_ottimizza:
        ottimizza_section = """
MODALITÀ: OTTIMIZZAZIONE ESISTENTE — AUDIT & RAG (OBJ 4):
Non stai scrivendo da zero. Stai correggendo e integrando contenuti esistenti.
- Identifica solo i gap rispetto alle 8 dimensioni GEO Score™
- Proponi correzioni chirurgiche (patch) senza riscrivere l'intera pagina
- Aggiungi solo ciò che manca: dati numerici, fonti, keyword LSI, claim verificabili
- Prioritizza le dimensioni con score più basso (autorità e credibilità prima)
"""

    # ── Assemblaggio finale del system prompt ────────────────────────────────
    return f"""Sei il copywriter GEO/SEO senior di Alligator. Generi contenuti web ad alta citabilità AI.

{alligator_rules}
{style_section}
{evidence_section}
{vertical_entities_section}
{nuovo_sito_section}
{ottimizza_section}

FRAMEWORK GEO SCORE:
{GEO_CRITERIA}

REGOLE OUTPUT (ASSOLUTE):
- Rispondi SOLO con JSON valido. Zero testo fuori dal JSON.
- NO introduzioni, NO conclusioni, NO commenti, NO markdown fuori JSON.
- Ogni sezione: minimo 1 dato numerico citabile.
- Claim autonomi: ogni frase chiave ha senso estratta fuori contesto.
- Zero cliché: sostituisci "leader/eccellente/innovativo/qualità" con dati.
- Se hai fonti verificate, citale nel testo con "Secondo [Fonte Anno]..."."""

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 8: CONTEXT BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def build_ctx(azienda, servizi, target, fatti, local_seo, lingua) -> str:
    """Costruisce il contesto aziendale da iniettare in ogni prompt modulare."""
    addr = local_seo.get("indirizzo", "")
    return f"""AZIENDA: {azienda}
SERVIZI: {servizi}
TARGET: {target}
FATTI CITABILI: {fatti}
INDIRIZZO: {addr if addr else "Non specificato"}
LINGUA: {lingua}"""

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 9: PROMPT MODULARI
# Una funzione per sezione → output ~800-1200 token max → no troncature.
# ─────────────────────────────────────────────────────────────────────────────
def prompt_home(ctx: str) -> str:
    return f"""{ctx}

Genera SOLO il blocco "home". Rispondi ESCLUSIVAMENTE con questo JSON:
{{
  "home": {{
    "h1": "Titolo H1 max 60 char, keyword principale",
    "intro": "150-200 parole. Prima frase = risposta diretta. 1 dato numerico. Stile Alligator. Se hai fonti verificate, citane almeno 1.",
    "sezione_1": {{
      "h2": "H2 valore concreto non generico",
      "body": "100-150 parole. Dato numerico o fatto unico dal debrief."
    }},
    "sezione_2": {{
      "h2": "H2 differenziazione specifica",
      "body": "100-150 parole. Unicità con dati concreti, zero cliché."
    }},
    "cta": "1 frase imperativa e specifica",
    "riconoscimenti": null
  }}
}}

NOTA su "riconoscimenti": Se hai trovato premi o menzioni autorevoli nelle FONTI VERIFICATE,
compila il campo con: {{"titolo": "Riconoscimenti e Fonti", "voci": [{{"testo": "...", "url": "..."}}]}}
Altrimenti lascialo null."""


def prompt_servizio(ctx: str) -> str:
    return f"""{ctx}

Genera SOLO il blocco "pagina_servizio". Rispondi ESCLUSIVAMENTE con questo JSON:
{{
  "pagina_servizio": {{
    "h1": "H1 pagina servizio con keyword long-tail",
    "intro": "100-150 parole. Cosa ottiene il cliente, non cosa fa l'azienda. Cita fonti se disponibili.",
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
      "domanda": "Query reale motore AI — inizia con Come/Cosa/Quanto/Perché/Chi",
      "risposta": "80-120 parole. Autonoma fuori contesto. Include dato concreto. Cita fonte se disponibile."
    }},
    {{"domanda": "Domanda 2", "risposta": "Risposta 2 80-120 parole"}},
    {{"domanda": "Domanda 3", "risposta": "Risposta 3 80-120 parole"}},
    {{"domanda": "Domanda 4", "risposta": "Risposta 4 80-120 parole"}},
    {{"domanda": "Domanda 5", "risposta": "Risposta 5 80-120 parole"}}
  ]
}}"""


def prompt_schema(ctx: str, azienda: str, local_seo: dict, faq_data: list) -> str:
    """Prompt schema: inietta dati Local SEO → modello genera schema base."""
    indirizzo   = local_seo.get("indirizzo", "")
    url_sito    = local_seo.get("url",       "https://www.esempio.it")
    linkedin    = local_seo.get("linkedin",  "")
    schema_type = "LocalBusiness" if indirizzo.strip() else "Organization"

    orari     = local_seo.get("orari", {})
    orari_str = ""
    giorni_map = {
        "Lunedì":    "Monday",   "Martedì":   "Tuesday",
        "Mercoledì": "Wednesday","Giovedì":   "Thursday",
        "Venerdì":   "Friday",   "Sabato":    "Saturday",
        "Domenica":  "Sunday"
    }
    for g, valore in orari.items():
        # OBJ 3: valore può essere stringa "09:00-13:00, 15:00-19:00"
        if isinstance(valore, str) and valore.strip():
            orari_str += f"{giorni_map.get(g, g)}: {valore} | "
        elif isinstance(valore, (list, tuple)) and len(valore) == 2:
            ap, ch = valore
            if ap and ch:
                orari_str += f"{giorni_map.get(g, g)}: {ap}-{ch} | "

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
# SEZIONE 10: API CALL HANDLERS
#
# OBJ 1 — FIX CRITICO: call_anthropic NON usa "response_format".
#   Anthropic non supporta quel parametro → causa errore 400.
#   Il JSON è forzato via prefill dell'assistant con "{".
# ─────────────────────────────────────────────────────────────────────────────
def call_openai(api_key: str, model: str, system: str, user: str) -> tuple:
    """
    Chiama OpenAI. Usa response_format json_object (supportato da OpenAI).
    """
    try:
        from openai import OpenAI
        client  = OpenAI(api_key=api_key)
        max_tok = MODEL_MAX_TOKENS.get(model, 4000)
        resp    = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user}
            ],
            temperature=0.7,
            max_tokens=max_tok,
            response_format={"type": "json_object"}  # Solo OpenAI supporta questo
        )
        return resp.choices[0].message.content, resp.usage.prompt_tokens, resp.usage.completion_tokens
    except ImportError:
        return None, 0, 0
    except Exception as e:
        raise e


def call_anthropic(api_key: str, model: str, system: str, user: str) -> tuple:
    """
    Chiama Anthropic Claude.

    OBJ 1 — FIX BUG ERRORE 400:
      • RIMOSSO "response_format": {"type": "json_object"} — NON supportato da Anthropic
      • Il JSON è forzato tramite prefill: assistant inizia con "{"
        Anthropic completa da quel punto → output sempre JSON, senza preamble
      • La risposta viene riassemblata aggiungendo il "{" iniziale del prefill
    """
    try:
        import anthropic
        client  = anthropic.Anthropic(api_key=api_key)
        max_tok = MODEL_MAX_TOKENS.get(model, 4000)

        resp = client.messages.create(
            model=model,
            max_tokens=max_tok,
            system=system,
            messages=[
                {"role": "user",      "content": user},
                {"role": "assistant", "content": "{"}  # Prefill: forza JSON, elimina preamble
                # NOTA: NON aggiungere response_format qui — Anthropic lo rifiuterà con 400
            ],
            temperature=0.7
        )

        # Riattacca il "{" del prefill (non incluso nel response body)
        content = "{" + resp.content[0].text
        return content, resp.usage.input_tokens, resp.usage.output_tokens

    except ImportError:
        return None, 0, 0
    except Exception as e:
        raise e


def call_api(provider, api_key, model, system, user):
    """Router: indirizza la chiamata al provider corretto."""
    if provider == "openai":
        return call_openai(api_key, model, system, user)
    return call_anthropic(api_key, model, system, user)

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 11: JSON PARSER ROBUSTO
# Cascata: parsing diretto → estrazione blocco → repair_json
# ─────────────────────────────────────────────────────────────────────────────
def parse_json_response(raw: str) -> Optional[dict]:
    """
    Tenta di parsare il JSON con 3 strategie in cascata:
    1. Parsing diretto
    2. Estrazione del primo blocco {}
    3. repair_json su blocco parziale
    """
    if not raw:
        return None

    cleaned = re.sub(r"```(?:json)?", "", raw).strip()

    # Tentativo 1: parsing diretto
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Tentativo 2: estrai primo blocco JSON completo
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
# SEZIONE 12: SCHEMA MARKUP BUILDER — ORARI SPEZZATI (OBJ 3)
# Supporta "09:00-13:00, 15:00-19:00" → array multipli OpeningHoursSpecification
# ─────────────────────────────────────────────────────────────────────────────
def _parse_orari_giorno(valore_orario) -> list:
    """
    OBJ 3 — ORARI SPEZZATI:
    Parsa un valore orario che può essere:
      - Tupla/lista legacy: ("09:00", "18:00") → un singolo slot
      - Stringa singola: "09:00-18:00" → un singolo slot
      - Stringa multipla: "09:00-13:00, 15:00-19:00" → due slot

    Restituisce lista di tuple [(opens, closes), ...]
    """
    slots = []

    if isinstance(valore_orario, (list, tuple)) and len(valore_orario) == 2:
        apertura, chiusura = valore_orario
        if apertura and chiusura:
            # Potrebbero essere già in formato "09:00-13:00, 15:00-19:00"
            # se l'utente ha inserito tutto nell'apertura
            if "," in str(apertura):
                return _parse_orari_giorno(apertura)
            slots.append((str(apertura).strip(), str(chiusura).strip()))
        return slots

    if isinstance(valore_orario, str) and valore_orario.strip():
        # Split per virgola → gestisce orari spezzati
        parti = [p.strip() for p in valore_orario.split(",")]
        for parte in parti:
            if "-" in parte:
                segmenti = parte.split("-")
                if len(segmenti) == 2:
                    ap = segmenti[0].strip()
                    ch = segmenti[1].strip()
                    if ap and ch:
                        slots.append((ap, ch))

    return slots


def build_final_schema(data: dict, local_seo: dict, azienda: str) -> str:
    """
    Costruisce il JSON-LD finale sovrascrivendo in Python i valori Local SEO.
    OBJ 3: genera array multipli OpeningHoursSpecification per orari spezzati.
    """
    schema_raw = data.get("schema_markup", {})
    org        = dict(schema_raw.get("organization", {}))
    faqs       = data.get("faq", [])

    indirizzo = local_seo.get("indirizzo", "").strip()
    gps_lat   = local_seo.get("gps_lat",   "").strip()
    gps_lon   = local_seo.get("gps_lon",   "").strip()
    orari     = local_seo.get("orari",     {})
    url_sito  = local_seo.get("url",       "https://www.esempio.it").strip()
    linkedin  = local_seo.get("linkedin",  "").strip()

    # Tipo schema
    schema_type     = "LocalBusiness" if indirizzo else "Organization"
    org["@context"] = "https://schema.org"
    org["@type"]    = schema_type
    org["name"]     = azienda
    if url_sito:  org["url"]    = url_sito
    if linkedin:  org["sameAs"] = [linkedin]

    # Indirizzo strutturato
    if indirizzo:
        parts = [p.strip() for p in indirizzo.split(",")]
        org["address"] = {
            "@type":           "PostalAddress",
            "streetAddress":   parts[0] if len(parts) > 0 else "",
            "addressLocality": parts[1] if len(parts) > 1 else "",
            "postalCode":      parts[2] if len(parts) > 2 else "",
            "addressRegion":   parts[3] if len(parts) > 3 else "",
            "addressCountry":  "IT"
        }

    # Coordinate GPS
    if gps_lat and gps_lon:
        try:
            org["geo"] = {
                "@type":     "GeoCoordinates",
                "latitude":  float(gps_lat),
                "longitude": float(gps_lon)
            }
        except ValueError:
            pass

    # ── OBJ 3: openingHoursSpecification con supporto orari spezzati ─────────
    giorni_map = {
        "Lunedì":    "Monday",   "Martedì":   "Tuesday",
        "Mercoledì": "Wednesday","Giovedì":   "Thursday",
        "Venerdì":   "Friday",   "Sabato":    "Saturday",
        "Domenica":  "Sunday"
    }
    oh = []

    for g_it, valore in orari.items():
        g_en = giorni_map.get(g_it, g_it)

        # Parsa il valore (supporta sia tuple legacy che stringhe "09:00-13:00, 15:00-19:00")
        slots = _parse_orari_giorno(valore)

        for (opens, closes) in slots:
            oh.append({
                "@type":     "OpeningHoursSpecification",
                "dayOfWeek": f"https://schema.org/{g_en}",
                "opens":     opens,
                "closes":    closes
            })

    if oh:
        org["openingHoursSpecification"] = oh

    # Schema FAQPage
    faq_schema = {
        "@context": "https://schema.org",
        "@type":    "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name":  f.get("domanda", ""),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text":  f.get("risposta", "")
                }
            }
            for f in faqs
        ]
    }

    # Restituisce @graph con entrambi gli schemi
    return json.dumps(
        {"@context": "https://schema.org", "@graph": [org, faq_schema]},
        ensure_ascii=False, indent=2
    )

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 13: UI HELPERS (RENDER + COPY)
# ─────────────────────────────────────────────────────────────────────────────
def copy_box(label: str, text: str, key: str):
    st.text_area(label, value=text, height=200, key=key,
                 help="Ctrl+A per selezionare tutto → Ctrl+C per copiare")


def render_home(home: dict):
    st.markdown(f"**H1:** `{home.get('h1','')}`")
    st.markdown(f"**Intro:**\n\n{home.get('intro','')}")
    for k, lbl in [("sezione_1","Sezione 1"),("sezione_2","Sezione 2")]:
        s = home.get(k, {})
        if s:
            st.markdown(f"**H2 {lbl}:** `{s.get('h2','')}`")
            st.markdown(s.get("body",""))
    st.markdown(f"**CTA:** _{home.get('cta','')}_")

    # OBJ 5: Visualizza sezione Riconoscimenti se presente
    riconosc = home.get("riconoscimenti")
    if riconosc and isinstance(riconosc, dict):
        with st.expander(f"🏆 {riconosc.get('titolo','Riconoscimenti e Fonti')}"):
            for voce in riconosc.get("voci", []):
                st.markdown(f"- [{voce.get('testo','')}]({voce.get('url','')})")


def render_service(page: dict):
    st.markdown(f"**H1:** `{page.get('h1','')}`")
    st.markdown(f"**Intro:**\n\n{page.get('intro','')}")
    cf = page.get("come_funziona", {})
    if cf:
        st.markdown(f"**H2:** `{cf.get('h2','')}`")
        for step in cf.get("steps", []):
            st.markdown(f"- {step}")
    ben = page.get("benefici", {})
    if ben:
        st.markdown(f"**H2:** `{ben.get('h2','')}`")
        for b in ben.get("lista", []):
            st.markdown(f"✅ {b}")
    st.markdown(f"**CTA:** _{page.get('cta','')}_")


def render_faq(faqs: list):
    for i, faq in enumerate(faqs, 1):
        with st.expander(f"❓ {faq.get('domanda', f'FAQ {i}')}"):
            st.markdown(faq.get("risposta",""))


def render_audit(audit_data: dict):
    """Visualizza i risultati dell'audit GEO Score™."""
    audit = audit_data.get("audit", {})
    if not audit:
        st.warning("Nessun dato di audit trovato.")
        return

    # Score totali
    score_att  = audit.get("score_totale_attuale", 0)
    score_post = audit.get("score_potenziale_post_fix", 0)
    c1, c2 = st.columns(2)
    c1.metric("Score Attuale",  f"{score_att}/100",  delta=None)
    c2.metric("Score Potenziale", f"{score_post}/100", delta=f"+{score_post-score_att}")

    # Punteggi per dimensione
    punteggi = audit.get("punteggi", {})
    if punteggi:
        st.markdown("#### Punteggi per Dimensione GEO Score™")
        cols = st.columns(4)
        for i, (dim, score) in enumerate(punteggi.items()):
            cols[i%4].metric(dim.upper(), f"{score}/10")

    # Gap critici
    gaps = audit.get("gap_critici", [])
    if gaps:
        st.markdown("#### 🔴 Gap Critici")
        for g in gaps:
            st.markdown(f"- {g}")

    # Patch testuali
    patches = audit.get("patch_testo", [])
    if patches:
        st.markdown("#### ✂️ Patch Testuali Consigliate")
        for p in patches:
            with st.expander(f"[{p.get('impatto','?')}] {p.get('posizione','')} — {p.get('dimensione_geo','')}"):
                st.markdown(f"**Attuale:** _{p.get('testo_attuale','')}_")
                st.markdown(f"**Ottimizzato:** {p.get('testo_ottimizzato','')}")

    # Elementi da aggiungere
    aggiunte = audit.get("elementi_da_aggiungere", [])
    if aggiunte:
        st.markdown("#### ➕ Elementi da Aggiungere")
        for a in aggiunte:
            st.markdown(f"- {a}")


def home_to_md(h: dict) -> str:
    t = f"# {h.get('h1','')}\n\n{h.get('intro','')}\n\n"
    for k in ["sezione_1","sezione_2"]:
        s = h.get(k, {})
        if s:
            t += f"## {s.get('h2','')}\n\n{s.get('body','')}\n\n"
    t += h.get("cta","")
    riconosc = h.get("riconoscimenti")
    if riconosc and isinstance(riconosc, dict):
        t += f"\n\n## {riconosc.get('titolo','Riconoscimenti e Fonti')}\n"
        for voce in riconosc.get("voci", []):
            t += f"- [{voce.get('testo','')}]({voce.get('url','')})\n"
    return t


def service_to_md(p: dict) -> str:
    t = f"# {p.get('h1','')}\n\n{p.get('intro','')}\n\n"
    cf = p.get("come_funziona", {})
    if cf:
        t += f"## {cf.get('h2','')}\n\n"
        for s in cf.get("steps",[]): t += f"- {s}\n"
        t += "\n"
    ben = p.get("benefici", {})
    if ben:
        t += f"## {ben.get('h2','')}\n\n"
        for b in ben.get("lista",[]): t += f"✅ {b}\n"
        t += "\n"
    t += p.get("cta","")
    return t


def faq_to_md(faqs: list) -> str:
    t = "## Domande Frequenti\n\n"
    for f in faqs:
        t += f"### {f.get('domanda','')}\n\n{f.get('risposta','')}\n\n"
    return t

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 14: MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="GEO Score™ v3 — Alligator Edition",
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
    .rag-box {
        background: #f0fff4; border-left: 4px solid #22c55e;
        padding: 0.7rem 1rem; border-radius: 6px; margin: 0.4rem 0; font-size: 0.85rem;
    }
    .mode-box {
        background: #fefce8; border-left: 4px solid #eab308;
        padding: 0.7rem 1rem; border-radius: 6px; margin: 0.4rem 0; font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="geo-header">
        <h1>🐊 GEO Score™ Content Generator v3 — Alligator Edition</h1>
        <p>Web RAG · Orari Spezzati · Sito Nuovo vs Ottimizzazione · Sitelinks · Universale per settore</p>
    </div>
    """, unsafe_allow_html=True)

    # ── SIDEBAR ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Configurazione API")

        provider = st.selectbox("Provider AI", ["anthropic","openai"],
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

        # ── OBJ 4: Modalità Sito Nuovo / Ottimizzazione ───────────────────────
        st.subheader("🎯 Modalità di Generazione")

        is_nuovo_sito = st.checkbox(
            "🆕 SITO NUOVO (Boost Semantico)",
            key="is_nuovo_sito",
            help="Crea autorità da zero: keyword LSI, entità tecniche, GEO from scratch."
        )
        if is_nuovo_sito:
            st.markdown("""
            <div class="mode-box">
            ✅ <b>Boost Semantico attivo</b><br>
            Keyword LSI · Entità verticali · GEO da zero · Journey completo
            </div>""", unsafe_allow_html=True)

        is_ottimizza = st.checkbox(
            "🔧 OTTIMIZZAZIONE ESISTENTE (Audit & RAG)",
            key="is_ottimizza",
            help="Analizza il contenuto attuale e produce solo correzioni mirate."
        )
        if is_ottimizza:
            st.markdown("""
            <div class="mode-box">
            ✅ <b>Audit & RAG attivo</b><br>
            Gap Analysis · Patch chirurgiche · Score GEO attuale vs potenziale
            </div>""", unsafe_allow_html=True)

        # Le due modalità sono complementari ma non mutuamente esclusive
        if is_nuovo_sito and is_ottimizza:
            st.warning("⚠️ Hai attivato entrambe. Il sistema darà priorità all'Audit.")

        st.divider()

        # ── Web RAG Config ───────────────────────────────────────────────────
        st.subheader("🌐 Web RAG — Fonti Esterne")

        search_provider = st.selectbox(
            "Provider Ricerca",
            ["simulate", "serper", "tavily"],
            format_func=lambda x: {
                "simulate": "🧪 Simulazione (offline)",
                "serper":   "🔍 Serper (Google Search)",
                "tavily":   "🔎 Tavily (AI Search)"
            }.get(x, x),
            key="search_provider"
        )

        search_api_key = ""
        if search_provider != "simulate":
            search_api_key = st.text_input(
                f"🔑 {search_provider.title()} API Key",
                type="password",
                key="search_api_key",
                placeholder="Enter API key..."
            )

        enable_rag = st.checkbox("✅ Abilita Web RAG", value=True, key="enable_rag",
                                  help="Cerca evidenze online e iniettale nel prompt per Dim.5 e Dim.6.")

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
            st.markdown(
                "1.⚙️Tecnica · 2.📝Contenuto · 3.🏷️Identità · 4.🔍Leggibilità\n"
                "5.🌐Autorità · 6.🏅Credibilità · 7.💎Unicità · 8.🔄Freschezza\n\n"
                "*0 token overhead — costante Python*"
            )

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
                                    placeholder="es. Studio Rossi & Associati")
            servizi = st.text_area("Servizi Principali *", key="servizi", height=100,
                                   placeholder="es. Consulenza fiscale, Contabilità PMI, Due Diligence")
            settore = st.text_input(
                "Settore / Categoria Business *",
                key="settore",
                placeholder="es. Studio Commercialista, Ristorante, Dentista, SaaS B2B...",
                help="OBJ 6: Il tool si adatta alle entità verticali del tuo settore."
            )
        with c2:
            target = st.text_area("Target / Clienti Ideali *", key="target", height=100,
                                  placeholder="es. PMI con fatturato >500k, imprenditori nord Italia")
            lingua = st.selectbox("Lingua Output", ["italiano","inglese","francese","spagnolo"],
                                  key="lingua")

        fatti = st.text_area(
            "💡 Fatti Unici & Citabili *", key="fatti", height=130,
            placeholder='"30 anni di esperienza" · "200+ aziende seguite" · "Partner Confindustria Milano"'
        )

        st.divider()

        # Tono di voce / esempi style
        st.markdown("#### 🐊 Tono di Voce — Esempi Reali di Copy")
        st.caption("Il modello analizza questi testi e replica esattamente il tono nei contenuti generati.")
        stile_esempi = st.text_area(
            "Esempi di Stile/Copy (opzionale — fortemente consigliato)",
            key="stile_esempi", height=150,
            placeholder='"Non vendiamo consulenza. Costruiamo bilanci che reggono i controlli."\n"La tua azienda cresce. Il fisco pure. Noi facciamo in modo che non ti sorprenda."'
        )

        st.divider()

        # OBJ 4b: Contenuto esistente per audit
        if st.session_state.get("is_ottimizza"):
            st.markdown("#### 🔧 Contenuto Esistente da Ottimizzare")
            st.caption("Incolla qui il testo attuale della pagina. Il tool produrrà solo le correzioni necessarie.")
            testo_esistente = st.text_area(
                "Testo pagina da ottimizzare",
                key="testo_esistente", height=300,
                placeholder="Incolla qui il testo attuale del sito (homepage, pagina servizio, ecc.)..."
            )

        st.divider()

        # LOCAL SEO DATA
        st.markdown("#### 📍 Dati Local SEO (Schema Markup)")
        st.caption("Compilati automaticamente in JSON-LD LocalBusiness se l'indirizzo è presente.")

        col_a, col_b = st.columns(2)
        with col_a:
            via_civico = st.text_input("Via e Numero Civico", key="via",
                                       placeholder="es. Via Roma 42")
            cap        = st.text_input("CAP",       key="cap",  placeholder="20121")
            citta      = st.text_input("Città",     key="citta",placeholder="Milano")
            provincia  = st.text_input("Provincia", key="prov", placeholder="MI")
        with col_b:
            url_sito = st.text_input("URL Sito Web",          key="url_sito",
                                      placeholder="https://www.studiorossi.it")
            linkedin = st.text_input("URL LinkedIn Company",  key="linkedin",
                                      placeholder="https://www.linkedin.com/company/...")
            gps_lat  = st.text_input("Latitudine GPS (opz.)", key="gps_lat",
                                      placeholder="45.4654219")
            gps_lon  = st.text_input("Longitudine GPS (opz.)",key="gps_lon",
                                      placeholder="9.1859243")

        # ── OBJ 3: GRIGLIA ORARI SPEZZATI ────────────────────────────────────
        st.markdown("**🕐 Orari di Apertura**")
        st.caption(
            "Supporta orari spezzati: es. `09:00-13:00, 15:00-19:00` — "
            "genera automaticamente più slot OpeningHoursSpecification nel JSON-LD."
        )

        giorni    = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
        orari_dict = {}

        h_cols = st.columns([2, 5])
        h_cols[0].markdown("**Giorno**")
        h_cols[1].markdown("**Orario** *(es: 09:00-13:00, 15:00-19:00)*")

        for giorno in giorni:
            row = st.columns([2, 5])
            row[0].markdown(f"*{giorno}*")
            # Singolo campo stringa per supportare orari spezzati (OBJ 3)
            orario_str = row[1].text_input(
                "",
                key=f"orario_{giorno}",
                placeholder="09:00-13:00, 15:00-19:00",
                label_visibility="collapsed"
            )
            orari_dict[giorno] = orario_str  # Stringa grezza → parsata in build_final_schema

        # Componi indirizzo e salva in session_state
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
            st.session_state.get("settore"),
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

        _az  = st.session_state.get("azienda","")
        _sv  = st.session_state.get("servizi","")
        _tg  = st.session_state.get("target","")
        _ft  = st.session_state.get("fatti","")
        _ln  = st.session_state.get("lingua","italiano")
        _st  = st.session_state.get("stile_esempi","")
        _loc = st.session_state.get("local_seo",{})
        _set = st.session_state.get("settore","")
        _tex = st.session_state.get("testo_esistente","")

        _is_nuovo    = st.session_state.get("is_nuovo_sito", False)
        _is_ottimizza = st.session_state.get("is_ottimizza",  False)

        ready = bool(_az and _sv and _tg and _ft and _set and api_key)

        if not ready:
            missing = [x for x,v in [
                ("Nome Azienda",_az), ("Servizi",_sv), ("Target",_tg),
                ("Fatti",_ft), ("Settore",_set), ("API Key (sidebar)",api_key)
            ] if not v]
            st.warning(f"⚠️ Mancano: **{', '.join(missing)}**")

        # ── Sezioni da generare ───────────────────────────────────────────────
        st.markdown("#### Seleziona le sezioni da generare")
        st.caption("1 sezione = 1 chiamata API (~1200 token output) → nessun troncamento JSON.")

        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            gen_home    = st.checkbox("🏠 Homepage",         value=True,  key="gen_home")
            st.caption("H1, intro, 2 sezioni, CTA")
        with mc2:
            gen_service = st.checkbox("📄 Pagina Servizio",  value=True,  key="gen_service")
            st.caption("H1, come funziona, benefici, CTA")
        with mc3:
            gen_faq     = st.checkbox("❓ FAQ (5 domande)",   value=True,  key="gen_faq")
            st.caption("Query AI reali, risposte autonome")
        with mc4:
            gen_schema  = st.checkbox("🔗 Schema Markup",    value=True,  key="gen_schema")
            st.caption("JSON-LD LocalBusiness/Org + FAQ")

        # Modalità Audit: aggiungi checkbox dedicato
        gen_audit = False
        if _is_ottimizza and _tex:
            gen_audit = st.checkbox("🔧 Audit GEO Score™ (Ottimizzazione)", value=True, key="gen_audit")
            st.caption("Gap Analysis + Patch mirate sul contenuto esistente")

        n_sel = sum([gen_home, gen_service, gen_faq, gen_schema, gen_audit])

        if n_sel == 0:
            st.warning("Seleziona almeno una sezione.")

        st.divider()

        if ready and n_sel > 0:
            sp_preview = build_system_prompt(settore=_set)
            in_est_r   = estimate_tokens(sp_preview) + 300
            tot_est    = estimate_cost(in_est_r, 1200, provider, model) * n_sel
            st.info(f"📊 **{n_sel} chiamate pianificate** · Costo totale stimato: **${tot_est:.5f}**")

        gen_btn = st.button(
            f"🚀 Genera {n_sel} sezione{'i' if n_sel!=1 else ''}",
            disabled=(not ready or n_sel==0),
            type="primary"
        )

        if gen_btn and ready and n_sel > 0:

            # ── Step 1: Web RAG (OBJ 2) ───────────────────────────────────────
            evidence = None
            if st.session_state.get("enable_rag", True):
                with st.spinner("🌐 Ricerca fonti esterne (Web RAG)..."):
                    _citta = st.session_state.get("citta","")
                    evidence = get_external_evidence(
                        azienda         = _az,
                        settore         = _set,
                        localita        = _citta,
                        search_api_key  = st.session_state.get("search_api_key",""),
                        search_provider = st.session_state.get("search_provider","simulate")
                    )

                if evidence:
                    n_fonti = len(evidence.get("fonti",[]))
                    has_award = len(evidence.get("awards",[])) > 0
                    st.markdown(f"""
                    <div class="rag-box">
                    🌐 <b>Web RAG completato</b> — {n_fonti} fonti trovate
                    {'· 🏆 Award/premi rilevati' if has_award else ''}
                    {'· 🏛️ Fonte .gov/.edu' if evidence.get("ha_gov_edu") else ''}
                    {'· ⚠️ ' + evidence.get("nota","") if evidence.get("nota") else ''}
                    </div>""", unsafe_allow_html=True)

            # ── Step 2: Build prompt & generazione ───────────────────────────
            sys_p = build_system_prompt(
                stile_esempi  = _st,
                evidence      = evidence,
                settore       = _set,
                is_nuovo_sito = _is_nuovo,
                is_ottimizza  = _is_ottimizza
            )
            ctx = build_ctx(_az, _sv, _tg, _ft, _loc, _ln)

            total_in  = 0
            total_out = 0
            generated = dict(st.session_state.get("generated", {}))
            call_log  = []

            sections = []
            if gen_home:    sections.append("home")
            if gen_service: sections.append("servizio")
            if gen_faq:     sections.append("faq")
            if gen_schema:  sections.append("schema")
            if gen_audit:   sections.append("audit")

            progress = st.progress(0, text="Avvio generazione modulare...")

            for i, section in enumerate(sections):
                progress.progress(
                    int(i / len(sections) * 100),
                    text=f"⏳ Generando: **{section}**..."
                )

                try:
                    if section == "home":
                        user_p = prompt_home(ctx)
                    elif section == "servizio":
                        user_p = prompt_servizio(ctx)
                    elif section == "faq":
                        user_p = prompt_faq(ctx)
                    elif section == "schema":
                        faq_data = generated.get("faq", [])
                        user_p   = prompt_schema(ctx, _az, _loc, faq_data)
                    elif section == "audit":
                        user_p = build_audit_prompt(_tex, ctx)
                    else:
                        continue

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
                        call_log.append((
                            section, False,
                            f"Parsing fallito · Anteprima: {raw[:80] if raw else 'vuoto'}"
                        ))

                except Exception as e:
                    err_msg = str(e)
                    call_log.append((section, False, err_msg[:120]))
                    if "api_key" in err_msg.lower() or "auth" in err_msg.lower():
                        st.error("🔑 API Key non valida — controlla nella sidebar.")
                        break

            progress.progress(100, text="✅ Generazione completata!")

            # Salva evidence nel session_state per uso nei risultati
            st.session_state["generated"]  = generated
            st.session_state["in_tokens"]  = total_in
            st.session_state["out_tokens"] = total_out
            st.session_state["evidence"]   = evidence
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

        data     = st.session_state["generated"]
        in_t     = st.session_state.get("in_tokens",  0)
        out_t    = st.session_state.get("out_tokens", 0)
        cost_r   = st.session_state.get("real_cost",  0.0)
        _loc     = st.session_state.get("local_seo",  {})
        _az      = st.session_state.get("azienda",    "Brand")
        evidence = st.session_state.get("evidence",   None)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Token Input",  f"{in_t:,}")
        m2.metric("Token Output", f"{out_t:,}")
        m3.metric("Totale Token", f"{in_t+out_t:,}")
        m4.metric("Costo Reale",  f"${cost_r:.5f}")

        # OBJ 2 + OBJ 5: Mostra riepilogo fonti RAG se disponibili
        if evidence and evidence.get("fonti"):
            with st.expander("🌐 Fonti Web RAG utilizzate nella generazione"):
                for f in evidence["fonti"]:
                    autorita = f.get("autorita","").upper()
                    st.markdown(f"**[{autorita}]** [{f.get('titolo','')}]({f.get('url','')})")
                    if f.get("citazione"):
                        st.caption(f.get("citazione","")[:150])
                if evidence.get("suggerisci_sitelinks"):
                    st.success("🏆 Sezione 'Riconoscimenti e Fonti' suggerita nel testo (External Linking attivo)")

        st.divider()

        # Costruisci tab solo per sezioni disponibili
        avail = []
        if data.get("home"):            avail.append(("🏠 Homepage","home"))
        if data.get("pagina_servizio"): avail.append(("📄 Servizio","servizio"))
        if data.get("faq"):             avail.append(("❓ FAQ","faq"))
        if data.get("schema_markup") or data.get("faq"):
            avail.append(("🔗 Schema","schema"))
        if data.get("audit"):           avail.append(("🔧 Audit GEO","audit"))

        if not avail:
            st.warning("Nessuna sezione trovata. Ritorna al Generatore.")
            st.stop()

        rtabs = st.tabs([a[0] for a in avail])

        for rtab, (lbl, key) in zip(rtabs, avail):
            with rtab:
                if key == "home":
                    home = data.get("home", {})
                    render_home(home)
                    st.divider()
                    copy_box("📋 Copia Homepage (Markdown/Gutenberg)", home_to_md(home), "cp_home")

                elif key == "servizio":
                    page = data.get("pagina_servizio", {})
                    render_service(page)
                    st.divider()
                    copy_box("📋 Copia Pagina Servizio", service_to_md(page), "cp_serv")

                elif key == "faq":
                    faqs = data.get("faq", [])
                    render_faq(faqs)
                    st.divider()
                    copy_box("📋 Copia FAQ (Markdown/Gutenberg)", faq_to_md(faqs), "cp_faq")

                elif key == "schema":
                    schema_json  = build_final_schema(data, _loc, _az)
                    stype        = "LocalBusiness 📍" if _loc.get("indirizzo","").strip() else "Organization 🌐"
                    st.caption(f"Schema: **{stype}** · Usa plugin WordPress 'Insert Headers and Footers'")
                    script_block = f'<script type="application/ld+json">\n{schema_json}\n</script>'
                    st.code(script_block, language="html")
                    copy_box("📋 Copia Schema JSON-LD", script_block, "cp_schema")

                elif key == "audit":
                    render_audit(data)
                    st.divider()
                    copy_box(
                        "📋 Copia Audit (JSON)",
                        json.dumps(data.get("audit",{}), ensure_ascii=False, indent=2),
                        "cp_audit"
                    )

        st.divider()

        with st.expander("🔧 JSON Raw completo (debug / sviluppatori)"):
            st.code(json.dumps(data, ensure_ascii=False, indent=2), language="json")

        export = {
            "meta": {
                "azienda":   _az,
                "settore":   st.session_state.get("settore",""),
                "provider":  provider,
                "model":     model,
                "in_tokens": in_t,
                "out_tokens":out_t,
                "cost_usd":  cost_r,
                "local_seo": _loc,
                "modalita": {
                    "sito_nuovo":   st.session_state.get("is_nuovo_sito", False),
                    "ottimizzazione": st.session_state.get("is_ottimizza", False),
                }
            },
            "evidence": evidence,
            "content":  data
        }
        st.download_button(
            "⬇️ Scarica pacchetto completo (JSON)",
            data=json.dumps(export, ensure_ascii=False, indent=2),
            file_name=f"geo_alligator_{_az.replace(' ','_').lower()}_v3.json",
            mime="application/json"
        )

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
