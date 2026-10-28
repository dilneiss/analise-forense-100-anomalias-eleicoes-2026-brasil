"""Descoberta de arquivos e identificacao de tipo por conteudo.

Nada aqui abre um arquivo para escrita. O scanner tambem nao segue links
simbolicos, para nao sair da arvore de evidencia.
"""

from __future__ import annotations

import hashlib
import itertools
import os
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

from .crypto.hashes import hash_file
from .models import EvidenceFile, UrnaKey

# ``o03220sc8053500440144-bu.dat``:
#   1 letra + 5 digitos + UF(2) + municipio TSE(5) + zona(4) + secao(4) + tipo
NAME_RE = re.compile(
    r"^(?P<prefix>[a-z]\d{5})(?P<uf>[a-z]{2})(?P<municipio>\d{5})"
    r"(?P<zona>\d{4})(?P<secao>\d{4})-(?P<kind>[a-z0-9]+)\.(?P<ext>[a-z0-9]+)$",
    re.IGNORECASE,
)

_MAGIC = (
    (b"PK\x03\x04", "zip"),
    (b"PK\x05\x06", "zip-vazio"),
    (b"7z\xbc\xaf\x27\x1c", "7z"),
    (b"Rar!\x1a\x07", "rar"),
    (b"%PDF", "pdf"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpeg"),
    (b"GIF8", "gif"),
    (b"BM", "bmp"),
    (b"II*\x00", "tiff"),
    (b"MM\x00*", "tiff"),
    (b"\x1f\x8b", "gzip"),
    (b"\xfd7zXZ\x00", "xz"),
)

LOG_LINE_RE = re.compile(
    rb"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\t"
)


@dataclass
class ScanResult:
    files: list[EvidenceFile] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    skipped_symlinks: int = 0
    total_bytes: int = 0
    root: Optional[Path] = None


def parse_name(name: str) -> Optional[tuple[UrnaKey, str]]:
    """Extrai (urna, tipo) do nome no padrao do TSE, ou ``None``."""
    match = NAME_RE.match(name)
    if not match:
        return None
    urna = UrnaKey(
        uf=match.group("uf").lower(),
        municipio=int(match.group("municipio")),
        zona=int(match.group("zona")),
        secao=int(match.group("secao")),
    )
    return urna, match.group("kind").lower()


def detect_type(head: bytes, name: str = "") -> str:
    """Tipo pelo conteudo; a extensao e apenas um desempate documentado."""
    if not head:
        return "vazio"
    for magic, label in _MAGIC:
        if head.startswith(magic):
            return label
    if LOG_LINE_RE.search(head[:8192]):
        return "log-texto"
    if head[0] == 0x30 and len(head) > 2:
        if head[1] < 0x80 or head[1] in (0x81, 0x82, 0x83, 0x84):
            try:
                from .der import _read_length, _read_tag

                _, _, _, after_tag = _read_tag(head, 0)
                length, _ = _read_length(head, after_tag)
                if length >= 0:
                    return "asn1-ber"
            except Exception:
                pass
    sample = head[:8192]
    printable = sum(
        1 for byte in sample
        if byte in (9, 10, 13) or 32 <= byte <= 126 or byte >= 0xA0
    )
    if printable / len(sample) >= 0.90:
        return "texto"
    return "binario"


def iter_files(root: Path, exclude: Optional[Path] = None) -> Iterator[Path]:
    """Percorre a arvore sem seguir links simbolicos."""
    root = root.resolve()
    exclude = exclude.resolve() if exclude else None
    stack = [root]
    while stack:
        directory = stack.pop()
        try:
            entries = list(os.scandir(directory))
        except OSError:
            continue
        for entry in entries:
            path = Path(entry.path)
            if exclude and (path == exclude or exclude in path.parents):
                continue
            if entry.is_symlink():
                continue
            if entry.is_dir(follow_symlinks=False):
                stack.append(path)
            elif entry.is_file(follow_symlinks=False):
                yield path

def _process_file(
    path: Path,
    root: Path,
    compute_hashes: bool,
    hash_filter: Optional[set[Path]],
) -> tuple[Optional[EvidenceFile], Optional[str], bool, int]:
    try:
        stat = path.stat()
    except OSError as exc:
        return None, f"nao foi possivel ler metadados de {path}: {exc}", False, 0
    if path.is_symlink():
        return None, None, True, 0

    should_hash = compute_hashes and (hash_filter is None or path in hash_filter)
    hashes = {"sha256": "", "sha512": ""}
    head = b""
    try:
        if stat.st_size <= 8 * 1024 * 1024:
            with open(path, "rb") as handle:
                data = handle.read()
            head = data[:8192]
            if should_hash:
                hashes["sha256"] = hashlib.sha256(data).hexdigest()
                hashes["sha512"] = hashlib.sha512(data).hexdigest()
        else:
            with open(path, "rb") as handle:
                head = handle.read(8192)
            if should_hash:
                hashes = hash_file(path)
    except OSError as exc:
        return None, f"nao foi possivel ler {path}: {exc}", False, 0

    relative = path.relative_to(root).as_posix()
    parsed = parse_name(path.name)
    urna, kind = (parsed if parsed else (None, None))
    detected = detect_type(head, path.name)
    ev = EvidenceFile(
        relpath=relative,
        size=stat.st_size,
        sha256=hashes["sha256"],
        sha512=hashes["sha512"],
        ext=path.suffix.lower(),
        detected_type=detected,
        mtime_ns=stat.st_mtime_ns,
        urna=urna,
        kind=kind,
        magic=head[:16].hex(" "),
        abs_path=path,
    )
    return ev, None, False, stat.st_size


def scan(
    root: Path,
    *,
    exclude: Optional[Path] = None,
    compute_hashes: bool = True,
    hash_filter: Optional[set[Path]] = None,
    progress=None,
    max_workers: int = 32,
) -> ScanResult:
    """Inventaria a arvore de evidencia concorrentemente.

    ``hash_filter`` limita o calculo de hash a um conjunto de caminhos
    absolutos (usado por ``--hash-scope target``); nesse caso os demais
    arquivos aparecem no inventario sem hash, e o manifesto declara o escopo.
    """
    root = root.resolve()
    result = ScanResult(root=root)
    all_paths = sorted(iter_files(root, exclude))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(
            _process_file,
            all_paths,
            itertools.repeat(root),
            itertools.repeat(compute_hashes),
            itertools.repeat(hash_filter),
        )
        for count, (ev, note, skipped_symlink, sz) in enumerate(results, start=1):
            if note:
                result.notes.append(note)
            if skipped_symlink:
                result.skipped_symlinks += 1
            if ev:
                result.files.append(ev)
                result.total_bytes += sz
            if progress and count % 5000 == 0:
                progress(count, result.total_bytes)

    if result.skipped_symlinks:
        result.notes.append(
            f"{result.skipped_symlinks} link(s) simbolico(s) ignorado(s)"
        )
    return result


def scan_target(
    root: Path,
    pattern: str,
    *,
    exclude: Optional[Path] = None,
) -> ScanResult:
    """Modo rapido: localiza diretamente apenas os arquivos da urna alvo."""
    root = root.resolve()
    result = ScanResult(root=root)
    matched_paths: list[Path] = []
    pattern_lower = pattern.lower()
    stack = [root]
    while stack:
        directory = stack.pop()
        try:
            entries = list(os.scandir(directory))
        except OSError:
            continue
        for entry in entries:
            path = Path(entry.path)
            if exclude and (path == exclude or exclude in path.parents):
                continue
            if entry.is_symlink():
                continue
            if entry.is_dir(follow_symlinks=False):
                stack.append(path)
            elif entry.is_file(follow_symlinks=False):
                if pattern_lower in entry.name.lower():
                    matched_paths.append(path)
    for path in sorted(matched_paths):
        ev, note, skipped, sz = _process_file(
            path, root, compute_hashes=True, hash_filter=None
        )
        if note:
            result.notes.append(note)
        if skipped:
            result.skipped_symlinks += 1
        if ev:
            result.files.append(ev)
            result.total_bytes += sz
    return result
def group_urnas(files: list[EvidenceFile]) -> dict[UrnaKey, dict[str, EvidenceFile]]:
    """Agrupa arquivos por urna; o tipo duplicado mantem o primeiro."""
    urnas: dict[UrnaKey, dict[str, EvidenceFile]] = {}
    for item in files:
        if item.urna is None or not item.kind:
            continue
        urnas.setdefault(item.urna, {})
        urnas[item.urna].setdefault(item.kind, item)
    return urnas


def select_urna(
    urnas: dict[UrnaKey, dict[str, EvidenceFile]],
    *,
    uf: Optional[str] = None,
    municipio: Optional[int] = None,
    zona: Optional[int] = None,
    secao: Optional[int] = None,
) -> list[UrnaKey]:
    matches = []
    for key in sorted(urnas, key=lambda k: (k.uf, k.municipio, k.zona, k.secao)):
        if uf and key.uf.lower() != uf.lower():
            continue
        if municipio is not None and key.municipio != municipio:
            continue
        if zona is not None and key.zona != zona:
            continue
        if secao is not None and key.secao != secao:
            continue
        matches.append(key)
    return matches
