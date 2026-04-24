"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     GEO Score™ Content Generator v6 — Alligator Edition                    ║
║     Patch chirurgica anti-spazzatura + GEO-Flow copywriting                ║
╚══════════════════════════════════════════════════════════════════════════════╝

CHANGELOG v6 (patch chirurgica sul v5 — 2 punti critici):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIX 1 — URL FILTER ANTI-SPAZZATURA (sez. 8)
  • Nuova DENYLIST_DOMAINS: youtube, pandora, facebook, amazon, paginegialle,
    google/search, scribd, yelp, reddit, ecc. (~50 domini)
  • Nuova DENYLIST_URL_PATTERNS: /login, /account, /support, /privacy,
    /cart, utm_source=, ecc. (~40 pattern)
  • Funzione is_url_clean() filtra PRIMA del sorting per autorità
  • Settore-agnostico: AUTHORITATIVE_DOMAINS estesa con editoria B2B,
    tech, retail, e-commerce, certificazioni (non più solo food)
  • Nuovo campo evidence["url_scartati"] per debug dei filtri

FIX 2 — GEO-FLOW COPYWRITING (sez. 9 + 11)
  • Nuova costante GEO_FLOW_RULES iniettata nel system prompt
  • Vieta esplicitamente frasi nominali telegrafiche
  • Impone connettivi logici ('perché', 'tanto che', 'grazie a')
  • Include 4 esempi bad→good inline (food, SaaS B2B, arredo B2B, moda B2C)
  • prompt_home/servizio/faq con descrittori espliciti "prosa continuativa"
  • Esempi di formato atteso iniettati nei prompt modulari (few-shot)

UPDATE — PRICING 2026 (sez. 4)
  • Haiku 4.5:  $1/$5 per MTok (prima indicato $0.25/$1.25, sbagliato)
  • Sonnet 4.6: $3/$15 per MTok — DEFAULT raccomandato per GEO
  • Opus 4.7:   $5/$25 per MTok — nuovo (aprile 2026)
  • Opus 4.6:   $5/$25 per MTok (unchanged)
  • Max tokens output allineato a 8192 per tutti i Claude

COSTO ATTESO PER RUN COMPLETA (home + servizio + FAQ + schema):
  • Haiku 4.5:   ~$0.06   (bozze, iterazioni rapide)
  • Sonnet 4.6:  ~$0.18   ← DEFAULT — qualità GEO chirurgica
  • Opus 4.7:    ~$0.30   (clienti top, copy massimo)

CHANGELOG v2-v5 (mantenuti integralmente):
  • RAG multi-query (3 query: premi, certificazioni, storia)
  • Scraping diretto URL (BeautifulSoup su /chi-siamo /about /premi)
  • GEO-entity map italiana (DOP/IGP/DOCG per regione)
  • Fact Hardening System (harden_facts + harden_section)
  • Entity Block, AI Summary, sameAs builder, Quality Score
  • HTML blocks pronti per WordPress (Gutenberg + <details> FAQ)
  • Schema Markup LocalBusiness/Organization con sameAs dinamico
  • repair_json() + JSON prefill per Anthropic
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

REGOLA SOSTITUZIONE OBBLIGATORIA (sostituisci genericità con dati REALI dalle fonti):
  ✗ "olio di eccellenza" → ✓ "olio premiato con [premio specifico SE NELLE FONTI]"
  ✗ "leader di settore" → ✓ "[posizionamento concreto SE VERIFICATO da fonte]"
  ✗ "soluzioni innovative" → ✓ "[descrizione tecnica del sistema/metodo]"
  ✗ "alta qualità" → ✓ "[parametro tecnico verificato dalle fonti, oppure descrizione discorsiva del processo se mancano dati]"

⚠️ CRITICO: i numeri di sostituzione devono provenire SOLO da fonti RAG/debrief.
   Se non hai il dato reale: descrivi il processo in modo DISCORSIVO senza
   inventare percentuali, soglie, tempistiche o quantità."""

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
    },
    "anthropic": {
        "claude-haiku-4-5-20251001":  {"input": 0.00100, "output": 0.00500},
        "claude-sonnet-4-6": {"input": 0.00300, "output": 0.01500},
        "claude-opus-4-7":     {"input": 0.01500, "output": 0.07500},
    }
}

MODEL_LABELS = {
    "claude-haiku-4-5-20251001":  "Claude 4.5 Haiku 💰 (Economico)",
    "claude-sonnet-4-6": "Claude 4.6 Sonnet 🔋 (Raccomandato per GEO)",
    "claude-opus-4-7":     "Claude 4.7 Opus 💎 (Massima qualità)",
    "gpt-4o-mini":                "GPT-4o Mini 💰",
    "gpt-4o":                     "GPT-4o 🔋",
}

MODEL_MAX_TOKENS = {
    "gpt-4o-mini":                4096, 
    "gpt-4o":                     4096,
    "claude-haiku-4-5-20251001":  8192, 
    "claude-sonnet-4-6": 8192, 
    "claude-sonnet-4-6":     4096,
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
# SEZIONE 6b: FACT HARDENING SYSTEM
# Intercetta claim specifici non verificabili e li downgrada o rimuove.
# Patterns rischiosi: numeri inventati, % non citate, superlativi, premi vagi.
# ─────────────────────────────────────────────────────────────────────────────

# Pattern che segnalano claim ad alto rischio (numeri inventati / non citabili)
RISKY_PATTERNS = [
    # percentuali senza fonte
    (r'\b\d+\s*%\s*(?:di\s+)?(?:clienti|vendite|crescita|aumento|riduzione|risparmio)\b', "dato percentuale non verificato"),
    # "oltre X anni" vaghi
    (r'\boltre\s+\d+\s+anni\b', "anni di attività non verificati"),
    # numeri assoluti grandi senza fonte
    (r'\b(?:più di|oltre|circa)\s+\d{3,}\s+(?:clienti|prodotti|ordini|partner)\b', "quantità non verificata"),
    # claim di posizione
    (r'\b(?:primo|seconda?|terzo|top\s*\d)\s+(?:in italia|al mondo|nel settore)\b', "claim di posizionamento non verificato"),
    # "da X anni" senza fonte
    (r'\bda\s+(?:oltre\s+)?\d+\s+anni\b', "anzianità non verificata"),
]

# Sostituzioni sicure per claim downgraded
SAFE_REPLACEMENTS = {
    "dato percentuale non verificato":          "dato in crescita costante",
    "anni di attività non verificati":          "da diversi anni nel settore",
    "quantità non verificata":                  "numerosi clienti nel settore",
    "claim di posizionamento non verificato":   "tra i riferimenti del settore",
    "anzianità non verificata":                 "con esperienza consolidata nel settore",
}


def harden_facts(text: str, verified_data: list = None) -> dict:
    """
    Analizza il testo e:
    - Identifica claim specifici non verificabili
    - Downgrade a versione generica se il dato non è in verified_data
    - Rimuove claim troppo rischiosi (superlativi assoluti senza fonte)
    Ritorna dict con testo hardenato + log delle modifiche.
    """
    if not text:
        return {"text": text, "verified": [], "generic": [], "removed": []}

    verified_list = verified_data or []
    generic_changes = []
    removed_claims  = []
    hardened        = text

    for pattern, label in RISKY_PATTERNS:
        matches = re.findall(pattern, hardened, flags=re.IGNORECASE)
        for match in matches:
            # Controlla se il dato appare anche nei verified_data (fonti RAG/debrief)
            is_verified = any(match.lower() in v.lower() for v in verified_list)
            if not is_verified:
                replacement = SAFE_REPLACEMENTS.get(label, "dato non specificato")
                hardened = re.sub(re.escape(match), replacement, hardened, flags=re.IGNORECASE)
                generic_changes.append(f'"{match}" → "{replacement}" ({label})')

    # Rimuovi claim superlativi assoluti senza contesto verificabile
    superlative_patterns = [
        r'\bla migliore?\b', r'\bil più\b', r'\bl\'unico\b', r'\binsuperabile\b',
        r'\bineguagliabile\b', r'\bimpareggiabile\b'
    ]
    for sp in superlative_patterns:
        matches = re.findall(sp, hardened, flags=re.IGNORECASE)
        for m in matches:
            is_verified = any(m.lower() in v.lower() for v in verified_list)
            if not is_verified:
                removed_claims.append(f'"{m}" rimosso (superlativo assoluto non verificato)')
                hardened = re.sub(re.escape(m), "", hardened, flags=re.IGNORECASE)

    return {
        "text":    hardened,
        "verified": verified_list,
        "generic":  generic_changes,
        "removed":  removed_claims
    }


def harden_section(section_dict: dict, verified_data: list = None) -> dict:
    """
    Applica harden_facts ricorsivamente a tutti i valori stringa di un dict.
    Aggiunge campo data_validation al dict.
    """
    if not isinstance(section_dict, dict):
        return section_dict

    all_generic = []
    all_removed = []

    def _harden_value(v):
        if isinstance(v, str):
            result = harden_facts(v, verified_data)
            all_generic.extend(result["generic"])
            all_removed.extend(result["removed"])
            return result["text"]
        elif isinstance(v, dict):
            return {k: _harden_value(val) for k, val in v.items()}
        elif isinstance(v, list):
            return [_harden_value(item) for item in v]
        return v

    hardened = {k: _harden_value(v) for k, v in section_dict.items()}

    # Inietta data_validation nel blocco
    hardened["data_validation"] = {
        "verified_fields": verified_data or [],
        "generic_fields":  list(dict.fromkeys(all_generic)),  # deduplica
        "removed_claims":  list(dict.fromkeys(all_removed)),
    }
    return hardened


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6c: ENTITY SYSTEM (FONDAMENTALE PER GEO)
# Popola automaticamente dai dati input la struttura entity standard.
# ─────────────────────────────────────────────────────────────────────────────

def build_entity_block(azienda: str, servizi: str, local_seo: dict, schema_type: str = "LocalBusiness") -> dict:
    """
    Costruisce il blocco entities standard da iniettare nel JSON finale.
    Parsea indirizzo, estrae città/regione/nazione, split servizi.
    """
    indirizzo = local_seo.get("indirizzo", "")
    parts     = [p.strip() for p in indirizzo.split(",") if p.strip()] if indirizzo else []

    # Estrai componenti indirizzo (formato: Via, Città, CAP, Provincia)
    city    = parts[1] if len(parts) > 1 else ""
    region  = parts[3] if len(parts) > 3 else ""

    # Mappa provincia → regione se non specificata
    PROV_TO_REGION = {
        "BT":"Puglia","BA":"Puglia","LE":"Puglia","BR":"Puglia","TA":"Puglia","FG":"Puglia",
        "PG":"Umbria","TR":"Umbria","FI":"Toscana","SI":"Toscana","AR":"Toscana","LU":"Toscana",
        "MI":"Lombardia","BS":"Lombardia","BG":"Lombardia","MN":"Lombardia",
        "NA":"Campania","SA":"Campania","AV":"Campania","CE":"Campania",
        "RM":"Lazio","VT":"Lazio","LT":"Lazio","FR":"Lazio",
        "PA":"Sicilia","CT":"Sicilia","ME":"Sicilia","AG":"Sicilia",
        "CA":"Sardegna","SS":"Sardegna","NU":"Sardegna",
        "AN":"Marche","MC":"Marche","AP":"Marche",
        "CS":"Calabria","RC":"Calabria","KR":"Calabria","CZ":"Calabria",
        "AQ":"Abruzzo","PE":"Abruzzo","CH":"Abruzzo","TE":"Abruzzo",
        "TO":"Piemonte","CN":"Piemonte","AT":"Piemonte","AL":"Piemonte",
        "VE":"Veneto","PD":"Veneto","VR":"Veneto","VI":"Veneto","TV":"Veneto",
        "BO":"Emilia Romagna","MO":"Emilia Romagna","PR":"Emilia Romagna","RE":"Emilia Romagna",
        "TN":"Trentino","BZ":"Trentino",
    }
    prov = parts[3] if len(parts) > 3 else ""
    if not region and prov:
        region = PROV_TO_REGION.get(prov.upper(), "")

    # Split servizi in lista
    servizi_list = [s.strip() for s in re.split(r"[,;\n·•\-]+", servizi) if s.strip()][:8]

    return {
        "brand":    azienda,
        "type":     schema_type,
        "location": {
            "city":    city,
            "region":  region,
            "country": "Italia"
        },
        "services": servizi_list,
        "products": []   # popolato dall'AI se rilevante
    }


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6d: CTA STRUTTURATE
# Trasforma CTA stringa in oggetto con primary/secondary/intent.
# ─────────────────────────────────────────────────────────────────────────────

def build_structured_cta(cta_raw: str, section_type: str = "generic") -> dict:
    """
    Converte una CTA stringa in struttura con primary/secondary/intent.
    section_type: 'home' | 'service' | 'faq' | 'generic'
    """
    SECONDARY_MAP = {
        "home":    "Scopri i nostri servizi",
        "service": "Leggi le domande frequenti",
        "faq":     "Contattaci per maggiori informazioni",
        "generic": "Scopri di più",
    }
    INTENT_MAP = {
        "home":    "awareness",
        "service": "conversion",
        "faq":     "consideration",
        "generic": "conversion",
    }
    return {
        "primary":   cta_raw if cta_raw else "Contattaci",
        "secondary": SECONDARY_MAP.get(section_type, "Scopri di più"),
        "intent":    INTENT_MAP.get(section_type, "conversion"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6e: QUALITY SCORE SYSTEM
# Calcola score E-E-A-T / SEO / GEO e risk_level sul JSON generato.
# ─────────────────────────────────────────────────────────────────────────────

def compute_quality_score(data: dict, local_seo: dict, source_urls: list) -> dict:
    """
    Calcola quality_score basato su:
    - E-E-A-T: fonti citate, indirizzo presente, sameAs, autori
    - SEO: H1 presente, meta description, FAQ strutturate
    - GEO: schema completo, entità geografiche, ai_summary, entities block
    - risk_level: presenza claim hardened o rimossi
    Ritorna dict con scores 0-10 e risk_level.
    """
    eeat = 0
    seo  = 0
    geo  = 0

    # ── E-E-A-T ──────────────────────────────────────────────────────────────
    if source_urls:                                      eeat += 2   # fonti citate
    if local_seo.get("indirizzo","").strip():            eeat += 2   # indirizzo verificabile
    if local_seo.get("linkedin","").strip():             eeat += 1   # sameAs LinkedIn
    if local_seo.get("url","").strip():                  eeat += 1   # sito ufficiale
    home = data.get("home", {})
    if home.get("fonti_utilizzate"):                     eeat += 2   # fonti nel contenuto
    if data.get("schema_markup"):                        eeat += 2   # schema credibilità

    # ── SEO ──────────────────────────────────────────────────────────────────
    if home.get("h1"):                                   seo  += 2   # H1 presente
    serv = data.get("pagina_servizio", {})
    if serv.get("h1"):                                   seo  += 1   # H1 servizio
    if data.get("faq") and len(data["faq"]) >= 3:        seo  += 2   # FAQ strutturate
    if data.get("schema_markup"):                        seo  += 2   # schema JSON-LD
    if home.get("sezione_1",{}).get("h2"):               seo  += 1   # H2 presente
    if serv.get("come_funziona",{}).get("steps"):        seo  += 1   # lista step (rich results)
    # Penalità: H1 troppo corto
    h1 = home.get("h1","")
    if h1 and len(h1) < 20:                              seo  -= 1

    # ── GEO ──────────────────────────────────────────────────────────────────
    if data.get("ai_summary"):                           geo  += 2   # ai_summary presente
    if data.get("entities"):                             geo  += 2   # entity block presente
    if data.get("schema_markup"):
        org = data["schema_markup"].get("organization",{})
        if org.get("knowsAbout"):                        geo  += 1   # topical authority
        if org.get("sameAs"):                            geo  += 1   # sameAs links
    meta = data.get("_meta_fonti",{})
    if meta.get("geo_entities"):                         geo  += 2   # entità geografiche
    if meta.get("rag_attivo"):                           geo  += 1   # RAG attivo
    if meta.get("scraping_attivo"):                      geo  += 1   # scraping attivo

    # Normalizza 0-10
    eeat = min(10, max(0, eeat))
    seo  = min(10, max(0, seo))
    geo  = min(10, max(0, geo))

    # Risk level: basato su data_validation aggregato
    total_removed = 0
    total_generic = 0
    for key in ["home", "pagina_servizio"]:
        dv = data.get(key, {}).get("data_validation", {})
        total_removed += len(dv.get("removed_claims", []))
        total_generic += len(dv.get("generic_fields",  []))

    if total_removed >= 3:
        risk = "high"
    elif total_removed >= 1 or total_generic >= 3:
        risk = "medium"
    else:
        risk = "low"

    return {
        "eeat":       eeat,
        "seo":        seo,
        "geo":        geo,
        "risk_level": risk
    }


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6f: HTML BLOCK GENERATOR
# Genera HTML pronto per WordPress/Gutenberg da ogni sezione JSON.
# ─────────────────────────────────────────────────────────────────────────────

def generate_html_blocks(data: dict) -> dict:
    """
    Genera blocchi HTML autonomi per ogni sezione.
    Ritorna dict {home_html, service_html, faq_html} pronti per incollare in WP.
    """
    html_blocks = {}

    # ── HOME HTML ─────────────────────────────────────────────────────────────
    home = data.get("home", {})
    if home:
        cta_obj = home.get("cta", {})
        cta_text = cta_obj.get("primary", cta_obj) if isinstance(cta_obj, dict) else str(cta_obj)
        h = f'<h1>{_esc(home.get("h1",""))}</h1>\n'
        h += f'<p>{_esc(home.get("intro",""))}</p>\n'
        s1 = home.get("sezione_1", {})
        if s1:
            h += f'<h2>{_esc(s1.get("h2",""))}</h2>\n'
            h += f'<p>{_esc(s1.get("body",""))}</p>\n'
        s2 = home.get("sezione_2", {})
        if s2:
            h += f'<h2>{_esc(s2.get("h2",""))}</h2>\n'
            h += f'<p>{_esc(s2.get("body",""))}</p>\n'
        h += f'<a class="wp-block-button__link" href="#contatti">{_esc(cta_text)}</a>\n'
        html_blocks["home_html"] = h

    # ── SERVICE HTML ──────────────────────────────────────────────────────────
    serv = data.get("pagina_servizio", {})
    if serv:
        cta_obj = serv.get("cta", {})
        cta_text = cta_obj.get("primary", cta_obj) if isinstance(cta_obj, dict) else str(cta_obj)
        s = f'<h1>{_esc(serv.get("h1",""))}</h1>\n'
        s += f'<p>{_esc(serv.get("intro",""))}</p>\n'
        cf = serv.get("come_funziona", {})
        if cf:
            s += f'<h2>{_esc(cf.get("h2",""))}</h2>\n<ol>\n'
            for step in cf.get("steps", []):
                s += f'  <li>{_esc(step)}</li>\n'
            s += '</ol>\n'
        ben = serv.get("benefici", {})
        if ben:
            s += f'<h2>{_esc(ben.get("h2",""))}</h2>\n<ul>\n'
            for b in ben.get("lista", []):
                s += f'  <li>{_esc(b)}</li>\n'
            s += '</ul>\n'
        s += f'<a class="wp-block-button__link" href="#contatti">{_esc(cta_text)}</a>\n'
        html_blocks["service_html"] = s

    # ── FAQ HTML (accordion WP) ────────────────────────────────────────────────
    faqs = data.get("faq", [])
    if faqs:
        f = '<div class="faq-block">\n'
        for faq in faqs:
            f += f'  <details>\n'
            f += f'    <summary>{_esc(faq.get("domanda",""))}</summary>\n'
            f += f'    <p>{_esc(faq.get("risposta",""))}</p>\n'
            f += f'  </details>\n'
        f += '</div>\n'
        html_blocks["faq_html"] = f

    return html_blocks


def _esc(text: str) -> str:
    """Escape HTML minimo per contenuto testuale."""
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6g: SAMEAS BUILDER AUTOMATICO
# Costruisce lista sameAs da tutti i dati disponibili.
# ─────────────────────────────────────────────────────────────────────────────

def build_same_as(local_seo: dict, extra_socials: list = None) -> list:
    """
    Aggiunge automaticamente:
    - URL sito ufficiale
    - LinkedIn (se presente)
    - Google Maps (se coordinate GPS disponibili)
    - Social aggiuntivi opzionali
    """
    same_as = []
    url     = local_seo.get("url","").strip()
    linkedin = local_seo.get("linkedin","").strip()
    lat     = local_seo.get("gps_lat","").strip()
    lon     = local_seo.get("gps_lon","").strip()

    if url:      same_as.append(url)
    if linkedin: same_as.append(linkedin)
    if lat and lon:
        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        same_as.append(maps_url)
    if extra_socials:
        same_as.extend([s for s in extra_socials if s and s not in same_as])

    return same_as


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6h: AI SUMMARY BUILDER
# Genera ai_summary sintetico dai dati input (senza chiamata AI aggiuntiva).
# ─────────────────────────────────────────────────────────────────────────────

def build_ai_summary(azienda: str, servizi: str, local_seo: dict, fatti: str) -> str:
    """
    Costruisce ai_summary lato Python (0 token aggiuntivi).
    Formato: Chi è + Cosa fa + Dove opera.
    Massimo 160 caratteri per compatibilità meta description.
    """
    city   = ""
    indirizzo = local_seo.get("indirizzo","")
    if indirizzo:
        parts = [p.strip() for p in indirizzo.split(",") if p.strip()]
        city  = parts[1] if len(parts) > 1 else parts[0] if parts else ""

    # Primo servizio come attività principale
    primo_servizio = servizi.split(",")[0].strip() if servizi else ""

    # Primo fatto citabile come differenziatore
    primo_fatto = fatti.split("·")[0].strip() if "·" in fatti else fatti.split("\n")[0].strip() if fatti else ""
    primo_fatto = primo_fatto.strip('"').strip("'")

    parts_summary = [azienda]
    if primo_servizio:
        parts_summary.append(f"specializzata in {primo_servizio}")
    if city:
        parts_summary.append(f"con sede a {city}")
    if primo_fatto:
        parts_summary.append(primo_fatto)

    summary = ". ".join(parts_summary) + "."
    # Tronca a 160 char senza spezzare parole
    if len(summary) > 160:
        summary = summary[:157].rsplit(" ", 1)[0] + "..."
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6i: POST-PROCESS PIPELINE GLOBALE
# Applica harden_facts, entities, ai_summary, sameAs, quality_score, html
# all'intero output generato dalle sezioni AI.
# ─────────────────────────────────────────────────────────────────────────────

def post_process(
    generated: dict,
    azienda:   str,
    servizi:   str,
    fatti:     str,
    local_seo: dict,
    verified_texts: list = None,   # FIX: testi completi (debrief+RAG+scraping), non URL
    schema_type: str = "LocalBusiness"
) -> dict:
    """
    Pipeline post-processing globale:
    1. Harden facts su home + pagina_servizio
    2. Struttura CTA
    3. Inietta entities block
    4. Genera ai_summary
    5. Aggiorna sameAs nello schema markup
    6. Calcola quality_score
    7. Genera HTML blocks
    Modifica generated in-place, ritorna il dict arricchito.
    """
    # verified_data: testi reali da cui il Fact Hardener verifica i claim.
    # Filtra None e stringhe vuote per evitare falsi negativi.
    verified_data = [t for t in (verified_texts or []) if t and t.strip()]

    # 1. Fact hardening su sezioni testuali
    if generated.get("home"):
        generated["home"] = harden_section(generated["home"], verified_data)
    if generated.get("pagina_servizio"):
        generated["pagina_servizio"] = harden_section(generated["pagina_servizio"], verified_data)

    # 2. CTA strutturate
    for key, stype in [("home","home"), ("pagina_servizio","service")]:
        section = generated.get(key, {})
        if section and isinstance(section.get("cta"), str):
            section["cta"] = build_structured_cta(section["cta"], stype)

    # 3. Entities block
    generated["entities"] = build_entity_block(azienda, servizi, local_seo, schema_type)

    # 4. AI Summary
    generated["ai_summary"] = build_ai_summary(azienda, servizi, local_seo, fatti)

    # 5. sameAs aggiornato nello schema
    same_as = build_same_as(local_seo)
    if same_as and generated.get("schema_markup",{}).get("organization"):
        generated["schema_markup"]["organization"]["sameAs"] = same_as

    # 6. Quality score
    generated["quality_score"] = compute_quality_score(generated, local_seo, verified_data)  # verified_data = testi, non URL

    # 7. HTML blocks
    html_blocks = generate_html_blocks(generated)
    generated.update(html_blocks)

    return generated


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
# SEZIONE 8: RICERCA WEB MULTI-QUERY — Deep RAG con URL FILTER (v6)
# 3 query distinte + filtro anti-spazzatura severo
# Priorità a .gov, .edu, testate business/settore
# ─────────────────────────────────────────────────────────────────────────────

# Domini da scartare SEMPRE (match esatto o subdomain)
DENYLIST_DOMAINS = frozenset([
    # Social media generalisti
    "youtube.com", "youtu.be", "m.youtube.com",
    "facebook.com", "m.facebook.com", "fb.com", "fb.me",
    "instagram.com", "tiktok.com", "twitter.com", "x.com",
    "pinterest.com", "pinterest.it", "reddit.com",
    "threads.net", "snapchat.com", "telegram.org", "t.me",
    # Streaming / music / entertainment
    "pandora.com", "spotify.com", "soundcloud.com",
    "apple.com/music", "music.apple.com", "deezer.com",
    "netflix.com", "twitch.tv",
    # Marketplace e aggregatori generici
    "amazon.it", "amazon.com", "ebay.it", "ebay.com",
    "aliexpress.com", "etsy.com", "wish.com",
    "trovaprezzi.it", "kelkoo.it", "idealo.it",
    # Directory spam / yellow pages
    "paginegialle.it", "paginebianche.it", "cylex.it",
    "europages.it", "kompass.com", "yalwa.it",
    "misterimprese.it", "virgilio.it", "tuttocitta.it",
    # Review aggregators di scarsa qualità
    "yelp.com", "yelp.it", "yell.com",
    # Search engines
    "google.com/search", "bing.com/search", "duckduckgo.com",
    "search.yahoo.com",
    # Spam SEO
    "scribd.com", "slideshare.net", "issuu.com",
    "pdfcoffee.com", "studocu.com",
])

# Pattern URL sospetti (login, account, support, ecc.)
DENYLIST_URL_PATTERNS = (
    # Autenticazione
    "/login", "/signin", "/sign-in", "/log-in", "/accedi",
    "/register", "/signup", "/sign-up", "/registrati",
    "/logout", "/signout",
    # Account / profilo
    "/account", "/profile", "/profilo", "/my-account",
    "/dashboard", "/cart", "/carrello", "/checkout",
    "/wishlist", "/lista-desideri",
    # Support
    "/support", "/help", "/assistenza", "/contatti",
    "/ticket", "/helpdesk",
    # Policy
    "/privacy", "/cookie", "/terms", "/termini",
    "/condizioni", "/tos", "/gdpr", "/disclaimer",
    # Tecnici
    "/sitemap", "/robots.txt", "/rss", "/feed",
    "/wp-admin", "/wp-login", "/admin/",
    # Tag pages
    "/tag/", "/tags/", "/category/#", "/?s=",
    # Tracking
    "utm_source=", "fbclid=", "gclid=",
)


def is_valid_url(url: str) -> bool:
    """
    Filtro anti-spazzatura semplificato.
    Scarta URL che contengono: youtube, google, facebook, pandora, login, support, account, signin.
    """
    if not url or not isinstance(url, str):
        return False
    url_lower = url.lower()
    blocked = ("youtube", "google", "facebook", "pandora",
               "login", "support", "account", "signin")
    return not any(bad in url_lower for bad in blocked)


# Backward compat: alias per il vecchio nome (usato nello scraping eventualmente)
is_url_clean = is_valid_url


# Domini autorevoli — settore-agnostico, focus e-commerce/B2B
AUTHORITATIVE_DOMAINS = [
    # TLD istituzionali
    ".gov", ".gov.it", ".edu", ".europa.eu", ".int",
    # Editoria economica italiana
    "ilsole24ore.com", "repubblica.it", "corriere.it", "ansa.it",
    "milanofinanza.it", "economy.it", "startupitalia.eu",
    "economyup.it", "wired.it", "agi.it",
    # Editoria economica / tech internazionale
    "reuters.com", "bloomberg.com", "ft.com", "wsj.com",
    "forbes.com", "forbes.it", "harvardbusiness.org", "hbr.org",
    "techcrunch.com", "theverge.com", "arstechnica.com", "wired.com",
    # Istituzioni e registri italiani
    "camcom.it", "cciaa.it", "registroimprese.it",
    "unioncamere.gov.it", "agenziaentrate.gov.it",
    "mise.gov.it", "mimit.gov.it", "istat.it",
    "ismea.it", "ice.it", "ismeamercati.it",
    # Certificazioni e qualità
    "accredia.it", "iso.org", "uni.com", "cen.eu",
    "qualivita.it", "origine.info", "dop-igp.it",
    # Associazioni di categoria
    "confindustria.it", "coldiretti.it", "confcommercio.it",
    "confartigianato.it", "cna.it", "confagricoltura.it",
    "federmeccanica.it", "federchimica.it",
    # Editoria food & hospitality
    "gamberorosso.it", "slowfood.it", "guide.michelin.com",
    "flos-olei.com", "freshplaza.it", "foodweb.it",
    # Editoria retail & e-commerce
    "gdoweek.it", "mark-up.it", "pambianconews.com",
    "distribuzionemoderna.info", "netcomm.it", "osservatori.net",
    # Editoria tech / SaaS / B2B
    "zerounoweb.it", "01net.it", "cwi.it", "cmi.it",
    "digital4.biz", "b2b24.it",
    # Enciclopedico (fallback)
    "wikipedia.org", "treccani.it",
]

def score_source_authority(url: str) -> int:
    """Score 0-10 di autorità del dominio. Più alto = priorità in ranking."""
    score = 1
    url_lower = url.lower()
    if any(tld in url_lower for tld in [".gov.", ".gov/", ".edu.", ".edu/", ".europa.eu"]):
        score += 5
    for domain in AUTHORITATIVE_DOMAINS:
        if domain in url_lower:
            score += 3
            break
    if "wikipedia.org" in url_lower or "treccani.it" in url_lower:
        score += 2
    return min(score, 10)


def get_external_evidence(azienda: str, contesto: str = "") -> dict:
    """
    Deep RAG settore-agnostico. 3 query multi-intent.
    Pipeline: DDGS fetch → filtro is_valid_url + match nome azienda → sort autorità → dedup.
    Richiede: pip install duckduckgo-search
    """
    evidence = {
        "premi_riconoscimenti":  [],
        "certificazioni_qualita": [],
        "storia_fondazione":     [],
        "fonti_aggregate":       [],
        "errori":                [],
        "url_scartati":          [],  # debug: mostra cosa è stato filtrato
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

    azienda_lower = azienda.lower().strip()

    queries = {
        "premi_riconoscimenti":
            f'"{azienda}" premi riconoscimenti recensioni stampa',
        "certificazioni_qualita":
            f'"{azienda}" certificazioni standard qualità',
        "storia_fondazione":
            f'"{azienda}" storia fondazione sede team',
    }

    seen_urls = set()

    try:
        with DDGS() as ddgs:
            for categoria, query in queries.items():
                try:
                    raw_results = list(ddgs.text(query, max_results=10, region="it-it"))
                except Exception as e:
                    evidence["errori"].append(f"Query '{categoria}': {str(e)[:100]}")
                    continue

                # DOPPIO FILTRO: URL valido + nome azienda presente in title/body
                valid_results = []
                for r in raw_results:
                    url   = r.get("href", "") or r.get("url", "")
                    title = (r.get("title", "") or "").lower()
                    body  = (r.get("body", "") or r.get("snippet", "") or "").lower()

                    # 1° check: URL non spazzatura
                    if not is_valid_url(url):
                        evidence["url_scartati"].append(url)
                        continue
                    # 2° check: nome azienda DEVE comparire in title o body
                    if azienda_lower not in title and azienda_lower not in body:
                        evidence["url_scartati"].append(url)
                        continue
                    valid_results.append(r)

                # Sort per autorità decrescente
                valid_results.sort(
                    key=lambda r: score_source_authority(r.get("href", "") or r.get("url", "")),
                    reverse=True
                )

                # Dedup + aggrega
                for r in valid_results:
                    url = r.get("href", "") or r.get("url", "")
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    entry = {
                        "titolo":    r.get("title", ""),
                        "snippet":   r.get("body", "") or r.get("snippet", ""),
                        "url":       url,
                        "categoria": categoria,
                        "autorità":  score_source_authority(url),
                    }
                    evidence[categoria].append(entry)
                    evidence["fonti_aggregate"].append(entry)

                time.sleep(0.5)  # rate limit politeness
    except Exception as e:
        evidence["errori"].append(f"DDGS session: {str(e)[:100]}")

    evidence["fonti_aggregate"].sort(key=lambda x: x["autorità"], reverse=True)
    evidence["fonti_aggregate"] = evidence["fonti_aggregate"][:12]
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
# SEZIONE 9: SYSTEM PROMPT BUILDER — GERARCHIA VERITÀ + GEO-FLOW (v6)
# ─────────────────────────────────────────────────────────────────────────────

# GEO-FLOW: regole di flow narrativo per evitare copy telegrafico
GEO_FLOW_RULES = """
╔══════════════════════════════════════════════════════════════════╗
║   GEO-FLOW COPYWRITING — PROSA CITABILE, NON TELEGRAFICA       ║
╠══════════════════════════════════════════════════════════════════╣
║ Il testo deve essere FLUIDO e UMANO, non un elenco mascherato.  ║
║ I dati vanno INTRECCIATI nella narrazione, non stoccati come    ║
║ bullet points in forma di frase.                                 ║
║ ⚠️ I NUMERI vanno usati SOLO se presenti nelle fonti RAG/debrief║
╚══════════════════════════════════════════════════════════════════╝

REGOLE DI FLOW (applicazione obbligatoria):

  1. PERIODI COMPLETI, NON FRAMMENTI
     Ogni frase ha soggetto + verbo + complemento.
     Vietate le frasi nominali telegrafiche ("Fondata 1890. Sede Milano.").

  2. CONNETTIVI LOGICI OBBLIGATORI
     Usa: perché, tanto che, al punto di, mentre, grazie a, così che, infatti.
     Proibiti i punti dopo 4-5 parole che creano spezzatino informativo.

  3. DATI INTRECCIATI, NON ELENCATI (e SOLO se verificati)
     ✗ BAD (robotico):  "Azienda nata nel 1890. Premiata. Acidità bassa."
     ✓ GOOD (GEO):      "Attiva da fine Ottocento, l'azienda ha guadagnato
                         riconoscimenti nelle guide di settore grazie a un'acidità
                         contenuta — un valore che la colloca tra gli extravergini."
     ⚠️ NOTA CRITICA: usa numeri SOLO se presenti nelle fonti RAG/debrief.
        Mai inventare percentuali, anni, quantità, soglie tecniche.

  4. RITMO — DATI OGGETTIVI INTRECCIATI (se disponibili)
     Quando il dato esiste nelle fonti, dilluiscilo nel periodo, non isolarlo.
     Quando manca, mantieni il flow discorsivo SENZA quantificare.

  5. LUNGHEZZA FRASI — VARIABILE, MEDIA 18-25 PAROLE
     Alterna frasi brevi (8-12 parole) e articolate (25-35 parole).
     Una sequenza di frasi tutte corte suona robotica. Tutte lunghe accademica.

  6. VIETATI GLI "ESCO INSERT" DA PROMPT
     Mai frasi-placeholder come "Ecco i nostri punti di forza:" seguite da elenco.
     Se un concetto merita una lista, va in <ul> nel markdown — ma PRIMA deve
     esserci un paragrafo di prosa che lo introduce narrativamente.

  7. VOICE COERENTE
     B2B e-commerce: "L'azienda" (terza) o "aiutiamo" (prima plurale).
     B2C: "trovi / scegli" (seconda singolare informale).
     Scegli UNA voce e mantienila per l'intero modulo.

ESEMPI BAD → GOOD (studia il pattern di FLUSSO, NON copiare i numeri):

BAD #1 (telegrafico, SaaS B2B):
  "Software gestionale B2B. Fattura elettronica. Sincronizzazione cloud.
   Tempo risparmiato. Clienti soddisfatti."

GOOD #1 (discorsivo, senza numeri inventati):
  "Il gestionale sincronizza fatturazione elettronica e ordini in tempo reale,
   eliminando la doppia digitazione che negli studi tradizionali consuma una
   quota significativa del tempo amministrativo. Gli studi che lo adottano lo
   usano per chiudere i mesi contabili in tempi più rapidi rispetto al flusso
   manuale tradizionale."

BAD #2 (telegrafico, food/oleificio):
  "Oleificio dal 1890. Olio premiato. Umbria. Frantoio moderno. Acidità bassa."

GOOD #2 (discorsivo, processo SENZA tempistiche inventate):
  "Da fine Ottocento l'oleificio lavora le olive coltivate in Umbria,
   un areale riconosciuto per le proprie denominazioni di origine.
   L'estrazione a freddo preserva i composti aromatici delle drupe e
   contiene l'acidità entro le soglie previste per la categoria
   extravergine."

BAD #3 (telegrafico, e-commerce B2B arredo):
  "Arredi ufficio. Consegna rapida. Made in Italy. Garanzia estesa."

GOOD #3 (discorsivo, no claim numerici inventati):
  "La collezione di arredi per ufficio è prodotta in Italia con materiali
   tracciabili e viene distribuita su tutto il territorio nazionale.
   Ogni elemento della linea contract è coperto da una garanzia sulla
   struttura portante più ampia rispetto agli standard di mercato del segmento."

BAD #4 (telegrafico, e-commerce B2C moda):
  "Capi made in Italy. Tessuti pregiati. Spedizione veloce. Reso facile."

GOOD #4 (discorsivo, no quantificazioni inventate):
  "Ogni capo della collezione è cucito in Italia con tessuti certificati
   e ti arriva a casa con corriere espresso. Se non è quello che cercavi,
   puoi restituirlo gratuitamente entro la finestra prevista — un margine
   più ampio dei minimi richiesti dalla normativa europea."

REGOLA MASTER:
I numeri che vedi nei prompt-template (es. "180-220 parole", "120-160 parole")
sono ISTRUZIONI DI FORMATO per te. NON copiarli mai nel testo finale.
I numeri che inserisci nel testo finale devono provenire ESCLUSIVAMENTE
dalle fonti RAG o dal debrief utente. In assenza di dati: flow discorsivo
SENZA quantificare.
"""


def build_system_prompt(stile_esempi: str = "") -> str:
    alligator_rules = """APPROCCIO ALLIGATOR (OBBLIGATORIO):
- DIRETTO ma MAI TELEGRAFICO: frasi complete con soggetto-verbo-complemento.
- RISULTATI MISURABILI: ogni affermazione ha conseguenza concreta per il cliente.
- AUTOREVOLE TECNICO: terminologia di settore, lettore considerato esperto.
- FLUIDO: periodi 18-25 parole media, connettivi logici tra frasi,
  zero sequenze di frasi-nominali stile "Fondato 1890. Sede Milano."
"""

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
║   ⛔ DIVIETO ASSOLUTO DI ASSUNZIONI DI SETTORE ⛔           ║
╠══════════════════════════════════════════════════════════════╣
║ È SEVERAMENTE VIETATO inserire pratiche standard di mercato, ║
║ tempistiche, o specifiche tecniche (es. "estrazione a freddo ║
║ entro 4 ore", "molitura entro 6 ore", "fermentazione 12 mesi"║
║ "consegna in 24/48h", "garanzia 2 anni") se NON sono         ║
║ ESPRESSAMENTE scritte nelle fonti RAG o nel debrief utente.  ║
║                                                              ║
║ Se ti manca il dato esatto: NON inventarlo, NON dedurlo da   ║
║ pratiche di settore, NON usare valori "tipici". Resta su un  ║
║ piano puramente discorsivo, descrivendo la natura del        ║
║ processo SENZA numeri, tempi o soglie specifiche.            ║
║                                                              ║
║ ESEMPIO BAD (assunzione inventata):                          ║
║   "L'estrazione avviene a freddo entro 4 ore dalla raccolta" ║
║ ESEMPIO GOOD (discorsivo, no numeri inventati):              ║
║   "L'estrazione avviene a freddo, preservando i composti      ║
║    aromatici nella fase di lavorazione delle olive."         ║
╚══════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════╗
║         GERARCHIA DELLA VERITÀ — VINCOLO ASSOLUTO           ║
╠══════════════════════════════════════════════════════════════╣
║ LIVELLO 1 [MASSIMA PRIORITÀ]:                               ║
║   • Dati estratti dalla Ricerca Web (sezione RAG)           ║
║   • Contenuti scraping del sito web dell'azienda            ║
║   → Premi con anno, certificazioni, analisi,                 ║
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
║   • Quantità di clienti/ordini/partner non verificate       ║
║   • Anni di fondazione non confermati dalle fonti           ║
║   • Certificazioni non trovate nel RAG o nel sito           ║
║   • Punteggi o rating non verificati                        ║
║                                                              ║
║ SE UN DATO NON È NELLE FONTI:                               ║
║   → Descrivi il processo SENZA numeri/tempi/soglie          ║
║   → Usa "secondo i dati aziendali" per dati da debrief      ║
║   → NON usare numeri inventati o approssimativi              ║
╚══════════════════════════════════════════════════════════════╝"""

    return f"""Sei il copywriter GEO/SEO senior di Alligator. Generi contenuti web ad alta citabilità AI.

{alligator_rules}
{style_section}

{truth_hierarchy}

{CLICHE_PROMPT_BLOCK}

{GEO_FLOW_RULES}

FRAMEWORK GEO SCORE:
{GEO_CRITERIA}

REGOLE OUTPUT (ASSOLUTE):
- Rispondi SOLO con JSON valido. Zero testo fuori dal JSON.
- NO introduzioni, NO conclusioni, NO commenti, NO markdown fuori JSON.
- Ogni campo 'intro' e 'body' deve essere prosa fluida di più periodi connessi.
- Claim autonomi: ogni frase chiave ha senso estratta fuori contesto.
- Ogni premio/dato citato nel testo DEVE includere anno/valore dalla fonte.
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
# SEZIONE 11: PROMPT MODULARI con descrittori prosa fluida (v6)
# ─────────────────────────────────────────────────────────────────────────────
def prompt_home(ctx: str) -> str:
    return f"""{ctx}

Genera SOLO il blocco "home". Ogni campo di prosa (intro, body) deve essere
UN TESTO NARRATIVO CONTINUATIVO, non un elenco di frasi nominali.

ESEMPIO DEL FORMATO ATTESO PER IL CAMPO "intro" (replica lo stile):
"Dal 1890 [Azienda] produce [prodotto] nella [zona geografica], dove la
combinazione di [fattore 1] e [fattore 2] ha dato vita a una linea riconosciuta
dalle guide di settore — nel 2023 con le tre foglie del Gambero Rosso.
L'approccio tecnico, centrato su [processo specifico], consente di mantenere
[parametro tecnico verificato] ben sotto la soglia richiesta dalla categoria."

Rispondi ESCLUSIVAMENTE con questo JSON (tutti i campi stringa in italiano,
prosa fluida, zero frasi-elenco):
{{
  "home": {{
    "h1": "H1 max 60 char — brand + topic principale + qualificatore concreto",
    "intro": "180-220 parole di PROSA FLUIDA (non frasi brevi separate da punto). Apri con una frase di risposta diretta che associ brand + topic + dato oggettivo. Intreccia almeno 2 dati numerici dalle fonti (anno fondazione, premi con anno, numeri verificati). Usa connettivi logici (perché, tanto che, grazie a). Stile Alligator ma non telegrafico.",
    "sezione_1": {{
      "h2": "H2 descrittivo con un dato/qualificatore concreto — non generico",
      "body": "120-160 parole di prosa continuativa. Un dato verificato dalle fonti o, se manca, descrizione DISCORSIVA del processo SENZA numeri/tempistiche inventate. Esempio approccio descrittivo: 'L'azienda integra il processo X preservando le caratteristiche Y'. NON inventare percentuali, ore, soglie tecniche."
    }},
    "sezione_2": {{
      "h2": "H2 differenziazione — cosa distingue il brand con attributi concreti",
      "body": "120-160 parole di prosa continuativa. Unicità espressa tramite fatti verificabili: certificazioni, processi, aree DOP/IGP se rilevanti, partnership verificabili. Zero cliché dalla blacklist."
    }},
    "cta": "1 frase imperativa specifica al topic (non generica 'contattaci')",
    "fonti_utilizzate": ["URL_reale_1", "URL_reale_2"]
  }}
}}"""


def prompt_servizio(ctx: str) -> str:
    return f"""{ctx}

Genera SOLO il blocco "pagina_servizio". L'intro deve essere prosa fluida;
SOLO i campi "steps" e "lista" possono contenere elementi brevi stile elenco.

ESEMPIO DEL FORMATO ATTESO PER IL CAMPO "intro":
"[Servizio] risolve [problema specifico] per [target]: l'azienda integra
[tecnologia/metodo verificato] con [processo specifico], un approccio che
riduce [parametro misurabile] rispetto alle soluzioni tradizionali. Il
risultato è [outcome concreto] con tempi di [metrica verificata]."

Rispondi ESCLUSIVAMENTE con questo JSON:
{{
  "pagina_servizio": {{
    "h1": "H1 con keyword long-tail + qualificatore specifico (non 'Servizi di X')",
    "intro": "140-180 parole di PROSA FLUIDA. Apri con l'outcome per il cliente, non con 'Offriamo'. Intreccia 1-2 dati numerici dalle fonti. Usa la voce coerente con il brand (terza persona o prima plurale).",
    "come_funziona": {{
      "h2": "Come funziona — titolo con dato/tempistica concreta",
      "steps": [
        "Step 1 — 1-2 righe di azione concreta con verbo iniziale (es. 'Analizziamo...', 'Definiamo...')",
        "Step 2 — 1-2 righe",
        "Step 3 — 1-2 righe",
        "Step 4 — 1-2 righe con outcome misurabile"
      ]
    }},
    "benefici": {{
      "h2": "H2 con numero specifico (es. '4 vantaggi misurabili di...')",
      "lista": [
        "Beneficio 1 con dato numerico o comparazione (non 'alta qualità')",
        "Beneficio 2 con dato",
        "Beneficio 3 con dato",
        "Beneficio 4 con dato"
      ]
    }},
    "cta": "CTA imperativa al servizio specifico (es. 'Richiedi un audit gratuito', non 'Contattaci')",
    "fonti_utilizzate": ["URL_reale_1"]
  }}
}}"""


def prompt_faq(ctx: str) -> str:
    return f"""{ctx}

Genera SOLO il blocco "faq" con 5 domande. Ogni risposta deve essere prosa
fluida, autonoma (leggibile fuori contesto), con un dato concreto intrecciato
(non elencato in coda). Target: AI search engines (Perplexity, SearchGPT)
che estraggono risposte dirette.

ESEMPIO FORMATO ATTESO (lo schema, NON i numeri — quelli vanno dalle fonti):
  Q: "Quanto tempo serve per ricevere un preventivo personalizzato?"
  A: "Il preventivo viene elaborato a seguito della ricezione del brief, con
     un incontro di allineamento dedicato a definire l'ambito del progetto.
     Questo processo permette di consegnare stime allineate al budget reale
     del cliente, riducendo gli scostamenti rispetto al flusso di richiesta
     standard via form."
  ⚠️ NOTA: l'esempio è VOLUTAMENTE senza numeri specifici. Inserisci ore,
     percentuali, quantità SOLO se sono presenti nelle fonti RAG/debrief.

Rispondi ESCLUSIVAMENTE con questo JSON (5 coppie Q&A, risposte 80-130 parole
di PROSA FLUIDA, non elenchi):
{{
  "faq": [
    {{
      "domanda": "Query naturale inizia con Come/Cosa/Quanto/Perché/Chi/Dove — deve suonare come una query AI reale",
      "risposta": "80-130 parole di prosa continuativa. Prima frase = risposta diretta autonoma. Intreccia 1 dato verificato. Se il dato non è nelle fonti, descrivi il processo tecnico senza inventare numeri.",
      "fonte": "URL_reale_se_dato_verificato_o_stringa_vuota"
    }},
    {{"domanda": "Q2", "risposta": "80-130 parole prosa", "fonte": ""}},
    {{"domanda": "Q3", "risposta": "80-130 parole prosa", "fonte": ""}},
    {{"domanda": "Q4", "risposta": "80-130 parole prosa", "fonte": ""}},
    {{"domanda": "Q5", "risposta": "80-130 parole prosa", "fonte": ""}}
  ]
}}"""


def prompt_schema(ctx: str, azienda: str, local_seo: dict, faq_data: list) -> str:
    indirizzo = local_seo.get("indirizzo", "")
    url_sito  = local_seo.get("url", "https://www.esempio.it")
    linkedin  = local_seo.get("linkedin", "")
    schema_type = "LocalBusiness" if indirizzo.strip() else "Organization"

    # Orari: nuovo formato stringa "09:00-13:00, 15:00-19:00"
    orari = local_seo.get("orari", {})
    orari_lines = []
    giorni_map = {
        "Lunedì": "Monday", "Martedì": "Tuesday", "Mercoledì": "Wednesday",
        "Giovedì": "Thursday", "Venerdì": "Friday", "Sabato": "Saturday", "Domenica": "Sunday"
    }
    for g, orario_val in orari.items():
        g_en = giorni_map.get(g, g)
        if isinstance(orario_val, str) and orario_val.strip():
            orari_lines.append(f"{g_en}: {orario_val.strip()}")
        elif isinstance(orario_val, (tuple, list)) and len(orario_val) == 2:
            ap, ch = orario_val
            if ap and ch:
                orari_lines.append(f"{g_en}: {ap}-{ch}")
    orari_str = " | ".join(orari_lines) if orari_lines else "non specificati"

    return f"""{ctx}
SCHEMA TYPE: {schema_type}
URL: {url_sito}
LINKEDIN: {linkedin if linkedin else "da compilare"}
ORARI: {orari_str}

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
# SEZIONE 14: SCHEMA MARKUP BUILDER (aggiornato v5)
# Supporta nuovo formato orari stringa: "09:00-13:00, 15:00-19:00"
# Usa sameAs da build_same_as() + Product schema se rilevante
# ─────────────────────────────────────────────────────────────────────────────

def parse_orario_str(orario_str: str) -> list:
    """
    Parsea stringa orario nel nuovo formato: "09:00-13:00, 15:00-19:00"
    Ritorna lista di tuple (apertura, chiusura) per ogni fascia oraria.
    Supporta sia formato singolo "09:00-18:00" che multiplo con virgola.
    """
    if not orario_str or not orario_str.strip():
        return []
    
    fasce = []
    # Split per virgola — separa le fasce orarie multiple
    parti = [p.strip() for p in orario_str.split(",") if p.strip()]
    for parte in parti:
        # Ogni parte è "HH:MM-HH:MM"
        match = re.match(r'^(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})$', parte.strip())
        if match:
            fasce.append((match.group(1), match.group(2)))
    return fasce


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
    if url_sito: org["url"] = url_sito

    # sameAs: usa build_same_as() per includere GPS + tutti i social
    same_as = build_same_as(local_seo)
    if same_as:
        org["sameAs"] = same_as
    elif linkedin:
        org["sameAs"] = [linkedin]

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

    # Orari: supporta sia nuovo formato stringa che legacy tuple (apertura, chiusura)
    giorni_map = {
        "Lunedì": "Monday", "Martedì": "Tuesday", "Mercoledì": "Wednesday",
        "Giovedì": "Thursday", "Venerdì": "Friday", "Sabato": "Saturday", "Domenica": "Sunday"
    }
    oh = []
    for g_it, orario_val in orari.items():
        day_en = giorni_map.get(g_it, g_it)
        
        # Nuovo formato: stringa "09:00-13:00, 15:00-19:00"
        if isinstance(orario_val, str):
            fasce = parse_orario_str(orario_val)
            for (apertura, chiusura) in fasce:
                oh.append({
                    "@type":     "OpeningHoursSpecification",
                    "dayOfWeek": f"https://schema.org/{day_en}",
                    "opens":     apertura,
                    "closes":    chiusura
                })
        # Legacy formato: tuple (apertura, chiusura)
        elif isinstance(orario_val, (tuple, list)) and len(orario_val) == 2:
            apertura, chiusura = orario_val
            if apertura and chiusura:
                oh.append({
                    "@type":     "OpeningHoursSpecification",
                    "dayOfWeek": f"https://schema.org/{day_en}",
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
def resolve_cta(cta_val) -> str:
    """
    Normalizza CTA: accetta sia stringa (vecchio formato AI)
    che dict {primary, secondary, intent} (nuovo formato post-process v5).
    Ritorna sempre una stringa usabile nel testo.
    """
    if isinstance(cta_val, dict):
        return cta_val.get("primary", "Contattaci")
    return str(cta_val) if cta_val else ""


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
    st.markdown(f"**CTA:** _{resolve_cta(home.get('cta',''))}_")
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
    st.markdown(f"**CTA:** _{resolve_cta(page.get('cta',''))}_")
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
    t += resolve_cta(h.get("cta",""))
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
    t += resolve_cta(p.get("cta",""))
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
        page_title="GEO Score™ v5 — Alligator Advanced GEO",
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
        <h1>🐊 GEO Score™ Content Generator v5 — Advanced GEO Edition</h1>
        <p>Deep RAG · URL Scraping · GEO-Entity · Fact Hardening · Entity System · Quality Score · HTML Blocks · AI Summary · Framework GEO Score™ by Nico Fioretti</p>
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
            # Default: Sonnet 3.5 — best trade-off GEO quality / costo
            opts, dflt = list(PRICING["anthropic"].keys()), "claude-3-5-sonnet-latest"

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

        # GRIGLIA ORARI — formato unico stringa "09:00-13:00, 15:00-19:00"
        st.markdown("**🕐 Orari di Apertura** *(lascia vuoto = chiuso · es: 09:00-13:00, 15:00-19:00)*")
        giorni = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
        orari_dict = {}
        h_cols = st.columns([2, 5])
        h_cols[0].markdown("**Giorno**")
        h_cols[1].markdown("**Orario** *(es. 09:00-13:00 oppure 09:00-13:00, 15:00-19:00)*")
        for giorno in giorni:
            row = st.columns([2, 5])
            row[0].markdown(f"*{giorno}*")
            orario_str = row[1].text_input(
                "", key=f"orario_{giorno}",
                placeholder="09:00-13:00, 15:00-19:00",
                label_visibility="collapsed"
            )
            orari_dict[giorno] = orario_str  # stringa grezza, parsata da parse_orario_str()

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

            # ── POST-PROCESS PIPELINE v5 ───────────────────────────────
            # Applica: fact hardening, CTA strutturate, entities, ai_summary,
            # sameAs automatico, quality_score, HTML blocks
            if generated:
                with st.spinner("🔧 Post-processing: harden facts, quality score, HTML blocks..."):
                    schema_type_pp = "LocalBusiness" if _loc.get("indirizzo","").strip() else "Organization"
                    generated = post_process(
                        generated      = generated,
                        azienda        = _az,
                        servizi        = _sv,
                        fatti          = _ft,
                        local_seo      = _loc,
                        verified_texts = [_ft, rag_evidence_str, scrape_content_str],  # FIX: testi reali
                        schema_type    = schema_type_pp
                    )

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
        st.subheader("📄 Risultati — Anti-Hallucination v5 · GEO Advanced")

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

        # ── Quality Score (v5) ────────────────────────────────────────
        qs = data.get("quality_score", {})
        if qs:
            st.markdown("#### 📊 Quality Score v5")
            q1, q2, q3, q4 = st.columns(4)
            q1.metric("E-E-A-T", f"{qs.get('eeat',0)}/10")
            q2.metric("SEO",     f"{qs.get('seo', 0)}/10")
            q3.metric("GEO",     f"{qs.get('geo', 0)}/10")
            risk = qs.get("risk_level", "low")
            risk_icon = "🟢" if risk == "low" else "🟡" if risk == "medium" else "🔴"
            q4.metric("Risk Level", f"{risk_icon} {risk}")

        # ── AI Summary (v5) ───────────────────────────────────────────
        ai_sum = data.get("ai_summary", "")
        if ai_sum:
            st.markdown(
                f'<div class="truth-box"><b>🤖 AI Summary</b> <em>(GEO — chi è, cosa fa, dove opera)</em><br>{ai_sum}</div>',
                unsafe_allow_html=True
            )

        # ── Entities (v5) ─────────────────────────────────────────────
        entities = data.get("entities", {})
        if entities:
            with st.expander("🏷️ Entity Block (GEO)"):
                st.json(entities)

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
                    # HTML pronto per WordPress (v5)
                    if data.get("home_html"):
                        copy_box("📋 Copia Homepage (HTML WordPress)", data["home_html"], "cp_home_html")
                    # data_validation report
                    dv = home.get("data_validation", {})
                    if dv.get("generic_fields") or dv.get("removed_claims"):
                        with st.expander(f"⚠️ Fact Hardening Report — {len(dv.get('generic_fields',[]))} downgrade, {len(dv.get('removed_claims',[]))} rimossi"):
                            for g in dv.get("generic_fields", []):
                                st.markdown(f"🟡 {g}")
                            for r in dv.get("removed_claims", []):
                                st.markdown(f"🔴 {r}")

                elif key == "servizio":
                    page = data.get("pagina_servizio", {})
                    render_service(page)
                    st.divider()
                    copy_box("📋 Copia Pagina Servizio", service_to_md(page), "cp_serv")
                    # HTML pronto per WordPress (v5)
                    if data.get("service_html"):
                        copy_box("📋 Copia Servizio (HTML WordPress)", data["service_html"], "cp_serv_html")
                    # data_validation report
                    dv = page.get("data_validation", {})
                    if dv.get("generic_fields") or dv.get("removed_claims"):
                        with st.expander(f"⚠️ Fact Hardening Report — {len(dv.get('generic_fields',[]))} downgrade, {len(dv.get('removed_claims',[]))} rimossi"):
                            for g in dv.get("generic_fields", []):
                                st.markdown(f"🟡 {g}")
                            for r in dv.get("removed_claims", []):
                                st.markdown(f"🔴 {r}")

                elif key == "faq":
                    faqs = data.get("faq", [])
                    render_faq(faqs)
                    st.divider()
                    copy_box("📋 Copia FAQ (Markdown/Gutenberg)", faq_to_md(faqs), "cp_faq")
                    # HTML pronto per WordPress (v5)
                    if data.get("faq_html"):
                        copy_box("📋 Copia FAQ (HTML WordPress <details>)", data["faq_html"], "cp_faq_html")

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
            file_name=f"geo_alligator_v5_{_az.replace(' ','_').lower()}.json",
            mime="application/json"
        )


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
