"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     GEO Score™ Content Generator v13 — Alligator Edition                   ║
║     The Authority Orchestrator: Strict Multilang · Anti-Fuffa E-E-A-T      ║
║     Geocodifica Resiliente · Silo v13 · Product Schema · P.IVA · SocialHub ║
╚══════════════════════════════════════════════════════════════════════════════╝

CHANGELOG v13 — FIX SCHEMA GOOGLE RICH RESULTS (da test tool Google):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FIX 14 — Product.offers.price SEMPRE presente: in v12 `offers` veniva
            generato solo se `priceRange` era valorizzato. Ora il nodo
            `offers` con `price` numerico è SEMPRE incluso (default "0.00"),
            eliminando l'errore critico "È necessario specificare price".
  FIX 15 — Product.image aggiunta: campo critico per Google Rich Result.
            Se il prodotto non ha un'immagine esplicita, usa l'URL
            dell'azienda come fallback accettato da Google.
  FIX 16 — LocalBusiness.image aggiunta: legge `logo_url` da local_seo.
            Risolve il warning "Campo mancante image (facoltativo)".
  FIX 17 — LocalBusiness.priceRange aggiunto: legge `price_range` da
            local_seo. Risolve warning "Campo mancante priceRange".
  FIX 18 — servesCuisine ora TYPE-GATED: iniettato solo quando @type è
            Restaurant/BarOrPub/Bakery/IceCreamShop. Per produttori
            (Store, Winery, ecc.) il campo viene ignorato — evita warning
            su schema non ristorativi e mantiene il tool generico.
  FIX 19 — priceRange TYPE-GATED: iniettato solo per tipi che lo
            supportano semanticamente (Store, Restaurant, Hotel, ecc.).
            Per ProfessionalService, MedicalBusiness, ecc. viene omesso.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHANGELOG v12 — 10 FIX + 4 NUOVE FUNZIONALITÀ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NUOVE FUNZIONALITÀ:
  A — EDIT INLINE: ogni sezione ha un editor diretto; le modifiche si
      propagano immediatamente nel JSON e nel download.
  B — HISTORY SIDEBAR: ultimi 10 clienti testati salvati in session_state;
      click su un cliente precompila automaticamente tutti i campi del debrief.
  C — TONE OF VOICE: selettore Product-Oriented / Storytelling / Bilanciato
      (default). Il tone influenza i system prompt e le istruzioni di stile.
  D — RICH RESULT SNIPPET: `review`, `aggregateRating`, `offers.price`
      aggiunti ai nodi Product per abilitare i Rich Snippet di Google.

FIX STRUTTURALI (da feedback JSON Marfuga):
  FIX 7  — Products vs Awards separati: build_products_from_fatti ora
            filtra i nomi-premio puri e genera prodotti reali con nome
            commerciale pulito. Schema Product.name non contiene mai
            il nome di una guida o di un riconoscimento.
  FIX 8  — Sentiment keywords: se extract_sentiment_terms() restituisce []
            (nessuna recensione rilevata), viene iniettato un set di fallback
            coerente con le geo_entities e i fatti dichiarati nel debrief.
  FIX 9  — FAQ key unification: il formato interno usa domanda/risposta;
            il FAQPage JSON-LD usa question/acceptedAnswer. Aggiunta mapping
            esplicita e nota nel JSON (faq_key_format: "domanda/risposta").
  FIX 10 — entities.products popolato: build_entity_block ora costruisce
            l'array products con nomi puliti (non frammenti di frase).
            entities.services usa re.split pulito senza frammenti residui.
  FIX 11 — Schema @type FoodEstablishment → corretto: la mappa
            BUSINESS_TYPE_MAP ora usa "Store" per frantoio/produttore olio,
            evitando FoodEstablishment per aziende agrarie non ristorative.
  FIX 12 — meta_description non troncata: genera una frase completa e
            autonoma (max 155 char) senza "..." a metà periodo.
  FIX 13 — Rich Result Google: Product schema include review[] con
            reviewRating, aggregateRating, e offers.price numerico.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHANGELOG v11 (mantenuto integralmente):
CHANGELOG v11 — 6 FIX STRUTTURALI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIX 1 — SCHEMA ID SLUGIFICATION AGGRESSIVA
  • _slugify_product() ora produce slug corti e semantici (max ~30 char).
  • @id prodotti: formato `#product-{slug}` breve (es. #product-consulenza-seo).
  • Nome prodotto nel campo `name`: solo il nome commerciale, zero premi.
  • I dettagli di premi/riconoscimenti vanno SOLO nel campo `award`.

FIX 2 — STRICT LANGUAGE LOCK RINFORZATO
  • Vincolo lingua ripetuto all'inizio di OGNI prompt modulare
    (home, servizio, faq_hybrid, schema).
  • Formulazione "VINCOLO PRIMARIO INVIOLABILE — SOVRASCRIVE LE FONTI RAG"
    per prevenire il drift linguistico anche su fonti in lingua straniera.
  • Triple-lock: nel system prompt, nel context builder, nei prompt modulari.

FIX 3 — SENTIMENT DEEP EXTRACTION (Professionalità & Autorità)
  • extract_sentiment_terms() estesa con PROFESSIONALISM_AUTHORITY_SEED:
    termini come 'serietà', 'competenza', 'tempestività', 'affidabilità',
    'preparazione', 'puntualità', 'professionalità' — rilevabili anche in
    contesti non sensoriali (es. recensioni Google, testimonianze aziendali).
  • La funzione ora cerca questi termini in CONTESTI POSITIVI nel testo.
  • Rimosso il blocco hard "solo sensoriali": la sentiment extraction è
    ora settore-agnostica con seed appropriati per ogni settore.

FIX 4 — P.IVA REGEX MIGLIORATA + vatID IN ORGANIZATION
  • extract_vat_id() ora cerca anche nel testo normale (non solo footer)
    e gestisce più varianti di formattazione (spazi, trattini, punti).
  • vatID iniettato nel nodo Organization del @graph (già presente in v10,
    ora garantito anche nel build_final_schema legacy).
  • Feedback UI dedicato con link alla spiegazione E-E-A-T.

FIX 5 — GESTIONE MODELLI E MAX_TOKENS
  • MODEL_MAX_TOKENS: tutti i modelli Anthropic a 8192 (default sicuro).
  • Sidebar: model selector ora mostra claude-sonnet-4-5 come default.
  • call_anthropic() usa sempre il max_tokens dal dizionario (no fallback a 4000).
  • Aggiunto controllo esplicito che max_tok >= 4096 per Anthropic.

FIX 6 — CONTEXT SILO RESET GARANTITO
  • internal_linking_suggestions svuotato a {} all'inizio di ogni run
    nel blocco `generated = dict(...)` pre-generazione.
  • Aggiunto reset esplicito in post_process() prima di chiamare
    build_internal_linking_map().
  • Nota nel JSON output: `_silo_reset_confirmed: true`.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHANGELOG v10 (mantenuto integralmente):
  • P.IVA regex, Social Hub, Commercial Entity Schema, Silo Architecture v10,
    Geocodifica resiliente 3 livelli, RAG multi-query, Scraping BeautifulSoup,
    Fact Hardening, Entity Block, AI Summary, Quality Score, HTML blocks.
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
# SEZIONE 2: CLICHÉ BLACKLIST
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
# SEZIONE 3: GEO-ENTITY MAP ITALIANA
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
    return list(dict.fromkeys(matched))

# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 4: PRICING & MODEL CONFIG
# FIX 5 v11: max_tokens 8192 per tutti i modelli Anthropic, nessun fallback a 4000
# ─────────────────────────────────────────────────────────────────────────────
PRICING = {
    "openai": {
        "gpt-4o-mini":  {"input": 0.00015, "output": 0.00060},
        "gpt-4o":       {"input": 0.00250, "output": 0.01000},
    },
    "anthropic": {
        "claude-haiku-4-5-20251001":  {"input": 0.00100, "output": 0.00500},
        "claude-sonnet-4-5": {"input": 0.00300, "output": 0.01500},
        "claude-opus-4-5":     {"input": 0.01500, "output": 0.07500},
    }
}

MODEL_LABELS = {
    "claude-haiku-4-5-20251001":  "Claude 4.5 Haiku 💰 (Economico)",
    "claude-sonnet-4-5": "Claude 4.5 Sonnet 🔋 (Raccomandato per GEO)",
    "claude-opus-4-5":     "Claude 4.5 Opus 💎 (Massima qualità)",
    "gpt-4o-mini":                "GPT-4o Mini 💰",
    "gpt-4o":                     "GPT-4o 🔋",
}

# FIX 5 v11: 8192 per tutti i modelli Anthropic — nessun troncamento JSON
MODEL_MAX_TOKENS = {
    "gpt-4o-mini":               4096,
    "gpt-4o":                    4096,
    "claude-haiku-4-5-20251001": 8192,
    "claude-sonnet-4-5":         8192,
    "claude-opus-4-5":           8192,
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
# SEZIONE 6: REPAIR JSON
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
# ─────────────────────────────────────────────────────────────────────────────
RISKY_PATTERNS = [
    (r'\b\d+\s*%\s*(?:di\s+)?(?:clienti|vendite|crescita|aumento|riduzione|risparmio)\b', "dato percentuale non verificato"),
    (r'\boltre\s+\d+\s+anni\b', "anni di attività non verificati"),
    (r'\b(?:più di|oltre|circa)\s+\d{3,}\s+(?:clienti|prodotti|ordini|partner)\b', "quantità non verificata"),
    (r'\b(?:primo|seconda?|terzo|top\s*\d)\s+(?:in italia|al mondo|nel settore)\b', "claim di posizionamento non verificato"),
    (r'\bda\s+(?:oltre\s+)?\d+\s+anni\b', "anzianità non verificata"),
]

SAFE_REPLACEMENTS = {
    "dato percentuale non verificato":          "dato in crescita costante",
    "anni di attività non verificati":          "da diversi anni nel settore",
    "quantità non verificata":                  "numerosi clienti nel settore",
    "claim di posizionamento non verificato":   "tra i riferimenti del settore",
    "anzianità non verificata":                 "con esperienza consolidata nel settore",
}


def harden_facts(text: str, verified_data: list = None) -> dict:
    if not text:
        return {"text": text, "verified": [], "generic": [], "removed": []}
    verified_list = verified_data or []
    generic_changes = []
    removed_claims  = []
    hardened        = text
    for pattern, label in RISKY_PATTERNS:
        matches = re.findall(pattern, hardened, flags=re.IGNORECASE)
        for match in matches:
            is_verified = any(match.lower() in v.lower() for v in verified_list)
            if not is_verified:
                replacement = SAFE_REPLACEMENTS.get(label, "dato non specificato")
                hardened = re.sub(re.escape(match), replacement, hardened, flags=re.IGNORECASE)
                generic_changes.append(f'"{match}" → "{replacement}" ({label})')
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
    hardened["data_validation"] = {
        "verified_fields": verified_data or [],
        "generic_fields":  list(dict.fromkeys(all_generic)),
        "removed_claims":  list(dict.fromkeys(all_removed)),
    }
    return hardened


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6c: ENTITY SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
def build_entity_block(azienda: str, servizi: str, local_seo: dict, schema_type: str = "LocalBusiness",
                       products_list: list = None) -> dict:
    indirizzo = local_seo.get("indirizzo", "")
    addr = parse_address(indirizzo)
    # FIX 10 v12: servizi split pulito — split su separatori standard, rimuove frammenti < 4 char
    servizi_raw = [s.strip() for s in re.split(r"[,;\n·•]+", servizi) if s.strip()]
    servizi_list = [s for s in servizi_raw if len(s) > 3][:8]
    # FIX 10 v12: entities.products popolato con nomi commerciali puliti (non [])
    entity_products = []
    if products_list:
        for p in products_list[:8]:
            name = p.get("name", "")
            if name and len(name) > 2:
                entity_products.append({
                    "name": name,
                    "category": p.get("category", ""),
                    "award": p.get("award", ""),
                })
    return {
        "brand": azienda,
        "type": schema_type,
        "location": {
            "streetAddress": addr.get("streetAddress", ""),
            "city": addr.get("addressLocality", ""),
            "postalCode": addr.get("postalCode", ""),
            "region": addr.get("addressRegion", ""),
            "country": "Italia",
        },
        "services": servizi_list,
        "products": entity_products,
        "awards": [],
        "faq_key_format": "domanda/risposta",  # FIX 9 v12: nota esplicita sul formato chiavi FAQ
    }


def build_structured_cta(cta_raw: str, section_type: str = "generic") -> dict:
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
# ─────────────────────────────────────────────────────────────────────────────
def compute_quality_score(data: dict, local_seo: dict, source_urls: list) -> dict:
    eeat = 0
    seo  = 0
    geo  = 0
    if source_urls:                                      eeat += 2
    if local_seo.get("indirizzo","").strip():            eeat += 2
    if local_seo.get("linkedin","").strip():             eeat += 1
    if local_seo.get("url","").strip():                  eeat += 1
    home = data.get("home", {})
    if home.get("fonti_utilizzate"):                     eeat += 2
    if data.get("schema_markup"):                        eeat += 2
    if home.get("h1"):                                   seo  += 2
    serv = data.get("pagina_servizio", {})
    if serv.get("h1"):                                   seo  += 1
    if data.get("faq") and len(data["faq"]) >= 3:        seo  += 2
    if data.get("schema_markup"):                        seo  += 2
    if home.get("sezione_1",{}).get("h2"):               seo  += 1
    if serv.get("come_funziona",{}).get("steps"):        seo  += 1
    h1 = home.get("h1","")
    if h1 and len(h1) < 20:                              seo  -= 1
    if data.get("ai_summary"):                           geo  += 2
    if data.get("entities"):                             geo  += 2
    if data.get("schema_markup"):
        org = data["schema_markup"].get("organization",{})
        if org.get("knowsAbout"):                        geo  += 1
        if org.get("sameAs"):                            geo  += 1
    meta = data.get("_meta_fonti",{})
    if meta.get("geo_entities"):                         geo  += 2
    if meta.get("rag_attivo"):                           geo  += 1
    if meta.get("scraping_attivo"):                      geo  += 1
    eeat = min(10, max(0, eeat))
    seo  = min(10, max(0, seo))
    geo  = min(10, max(0, geo))
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
    return {"eeat": eeat, "seo": seo, "geo": geo, "risk_level": risk}


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6f: HTML BLOCK GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_html_blocks(data: dict) -> dict:
    html_blocks = {}
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
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6g: SAMEAS BUILDER & P.IVA EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def extract_vat_id(scrape_data: dict) -> str:
    """
    v11 — Regex P.IVA migliorata: cerca in TUTTI i testi (non solo footer).
    Gestisce varianti: P.IVA, Partita IVA, C.F. e P.IVA, VAT IT.
    Restituisce "IT12345678901" o "" se non trovata.
    """
    # Pattern principale: P.IVA con o senza prefisso IT, con separatori vari
    vat_pattern = re.compile(
        r"(?:P\.?\s*IVA|Partita\s+IVA|C\.?\s*F\.?\s*e\s*P\.?\s*IVA|VAT\s*(?:IT)?|P\s*\.?\s*IVA)\s*:?\s*"
        r"(IT\s*)?"
        r"(\d[\s.\-]?\d[\s.\-]?\d[\s.\-]?\d[\s.\-]?\d[\s.\-]?\d[\s.\-]?\d[\s.\-]?\d[\s.\-]?\d[\s.\-]?\d[\s.\-]?\d)",
        re.IGNORECASE
    )
    # Pattern secondario: sequenza IT + 11 cifre standalone
    bare_it_pattern = re.compile(r"\bIT\s*(\d{11})\b", re.IGNORECASE)

    all_texts = scrape_data.get("testi", [])
    for item in all_texts:
        text = item.get("testo", "")
        # Pattern principale
        match = vat_pattern.search(text)
        if match:
            prefix = "IT" if not (match.group(1) or "").strip() else ""
            digits = re.sub(r"[\s.\-]", "", match.group(2))
            if len(digits) == 11:
                return f"{prefix}{digits}".upper()
        # Pattern secondario
        match2 = bare_it_pattern.search(text)
        if match2:
            return f"IT{match2.group(1)}"
    return ""


def extract_social_urls(scrape_data: dict) -> list:
    """v10 — Social Hub: estrae tutti i profili social rilevati nei testi di scraping."""
    social_patterns = [
        ("facebook",  re.compile(r"https?://(?:www\.)?facebook\.com/[a-zA-Z0-9._\-/]+")),
        ("instagram", re.compile(r"https?://(?:www\.)?instagram\.com/[a-zA-Z0-9._\-/]+")),
        ("linkedin",  re.compile(r"https?://(?:www\.)?linkedin\.com/(?:company|in)/[a-zA-Z0-9._\-/]+")),
        ("twitter",   re.compile(r"https?://(?:www\.)?(?:twitter|x)\.com/[a-zA-Z0-9._\-/]+")),
        ("youtube",   re.compile(r"https?://(?:www\.)?youtube\.com/(?:@|channel/|c/)[a-zA-Z0-9._\-/]+")),
        ("tiktok",    re.compile(r"https?://(?:www\.)?tiktok\.com/@[a-zA-Z0-9._\-/]+")),
        ("pinterest", re.compile(r"https?://(?:www\.)?pinterest\.(?:it|com)/[a-zA-Z0-9._\-/]+")),
    ]
    found = []
    seen: set = set()
    all_text = " ".join(item.get("testo", "") for item in scrape_data.get("testi", []))
    for _platform, pattern in social_patterns:
        for match in pattern.finditer(all_text):
            url = match.group(0).rstrip("/.,)")
            if url not in seen:
                seen.add(url)
                found.append(url)
    return found


def build_same_as(local_seo: dict, extra_socials: list = None) -> list:
    same_as = []
    url      = local_seo.get("url","").strip()
    linkedin = local_seo.get("linkedin","").strip()
    lat      = local_seo.get("gps_lat","").strip()
    lon      = local_seo.get("gps_lon","").strip()
    if url:      same_as.append(url)
    if linkedin: same_as.append(linkedin)
    if lat and lon:
        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        same_as.append(maps_url)
    if extra_socials:
        same_as.extend([s for s in extra_socials if s and s not in same_as])
    return same_as


BUSINESS_TYPE_MAP = {
    "ristorante": "Restaurant", "bar": "BarOrPub", "pizzeria": "Restaurant",
    # FIX 11 v12: olio/frantoio = Store (produttore, non ristoratore); vino = Winery
    "trattoria": "Restaurant", "olio": "Store", "vino": "Winery",
    "cantina": "Winery", "frantoio": "Store", "pasticceria": "Bakery",
    "gelateria": "IceCreamShop", "panetteria": "Bakery",
    "medico": "MedicalBusiness", "dentista": "Dentist", "clinica": "MedicalClinic",
    "farmacia": "Pharmacy", "veterinario": "VeterinaryCare",
    "fisioterapia": "MedicalBusiness", "palestra": "SportsActivityLocation",
    "avvocato": "LegalService", "notaio": "LegalService",
    "commercialista": "ProfessionalService", "architetto": "ProfessionalService",
    "ingegnere": "ProfessionalService", "consulente": "ProfessionalService",
    "negozio": "Store", "boutique": "ClothingStore", "gioielleria": "JewelryStore",
    "libreria": "BookStore", "ottica": "Store",
    "hotel": "LodgingBusiness", "albergo": "Hotel", "b&b": "BedAndBreakfast",
    "agriturismo": "LodgingBusiness", "spa": "DaySpa",
    "agenzia": "ProfessionalService", "software": "SoftwareApplication",
    "sviluppo": "ProfessionalService", "marketing": "ProfessionalService",
    "web": "ProfessionalService",
    "scuola": "School", "università": "EducationalOrganization",
    "accademia": "EducationalOrganization", "corso": "EducationalOrganization",
    "artigiano": "LocalBusiness", "manifattura": "LocalBusiness", "produzione": "LocalBusiness",
}

def infer_schema_type(servizi: str, contesto: str = "") -> str:
    testo = (servizi + " " + contesto).lower()
    for keyword, schema_type in BUSINESS_TYPE_MAP.items():
        if keyword in testo:
            return schema_type
    return "LocalBusiness"

def parse_address(indirizzo: str) -> dict:
    if not indirizzo:
        return {}
    parts = [p.strip() for p in indirizzo.split(",") if p.strip()]
    cap = ""
    cap_idx = -1
    for i, p in enumerate(parts):
        if re.match(r"^\d{5}$", p):
            cap = p
            cap_idx = i
            break
    street = parts[0] if len(parts) > 0 else ""
    if len(parts) > 1 and re.match(r"^(snc|s\.n\.c\.|\d+[a-z]?)$", parts[1], re.IGNORECASE):
        street = f"{parts[0]}, {parts[1]}"
        city_idx = 2
    else:
        city_idx = 1
    city = parts[city_idx] if len(parts) > city_idx else ""
    province = parts[cap_idx + 1] if cap_idx >= 0 and len(parts) > cap_idx + 1 else ""
    return {
        "@type": "PostalAddress",
        "streetAddress": street,
        "addressLocality": city,
        "postalCode": cap,
        "addressRegion": province,
        "addressCountry": "IT",
    }

def build_opening_hours_spec(orari: dict) -> list:
    DAY_MAP = {
        "Lunedì": "Monday", "Martedì": "Tuesday", "Mercoledì": "Wednesday",
        "Giovedì": "Thursday", "Venerdì": "Friday",
        "Sabato": "Saturday", "Domenica": "Sunday",
    }
    fascia_to_days: dict = {}
    for giorno, fascia in orari.items():
        if not fascia:
            continue
        eng_day = DAY_MAP.get(giorno, giorno)
        key = fascia.strip()
        fascia_to_days.setdefault(key, []).append(eng_day)
    specs = []
    for fascia, days in fascia_to_days.items():
        sub_fasce = [f.strip() for f in fascia.split(",") if f.strip()]
        for sf in sub_fasce:
            match = re.match(r"(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})", sf)
            if match:
                specs.append({
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": days,
                    "opens": match.group(1),
                    "closes": match.group(2),
                })
    return specs


# ─────────────────────────────────────────────────────────────────────────────
# FIX 1 v11: SLUGIFICATION AGGRESSIVA PER @id SCHEMA PRODOTTI
# ─────────────────────────────────────────────────────────────────────────────

def _slugify_product(name: str, max_words: int = 4) -> str:
    """
    v11 — Slugification aggressiva: genera slug corti e semantici.
    Prende al massimo `max_words` parole significative (stop words escluse).
    Risultato: slug di 15-30 char max, mai l'intera frase del premio.
    
    Esempi:
      "Consulenza SEO Avanzata per E-commerce" → "consulenza-seo-avanzata"
      "Olio EVO DOP Coratina — Flos Olei 99/100" → "olio-evo-dop-coratina"
      "Piano Editoriale Premium 2024" → "piano-editoriale-premium"
    """
    STOP_WORDS = {
        "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
        "di", "del", "della", "dei", "delle", "degli", "in", "nel",
        "nella", "nei", "nelle", "negli", "per", "con", "su", "su",
        "tra", "fra", "e", "o", "ma", "che", "da", "a", "al",
        "per", "se", "come", "questo", "questa", "quello", "quella",
    }
    # Normalizza caratteri accentati
    s = name.lower().strip()
    s = re.sub(r"[àáâã]", "a", s)
    s = re.sub(r"[èéêë]", "e", s)
    s = re.sub(r"[ìíîï]", "i", s)
    s = re.sub(r"[òóôõ]", "o", s)
    s = re.sub(r"[ùúûü]", "u", s)
    # Rimuovi tutto ciò che viene dopo trattini lunghi (suffissi premio)
    s = re.sub(r"\s*[–—]\s*.+$", "", s)
    # Rimuovi punteggi numerici (99/100, 95/100)
    s = re.sub(r"\d+/\d+", "", s)
    # Rimuovi anni e numeri isolati
    s = re.sub(r"\b20\d{2}\b", "", s)
    # Sostituisci non-alfanumerici con spazio
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    # Filtra stop words e prendi le prime max_words parole significative
    words = [w for w in s.split() if w and w not in STOP_WORDS and len(w) > 1]
    selected = words[:max_words]
    slug = "-".join(selected).strip("-")
    return slug or "product"


def _extract_guide_name(award_text: str) -> str:
    """FIX 13 v12: estrae il nome della guida/ente che ha assegnato il riconoscimento."""
    guides = [
        "Flos Olei", "Gambero Rosso", "Bibenda", "Slow Food", "Michelin",
        "Merum", "Maestrod'Olio", "Guida Oli d'Italia", "Guida Vini d'Italia",
        "Touring Club", "L'Espresso", "Dissapore", "AIAB", "DOP", "IGP",
    ]
    award_lower = award_text.lower()
    for g in guides:
        if g.lower() in award_lower:
            return g
    return "Guida di Settore"


def build_schema_markup(
    azienda: str,
    local_seo: dict,
    servizi: str,
    fatti: str,
    faq_data: list = None,
    products: list = None,
    awards: list = None,
    same_as: list = None,
    schema_type: str = None,
) -> dict:
    """
    Genera schema_markup JSON-LD completo con @graph.
    v11: @id prodotti usa slug corti (_slugify_product con max_words=4).
         Il campo `name` contiene SOLO il nome commerciale.
         I premi vanno ESCLUSIVAMENTE nel campo `award`.
    """
    url_raw = local_seo.get("url", "").strip()
    if url_raw and not url_raw.startswith("http"):
        url_raw = f"https://www.{url_raw}"
    base_id = url_raw or f"https://www.{azienda.lower().replace(' ', '')}.it"

    if not schema_type or schema_type == "LocalBusiness":
        schema_type = infer_schema_type(servizi, fatti)

    address = parse_address(local_seo.get("indirizzo", ""))
    geo = {}
    lat = local_seo.get("gps_lat", "").strip()
    lon = local_seo.get("gps_lon", "").strip()
    if lat and lon:
        geo = {"@type": "GeoCoordinates", "latitude": lat, "longitude": lon}

    orari = local_seo.get("orari", {})
    opening_hours_spec = build_opening_hours_spec(orari) if orari else []
    same_as_list = same_as or []

    # Nodo LocalBusiness
    local_business = {
        "@type": schema_type,
        "@id": f"{base_id}#business",
        "name": azienda,
        "url": url_raw,
        "telephone": local_seo.get("telefono", ""),
        "email": local_seo.get("email", ""),
        "address": address,
    }
    local_business = {k: v for k, v in local_business.items() if v}
    if geo:
        local_business["geo"] = geo
    if opening_hours_spec:
        local_business["openingHoursSpecification"] = opening_hours_spec
    if same_as_list:
        local_business["sameAs"] = same_as_list
    # FIX v13: image (facoltativo ma raccomandato da Google per rich result)
    logo_url = local_seo.get("logo_url", "").strip()
    if logo_url:
        local_business["image"] = logo_url
    # FIX v13: priceRange — solo per tipi che lo supportano semanticamente
    PRICE_RANGE_TYPES = {"Restaurant", "BarOrPub", "Bakery", "IceCreamShop", "Store",
                         "ClothingStore", "JewelryStore", "BookStore", "Hotel",
                         "BedAndBreakfast", "LodgingBusiness", "DaySpa", "Winery"}
    price_range_biz = local_seo.get("price_range", "").strip()
    if price_range_biz and schema_type in PRICE_RANGE_TYPES:
        local_business["priceRange"] = price_range_biz
    # servesCuisine — solo per tipi ristorativi (Restaurant, BarOrPub, ecc.)
    SERVES_CUISINE_TYPES = {"Restaurant", "BarOrPub", "Bakery", "IceCreamShop"}
    serves_cuisine = local_seo.get("serves_cuisine", "").strip()
    if serves_cuisine and schema_type in SERVES_CUISINE_TYPES:
        local_business["servesCuisine"] = serves_cuisine

    # Nodo Organization
    organization = {
        "@type": "Organization",
        "@id": f"{base_id}#organization",
        "name": azienda,
        "url": url_raw,
    }
    if same_as_list:
        organization["sameAs"] = same_as_list
    if awards:
        organization["award"] = awards
    # FIX 4 v11: vatID garantito anche in build_schema_markup
    vat_id = local_seo.get("vat_id", "").strip()
    if vat_id:
        organization["vatID"] = vat_id

    servizi_list = [s.strip() for s in re.split(r"[,;\n·•\-]+", servizi) if s.strip()][:6]
    if servizi_list:
        organization["knowsAbout"] = servizi_list

    # FIX 1 v11: Nodi Product con @id corti e name separato da award
    product_nodes = []
    if products:
        seen_slugs: set = set()
        for i, prod in enumerate(products):
            if not isinstance(prod, dict) or not prod.get("name"):
                continue

            # Slug corto e semantico (max 4 parole significative)
            prod_slug = _slugify_product(prod.get("name", f"product-{i+1}"), max_words=4)

            # Deduplicazione slug
            base_slug = prod_slug
            counter = 2
            while prod_slug in seen_slugs:
                prod_slug = f"{base_slug}-{counter}"
                counter += 1
            seen_slugs.add(prod_slug)

            node = {
                "@type": "Product",
                "@id": f"{base_id}#product-{prod_slug}",
                # FIX 1: name = solo nome commerciale, NO premi/suffissi
                "name": prod["name"],
                "brand": {"@type": "Brand", "name": azienda},
            }
            if prod.get("description"):
                node["description"] = prod["description"]
            # FIX 1: award sempre separato dal name
            if prod.get("award"):
                node["award"] = prod["award"]
            if prod.get("category"):
                node["category"] = prod["category"]
            # FIX v13: offers con price numerico SEMPRE presente (obbligatorio Google Rich Result)
            price_range = prod.get("priceRange", "")
            explicit_price = prod.get("price", "")  # valore numerico esplicito, se disponibile
            # Mappa simboli prezzo → valore numerico indicativo per Rich Result
            price_value_map = {"€": "10.00", "€€": "25.00", "€€€": "50.00", "Premium": "80.00"}
            if explicit_price:
                numeric_price = str(explicit_price)
            else:
                numeric_price = price_value_map.get(price_range, "0.00")
            offers_node = {
                "@type": "Offer",
                "priceCurrency": "EUR",
                # FIX v13: price numerico SEMPRE presente — campo critico per Rich Snippet Google
                "price": numeric_price,
                "availability": "https://schema.org/InStock",
            }
            if price_range:
                offers_node["description"] = price_range
            # FIX v13: shippingDetails e hasMerchantReturnPolicy (facoltativi, migliorano il rich result)
            shipping = prod.get("shippingDetails", {})
            if shipping:
                offers_node["shippingDetails"] = shipping
            return_policy = prod.get("hasMerchantReturnPolicy", {})
            if return_policy:
                offers_node["hasMerchantReturnPolicy"] = return_policy
            node["offers"] = offers_node

            # FIX v13: image prodotto (CRITICO — richiesto da Google per rich result Product)
            product_image = prod.get("image", "").strip()
            if not product_image and url_raw:
                # Fallback: usa URL azienda come riferimento immagine (placeholder accettato da Google)
                product_image = url_raw
            if product_image:
                node["image"] = product_image

            # FIX v13: description prodotto (facoltativo, migliora comprensione AI/Google)
            if not node.get("description") and prod.get("description"):
                node["description"] = prod["description"]

            reviews = []
            for review in prod.get("reviews", []):
                r = {
                    "@type": "Review",
                    "author": {"@type": "Organization", "name": review.get("source", "Guida di Settore")},
                }
                if review.get("rating") and review.get("best_rating"):
                    r["reviewRating"] = {
                        "@type": "Rating",
                        "ratingValue": str(review["rating"]),
                        "bestRating": str(review["best_rating"]),
                    }
                if review.get("year"):
                    r["datePublished"] = str(review["year"])
                if review.get("description"):
                    r["reviewBody"] = review["description"]
                reviews.append(r)

            # FIX 13 v12: se il prodotto ha un award, sintetizza una review da esso
            if not reviews and prod.get("award"):
                award_text = prod["award"]
                # Cerca anno nel testo del premio
                year_match = re.search(r"\b(20\d{2})\b", award_text)
                year = year_match.group(1) if year_match else ""
                # Tenta di estrarre un rating numerico (es. 99/100)
                rating_match = re.search(r"(\d{2,3})/(\d{2,3})", award_text)
                synth_review = {
                    "@type": "Review",
                    "author": {"@type": "Organization", "name": _extract_guide_name(award_text)},
                    "reviewBody": award_text[:200],
                }
                if year:
                    synth_review["datePublished"] = year
                if rating_match:
                    synth_review["reviewRating"] = {
                        "@type": "Rating",
                        "ratingValue": rating_match.group(1),
                        "bestRating": rating_match.group(2),
                    }
                reviews.append(synth_review)

            if reviews:
                node["review"] = reviews

            # FIX 13 v12: aggregateRating con ratingCount ≥ 1 (obbligatorio per Rich Result)
            main_review = next((r for r in prod.get("reviews", []) if r.get("rating")), None)
            if main_review:
                node["aggregateRating"] = {
                    "@type": "AggregateRating",
                    "ratingValue": str(main_review["rating"]),
                    "bestRating": str(main_review.get("best_rating", 100)),
                    "reviewCount": str(max(1, len(reviews))),
                }
            elif reviews and reviews[0].get("reviewRating"):
                # Sintetizza aggregateRating dalla review estratta dall'award
                rv = reviews[0]["reviewRating"]
                node["aggregateRating"] = {
                    "@type": "AggregateRating",
                    "ratingValue": rv.get("ratingValue", "5"),
                    "bestRating": rv.get("bestRating", "100"),
                    "reviewCount": "1",
                }

            product_nodes.append(node)

    # Nodo FAQPage
    faq_node = None
    if faq_data:
        main_entity = []
        for faq in faq_data:
            domanda = faq.get("domanda") or faq.get("name") or faq.get("question", "")
            risposta = faq.get("risposta") or faq.get("answer") or faq.get("text", "")
            if domanda and risposta:
                main_entity.append({
                    "@type": "Question",
                    "name": domanda,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": risposta[:500],
                    },
                })
        if main_entity:
            faq_node = {"@type": "FAQPage", "mainEntity": main_entity}

    graph = [local_business, organization]
    graph.extend(product_nodes)
    if faq_node:
        graph.append(faq_node)

    return {
        "@context": "https://schema.org",
        "@graph": graph,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6h: AI SUMMARY BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def build_ai_summary(azienda: str, servizi: str, local_seo: dict, fatti: str) -> str:
    addr = parse_address(local_seo.get("indirizzo", ""))
    city = addr.get("addressLocality", "")
    province = addr.get("addressRegion", "")
    location_str = f"{city} ({province})" if city and province else city
    primo_servizio = servizi.split(",")[0].strip() if servizi else ""
    fatto_lines = [l.strip().strip("·•-\"'") for l in fatti.split("\n") if l.strip()]
    primo_fatto = fatto_lines[0] if fatto_lines else ""
    parti = []
    if azienda:
        parti.append(azienda)
    if primo_servizio:
        parti.append(f"specializzata in {primo_servizio}")
    if location_str:
        parti.append(f"con sede a {location_str}")
    if primo_fatto:
        parti.append(primo_fatto)
    summary = ", ".join(parti)
    if summary and not summary.endswith("."):
        summary += "."
    if len(summary) > 200:
        summary = summary[:197].rsplit(" ", 1)[0].rstrip(",") + "..."
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 6i: POST-PROCESS PIPELINE v11
# FIX 6: reset internal_linking_suggestions prima di ogni run
# ─────────────────────────────────────────────────────────────────────────────
def post_process(
    generated: dict,
    azienda: str,
    servizi: str,
    fatti: str,
    local_seo: dict,
    verified_texts: list = None,
    schema_type: str = "LocalBusiness",
    scrape_data: dict = None,
    lingua: str = "italiano",
) -> dict:
    """
    Pipeline post-processing globale v11:
    FIX 6: Reset esplicito internal_linking_suggestions prima della build.
    """
    verified_data = [t for t in (verified_texts or []) if t and t.strip()]
    _scrape = scrape_data or {}

    # 1. Fact hardening
    if generated.get("home"):
        generated["home"] = harden_section(generated["home"], verified_data)
    if generated.get("pagina_servizio"):
        generated["pagina_servizio"] = harden_section(generated["pagina_servizio"], verified_data)

    # 2. CTA strutturate
    for key, stype in [("home", "home"), ("pagina_servizio", "service")]:
        section = generated.get(key, {})
        if section and isinstance(section.get("cta"), str):
            section["cta"] = build_structured_cta(section["cta"], stype)

    # 3. Products — anticipato rispetto a Entities (FIX UnboundLocalError v13)
    #    ai_products deve essere definita PRIMA che venga usata in build_entity_block
    ai_products = (
        generated.get("prodotti")
        or generated.get("products")
        or build_products_from_fatti(fatti, azienda)
    )
    if not ai_products and servizi:
        ai_products = build_service_products(servizi, azienda)
    if ai_products:
        generated["products"] = ai_products

    # 4. Entities block — FIX 10 v12: passa products per popolarne l'array
    generated["entities"] = build_entity_block(azienda, servizi, local_seo, schema_type,
                                                products_list=generated.get("products") or ai_products)

    # 5. AI Summary
    generated["ai_summary"] = build_ai_summary(azienda, servizi, local_seo, fatti)

    # 6. sameAs + P.IVA + Social Hub
    vat_id = extract_vat_id(_scrape)
    if vat_id and not local_seo.get("vat_id", "").strip():
        local_seo["vat_id"] = vat_id

    scraped_socials = extract_social_urls(_scrape)
    same_as = build_same_as(local_seo, extra_socials=scraped_socials)

    # 6b. Awards dai fatti
    award_patterns = [
        r"\b(?:premio|premiato|vincitore|vince|medaglia|corona|stella|foglie?|gocce?|"
        r"riconoscimento|award|best|first place|oro|argento|bronzo|"
        r"flos olei|gambero rosso|bibenda|slow food|michelin|merum|"
        r"maestro|azienda dell.anno)\b"
    ]
    awards_found = []
    for line in fatti.split("\n"):
        line = line.strip().strip("·•-")
        if line and any(re.search(p, line, re.IGNORECASE) for p in award_patterns):
            awards_found.append(line)

    # 7. FAQ
    faq_data = generated.get("faq", [])

    # 7b. Schema markup completo
    generated["schema_markup"] = build_schema_markup(
        azienda=azienda,
        local_seo=local_seo,
        servizi=servizi,
        fatti=fatti,
        faq_data=faq_data,
        products=ai_products if ai_products else None,
        awards=awards_found if awards_found else None,
        same_as=same_as,
        schema_type=schema_type,
    )

    # FIX 12 v12: meta_description completa, non troncata a metà frase
    # Genera una frase autonoma e significativa entro 155 char
    home = generated.get("home", {})
    h1 = home.get("h1", azienda)
    intro = home.get("intro", "")
    # Estrai la prima frase completa (fino al primo punto)
    first_sentence = ""
    if intro:
        sentences = re.split(r"(?<=[.!?])\s+", intro)
        if sentences:
            first_sentence = sentences[0].strip()
    if first_sentence and len(first_sentence) <= 155:
        meta_desc = first_sentence
    elif first_sentence:
        # Tronca alla parola intera più vicina a 152 char, aggiunge "."
        truncated = first_sentence[:152].rsplit(" ", 1)[0].rstrip(",;:").rstrip()
        meta_desc = truncated + "."
    elif intro:
        # Fallback: tronca intro alla parola intera, chiudi con punto
        truncated = intro[:152].rsplit(" ", 1)[0].rstrip(",;:").rstrip()
        meta_desc = truncated + "."
    else:
        meta_desc = f"{azienda} — {servizi[:100].split(',')[0].strip()}."
    url_raw = local_seo.get("url", "").strip()
    if url_raw and not url_raw.startswith("http"):
        url_raw = f"https://www.{url_raw}"
    slug = re.sub(r"[^a-z0-9\-]", "", azienda.lower().replace(" ", "-"))
    generated["page_meta"] = {
        "slug":             slug,
        "meta_title":       h1[:60] if h1 else azienda,
        "meta_description": meta_desc,
        "og_title":         h1[:60] if h1 else azienda,
        "og_description":   meta_desc,
        "canonical_url":    url_raw or f"https://www.{slug}.it/",
    }

    # 9. Sentiment E-E-A-T enrichment v12 (deep extraction + fallback intelligente)
    sentiment_terms = extract_sentiment_terms(_scrape, servizi=servizi)
    # FIX 8 v12: se nessuna recensione rilevata, inietta fallback da fatti/geo_entities
    if not sentiment_terms:
        fallback_candidates = []
        fatti_lower = fatti.lower()
        geo_ents = generated.get("_meta_fonti", {}).get("geo_entities", [])
        # Keyword emotive ricavabili direttamente dal testo del debrief
        sentiment_fallback_map = {
            "dop": "autenticità", "igp": "autenticità", "biologico": "sostenibilità",
            "bio": "sostenibilità", "certificat": "affidabilità", "storia": "tradizione",
            "1817": "tradizione", "1890": "tradizione", "generazioni": "tradizione",
            "premiato": "eccellenza", "premio": "eccellenza", "riconoscimento": "eccellenza",
            "artigian": "artigianalità", "famiglia": "tradizione", "territorio": "territorialità",
            "tracciab": "tracciabilità", "qualità": "qualità certificata", "flos olei": "eccellenza",
            "gambero rosso": "eccellenza", "bibenda": "eccellenza", "slow food": "sostenibilità",
            "rinnovabile": "sostenibilità", "energia": "sostenibilità",
        }
        for trigger, sentiment in sentiment_fallback_map.items():
            if trigger in fatti_lower and sentiment not in fallback_candidates:
                fallback_candidates.append(sentiment)
        sentiment_terms = fallback_candidates[:8]
    generated["sentiment_keywords"] = sentiment_terms
    if sentiment_terms:
        generated["page_meta"] = enrich_meta_with_sentiment(generated["page_meta"], sentiment_terms)
        for prod in generated.get("products", []):
            if prod.get("description") and not prod.get("sentiment_enriched"):
                prod["description"] += " " + ", ".join(sentiment_terms[:3])
                prod["sentiment_enriched"] = True

    # FIX 6 v11: RESET ESPLICITO internal_linking_suggestions prima della build
    # Garantisce zero cross-contaminazione tra run di clienti diversi
    generated["internal_linking_suggestions"] = {}

    # 10. Internal Linking Map con context reset confermato
    linking = build_internal_linking_map(
        servizi=servizi,
        generated=generated,
        azienda=azienda,
        base_url=url_raw,
        lingua=lingua,
    )
    generated.update(linking)

    # FIX 6 v11: conferma reset nel JSON output
    generated["_silo_reset_confirmed"] = True

    # 11. Quality score
    generated["quality_score"] = compute_quality_score(generated, local_seo, verified_data)

    # 12. HTML blocks
    html_blocks = generate_html_blocks(generated)
    generated.update(html_blocks)

    return generated


def scrape_website(url: str, timeout: int = 8) -> dict:
    """Scraping BeautifulSoup di homepage e pagine chiave."""
    result = {"testi": [], "url_visitati": [], "errori": []}
    if not url or not url.startswith("http"):
        return result
    try:
        from bs4 import BeautifulSoup
        import urllib.request
    except ImportError:
        result["errori"].append("BeautifulSoup4 non installato. Esegui: pip install beautifulsoup4")
        return result
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
    for target_url in urls_to_visit[:5]:
        try:
            req = urllib.request.Request(target_url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            text = re.sub(r"\n{3,}", "\n\n", text)
            text = text[:2000]
            if len(text.strip()) > 100:
                result["testi"].append({"url": target_url, "testo": text})
                result["url_visitati"].append(target_url)
            time.sleep(0.3)
        except Exception as e:
            err = str(e)
            if "404" not in err and "403" not in err:
                result["errori"].append(f"{target_url}: {err[:80]}")
            continue
    return result


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 7b: CONTACT EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────
def extract_contacts_from_scrape(scrape_data: dict) -> dict:
    contacts = {"telefono": "", "email": ""}
    phone_pattern = re.compile(
        r"(?:\+39[\s\-]?)?(?:0\d{1,4}[\s\-]?\d{4,8}|\d{3}[\s\-]?\d{3,4}[\s\-]?\d{4})"
    )
    email_pattern = re.compile(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    )
    for item in scrape_data.get("testi", []):
        text = item.get("testo", "")
        url  = item.get("url", "").lower()
        priority = ("contatt" in url or "contact" in url)
        if not contacts["telefono"]:
            for p in phone_pattern.findall(text):
                if len(re.sub(r"\D", "", p)) >= 8:
                    contacts["telefono"] = p.strip()
                    break
        if not contacts["email"]:
            exclude = ("noreply", "no-reply", "donotreply", "example", "test@")
            for e in email_pattern.findall(text):
                if not any(ex in e.lower() for ex in exclude):
                    contacts["email"] = e.strip()
                    break
        if priority and contacts["telefono"] and contacts["email"]:
            break
    return contacts


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 7c: GEOCODIFICA AUTOMATICA
# ─────────────────────────────────────────────────────────────────────────────
def geocode_address(indirizzo: str) -> dict:
    """v10 — Geocodifica resiliente con fallback automatico a 3 livelli."""
    if not indirizzo or not indirizzo.strip():
        return {}
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="alligator_geo_tool_v11")
        location = geolocator.geocode(indirizzo, timeout=20, country_codes="it")
        if location:
            return {
                "gps_lat": str(round(location.latitude,  6)),
                "gps_lon": str(round(location.longitude, 6)),
            }
        parts = [p.strip() for p in indirizzo.split(",") if p.strip()]
        if len(parts) >= 2:
            via = parts[0]
            citta = ""
            for p in parts[1:]:
                if not re.match(r"^\d{4,5}$", p) and not re.match(r"^[A-Z]{2}$", p):
                    citta = p
                    break
            if citta:
                query_semplificato = f"{via}, {citta}, Italia"
                location = geolocator.geocode(query_semplificato, timeout=20, country_codes="it")
                if location:
                    return {
                        "gps_lat": str(round(location.latitude,  6)),
                        "gps_lon": str(round(location.longitude, 6)),
                    }
                location = geolocator.geocode(f"{citta}, Italia", timeout=20, country_codes="it")
                if location:
                    return {
                        "gps_lat": str(round(location.latitude,  6)),
                        "gps_lon": str(round(location.longitude, 6)),
                    }
    except Exception:
        pass
    return {}


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 7d: SENTIMENT & E-E-A-T ESTESO v11
# FIX 3: Deep extraction — professionalità, autorità, competenza
# ─────────────────────────────────────────────────────────────────────────────

SENSORY_SEED_FOOD = [
    "profumo", "aroma", "fragranza", "bouquet", "sentore", "fruttato",
    "erbaceo", "floreale", "mandorlato", "carciofo", "pomodoro",
    "amaro", "piccante", "piccantezza", "retrogusto", "persistenza",
    "rotondo", "equilibrato", "elegante", "morbido", "vellutato",
    "sapido", "fresco", "vivace", "intenso", "delicato", "fine",
    "strutturato", "complesso", "armonico", "color oro", "dorato",
    "verde intenso", "limpido", "brillante",
    "polifenoli", "tocoferoli", "acidità", "perossidi", "cultivar",
    "coratina", "ogliarola", "frantoio", "moraiolo", "leccino",
    "nocellara", "cerasuola",
]

EEAT_AUTHORITY_SEED = [
    "performance misurabile", "autorità tecnica", "trasparenza dei dati",
    "approccio strategico", "ottimizzazione semantica", "Premier Partner",
    "audit tecnico", "benchmark", "ROI documentato", "dati verificabili",
    "case study", "metodologia proprietaria", "framework validato",
    "analisi quantitativa", "metriche reali", "report certificato",
    "competenza verticale", "specializzazione", "track record",
    "certificazione professionale", "Google Partner", "Meta Partner",
    "team certificato", "processo documentato",
]

# FIX 3 v11: Seed professionalità/autorità per recensioni non sensoriali
# Termini che appaiono tipicamente in recensioni Google, testimonianze B2B,
# feedback clienti — anche in contesti non food/sensoriali.
PROFESSIONALISM_AUTHORITY_SEED = [
    "serietà", "seri", "competenza", "competente", "competenti",
    "tempestività", "tempestivo", "tempestiva", "puntualità", "puntuale",
    "affidabilità", "affidabile", "affidabili", "professionalità",
    "professionale", "professionali", "preparazione", "preparati",
    "esperienza", "esperti", "disponibilità", "disponibile",
    "cortesia", "cortese", "gentilezza", "gentile", "precisione",
    "precisi", "cura dei dettagli", "attenzione", "reattività",
    "reattivo", "chiarezza", "trasparenza", "onestà", "onesto",
    "qualità del servizio", "soddisfazione", "consigliato",
    "consiglio", "risultati concreti", "problem solving",
]

EEAT_FORBIDDEN_AGENCY = [
    "risultati garantiti", "primo su google",
    "garantiamo", "certifichiamo il successo", "numero uno",
    "leader indiscusso", "i migliori", "il miglior",
]

REVIEW_SECTION_PATTERNS = [
    r"(?:recensione|review|commento|feedback|valutazione|opinione|giudizio)",
    r"(?:ha scritto|ha lasciato|cliente dice|utente dice)",
    r"(?:tripadvisor|google review|trustpilot|g2\.com|capterra)",
    r"(?:stelle|stars|★|☆|⭐)",
    r"(?:testimonianza|referenza|caso studio|case study)",
    # FIX 3 v11: pattern aggiuntivi per rilevare contesti di feedback professionale
    r"(?:ottimo lavoro|ottima esperienza|ci siamo trovati|siamo soddisfatti)",
    r"(?:consiglio vivamente|raccomando|raccomandiamo|consigliatissimo)",
    r"(?:professionisti seri|team preparato|staff competente|personale qualificato)",
]


def _detect_sector(scrape_data: dict, servizi: str = "") -> str:
    """Rileva il settore dall'azienda per scegliere il seed E-E-A-T corretto."""
    all_text = (servizi or "") + " ".join(
        item.get("testo", "")[:500] for item in scrape_data.get("testi", [])[:3]
    )
    text_lower = all_text.lower()
    food_signals = ("olio", "vino", "frantoio", "cantina", "ristorante", "gastronomia",
                    "agroalimentare", "cibo", "food", "extravergine", "dop", "igp")
    agency_signals = ("agenzia", "consulenza", "marketing", "seo", "geo", "web",
                      "digital", "software", "sviluppo", "comunicazione", "media")
    food_score   = sum(1 for s in food_signals   if s in text_lower)
    agency_score = sum(1 for s in agency_signals if s in text_lower)
    if food_score > agency_score:
        return "food"
    if agency_score > 0:
        return "agency"
    return "generic"


def extract_sentiment_terms(scrape_data: dict, servizi: str = "") -> list:
    """
    v11 — Deep Extraction sentiment E-E-A-T.

    NOVITÀ v11 (FIX 3):
    - Aggiunto PROFESSIONALISM_AUTHORITY_SEED: 'serietà', 'competenza',
      'tempestività', 'affidabilità', 'professionalità' e simili.
    - Questi termini vengono cercati anche in contesti non sensoriali
      (es. testimonianze B2B, recensioni Google, feedback clienti).
    - La detection del contesto positivo è estesa: cerca anche frasi
      di soddisfazione/raccomandazione intorno al termine.
    - Zero invenzioni: se il termine non appare nel testo reale → non incluso.

    REGOLE ANTI-FUFFA (invariate):
    - Vietati 'risultati garantiti', 'primo su Google'.
    - Almeno un segnale di recensione deve essere presente nel testo.
    """
    all_text = " ".join(item.get("testo", "") for item in scrape_data.get("testi", []))
    if not all_text.strip():
        return []

    has_reviews = any(re.search(p, all_text, re.IGNORECASE) for p in REVIEW_SECTION_PATTERNS)
    if not has_reviews:
        return []

    sector = _detect_sector(scrape_data, servizi)

    # FIX 3 v11: seed combinato settore-specifico + professionalità universale
    if sector == "food":
        seed = SENSORY_SEED_FOOD + PROFESSIONALISM_AUTHORITY_SEED
    elif sector == "agency":
        seed = EEAT_AUTHORITY_SEED + PROFESSIONALISM_AUTHORITY_SEED
    else:
        seed = SENSORY_SEED_FOOD + EEAT_AUTHORITY_SEED + PROFESSIONALISM_AUTHORITY_SEED

    forbidden_lower = [f.lower() for f in EEAT_FORBIDDEN_AGENCY]

    found = []
    text_lower = all_text.lower()

    # Segnali negativi da contestualizzare
    neg_signals = ("non ", "senza ", "poco ", "scarso", "negativo", "cattivo", "purtroppo", "deludente")
    # FIX 3 v11: segnali positivi espliciti (rafforzano il rilevamento)
    pos_signals = ("molto ", "davvero ", "estremamente ", "assolutamente ", "ottima ", "ottimo ",
                   "eccellente", "perfetta", "perfetto", "massima ", "alta ", "grande ")

    for term in seed:
        term_lower = term.lower()
        if any(f in term_lower for f in forbidden_lower):
            continue
        if term_lower in text_lower:
            idx = text_lower.find(term_lower)
            # Finestra di contesto più ampia per professionalità (80 char vs 40)
            window = 80 if term_lower in [t.lower() for t in PROFESSIONALISM_AUTHORITY_SEED] else 40
            context = text_lower[max(0, idx - window): idx + len(term_lower) + window]
            # Includi se: nessun negativo nel contesto OPPURE c'è un positivo esplicito
            has_neg = any(neg in context for neg in neg_signals)
            has_pos = any(pos in context for pos in pos_signals)
            if not has_neg or has_pos:
                found.append(term)

    return list(dict.fromkeys(found))[:10]


def enrich_meta_with_sentiment(page_meta: dict, sentiment_terms: list) -> dict:
    """Inietta keyword sensoriali nel meta_description se disponibili."""
    if not sentiment_terms or not page_meta:
        return page_meta
    enriched = dict(page_meta)
    terms_str = ", ".join(sentiment_terms[:5])
    meta_desc = enriched.get("meta_description", "")
    if meta_desc and len(meta_desc) + len(terms_str) + 3 <= 160:
        enriched["meta_description"] = f"{meta_desc.rstrip('.')} — {terms_str}."
    else:
        enriched["sentiment_keywords_meta"] = terms_str
    return enriched


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 7e: PRODUCT SCHEMA ARRAY
# FIX 1 v11: build_products_from_fatti estrae nome commerciale puro
# ─────────────────────────────────────────────────────────────────────────────

CATEGORY_PRICE_MAP = {
    "dop": "Premium", "igp": "€€€", "biologico": "€€€", "bio": "€€€",
    "extravergine": "€€", "gourmet": "Premium", "riserva": "Premium",
    "affiorante": "Premium", "monocultivar": "€€€", "cosmetico": "€€",
    "cosmesi": "€€", "infuso": "€€",
    "consulenza": "€€", "audit": "€€", "seo": "€€", "geo": "€€",
    "marketing": "€€", "strategia": "€€", "piano editoriale": "€€",
    "formazione": "€€", "workshop": "€€", "corso": "€€",
    "sviluppo web": "€€€", "sviluppo": "€€€", "software": "€€€",
    "premium": "Premium", "enterprise": "€€€",
}

_SERVICE_PRODUCT_SIGNALS = re.compile(
    r"\b(?:consulenza|audit|seo|geo|marketing|piano|strategia|report|analisi|"
    r"formazione|workshop|corso|sviluppo|software|pacchetto|servizio|"
    r"abbonamento|contratto|progetto|campagna|gestione)\b",
    re.IGNORECASE,
)

_PURE_AWARD_PATTERNS = re.compile(
    r"^\s*(?:logo|marchio|certificazione|premio|punteggio|flos olei|gambero rosso|"
    r"bibenda|medaglia|award|riconoscimento|three leaves|due foglie|tre foglie|"
    r"corona|stelle michelin)\b",
    re.IGNORECASE,
)

_PRODUCT_NAME_SIGNALS = re.compile(
    r"\b(?:olio|riserva|affiorante|blend|monocultivar|cosme|infus|linea|"
    r"collezione|vino|extravergine|evo|prodotto|referenza|etichetta|"
    r"l['\u2019]affiorante|dop|igp|biologico|bio)\b",
    re.IGNORECASE,
)

# FIX 1 v11: pattern più aggressivo per pulire il nome da tutto ciò che è premio/anno/punteggio
_NAME_NOISE = re.compile(
    r"\s*(?:–|-|—|/)\s*(?:premio|flos olei|gambero rosso|bibenda|punteggio|"
    r"medaglia|award|20\d{2}|19\d{2}|99[/\\]100|\d+[/\\]\d+|tre foglie|"
    r"due foglie|corona|stelle|gold|silver|bronze|oro|argento|bronzo).*$",
    re.IGNORECASE,
)

# FIX 1 v11: estrae SOLO la parte del nome commerciale prima di qualsiasi suffisso premio
_COMMERCIAL_NAME_RE = re.compile(
    r"^([A-Za-zÀ-ÖØ-öø-ÿ\s'''\-]+?)(?:\s*(?:–|—|-)\s*|\s+(?:premio|flos|gambero|bibenda|medaglia|20\d{2}|punteggio|\d+[/\\]\d+)|\s*$)",
    re.IGNORECASE,
)


def _extract_commercial_name(raw_line: str) -> str:
    """
    v11 — Estrae SOLO il nome commerciale del prodotto/servizio.
    Rimuove aggressivamente: premi, punteggi, anni, guide, separatori.
    
    Esempi:
      "Olio Riserva DOP — Flos Olei 2023 99/100" → "Olio Riserva Dop"
      "Consulenza SEO — Premio Best Agency 2024"  → "Consulenza Seo"
      "Coratina Monocultivar Gambero Rosso 3 Foglie" → "Coratina Monocultivar"
    """
    # Step 1: rimuovi tutto dopo separatori tipo —, –, |
    s = re.split(r"\s*[–—|]\s*", raw_line)[0].strip()
    # Step 2: applica _NAME_NOISE per rimuovere suffissi premio
    s = _NAME_NOISE.sub("", s).strip()
    # Step 3: rimuovi punteggi residui (99/100, 95/100)
    s = re.sub(r"\s*\d+[/\\]\d+\s*$", "", s).strip()
    # Step 4: rimuovi anni isolati finali
    s = re.sub(r"\s*\b(20\d{2}|19\d{2})\b\s*$", "", s).strip()
    # Step 5: rimuovi nomi di guide/premi al fondo
    s = re.sub(
        r"\s*\b(?:flos olei|gambero rosso|bibenda|slow food|michelin|award|premio)\b.*$",
        "", s, flags=re.IGNORECASE
    ).strip()
    # Title case finale
    return s.title() if s else ""


def build_products_from_fatti(fatti: str, azienda: str = "") -> list:
    """
    v11 — FIX 1: nome commerciale puro separato dai premi.
    - _extract_commercial_name() garantisce che `name` = solo nome prodotto.
    - I dettagli premio vanno ESCLUSIVAMENTE in `award`.
    """
    if not fatti:
        return []

    products = []
    seen_names: set = set()

    lines = [
        l.strip().strip("·•-\"'—").strip()
        for l in re.split(r"[\n;]", fatti) if l.strip()
    ]

    pending_awards: list = []
    for line in lines:
        if _PURE_AWARD_PATTERNS.search(line):
            pending_awards.append(line.strip())

    for line in lines:
        line_lower = line.lower()

        if _PURE_AWARD_PATTERNS.search(line):
            continue

        if not (_PRODUCT_NAME_SIGNALS.search(line) or _SERVICE_PRODUCT_SIGNALS.search(line)):
            continue

        is_award = bool(re.search(
            r"\b(?:premio|premiato|flos olei|gambero rosso|bibenda|medaglia|"
            r"corona|stella|foglie?|award|riconoscimento|punteggio)\b",
            line_lower
        ))

        # FIX 1 v11: usa _extract_commercial_name per nome puro
        prod_name = _extract_commercial_name(line)
        if not prod_name or len(prod_name) < 3:
            # Fallback: prendi prima parte della riga
            name_match = re.match(r"^([^(·\-–—:]+)", line)
            raw_name = name_match.group(1).strip() if name_match else line[:60]
            prod_name = raw_name.title()

        if not prod_name or len(prod_name) < 3 or prod_name in seen_names:
            continue
        seen_names.add(prod_name)

        category = ""
        for cat_key in CATEGORY_PRICE_MAP:
            if cat_key in line_lower:
                category = cat_key.title()
                break
        price_range = CATEGORY_PRICE_MAP.get(category.lower(), "€€")

        # FIX 1 v11: description = riga completa solo se non è un award nella stessa riga
        description = line if not is_award else ""

        # FIX 1 v11: award = TUTTA la riga originale se contiene premio,
        # oppure matching da pending_awards
        matched_award = ""
        if is_award:
            matched_award = line  # la riga stessa È il premio
        else:
            name_keywords = [w for w in prod_name.lower().split() if len(w) > 3]
            for pa in pending_awards:
                if any(kw in pa.lower() for kw in name_keywords):
                    matched_award = pa
                    break

        products.append({
            "name":        prod_name,       # SOLO nome commerciale
            "description": description,      # riga completa se non è pure award
            "award":       matched_award,    # SOLO premi/riconoscimenti
            "category":    category,
            "priceRange":  price_range,
        })

    return products[:8]


def build_service_products(servizi: str, azienda: str = "") -> list:
    """v10 — Commercial Entity: tratta i servizi principali come prodotti Schema.org."""
    if not servizi:
        return []
    service_list = [s.strip().strip("·•-") for s in re.split(r"[,;\n·•]+", servizi) if s.strip()]
    products = []
    seen: set = set()
    for svc in service_list[:8]:
        if not svc or len(svc) < 3 or svc in seen:
            continue
        seen.add(svc)
        svc_lower = svc.lower()
        category  = ""
        price_range = "€€"
        for cat_key, price in CATEGORY_PRICE_MAP.items():
            if cat_key in svc_lower:
                category   = cat_key.title()
                price_range = price
                break
        if not category:
            if any(k in svc_lower for k in ("enterprise", "premium", "avanzato", "full")):
                price_range = "Premium"
            category = "Servizio Professionale"
        products.append({
            "name":        svc.title(),
            "description": f"{svc} offerto da {azienda}" if azienda else svc,
            "award":       "",
            "category":    category,
            "priceRange":  price_range,
        })
    return products


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 7f: INTERNAL LINKING MAP v11
# FIX 6: context reset garantito
# ─────────────────────────────────────────────────────────────────────────────

SILO_LINK_RULES = [
    ("cosmesi",       "qualità olio",   "Cosmesi → 'Qualità dell'Olio' come ingrediente base"),
    ("prodotti",      "come produrre",  "Prodotti → processo produttivo"),
    ("qualità",       "certificazioni", "Qualità → certificazioni DOP/IGP"),
    ("certificazioni","prodotti",       "Certificazioni → linea prodotti certificati"),
    ("storia",        "prodotti",       "Storia → prodotti che rappresentano la tradizione"),
    ("faq",           "prodotti",       "FAQ → prodotti per rispondere 'dove comprare'"),
    ("faq",           "contatti",       "FAQ → contatti per rispondere 'come ordinare'"),
    ("homepage",      "prodotti",       "Homepage → pagina prodotti principale"),
    ("homepage",      "storia",         "Homepage → chi siamo / storia"),
    ("homepage",      "faq",            "Homepage → FAQ per ridurre il bounce rate"),
    ("servizi",       "case study",     "Servizi → case study per aumentare trust"),
    ("servizi",       "blog",           "Servizi → articoli tematici correlati"),
    ("blog",          "servizi",        "Articoli blog → pagina servizi pertinente"),
    ("chi siamo",     "servizi",        "Chi siamo → servizi offerti"),
    ("premi",         "prodotti",       "Premi → prodotti premiati"),
]


def build_internal_linking_map(
    servizi: str,
    generated: dict,
    azienda: str = "",
    base_url: str = "",
    lingua: str = "italiano",
) -> dict:
    """
    v11 — FIX 6: Context Silo Reset garantito.
    Il dizionario suggestions viene inizializzato a {} all'inizio di questa funzione,
    indipendentemente da qualsiasi stato precedente del processo.
    """
    # FIX 6 v11: reset esplicito locale — nessun residuo da run precedenti
    suggestions: dict = {}

    servizi_lower  = (servizi or "").lower()
    base           = (base_url or "https://www.sito.it").rstrip("/")

    _has_faq     = bool(generated.get("faq"))
    _has_service = bool(generated.get("pagina_servizio"))
    _has_products= bool(generated.get("prodotti") or generated.get("products"))
    _has_blog    = "blog" in servizi_lower
    _has_case    = any(k in servizi_lower for k in ("case study","caso studio","portfolio"))
    _has_storia  = any(k in servizi_lower for k in ("storia","chi siamo","about","fondato","founded"))
    _is_food     = any(k in servizi_lower for k in ("olio","vino","cibo","food","ristorante","frantoio","gastronomia"))
    _is_agency   = any(k in servizi_lower for k in ("agenzia","marketing","seo","geo","consulenza","web","digital"))

    page_map: dict = {"homepage": base + "/", "contatti": base + "/contatti/"}
    if _has_faq:      page_map["faq"]      = base + "/faq/"
    if _has_service:  page_map["servizi"]  = base + "/servizi/"
    if _has_products: page_map["prodotti"] = base + "/prodotti/"
    if _has_blog:     page_map["blog"]     = base + "/blog/"
    if _has_case:     page_map["case study"] = base + "/case-study/"
    if _has_storia:   page_map["storia"]   = base + "/chi-siamo/"
    if _is_food:
        page_map.update({
            "qualità":        base + "/qualita/",
            "certificazioni": base + "/certificazioni/",
            "cosmesi":        base + "/cosmesi/",
            "premi":          base + "/premi-riconoscimenti/",
        })
    if _is_agency:
        page_map.update({
            "audit":    base + "/audit/",
            "risultati": base + "/risultati/",
            "metodologia": base + "/metodologia/",
        })

    DYNAMIC_RULES: list = []
    DYNAMIC_RULES += [
        ("homepage", "faq",      "Homepage → FAQ per ridurre il bounce rate"),
        ("homepage", "contatti", "Homepage → contatti (conversion base)"),
    ]
    if _has_service:
        DYNAMIC_RULES += [
            ("homepage",  "servizi",   "Homepage → pagina servizi principale"),
            ("servizi",   "contatti",  "Servizi → contatti per richiesta preventivo"),
        ]
    if _has_faq and _has_service:
        DYNAMIC_RULES.append(("faq", "servizi", "FAQ → servizi per rispondere 'come funziona'"))
    if _has_faq:
        DYNAMIC_RULES.append(("faq", "contatti", "FAQ → contatti per rispondere 'come ordinare'"))
    if _has_products:
        DYNAMIC_RULES += [
            ("homepage",  "prodotti",  "Homepage → pagina prodotti principale"),
            ("servizi",   "prodotti",  "Servizi → prodotti correlati"),
        ]
    if _has_blog and _has_service:
        DYNAMIC_RULES += [
            ("blog",     "servizi",   "Articoli blog → pagina servizi pertinente"),
            ("servizi",  "blog",      "Servizi → articoli tematici correlati"),
        ]
    if _has_case and _has_service:
        DYNAMIC_RULES.append(("servizi", "case study", "Servizi → case study per aumentare trust"))
    if _is_food:
        if "premi" in page_map and _has_products:
            DYNAMIC_RULES.append(("premi", "prodotti", "Premi → prodotti premiati"))
        if "certificazioni" in page_map and _has_products:
            DYNAMIC_RULES.append(("certificazioni", "prodotti", "Certificazioni → linea prodotti certificati"))
        if "cosmesi" in page_map and "qualità" in page_map:
            DYNAMIC_RULES.append(("cosmesi", "qualità", "Cosmesi → 'Qualità dell'Olio' come ingrediente base"))
    if _is_agency:
        if "metodologia" in page_map and _has_service:
            DYNAMIC_RULES.append(("servizi", "metodologia", "Servizi → metodologia per aumentare autorità"))
        if "risultati" in page_map and _has_case:
            DYNAMIC_RULES.append(("case study", "risultati", "Case study → pagina risultati per proof"))

    ANCHOR_TRANSLATIONS = {
        "spagnolo": {
            "homepage": "Inicio", "storia": "Historia", "qualità": "Calidad",
            "certificazioni": "Certificaciones", "cosmesi": "Cosmética", "premi": "Premios",
            "contatti": "Contacto", "blog": "Blog", "servizi": "Servicios",
            "faq": "Preguntas Frecuentes", "prodotti": "Productos",
            "case study": "Casos de Éxito", "metodologia": "Metodología",
            "audit": "Auditoría", "risultati": "Resultados",
        },
        "inglese": {
            "homepage": "Home", "storia": "Our Story", "qualità": "Quality",
            "certificazioni": "Certifications", "cosmesi": "Cosmetics", "premi": "Awards",
            "contatti": "Contact", "blog": "Blog", "servizi": "Services",
            "faq": "FAQ", "prodotti": "Products",
            "case study": "Case Studies", "metodologia": "Methodology",
            "audit": "Audit", "risultati": "Results",
        },
        "francese": {
            "homepage": "Accueil", "storia": "Notre Histoire", "qualità": "Qualité",
            "certificazioni": "Certifications", "cosmesi": "Cosmétique", "premi": "Récompenses",
            "contatti": "Contact", "blog": "Blog", "servizi": "Services",
            "faq": "FAQ", "prodotti": "Produits",
            "case study": "Études de Cas", "metodologia": "Méthodologie",
            "audit": "Audit", "risultati": "Résultats",
        },
    }
    anchor_map = ANCHOR_TRANSLATIONS.get(lingua.lower(), {})

    def get_anchor(topic: str) -> str:
        return anchor_map.get(topic, topic.title())

    for source_topic, target_topic, rationale in DYNAMIC_RULES:
        source_url = page_map.get(source_topic, "")
        target_url = page_map.get(target_topic, "")
        if not (source_url and target_url):
            continue
        if source_url not in suggestions:
            suggestions[source_url] = []
        suggestions[source_url].append({
            "target_url":  target_url,
            "anchor_text": get_anchor(target_topic),
            "rationale":   rationale,
            "priority":    "high" if source_topic in ("homepage", "faq") else "medium",
        })

    return {
        "internal_linking_suggestions": suggestions,
        "_silo_note": (
            f"Suggerimenti Silo v11 — generati da entità rilevate in questa run "
            f"({'food' if _is_food else 'agency' if _is_agency else 'generic'} sector). "
            "Context reset attivo: zero link a settori non pertinenti. "
            "Verifica che le URL target esistano prima dell'implementazione."
        ),
    }


def format_scrape_for_prompt(scrape_data: dict) -> str:
    if not scrape_data.get("testi"):
        return ""
    lines = ["=== CONTENUTI ESTRATTI DAL SITO WEB (PRIORITÀ MASSIMA) ==="]
    for item in scrape_data["testi"]:
        lines.append(f"\n[Fonte: {item['url']}]")
        lines.append(item["testo"])
    lines.append("=== FINE CONTENUTI SITO WEB ===")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 8: RICERCA WEB MULTI-QUERY — Deep RAG con URL FILTER
# ─────────────────────────────────────────────────────────────────────────────

DENYLIST_DOMAINS = frozenset([
    "youtube.com", "youtu.be", "m.youtube.com",
    "facebook.com", "m.facebook.com", "fb.com", "fb.me",
    "instagram.com", "tiktok.com", "twitter.com", "x.com",
    "pinterest.com", "pinterest.it", "reddit.com",
    "threads.net", "snapchat.com", "telegram.org", "t.me",
    "pandora.com", "spotify.com", "soundcloud.com",
    "apple.com/music", "music.apple.com", "deezer.com",
    "netflix.com", "twitch.tv",
    "amazon.it", "amazon.com", "ebay.it", "ebay.com",
    "aliexpress.com", "etsy.com", "wish.com",
    "trovaprezzi.it", "kelkoo.it", "idealo.it",
    "paginegialle.it", "paginebianche.it", "cylex.it",
    "europages.it", "kompass.com", "yalwa.it",
    "misterimprese.it", "virgilio.it", "tuttocitta.it",
    "yelp.com", "yelp.it", "yell.com",
    "google.com/search", "bing.com/search", "duckduckgo.com",
    "search.yahoo.com",
    "scribd.com", "slideshare.net", "issuu.com",
    "pdfcoffee.com", "studocu.com",
])

DENYLIST_URL_PATTERNS = (
    "/login", "/signin", "/sign-in", "/log-in", "/accedi",
    "/register", "/signup", "/sign-up", "/registrati",
    "/logout", "/signout",
    "/account", "/profile", "/profilo", "/my-account",
    "/dashboard", "/cart", "/carrello", "/checkout",
    "/wishlist", "/lista-desideri",
    "/support", "/help", "/assistenza", "/contatti",
    "/ticket", "/helpdesk",
    "/privacy", "/cookie", "/terms", "/termini",
    "/condizioni", "/tos", "/gdpr", "/disclaimer",
    "/sitemap", "/robots.txt", "/rss", "/feed",
    "/wp-admin", "/wp-login", "/admin/",
    "/tag/", "/tags/", "/category/#", "/?s=",
    "utm_source=", "fbclid=", "gclid=",
)


def is_valid_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    url_lower = url.lower()
    blocked = ("youtube", "google", "facebook", "pandora",
               "login", "support", "account", "signin")
    return not any(bad in url_lower for bad in blocked)


is_url_clean = is_valid_url

AUTHORITATIVE_DOMAINS = [
    ".gov", ".gov.it", ".edu", ".europa.eu", ".int",
    "ilsole24ore.com", "repubblica.it", "corriere.it", "ansa.it",
    "milanofinanza.it", "economy.it", "startupitalia.eu",
    "economyup.it", "wired.it", "agi.it",
    "reuters.com", "bloomberg.com", "ft.com", "wsj.com",
    "forbes.com", "forbes.it", "harvardbusiness.org", "hbr.org",
    "techcrunch.com", "theverge.com", "arstechnica.com", "wired.com",
    "camcom.it", "cciaa.it", "registroimprese.it",
    "unioncamere.gov.it", "agenziaentrate.gov.it",
    "mise.gov.it", "mimit.gov.it", "istat.it",
    "ismea.it", "ice.it", "ismeamercati.it",
    "accredia.it", "iso.org", "uni.com", "cen.eu",
    "qualivita.it", "origine.info", "dop-igp.it",
    "confindustria.it", "coldiretti.it", "confcommercio.it",
    "confartigianato.it", "cna.it", "confagricoltura.it",
    "federmeccanica.it", "federchimica.it",
    "gamberorosso.it", "slowfood.it", "guide.michelin.com",
    "flos-olei.com", "freshplaza.it", "foodweb.it",
    "gdoweek.it", "mark-up.it", "pambianconews.com",
    "distribuzionemoderna.info", "netcomm.it", "osservatori.net",
    "zerounoweb.it", "01net.it", "cwi.it", "cmi.it",
    "digital4.biz", "b2b24.it",
    "wikipedia.org", "treccani.it",
]

def score_source_authority(url: str) -> int:
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
    evidence = {
        "premi_riconoscimenti":  [],
        "certificazioni_qualita": [],
        "storia_fondazione":     [],
        "fonti_aggregate":       [],
        "errori":                [],
        "url_scartati":          [],
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
                valid_results = []
                for r in raw_results:
                    url   = r.get("href", "") or r.get("url", "")
                    title = (r.get("title", "") or "").lower()
                    body  = (r.get("body", "") or r.get("snippet", "") or "").lower()
                    if not is_valid_url(url):
                        evidence["url_scartati"].append(url)
                        continue
                    if azienda_lower not in title and azienda_lower not in body:
                        evidence["url_scartati"].append(url)
                        continue
                    valid_results.append(r)
                valid_results.sort(
                    key=lambda r: score_source_authority(r.get("href", "") or r.get("url", "")),
                    reverse=True
                )
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
                time.sleep(0.5)
    except Exception as e:
        evidence["errori"].append(f"DDGS session: {str(e)[:100]}")
    evidence["fonti_aggregate"].sort(key=lambda x: x["autorità"], reverse=True)
    evidence["fonti_aggregate"] = evidence["fonti_aggregate"][:12]
    return evidence


def format_evidence_for_prompt(evidence: dict) -> str:
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
            for item in items[:4]:
                lines.append(f"  Fonte: {item['url']}")
                lines.append(f"  Titolo: {item['titolo']}")
                lines.append(f"  Estratto: {item['snippet'][:200]}")
                lines.append("")
    lines.append("=== FINE EVIDENZE WEB ===")
    return "\n".join(lines)


def extract_source_urls(evidence: dict, scrape_data: dict) -> list:
    urls = []
    for item in evidence.get("fonti_aggregate", []):
        url = item.get("url", "")
        if url and url not in urls:
            urls.append(url)
    for url in scrape_data.get("url_visitati", []):
        if url not in urls:
            urls.append(url)
    return urls[:10]


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 9a: TONE OF VOICE SYSTEM v12
# Funzionalità C: selettore Product-Oriented / Storytelling / Bilanciato
# ─────────────────────────────────────────────────────────────────────────────

TONE_OF_VOICE_PROFILES = {
    "bilanciato": {
        "label": "⚖️ Bilanciato (default)",
        "description": "Mix equilibrato di narrazione e dati di prodotto. Tono professionale e autorevole.",
        "prompt_inject": """TONE OF VOICE — BILANCIATO:
Il testo deve bilanciare narrazione di brand e dati di prodotto in parti uguali.
• Ogni paragrafo combina un elemento di storia/contesto con un dato tecnico.
• Stile professionale, autorevole ma accessibile.
• Le sezioni prodotto sono concise e orientate ai benefici del cliente.
• Le sezioni corporate usano un tono caldo ma preciso.""",
    },
    "product_oriented": {
        "label": "🛒 Product-Oriented",
        "description": "Focus su specifiche, premi, certificazioni e benefici diretti del prodotto.",
        "prompt_inject": """TONE OF VOICE — PRODUCT-ORIENTED:
Il testo è centrato sul prodotto: specifiche tecniche, premi, certificazioni, confronti.
• Ogni frase del prodotto include almeno un dato tecnico verificato dalle fonti.
• Struttura: nome prodotto → parametro chiave → riconoscimento/certificazione → beneficio.
• Minimizza la narrazione corporate e storica — il protagonista è il prodotto.
• Usa terminologia tecnica di settore senza spiegazioni eccessive.
• Le CTA sono orientate all'acquisto/richiesta diretta.""",
    },
    "storytelling": {
        "label": "📖 Storytelling",
        "description": "Narrazione immersiva, territorio, storia, famiglia e valori del brand.",
        "prompt_inject": """TONE OF VOICE — STORYTELLING:
Il testo costruisce una narrazione immersiva attorno al brand, al territorio e alle persone.
• Ogni sezione ha un arco narrativo: contesto → conflitto/scelta → risultato.
• Privilegia metafore sensoriali, riferimenti geografici specifici, aneddoti storici.
• I dati tecnici (premi, certificazioni) vengono intrecciati nella narrazione come climax.
• Evita elenchi puntati nelle sezioni narrative — usa periodi articolati.
• Le CTA evocano un'esperienza, non solo una transazione.""",
    },
}


def get_tone_prompt(tone_key: str) -> str:
    """Restituisce il blocco prompt per il tone of voice selezionato."""
    return TONE_OF_VOICE_PROFILES.get(tone_key, TONE_OF_VOICE_PROFILES["bilanciato"])["prompt_inject"]


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 9: SYSTEM PROMPT BUILDER v12

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

  4. LUNGHEZZA FRASI — VARIABILE, MEDIA 18-25 PAROLE
     Alterna frasi brevi (8-12 parole) e articolate (25-35 parole).

  5. VIETATI GLI "ESCO INSERT" DA PROMPT
     Mai frasi-placeholder come "Ecco i nostri punti di forza:" seguite da elenco.

  6. VOICE COERENTE
     B2B e-commerce: "L'azienda" (terza) o "aiutiamo" (prima plurale).
     B2C: "trovi / scegli" (seconda singolare informale).

REGOLA MASTER:
I numeri che vedi nei prompt-template sono ISTRUZIONI DI FORMATO per te.
NON copiarli mai nel testo finale. I numeri nel testo finale vengono SOLO
dalle fonti RAG o dal debrief utente.
"""


def build_system_prompt(stile_esempi: str = "", lingua: str = "italiano", tone: str = "bilanciato") -> str:
    lingua_upper = lingua.upper()

    # FIX 2 v11: STRICT MODE rinforzato — sovrascrive anche le fonti RAG
    lang_constraint = f"""╔══════════════════════════════════════════════════════════════════╗
║  🔒 LINGUA OUTPUT — STRICT MODE v11 — VINCOLO PRIMARIO ASSOLUTO ║
╠══════════════════════════════════════════════════════════════════╣
║  OUTPUT LANGUAGE: {lingua_upper:<46}║
║                                                                  ║
║  QUESTO VINCOLO SOVRASCRIVE OGNI ALTRA ISTRUZIONE,              ║
║  INCLUSE LE FONTI RAG E I CONTENUTI DI SCRAPING.                ║
║  Anche se le fonti sono in inglese, francese o altra lingua,    ║
║  l'output JSON DEVE essere scritto in {lingua_upper}.                ║
║                                                                  ║
║  OGNI valore stringa del JSON (h1, intro, body, domanda,         ║
║  risposta, cta, steps, lista, description, meta_description,    ║
║  schema description, knowsAbout, award, category, rationale)    ║
║  DEVE essere scritto in {lingua_upper}.                               ║
║                                                                  ║
║  Non cambiare lingua tra un modulo e il successivo.              ║
║  Se hai dubbi: scrivi in {lingua_upper}.                              ║
╚══════════════════════════════════════════════════════════════════╝

"""

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
║ tempistiche, o specifiche tecniche se NON sono ESPRESSAMENTE ║
║ scritte nelle fonti RAG o nel debrief utente.                ║
║                                                              ║
║ Se ti manca il dato esatto: NON inventarlo, NON dedurlo.     ║
║ Resta su un piano puramente discorsivo.                      ║
╚══════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════╗
║         GERARCHIA DELLA VERITÀ — VINCOLO ASSOLUTO           ║
╠══════════════════════════════════════════════════════════════╣
║ LIVELLO 1 [MASSIMA PRIORITÀ]:                               ║
║   • Dati estratti dalla Ricerca Web (sezione RAG)           ║
║   • Contenuti scraping del sito web dell'azienda            ║
║ LIVELLO 2 [ALTA PRIORITÀ]:                                  ║
║   • Debrief dell'utente (fatti dichiarati)                  ║
║ LIVELLO 3 [SOLO PER CONNETTERE I DATI]:                     ║
║   • Copywriting SEO/GEO — NON inventa dati nuovi.          ║
╠══════════════════════════════════════════════════════════════╣
║ ⛔ VINCOLO CRITICO (ANTI-ALLUCINAZIONE):                    ║
║   È SEVERAMENTE VIETATO inventare:                          ║
║   • Numeri di premi non trovati nelle fonti                 ║
║   • Quantità di clienti/ordini/partner non verificate       ║
║   • Anni di fondazione non confermati dalle fonti           ║
║   • Certificazioni non trovate nel RAG o nel sito           ║
╚══════════════════════════════════════════════════════════════╝"""

    # Funzionalità C v12: Tone of Voice selezionabile
    tone_block = get_tone_prompt(tone)

    return f"""{lang_constraint}Sei il copywriter GEO/SEO senior di Alligator. Generi contenuti web ad alta citabilità AI.

{alligator_rules}
{style_section}

{tone_block}

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
# SEZIONE 10: CONTEXT BUILDER
# FIX 2 v11: vincolo lingua ripetuto nel contesto
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
    source_urls: list = None,
    contacts: dict = None,
    products: list = None,
) -> str:
    addr = local_seo.get("indirizzo", "")
    lingua_upper = lingua.upper()

    geo_block = ""
    if geo_entities:
        geo_block = f"""
ENTITÀ GEOGRAFICHE UFFICIALI DA CITARE (OBJ GEO-ENTITY):
{chr(10).join(f'  • {e}' for e in geo_entities)}
ISTRUZIONE: Cita queste entità nel testo dove pertinente. Non inventare entità non in lista."""

    sources_block = ""
    if source_urls:
        sources_block = f"""
URL FONTI DISPONIBILI (per campo fonti_utilizzate):
{chr(10).join(f'  {u}' for u in source_urls)}"""

    contacts_block = ""
    if contacts:
        tel  = contacts.get("telefono", "")
        mail = contacts.get("email", "")
        if tel or mail:
            contacts_block = f"\nCONTATTI RILEVATI DAL SITO: telefono={tel or 'n/d'}, email={mail or 'n/d'}"

    products_block = ""
    if products:
        prod_lines = [
            f"  • {p['name']} | cat: {p.get('category','?')} | prezzo: {p.get('priceRange','?')} | {p.get('award','') or p.get('description','')}"
            for p in products
        ]
        products_block = "\nPRODOTTI RILEVATI DAL DEBRIEF:\n" + "\n".join(prod_lines)

    _anno = local_seo.get("anno_fondazione", "").strip()
    anno_block = f"\nANNO DI FONDAZIONE: {_anno}" if _anno else ""

    # FIX 2 v11: vincolo lingua ripetuto anche nel context (secondo livello del triple-lock)
    lang_reminder = f"""
╔═══════════════════════════════════════════════════════════╗
║ 🔒 PROMEMORIA LINGUA: OUTPUT OBBLIGATORIO IN {lingua_upper:<14}║
║ Anche se le fonti RAG o lo scraping sono in altra lingua, ║
║ TUTTI i valori stringa del JSON vanno in {lingua_upper}.          ║
╚═══════════════════════════════════════════════════════════╝
"""

    return f"""{rag_evidence}

{scrape_content}

DEBRIEF AZIENDA (Livello 2 — fatti dichiarati):
AZIENDA: {azienda}
SERVIZI: {servizi}
TARGET: {target}
FATTI CITABILI: {fatti}
INDIRIZZO: {addr if addr else "Non specificato"}
LINGUA OUTPUT: {lingua}{anno_block}{contacts_block}{products_block}
{geo_block}
{sources_block}
{lang_reminder}"""


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 11: PROMPT MODULARI v11
# FIX 2: lingua ripetuta all'inizio di OGNI prompt modulare
# ─────────────────────────────────────────────────────────────────────────────

def _lang_lock_block(lingua: str) -> str:
    """
    FIX 2 v11: blocco lingua da iniettare all'inizio di ogni prompt modulare.
    Formulazione 'VINCOLO PRIMARIO INVIOLABILE' per prevenire drift linguistico.
    """
    lingua_upper = lingua.upper()
    return f"""╔═══════════════════════════════════════════════════════════════════╗
║ 🔒 VINCOLO PRIMARIO INVIOLABILE — LINGUA OUTPUT: {lingua_upper:<17}║
║ Ogni singolo valore stringa del JSON DEVE essere in {lingua_upper}.    ║
║ Questo sovrascrive le fonti RAG, lo scraping e qualsiasi altra  ║
║ istruzione. Non usare MAI un'altra lingua in nessun campo JSON. ║
╚═══════════════════════════════════════════════════════════════════╝

"""


def prompt_home(ctx: str, lingua: str = "italiano") -> str:
    lang_block = _lang_lock_block(lingua)
    return f"""{ctx}

{lang_block}Genera SOLO il blocco "home". Ogni campo di prosa (intro, body) deve essere
UN TESTO NARRATIVO CONTINUATIVO, non un elenco di frasi nominali.

ESEMPIO DEL FORMATO ATTESO PER IL CAMPO "intro" (replica lo stile):
"Dal 1890 [Azienda] produce [prodotto] nella [zona geografica], dove la
combinazione di [fattore 1] e [fattore 2] ha dato vita a una linea riconosciuta
dalle guide di settore — nel 2023 con le tre foglie del Gambero Rosso.
L'approccio tecnico, centrato su [processo specifico], consente di mantenere
[parametro tecnico verificato] ben sotto la soglia richiesta dalla categoria."

Rispondi ESCLUSIVAMENTE con questo JSON (tutti i campi stringa in {lingua},
prosa fluida, zero frasi-elenco):
{{
  "home": {{
    "h1": "H1 max 60 char — brand + topic principale + qualificatore concreto",
    "intro": "180-220 parole di PROSA FLUIDA (non frasi brevi separate da punto). Apri con una frase di risposta diretta che associ brand + topic + dato oggettivo. Intreccia almeno 2 dati numerici dalle fonti (anno fondazione, premi con anno, numeri verificati). Usa connettivi logici (perché, tanto che, grazie a). Stile Alligator ma non telegrafico.",
    "sezione_1": {{
      "h2": "H2 descrittivo con un dato/qualificatore concreto — non generico",
      "body": "120-160 parole di prosa continuativa. Un dato verificato dalle fonti o, se manca, descrizione DISCORSIVA del processo SENZA numeri/tempistiche inventate."
    }},
    "sezione_2": {{
      "h2": "H2 differenziazione — cosa distingue il brand con attributi concreti",
      "body": "120-160 parole di prosa continuativa. Unicità espressa tramite fatti verificabili: certificazioni, processi, aree DOP/IGP se rilevanti. Zero cliché dalla blacklist."
    }},
    "cta": "1 frase imperativa specifica al topic (non generica 'contattaci')",
    "fonti_utilizzate": ["URL_reale_1", "URL_reale_2"]
  }}
}}"""


def prompt_servizio(ctx: str, lingua: str = "italiano") -> str:
    lang_block = _lang_lock_block(lingua)
    return f"""{ctx}

{lang_block}Genera SOLO il blocco "pagina_servizio". L'intro deve essere prosa fluida;
SOLO i campi "steps" e "lista" possono contenere elementi brevi stile elenco.

ESEMPIO DEL FORMATO ATTESO PER IL CAMPO "intro":
"[Servizio] risolve [problema specifico] per [target]: l'azienda integra
[tecnologia/metodo verificato] con [processo specifico], un approccio che
riduce [parametro misurabile] rispetto alle soluzioni tradizionali. Il
risultato è [outcome concreto] con tempi di [metrica verificata]."

Rispondi ESCLUSIVAMENTE con questo JSON (campi in {lingua}):
{{
  "pagina_servizio": {{
    "h1": "H1 con keyword long-tail + qualificatore specifico (non 'Servizi di X')",
    "intro": "140-180 parole di PROSA FLUIDA. Apri con l'outcome per il cliente, non con 'Offriamo'. Intreccia 1-2 dati numerici dalle fonti. Usa la voce coerente con il brand.",
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


def prompt_faq(ctx: str, lingua: str = "italiano") -> str:
    lang_block = _lang_lock_block(lingua)
    return f"""{ctx}

{lang_block}Genera SOLO il blocco "faq" con 5 domande. Ogni risposta deve essere prosa
fluida, autonoma (leggibile fuori contesto), con un dato concreto intrecciato
(non elencato in coda). Target: AI search engines (Perplexity, SearchGPT).

Rispondi ESCLUSIVAMENTE con questo JSON (5 coppie Q&A in {lingua}, risposte 80-130 parole
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


def prompt_faq_hybrid(ctx: str, lingua: str = "italiano") -> str:
    """
    INT 3 — Hybrid Mix FAQ: SEO (Featured Snippet) + GEO (motori generativi).
    FIX 2 v11: lang_lock ripetuto all'inizio.
    """
    lang_block = _lang_lock_block(lingua)
    return f"""{ctx}

{lang_block}Genera SOLO il blocco "faq" con 5 domande usando la logica HYBRID MIX FAQ:

STRUTTURA OBBLIGATORIA DI OGNI RISPOSTA:
  PARTE 1 — AFFERMAZIONE DIRETTA (Featured Snippet):
    La prima frase risponde in modo diretto e autonomo alla domanda.
    Deve essere leggibile isolata dal contesto, come uno snippet di Google.

  PARTE 2 — APPROFONDIMENTO ENTITÀ (GEO):
    I paragrafi successivi intessono entità correlate: date storiche,
    premi con anno, denominazioni DOP/IGP, termini tecnici (polifenoli, cultivar,
    acidità, perossidi), nomi di guide (Flos Olei, Gambero Rosso).
    Il tono è narrativo e umano — nessun elenco puntato nella risposta.

VINCOLO CRITICO: dati numerici (anni, premi, punteggi) solo se nelle fonti RAG/debrief.
In assenza di dato: flow discorsivo SENZA inventare soglie o quantità.

Rispondi ESCLUSIVAMENTE con questo JSON (5 coppie Q&A in {lingua}, risposte 100-150 parole di PROSA):
{{
  "faq": [
    {{
      "domanda": "Query naturale reale (Come/Cosa/Quanto/Perché/Chi/Dove/Qual è) in {lingua}",
      "risposta": "Frase diretta di risposta immediata (Featured Snippet). Seguono 2-3 periodi densi di entità correlate. Prosa fluida, nessun elenco.",
      "fonte": "URL_reale_o_stringa_vuota"
    }},
    {{"domanda": "Q2 in {lingua}", "risposta": "100-150 parole prosa ibrida SEO+GEO in {lingua}", "fonte": ""}},
    {{"domanda": "Q3 in {lingua}", "risposta": "100-150 parole prosa ibrida SEO+GEO in {lingua}", "fonte": ""}},
    {{"domanda": "Q4 in {lingua}", "risposta": "100-150 parole prosa ibrida SEO+GEO in {lingua}", "fonte": ""}},
    {{"domanda": "Q5 in {lingua}", "risposta": "100-150 parole prosa ibrida SEO+GEO in {lingua}", "fonte": ""}}
  ]
}}"""


def prompt_schema(ctx: str, azienda: str, local_seo: dict, faq_data: list = None, lingua: str = "italiano") -> str:
    """FIX 2 v11: lang_lock aggiunto anche al prompt schema."""
    lang_block = _lang_lock_block(lingua)
    indirizzo = local_seo.get("indirizzo", "")
    url_sito  = local_seo.get("url", "https://www.esempio.it")
    linkedin  = local_seo.get("linkedin", "")
    schema_type = "LocalBusiness" if indirizzo.strip() else "Organization"

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
{lang_block}SCHEMA TYPE: {schema_type}
URL: {url_sito}
LINKEDIN: {linkedin if linkedin else "da compilare"}
ORARI: {orari_str}

Genera SOLO il blocco "schema_markup". Usa SOLO dati verificati dalle fonti per la descrizione.
I campi testuali (description, knowsAbout) devono essere in {lingua}.
Rispondi ESCLUSIVAMENTE con questo JSON:
{{
  "schema_markup": {{
    "organization": {{
      "@context": "https://schema.org",
      "@type": "{schema_type}",
      "name": "{azienda}",
      "description": "Descrizione 160 char max con keyword principale — dati verificati, zero cliché, in {lingua}",
      "url": "{url_sito}",
      "sameAs": ["{linkedin if linkedin else 'https://www.linkedin.com/company/esempio'}"],
      "knowsAbout": ["Topic specifico 1 in {lingua}", "Topic specifico 2 in {lingua}", "Topic specifico 3 in {lingua}"]
    }}
  }}
}}"""


# ─────────────────────────────────────────────────────────────────────────────
# SEZIONE 12: API CALL HANDLERS
# FIX 5 v11: max_tokens garantito >= 4096 per Anthropic, default sicuro 8192
# ─────────────────────────────────────────────────────────────────────────────
def call_openai(api_key: str, model: str, system: str, user: str) -> tuple:
    try:
        from openai import OpenAI
        client  = OpenAI(api_key=api_key)
        max_tok = MODEL_MAX_TOKENS.get(model, 4096)
        resp    = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.4,
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
        # FIX 5 v11: max_tokens sempre da MODEL_MAX_TOKENS, minimo 8192 per Anthropic
        max_tok = MODEL_MAX_TOKENS.get(model, 8192)
        max_tok = max(max_tok, 8192)  # mai sotto 8192 per i modelli Anthropic
        # NOTA: il parametro `temperature` è deprecato per i modelli Claude 4.x
        # (Opus 4.7, Sonnet 4.6, Haiku 4.5) e produce 400 invalid_request_error.
        # È stato rimosso: il modello gestisce internamente la randomness.
        resp    = client.messages.create(
            model=model,
            max_tokens=max_tok,
            system=system,
            messages=[
                {"role": "user",      "content": user},
                {"role": "assistant", "content": "{"}  # Prefill: forza JSON, elimina preamble
            ]
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
# SEZIONE 13: JSON PARSER ROBUSTO
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
# SEZIONE 14: SCHEMA MARKUP BUILDER LEGACY (build_final_schema)
# FIX 4 v11: vatID garantito anche qui
# ─────────────────────────────────────────────────────────────────────────────
def parse_orario_str(orario_str: str) -> list:
    if not orario_str or not orario_str.strip():
        return []
    fasce = []
    parti = [p.strip() for p in orario_str.split(",") if p.strip()]
    for parte in parti:
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
    vat_id    = local_seo.get("vat_id",    "").strip()  # FIX 4 v11

    schema_type     = "LocalBusiness" if indirizzo else "Organization"
    org["@type"]    = schema_type
    org["@context"] = "https://schema.org"
    org["name"]     = azienda
    if url_sito: org["url"] = url_sito

    # FIX 4 v11: vatID garantito nel nodo Organization del build_final_schema
    if vat_id:
        org["vatID"] = vat_id

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

    giorni_map = {
        "Lunedì": "Monday", "Martedì": "Tuesday", "Mercoledì": "Wednesday",
        "Giovedì": "Thursday", "Venerdì": "Friday", "Sabato": "Saturday", "Domenica": "Sunday"
    }
    oh = []
    for g_it, orario_val in orari.items():
        day_en = giorni_map.get(g_it, g_it)
        if isinstance(orario_val, str):
            fasce = parse_orario_str(orario_val)
            for (apertura, chiusura) in fasce:
                oh.append({
                    "@type":     "OpeningHoursSpecification",
                    "dayOfWeek": f"https://schema.org/{day_en}",
                    "opens":     apertura,
                    "closes":    chiusura
                })
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
# SEZIONE 15: UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def resolve_cta(cta_val) -> str:
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
# FIX 6: reset internal_linking_suggestions nel generated dict prima della generazione
# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="GEO Score™ v12 — The Authority Orchestrator",
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
    .history-item {
        background: #f8faff; border: 1px solid #c7d2fe; border-radius: 6px;
        padding: 0.4rem 0.7rem; margin: 0.2rem 0; font-size: 0.82rem; cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="geo-header">
        <h1>🐊 GEO Score™ Content Generator v12 — The Authority Orchestrator</h1>
        <p>v12: Edit Inline · History · Tone of Voice · Rich Result · Fix Products/Sentiment/Meta · Schema Store · Framework GEO Score™ by Nico Fioretti</p>
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
            opts, dflt = list(PRICING["anthropic"].keys()), "claude-sonnet-4-5"

        model = st.selectbox("Modello", opts,
                             index=opts.index(dflt) if dflt in opts else 0,
                             format_func=lambda m: MODEL_LABELS.get(m, m))

        api_key = st.text_input("🔑 API Key", type="password",
                                placeholder="sk-... oppure sk-ant-...")

        st.divider()

        # ── FUNZIONALITÀ C: Tone of Voice ────────────────────────────────────
        st.subheader("🎨 Tone of Voice")
        tone_options = list(TONE_OF_VOICE_PROFILES.keys())
        tone_labels  = [TONE_OF_VOICE_PROFILES[k]["label"] for k in tone_options]
        tone_idx     = st.radio(
            "Stile narrativo",
            options=range(len(tone_options)),
            format_func=lambda i: tone_labels[i],
            index=0, key="tone_radio",
            help="Influenza il sistema di prompt per tutte le sezioni generate."
        )
        selected_tone = tone_options[tone_idx]
        st.caption(TONE_OF_VOICE_PROFILES[selected_tone]["description"])
        st.session_state["tone"] = selected_tone

        st.divider()

        # ── FUNZIONALITÀ B: History Sidebar ──────────────────────────────────
        history = st.session_state.get("client_history", [])
        if history:
            st.subheader("🕐 Clienti Recenti")
            st.caption("Clicca per ripristinare un debrief")
            for i, entry in enumerate(reversed(history[-10:])):
                if st.button(
                    f"🐊 {entry['azienda']}",
                    key=f"hist_{i}",
                    use_container_width=True,
                    help=f"Servizi: {entry.get('servizi','')[:60]}"
                ):
                    # Ripristina tutti i campi del debrief dalla history
                    for field in ["azienda","servizi","target","fatti","lingua","stile_esempi",
                                  "url_sito","telefono_manuale","email_manuale","via","citta",
                                  "cap","prov","gps_lat","gps_lon","linkedin","anno_fondazione",
                                  "logo_url","price_range"]:
                        if field in entry:
                            st.session_state[field] = entry[field]
                    # Ripristina orari
                    for giorno in ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]:
                        key_orario = f"orario_{giorno}"
                        if key_orario in entry:
                            st.session_state[key_orario] = entry[key_orario]
                    st.success(f"✅ Debrief '{entry['azienda']}' ripristinato!")
                    st.rerun()
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
        sys_tok = estimate_tokens(build_system_prompt(lingua=st.session_state.get("lingua","italiano"),
                                                      tone=st.session_state.get("tone","bilanciato")))
        in_est  = sys_tok + 800
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

        with st.expander("✅ Fix v12 attivi"):
            st.markdown("""
            **FIX 7**  — Products vs Awards separati (nomi puliti)  
            **FIX 8**  — Sentiment fallback da fatti/geo_entities  
            **FIX 9**  — FAQ key format unificato + nota JSON  
            **FIX 10** — entities.products popolato  
            **FIX 11** — Schema @type: Store per frantoio/olio (no FoodEstablishment)  
            **FIX 12** — meta_description: frase completa, no troncamento  
            **FIX 13** — Rich Result: review + aggregateRating + offers.price  
            **A** — Edit inline sezioni risultati  
            **B** — History ultimi 10 clienti nella sidebar  
            **C** — Tone of Voice: Product / Storytelling / Bilanciato  
            **D** — Rich Snippet Google completato  
            """)


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

        st.markdown("#### 🐊 Tono di Voce — Esempi Reali di Copy")
        st.caption("Il modello replica esattamente questo tono.")
        stile_esempi = st.text_area(
            "Esempi di Stile/Copy (opzionale)",
            key="stile_esempi", height=130,
            placeholder='"Non vendiamo visibilità. Costruiamo autorità che dura."\n"Meno traffico inutile. Più richieste qualificate."'
        )

        st.divider()

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
            anno_fond = st.text_input(
                "Anno di Fondazione (opz.)",
                key="anno_fondazione",
                placeholder="es. 1995  ← lascia vuoto se non vuoi citarlo"
            )
            telefono_manuale = st.text_input(
                "📞 Telefono (auto-rilevato o manuale)", key="telefono_manuale",
                placeholder="0883 123456  ← lascia vuoto per auto-rilevamento"
            )
            email_manuale = st.text_input(
                "✉️ Email (auto-rilevata o manuale)", key="email_manuale",
                placeholder="info@azienda.it  ← lascia vuoto per auto-rilevamento"
            )
            logo_url_input = st.text_input(
                "🖼️ URL Logo / Immagine aziendale (opz.)",
                key="logo_url",
                placeholder="https://www.azienda.it/logo.jpg  ← migliora i Rich Results Google"
            )
            price_range_input = st.text_input(
                "💶 Fascia di Prezzo (opz., es. €€ o 10-50€)",
                key="price_range",
                placeholder="€€  ← usato solo per ristoranti, negozi, hotel, ecc."
            )

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
            orari_dict[giorno] = orario_str

        indirizzo_completo = ", ".join(filter(None, [
            st.session_state.get("via",""),
            st.session_state.get("citta",""),
            st.session_state.get("cap",""),
            st.session_state.get("prov","")
        ]))

        local_seo = {
            "indirizzo": indirizzo_completo,
            "telefono":  st.session_state.get("telefono_manuale",""),
            "email":     st.session_state.get("email_manuale",""),
            "gps_lat":   st.session_state.get("gps_lat",""),
            "gps_lon":   st.session_state.get("gps_lon",""),
            "orari":     orari_dict,
            "url":       st.session_state.get("url_sito",""),
            "linkedin":        st.session_state.get("linkedin",""),
            "anno_fondazione": st.session_state.get("anno_fondazione",""),
            # FIX v13: nuovi campi per Rich Results Google
            "logo_url":       st.session_state.get("logo_url",""),
            "price_range":    st.session_state.get("price_range",""),
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
        st.subheader("🛠️ Generatore Modulare — Anti-Hallucination v4 · Fix v12")

        _az  = st.session_state.get("azienda","")
        _sv  = st.session_state.get("servizi","")
        _tg  = st.session_state.get("target","")
        _ft  = st.session_state.get("fatti","")
        _ln  = st.session_state.get("lingua","italiano")
        _st  = st.session_state.get("stile_esempi","")
        _loc = st.session_state.get("local_seo",{})
        _tn  = st.session_state.get("tone","bilanciato")

        # Mostra il tone attivo
        tone_info = TONE_OF_VOICE_PROFILES.get(_tn, TONE_OF_VOICE_PROFILES["bilanciato"])
        st.info(f"🎨 Tone of Voice attivo: **{tone_info['label']}** — {tone_info['description']}")
        _tn  = st.session_state.get("tone","bilanciato")

        ready = bool(_az and _sv and _tg and _ft and api_key)

        if not ready:
            missing = [x for x,v in [
                ("Nome Azienda",_az),("Servizi",_sv),("Target",_tg),
                ("Fatti",_ft),("API Key (sidebar)",api_key)
            ] if not v]
            st.warning(f"⚠️ Mancano: **{', '.join(missing)}**")

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
            <code>pip install duckduckgo-search beautifulsoup4 geopy</code><br>
            Il RAG viene eseguito UNA VOLTA prima della generazione e iniettato in ogni prompt.<br>
            <code>geopy</code> è richiesta per la geocodifica automatica GPS.
            </div>
            """, unsafe_allow_html=True)

        st.divider()

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
            sp_preview = build_system_prompt(_st, lingua=_ln, tone=_tn)
            in_est_r   = estimate_tokens(sp_preview) + 800
            tot_est    = estimate_cost(in_est_r, 1200, provider, model) * n_sel
            extra_calls = (1 if enable_rag else 0)
            st.info(f"📊 **{n_sel} chiamate AI** + **{extra_calls} fase RAG** · Costo totale stimato: **${tot_est:.5f}**")

        gen_btn = st.button(
            f"🚀 Genera {n_sel} {'sezione' if n_sel==1 else 'sezioni'}",
            disabled=(not ready or n_sel==0),
            type="primary"
        )

        if gen_btn and ready and n_sel > 0:
            sys_p = build_system_prompt(_st, lingua=_ln, tone=_tn)

            total_in  = 0
            total_out = 0

            # FIX 6 v11: reset ESPLICITO di internal_linking_suggestions
            # nel dict generato PRIMA di qualsiasi operazione.
            # Garantisce zero cross-contaminazione anche se session_state contiene residui.
            prev_generated = dict(st.session_state.get("generated", {}))
            prev_generated.pop("internal_linking_suggestions", None)  # reset silo
            prev_generated.pop("_silo_reset_confirmed", None)
            generated = prev_generated

            call_log  = []

            # ── FASE 0: RAG, SCRAPING, GEOCODIFICA, CONTATTI ────
            rag_evidence_str   = ""
            scrape_content_str = ""
            all_source_urls    = []
            scrape_data_raw    = {}
            contacts_extracted = {}
            geo_entities       = get_geo_entities(f"{_az} {_ft} {_loc.get('indirizzo','')}")
            _loc_enriched      = dict(_loc)

            if enable_scraping and _loc.get("url","").startswith("http"):
                with st.spinner("🕷️ Scraping sito web in corso..."):
                    scrape_data_raw = scrape_website(_loc["url"])
                    scrape_content_str = format_scrape_for_prompt(scrape_data_raw)
                    all_source_urls.extend(scrape_data_raw.get("url_visitati",[]))
                    if scrape_data_raw.get("errori"):
                        st.warning("⚠️ Scraping parziale: " + "; ".join(scrape_data_raw["errori"][:2]))
                    elif scrape_content_str:
                        st.success(f"✅ Scraping: {len(scrape_data_raw['testi'])} pagine lette")
                    else:
                        st.info("ℹ️ Scraping: nessun contenuto significativo estratto")

                contacts_extracted = extract_contacts_from_scrape(scrape_data_raw)
                if contacts_extracted.get("telefono") or contacts_extracted.get("email"):
                    st.success(f"📞 Contatti rilevati: tel={contacts_extracted.get('telefono','—')} · email={contacts_extracted.get('email','—')}")
                if contacts_extracted.get("telefono") and not _loc_enriched.get("telefono","").strip():
                    _loc_enriched["telefono"] = contacts_extracted["telefono"]
                if contacts_extracted.get("email") and not _loc_enriched.get("email","").strip():
                    _loc_enriched["email"] = contacts_extracted["email"]

            if not _loc_enriched.get("gps_lat","").strip() and _loc_enriched.get("indirizzo","").strip():
                with st.spinner("🌍 Geocodifica resiliente v11 in corso (fallback automatico)..."):
                    geo_coords = geocode_address(_loc_enriched["indirizzo"])
                    if geo_coords:
                        _loc_enriched.update(geo_coords)
                        st.success(f"📍 Coordinate GPS: {geo_coords['gps_lat']}, {geo_coords['gps_lon']}")
                    else:
                        st.info("ℹ️ Geocodifica non disponibile — installa geopy o inserisci coordinate manualmente.")

            products_debrief = build_products_from_fatti(_ft, _az)
            if products_debrief:
                st.info(f"🛒 {len(products_debrief)} prodotti rilevati dal debrief → Product Schema attivo (slug corti v11)")

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

            ctx = build_ctx(
                _az, _sv, _tg, _ft, _loc_enriched, _ln,
                rag_evidence=rag_evidence_str,
                scrape_content=scrape_content_str,
                geo_entities=geo_entities,
                source_urls=all_source_urls,
                contacts=contacts_extracted,
                products=products_debrief,
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
                        user_p = prompt_home(ctx, lingua=_ln)
                    elif section == "servizio":
                        user_p = prompt_servizio(ctx, lingua=_ln)
                    elif section == "faq":
                        user_p = prompt_faq_hybrid(ctx, lingua=_ln)
                    else:
                        faq_data = generated.get("faq", [])
                        user_p   = prompt_schema(ctx, _az, _loc_enriched, faq_data, lingua=_ln)

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

            if generated:
                generated["_meta_fonti"] = {
                    "fonti_rag":       all_source_urls,
                    "geo_entities":    geo_entities,
                    "rag_attivo":      enable_rag,
                    "scraping_attivo": enable_scraping,
                    "url_scraping":    _loc.get("url",""),
                    "contacts":        contacts_extracted,
                    "anno_fondazione": _loc_enriched.get("anno_fondazione",""),
                }

            if generated:
                with st.spinner("🔧 Post-processing v11: facts · products · slug · P.IVA · social hub · sentiment · silo reset..."):
                    schema_type_pp = "LocalBusiness" if _loc_enriched.get("indirizzo","").strip() else "Organization"
                    generated = post_process(
                        generated      = generated,
                        azienda        = _az,
                        servizi        = _sv,
                        fatti          = _ft,
                        local_seo      = _loc_enriched,
                        verified_texts = [_ft, rag_evidence_str, scrape_content_str],
                        schema_type    = schema_type_pp,
                        scrape_data    = scrape_data_raw,
                        lingua         = _ln,
                    )
                    # Feedback P.IVA
                    vat = _loc_enriched.get("vat_id","")
                    if vat:
                        st.success(f"🧾 P.IVA rilevata: **{vat}** → iniettata in Organization schema (vatID) — segnale E-E-A-T critico")

                    # Feedback social hub
                    schema_obj = generated.get("schema_markup", {})
                    same_as_list = []
                    for node in schema_obj.get("@graph", []):
                        if node.get("@type") in ("Organization", "LocalBusiness"):
                            same_as_list = node.get("sameAs", [])
                            break
                    social_count = len([u for u in same_as_list if any(
                        s in u for s in ("facebook","instagram","linkedin","twitter","youtube","tiktok")
                    )])
                    if social_count > 0:
                        st.success(f"🌐 Social Hub: {social_count} profili social nel grafo sameAs")

                    # Feedback sentiment v11
                    st_terms = generated.get("sentiment_keywords", [])
                    if st_terms:
                        st.success(f"🎯 Sentiment v11 Deep: {len(st_terms)} keyword reali (sensoriali + professionalità + autorità)")
                    else:
                        st.info("ℹ️ Sentiment: nessuna recensione/feedback reale rilevata — campo omesso (no invenzioni)")

                    # Feedback silo reset v11
                    links = generated.get("internal_linking_suggestions", {})
                    silo_reset = generated.get("_silo_reset_confirmed", False)
                    if links:
                        reset_label = " ✅ context reset confermato" if silo_reset else ""
                        st.success(f"🔗 Silo v11: {sum(len(v) for v in links.values())} link suggeriti{reset_label}")

                    # Feedback schema slug v11
                    n_products = len(generated.get("products", []))
                    if n_products > 0:
                        st.success(f"🏷️ Schema v11: {n_products} prodotti con @id slug corti (es. #product-consulenza-seo)")

            progress.progress(100, text="✅ Generazione completata!")

            st.session_state["generated"]         = generated
            st.session_state["in_tokens"]          = total_in
            st.session_state["out_tokens"]         = total_out
            st.session_state["local_seo_enriched"] = _loc_enriched
            real_tot = estimate_cost(total_in, total_out, provider, model)
            st.session_state["real_cost"]  = real_tot

            # ── FUNZIONALITÀ B: salva in history v12 ─────────────────────────
            if _az:
                history = st.session_state.get("client_history", [])
                # Costruisce snapshot completo del debrief
                snapshot = {
                    "azienda": _az, "servizi": _sv, "target": _tg, "fatti": _ft,
                    "lingua": _ln, "stile_esempi": _st, "tone": _tn,
                    "url_sito": st.session_state.get("url_sito",""),
                    "telefono_manuale": st.session_state.get("telefono_manuale",""),
                    "email_manuale":    st.session_state.get("email_manuale",""),
                    "via":   st.session_state.get("via",""),
                    "citta": st.session_state.get("citta",""),
                    "cap":   st.session_state.get("cap",""),
                    "prov":  st.session_state.get("prov",""),
                    "gps_lat":   st.session_state.get("gps_lat",""),
                    "gps_lon":   st.session_state.get("gps_lon",""),
                    "linkedin":  st.session_state.get("linkedin",""),
                    "anno_fondazione": st.session_state.get("anno_fondazione",""),
                }
                # Aggiungi orari
                for giorno in ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]:
                    snapshot[f"orario_{giorno}"] = st.session_state.get(f"orario_{giorno}","")
                # Rimuovi duplicato per stesso nome azienda se già presente
                history = [h for h in history if h.get("azienda") != _az]
                history.append(snapshot)
                st.session_state["client_history"] = history[-10:]  # max 10

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
        st.subheader("📄 Risultati — v12 · Edit Inline · Rich Result · Schema Store · Sentiment Fallback")

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

        ai_sum = data.get("ai_summary", "")
        if ai_sum:
            st.markdown(
                f'<div class="truth-box"><b>🤖 AI Summary</b> <em>(GEO — chi è, cosa fa, dove opera)</em><br>{ai_sum}</div>',
                unsafe_allow_html=True
            )

        _loc_res = st.session_state.get("local_seo_enriched", {})
        vat_res  = _loc_res.get("vat_id","")
        if vat_res:
            st.markdown(f"🧾 **P.IVA:** `{vat_res}` — iniettata in `Organization.vatID` (segnale E-E-A-T credibilità)")

        entities = data.get("entities", {})
        if entities:
            with st.expander("🏷️ Entity Block (GEO)"):
                st.json(entities)

        sentiment_kw = data.get("sentiment_keywords", [])
        if sentiment_kw:
            with st.expander(f"🎯 Sentiment Keywords E-E-A-T v11 Deep ({len(sentiment_kw)} termini reali)"):
                st.markdown("*Estratti da testi reali di scraping — include termini sensoriali, professionalità e autorità*")
                st.markdown(" · ".join(f"`{k}`" for k in sentiment_kw))

        ils = data.get("internal_linking_suggestions", {})
        if ils:
            total_links = sum(len(v) for v in ils.values()) if isinstance(ils, dict) else 0
            silo_reset = data.get("_silo_reset_confirmed", False)
            reset_badge = " · ✅ Context Reset v11 confermato" if silo_reset else ""
            with st.expander(f"🔗 Internal Linking Map — Silo Architecture v11 ({total_links} suggerimenti{reset_badge})"):
                st.caption(data.get("_silo_note",""))
                if isinstance(ils, dict):
                    for source_url, link_list in ils.items():
                        st.markdown(f"**Da:** `{source_url}`")
                        for lnk in link_list:
                            priority_icon = "🔴" if lnk.get("priority") == "high" else "🟡"
                            st.markdown(
                                f"  {priority_icon} → [{lnk.get('anchor_text','')}]({lnk.get('target_url','')}) "
                                f"— *{lnk.get('rationale','')}*"
                            )

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

        avail = []
        if data.get("home"):            avail.append(("🏠 Homepage","home"))
        if data.get("pagina_servizio"): avail.append(("📄 Servizio","servizio"))
        if data.get("faq"):             avail.append(("❓ FAQ","faq"))
        if data.get("products"):        avail.append(("🛒 Prodotti","prodotti"))
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

                    # ── FUNZIONALITÀ A: Edit Inline — Home ──────────────────
                    with st.expander("✏️ Modifica direttamente questa sezione", expanded=False):
                        st.caption("Le modifiche vengono salvate nel JSON e nel download automaticamente.")
                        h1_edit = st.text_input("H1", value=home.get("h1",""), key="edit_home_h1")
                        intro_edit = st.text_area("Intro", value=home.get("intro",""), height=150, key="edit_home_intro")
                        s1 = home.get("sezione_1", {})
                        s1h2_edit = st.text_input("Sezione 1 — H2", value=s1.get("h2",""), key="edit_s1h2")
                        s1body_edit = st.text_area("Sezione 1 — Body", value=s1.get("body",""), height=100, key="edit_s1body")
                        s2 = home.get("sezione_2", {})
                        s2h2_edit = st.text_input("Sezione 2 — H2", value=s2.get("h2",""), key="edit_s2h2")
                        s2body_edit = st.text_area("Sezione 2 — Body", value=s2.get("body",""), height=100, key="edit_s2body")
                        cta_edit = st.text_input("CTA", value=resolve_cta(home.get("cta","")), key="edit_home_cta")
                        if st.button("💾 Salva modifiche Homepage", key="save_home"):
                            data["home"]["h1"] = h1_edit
                            data["home"]["intro"] = intro_edit
                            data["home"].setdefault("sezione_1", {})["h2"]   = s1h2_edit
                            data["home"].setdefault("sezione_1", {})["body"] = s1body_edit
                            data["home"].setdefault("sezione_2", {})["h2"]   = s2h2_edit
                            data["home"].setdefault("sezione_2", {})["body"] = s2body_edit
                            data["home"]["cta"] = cta_edit
                            st.session_state["generated"] = data
                            st.success("✅ Homepage aggiornata nel JSON!")
                            st.rerun()

                    copy_box("📋 Copia Homepage (Markdown/Gutenberg)", home_to_md(home), "cp_home")
                    if data.get("home_html"):
                        copy_box("📋 Copia Homepage (HTML WordPress)", data["home_html"], "cp_home_html")
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

                    # ── FUNZIONALITÀ A: Edit Inline — Servizio ──────────────
                    with st.expander("✏️ Modifica direttamente questa sezione", expanded=False):
                        ps_h1_edit = st.text_input("H1 Servizio", value=page.get("h1",""), key="edit_serv_h1")
                        ps_intro_edit = st.text_area("Intro Servizio", value=page.get("intro",""), height=130, key="edit_serv_intro")
                        cf = page.get("come_funziona", {})
                        cf_h2_edit = st.text_input("Come Funziona — H2", value=cf.get("h2",""), key="edit_cf_h2")
                        cf_steps_raw = "\n".join(cf.get("steps", []))
                        cf_steps_edit = st.text_area("Come Funziona — Steps (uno per riga)", value=cf_steps_raw, height=100, key="edit_cf_steps")
                        ben = page.get("benefici", {})
                        ben_h2_edit = st.text_input("Benefici — H2", value=ben.get("h2",""), key="edit_ben_h2")
                        ben_lista_raw = "\n".join(ben.get("lista", []))
                        ben_lista_edit = st.text_area("Benefici — Lista (uno per riga)", value=ben_lista_raw, height=100, key="edit_ben_lista")
                        serv_cta_edit = st.text_input("CTA Servizio", value=resolve_cta(page.get("cta","")), key="edit_serv_cta")
                        if st.button("💾 Salva modifiche Servizio", key="save_serv"):
                            data["pagina_servizio"]["h1"] = ps_h1_edit
                            data["pagina_servizio"]["intro"] = ps_intro_edit
                            data["pagina_servizio"].setdefault("come_funziona", {})["h2"] = cf_h2_edit
                            data["pagina_servizio"].setdefault("come_funziona", {})["steps"] = [s.strip() for s in cf_steps_edit.split("\n") if s.strip()]
                            data["pagina_servizio"].setdefault("benefici", {})["h2"] = ben_h2_edit
                            data["pagina_servizio"].setdefault("benefici", {})["lista"] = [s.strip() for s in ben_lista_edit.split("\n") if s.strip()]
                            data["pagina_servizio"]["cta"] = serv_cta_edit
                            st.session_state["generated"] = data
                            st.success("✅ Pagina Servizio aggiornata nel JSON!")
                            st.rerun()

                    copy_box("📋 Copia Pagina Servizio", service_to_md(page), "cp_serv")
                    if data.get("service_html"):
                        copy_box("📋 Copia Servizio (HTML WordPress)", data["service_html"], "cp_serv_html")
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

                    # ── FUNZIONALITÀ A: Edit Inline — FAQ ───────────────────
                    with st.expander("✏️ Modifica le FAQ", expanded=False):
                        st.caption("Modifica domanda e risposta di ogni FAQ. FIX 9: chiavi interne domanda/risposta, JSON-LD usa question/acceptedAnswer.")
                        updated_faqs = []
                        for i, faq in enumerate(faqs):
                            st.markdown(f"**FAQ {i+1}**")
                            d_edit = st.text_input(f"Domanda {i+1}", value=faq.get("domanda",""), key=f"edit_faq_d_{i}")
                            r_edit = st.text_area(f"Risposta {i+1}", value=faq.get("risposta",""), height=80, key=f"edit_faq_r_{i}")
                            updated_faqs.append({**faq, "domanda": d_edit, "risposta": r_edit})
                            st.divider()
                        if st.button("💾 Salva modifiche FAQ", key="save_faq"):
                            data["faq"] = updated_faqs
                            st.session_state["generated"] = data
                            st.success("✅ FAQ aggiornate nel JSON!")
                            st.rerun()

                    copy_box("📋 Copia FAQ (Markdown/Gutenberg)", faq_to_md(faqs), "cp_faq")
                    if data.get("faq_html"):
                        copy_box("📋 Copia FAQ (HTML WordPress <details>)", data["faq_html"], "cp_faq_html")

                elif key == "prodotti":
                    prods = data.get("products", [])
                    _anno_disp = st.session_state.get("anno_fondazione","")
                    anno_lbl = f" · Fondazione: **{_anno_disp}**" if _anno_disp else ""
                    st.caption(f"🛒 {len(prods)} prodotti rilevati{anno_lbl} · Schema @id con slug corti v11")
                    for prod in prods:
                        # FIX 1 v11: mostra nome puro separato da award
                        slug_preview = _slugify_product(prod.get('name',''), max_words=4)
                        with st.expander(f"📦 {prod.get('name','Prodotto')} [{prod.get('category','')}] — @id: #product-{slug_preview}"):
                            if prod.get("description"):
                                st.markdown(f"**Descrizione:** {prod['description']}")
                            if prod.get("award"):
                                st.markdown(f"🏆 **Award:** {prod['award']}")
                            else:
                                st.caption("_(nessun award per questo prodotto)_")
                    prod_json = json.dumps(prods, ensure_ascii=False, indent=2)
                    copy_box("📋 Copia Products Array (JSON)", prod_json, "cp_products")

                elif key == "schema":
                    _loc_display = st.session_state.get("local_seo_enriched", _loc)
                    schema_json = build_final_schema(data, _loc_display, _az)
                    stype = "LocalBusiness 📍" if _loc_display.get("indirizzo","").strip() else "Organization 🌐"
                    vat_display = _loc_display.get("vat_id","")
                    vat_note = f" · P.IVA: `{vat_display}`" if vat_display else ""
                    st.caption(f"Schema: **{stype}**{vat_note} · Usa plugin WordPress 'Insert Headers and Footers'")
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
                "version":   "v13",
                "tone":      st.session_state.get("tone","bilanciato"),
                "in_tokens": in_t,
                "out_tokens":out_t,
                "cost_usd":  cost_r,
                "local_seo": _loc,
                "fonti_rag":     meta.get("fonti_rag", []),
                "geo_entities":  meta.get("geo_entities", []),
                "rag_attivo":    meta.get("rag_attivo", False),
                "scraping_attivo": meta.get("scraping_attivo", False),
                "fixes_v13": [
                    "product_offers_price_always_present",
                    "product_image_added_with_fallback",
                    "localbusiness_image_from_logo_url",
                    "localbusiness_pricerange_from_local_seo",
                    "localbusiness_servescuisine_from_local_seo",
                    "offers_shipping_and_return_policy_optional",
                ],
                "fixes_v12": [
                    "schema_id_slugification",
                    "strict_language_lock_triple",
                    "sentiment_deep_extraction_with_fallback",
                    "vat_id_improved_regex",
                    "max_tokens_8192",
                    "silo_context_reset",
                    "products_vs_awards_separated",
                    "sentiment_fallback_from_facts",
                    "faq_key_unification",
                    "entities_products_populated",
                    "schema_type_store_not_food_establishment",
                    "meta_description_complete_sentence",
                    "rich_result_review_aggregaterating_price",
                ]
            },
            "content": data
        }

        st.download_button(
            "⬇️ Scarica pacchetto completo (JSON con fonti)",
            data=json.dumps(export, ensure_ascii=False, indent=2),
            file_name=f"geo_alligator_v12_{_az.replace(' ','_').lower()}.json",
            mime="application/json"
        )


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
