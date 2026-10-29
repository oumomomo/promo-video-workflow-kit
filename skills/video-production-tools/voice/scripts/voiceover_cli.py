#!/usr/bin/env python3
"""Select a project voice style and route Chinese to Doubao TTS, English to Google."""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import json
import getpass
import os
import re
import shutil
import ssl
import struct
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "references" / "voice-style-registry.json"
GOOGLE_ENDPOINT = "https://texttospeech.googleapis.com/v1/text:synthesize"
DOUBAO_ENDPOINT = "wss://openspeech.bytedance.com/api/v3/tts/bidirection"
DOUBAO_API_KEY_SERVICE = "video-workflow-doubao-tts-api-key"
DOUBAO_APP_ID_SERVICE = "video-workflow-doubao-tts-app-id"
DOUBAO_TOKEN_SERVICE = "video-workflow-doubao-tts-access-token"
GCLOUD_CANDIDATES = [
    shutil.which("gcloud"),
    str(Path.home() / "google-cloud-sdk/bin/gcloud"),
]


def ssl_context() -> ssl.SSLContext:
    """Use certifi when the framework Python lacks a usable macOS CA chain."""
    try:
        import certifi  # type: ignore

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def detect_language(text: str) -> tuple[str, str]:
    """Route mixed Chinese/English narration to Chinese; pure Latin text to English."""
    if re.search(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", text):
        return "zh-CN", "doubao"
    return "en-US", "google"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def read_input(args: argparse.Namespace) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    if args.storyboard:
        source_path = Path(args.storyboard).expanduser().resolve()
        source = load_json(source_path)
        shots = source.get("shots") or []
        if not shots:
            raise ValueError("分镜 JSON 缺少 shots。")
        narration = "\n".join(str(shot.get("narration", "")).strip() for shot in shots).strip()
        if not narration:
            raise ValueError("分镜 shots 中没有 narration。")
        metadata = {
            "input_type": "storyboard",
            "source_path": str(source_path),
            "source_hash": canonical_hash(source),
            "content_id": source.get("content_id"),
            "duration_ms": source.get("duration_ms"),
        }
        return narration, shots, metadata
    source_path = Path(args.text_file).expanduser().resolve()
    narration = source_path.read_text(encoding="utf-8").strip()
    if not narration:
        raise ValueError("文本文件为空。")
    return narration, [{"shot_id": "FULL", "narration": narration}], {
        "input_type": "text",
        "source_path": str(source_path),
        "source_hash": hashlib.sha256(narration.encode("utf-8")).hexdigest(),
    }


def select_style(styles: list[dict[str, Any]], shots: list[dict[str, Any]], explicit: str | None) -> dict[str, Any]:
    if explicit:
        for style in styles:
            if style["style_id"] == explicit:
                return {
                    "selection_mode": "explicit",
                    "selected_style": style,
                    "scores": {item["style_id"]: (100 if item["style_id"] == explicit else 0) for item in styles},
                    "reason": f"用户或上游工作流显式指定 {explicit}。",
                    "alternatives": [],
                }
        raise ValueError(f"未知 style-id: {explicit}")

    searchable = " ".join(
        str(shot.get(field, ""))
        for shot in shots
        for field in ("purpose", "caption", "narration", "composition")
    ).lower()
    purposes = {str(shot.get("purpose", "")).lower() for shot in shots}
    scores: dict[str, int] = {}
    reasons: dict[str, list[str]] = {}
    for style in styles:
        score = 0
        hits: list[str] = []
        for keyword in style.get("keywords", []):
            if keyword.lower() in searchable:
                score += 2
                hits.append(keyword)
        style_id = style["style_id"]
        if "explanation" in purposes and style_id == "professional-explainer":
            score += 2
        if purposes.intersection({"tutorial", "demo"}) and style_id == "product-demo":
            score += 3
        if purposes.intersection({"hook", "evidence"}) and style_id == "evidence-tech":
            score += 1
        if purposes.intersection({"story", "conflict"}) and style_id == "narrative-story":
            score += 2
        scores[style_id] = score
        reasons[style_id] = hits
    ranked = sorted(enumerate(styles), key=lambda pair: (-scores[pair[1]["style_id"]], pair[0]))
    selected = ranked[0][1]
    alternatives = [item[1]["style_id"] for item in ranked[1:3]]
    hit_text = "、".join(reasons[selected["style_id"]][:6]) or "默认专业解释路由"
    return {
        "selection_mode": "automatic",
        "selected_style": selected,
        "scores": scores,
        "reason": f"根据分镜用途与关键词匹配：{hit_text}。",
        "alternatives": alternatives,
    }


def build_google_request(
    text: str,
    style: dict[str, Any],
    model: str,
    language_code: str,
    audio_encoding: str = "MP3",
) -> dict[str, Any]:
    prompt = style.get("english_prompt") or (
        f"Speak in natural, clear American English with a {style['style_id'].replace('-', ' ')} delivery. "
        "Sound human, confident, and conversational. Use deliberate emphasis and short natural pauses. "
        "Avoid a mechanical reading voice, exaggerated advertising energy, and repetitive sentence endings."
    )
    if len(text.encode("utf-8")) > 4000:
        raise ValueError("单次英文正文超过 Gemini-TTS 4,000-byte 限制；请使用 --mode shots。")
    if len(prompt.encode("utf-8")) > 4000 or len((prompt + text).encode("utf-8")) > 8000:
        raise ValueError("prompt/text 超过 Gemini-TTS 字节限制。")
    return {
        "input": {"prompt": prompt, "text": text},
        "voice": {
            "languageCode": language_code,
            "name": style["speaker"],
            "modelName": model,
        },
        "audioConfig": {"audioEncoding": audio_encoding},
    }


def build_doubao_request(
    text: str,
    voice_type: str,
    audio_encoding: str = "MP3",
    context_text: str = "",
    speech_rate: int = 0,
    loudness_rate: int = 0,
) -> dict[str, Any]:
    if audio_encoding != "MP3":
        raise ValueError("豆包 V3 当前只输出 MP3；LINEAR16 仍仅用于 Google。")
    additions: dict[str, Any] = {"disable_markdown_filter": False}
    if context_text.strip():
        additions["context_texts"] = [context_text.strip()]
    return {
        "user": {"uid": "univer-voiceover-cli"},
        "namespace": "BidirectionalTTS",
        "req_params": {
            "text": text,
            "speaker": voice_type,
            "audio_params": {
                "format": "mp3",
                "sample_rate": 24000,
                "bit_rate": 128000,
                "speech_rate": speech_rate,
                "loudness_rate": loudness_rate,
            },
            "additions": json.dumps(additions, ensure_ascii=False),
        },
    }


def find_gcloud() -> str:
    for candidate in GCLOUD_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    raise RuntimeError("未找到 gcloud；请安装 Google Cloud CLI。")


def access_token() -> str:
    result = subprocess.run(
        [find_gcloud(), "auth", "application-default", "print-access-token"],
        check=True,
        capture_output=True,
        text=True,
    )
    token = result.stdout.strip()
    if not token:
        raise RuntimeError("ADC 未返回访问令牌。")
    return token


def call_google_api(request_body: dict[str, Any], project_id: str) -> bytes:
    if not project_id:
        raise ValueError("请用--project-id或GOOGLE_CLOUD_PROJECT指定自己的Google项目")
    body = json.dumps(request_body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        GOOGLE_ENDPOINT,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {access_token()}",
            "x-goog-user-project": project_id,
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=180, context=ssl_context()) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini-TTS HTTP {error.code}: {detail[:1200]}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Gemini-TTS 网络或 TLS 失败: {error.reason}") from error
    audio = payload.get("audioContent")
    if not audio:
        raise RuntimeError(f"Gemini-TTS 未返回 audioContent: {json.dumps(payload, ensure_ascii=False)[:1200]}")
    return base64.b64decode(audio)


def keychain_secret(service: str, configure_hint: str = "configure-doubao") -> str:
    security = shutil.which("security")
    if not security:
        raise RuntimeError("当前系统没有 macOS security 命令，无法从钥匙串读取豆包凭据。")
    result = subprocess.run(
        [security, "find-generic-password", "-s", service, "-w"],
        check=False,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()
    if result.returncode != 0 or not value:
        raise RuntimeError(
            f"钥匙串缺少 {service}；请先运行 voiceover_cli.py {configure_hint}。"
        )
    return value


def optional_keychain_secret(service: str) -> str | None:
    security = shutil.which("security")
    if not security:
        return None
    result = subprocess.run(
        [security, "find-generic-password", "-s", service, "-w"],
        check=False,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def _pack_doubao_message(event: int, payload: bytes, session_id: str = "") -> bytes:
    # V3 binary protocol: version=1, header=4 bytes, full-client request, event, JSON, no compression.
    data = bytearray((0x11, 0x14, 0x10, 0x00))
    data.extend(struct.pack(">i", event))
    if event not in {1, 2}:
        session = session_id.encode("utf-8")
        data.extend(struct.pack(">I", len(session)))
        data.extend(session)
    data.extend(struct.pack(">I", len(payload)))
    data.extend(payload)
    return bytes(data)


def _unpack_doubao_message(data: bytes) -> dict[str, Any]:
    if len(data) < 8:
        raise RuntimeError("豆包 V3 返回了过短的数据帧。")
    header_size = (data[0] & 0x0F) * 4
    msg_type = data[1] >> 4
    flag = data[1] & 0x0F
    offset = header_size
    result: dict[str, Any] = {"type": msg_type, "flag": flag, "event": 0, "payload": b""}
    if flag in {1, 3}:
        offset += 4  # sequence
    if msg_type == 0x0F:
        result["error_code"] = struct.unpack_from(">I", data, offset)[0]
        offset += 4
    if flag == 4:
        result["event"] = struct.unpack_from(">i", data, offset)[0]
        offset += 4
        event = result["event"]
        if event not in {1, 2, 50, 51, 52}:
            size = struct.unpack_from(">I", data, offset)[0]
            offset += 4
            result["session_id"] = data[offset : offset + size].decode("utf-8", errors="replace")
            offset += size
        if event in {50, 51, 52}:
            size = struct.unpack_from(">I", data, offset)[0]
            offset += 4
            result["connect_id"] = data[offset : offset + size].decode("utf-8", errors="replace")
            offset += size
    if offset + 4 <= len(data):
        size = struct.unpack_from(">I", data, offset)[0]
        offset += 4
        result["payload"] = data[offset : offset + size]
    return result


def _doubao_error_message(message: dict[str, Any]) -> str:
    payload = message.get("payload", b"")
    try:
        detail = json.loads(payload.decode("utf-8")) if payload else {}
        return json.dumps(detail, ensure_ascii=False)[:1200]
    except (UnicodeDecodeError, json.JSONDecodeError):
        return payload.decode("utf-8", errors="replace")[:1200]


async def _call_doubao_v3(request_body: dict[str, Any], api_key: str, resource_id: str) -> bytes:
    try:
        from websockets.asyncio.client import connect  # type: ignore
    except ImportError as error:
        raise RuntimeError("缺少 websockets>=14；请先安装官方 V3 示例依赖。") from error

    headers = {
        "X-Api-Key": api_key,
        "X-Api-Resource-Id": resource_id,
        "X-Api-Connect-Id": str(uuid.uuid4()),
    }
    session_id = str(uuid.uuid4())
    audio = bytearray()
    try:
        async with connect(
            DOUBAO_ENDPOINT,
            additional_headers=headers,
            max_size=10 * 1024 * 1024,
            ssl=ssl_context(),
            proxy=None,
            open_timeout=30,
            close_timeout=10,
        ) as websocket:
            await websocket.send(_pack_doubao_message(1, b"{}"))
            message = _unpack_doubao_message(await websocket.recv())
            if message["event"] != 50:
                raise RuntimeError(f"豆包 V3 建连失败: {_doubao_error_message(message)}")

            base_request = json.loads(json.dumps(request_body))
            text = str(base_request["req_params"].pop("text"))
            start_request = json.loads(json.dumps(base_request))
            start_request["event"] = 100
            await websocket.send(
                _pack_doubao_message(100, json.dumps(start_request, ensure_ascii=False).encode("utf-8"), session_id)
            )
            message = _unpack_doubao_message(await websocket.recv())
            if message["event"] != 150:
                raise RuntimeError(f"豆包 V3 会话启动失败: {_doubao_error_message(message)}")

            task_request = json.loads(json.dumps(base_request))
            task_request["event"] = 200
            task_request["req_params"]["text"] = text
            await websocket.send(
                _pack_doubao_message(200, json.dumps(task_request, ensure_ascii=False).encode("utf-8"), session_id)
            )
            await websocket.send(_pack_doubao_message(102, b"{}", session_id))

            while True:
                raw = await websocket.recv()
                if isinstance(raw, str):
                    raise RuntimeError(f"豆包 V3 返回了意外文本帧: {raw[:400]}")
                message = _unpack_doubao_message(raw)
                if message["type"] == 0x0F or message["event"] in {51, 153}:
                    raise RuntimeError(f"豆包 V3 合成失败: {_doubao_error_message(message)}")
                if message["type"] == 0x0B and message.get("payload"):
                    audio.extend(message["payload"])
                if message["event"] == 152:
                    break

            await websocket.send(_pack_doubao_message(2, b"{}"))
            while True:
                raw = await websocket.recv()
                if isinstance(raw, bytes) and _unpack_doubao_message(raw)["event"] == 52:
                    break
    except RuntimeError:
        raise
    except Exception as error:
        raise RuntimeError(f"豆包 V3 WebSocket 调用失败: {error}") from error
    if not audio:
        raise RuntimeError("豆包 V3 未返回音频数据。")
    return bytes(audio)


def call_doubao_api(request_body: dict[str, Any]) -> bytes:
    # Prefer the dedicated V3 API Key. The former Access Token slot is accepted as a
    # one-time compatibility path because early project setup stored the API Key there.
    api_key = os.environ.get("DOUBAO_TTS_API_KEY") or optional_keychain_secret(os.environ.get("DOUBAO_TTS_KEYCHAIN_SERVICE",DOUBAO_API_KEY_SERVICE)) or optional_keychain_secret(DOUBAO_TOKEN_SERVICE)
    if not api_key:
        raise RuntimeError("钥匙串缺少豆包 API Key；请运行 voiceover_cli.py configure-doubao。")
    resource_id = os.environ.get("DOUBAO_TTS_RESOURCE_ID") or "seed-tts-2.0"
    return asyncio.run(_call_doubao_v3(request_body, api_key, resource_id))


def probe_audio(path: Path) -> dict[str, Any]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {"status": "unverified", "reason": "ffprobe not found", "size_bytes": path.stat().st_size}
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration,size,bit_rate", "-of", "json", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"status": "failed", "error": result.stderr.strip(), "size_bytes": path.stat().st_size}
    payload = json.loads(result.stdout)
    fmt = payload.get("format", {})
    duration = float(fmt.get("duration", 0) or 0)
    return {
        "status": "passed" if duration > 0 and path.stat().st_size > 1024 else "failed",
        "duration_seconds": duration,
        "size_bytes": path.stat().st_size,
        "bit_rate": int(fmt.get("bit_rate", 0) or 0),
    }


def output_selection(out_dir: Path, registry: dict[str, Any], selection: dict[str, Any], metadata: dict[str, Any], text: str) -> dict[str, Any]:
    style = selection["selected_style"]
    language_code, provider = detect_language(text)
    speaker = (os.environ.get("DOUBAO_TTS_VOICE_TYPE") or registry["doubao"]["default_voice_type"]) if provider == "doubao" else style["speaker"]
    model = registry["doubao"]["model"] if provider == "doubao" else registry["google"]["default_model"]
    value = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input": metadata,
        "selection_mode": selection["selection_mode"],
        "selected_style": style["style_id"],
        "label": style["label"],
        "provider": provider,
        "speaker": speaker,
        "model": model,
        "language_code": language_code,
        "reason": selection["reason"],
        "scores": selection["scores"],
        "alternatives": selection["alternatives"],
        "prompt_hash": hashlib.sha256(style["prompt"].encode("utf-8")).hexdigest(),
        "source_refs": style.get("source_refs", []),
    }
    write_json(out_dir / "voice-selection.json", value)
    return value


def synthesize_one(
    text: str,
    style: dict[str, Any],
    registry: dict[str, Any],
    project_id: str,
    out_path: Path,
    cache_dir: Path,
    force: bool,
    audio_encoding: str = "MP3",
) -> dict[str, Any]:
    language_code, provider = detect_language(text)
    if provider == "doubao":
        voice_type = os.environ.get("DOUBAO_TTS_VOICE_TYPE") or registry["doubao"]["default_voice_type"]
        request_body = build_doubao_request(
            text,
            voice_type,
            audio_encoding,
            str(style.get("doubao_context") or style.get("prompt") or ""),
            int(style.get("doubao_speech_rate", 0)),
            int(style.get("doubao_loudness_rate", 0)),
        )
    else:
        request_body = build_google_request(text, style, registry["google"]["default_model"], language_code, audio_encoding)
    request_hash = canonical_hash({"provider": provider, "request": request_body})
    extension = ".wav" if audio_encoding == "LINEAR16" else ".mp3"
    cache_path = cache_dir / f"{request_hash}{extension}"
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cache_hit = cache_path.exists() and not force
    receipt_path = cache_path.with_suffix(cache_path.suffix + ".sha256")
    if cache_hit:
        if not receipt_path.is_file() or hashlib.sha256(cache_path.read_bytes()).hexdigest() != receipt_path.read_text().strip():
            raise ValueError("配音缓存身份缺失或不符，保留文件待检查；不自动重新付费生成")
        shutil.copy2(cache_path, out_path)
    else:
        audio = call_doubao_api(request_body) if provider == "doubao" else call_google_api(request_body, project_id)
        cache_path.write_bytes(audio)
        receipt_path.write_text(hashlib.sha256(audio).hexdigest())
        shutil.copy2(cache_path, out_path)
    return {
        "path": str(out_path.resolve()),
        "request_hash": request_hash,
        "text_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "provider": provider,
        "language_code": language_code,
        "cache_hit": cache_hit,
        "quality": probe_audio(out_path),
    }


def command_select(args: argparse.Namespace) -> int:
    registry = load_json(REGISTRY_PATH)
    narration, shots, metadata = read_input(args)
    out_dir = Path(args.output_dir).expanduser().resolve()
    selection = select_style(registry["styles"], shots, args.style_id)
    value = output_selection(out_dir, registry, selection, metadata, narration)
    print(json.dumps(value, ensure_ascii=False, indent=2))
    return 0


def command_synthesize(args: argparse.Namespace) -> int:
    registry = load_json(REGISTRY_PATH)
    narration, shots, metadata = read_input(args)
    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    selection = select_style(registry["styles"], shots, args.style_id)
    selection_record = output_selection(out_dir, registry, selection, metadata, narration)
    style = selection["selected_style"]
    preview_text = narration if args.mode == "full" else str(shots[0].get("narration", ""))
    preview_language, preview_provider = detect_language(preview_text)
    if preview_provider == "doubao":
        preview_voice = os.environ.get("DOUBAO_TTS_VOICE_TYPE") or registry["doubao"]["default_voice_type"]
        request_preview = build_doubao_request(
            preview_text,
            preview_voice,
            args.audio_encoding,
            str(style.get("doubao_context") or style.get("prompt") or ""),
            int(style.get("doubao_speech_rate", 0)),
            int(style.get("doubao_loudness_rate", 0)),
        )
    else:
        request_preview = build_google_request(preview_text, style, registry["google"]["default_model"], preview_language, args.audio_encoding)
    if args.dry_run:
        preview = {
            "dry_run": True,
            "selected_style": style["style_id"],
            "provider": preview_provider,
            "language_code": preview_language,
            "speaker": preview_voice if preview_provider == "doubao" else style["speaker"],
            "model": registry[preview_provider]["model" if preview_provider == "doubao" else "default_model"],
            "mode": args.mode,
            "request_hash": canonical_hash(request_preview),
            "text_bytes": len(narration.encode("utf-8")),
            "prompt_bytes": len(style["prompt"].encode("utf-8")),
            "audio_encoding": args.audio_encoding,
        }
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return 0

    generated: list[dict[str, Any]] = []
    cache_dir = out_dir / ".cache"
    extension = ".wav" if args.audio_encoding == "LINEAR16" else ".mp3"
    if args.mode == "full":
        generated.append(
            synthesize_one(
                narration,
                style,
                registry,
                args.project_id,
                out_dir / f"voiceover{extension}",
                cache_dir,
                args.force,
                args.audio_encoding,
            )
        )
    else:
        for index, shot in enumerate(shots, start=1):
            text = str(shot.get("narration", "")).strip()
            if not text:
                continue
            shot_id = str(shot.get("shot_id") or f"S{index:02d}")
            item = synthesize_one(
                text,
                style,
                registry,
                args.project_id,
                out_dir / "shots" / f"{shot_id}{extension}",
                cache_dir,
                args.force,
                args.audio_encoding,
            )
            item["shot_id"] = shot_id
            generated.append(item)
    manifest = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if generated and all(item["quality"]["status"] == "passed" for item in generated) else "failed",
        "google_project_id": args.project_id,
        "input": metadata,
        "selection": selection_record,
        "mode": args.mode,
        "generated": generated,
    }
    write_json(out_dir / "voiceover-manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if manifest["status"] == "passed" else 2


def command_validate(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).expanduser().resolve()
    manifest = load_json(manifest_path)
    checks = []
    for item in manifest.get("generated", []):
        path = Path(item["path"])
        checks.append({"path": str(path), "exists": path.exists(), "quality": probe_audio(path) if path.exists() else {"status": "failed"}})
    passed = bool(checks) and all(item["exists"] and item["quality"]["status"] == "passed" for item in checks)
    result = {"status": "passed" if passed else "failed", "manifest": str(manifest_path), "checks": checks}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if passed else 2


def command_configure_doubao(args: argparse.Namespace) -> int:
    security = shutil.which("security")
    if not security:
        raise RuntimeError("configure-doubao 只支持带 macOS 钥匙串的系统。")
    api_key = getpass.getpass("豆包 API Key（输入不会回显）: ").strip()
    if not api_key:
        raise ValueError("API Key 不能为空。")
    account = os.environ.get("USER", "univer")
    subprocess.run(
        [security, "add-generic-password", "-U", "-a", account, "-s", DOUBAO_API_KEY_SERVICE, "-w", api_key],
        check=True,
        capture_output=True,
        text=True,
    )
    print(json.dumps({"status": "configured", "provider": "doubao-v3", "storage": "macOS Keychain"}, ensure_ascii=False))
    return 0


def build_multi_request(source: dict[str, Any]) -> dict[str, Any]:
    prompt = str(source.get("prompt", "")).strip()
    turns = source.get("turns") or []
    speakers = source.get("speakers") or []
    if not prompt or not turns:
        raise ValueError("多说话人输入缺少 prompt 或 turns。")
    if len(speakers) != 2:
        raise ValueError("多说话人输入必须恰好配置两个 speakers。")
    aliases = {str(item.get("alias", "")) for item in speakers}
    if any(not alias.isalnum() for alias in aliases):
        raise ValueError("speaker alias 只能包含字母和数字。")
    normalized_turns = []
    for turn in turns:
        speaker = str(turn.get("speaker", ""))
        text = str(turn.get("text", "")).strip()
        if speaker not in aliases or not text:
            raise ValueError("turn 的 speaker 未登记或 text 为空。")
        normalized_turns.append({"speaker": speaker, "text": text})
    dialogue_bytes = len(json.dumps(normalized_turns, ensure_ascii=False).encode("utf-8"))
    prompt_bytes = len(prompt.encode("utf-8"))
    if dialogue_bytes > 4000 or prompt_bytes > 4000 or dialogue_bytes + prompt_bytes > 8000:
        raise ValueError("多说话人 prompt/turns 超过 Gemini-TTS 字节限制。")
    return {
        "input": {"prompt": prompt, "multiSpeakerMarkup": {"turns": normalized_turns}},
        "voice": {
            "languageCode": str(source.get("language_code") or "cmn-CN"),
            "modelName": str(source.get("model") or "gemini-2.5-pro-tts"),
            "multiSpeakerVoiceConfig": {
                "speakerVoiceConfigs": [
                    {"speakerAlias": str(item["alias"]), "speakerId": str(item["speaker_id"])}
                    for item in speakers
                ]
            },
        },
        "audioConfig": {"audioEncoding": "MP3"},
    }


def command_multi_synthesize(args: argparse.Namespace) -> int:
    source_path = Path(args.dialogue_json).expanduser().resolve()
    source = load_json(source_path)
    dialogue_text = " ".join(str(turn.get("text", "")) for turn in source.get("turns", []))
    if detect_language(dialogue_text)[1] == "doubao":
        raise ValueError("中文多说话人暂不允许继续走 Google；请拆成单人/逐镜头豆包合成。")
    request_body = build_multi_request(source)
    request_hash = canonical_hash(request_body)
    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        preview = {
            "dry_run": True,
            "model": request_body["voice"]["modelName"],
            "speakers": request_body["voice"]["multiSpeakerVoiceConfig"]["speakerVoiceConfigs"],
            "turn_count": len(request_body["input"]["multiSpeakerMarkup"]["turns"]),
            "request_hash": request_hash,
            "source_hash": canonical_hash(source),
        }
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return 0
    cache_dir = out_dir / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{request_hash}.mp3"
    output_path = out_dir / "dialogue-master.mp3"
    cache_hit = cache_path.exists() and not args.force
    if cache_hit:
        shutil.copy2(cache_path, output_path)
    else:
        cache_path.write_bytes(call_google_api(request_body, args.project_id))
        shutil.copy2(cache_path, output_path)
    generated = {
        "path": str(output_path.resolve()),
        "request_hash": request_hash,
        "cache_hit": cache_hit,
        "quality": probe_audio(output_path),
    }
    manifest = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if generated["quality"]["status"] == "passed" else "failed",
        "project_id": args.project_id,
        "input": {"source_path": str(source_path), "source_hash": canonical_hash(source)},
        "mode": "multi-speaker-structured",
        "speakers": request_body["voice"]["multiSpeakerVoiceConfig"]["speakerVoiceConfigs"],
        "turn_count": len(request_body["input"]["multiSpeakerMarkup"]["turns"]),
        "generated": [generated],
    }
    write_json(out_dir / "voiceover-manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if manifest["status"] == "passed" else 2


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    source = common.add_mutually_exclusive_group(required=True)
    source.add_argument("--storyboard")
    source.add_argument("--text-file")
    common.add_argument("--output-dir", required=True)
    common.add_argument("--style-id")
    select = sub.add_parser("select", parents=[common])
    select.set_defaults(func=command_select)
    synth = sub.add_parser("synthesize", parents=[common])
    synth.add_argument("--project-id", default=os.environ.get("GOOGLE_CLOUD_PROJECT", ""))
    synth.add_argument("--mode", choices=["full", "shots"], default="full")
    synth.add_argument("--dry-run", action="store_true")
    synth.add_argument("--force", action="store_true")
    synth.add_argument("--audio-encoding", choices=["MP3", "LINEAR16"], default="MP3")
    synth.set_defaults(func=command_synthesize)
    multi = sub.add_parser("multi-synthesize")
    multi.add_argument("--dialogue-json", required=True)
    multi.add_argument("--output-dir", required=True)
    multi.add_argument("--project-id", default=os.environ.get("GOOGLE_CLOUD_PROJECT", ""))
    multi.add_argument("--dry-run", action="store_true")
    multi.add_argument("--force", action="store_true")
    multi.set_defaults(func=command_multi_synthesize)
    validate = sub.add_parser("validate")
    validate.add_argument("--manifest", required=True)
    validate.set_defaults(func=command_validate)
    configure = sub.add_parser("configure-doubao", help="将豆包新版 API Key 安全写入 macOS 钥匙串")
    configure.add_argument("--app-id", required=False, help="旧版兼容参数；V3 新版调用不再使用")
    configure.set_defaults(func=command_configure_doubao)
    return root


def main() -> int:
    try:
        args = parser().parse_args()
        return args.func(args)
    except (ValueError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "failed", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
