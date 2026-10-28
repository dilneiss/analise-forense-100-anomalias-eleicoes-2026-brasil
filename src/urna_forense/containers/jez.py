"""Leitura de containers da urna (.jez) sem extrair sobre a evidencia.

O LEIA-ME oficial descreve o log como "empacotado num arquivo em formato
7z". Nos arquivos de 2026 observados o container e um ZIP (``PK\\x03\\x04``)
com uma entrada ``logd.dat``. A ferramenta identifica pelo conteudo, aceita
ZIP nativamente e 7z quando ``py7zr`` estiver instalado, e declara o que
encontrou em vez de supor.
"""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..crypto.hashes import hash_bytes
from ..models import ContainerEntry

MAX_ENTRY_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_DEPTH = 3


class ContainerError(RuntimeError):
    """Container reconhecido mas ilegivel (corrompido, cifrado, grande)."""


@dataclass
class ContainerInfo:
    format: str
    entries: list[ContainerEntry] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    source: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "container": self.format,
            "source": self.source,
            "entries": [entry.as_dict() for entry in self.entries],
            "notes": self.notes,
        }


@dataclass
class LogPayload:
    entry_path: str
    text: str
    size: int
    sha256: str

    def as_dict(self) -> dict[str, object]:
        return {
            "entry": self.entry_path,
            "size": self.size,
            "sha256": self.sha256,
        }


def detect_container(data: bytes) -> str:
    if data.startswith(b"PK\x03\x04") or data.startswith(b"PK\x05\x06"):
        return "zip"
    if data.startswith(b"7z\xbc\xaf\x27\x1c"):
        return "7z"
    if data.startswith(b"Rar!\x1a\x07"):
        return "rar"
    return "desconhecido"


def _zip_infos(handle: io.BufferedIOBase | bytes) -> list[zipfile.ZipInfo]:
    with zipfile.ZipFile(handle) as archive:
        return [info for info in archive.infolist() if not info.is_dir()]


def _read_zip_entry(handle, info: zipfile.ZipInfo) -> bytes:
    if info.flag_bits & 0x1:
        raise ContainerError(f"entrada cifrada: {info.filename}")
    if info.file_size > MAX_ENTRY_BYTES:
        raise ContainerError(
            f"entrada {info.filename} tem {info.file_size} bytes "
            f"(limite {MAX_ENTRY_BYTES})"
        )
    with zipfile.ZipFile(handle) as archive:
        return archive.read(info)


def list_container(raw: bytes, source: str = "", depth: int = 0) -> ContainerInfo:
    """Lista as entradas de um container (recursivo em containers aninhados)."""
    kind = detect_container(raw)
    info = ContainerInfo(format=kind, source=source)
    if kind == "zip":
        try:
            entries = _zip_infos(io.BytesIO(raw))
        except (zipfile.BadZipFile, OSError) as exc:
            raise ContainerError(f"ZIP ilegivel: {exc}") from exc
        total = 0
        for entry in entries:
            try:
                content = _read_zip_entry(io.BytesIO(raw), entry)
            except (ContainerError, zipfile.BadZipFile, OSError) as exc:
                info.notes.append(str(exc))
                continue
            total += len(content)
            if total > MAX_TOTAL_BYTES:
                raise ContainerError("conteudo descompactado acima do limite")
            nested = detect_container(content) in ("zip", "7z")
            info.entries.append(
                ContainerEntry(
                    name=entry.filename,
                    size=entry.file_size,
                    compressed_size=entry.compress_size,
                    crc32=entry.CRC,
                    sha256=hash_bytes(content, "sha256"),
                    is_nested_container=nested,
                    depth=depth,
                    date_time="%04d-%02d-%02dT%02d:%02d:%02d" % entry.date_time,
                )
            )
            if nested and depth + 1 < MAX_DEPTH:
                try:
                    child = list_container(
                        content, source=f"{source}!{entry.filename}", depth=depth + 1
                    )
                except ContainerError as exc:
                    info.notes.append(f"{entry.filename}: {exc}")
                    continue
                for child_entry in child.entries:
                    child_entry.name = f"{entry.filename}!{child_entry.name}"
                    info.entries.append(child_entry)
                info.notes.extend(child.notes)
        return info
    if kind == "7z":
        try:
            import py7zr  # type: ignore
        except ImportError:
            info.notes.append(
                "container 7z detectado; instale 'py7zr' para leitura nativa "
                "(o LEIA-ME cita 7z, mas os arquivos de 2026 observados sao ZIP)"
            )
            return info
        try:
            with py7zr.SevenZipFile(io.BytesIO(raw)) as archive:
                for item in archive.list():
                    if item.is_directory:
                        continue
                    info.entries.append(
                        ContainerEntry(
                            name=item.filename,
                            size=item.uncompressed or 0,
                            compressed_size=item.compressed or 0,
                            crc32=item.crc32,
                            sha256="",
                            is_nested_container=False,
                            depth=depth,
                        )
                    )
        except Exception as exc:  # noqa: BLE001 - biblioteca externa
            raise ContainerError(f"7z ilegivel: {exc}") from exc
        return info
    info.notes.append(f"container nao reconhecido (magic {raw[:8].hex(' ')})")
    return info


def read_log_payloads(
    path: Path, *, source: str = ""
) -> tuple[ContainerInfo, list[LogPayload]]:
    """Le, em memoria, os textos de log de um ``.jez``.

    Containers aninhados vem antes do ``logd.dat`` do proprio pacote, para
    que a ordem reflita a sequencia de urnas. Linhas repetidas NAO sao
    removidas: o conteudo e preservado como evidencia.
    """
    raw = path.read_bytes()
    info = list_container(raw, source=source or path.name)
    payloads: list[LogPayload] = []

    def _walk(data: bytes, prefix: str, depth: int) -> None:
        if depth >= MAX_DEPTH:
            return
        kind = detect_container(data)
        if kind != "zip":
            return
        try:
            entries = _zip_infos(io.BytesIO(data))
        except (zipfile.BadZipFile, OSError):
            return
        nested: list[tuple[str, bytes]] = []
        own: list[tuple[str, bytes]] = []
        for entry in sorted(entries, key=lambda item: item.filename):
            try:
                content = _read_zip_entry(io.BytesIO(data), entry)
            except (ContainerError, zipfile.BadZipFile, OSError) as exc:
                info.notes.append(f"{prefix}{entry.filename}: {exc}")
                continue
            label = f"{prefix}{entry.filename}"
            if detect_container(content) == "zip":
                nested.append((label, content))
            else:
                own.append((label, content))
        for label, content in nested:
            _walk(content, f"{label}!", depth + 1)
        for label, content in own:
            text = content.decode("latin-1", errors="replace")
            payloads.append(
                LogPayload(
                    entry_path=label,
                    text=text,
                    size=len(content),
                    sha256=hash_bytes(content, "sha256"),
                )
            )

    _walk(raw, "", 0)
    if not payloads:
        info.notes.append("nenhum texto de log encontrado no container")
    return info, payloads
