"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     GEO Score™ Content Generator v4 — Alligator Edition                    ║
║     Senior Python Developer & Data Engineering Build                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

CHANGELOG v4 (anti-hallucination + deep RAG):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OBJ 1 — GERARCHIA DELLA VERITÀ (System Prompt aggiornato)
  • Livello 1: Dati RAG (web) + scraping URL sito web
  • Livello 2: Debrief utente (fatti citabili)
  • Livello 3: Copywriting SEO/GEO (connette dati, NON inventa)
  • Vincolo assoluto: vietato inventare numeri/premi non trovati nelle fonti

OBJ 2 — RICERCA WEB MULTI-QUERY (Deep RAG)
  • get_external_evidence(): 3 query distinte (premi, certificazioni, storia)
  • Aggregazione risultati con deduplicazione
  • Priorità a fonti .gov, .edu e testate di settore

OBJ 3 — SCRAPING DIRETTO URL (BeautifulSoup)
  • scrape_website(): legge homepage + path /chi-siamo, /about, /awards, /premi
  • I dati del sito sovrascrivono la conoscenza generica del modello
  • Timeout e fallback graziosi integrati

OBJ 4 — GEO-ENTITY REINFORCEMENT
  • Entità geografiche ufficiali correlate iniettate nel contesto
  • Mappa regioni → DOP, IGP, Denominazioni, Fascie olivate, ecc.
  • Obbliga il modello a citarle nel testo se rilevanti

OBJ 5 — CAMPO "fonti_utilizzate" nel JSON finale
  • Ogni premio deve essere citato con anno corretto trovato nelle fonti
  • URL reali degli scraping inclusi nell'output

OBJ 6 — BLACKLIST CLICHÉ
  • Lista nera hard-coded nel prompt: "leader di settore", "eccellenza a 360°",
    "sinergia", "soluzioni innovative", "paradigma", "ecosistema", ecc.
  • Sostituzione obbligatoria con dati concreti

CHANGELOG v2/v3 (mantenuti):
  • repair_json(), generazione modulare, Local SEO, Schema JSON-LD
  • claude-haiku-4-5-20251001 default, claude-sonnet-4-6 premium
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import streamlit as st
import json
import re
import time
from typing import Optional
from urllib.parse import urljoin, urlparse

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 1: GEO CRITERIA CONSTANT
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
# SEZIONE 2: CLICHÉ BLACKLIST (OBJ 6)
# ─────────────────────────────────────────────────────────────────────────────
CLICHE_BLACKLIST = [
    "leader di settore", "leader nel settore", "eccellenza a 360 gradi",
    "eccellenza a 360°", "eccellenza italiana", "sinergia", "sinergie",
    "soluzioni innovative", "soluzione innovativa", "paradigma",
    "ecosistema digitale", "ecosistema", "digital transformation",
    "trasformazione digitale", "su misura per voi", "su misura per te",
    "qualità artigianale", "alta qualità", "prodotto di qualità",
    "passione per la qualità", "la nostra missione è",
    "siamo orgogliosi di", "ci distinguiamo per l'eccellenza",
    "best practice", "value proposition", "stakeholder",
    "approccio olistico", "a tutto tondo"
]

CLICHE_PROMPT_BLOCK = f"""BLACKLIST TERMINI VIETATI (ASSOLUTO — zero eccezioni):
I seguenti termini/frasi sono PROIBITI in qualsiasi output:
{chr(10).join(f'  ✗ "{t}"' for t in CLICHE_BLACKLIST)}

REGOLA SOSTITUZIONE OBBLIGATORIA:
  ✗ "olio di eccellenza" → ✓ "olio premiato con 3 Foglie Gambero Rosso 2023"
  ✗ "leader di settore" → ✓ "secondo produttore italiano per volume certificato DOP [fonte]"
  ✗ "soluzioni innovative" → ✓ "sistema brevettato che riduce i tempi del 40%"
  ✗ "alta qualità" → ✓ "acidità 0,18% — sotto la soglia extra vergine del 65%"
Se non hai il dato reale per sostituire: descrivi il processo tecnico verificabile."""

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 3: GEO-ENTITY MAP ITALIANA (OBJ 4)
# Mappa regioni → entità geografiche, DOP, IGP, Denominazioni ufficiali
# ─────────────────────────────────────────────────────────────────────────────
GEO_ENTITY_MAP = {
    "umbria": [
        "DOP Umbria", "Fascia Olivata Assisi-Spoleto", "Colli Assisi-Spoleto",
        "Colli Martani", "Colli Amerini", "Colli del Trasimeno",
        "IGT Umbria", "DOC Orvieto", "DOCG Sagrantino di Montefalco",
        "Denominazione di Origine Protetta Umbria"
    ],
    "toscana": [
        "DOP Toscano", "IGT Toscana", "DOCG Chianti Classico",
        "Strada del Vino e dell'Olio di Lucca, Montecarlo e Versilia",
        "Fascia Olivata Chianti", "DOP Lucca", "DOP Seggiano"
    ],
    "sicilia": [
        "DOP Val di Mazara", "DOP Monte Etna", "DOP Monti Iblei",
        "DOP Valli Trapanesi", "DOP Valdemone", "IGP Sicilia",
        "DOC Etna", "DOCG Cerasuolo di Vittoria"
    ],
    "puglia": [
        "DOP Terra di Bari", "DOP Collina di Brindisi", "DOP Dauno",
        "DOP Terra d'Otranto", "DOP Terre Tarentine", "IGP Puglia",
        "DOC Primitivo di Manduria"
    ],
    "lombardia": [
        "DOP Laghi Lombardi", "DOP Garda Bresciano", "DOP Sebino",
        "DOC Franciacorta", "DOCG Franciacorta", "IGT Lombardia"
    ],
    "campania": [
        "DOP Cilento", "DOP Colline Salernitane", "DOP Penisola Sorrentina",
        "DOP Irpinia - Colline dell'Ufita", "DOC Greco di Tufo",
        "DOCG Fiano di Avellino", "IGT Campania"
    ],
    "calabria": [
        "DOP Bruzio", "DOP Lamezia", "DOP Sotto il Monte",
        "DOP Alto Crotonese", "DOP Esaro", "DOP Sibaritide", "IGP Calabria"
    ],
    "lazio": [
        "DOP Sabina", "DOP Tuscia", "DOP Canino", "DOP Colline Pontine",
        "DOP Colline Teatine", "DOC Frascati", "DOCG Frascati Superiore"
    ],
    "veneto": [
        "DOP Veneto Euganei e Berici", "DOP Veneto Valpolicella",
        "DOP Veneto del Grappa", "DOC Prosecco", "DOCG Amarone della Valpolicella",
        "IGT Venezia Giulia"
    ],
    "sardegna": [
        "DOP Sardegna", "IGP Sardegna", "DOC Vermentino di Gallura",
        "DOCG Vermentino di Gallura", "DOP Cannonau di Sardegna"
    ],
    "marche": [
        "DOP Cartoceto", "IGT Marche", "DOCG Verdicchio dei Castelli di Jesi",
        "DOC Rosso Piceno", "DOP Oliva Ascolana del Piceno"
    ],
    "abruzzo": [
        "DOP Aprutino Pescarese", "DOP Colline Teatine", "DOP Pretuziano delle Rocche",
        "DOC Montepulciano d'Abruzzo", "IGT Abruzzo"
    ],
    "piemonte": [
        "DOP Riviera Ligure", "DOCG Barolo", "DOCG Barbaresco",
        "DOCG Asti", "DOP Langhe", "IGT Piemonte"
    ],
    "trentino": [
        "DOP Garda Trentino", "DOC Trento", "IGT Vigneti delle Dolomiti",
        "DOP Trentino", "DOCG Trento Classico"
    ],
    "emilia romagna": [
        "DOP Brisighella", "DOP Colline di Romagna", "DOP Riviera Ligure",
        "DOP Parmigiano Reggiano", "DOP Prosciutto di Parma", "IGP Mortadella Bologna",
        "DOCG Albana di Romagna"
    ],
}

def get_geo_entities(testo_contesto: str) -> list:
    """Estrae entità geografiche ufficiali correlate dal contesto fornito."""
    testo_lower = testo_contesto.lower()
    matched = []
    for regione, entita in GEO_ENTITY_MAP.items():
        if regione in testo_lower:
            matched.extend(entita)
    return list(dict.fromkeys(matched))  # deduplica mantenendo ordine

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 4: PRICING & MODEL CONFIG
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
    "claude-sonnet-4-6":         "Claude Sonnet 🔋 (premium — raccomandato per RAG)",
    "claude-opus-4-6":           "Claude Opus 💎 (massima qualità)",
    "gpt-4o-mini":               "GPT-4o Mini 💰 (default economico)",
    "gpt-4o":                    "GPT-4o 🔋 (premium)",
    "gpt-4.1-mini":              "GPT-4.1 Mini 💰",
    "gpt-4.1":                   "GPT-4.1 🔋",
}

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
# SEZIONE 5: TOKEN UTILITIES
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
# SEZIONE 6: REPAIR JSON (mantenuto da v2)
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
# SEZIONE 7: SCRAPING DIRETTO URL (OBJ 3)
# Tenta di leggere homepage + pagine /chi-siamo /about /premi /awards
# I dati estratti sovrascrivono la conoscenza generica del modello.
# ─────────────────────────────────────────────────────────────────────────────
def scrape_website(url: str, timeout: int = 8) -> dict:
    """
    Scraping BeautifulSoup di homepage e pagine chiave.
    Ritorna dict con testi estratti e URL visitati.
    Fallback gracioso: restituisce dict vuoto in caso di errore.
    """
    result = {"testi": [], "url_visitati": [], "errori": []}

    if not url or not url.startswith("http"):
        return result

    try:
        from bs4 import BeautifulSoup
        import urllib.request
    except ImportError:
        result["errori"].append("BeautifulSoup4 non installato. Esegui: pip install beautifulsoup4")
        return result

    # Path extra da tentare oltre alla homepage
    extra_paths = [
        "/chi-siamo", "/about", "/about-us", "/azienda",
        "/premi", "/awards", "/riconoscimenti", "/certificazioni",
        "/storia", "/history", "/chi-siamo/premi"
    ]

    parsed_base = urlparse(url)
    base_url = f"{parsed_base.scheme}://{parsed_base.netloc}"
    urls_to_visit = [url] + [urljoin(base_url, p) for p in extra_paths]

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; GeoScoreBot/4.0; +https://alligator.it/bot)"
    }

    for target_url in urls_to_visit[:5]:  # max 5 pagine per non appesantire
        try:
            req = urllib.request.Request(target_url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")

            # Rimuovi script, style, nav, footer
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            # Estrai testo pulito
            text = soup.get_text(separator="\n", strip=True)
            # Comprimi righe vuote multiple
            text = re.sub(r"\n{3,}", "\n\n", text)
            # Tronca a 2000 caratteri per pagina per non saturare il contesto
            text = text[:2000]

            if len(text.strip()) > 100:
                result["testi"].append({
                    "url": target_url,
                    "testo": text
                })
                result["url_visitati"].append(target_url)

            time.sleep(0.3)  # politeness delay

        except Exception as e:
            err = str(e)
            # 404 è normale per path extra — non loggare come errore critico
            if "404" not in err and "403" not in err:
                result["errori"].append(f"{target_url}: {err[:80]}")
            continue

    return result


def format_scrape_for_prompt(scrape_data: dict) -> str:
    """Formatta i dati di scraping in testo leggibile per il prompt."""
    if not scrape_data.get("testi"):
        return ""
    lines = ["=== CONTENUTI ESTRATTI DAL SITO WEB (PRIORITÀ MASSIMA) ==="]
    for item in scrape_data["testi"]:
        lines.append(f"\n[Fonte: {item['url']}]")
        lines.append(item["testo"])
    lines.append("=== FINE CONTENUTI SITO WEB ===")
    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 8: RICERCA WEB MULTI-QUERY — Deep RAG (OBJ 2)
# 3 query distinte: premi, certificazioni, storia/fondazione
# Priorità a .gov, .edu, testate di settore
# ─────────────────────────────────────────────────────────────────────────────
AUTHORITATIVE_DOMAINS = [
    ".gov", ".edu", ".org",
    "gamberorosso.it", "slowfood.it", "coldiretti.it", "confagricoltura.it",
    "ismea.it", "istat.it", "cciaa.it", "cameradicommercio.it",
    "guide.michelin.com", "viadelgusto.it", "olio.com",
    "theathenaeumhotel.com",  # es. premi internazionali
    "flos-olei.com", "terraevita.editrice.it", "freshplaza.it",
    "agrilevante.it", "fieragricola.it", "sana.it",
    "qualivita.it", "origine.info", "dop-igp.it"
]

def score_source_authority(url: str) -> int:
    """Punteggio di autorità della fonte (0-10). Più alto = più priorità."""
    score = 1
    url_lower = url.lower()
    for domain in AUTHORITATIVE_DOMAINS:
        if domain in url_lower:
            score += 3
    if any(tld in url_lower for tld in [".gov.", ".gov/", ".edu.", ".edu/"]):
        score += 5
    # Wikipedia come fallback enciclopedico
    if "wikipedia.org" in url_lower:
        score += 2
    return score


def get_external_evidence(azienda: str, contesto: str = "") -> dict:
    """
    Deep RAG: 3 query distinte per raccogliere evidenze granulari.
    Aggrega risultati, deduplica, ordina per autorità della fonte.
    Richiede: pip install duckduckgo-search
    Fallback gracioso se libreria non disponibile.
    """
    evidence = {
        "premi_riconoscimenti": [],
        "certificazioni_qualita": [],
        "storia_fondazione": [],
        "fonti_aggregate": [],
        "errori": []
    }

    if not azienda:
        return evidence

    try:
        from duckduckgo_search import DDGS
    except ImportError:
        evidence["errori"].append(
            "duckduckgo-search non installato. Esegui: pip install duckduckgo-search"
        )
        return evidence

    queries = {
        "premi_riconoscimenti": f'"{azienda}" premi riconoscimenti guide settore',
        "certificazioni_qualita": f'"{azienda}" certificazioni qualità analisi tecniche',
        "storia_fondazione": f'"{azienda}" storia fondazione sede legale anno',
    }

    seen_urls = set()

    with DDGS() as ddgs:
        for categoria, query in queries.items():
            try:
                raw_results = list(ddgs.text(query, max_results=8, region="it-it"))
                # Ordina per autorità della fonte
                raw_results.sort(
                    key=lambda r: score_source_authority(r.get("href", "")),
                    reverse=True
                )
                for r in raw_results:
                    url = r.get("href", "")
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    entry = {
                        "titolo":    r.get("title", ""),
                        "snippet":   r.get("body", ""),
                        "url":       url,
                        "categoria": categoria,
                        "autorità":  score_source_authority(url)
                    }
                    evidence[categoria].append(entry)
                    evidence["fonti_aggregate"].append(entry)
                time.sleep(0.5)  # rispetta rate limit DDG
            except Exception as e:
                evidence["errori"].append(f"Query '{categoria}': {str(e)[:80]}")

    # Ordina aggregato per autorità decrescente
    evidence["fonti_aggregate"].sort(key=lambda x: x["autorità"], reverse=True)
    return evidence


def format_evidence_for_prompt(evidence: dict) -> str:
    """Formatta le evidenze RAG in testo strutturato per il prompt."""
    if not any(evidence.get(k) for k in ["premi_riconoscimenti", "certificazioni_qualita", "storia_fondazione"]):
        return ""

    lines = ["=== RICERCA WEB — EVIDENZE VERIFICATE (PRIORITÀ ALTA) ==="]
    lines.append("REGOLA: Usa SOLO questi dati per premi, certificazioni e date. Non inventare dati assenti.")

    for cat, label in [
        ("premi_riconoscimenti",  "🏆 PREMI & RICONOSCIMENTI"),
        ("certificazioni_qualita", "📋 CERTIFICAZIONI & ANALISI"),
        ("storia_fondazione",     "🏛️ STORIA & FONDAZIONE"),
    ]:
        items = evidence.get(cat, [])
        if items:
            lines.append(f"\n{label}:")
            for item in items[:4]:  # max 4 per categoria
                lines.append(f"  Fonte: {item['url']}")
                lines.append(f"  Titolo: {item['titolo']}")
                lines.append(f"  Estratto: {item['snippet'][:200]}")
                lines.append("")

    lines.append("=== FINE EVIDENZE WEB ===")
    return "\n".join(lines)


def extract_source_urls(evidence: dict, scrape_data: dict) -> list:
    """Estrae lista URL reali usati come fonti per il campo 'fonti_utilizzate'."""
    urls = []
    for item in evidence.get("fonti_aggregate", []):
        url = item.get("url", "")
        if url and url not in urls:
            urls.append(url)
    for url in scrape_data.get("url_visitati", []):
        if url not in urls:
            urls.append(url)
    return urls[:10]  # max 10 fonti nel JSON finale

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 9: SYSTEM PROMPT BUILDER — GERARCHIA DELLA VERITÀ (OBJ 1 + OBJ 6)
# ─────────────────────────────────────────────────────────────────────────────
def build_system_prompt(stile_esempi: str = "") -> str:
    alligator_rules = """APPROCCIO ALLIGATOR (OBBLIGATORIO):
- DIRETTO: Frasi brevi. Soggetto + Verbo + Oggetto. Zero giri di parole.
- RISULTATI: Ogni affermazione ha una conseguenza misurabile per il cliente.
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

    truth_hierarchy = """
╔══════════════════════════════════════════════════════════════╗
║         GERARCHIA DELLA VERITÀ — VINCOLO ASSOLUTO           ║
╠══════════════════════════════════════════════════════════════╣
║ LIVELLO 1 [MASSIMA PRIORITÀ]:                               ║
║   • Dati estratti dalla Ricerca Web (sezione RAG)           ║
║   • Contenuti scraping del sito web dell'azienda            ║
║   → Premi con anno, certificazioni, analisi chimiche,        ║
║     date di fondazione, sedi, numeri verificati.            ║
║                                                              ║
║ LIVELLO 2 [ALTA PRIORITÀ]:                                  ║
║   • Debrief dell'utente (fatti dichiarati)                  ║
║   → Citabili come "secondo i dati aziendali"                ║
║                                                              ║
║ LIVELLO 3 [SOLO PER CONNETTERE I DATI]:                     ║
║   • Copywriting SEO/GEO                                     ║
║   → Connette i dati reali. NON inventa dati nuovi.          ║
╠══════════════════════════════════════════════════════════════╣
║ ⛔ VINCOLO CRITICO (ANTI-ALLUCINAZIONE):                    ║
║   È SEVERAMENTE VIETATO inventare:                          ║
║   • Numeri di premi non trovati nelle fonti                 ║
║   • Quantità di ristoranti/clienti serviti non verificate   ║
║   • Anni di fondazione non confermati dalle fonti           ║
║   • Certificazioni non trovate nel RAG o nel sito           ║
║   • Punteggi o rating non verificati                        ║
║                                                              ║
║ SE UN DATO NON È NELLE FONTI:                               ║
║   → Descrivi il PROCESSO TECNICO verificabile               ║
║   → Usa "secondo i dati aziendali" per dati da debrief      ║
║   → NON usare numeri inventati o approssimativi              ║
╚══════════════════════════════════════════════════════════════╝"""

    return f"""Sei il copywriter GEO/SEO senior di Alligator. Generi contenuti web ad alta citabilità AI.

{alligator_rules}
{style_section}

{truth_hierarchy}

{CLICHE_PROMPT_BLOCK}

FRAMEWORK GEO SCORE:
{GEO_CRITERIA}

REGOLE OUTPUT (ASSOLUTE):
- Rispondi SOLO con JSON valido. Zero testo fuori dal JSON.
- NO introduzioni, NO conclusioni, NO commenti, NO markdown fuori JSON.
- Ogni sezione: minimo 1 dato numerico citabile (solo se verificato dalle fonti).
- Claim autonomi: ogni frase chiave ha senso estratta fuori contesto.
- Ogni premio citato nel testo DEVE includere l'anno corretto dalla fonte.
- Il campo "fonti_utilizzate" elenca gli URL reali delle fonti usate."""


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 10: CONTEXT BUILDER con RAG + Scraping + GEO Entities
# ─────────────────────────────────────────────────────────────────────────────
def build_ctx(
    azienda: str,
    servizi: str,
    target: str,
    fatti: str,
    local_seo: dict,
    lingua: str,
    rag_evidence: str = "",
    scrape_content: str = "",
    geo_entities: list = None,
    source_urls: list = None
) -> str:
    addr = local_seo.get("indirizzo", "")

    geo_block = ""
    if geo_entities:
        geo_block = f"""
ENTITÀ GEOGRAFICHE UFFICIALI DA CITARE (OBJ GEO-ENTITY):
{chr(10).join(f"  • {e}" for e in geo_entities)}
ISTRUZIONE: Cita queste entità nel testo dove pertinente — sono denominazioni ufficiali
che aumentano l'autorità e la citabilità AI. Non inventare entità non in lista."""

    sources_block = ""
    if source_urls:
        sources_block = f"""
URL FONTI DISPONIBILI (per campo fonti_utilizzate):
{chr(10).join(f"  {u}" for u in source_urls)}"""

    # Il RAG e lo scraping vengono PRIMA del debrief (Livello 1 > Livello 2)
    return f"""{rag_evidence}

{scrape_content}

DEBRIEF AZIENDA (Livello 2 — fatti dichiarati):
AZIENDA: {azienda}
SERVIZI: {servizi}
TARGET: {target}
FATTI CITABILI: {fatti}
INDIRIZZO: {addr if addr else "Non specificato"}
LINGUA OUTPUT: {lingua}
{geo_block}
{sources_block}"""


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 11: PROMPT MODULARI con campo fonti_utilizzate (OBJ 5)
# ─────────────────────────────────────────────────────────────────────────────
def prompt_home(ctx: str) -> str:
    return f"""{ctx}

Genera SOLO il blocco "home". Rispondi ESCLUSIVAMENTE con questo JSON:
{{
  "home": {{
    "h1": "Titolo H1 max 60 char, keyword principale — usa dati reali dal RAG",
    "intro": "150-200 parole. Prima frase = risposta diretta. Minimo 1 dato numerico verificato. Se presente un premio nelle fonti, citalo con anno. Stile Alligator.",
    "sezione_1": {{
      "h2": "H2 valore concreto — dato verificato, non generico",
      "body": "100-150 parole. Dato numerico o fatto unico dalle fonti RAG/sito. Se il dato non c'è nelle fonti, descrivi il processo tecnico."
    }},
    "sezione_2": {{
      "h2": "H2 differenziazione specifica",
      "body": "100-150 parole. Unicità con dati concreti dalle fonti. Zero cliché dalla blacklist."
    }},
    "cta": "1 frase imperativa e specifica",
    "fonti_utilizzate": ["URL1_reale_da_cui_provengono_i_dati", "URL2_se_usato"]
  }}
}}"""


def prompt_servizio(ctx: str) -> str:
    return f"""{ctx}

Genera SOLO il blocco "pagina_servizio". Rispondi ESCLUSIVAMENTE con questo JSON:
{{
  "pagina_servizio": {{
    "h1": "H1 pagina servizio con keyword long-tail",
    "intro": "100-150 parole. Cosa ottiene il cliente, non cosa fa l'azienda. Dati verificati dalle fonti.",
    "come_funziona": {{
      "h2": "Come funziona [Servizio] — titolo descrittivo con dato",
      "steps": [
        "Step 1: azione concreta max 2 righe",
        "Step 2: azione concreta max 2 righe",
        "Step 3: azione concreta max 2 righe",
        "Step 4: azione concreta max 2 righe"
      ]
    }},
    "benefici": {{
      "h2": "Titolo con numero specifico es. 4 risultati concreti",
      "lista": [
        "Beneficio 1 + dato numerico verificato dalle fonti",
        "Beneficio 2 + dato numerico verificato dalle fonti",
        "Beneficio 3 + dato numerico verificato dalle fonti",
        "Beneficio 4 + dato numerico verificato dalle fonti"
      ]
    }},
    "cta": "CTA specifica al servizio, imperativa",
    "fonti_utilizzate": ["URL1_reale", "URL2_se_usato"]
  }}
}}"""


def prompt_faq(ctx: str) -> str:
    return f"""{ctx}

Genera SOLO il blocco "faq" con 5 domande. Ogni risposta deve usare SOLO dati dalle fonti RAG/sito. Rispondi ESCLUSIVAMENTE con questo JSON:
{{
  "faq": [
    {{
      "domanda": "Query reale motore AI — inizia con Come/Cosa/Quanto/Perché/Chi/Dove",
      "risposta": "80-120 parole. Autonoma fuori contesto. Include dato concreto verificato. Se il dato non è nelle fonti, descrive il processo tecnico.",
      "fonte": "URL_fonte_se_disponibile"
    }},
    {{"domanda": "Domanda 2", "risposta": "Risposta 2 80-120 parole", "fonte": ""}},
    {{"domanda": "Domanda 3", "risposta": "Risposta 3 80-120 parole", "fonte": ""}},
    {{"domanda": "Domanda 4", "risposta": "Risposta 4 80-120 parole", "fonte": ""}},
    {{"domanda": "Domanda 5", "risposta": "Risposta 5 80-120 parole", "fonte": ""}}
  ]
}}"""


def prompt_schema(ctx: str, azienda: str, local_seo: dict, faq_data: list) -> str:
    indirizzo = local_seo.get("indirizzo", "")
    url_sito  = local_seo.get("url", "https://www.esempio.it")
    linkedin  = local_seo.get("linkedin", "")
    schema_type = "LocalBusiness" if indirizzo.strip() else "Organization"

    orari = local_seo.get("orari", {})
    orari_str = ""
    giorni_map = {
        "Lunedì": "Monday", "Martedì": "Tuesday", "Mercoledì": "Wednesday",
        "Giovedì": "Thursday", "Venerdì": "Friday", "Sabato": "Saturday", "Domenica": "Sunday"
    }
    for g, (ap, ch) in orari.items():
        if ap and ch:
            g_clean = g.replace("ì","i").replace("è","e").replace("é","e")
            orari_str += f"{giorni_map.get(g_clean, g)}: {ap}-{ch} | "

    return f"""{ctx}
SCHEMA TYPE: {schema_type}
URL: {url_sito}
LINKEDIN: {linkedin if linkedin else "da compilare"}
ORARI: {orari_str if orari_str else "non specificati"}

Genera SOLO il blocco "schema_markup". Usa SOLO dati verificati dalle fonti per la descrizione. Rispondi ESCLUSIVAMENTE con questo JSON:
{{
  "schema_markup": {{
    "organization": {{
      "@context": "https://schema.org",
      "@type": "{schema_type}",
      "name": "{azienda}",
      "description": "Descrizione 160 char max con keyword principale — dati verificati, zero cliché",
      "url": "{url_sito}",
      "sameAs": ["{linkedin if linkedin else 'https://www.linkedin.com/company/esempio'}"],
      "knowsAbout": ["Topic specifico 1 dalle fonti", "Topic specifico 2 dalle fonti", "Topic specifico 3 dalle fonti"]
    }}
  }}
}}"""


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 12: API CALL HANDLERS
# ─────────────────────────────────────────────────────────────────────────────
def call_openai(api_key: str, model: str, system: str, user: str) -> tuple:
    try:
        from openai import OpenAI
        client  = OpenAI(api_key=api_key)
        max_tok = MODEL_MAX_TOKENS.get(model, 4000)
        resp    = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.4,  # abbassato per ridurre allucinazioni
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
            temperature=0.4  # abbassato per ridurre allucinazioni
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
# SEZIONE 13: JSON PARSER ROBUSTO (da v2)
# ─────────────────────────────────────────────────────────────────────────────
def parse_json_response(raw: str) -> Optional[dict]:
    if not raw:
        return None
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    start = cleaned.find("{")
    end   = cleaned.rfind("}") + 1
    if start != -1 and end > start:
        chunk = cleaned[start:end]
        try:
            return json.loads(chunk)
        except json.JSONDecodeError:
            pass
        repaired = repair_json(chunk)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 14: SCHEMA MARKUP BUILDER (da v2)
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

    schema_type     = "LocalBusiness" if indirizzo else "Organization"
    org["@type"]    = schema_type
    org["@context"] = "https://schema.org"
    org["name"]     = azienda
    if url_sito: org["url"]    = url_sito
    if linkedin: org["sameAs"] = [linkedin]

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

    if gps_lat and gps_lon:
        try:
            org["geo"] = {
                "@type":     "GeoCoordinates",
                "latitude":  float(gps_lat),
                "longitude": float(gps_lon)
            }
        except ValueError:
            pass

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

    return json.dumps(
        {"@context": "https://schema.org", "@graph": [org, faq_schema]},
        ensure_ascii=False, indent=2
    )


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 15: UI HELPERS (da v2, invariati)
# ─────────────────────────────────────────────────────────────────────────────
def copy_box(label, text, key):
    st.text_area(label, value=text, height=200, key=key,
                 help="Ctrl+A per selezionare tutto → Ctrl+C per copiare")

def render_home(home):
    st.markdown(f"**H1:** `{home.get('h1','')}`")
    st.markdown(f"**Intro:**\n\n{home.get('intro','')}")
    for k, lbl in [("sezione_1","Sezione 1"),("sezione_2","Sezione 2")]:
        s = home.get(k, {})
        if s:
            st.markdown(f"**H2 {lbl}:** `{s.get('h2','')}`")
            st.markdown(s.get("body",""))
    st.markdown(f"**CTA:** _{home.get('cta','')}_")
    if home.get("fonti_utilizzate"):
        with st.expander("📎 Fonti utilizzate per questa sezione"):
            for u in home["fonti_utilizzate"]:
                st.markdown(f"- {u}")

def render_service(page):
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
    if page.get("fonti_utilizzate"):
        with st.expander("📎 Fonti utilizzate per questa sezione"):
            for u in page["fonti_utilizzate"]:
                st.markdown(f"- {u}")

def render_faq(faqs):
    for i, faq in enumerate(faqs, 1):
        with st.expander(f"❓ {faq.get('domanda', f'FAQ {i}')}"):
            st.markdown(faq.get("risposta", ""))
            fonte = faq.get("fonte", "")
            if fonte:
                st.caption(f"📎 Fonte: {fonte}")

def home_to_md(h):
    t = f"# {h.get('h1','')}\n\n{h.get('intro','')}\n\n"
    for k in ["sezione_1","sezione_2"]:
        s = h.get(k, {})
        if s: t += f"## {s.get('h2','')}\n\n{s.get('body','')}\n\n"
    t += h.get("cta","")
    fonti = h.get("fonti_utilizzate", [])
    if fonti:
        t += "\n\n---\n**Fonti:** " + " | ".join(fonti)
    return t

def service_to_md(p):
    t = f"# {p.get('h1','')}\n\n{p.get('intro','')}\n\n"
    cf = p.get("come_funziona", {})
    if cf:
        t += f"## {cf.get('h2','')}\n\n"
        for s in cf.get("steps", []): t += f"- {s}\n"
        t += "\n"
    ben = p.get("benefici", {})
    if ben:
        t += f"## {ben.get('h2','')}\n\n"
        for b in ben.get("lista", []): t += f"✅ {b}\n"
        t += "\n"
    t += p.get("cta","")
    fonti = p.get("fonti_utilizzate", [])
    if fonti:
        t += "\n\n---\n**Fonti:** " + " | ".join(fonti)
    return t

def faq_to_md(faqs):
    t = "## Domande Frequenti\n\n"
    for f in faqs:
        t += f"### {f.get('domanda','')}\n\n{f.get('risposta','')}\n\n"
        if f.get("fonte"):
            t += f"*Fonte: {f['fonte']}*\n\n"
    return t


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 16: MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="GEO Score™ v4 — Alligator Anti-Hallucination",
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
    .truth-box {
        background: #fff7ed; border-left: 4px solid #f59e0b;
        padding: 0.7rem 1rem; border-radius: 6px; margin: 0.4rem 0; font-size: 0.85rem;
    }
    .rag-box {
        background: #f0fdf4; border-left: 4px solid #22c55e;
        padding: 0.7rem 1rem; border-radius: 6px; margin: 0.4rem 0; font-size: 0.85rem;
    }
    .module-card {
        border: 1px solid #e2e8f0; border-radius: 8px;
        padding: 0.75rem 1rem; margin: 0.3rem 0; background: #fafafa;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="geo-header">
        <h1>🐊 GEO Score™ Content Generator v4 — Anti-Hallucination Edition</h1>
        <p>Deep RAG · URL Scraping · GEO-Entity Reinforcement · Gerarchia della Verità · Cliché Blacklist · Framework GEO Score™ by Nico Fioretti</p>
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

        st.markdown("""
        <div class="truth-box">
        <b>🔺 Gerarchia della Verità v4</b><br>
        L1: RAG Web + Scraping URL<br>
        L2: Debrief utente<br>
        L3: SEO copy (connette, non inventa)
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.subheader("💰 Stima Costi")
        sys_tok = estimate_tokens(build_system_prompt())
        in_est  = sys_tok + 800   # contesto più grande con RAG
        out_est = 1200
        cpp     = estimate_cost(in_est, out_est, provider, model)
        st.markdown(f"""
        <div class="cost-box">
            <b>Per sezione (con RAG):</b><br>
            Input ~{in_est:,} tok · Output ~{out_est:,} tok<br>
            <b>Costo/sezione: ${cpp:.5f}</b><br>
            4 sezioni totali: <b>~${cpp*4:.5f}</b>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        with st.expander("📖 GEO 8 Dimensioni"):
            st.markdown("1.⚙️Tecnica · 2.📝Contenuto · 3.🏷️Identità · 4.🔍Leggibilità\n5.🌐Autorità · 6.🏅Credibilità · 7.💎Unicità · 8.🔄Freschezza")
        with st.expander("🚫 Cliché Blacklist attiva"):
            for t in CLICHE_BLACKLIST:
                st.markdown(f"✗ _{t}_")

    # ── TABS ─────────────────────────────────────────────────────────────────
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
                                    placeholder="es. Frantoio Muraglia")
            servizi = st.text_area("Servizi / Prodotti Principali *", key="servizi", height=100,
                                   placeholder="es. Olio EVO DOP, Frantoiatura, Vendita diretta")
        with c2:
            target  = st.text_area("Target / Clienti Ideali *", key="target", height=100,
                                   placeholder="es. Ristoratori stellati, gourmet B2C, export EU")
            lingua  = st.selectbox("Lingua Output", ["italiano","inglese","francese","spagnolo"],
                                   key="lingua")

        fatti = st.text_area(
            "💡 Fatti Unici & Citabili *", key="fatti", height=130,
            placeholder='"Premio Flos Olei 2023 · "Blend cultivar Coratina/Ogliarola" · "Acidità 0.18%"'
        )

        st.divider()

        # STYLE BRAND
        st.markdown("#### 🐊 Tono di Voce — Esempi Reali di Copy")
        st.caption("Il modello replica esattamente questo tono.")
        stile_esempi = st.text_area(
            "Esempi di Stile/Copy (opzionale)",
            key="stile_esempi", height=130,
            placeholder='"Non vendiamo visibilità. Costruiamo autorità che dura."\n"Meno traffico inutile. Più richieste qualificate."'
        )

        st.divider()

        # LOCAL SEO
        st.markdown("#### 📍 Dati Local SEO (Schema Markup)")
        st.caption("Compilati automaticamente in JSON-LD LocalBusiness.")

        col_a, col_b = st.columns(2)
        with col_a:
            via_civico = st.text_input("Via e Numero Civico", key="via",
                                       placeholder="es. Contrada Sant'Angelo 68")
            cap        = st.text_input("CAP",       key="cap",   placeholder="76123")
            citta      = st.text_input("Città",     key="citta", placeholder="Andria")
            provincia  = st.text_input("Provincia", key="prov",  placeholder="BT")
        with col_b:
            url_sito = st.text_input(
                "URL Sito Web (usato per scraping automatico)",
                key="url_sito",
                placeholder="https://www.frantoiomuraglia.it"
            )
            linkedin = st.text_input("URL LinkedIn Company", key="linkedin",
                                      placeholder="https://www.linkedin.com/company/...")
            gps_lat  = st.text_input("Latitudine GPS (opz.)", key="gps_lat",
                                      placeholder="41.2232")
            gps_lon  = st.text_input("Longitudine GPS (opz.)", key="gps_lon",
                                      placeholder="16.2934")

        # GRIGLIA ORARI
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
            url_val = st.session_state.get("url_sito","")
            scrape_note = "🌐 URL inserito → scraping automatico attivo" if url_val else "⚠️ URL non inserito → scraping disattivato"
            st.success(f"✅ Debrief completo · Schema: **{stype}** · {scrape_note}")
        else:
            st.info("💡 Compila i campi obbligatori (*) per sbloccare il Generatore.")

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 2: GENERATORE MODULARE
    # ═══════════════════════════════════════════════════════════════════════
    with tab2:
        st.subheader("🛠️ Generatore Modulare — Anti-Hallucination v4")

        _az  = st.session_state.get("azienda","")
        _sv  = st.session_state.get("servizi","")
        _tg  = st.session_state.get("target","")
        _ft  = st.session_state.get("fatti","")
        _ln  = st.session_state.get("lingua","italiano")
        _st  = st.session_state.get("stile_esempi","")
        _loc = st.session_state.get("local_seo",{})

        ready = bool(_az and _sv and _tg and _ft and api_key)

        if not ready:
            missing = [x for x,v in [
                ("Nome Azienda",_az),("Servizi",_sv),("Target",_tg),
                ("Fatti",_ft),("API Key (sidebar)",api_key)
            ] if not v]
            st.warning(f"⚠️ Mancano: **{', '.join(missing)}**")

        # ── OPZIONI RAG ──────────────────────────────────────────────────
        st.markdown("#### 🔍 Configurazione Deep RAG & Scraping")

        col_rag1, col_rag2 = st.columns(2)
        with col_rag1:
            enable_rag = st.checkbox(
                "🌐 Abilita Ricerca Web Multi-Query (Deep RAG)",
                value=True, key="enable_rag",
                help="3 query distinte: premi, certificazioni, storia. Richiede: pip install duckduckgo-search"
            )
        with col_rag2:
            enable_scraping = st.checkbox(
                "🕷️ Abilita Scraping URL Sito Web",
                value=True, key="enable_scraping",
                help="Legge homepage + /chi-siamo /premi /about. Richiede: pip install beautifulsoup4"
            )

        if enable_rag or enable_scraping:
            st.markdown("""
            <div class="rag-box">
            📦 <b>Dipendenze richieste:</b><br>
            <code>pip install duckduckgo-search beautifulsoup4</code><br>
            Il RAG viene eseguito UNA VOLTA prima della generazione e iniettato in ogni prompt.
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ── SELEZIONE SEZIONI ────────────────────────────────────────────
        st.markdown("#### Seleziona le sezioni da generare")
        st.caption("1 sezione = 1 chiamata API · Output ~1200 token → nessun troncamento JSON.")

        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            gen_home    = st.checkbox("🏠 Homepage",        value=True, key="gen_home")
            st.caption("H1, intro, 2 sezioni, CTA + fonti")
        with mc2:
            gen_service = st.checkbox("📄 Pagina Servizio", value=True, key="gen_service")
            st.caption("H1, come funziona, benefici, CTA")
        with mc3:
            gen_faq     = st.checkbox("❓ FAQ (5 domande)",  value=True, key="gen_faq")
            st.caption("Query AI reali, con fonte per risposta")
        with mc4:
            gen_schema  = st.checkbox("🔗 Schema Markup",   value=True, key="gen_schema")
            st.caption("JSON-LD LocalBusiness/Org + FAQ")

        n_sel = sum([gen_home, gen_service, gen_faq, gen_schema])
        if n_sel == 0:
            st.warning("Seleziona almeno una sezione.")

        st.divider()

        if ready and n_sel > 0:
            sp_preview = build_system_prompt(_st)
            in_est_r   = estimate_tokens(sp_preview) + 800
            tot_est    = estimate_cost(in_est_r, 1200, provider, model) * n_sel
            extra_calls = (1 if enable_rag else 0)
            st.info(f"📊 **{n_sel} chiamate AI** + **{extra_calls} fase RAG** · Costo totale stimato: **${tot_est:.5f}**")

        gen_btn = st.button(
            f"🚀 Genera {n_sel} sezione{'i' if n_sel!=1 else ''}",
            disabled=(not ready or n_sel==0),
            type="primary"
        )

        if gen_btn and ready and n_sel > 0:
            sys_p = build_system_prompt(_st)

            total_in  = 0
            total_out = 0
            generated = dict(st.session_state.get("generated", {}))
            call_log  = []

            # ── FASE 0: RAG & SCRAPING ────────────────────────────────
            rag_evidence_str  = ""
            scrape_content_str = ""
            all_source_urls   = []
            geo_entities      = get_geo_entities(f"{_az} {_ft} {_loc.get('indirizzo','')}")

            if enable_scraping and _loc.get("url","").startswith("http"):
                with st.spinner("🕷️ Scraping sito web in corso..."):
                    scrape_data = scrape_website(_loc["url"])
                    scrape_content_str = format_scrape_for_prompt(scrape_data)
                    all_source_urls.extend(scrape_data.get("url_visitati",[]))
                    if scrape_data.get("errori"):
                        st.warning("⚠️ Scraping parziale: " + "; ".join(scrape_data["errori"][:2]))
                    elif scrape_content_str:
                        st.success(f"✅ Scraping: {len(scrape_data['testi'])} pagine lette")
                    else:
                        st.info("ℹ️ Scraping: nessun contenuto significativo estratto")

            if enable_rag and _az:
                with st.spinner("🌐 Ricerca web multi-query in corso (3 query)..."):
                    evidence = get_external_evidence(_az)
                    rag_evidence_str = format_evidence_for_prompt(evidence)
                    rag_source_urls  = extract_source_urls(evidence, {})
                    all_source_urls.extend(rag_source_urls)
                    if evidence.get("errori"):
                        st.warning("⚠️ RAG parziale: " + "; ".join(evidence["errori"][:2]))
                    elif rag_evidence_str:
                        n_fonti = len(evidence.get("fonti_aggregate",[]))
                        st.success(f"✅ RAG: {n_fonti} risultati aggregati da {len(rag_source_urls)} fonti")
                    else:
                        st.info("ℹ️ RAG: nessun risultato trovato (proseguo con debrief)")

            if geo_entities:
                st.info(f"🗺️ GEO-Entity: {len(geo_entities)} entità geografiche iniettate nel contesto")

            # ── FASE 1: GENERAZIONE SEZIONI ───────────────────────────
            ctx = build_ctx(
                _az, _sv, _tg, _ft, _loc, _ln,
                rag_evidence=rag_evidence_str,
                scrape_content=scrape_content_str,
                geo_entities=geo_entities,
                source_urls=all_source_urls
            )

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

            # ── Aggiungi metadati anti-hallucination al JSON ──────────
            if generated:
                generated["_meta_fonti"] = {
                    "fonti_rag":     all_source_urls,
                    "geo_entities":  geo_entities,
                    "rag_attivo":    enable_rag,
                    "scraping_attivo": enable_scraping,
                    "url_scraping":  _loc.get("url","")
                }

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
        st.subheader("📄 Risultati — Anti-Hallucination v4")

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

        # Mostra fonti aggregate se disponibili
        meta = data.get("_meta_fonti", {})
        if meta.get("fonti_rag"):
            with st.expander(f"📎 {len(meta['fonti_rag'])} Fonti RAG utilizzate nella generazione"):
                for u in meta["fonti_rag"]:
                    st.markdown(f"- [{u}]({u})")
        if meta.get("geo_entities"):
            with st.expander(f"🗺️ {len(meta['geo_entities'])} Entità geografiche iniettate"):
                for e in meta["geo_entities"]:
                    st.markdown(f"- {e}")

        st.divider()

        # Costruisci tab risultati
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
                "azienda":   _az,
                "provider":  provider,
                "model":     model,
                "in_tokens": in_t,
                "out_tokens":out_t,
                "cost_usd":  cost_r,
                "local_seo": _loc,
                "fonti_rag":     meta.get("fonti_rag", []),
                "geo_entities":  meta.get("geo_entities", []),
                "rag_attivo":    meta.get("rag_attivo", False),
                "scraping_attivo": meta.get("scraping_attivo", False),
            },
            "content": data
        }

        st.download_button(
            "⬇️ Scarica pacchetto completo (JSON con fonti)",
            data=json.dumps(export, ensure_ascii=False, indent=2),
            file_name=f"geo_alligator_v4_{_az.replace(' ','_').lower()}.json",
            mime="application/json"
        )


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
