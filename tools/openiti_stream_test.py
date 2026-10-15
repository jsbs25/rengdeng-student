#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenITI 流式分页离线专项测试。

用本地 Range 服务模拟 raw.githubusercontent.com，不访问外网、不下载真实书籍。
"""
from __future__ import annotations

import importlib
import json
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
import openiti_stream as stream


LARGE_ID = "openiti-a1b2c3d4e5f60718"
SMALL_ID = "openiti-a1b2c3d4e5f60719"

# 让第一个 1 MiB Range 只处理 META 行，并正好截断一个 3 字节阿拉伯字符。
cut = stream.RANGE_CHUNK_BYTES - 1
meta_unit = b"#META# x\n"
large_prefix = meta_unit * (cut // len(meta_unit))
large_prefix += b" " * (cut - len(large_prefix) - 1) + b"\n"
assert len(large_prefix) == cut and large_prefix.endswith(b"\n")
large_tail = ("بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n\n"
              "هذه فقرة عربية بعد حد البايت\n\n")
LARGE_DATA = large_prefix + large_tail.encode("utf-8")
SMALL_DATA = "بِسْمِ اللَّهِ\n\nنص عربي قصير.".encode("utf-8")


class RangeHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _data(self):
        return SMALL_DATA if self.path.startswith("/small") else LARGE_DATA

    def _headers(self, status, start, end, total):
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("ETag", '"mock-etag-v1"')
        self.send_header("Content-Range", f"bytes {start}-{end}/{total}")
        self.send_header("Content-Length", str(max(0, end - start + 1)))
        self.end_headers()

    def do_HEAD(self):
        data = self._data()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("ETag", '"mock-etag-v1"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()

    def do_GET(self):
        data = self._data()
        raw = self.headers.get("Range", "")
        if not raw.startswith("bytes="):
            self.send_response(200)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        start_s, end_s = raw[6:].split("-", 1)
        start = int(start_s)
        end = min(int(end_s), len(data) - 1)
        if start >= len(data):
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{len(data)}")
            self.end_headers()
            return
        body = data[start:end + 1]
        self._headers(206, start, end, len(data))
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


def book(book_id, path, url):
    return {
        "id": book_id,
        "t": "Mock Arabic Book",
        "a": "Mock Author",
        "source": "OpenITI/KITAB mock",
        "text_url": url + path,
    }


def status_text(result):
    payload, status = result
    return status, payload


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), RangeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    # 只在本测试中放宽来源校验；真实 server.py 仍使用固定 HTTPS 白名单。
    stream._validate_source = lambda b: str(b["text_url"])
    stream.REQUEST_BUDGET_BYTES = stream.RANGE_CHUNK_BYTES
    try:
        with tempfile.TemporaryDirectory(prefix="openiti-stream-test-") as tmp:
            root = Path(tmp)
            large = book(LARGE_ID, "/large", base)
            first_status, first = status_text(stream.read_page(large, 0, root))
            assert first_status == 202, (first_status, first)
            assert first["bytes_read"] == stream.RANGE_CHUNK_BYTES
            assert first["pages_ready"] == 0
            manifest_path = root / LARGE_ID / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            assert manifest["next_byte"] == stream.RANGE_CHUNK_BYTES
            assert manifest["decoder_pending_b64"], manifest
            # 模拟进程重启：重新加载模块，第二次从 manifest 的 decoder state 继续。
            importlib.reload(stream)
            stream._validate_source = lambda b: str(b["text_url"])
            stream.REQUEST_BUDGET_BYTES = stream.RANGE_CHUNK_BYTES
            second_status, second = status_text(stream.read_page(large, 0, root))
            assert second_status == 200, (second_status, second)
            assert len(second["text"]) > 0
            assert "�" not in second["text"]
            assert "بِسْمِ اللَّهِ" in second["text"]
            assert second["bytes_read"] == len(LARGE_DATA)
            assert second["pages_ready"] == 1

            small = book(SMALL_ID, "/small", base)
            ready_status, ready = status_text(stream.read_page(small, 0, root))
            assert ready_status == 200
            assert ready["text"] and "�" not in ready["text"]
            eof_status, eof = status_text(stream.read_page(small, 1, root))
            assert eof_status == 416, (eof_status, eof)
            assert eof["total"] == 1

            assert stream.parse_content_range("bytes 0-6/1234") == (0, 6, 1234)
            assert stream.parse_content_range("bytes 0-6/*") == (0, 6, None)
            assert stream.parse_content_range("not-a-range") is None
            print(json.dumps({
                "ok": True,
                "large_first_status": first_status,
                "large_second_status": second_status,
                "large_source_bytes": len(LARGE_DATA),
                "small_eof_status": eof_status,
                "arabic_replacement": False,
                "manifest_resume": True,
            }, ensure_ascii=False))
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
