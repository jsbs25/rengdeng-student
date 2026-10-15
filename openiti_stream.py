#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenITI 按需流式分页核心。

安全边界：
- 只接受已由 server.py 校验过的固定 OpenITI raw URL；
- 每次上游请求只读取一个 Range 分段；
- 使用增量 UTF-8 解码器，避免阿拉伯字符在字节边界被截断；
- 页面、分段和解析状态均原子写入，可在进程重启后继续；
- 不会为了生成第一页下载整本原文。
"""

import base64
import codecs
import hashlib
import json
import os
import re
import threading
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


CACHE_SCHEMA = 1
RANGE_CHUNK_BYTES = 1024 * 1024
REQUEST_BUDGET_BYTES = 2 * 1024 * 1024
PAGE_CHARS = 5200
MAX_SOURCE_BYTES = 64 * 1024 * 1024
READ_TIMEOUT_SECONDS = 45
META_TTL_SECONDS = 600

_BOOK_LOCKS = {}
_BOOK_LOCKS_GUARD = threading.Lock()
_UPSTREAM_SEMAPHORE = threading.BoundedSemaphore(3)


class OpenITIStreamError(Exception):
    """带有稳定 error_code/status 的用户可见流式读取错误。"""

    def __init__(self, message, code='stream_error', status=502, extra=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.extra = extra or {}

    def payload(self):
        data = {'ready': False, 'error_code': self.code, 'error': self.message}
        data.update(self.extra)
        return data


def _book_lock(book_id):
    with _BOOK_LOCKS_GUARD:
        lock = _BOOK_LOCKS.get(book_id)
        if lock is None:
            lock = threading.Lock()
            _BOOK_LOCKS[book_id] = lock
        return lock


def _safe_id(book_id):
    value = str(book_id or '').strip()
    if not re.fullmatch(r'openiti-[0-9a-f]{16}', value):
        raise OpenITIStreamError('书目 ID 无效', 'invalid_book_id', 404)
    return value


def _validate_source(book):
    source = str(book.get('text_url') or '').strip()
    parsed = urlparse(source)
    if (
        parsed.scheme != 'https'
        or parsed.netloc != 'raw.githubusercontent.com'
        or not parsed.path.startswith('/OpenITI/RELEASE/')
    ):
        raise OpenITIStreamError('原文来源不在 OpenITI 官方白名单内', 'source_not_allowed', 403)
    return source


def _now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def _atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + '.part')
    tmp.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    os.replace(tmp, path)


def _atomic_bytes(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + '.part')
    with tmp.open('wb') as handle:
        handle.write(value)
    os.replace(tmp, path)


def _read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return default


def _url_hash(source):
    return hashlib.sha256(source.encode('utf-8')).hexdigest()


def _parse_content_range(value):
    match = re.match(r'bytes\s+(\d+)-(\d+)/(\d+|\*)', str(value or ''), re.I)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2)), (None if match.group(3) == '*' else int(match.group(3)))


def _parse_size(headers):
    cr = _parse_content_range(headers.get('Content-Range'))
    if cr and cr[2] is not None:
        return cr[2]
    try:
        return int(headers.get('Content-Length') or 0)
    except (TypeError, ValueError):
        return 0


def _source_meta(response, accept_ranges=None):
    size = _parse_size(response.headers)
    return {
        'source_size': size,
        'accept_ranges': bool(
            accept_ranges if accept_ranges is not None
            else str(response.headers.get('Accept-Ranges') or '').lower() == 'bytes'
        ),
        'etag': str(response.headers.get('ETag') or ''),
        'last_modified': str(response.headers.get('Last-Modified') or ''),
        'content_type': str(response.headers.get('Content-Type') or 'text/plain'),
    }


def _raise_size_limit(size):
    if size and size > MAX_SOURCE_BYTES:
        raise OpenITIStreamError(
            '原文超过应用内安全读取上限，请使用官方来源查看',
            'source_too_large', 413,
            {'source_bytes': size},
        )


def _range_probe(source, headers):
    req = Request(source, headers={**headers, 'Range': 'bytes=0-0'})
    try:
        with _UPSTREAM_SEMAPHORE:
            with urlopen(req, timeout=READ_TIMEOUT_SECONDS) as response:
                cr = _parse_content_range(response.headers.get('Content-Range'))
                if getattr(response, 'status', 200) != 206 or not cr or cr[0] != 0 or cr[1] != 0:
                    raise OpenITIStreamError(
                        '当前来源不支持安全分段读取',
                        'range_unsupported', 502,
                        {'fallback_url': source},
                    )
                meta = _source_meta(response, accept_ranges=True)
                meta['source_size'] = cr[2] or meta['source_size']
                _raise_size_limit(meta['source_size'])
                return meta
    except OpenITIStreamError:
        raise
    except Exception as exc:
        raise OpenITIStreamError(
            '原文源站暂时无法探测，请稍后重试',
            'source_probe_failed', 502,
            {'detail': str(exc)[:160]},
        ) from exc


def _head(source):
    headers = {
        'User-Agent': 'NourStudent/1.0 in-app-reader; segmented-openiti',
        'Accept': 'text/plain,text/*;q=0.9,*/*;q=0.5',
    }
    try:
        req = Request(source, headers=headers, method='HEAD')
        with _UPSTREAM_SEMAPHORE:
            with urlopen(req, timeout=READ_TIMEOUT_SECONDS) as response:
                meta = _source_meta(response)
                _raise_size_limit(meta['source_size'])
                if not meta['source_size'] or not meta['accept_ranges']:
                    return _range_probe(source, headers)
                return meta
    except OpenITIStreamError:
        raise
    except (HTTPError, URLError, TimeoutError, OSError):
        return _range_probe(source, headers)


def _metadata_matches(manifest, meta, source):
    return (
        manifest.get('source_url_sha256') == _url_hash(source)
        and int(manifest.get('source_size') or 0) == int(meta.get('source_size') or 0)
        and str(manifest.get('etag') or '') == str(meta.get('etag') or '')
        and str(manifest.get('last_modified') or '') == str(meta.get('last_modified') or '')
    )


def _new_manifest(book_id, source, meta):
    return {
        'schema': CACHE_SCHEMA,
        'book_id': book_id,
        'source_url_sha256': _url_hash(source),
        'source_size': int(meta.get('source_size') or 0),
        'etag': str(meta.get('etag') or ''),
        'last_modified': str(meta.get('last_modified') or ''),
        'accept_ranges': bool(meta.get('accept_ranges')),
        'next_byte': 0,
        'eof': False,
        'pages_ready': 0,
        'parser': _IncrementalParser().snapshot(),
        'decoder_pending_b64': '',
        'decoder_flag': 0,
        'checked_at': time.time(),
        'updated_at': _now(),
    }


def _remove_tree(path):
    path = Path(path)
    if not path.exists():
        return
    for child in sorted(path.rglob('*'), reverse=True):
        if child.is_file() or child.is_symlink():
            child.unlink(missing_ok=True)
        elif child.is_dir():
            child.rmdir()
    path.rmdir()


def _load_or_init(book, root):
    book_id = _safe_id(book.get('id'))
    source = _validate_source(book)
    root = Path(root) / book_id
    manifest_path = root / 'manifest.json'
    manifest = _read_json(manifest_path)
    now = time.time()
    if manifest and manifest.get('schema') == CACHE_SCHEMA and now - float(manifest.get('checked_at') or 0) < META_TTL_SECONDS:
        if manifest.get('source_url_sha256') == _url_hash(source):
            return root, manifest, source
        manifest = None

    meta = _head(source)
    if manifest and _metadata_matches(manifest, meta, source):
        manifest['checked_at'] = now
        _atomic_json(manifest_path, manifest)
        return root, manifest, source

    if manifest:
        _remove_tree(root)
    manifest = _new_manifest(book_id, source, meta)
    _atomic_json(manifest_path, manifest)
    return root, manifest, source


def _segment_path(root, start, end):
    return Path(root) / 'segments' / f'{start:012d}-{end:012d}.part'


def _fetch_segment(source, start, source_size, root, chunk_bytes=RANGE_CHUNK_BYTES):
    if start >= source_size:
        return b'', start, start - 1
    chunk_bytes = max(1, min(int(chunk_bytes), RANGE_CHUNK_BYTES))
    end = min(source_size - 1, start + chunk_bytes - 1)
    target = _segment_path(root, start, end)
    if target.exists() and target.stat().st_size == end - start + 1:
        return target.read_bytes(), start, end

    req = Request(source, headers={
        'User-Agent': 'NourStudent/1.0 in-app-reader; segmented-openiti',
        'Accept': 'text/plain,text/*;q=0.9,*/*;q=0.5',
        'Range': f'bytes={start}-{end}',
    })
    expected = end - start + 1
    data = bytearray()
    try:
        with _UPSTREAM_SEMAPHORE:
            with urlopen(req, timeout=READ_TIMEOUT_SECONDS) as response:
                if getattr(response, 'status', 200) != 206:
                    raise OpenITIStreamError(
                        '当前来源没有返回有效的分段响应',
                        'range_unsupported', 502,
                        {'fallback_url': source},
                    )
                cr = _parse_content_range(response.headers.get('Content-Range'))
                if not cr or cr[0] != start or cr[1] != end or cr[2] != source_size:
                    raise OpenITIStreamError('分段响应范围校验失败', 'range_mismatch', 502)
                while len(data) < expected:
                    chunk = response.read(min(262144, expected - len(data)))
                    if not chunk:
                        break
                    data.extend(chunk)
                    if len(data) > expected:
                        raise OpenITIStreamError('分段响应超过预期大小', 'range_overflow', 502)
    except OpenITIStreamError:
        raise
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise OpenITIStreamError('OpenITI 原文分段读取失败，请稍后重试', 'upstream_read_failed', 502) from exc
    if len(data) != expected:
        raise OpenITIStreamError('OpenITI 分段响应不完整，请稍后重试', 'range_incomplete', 502)
    _atomic_bytes(target, bytes(data))
    return bytes(data), start, end


class _IncrementalParser:
    """把 UTF-8 文本流转换成与现有阅读器兼容的 5,200 字符页面。"""

    def __init__(self, state=None):
        state = state or {}
        self.line_buffer = str(state.get('line_buffer') or '')
        self.paragraph_lines = list(state.get('paragraph_lines') or [])
        self.page_text = str(state.get('page_text') or '')
        self.pages = []

    def snapshot(self):
        return {
            'line_buffer': self.line_buffer,
            'paragraph_lines': self.paragraph_lines[-200:],
            'page_text': self.page_text,
        }

    def _emit_page(self):
        value = self.page_text.strip()
        if value:
            self.pages.append(value)
        self.page_text = ''

    def _append_block(self, block):
        block = str(block or '').strip()
        if not block:
            return
        while block:
            separator = '\n\n' if self.page_text else ''
            available = PAGE_CHARS - len(self.page_text) - len(separator)
            if available <= 0:
                self._emit_page()
                continue
            if len(block) <= available:
                self.page_text += separator + block
                return
            if self.page_text:
                self._emit_page()
                continue
            # 这里切的是 Python Unicode 字符，不是 UTF-8 字节，因此不会切断阿拉伯字符。
            self.page_text = block[:PAGE_CHARS]
            self._emit_page()
            block = block[PAGE_CHARS:].lstrip()

    def _flush_paragraph(self):
        if not self.paragraph_lines:
            return
        self._append_block('\n'.join(self.paragraph_lines))
        self.paragraph_lines = []

    def _line(self, line):
        line = str(line or '').rstrip('\r')
        stripped = line.strip()
        if stripped.startswith('######OpenITI#') or stripped.startswith('#META#'):
            return
        if not stripped:
            self._flush_paragraph()
            return
        self.paragraph_lines.append(stripped)

    def feed(self, text, final=False):
        text = str(text or '').replace('\r\n', '\n').replace('\r', '\n')
        self.line_buffer += text
        parts = self.line_buffer.split('\n')
        if final:
            self.line_buffer = ''
            complete = parts
        else:
            self.line_buffer = parts.pop()
            complete = parts
        for line in complete:
            self._line(line)
        if final:
            self._flush_paragraph()
            self._emit_page()
        emitted = self.pages
        self.pages = []
        return emitted


def _decoder_from_manifest(manifest):
    decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
    pending = manifest.get('decoder_pending_b64') or ''
    raw = base64.b64decode(pending.encode('ascii')) if pending else b''
    try:
        decoder.setstate((raw, int(manifest.get('decoder_flag') or 0)))
    except Exception:
        decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
    return decoder


def _save_decoder(manifest, decoder):
    pending, flag = decoder.getstate()
    manifest['decoder_pending_b64'] = base64.b64encode(pending).decode('ascii') if pending else ''
    manifest['decoder_flag'] = int(flag or 0)


def _page_path(root, index):
    return Path(root) / 'pages' / f'{int(index):08d}.json'


def _load_page(root, index):
    value = _read_json(_page_path(root, index))
    return value if isinstance(value, dict) and value.get('complete') else None


def _write_pages(root, start_index, pages, byte_start, byte_end):
    for offset, text in enumerate(pages):
        index = start_index + offset
        _atomic_json(_page_path(root, index), {
            'page': index,
            'text': text,
            'byte_start': byte_start,
            'byte_end': byte_end,
            'complete': True,
        })


def _base_payload(book, manifest, page, extra=None):
    source_size = int(manifest.get('source_size') or 0)
    next_byte = min(source_size, int(manifest.get('next_byte') or 0))
    data = {
        't': 'openiti',
        'id': book.get('id'),
        'title': book.get('t', ''),
        'author': book.get('a', ''),
        'page': int(page),
        'total': int(manifest.get('pages_ready') or 0) if manifest.get('eof') else None,
        'has_next': not bool(manifest.get('eof')) or int(page) + 1 < int(manifest.get('pages_ready') or 0),
        'source': book.get('source', 'OpenITI/KITAB'),
        'source_url': book.get('u', ''),
        'text_url': book.get('text_url', ''),
        'rights': book.get('rights', ''),
        'streaming': True,
        'cached': True,
        'bytes_read': next_byte,
        'source_bytes': source_size,
        'eof': bool(manifest.get('eof')),
        'progress': round(next_byte / source_size, 6) if source_size else 0,
        'pages_ready': int(manifest.get('pages_ready') or 0),
    }
    if extra:
        data.update(extra)
    return data


def read_page(book, page, cache_root):
    """读取一个逻辑页，返回 (payload, http_status)。"""
    try:
        page = int(page)
    except (TypeError, ValueError):
        raise OpenITIStreamError('页码无效', 'invalid_page', 400)
    if page < 0:
        raise OpenITIStreamError('页码无效', 'invalid_page', 400)

    book_id = _safe_id(book.get('id'))
    with _book_lock(book_id):
        root, manifest, source = _load_or_init(book, cache_root)
        page_record = _load_page(root, page)
        if page_record:
            return _base_payload(book, manifest, page, {'ready': True, 'text': page_record.get('text', '')}), 200
        if manifest.get('eof'):
            payload = _base_payload(book, manifest, page, {'error': '页码超出范围'})
            payload['total'] = int(manifest.get('pages_ready') or 0)
            return payload, 416

        bytes_used = 0
        while not manifest.get('eof') and not _load_page(root, page):
            source_size = int(manifest.get('source_size') or 0)
            start = int(manifest.get('next_byte') or 0)
            if start >= source_size:
                segment = b''
                end = start - 1
            else:
                remaining_budget = REQUEST_BUDGET_BYTES - bytes_used
                if remaining_budget <= 0:
                    break
                requested_chunk = min(RANGE_CHUNK_BYTES, remaining_budget)
                segment, start, end = _fetch_segment(source, start, source_size, root, requested_chunk)

            parser = _IncrementalParser(manifest.get('parser'))
            decoder = _decoder_from_manifest(manifest)
            if segment:
                decoded = decoder.decode(segment, final=False)
                is_eof = end >= source_size - 1
                if is_eof:
                    decoded += decoder.decode(b'', final=True)
                new_pages = parser.feed(decoded, final=is_eof)
                manifest['next_byte'] = end + 1
                manifest['eof'] = bool(is_eof)
                bytes_used += len(segment)
            else:
                decoded = decoder.decode(b'', final=True)
                new_pages = parser.feed(decoded, final=True)
                manifest['next_byte'] = source_size
                manifest['eof'] = True

            page_start = int(manifest.get('pages_ready') or 0)
            _write_pages(root, page_start, new_pages, start, end)
            manifest['pages_ready'] = page_start + len(new_pages)
            manifest['parser'] = parser.snapshot()
            _save_decoder(manifest, decoder)
            manifest['updated_at'] = _now()
            manifest['checked_at'] = float(manifest.get('checked_at') or time.time())
            _atomic_json(root / 'manifest.json', manifest)
            if bytes_used >= REQUEST_BUDGET_BYTES:
                break

        page_record = _load_page(root, page)
        if page_record:
            return _base_payload(book, manifest, page, {'ready': True, 'text': page_record.get('text', '')}), 200
        if manifest.get('eof'):
            payload = _base_payload(book, manifest, page, {'error': '页码超出范围'})
            payload['total'] = int(manifest.get('pages_ready') or 0)
            return payload, 416
        progress = _base_payload(book, manifest, page, {
            'ready': False,
            'pending_page': page,
            'next_page': page,
            'retry_after_ms': 500,
            'message': '正在分段读取阿拉伯原文…',
        })
        return progress, 202


# 供单元测试和后续维护使用的稳定符号。
IncrementalUTF8Decoder = codecs.getincrementaldecoder('utf-8')
IncrementalParser = _IncrementalParser
parse_content_range = _parse_content_range
