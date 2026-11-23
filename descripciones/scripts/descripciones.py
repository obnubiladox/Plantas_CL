#!/usr/bin/env python3
"""
Descripciones morfológicas de Plantas_CL: revisar, plantillas, índice y publicar.

Las descripciones viven en este repo, un archivo Markdown por especie en
`descripciones/Fichas/<N.° de ficha> <nombre>.md`. Este script es la única
lógica que las lee: lo usan los workflows de `.github/workflows/`
(`descripciones-*.yml`) y también se puede correr en un PC con el repo
clonado. Solo librería estándar (Python 3.10+).

Comandos:
    revisar      revisa un PR (formato, nombres, licencia) y deja anotaciones
    plantillas   crea las fichas que falten y renombra las que cambiaron de nombre
    indice       rehace descripciones/INDICE.md y descripciones/Familias/
    armar        arma los archivos de una publicación en una carpeta (sin GitHub)
    publicar     arma, crea el Release, actualiza Updates/descripciones.json y limpia

Formato que llega a la app (lo lee DescriptionPackage en la app):
    {"format": 1, "version": 20261215, "updated": "2026-12-15",
     "from": null | "<contentSha256 de la versión anterior>",
     "contentSha256": "<huella del resultado>",
     "entries": [{"id": 4534, "path": "descripciones/Fichas/4534 Vachellia caven.md", "text": "…"}],
     "removed": [123], "contributors": [{"name": "Ana Pérez", "login": "anaperez"}]}
`completo.json.gz` trae todas las fichas (las vacías sin "text"); cada
`cambios-<huella>.json.gz` solo lo que cambió desde esa versión.

El texto ("text") va en el formato interno de la app (DescriptionFormat):
bloques separados por una línea en blanco; `[[Título]]`, `[{Subtítulo}]`,
`{Fuente}`; listas con una línea por ítem ("- …" o "1. …"); `**negrita**`,
`*cursiva*` y `\\*` para un asterisco.
"""
from __future__ import annotations

import argparse
import datetime
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

FORMAT = 1
# Va al comienzo de la huella: un formato nuevo nunca coincide con uno viejo.
HASH_PREFIX = f"plantas-descripciones-{FORMAT}\n"
KEEP = 6                       # publicaciones anteriores con su archivo de cambios
TAG_PREFIX = "descripciones-"
TAG_RE = re.compile(r"^descripciones-(\d{8})$")
MAX_BYTES = 50 * 1024          # por ficha
CATALOG_MAX_ID = 1_000_000_000_000   # los ids sintéticos (sin URL udec) no tienen ficha
SAFE = re.compile(r'[<>:"/\\|?*]')
FILE_RE = re.compile(r"^(\d+) (.+)\.md$")
RANK_WORDS = {"subsp.", "ssp.", "var.", "subvar.", "f.", "fo.", "nothosubsp.", "nothovar."}
UA = "Plantas_CL-descripciones (+https://github.com/obnubiladox/Plantas_CL)"
MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre"]

ROOT = Path(__file__).resolve().parents[2]
REPO = os.environ.get("GITHUB_REPOSITORY", "obnubiladox/Plantas_CL")


def paths(root: Path):
    desc = root / "descripciones"
    return {
        "desc": desc, "fichas": desc / "Fichas", "familias": desc / "Familias",
        "indice": desc / "INDICE.md", "manifest": root / "Updates" / "descripciones.json",
        "catalog_manifest": root / "Updates" / "catalogo.json",
    }


# =========================================================================== utilidades
def say(text=""):
    print(text, flush=True)


def es_number(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def es_date(day: datetime.date) -> str:
    return f"{day.day} de {MONTHS[day.month - 1]} de {day.year}"


def today_chile() -> datetime.date:
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo("America/Santiago")).date()
    except Exception:  # noqa: BLE001  (sin tzdata)
        return (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)).date()


def fetch(url: str, headers=None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def gzip_bytes(data: bytes) -> bytes:
    """gzip sin fecha ni nombre: el mismo contenido da siempre el mismo archivo (y la misma huella)."""
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, compresslevel=9, mtime=0) as f:
        f.write(data)
    return buf.getvalue()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# Anotaciones de GitHub Actions: se ven en la pestaña "Files changed" del PR.
def _escape(value: str, prop=False) -> str:
    value = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    return value.replace(":", "%3A").replace(",", "%2C") if prop else value


def annotate(level: str, file: str | None, line: int | None, message: str):
    if os.environ.get("GITHUB_ACTIONS") == "true":
        props = []
        if file:
            props.append(f"file={_escape(file, True)}")
        if line:
            props.append(f"line={line}")
        print(f"::{level} {','.join(props)}::{_escape(message)}", flush=True)
    else:
        where = f"{file}:{line}" if file and line else (file or "")
        say(f"  {'ERROR' if level == 'error' else 'aviso'}: {where} {message}".rstrip())


def summary(text: str):
    """Resumen del job (se ve en la página de la ejecución y del chequeo)."""
    target = os.environ.get("GITHUB_STEP_SUMMARY")
    if target:
        with open(target, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        say(text)


def output(key: str, value: str):
    target = os.environ.get("GITHUB_OUTPUT")
    if target:
        with open(target, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")


# =========================================================================== catálogo
@dataclass(frozen=True)
class Species:
    id: int
    name: str
    family: str


def from_especie(especie: str) -> str | None:
    """SpeciesNames.fromEspecie de la app: género, epíteto y cada rango con su epíteto, sin autores."""
    words = [w for w in re.split(r"[ \n\t ]", especie or "") if w]
    if len(words) < 2:
        return None
    out = [words[0], words[1]]
    for i in range(2, len(words) - 1):
        if words[i] not in RANK_WORDS:
            continue
        nxt = words[i + 1]
        if nxt[0].islower() and all(c.isalpha() or c == "-" for c in nxt):
            out += [words[i], nxt]
    return " ".join(out)


def load_catalog(root: Path, db_path: str | None = None) -> dict[int, Species]:
    """Las especies de la base publicada (Updates/catalogo.json → catalogo.db.gz), o de una catalogo.db local."""
    tmp = None
    if db_path is None:
        m = json.loads(paths(root)["catalog_manifest"].read_text("utf-8"))
        data = fetch(m["db"])
        if m.get("dbSha256") and sha256(data) != m["dbSha256"]:
            raise SystemExit("La catalogo.db.gz publicada no coincide con su sha256 (Updates/catalogo.json).")
        tmp = Path(tempfile.mkdtemp()) / "catalogo.db"
        tmp.write_bytes(gzip.decompress(data))
        db_path = str(tmp)
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        out = {}
        for cid, especie, display, familia in con.execute(
                "SELECT catalogId, scientificName, displayName, familia FROM species WHERE catalogId < ?",
                (CATALOG_MAX_ID,)):
            name = from_especie(especie) or (display or "").strip() or str(cid)
            family = (familia or "").strip()
            out[int(cid)] = Species(int(cid), name, "Sin familia" if family in ("", "-", "--") else family)
        return out
    finally:
        con.close()
        if tmp:
            shutil.rmtree(tmp.parent, ignore_errors=True)


def expected_name(sp: Species) -> str:
    return f"{sp.id} {SAFE.sub('_', sp.name)}.md"


# =========================================================================== Markdown → formato interno
HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
QUOTE = re.compile(r"^ {0,3}>[ ]?(.*)$")
ITEM = re.compile(r"^ {0,3}([-+*]|\d{1,9}[.)])[ \t]+(.*)$")
RULE = re.compile(r"^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")
SETEXT = re.compile(r"^ {0,3}=+[ \t]*$")
FENCE = re.compile(r"^ {0,3}(```|~~~)")
TABLE = re.compile(r"^ {0,3}\|")
HYPHEN_END = re.compile(r"[^\W\d_]-$")
SPACES = re.compile(r"\s+")
PUNCT = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")

# Lo que GitHub mostraría distinto que la app, o que no se acepta (enlaces: spam).
FORBIDDEN = [
    (re.compile(r"`"), "Sin código (`): escribe el texto tal cual."),
    (re.compile(r"<[A-Za-z/!?]"), "Sin HTML (<…>)."),
    (re.compile(r"!\["), "Sin imágenes."),
    (re.compile(r"\]\(|\]\["), "Sin enlaces."),
    (re.compile(r"\[\^"), "Sin notas al pie: pon la fuente en su línea, con > Fuente: …"),
    (re.compile(r"(?i)\bhttps?://|\bwww\."), "Sin direcciones web."),
    (re.compile(r"\[\[|\]\]"), "Sin [[ ]]: usa ## para los títulos y ### para los subtítulos."),
    (re.compile(r"[{}]"), "Las llaves { } no se pueden usar: la fuente va en su línea, con > Fuente: …"),
    (re.compile(r"~~"), "Sin tachado (~~)."),
    (re.compile(r"&(?:#\d+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]*);"), "Sin entidades HTML (&…;): escribe el carácter."),
]


def join_lines(lines: list[str]) -> str:
    """Las líneas de un párrafo en una: espacios simples y la palabra cortada con guion, junta."""
    para = ""
    for raw in lines:
        line = SPACES.sub(" ", raw).strip()
        if not line:
            continue
        if not para:
            para = line
        elif HYPHEN_END.search(para) and line[:1].islower():
            para = para[:-1] + line
        else:
            para += " " + line
    return para


def inline(text: str, line: int, problems: list) -> str:
    """Cursiva y negrita de Markdown (* o _) a las del formato interno (* y **); el resto, literal."""
    for pattern, message in FORBIDDEN:
        if pattern.search(text):
            problems.append((line, message))
    out: list[str] = []
    stack: list[tuple[str, str, int]] = []   # (i | b, carácter, posición en out)
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\":
            nxt = text[i + 1] if i + 1 < n else ""
            if nxt in PUNCT and nxt:
                out.append("\\*" if nxt == "*" else "\\\\" if nxt == "\\" else nxt)
                i += 2
            else:
                out.append("\\\\")       # GitHub lo muestra tal cual
                i += 1
            continue
        if c not in "*_":
            out.append(c)
            i += 1
            continue
        j = i
        while j < n and text[j] == c:
            j += 1
        run = j - i
        prev = text[i - 1] if i > 0 else " "
        nxt = text[j] if j < n else " "
        can_open = not nxt.isspace()
        can_close = not prev.isspace()
        if c == "_":                 # un _ dentro de una palabra no es cursiva
            can_open = can_open and not prev.isalnum()
            can_close = can_close and not nxt.isalnum()
        literal = ("\\*" if c == "*" else "_") * run
        i = j
        if run > 3:
            out.append(literal)
            continue
        kinds = {1: ["i"], 2: ["b"], 3: ["b", "i"]}[run]
        top = [k for k, ch, _ in stack[-len(kinds):] if ch == c] if len(stack) >= len(kinds) else []
        if can_close and sorted(top) == sorted(kinds) and len(top) == len(kinds):
            for _ in kinds:
                stack.pop()
            out.append("*" * run)
        elif can_open:
            for k in kinds:
                stack.append((k, c, len(out)))
                out.append("**" if k == "b" else "*")
        else:
            out.append(literal)
    # Lo que quedó abierto se ve literal en GitHub: igual en la app.
    for k, c, pos in stack:
        out[pos] = ("\\*" if c == "*" else "_") * (2 if k == "b" else 1)
    return "".join(out)


def convert(md: str) -> tuple[str, list[tuple[int, str]]]:
    """Markdown de una ficha → (texto interno, problemas [(línea, mensaje)]). Texto vacío = sin descripción."""
    problems: list[tuple[int, str]] = []
    text = unicodedata.normalize("NFC", md).lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    blocks: list[str] = []
    kind: str | None = None     # p (párrafo), l (lista), q (fuente)
    buf: list = []
    start = 0
    seen = False

    def flush():
        nonlocal kind, buf
        if kind == "p":
            value = inline(join_lines(buf), start, problems)
            if value:
                blocks.append(value)
        elif kind == "l":
            items = []
            for marker, lines, at in buf:
                value = inline(join_lines(lines), at, problems)
                if value:
                    items.append(f"{marker} {value}")
            if items:
                blocks.append("\n".join(items))
        elif kind == "q":
            value = inline(join_lines(buf), start, problems)
            if value:
                blocks.append("{" + value + "}")
        kind, buf = None, []

    for number, raw in enumerate(text.split("\n"), 1):
        line = raw.replace("\t", "    ")
        if not line.strip():
            flush()
            continue
        if FENCE.match(line):
            problems.append((number, "Sin bloques de código (``` o ~~~)."))
            flush()
            continue
        h = HEADING.match(line)
        if h:
            flush()
            level, content = len(h.group(1)), (h.group(2) or "").strip()
            if level == 1:
                if seen:
                    problems.append((number, "El # va solo en la primera línea (el nombre): usa ## para un título y ### para un subtítulo."))
            elif level in (2, 3):
                value = inline(join_lines([content]), number, problems)
                if value:
                    blocks.append(("[[" + value + "]]") if level == 2 else ("[{" + value + "}]"))
            else:
                problems.append((number, "Solo hay dos niveles: ## para los títulos y ### para los subtítulos."))
            seen = True
            continue
        seen = True
        if line.lstrip().startswith("#"):
            problems.append((number, "Después de # va un espacio (## Título)."))
            continue
        if SETEXT.match(line) or RULE.match(line):
            problems.append((number, "Una línea de solo guiones, asteriscos, _ o = se ve distinto en GitHub: bórrala."))
            continue
        if TABLE.match(line):
            problems.append((number, "Sin tablas."))
            continue
        q = QUOTE.match(line)
        if q:
            if kind != "q":
                flush()
                kind, start = "q", number
            buf.append(q.group(1))
            continue
        item = ITEM.match(line)
        if item:
            if kind != "l":
                flush()
                kind, start = "l", number
            marker = item.group(1)
            marker = "-" if marker in "-+*" else marker[:-1] + "."
            buf.append([marker, [item.group(2)], number])
            continue
        indent = len(line) - len(line.lstrip(" "))
        if kind is None and indent >= 4:
            problems.append((number, "Una línea con sangría de 4 espacios se ve como código en GitHub: quita la sangría."))
            continue
        if kind == "l":
            buf[-1][1].append(line)       # el ítem sigue en esta línea
        elif kind == "q":
            buf.append(line)
        else:
            if kind != "p":
                flush()
                kind, start = "p", number
            buf.append(line)
    flush()
    return "\n\n".join(blocks), problems


# =========================================================================== fichas
@dataclass
class Ficha:
    id: int
    path: str          # desde la raíz del repo, con /
    name: str          # el nombre en el archivo
    file: Path


def list_fichas(root: Path, problems: list) -> dict[int, Ficha]:
    """Las fichas de descripciones/Fichas por N.°. problems recibe (archivo, línea, mensaje)."""
    folder = paths(root)["fichas"]
    out: dict[int, Ficha] = {}
    if not folder.is_dir():
        return out
    for entry in sorted(folder.iterdir(), key=lambda p: p.name):
        rel = entry.relative_to(root).as_posix()
        if entry.is_dir():
            problems.append((rel, None, "Fichas no lleva subcarpetas: todas las fichas van juntas."))
            continue
        m = FILE_RE.match(entry.name)
        if not m:
            problems.append((rel, None, "El nombre tiene que ser «<N.° de ficha> <nombre>.md», por ejemplo «4534 Vachellia caven.md»."))
            continue
        cid = int(m.group(1))
        if cid in out:
            problems.append((rel, None, f"El N.° {cid} ya está en {out[cid].path}: cada especie tiene una sola ficha."))
            continue
        out[cid] = Ficha(cid, rel, m.group(2), entry)
    return out


def read_ficha(ficha: Ficha) -> tuple[str, list[tuple[int, str]]]:
    data = ficha.file.read_bytes()
    if len(data) > MAX_BYTES:
        return "", [(1, f"La ficha pasa de {MAX_BYTES // 1024} KB.")]
    try:
        md = data.decode("utf-8")
    except UnicodeDecodeError:
        return "", [(1, "El archivo no está en UTF-8: guárdalo como UTF-8.")]
    return convert(md)


def content_hash(entries: dict[int, tuple[str, str | None]]) -> str:
    """Huella de todo (ids, rutas y textos), la misma que calcula la app (DescriptionPackage.contentHash)."""
    h = hashlib.sha256(HASH_PREFIX.encode())
    for cid in sorted(entries):
        path, text = entries[cid]
        h.update(f"{cid}\t{path}\t{text or ''}\n".encode())
    return h.hexdigest()


def build_entries(root: Path, catalog: dict[int, Species] | None) -> tuple[dict, list]:
    """Todas las fichas convertidas: ({id: (ruta, texto o None)}, problemas). Sin catálogo no se revisan los N.°."""
    problems: list = []
    fichas = list_fichas(root, problems)
    entries = {}
    for cid, f in fichas.items():
        if catalog is not None and cid not in catalog:
            annotate("warning", f.path, None, f"El N.° {cid} no está en el catálogo: no se publica.")
            continue
        text, probs = read_ficha(f)
        problems += [(f.path, line, msg) for line, msg in probs]
        entries[cid] = (f.path, text or None)
    return entries, problems


# =========================================================================== índice
def write_index(root: Path, catalog: dict[int, Species], fichas: dict[int, Ficha], with_text: set[int], when: datetime.date):
    p = paths(root)
    by_family: dict[str, list[Species]] = {}
    for sp in catalog.values():
        by_family.setdefault(sp.family, []).append(sp)
    if p["familias"].exists():
        shutil.rmtree(p["familias"])
    p["familias"].mkdir(parents=True)
    rows = []
    for family in sorted(by_family, key=str.lower):
        species = sorted(by_family[family], key=lambda s: s.name.lower())
        done = sum(1 for s in species if s.id in with_text)
        page = SAFE.sub("_", family) + ".md"
        lines = [f"# {family}", "",
                 f"[← Índice](../INDICE.md) · {es_number(done)} de {es_number(len(species))} "
                 f"{'especie' if len(species) == 1 else 'especies'} con descripción.", ""]
        for s in species:
            f = fichas.get(s.id)
            mark = "✅" if s.id in with_text else "⬜"
            if f:
                link = "../Fichas/" + urllib.parse.quote(f.file.name)
                lines.append(f"- {mark} [{s.name}]({link}) · {s.id}")
            else:
                lines.append(f"- {mark} {s.name} · {s.id} (sin ficha todavía)")
        (p["familias"] / page).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        rows.append(f"| [{family}](Familias/{urllib.parse.quote(page)}) | {es_number(done)} | {es_number(len(species))} |")
    total, done = len(catalog), sum(1 for cid in catalog if cid in with_text)
    orphans = sorted(cid for cid in fichas if cid not in catalog)
    lines = [
        "# Índice de las descripciones", "",
        f"**{es_number(done)} de {es_number(total)} especies** tienen descripción (al {es_date(when)}).", "",
        "Busca la especie en su familia y toca su nombre; después, el lápiz (✏️) para escribir o mejorar "
        "la descripción. También puedes buscarla por nombre o número con la tecla `t` en la página del repo. "
        "Antes de escribir, lee [cómo escribir una descripción](CONTRIBUTING.md).", "",
        "| Familia | Con descripción | Especies |", "|---|---:|---:|", *rows,
    ]
    if orphans:
        lines += ["", "## Fichas de especies que ya no están en el catálogo", "",
                  *[f"- [{fichas[cid].file.name}](Fichas/{urllib.parse.quote(fichas[cid].file.name)})" for cid in orphans]]
    p["indice"].write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


# =========================================================================== paquetes
def package(version: int, updated: str, base: str | None, target: str, entries: dict, ids, removed, contributors) -> bytes:
    obj = {
        "format": FORMAT, "version": version, "updated": updated, "from": base, "contentSha256": target,
        "entries": [dict(id=cid, path=entries[cid][0], **({"text": entries[cid][1]} if entries[cid][1] else {}))
                    for cid in sorted(ids)],
        "removed": sorted(removed), "contributors": contributors,
    }
    return gzip_bytes(json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode())


def read_package(data: bytes) -> tuple[dict, dict]:
    """Un completo.json.gz → (cabecera, {id: (ruta, texto)})."""
    obj = json.loads(gzip.decompress(data))
    entries = {int(e["id"]): (e["path"], e.get("text") or None) for e in obj.get("entries", [])}
    return obj, entries


@dataclass
class Previous:
    version: int
    hash: str
    entries: dict


def build_release(out: Path, entries: dict, version: int, updated: str, previous: list[Previous],
                  contributors: list, notes: str, base_url: str) -> dict:
    """Escribe completo.json.gz, un cambios-<huella>.json.gz por versión anterior y descripciones.json en out."""
    out.mkdir(parents=True, exist_ok=True)
    target = content_hash(entries)
    full = package(version, updated, None, target, entries, entries.keys(), [], contributors)
    (out / "completo.json.gz").write_bytes(full)
    changes = []
    for prev in previous:
        if prev.hash == target or any(c["from"] == prev.hash for c in changes):
            continue
        changed = [cid for cid in entries if prev.entries.get(cid) != entries[cid]]
        removed = [cid for cid in prev.entries if cid not in entries]
        data = package(version, updated, prev.hash, target, entries, changed, removed, contributors)
        name = f"cambios-{prev.hash[:12]}.json.gz"
        (out / name).write_bytes(data)
        changes.append({"from": prev.hash, "version": prev.version, "url": f"{base_url}/{name}",
                        "sha256": sha256(data), "bytes": len(data), "entries": len(changed) + len(removed)})
    manifest = {
        "format": FORMAT, "version": version, "updated": updated, "contentSha256": target,
        "rows": sum(1 for _, text in entries.values() if text), "species": len(entries),
        "notes": notes,
        "full": {"url": f"{base_url}/completo.json.gz", "sha256": sha256(full), "bytes": len(full)},
        "changes": changes,
    }
    (out / "descripciones.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


# =========================================================================== GitHub
def gh(*args, check=True, capture=True) -> str:
    r = subprocess.run(["gh", *args], check=check, capture_output=capture, text=True)
    return r.stdout if capture else ""


def git(root: Path, *args, check=True) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=check, capture_output=True, text=True).stdout


def api(path: str) -> object:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return json.loads(fetch(f"https://api.github.com{path}", headers))


def contributors() -> list[dict]:
    """Quienes hicieron commits en las fichas (los PR unidos con squash quedan a nombre de quien los propuso), sin bots."""
    counts: dict[str, int] = {}
    page = 1
    while True:
        batch = api(f"/repos/{REPO}/commits?path=descripciones/Fichas&per_page=100&page={page}")
        for c in batch:
            author = c.get("author") or {}
            login = author.get("login")
            if login and author.get("type") != "Bot" and not login.endswith("[bot]"):
                counts[login] = counts.get(login, 0) + 1
        if len(batch) < 100:
            break
        page += 1
    people = []
    for login, n in counts.items():
        name = (api(f"/users/{login}").get("name") or "").strip() or login
        people.append((-n, name.lower(), {"name": name, "login": login}))
    return [p for _, _, p in sorted(people, key=lambda x: (x[0], x[1]))]


def published_tags() -> list[str]:
    """Etiquetas de las publicaciones de descripciones, de la más nueva a la más vieja."""
    data = json.loads(gh("release", "list", "--repo", REPO, "--limit", "200", "--json", "tagName"))
    return sorted((r["tagName"] for r in data if TAG_RE.match(r["tagName"])), reverse=True)


# =========================================================================== comandos
def cmd_revisar(root: Path, base: str | None, autor: str, dueno: str, catalog_db: str | None) -> int:
    owner = bool(autor) and autor.lower() == dueno.lower()
    if base:
        # -z y sin quotepath: los nombres con espacios, tildes o × llegan tal cual.
        parts = git(root, "-c", "core.quotepath=false", "diff", "--name-status", "--no-renames", "-z", base, "HEAD").split("\0")
        changed = [(parts[i][0], parts[i + 1]) for i in range(0, len(parts) - 1, 2) if parts[i]]
    else:
        changed = [("M", f.relative_to(root).as_posix()) for f in sorted(paths(root)["fichas"].glob("*"))]
    in_fichas = [(s, p) for s, p in changed if p.startswith("descripciones/Fichas/")]
    outside = [p for s, p in changed if not p.startswith("descripciones/Fichas/")]
    errors = 0

    def error(file, line, msg):
        nonlocal errors
        errors += 1
        annotate("error", file, line, msg)

    if outside and not owner:
        for p in outside:
            error(p, None, "Las propuestas solo pueden cambiar archivos de descripciones/Fichas/.")
    if not in_fichas:
        summary("### Revisión de descripciones\n\nEste cambio no toca las fichas." +
                ("" if not errors else f"\n\n**{errors} problemas.**"))
        return 1 if errors else 0

    for status, p in in_fichas:
        if status == "D" and not owner:
            error(p, None, "No se borran fichas: para quitar una descripción, deja el archivo solo con su primera línea (# …).")

    if not owner:
        body = os.environ.get("PR_BODY") or ""
        checked = len(re.findall(r"^\s*[-*] \[[xX]\]", body, re.M))
        if checked < 3 or re.search(r"^\s*[-*] \[ \]", body, re.M):
            error(None, None, "Marca las tres casillas de la descripción del PR (texto propio, licencia CC0 y créditos). "
                              "Puedes editar la descripción del PR y la revisión se vuelve a correr sola.")

    catalog = load_catalog(root, catalog_db)
    listing: list = []
    fichas = list_fichas(root, listing)
    touched = {p for s, p in in_fichas if s != "D"}
    for file, line, msg in listing:
        if file in touched:
            error(file, line, msg)
    checked_files = 0
    for f in fichas.values():
        if f.path not in touched:
            continue
        checked_files += 1
        sp = catalog.get(f.id)
        if sp is None:
            error(f.path, None, f"El N.° {f.id} no está en el catálogo.")
            continue
        if f.file.name != expected_name(sp):
            annotate("warning", f.path, None, f"En el catálogo se llama «{sp.name}»: el nombre del archivo se corrige solo.")
        _, problems = read_ficha(f)
        for line, msg in problems:
            error(f.path, line, msg)
    summary(f"### Revisión de descripciones\n\n{checked_files} fichas revisadas: " +
            ("todo bien. 🌱" if not errors else f"**{errors} problemas** (ver las anotaciones en «Files changed»)."))
    return 1 if errors else 0


def cmd_plantillas(root: Path, catalog_db: str | None) -> int:
    p = paths(root)
    catalog = load_catalog(root, catalog_db)
    problems: list = []
    fichas = list_fichas(root, problems)
    for file, line, msg in problems:
        annotate("error", file, line, msg)
    if problems:
        return 1
    p["fichas"].mkdir(parents=True, exist_ok=True)
    in_git = (root / ".git").exists()
    created = renamed = 0
    for sp in sorted(catalog.values(), key=lambda s: s.id):
        name = expected_name(sp)
        f = fichas.get(sp.id)
        if f is None:
            (p["fichas"] / name).write_text(f"# {sp.name}\n", encoding="utf-8", newline="\n")
            created += 1
            continue
        if f.file.name == name:
            continue
        target = p["fichas"] / name
        if in_git:
            git(root, "mv", f.file.relative_to(root).as_posix(), target.relative_to(root).as_posix())
        else:
            f.file.rename(target)
        text = target.read_text("utf-8")
        lines = text.split("\n", 1)
        if lines[0].startswith("# "):        # el nombre de la primera línea también
            target.write_text(f"# {sp.name}\n" + (lines[1] if len(lines) > 1 else ""), encoding="utf-8", newline="\n")
        renamed += 1
    orphans = sorted(cid for cid in fichas if cid not in catalog)
    for cid in orphans:
        annotate("warning", fichas[cid].path, None, f"El N.° {cid} ya no está en el catálogo (no se borra: decide tú).")
    fichas = list_fichas(root, [])
    with_text = {cid for cid, f in fichas.items() if read_ficha(f)[0]}
    write_index(root, catalog, fichas, with_text, today_chile())
    summary(f"### Plantillas\n\n{es_number(created)} fichas nuevas, {es_number(renamed)} renombradas"
            f"{f', {len(orphans)} sin especie en el catálogo' if orphans else ''}.")
    return 0


def cmd_indice(root: Path, catalog_db: str | None) -> int:
    catalog = load_catalog(root, catalog_db)
    fichas = list_fichas(root, [])
    with_text = {cid for cid, f in fichas.items() if read_ficha(f)[0]}
    write_index(root, catalog, fichas, with_text, today_chile())
    say(f"Índice: {len(with_text)} de {len(catalog)} especies con descripción.")
    return 0


def check_all(root: Path, catalog: dict | None) -> dict | None:
    entries, problems = build_entries(root, catalog)
    for file, line, msg in problems:
        annotate("error", file, line, msg)
    if problems:
        summary(f"### Descripciones\n\n**{len(problems)} problemas**: no se publicó nada.")
        return None
    return entries


def cmd_armar(root: Path, out: Path, previous_files: list[str], version: int | None, updated: str | None,
              notes: str, catalog_db: str | None, base_url: str, no_catalog: bool) -> int:
    """Lo mismo que publicar, pero en una carpeta y sin tocar GitHub (pruebas)."""
    catalog = None if no_catalog else load_catalog(root, catalog_db)
    entries = check_all(root, catalog)
    if entries is None:
        return 1
    day = datetime.date.fromisoformat(updated) if updated else today_chile()
    previous = []
    for file in previous_files:
        head, prev_entries = read_package(Path(file).read_bytes())
        previous.append(Previous(int(head["version"]), content_hash(prev_entries), prev_entries))
    m = build_release(out, entries, version or int(day.strftime("%Y%m%d")), day.isoformat(), previous,
                      [], notes, base_url)
    say(f"{out}: {m['rows']} con texto de {m['species']}, {len(m['changes'])} archivos de cambios.")
    return 0


def cmd_publicar(root: Path, notes: str, catalog_db: str | None) -> int:
    p = paths(root)
    catalog = load_catalog(root, catalog_db)
    entries = check_all(root, catalog)
    if entries is None:
        return 1
    target = content_hash(entries)
    current = json.loads(p["manifest"].read_text("utf-8")) if p["manifest"].exists() else {}
    if current.get("contentSha256") == target:
        summary("### Descripciones\n\nNada cambió desde la última publicación: no se publicó nada.")
        output("publicado", "false")
        return 0

    day = today_chile()
    version = int(day.strftime("%Y%m%d"))
    tag = f"{TAG_PREFIX}{version}"
    base_url = f"https://github.com/{REPO}/releases/download/{tag}"
    tags = published_tags()
    work = Path(tempfile.mkdtemp())
    previous = []
    # Las publicaciones anteriores (también la de hoy, si se publica dos veces):
    # su completo da la base de cada archivo de cambios.
    for old in tags[:KEEP]:
        try:
            gh("release", "download", old, "--repo", REPO, "--pattern", "completo.json.gz",
               "--output", str(work / f"{old}.json.gz"), "--clobber")
        except subprocess.CalledProcessError:
            annotate("warning", None, None, f"{old} no tiene completo.json.gz: sin archivo de cambios desde esa versión.")
            continue
        head, old_entries = read_package((work / f"{old}.json.gz").read_bytes())
        previous.append(Previous(int(head["version"]), content_hash(old_entries), old_entries))

    people = contributors()
    out = work / "salida"
    manifest = build_release(out, entries, version, day.isoformat(), previous, people, notes, base_url)
    files = [str(out / "completo.json.gz"), *(str(out / c["url"].rsplit("/", 1)[1]) for c in manifest["changes"])]
    if tag in tags:      # segunda publicación del mismo día: reemplaza a la primera
        gh("release", "delete", tag, "--repo", REPO, "--yes", "--cleanup-tag")
    head_sha = git(root, "rev-parse", "HEAD").strip()
    gh("release", "create", tag, *files, "--repo", REPO, "--target", head_sha, "--latest=false",
       "--title", f"Descripciones del {es_date(day)}",
       "--notes", (notes + "\n\n" if notes else "") +
       f"{es_number(manifest['rows'])} de {es_number(manifest['species'])} especies con descripción.")

    # Recién con el Release listo: el manifest y el índice.
    shutil.copy2(out / "descripciones.json", p["manifest"])
    fichas = list_fichas(root, [])
    write_index(root, catalog, fichas, {cid for cid, (_, text) in entries.items() if text}, day)
    git(root, "add", "Updates/descripciones.json", "descripciones/INDICE.md", "descripciones/Familias")
    git(root, "commit", "-m", f"Descripciones del {es_date(day)}")
    for attempt in range(3):
        if subprocess.run(["git", "-C", str(root), "push"], capture_output=True).returncode == 0:
            break
        git(root, "pull", "--rebase")
    else:
        raise SystemExit("No se pudo subir Updates/descripciones.json: el Release quedó creado; vuelve a publicar.")

    # Se guardan la nueva y las KEEP anteriores.
    for old in [t for t in published_tags() if t != tag][KEEP:]:
        gh("release", "delete", old, "--repo", REPO, "--yes", "--cleanup-tag", check=False)
    summary(f"### Descripciones del {es_date(day)}\n\n"
            f"- {es_number(manifest['rows'])} de {es_number(manifest['species'])} especies con descripción.\n"
            f"- Completo: {manifest['full']['bytes'] / 1e6:.1f} MB.\n"
            + "".join(f"- Cambios desde {c['version']}: {c['entries']} fichas, {c['bytes'] / 1024:.0f} KB.\n"
                      for c in manifest["changes"])
            + f"- {len(people)} personas en los créditos.")
    output("publicado", "true")
    shutil.rmtree(work, ignore_errors=True)
    return 0


def main(argv=None) -> int:
    # Los mensajes llevan tildes: en una consola de Windows salían mal.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--raiz", default=str(ROOT), help="raíz del repo (por defecto, la de este script)")
    ap.add_argument("--catalogo", help="una catalogo.db local en vez de la publicada")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("revisar")
    s.add_argument("--base", help="commit base del PR (sin él, revisa todas las fichas)")
    s.add_argument("--autor", default="")
    s.add_argument("--dueno", default=REPO.split("/")[0])
    sub.add_parser("plantillas")
    sub.add_parser("indice")
    s = sub.add_parser("armar")
    s.add_argument("--salida", required=True)
    s.add_argument("--anterior", action="append", default=[], help="completo.json.gz de una versión anterior")
    s.add_argument("--version", type=int)
    s.add_argument("--fecha", help="AAAA-MM-DD")
    s.add_argument("--notas", default="")
    s.add_argument("--url", default=f"https://github.com/{REPO}/releases/download/{TAG_PREFIX}prueba")
    s.add_argument("--sin-catalogo", action="store_true", help="no revisa los N.° contra el catálogo")
    s = sub.add_parser("publicar")
    s.add_argument("--notas", default="")
    a = ap.parse_args(argv)
    root = Path(a.raiz).resolve()
    if a.cmd == "revisar":
        return cmd_revisar(root, a.base, a.autor, a.dueno, a.catalogo)
    if a.cmd == "plantillas":
        return cmd_plantillas(root, a.catalogo)
    if a.cmd == "indice":
        return cmd_indice(root, a.catalogo)
    if a.cmd == "armar":
        return cmd_armar(root, Path(a.salida), a.anterior, a.version, a.fecha, a.notas, a.catalogo, a.url, a.sin_catalogo)
    return cmd_publicar(root, a.notas.strip(), a.catalogo)


if __name__ == "__main__":
    sys.exit(main())
