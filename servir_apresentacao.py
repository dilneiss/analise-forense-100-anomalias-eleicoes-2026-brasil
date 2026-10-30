#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serve a apresentação em http://127.0.0.1:8765 para habilitar a gravação da aba.

O navegador só permite getDisplayMedia/getUserMedia em contexto seguro
(https:// ou localhost). Abrir o arquivo via file:// funciona no Chrome em
alguns casos, mas é bloqueado em diversos cenários — este servidor resolve.

Uso:
    python servir_apresentacao.py            # abre a apresentação no navegador
    python servir_apresentacao.py --porta 9000
    python servir_apresentacao.py --sem-abrir
"""

from __future__ import annotations

import argparse
import http.server
import socket
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PAGINA = "apresentacao_slides.html"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(RAIZ), **kwargs)

    def end_headers(self):
        # evita cache agressivo ao editar a apresentação
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))


def porta_livre(preferida: int) -> int:
    for p in range(preferida, preferida + 40):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    raise SystemExit("Nenhuma porta livre encontrada entre %d e %d" % (preferida, preferida + 39))


def main() -> int:
    ap = argparse.ArgumentParser(description="Servidor local da apresentação pericial")
    ap.add_argument("--porta", type=int, default=8765)
    ap.add_argument("--sem-abrir", action="store_true")
    args = ap.parse_args()

    if not (RAIZ / PAGINA).exists():
        print("ERRO: %s não encontrado em %s" % (PAGINA, RAIZ))
        return 2

    porta = porta_livre(args.porta)
    url = "http://127.0.0.1:%d/%s" % (porta, PAGINA)

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", porta), Handler)

    print("=" * 72)
    print(" APRESENTAÇÃO PERICIAL — SERVIDOR LOCAL")
    print("=" * 72)
    print(" URL:      %s" % url)
    print(" Contexto: seguro (localhost) — gravação de aba HABILITADA")
    print(" Encerrar: Ctrl+C")
    print("=" * 72)

    if not args.sem_abrir:
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
