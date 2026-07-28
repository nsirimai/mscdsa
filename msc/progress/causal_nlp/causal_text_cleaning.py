from __future__ import annotations

import hashlib
import html
import json
import os
import re
from pathlib import Path
from typing import Any

import pandas as pd

CLEANING_VERSION = "shared-causal-text"
MAX_SENTENCE_WORDS = 110
MIN_SENTENCE_WORDS = 6

CAUSAL_ARTIFACT_TOKENS = {
    "pdf", "qxp", "page", "pages", "copyright", "reserved", "docx",
    "figure", "fig", "table", "annex", "appendix", "footnote", "endnote",
    "isbn", "issn", "bibliography", "citation", "citations", "reference",
    "references", "metadata", "chart", "brochure", "matrix", "blueprint",
    "snapshot", "draft", "cover", "photo", "printed", "publishing",
    "directorate", "communications", "nan", "none", "null", "percentage",
    "percentages", "score", "scores", "likert", "respondent", "respondents",
    "comment", "comments", "select", "amp", "cedex", "shutterstock",
    "chapter", "section", "article", "clause", "paragraph", "subparagraph",
    "schedule", "exhibit", "supplement", "addendum", "preamble", "recital",
    "chapitre", "partie", "titre", "paragraphe", "alinea", "annexe",
    "appendice", "disposition", "bibliographie", "référence", "références",
    "tableau", "july", "april", "august", "juillet", "avril", "août",
    "vsv", "ahisa", "kwyk", "guidetoaiinschools", "nenufsd", "chatgtp",
    "tifi", "suppor", "informa", "implementa", "considera", "opportuni",
    "innova", "protec", "connec", "crea", "cod",
}

CAUSAL_ARTIFACT_PHRASES = {
    "all rights reserved", "creative commons", "executive summary",
    "table of contents", "reproduction of extracts", "printed in",
    "published by", "available at", "retrieved from", "contact us",
    "about the author", "figure source", "source figure", "photo credit",
    "cover photo", "for further information", "pour plus d'informations",
    "tous droits réservés", "table des matières", "résumé exécutif",
    "risk rating guide", "red high risk", "yellow moderate risk",
    "background material", "prepared for the members", "this figure presents",
    "this table presents", "press release on", "document:", "tags:",
    "sample cannot be assumed", "representative of the whole population",
    "response rate", "margin of error", "firm conclusions can be drawn",
    "limitations of this study", "survey methodology", "data collection method",
    "the figure is relevant because", "this figure is relevant because",
    "the table is relevant because", "this table is relevant because",
    "the discussion is relevant because", "refers to the ability",
    "is defined as",
}

ENGLISH_FUNCTION_STOPWORDS = frozenset({
    'a',
    'about',
    'above',
    'across',
    'after',
    'afterwards',
    'again',
    'against',
    'all',
    'almost',
    'alone',
    'along',
    'already',
    'also',
    'although',
    'always',
    'am',
    'among',
    'amongst',
    'amoungst',
    'amount',
    'an',
    'and',
    'another',
    'any',
    'anyhow',
    'anyone',
    'anything',
    'anyway',
    'anywhere',
    'are',
    'around',
    'as',
    'at',
    'back',
    'be',
    'became',
    'because',
    'become',
    'becomes',
    'becoming',
    'been',
    'before',
    'beforehand',
    'behind',
    'being',
    'below',
    'beside',
    'besides',
    'between',
    'beyond',
    'bill',
    'both',
    'bottom',
    'but',
    'by',
    'call',
    'can',
    'cannot',
    'cant',
    'co',
    'con',
    'could',
    'couldnt',
    'cry',
    'de',
    'describe',
    'detail',
    'do',
    'done',
    'down',
    'due',
    'during',
    'each',
    'eg',
    'eight',
    'either',
    'eleven',
    'else',
    'elsewhere',
    'empty',
    'enough',
    'etc',
    'even',
    'ever',
    'every',
    'everyone',
    'everything',
    'everywhere',
    'except',
    'few',
    'fifteen',
    'fifty',
    'fill',
    'find',
    'fire',
    'first',
    'five',
    'for',
    'former',
    'formerly',
    'forty',
    'found',
    'four',
    'from',
    'front',
    'full',
    'further',
    'get',
    'give',
    'go',
    'had',
    'has',
    'hasnt',
    'have',
    'he',
    'hence',
    'her',
    'here',
    'hereafter',
    'hereby',
    'herein',
    'hereupon',
    'hers',
    'herself',
    'him',
    'himself',
    'his',
    'how',
    'however',
    'hundred',
    'i',
    'ie',
    'if',
    'in',
    'inc',
    'indeed',
    'interest',
    'into',
    'is',
    'it',
    'its',
    'itself',
    'keep',
    'last',
    'latter',
    'latterly',
    'least',
    'less',
    'ltd',
    'made',
    'many',
    'may',
    'me',
    'meanwhile',
    'might',
    'mill',
    'mine',
    'more',
    'moreover',
    'most',
    'mostly',
    'move',
    'much',
    'must',
    'my',
    'myself',
    'name',
    'namely',
    'neither',
    'never',
    'nevertheless',
    'next',
    'nine',
    'no',
    'nobody',
    'none',
    'noone',
    'nor',
    'not',
    'nothing',
    'now',
    'nowhere',
    'of',
    'off',
    'often',
    'on',
    'once',
    'one',
    'only',
    'onto',
    'or',
    'other',
    'others',
    'otherwise',
    'our',
    'ours',
    'ourselves',
    'out',
    'over',
    'own',
    'part',
    'per',
    'perhaps',
    'please',
    'put',
    'rather',
    're',
    'same',
    'see',
    'seem',
    'seemed',
    'seeming',
    'seems',
    'serious',
    'several',
    'she',
    'should',
    'show',
    'side',
    'since',
    'sincere',
    'six',
    'sixty',
    'so',
    'some',
    'somehow',
    'someone',
    'something',
    'sometime',
    'sometimes',
    'somewhere',
    'still',
    'such',
    'system',
    'take',
    'ten',
    'than',
    'that',
    'the',
    'their',
    'them',
    'themselves',
    'then',
    'thence',
    'there',
    'thereafter',
    'thereby',
    'therefore',
    'therein',
    'thereupon',
    'these',
    'they',
    'thick',
    'thin',
    'third',
    'this',
    'those',
    'though',
    'three',
    'through',
    'throughout',
    'thru',
    'thus',
    'to',
    'together',
    'too',
    'top',
    'toward',
    'towards',
    'twelve',
    'twenty',
    'two',
    'un',
    'under',
    'until',
    'up',
    'upon',
    'us',
    'very',
    'via',
    'was',
    'we',
    'well',
    'were',
    'what',
    'whatever',
    'when',
    'whence',
    'whenever',
    'where',
    'whereafter',
    'whereas',
    'whereby',
    'wherein',
    'whereupon',
    'wherever',
    'whether',
    'which',
    'while',
    'whither',
    'who',
    'whoever',
    'whole',
    'whom',
    'whose',
    'why',
    'will',
    'with',
    'within',
    'without',
    'would',
    'yet',
    'you',
    'your',
    'yours',
    'yourself',
    'yourselves',
})

FRENCH_FUNCTION_STOPWORDS = {
    "au", "aux", "avec", "ce", "ces", "dans", "de", "des", "du", "elle",
    "en", "et", "eux", "il", "ils", "je", "la", "le", "les", "leur",
    "leurs", "lui", "ma", "mais", "me", "même", "mes", "moi", "mon",
    "ne", "nos", "notre", "nous", "on", "ou", "par", "pas", "pour",
    "qu", "que", "quelle", "quelles", "quels", "qui", "sa", "sans",
    "se", "ses", "son", "sont", "sur", "ta", "te", "tes", "toi", "ton",
    "tu", "un", "une", "vos", "votre", "vous", "ça", "ceci", "cela",
    "cet", "cette", "dont", "ici", "là", "plus", "moins", "très",
    "ainsi", "alors", "aussi", "cependant", "donc", "encore", "entre",
    "lorsque", "puis", "puisque", "tandis", "toute", "toutes", "tout",
    "tous",
}

CAUSAL_EMBEDDING_STOPWORDS = (
    set(ENGLISH_FUNCTION_STOPWORDS)
    | FRENCH_FUNCTION_STOPWORDS
    | CAUSAL_ARTIFACT_TOKENS
)

OCR_FRAGMENT_REPAIRS = [
    (r"\bh\s+tt\s+ps\b", "https"),
    (r"\bdra\s+ft\b", "draft"),
    (r"\ba\s+tt\s+ain\b", "attain"),
    (r"\bbe\s+tt\s+er\b", "better"),
    (r"\bpla\s+tf\s+orms?\b", "platform"),
    (r"\bci\s+ti\s+zens\b", "citizens"),
    (r"\bci\s+ti\s+zen\b", "citizen"),
    (r"\bs\s+ti\s+ll\b", "still"),
    (r"\bna\s+ti\s+onal\b", "national"),
    (r"\bpar\s+ti\s+cularly\b", "particularly"),
    (r"\bpar\s+ti\s+cular\b", "particular"),
    (r"\bpar\s+ti\s+cipation\b", "participation"),
    (r"\bpar\s+ti\s+cipate\b", "participate"),
    (r"\bpar\s+ti\s+cipants\b", "participants"),
    (r"\bac\s+ti\s+vely\b", "actively"),
    (r"\bac\s+ti\s+ve\b", "active"),
    (r"\bac\s+ti\s+ons\b", "actions"),
    (r"\bac\s+ti\s+on\b", "action"),
    (r"\bac\s+ti\s+vi\s+ti\s+es\b", "activities"),
    (r"\bac\s+ti\s+vity\b", "activity"),
    (r"\bop\s+ti\s+ons\b", "options"),
    (r"\bop\s+ti\s+on\b", "option"),
    (r"\borganisa\s+ti\s+onal\b", "organisational"),
    (r"\beduca\s+ti\s+onal\b", "educational"),
    (r"\bopera\s+ti\s+onalised\b", "operationalised"),
    (r"\bar\s+ti\s+culated\b", "articulated"),
    (r"\bmee\s+ti\s+ng\b", "meeting"),
    (r"\bcon\s+ti\s+nuously\b", "continuously"),
    (r"\bcon\s+ti\s+nuing\b", "continuing"),
    (r"\bcon\s+ti\s+nued\b", "continued"),
    (r"\bcon\s+ti\s+nue\b", "continue"),
    (r"\bsuppor\s+ti\s+ng\b", "supporting"),
    (r"\bpoten\s+ti\s+al\b", "potential"),
    (r"\bobjec\s+ti\s+ves\b", "objectives"),
    (r"\bti\s+me\b", "time"),
]

REQUIRED_CHUNK_COLUMNS = {
    "doc_id", "filename", "source_file", "relative_source_file", "corpus",
    "source_type", "country", "chunk_id", "chunk_index", "heading_context",
    "chunk_text",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalise_signature(text: str) -> str:
    return re.sub(r"[^a-z0-9à-ÿ]+", " ", str(text).lower()).strip()


def normalize_source_text(text: str) -> str:
    """Decode and repair common document-extraction artifacts."""
    value = html.unescape(str(text))
    value = re.sub(r"/?guillemet(?:left|right)", " ", value, flags=re.IGNORECASE)
    for pattern, replacement in OCR_FRAGMENT_REPAIRS:
        value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
    value = re.sub(
        r"\b([A-Za-zÀ-ÖØ-öø-ÿ]{3,})\s+ti\s+on(s?)\b",
        r"\1tion\2",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\b([A-Za-zÀ-ÖØ-öø-ÿ]{3,})\s+ti\s+ve\b",
        r"\1tive",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\b([A-Za-zÀ-ÖØ-öø-ÿ]{3,})\s+ti\s+([A-Za-zÀ-ÖØ-öø-ÿ]{1,8})\b",
        r"\1ti\2",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(r"\[[0-9,\s–-]+\]", " ", value)
    value = re.sub(
        r"^\s*(?:[-•●▪◦]|\d+[.)]|[A-Za-z][.)])\s+",
        "",
        value,
    )
    value = re.sub(r"^\s*\d{1,3}\s+(?=[A-ZÀ-ÖØ-Ý])", "", value)
    value = re.sub(r"^\s*sincerely,?\s*", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def content_token_ratio(text: str) -> float:
    tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", str(text).lower())
    if not tokens:
        return 0.0
    content = [
        token
        for token in tokens
        if token not in CAUSAL_ARTIFACT_TOKENS
        and len(token) > 1
        and not re.fullmatch(r"\d+", token)
    ]
    return len(content) / len(tokens)


def contains_contact_or_link(text: str) -> bool:
    """Detect web, DOI, or email residue inside extracted spans."""
    return bool(
        re.search(
            r"https?://|h\s+tt\s+ps|www\.|doi\.org|"
            r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
            str(text),
            flags=re.IGNORECASE,
        )
    )


def is_source_residue(text: str) -> bool:
    """Reject publication, reference, contact, table, code, and navigation residue."""
    raw = html.unescape(str(text))
    if re.search(
        r"https?://|h\s+tt\s+ps|www\.|doi\.org|\bdoi\s*:|"
        r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
        raw,
        flags=re.IGNORECASE,
    ):
        return True

    lowered = normalize_source_text(raw).lower()
    words = lowered.split()
    if not lowered or len(words) < MIN_SENTENCE_WORDS or len(words) > MAX_SENTENCE_WORDS:
        return True

    if re.search(
        r"function\s*\(|render\s*:\s*function|\bvar\s+[a-z_$]|"
        r"addclass|toggleclass|iframe|wp\.|navigate\s*\(|"
        r"document\.query|window\.|jquery",
        lowered,
        flags=re.IGNORECASE,
    ):
        return True
    if sum(lowered.count(symbol) for symbol in ["{", "}", "<", ">"] ) >= 3:
        return True

    if (
        re.match(
            r"^(?:pillar|teacher competency|competency|action|objective|"
            r"recommendation|cg[0-9])\b",
            lowered,
        )
        and (":" in lowered or " - " in lowered)
        and len(words) < 35
    ):
        return True
    if any(phrase in lowered for phrase in CAUSAL_ARTIFACT_PHRASES):
        return True
    if re.match(
        r"^(references?|bibliography|bibliographie|literature review|"
        r"table|tableau|figure|fig\.|appendix|annexe|percentages?|"
        r"scores?|mean|average)\b",
        lowered,
    ):
        return True
    if lowered.count("|") >= 1 or re.search(r"-{3,}", lowered):
        return True
    if lowered.count(" - ") >= 2 or lowered.count(":") >= 4:
        return True
    if len(words) > 90 and (
        lowered.count(":") >= 2
        or lowered.count(";") >= 4
        or lowered.count(" - ") >= 1
    ):
        return True
    year_count = len(re.findall(r"\b(?:19|20)\d{2}\b", lowered))
    if year_count >= 3:
        return True
    if year_count >= 1 and re.search(r"\bet\s+al\.?\b", lowered):
        return True
    artifact_hits = sum(
        token in CAUSAL_ARTIFACT_TOKENS
        for token in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", lowered)
    )
    if artifact_hits >= 4 and content_token_ratio(lowered) < 0.65:
        return True
    return content_token_ratio(lowered) < 0.44


def sentence_units(text: str) -> list[str]:
    """Split a chunk deterministically into cleaned sentence candidates."""
    cleaned = normalize_source_text(text)
    cleaned = re.sub(r"\s+[•●▪◦]\s+", ". ", cleaned)
    cleaned = re.sub(
        r"\s+-\s+(?=[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ ]{2,}:)",
        ". ",
        cleaned,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(
        r"([.!?])(['’\"])?\s+(?=[A-ZÀ-ÖØ-Ý])",
        lambda match: match.group(1) + (match.group(2) or "") + "\n",
        cleaned,
    )
    return [
        unit.strip(" -•\t")
        for unit in re.split(r"\n|(?<=[.!?])\s+(?=\S)", cleaned)
        if unit.strip()
    ]


def build_context_windows(chunks: pd.DataFrame) -> pd.DataFrame:
    ordered = chunks.sort_values(["doc_id", "chunk_index"]).copy()
    ordered["previous_chunk_text"] = ordered.groupby("doc_id")["chunk_text"].shift(1)
    ordered["next_chunk_text"] = ordered.groupby("doc_id")["chunk_text"].shift(-1)
    ordered["context_window"] = (
        ordered["heading_context"].fillna("").astype(str)
        + "\n\nPREVIOUS:\n"
        + ordered["previous_chunk_text"].fillna("").astype(str)
        + "\n\nCURRENT:\n"
        + ordered["chunk_text"].fillna("").astype(str)
        + "\n\nNEXT:\n"
        + ordered["next_chunk_text"].fillna("").astype(str)
    ).str.slice(0, 7000)
    return ordered


def build_topic_description(frame: pd.DataFrame) -> pd.Series:
    """Combine topic label, prototype, and keywords for projection."""
    return (
        frame["topic_label"].fillna("").astype(str)
        + " "
        + frame["topic_prototype"].fillna("").astype(str)
        + " "
        + frame["keywords"].fillna("").astype(str)
    ).str.replace(r"\s+", " ", regex=True).str.strip()


def infer_sentiment_country(row: pd.Series) -> str:
    source = " ".join(
        str(row.get(column, ""))
        for column in ["filename", "relative_source_file", "source_file", "doc_id"]
    ).lower()
    if any(token in source for token in ["ireland", "irish times", "qqi_", "qqi "]):
        return "ireland"
    if any(token in source for token in ["france", "français", "francais", "french", "ifop", "labo"]):
        return "france"
    return "other"


def build_clean_sentence_inventory(chunks: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_CHUNK_COLUMNS.difference(chunks.columns)
    if missing:
        raise ValueError(f"chunks_all.csv is missing columns: {sorted(missing)}")

    contextual = build_context_windows(chunks)
    rows: list[dict[str, Any]] = []
    for _, chunk in contextual.iterrows():
        for sentence_index, source_sentence in enumerate(sentence_units(chunk["chunk_text"])):
            if is_source_residue(source_sentence):
                continue
            clean_sentence = normalize_source_text(source_sentence)
            signature = normalise_signature(clean_sentence)
            if not signature:
                continue
            rows.append({
                "sentence_id": f"{chunk['chunk_id']}_sentence_{sentence_index:03d}",
                "sentence_index": int(sentence_index),
                "sentence_signature": signature,
                "source_sentence": source_sentence,
                "clean_sentence": clean_sentence,
                "cleaning_version": CLEANING_VERSION,
                "doc_id": chunk["doc_id"],
                "filename": chunk["filename"],
                "source_file": chunk["source_file"],
                "relative_source_file": chunk["relative_source_file"],
                "corpus": chunk["corpus"],
                "source_type": chunk["source_type"],
                "synthetic_type": chunk.get("synthetic_type", ""),
                "country": chunk.get("country", ""),
                "chunk_id": chunk["chunk_id"],
                "chunk_index": int(chunk["chunk_index"]),
                "heading_context": chunk.get("heading_context", ""),
            })

    inventory = pd.DataFrame(rows)
    if inventory.empty:
        raise ValueError("Shared cleaning produced an empty sentence inventory.")

    # Remove repetitions introduced by overlapping chunks, once and identically
    # for both downstream methods. Cross-document repetition remains visible.
    inventory = inventory.sort_values(
        ["doc_id", "chunk_index", "sentence_index", "sentence_id"]
    )
    inventory = inventory.drop_duplicates(
        subset=["doc_id", "sentence_signature"],
        keep="first",
    ).reset_index(drop=True)

    inventory["sentence_id"] = [
        f"clean_sentence_{index:06d}" for index in range(len(inventory))
    ]
    return inventory


def validate_clean_sentence_inventory(inventory: pd.DataFrame) -> pd.DataFrame:
    residue_mask = inventory["clean_sentence"].fillna("").map(is_source_residue)
    duplicate_mask = inventory.duplicated(["doc_id", "sentence_signature"])
    validation = pd.DataFrame([
        {
            "check": "sentence_rows",
            "value": len(inventory),
            "status": "passed" if len(inventory) > 0 else "failed",
        },
        {
            "check": "source_residue_rows",
            "value": int(residue_mask.sum()),
            "status": "passed" if not residue_mask.any() else "failed",
        },
        {
            "check": "within_document_duplicate_rows",
            "value": int(duplicate_mask.sum()),
            "status": "passed" if not duplicate_mask.any() else "failed",
        },
        {
            "check": "cleaning_version_values",
            "value": int(inventory["cleaning_version"].nunique()),
            "status": "passed" if inventory["cleaning_version"].nunique() == 1 else "failed",
        },
    ])
    return validation


def load_or_build_clean_sentence_inventory(
    chunks_path: Path,
    inventory_path: Path,
    metadata_path: Path,
    summary_path: Path,
    validation_path: Path,
    force_rebuild: bool = False,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    chunks_path = Path(chunks_path).resolve()
    inventory_path = Path(inventory_path).resolve()
    metadata_path = Path(metadata_path).resolve()
    summary_path = Path(summary_path).resolve()
    validation_path = Path(validation_path).resolve()
    inventory_path.parent.mkdir(parents=True, exist_ok=True)

    input_sha256 = sha256_file(chunks_path)
    expected = {
        "cleaning_version": CLEANING_VERSION,
        "chunks_all_sha256": input_sha256,
    }

    if not force_rebuild and inventory_path.exists() and metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if all(metadata.get(key) == value for key, value in expected.items()):
            inventory = pd.read_csv(inventory_path)
            validation = validate_clean_sentence_inventory(inventory)
            validation.to_csv(validation_path, index=False)
            if not validation["status"].eq("passed").all():
                raise ValueError("Cached shared sentence inventory failed validation.")
            return inventory, metadata

    chunks = pd.read_csv(chunks_path)
    inventory = build_clean_sentence_inventory(chunks)
    validation = validate_clean_sentence_inventory(inventory)
    if not validation["status"].eq("passed").all():
        raise ValueError(
            "Shared sentence inventory validation failed:\n"
            + validation.to_string(index=False)
        )

    summary = inventory.groupby(
        ["corpus", "source_type"],
        dropna=False,
        as_index=False,
    ).agg(
        clean_sentences=("sentence_id", "count"),
        documents=("doc_id", "nunique"),
        chunks=("chunk_id", "nunique"),
    )

    metadata = {
        **expected,
        "inventory_rows": int(len(inventory)),
        "inventory_sha256": hashlib.sha256(
            inventory.to_csv(index=False).encode("utf-8")
        ).hexdigest(),
        "shared_cleaning_source": "chunks_all.csv",
    }

    temporary_inventory = inventory_path.with_suffix(".tmp.csv")
    inventory.to_csv(temporary_inventory, index=False)
    os.replace(temporary_inventory, inventory_path)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    summary.to_csv(summary_path, index=False)
    validation.to_csv(validation_path, index=False)
    return inventory, metadata
