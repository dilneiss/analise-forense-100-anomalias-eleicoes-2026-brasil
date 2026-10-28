"""Verificacao criptografica com bibliotecas reconhecidas.

Nao ha implementacao propria de curvas ou de assinatura. Quando o algoritmo
ou a chave nao sao suportados pela biblioteca ``cryptography`` (caso do
Ed521 da ICP-Brasil, OID 1.3.6.1.4.1.44588.2.1), o resultado e
explicitamente "NAO FOI POSSIVEL VERIFICAR" com o motivo.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from cryptography import x509
from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed448, ed25519, padding, rsa
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

from ..models import NAO_VERIFICAVEL, NAO_VALIDADO, VALIDADO

OID_ED521 = "1.3.6.1.4.1.44588.2.1"
OID_EC_PUBLIC_KEY = "1.2.840.10045.2.1"


@dataclass
class CertificateInfo:
    subject: str
    issuer: str
    serial_hex: str
    sha256: str
    not_before: str
    not_after: str
    signature_oid: str
    key_oid: str
    common_name: Optional[str]
    key_type: str
    key_supported: bool
    key_error: Optional[str] = None
    pem_path: Optional[str] = None
    raw_der: bytes = field(default=b"", repr=False)
    certificate: Any = field(default=None, repr=False)

    def as_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "issuer": self.issuer,
            "serial_hex": self.serial_hex,
            "sha256": self.sha256,
            "not_before": self.not_before,
            "not_after": self.not_after,
            "signature_oid": self.signature_oid,
            "public_key_oid": self.key_oid,
            "common_name": self.common_name,
            "public_key_type": self.key_type,
            "public_key_supported": self.key_supported,
            "public_key_error": self.key_error,
            "pem_path": self.pem_path,
        }


@dataclass
class Verification:
    status: str
    algorithm: str
    detail: str
    checks: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "algorithm": self.algorithm,
            "detail": self.detail,
            "checks": self.checks,
        }


def load_certificate(raw: bytes) -> x509.Certificate:
    if b"-----BEGIN" in raw:
        return x509.load_pem_x509_certificate(raw)
    return x509.load_der_x509_certificate(raw)


def certificate_info(raw: bytes) -> CertificateInfo:
    cert = load_certificate(raw)
    der = cert.public_bytes(serialization.Encoding.DER)
    key_type = "desconhecido"
    supported = False
    key_error: Optional[str] = None
    try:
        public_key = cert.public_key()
        key_type = type(public_key).__name__
        if isinstance(public_key, ec.EllipticCurvePublicKey):
            key_type = f"EC/{public_key.curve.name}"
        elif isinstance(public_key, rsa.RSAPublicKey):
            key_type = f"RSA/{public_key.key_size}"
        elif isinstance(public_key, (ed25519.Ed25519PublicKey, ed448.Ed448PublicKey)):
            key_type = type(public_key).__name__
        supported = True
    except (UnsupportedAlgorithm, ValueError) as exc:
        key_error = f"{type(exc).__name__}: {exc}"
    cn = next(
        (
            attribute.value
            for attribute in cert.subject
            if attribute.oid.dotted_string == "2.5.4.3"
        ),
        None,
    )
    return CertificateInfo(
        subject=cert.subject.rfc4514_string(),
        issuer=cert.issuer.rfc4514_string(),
        serial_hex=format(cert.serial_number, "x"),
        sha256=hashlib.sha256(der).hexdigest(),
        not_before=cert.not_valid_before_utc.isoformat(),
        not_after=cert.not_valid_after_utc.isoformat(),
        signature_oid=cert.signature_algorithm_oid.dotted_string,
        key_oid=cert.public_key_algorithm_oid.dotted_string,
        common_name=cn,
        key_type=key_type,
        key_supported=supported,
        key_error=key_error,
        raw_der=der,
        certificate=cert,
    )


def _canonical_ecdsa(signature: bytes) -> Optional[bytes]:
    """Reescreve r||s ou DER nao minimo em DER canonico (para o OpenSSL)."""
    try:
        if signature[:1] == b"\x30":
            from .. import der

            node = der.parse(signature)
            parts = node.children()
            if len(parts) != 2:
                return None
            r, s = (int.from_bytes(part.value, "big", signed=True) for part in parts)
        elif len(signature) in (64, 96, 132) and len(signature) % 2 == 0:
            half = len(signature) // 2
            r = int.from_bytes(signature[:half], "big")
            s = int.from_bytes(signature[half:], "big")
        else:
            return None
    except (ValueError, IndexError):
        return None
    if r <= 0 or s <= 0:
        return None
    return encode_dss_signature(r, s)


def verify_entity_signature(
    *,
    algorithm: str,
    certificate: CertificateInfo,
    message_hash: bytes,
    signature: bytes,
    label: str,
) -> Verification:
    """Verifica a assinatura de hardware do autoassinado ou de um arquivo.

    Convencao documentada pela especificacao/implementacoes publicas:
    ECDSA P-521 recebe o hash declarado como mensagem (com SHA-512 aplicado
    pelo verificador) e Ed521 assina SHA-512(hash). Somente ECDSA e
    verificavel com ``cryptography``; o Ed521 da ICP-Brasil nao e suportado.
    """
    if algorithm == "ecdsa":
        if not certificate.key_supported:
            return Verification(
                NAO_VERIFICAVEL,
                "ECDSA-P521/SHA-512",
                "chave publica nao suportada pela biblioteca: "
                f"{certificate.key_error}",
                [{"key": label, "status": NAO_VERIFICAVEL}],
            )
        public_key = certificate.certificate.public_key()
        if not isinstance(public_key, ec.EllipticCurvePublicKey):
            return Verification(
                NAO_VERIFICAVEL,
                "ECDSA",
                f"certificado tem chave {certificate.key_type}, nao ECDSA",
                [{"key": label, "status": NAO_VERIFICAVEL}],
            )
        canonical = _canonical_ecdsa(signature)
        if canonical is None:
            return Verification(
                NAO_VALIDADO,
                f"ECDSA/{public_key.curve.name}",
                "formato da assinatura ECDSA nao reconhecido",
                [{"key": label, "status": NAO_VALIDADO}],
            )
        try:
            public_key.verify(
                canonical, message_hash, ec.ECDSA(hashes.SHA512())
            )
            return Verification(
                VALIDADO,
                f"ECDSA/{public_key.curve.name}/SHA-512",
                "assinatura verificada com a chave publica do certificado",
                [{"key": label, "status": VALIDADO}],
            )
        except InvalidSignature:
            return Verification(
                NAO_VALIDADO,
                f"ECDSA/{public_key.curve.name}/SHA-512",
                "a assinatura nao confere com a chave publica do certificado",
                [{"key": label, "status": NAO_VALIDADO}],
            )
    if algorithm == "eddsa":
        detail = (
            "algoritmo EdDSA Ed521 (ICP-Brasil, OID "
            f"{certificate.key_oid}) nao e suportado pela biblioteca "
            "cryptography; a verificacao exigiria implementacao propria de "
            "curva, o que esta fora do escopo desta ferramenta"
        )
        return Verification(
            NAO_VERIFICAVEL,
            "Ed521 (ICP-Brasil)",
            detail,
            [{"key": label, "status": NAO_VERIFICAVEL, "detail": detail}],
        )
    if algorithm == "rsa":
        if not certificate.key_supported:
            return Verification(
                NAO_VERIFICAVEL,
                "RSA",
                f"chave publica nao suportada: {certificate.key_error}",
                [{"key": label, "status": NAO_VERIFICAVEL}],
            )
        public_key = certificate.certificate.public_key()
        if not isinstance(public_key, rsa.RSAPublicKey):
            return Verification(
                NAO_VERIFICAVEL,
                "RSA",
                "certificado sem chave RSA",
                [{"key": label, "status": NAO_VERIFICAVEL}],
            )
        try:
            public_key.verify(
                signature, message_hash, padding.PKCS1v15(), hashes.SHA512()
            )
            return Verification(
                VALIDADO,
                "RSA/SHA-512",
                "assinatura verificada",
                [{"key": label, "status": VALIDADO}],
            )
        except InvalidSignature:
            return Verification(
                NAO_VALIDADO,
                "RSA/SHA-512",
                "assinatura nao confere",
                [{"key": label, "status": NAO_VALIDADO}],
            )
    return Verification(
        NAO_VERIFICAVEL,
        algorithm,
        f"algoritmo '{algorithm}' nao e verificavel por esta ferramenta",
        [{"key": label, "status": NAO_VERIFICAVEL}],
    )


def validity(certificate: CertificateInfo, when: datetime) -> bool:
    cert = certificate.certificate
    return cert.not_valid_before_utc <= when.astimezone(cert.not_valid_before_utc.tzinfo) <= cert.not_valid_after_utc


def load_ca_bundle(paths: list[Path]) -> dict[str, x509.Certificate]:
    """Carrega certificados de AC fornecidos pelo usuario (arquivo ou pasta)."""
    certificates: dict[str, x509.Certificate] = {}
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.glob("*.pem")))
            files.extend(sorted(path.glob("*.crt")))
            files.extend(sorted(path.glob("*.der")))
        elif path.is_file():
            files.append(path)
    for file in files:
        try:
            cert = load_certificate(file.read_bytes())
        except Exception:  # noqa: BLE001 - arquivo de AC opcional
            continue
        certificates[cert.subject.rfc4514_string()] = cert
    return certificates


def verify_chain(
    certificate: CertificateInfo,
    authorities: dict[str, x509.Certificate],
    when: Optional[datetime] = None,
    max_depth: int = 5,
) -> dict[str, Any]:
    """Sobe a cadeia enquanto houver AC fornecida e assinatura verificavel."""
    if not authorities:
        return {
            "status": NAO_VERIFICAVEL,
            "detail": (
                "certificados das AC nao fornecidos; a cadeia nao pode ser "
                "validada (use --ca DIR)"
            ),
            "levels": [],
        }
    chain: list[str] = [certificate.subject]
    current = certificate.certificate
    for _ in range(max_depth):
        issuer_name = current.issuer.rfc4514_string()
        if issuer_name == current.subject.rfc4514_string():
            return {
                "status": VALIDADO,
                "detail": f"cadeia alcancou a raiz autossinada ({current.subject.rfc4514_string()})",
                "levels": chain,
            }
        parent = authorities.get(issuer_name)
        if parent is None:
            return {
                "status": NAO_VERIFICAVEL,
                "detail": f"AC emissora nao fornecida: {issuer_name}",
                "levels": chain,
            }
        try:
            public_key = parent.public_key()
            if isinstance(public_key, ec.EllipticCurvePublicKey):
                public_key.verify(
                    current.signature,
                    current.tbs_certificate_bytes,
                    ec.ECDSA(current.signature_hash_algorithm),
                )
            elif isinstance(public_key, rsa.RSAPublicKey):
                public_key.verify(
                    current.signature,
                    current.tbs_certificate_bytes,
                    padding.PKCS1v15(),
                    current.signature_hash_algorithm,
                )
            elif isinstance(public_key, (ed25519.Ed25519PublicKey, ed448.Ed448PublicKey)):
                public_key.verify(current.signature, current.tbs_certificate_bytes)
            else:
                return {
                    "status": NAO_VERIFICAVEL,
                    "detail": f"chave da AC nao suportada: {type(public_key).__name__}",
                    "levels": chain,
                }
        except InvalidSignature:
            return {
                "status": NAO_VALIDADO,
                "detail": f"assinatura do certificado nao confere com a AC {issuer_name}",
                "levels": chain,
            }
        except (UnsupportedAlgorithm, ValueError) as exc:
            return {
                "status": NAO_VERIFICAVEL,
                "detail": f"nao foi possivel verificar a AC {issuer_name}: {exc}",
                "levels": chain,
            }
        chain.append(issuer_name)
        current = parent
    return {
        "status": NAO_VERIFICAVEL,
        "detail": f"cadeia excedeu {max_depth} niveis",
        "levels": chain,
    }
