#!/usr/bin/env python3
"""Read-only first-install checks. Never reads secrets, authenticates, or calls a service."""
import argparse
import importlib.util
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def command_output(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        return result.stdout if result.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def inspect_environment():
    tools = {name: shutil.which(name) for name in ("ffmpeg", "ffprobe", "node", "npm", "gcloud")}
    node_output = command_output([tools["node"], "--version"]) if tools["node"] else ""
    node_match = re.match(r"v?(\d+)", node_output.strip())
    node_major = int(node_match.group(1)) if node_match else 0
    encoders = command_output([tools["ffmpeg"], "-hide_banner", "-encoders"]) if tools["ffmpeg"] else ""
    modules = {name: importlib.util.find_spec(name) is not None for name in ("numpy", "websockets", "certifi")}
    versions = {}
    for name in ("numpy", "websockets"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    websocket_match = re.match(r"(\d+)", versions["websockets"] or "")
    websocket_major = int(websocket_match.group(1)) if websocket_match else 0
    numpy_match = re.match(r"(\d+)\.(\d+)", versions["numpy"] or "")
    numpy_version = tuple(map(int, numpy_match.groups())) if numpy_match else (0, 0)
    plugin = ROOT / "plugins/codex-video-review"
    checks = {
        "python310": sys.version_info >= (3, 10),
        "ffmpeg": bool(tools["ffmpeg"]),
        "ffprobe": bool(tools["ffprobe"]),
        "libx264": "libx264" in encoders,
        "node18": node_major >= 18,
        "node20": node_major >= 20,
        "npm": bool(tools["npm"]),
        "numpy>=1.26,<3": modules["numpy"] and (1, 26) <= numpy_version < (3, 0),
        "websockets>=15,<17": modules["websockets"] and 15 <= websocket_major < 17,
        "review_bundle": (plugin / "dist/widget.js").is_file(),
        "review_dependencies": all((plugin / "node_modules" / name).is_dir() for name in
                                   ("@modelcontextprotocol/sdk", "@modelcontextprotocol/ext-apps", "zod")),
    }
    requirements = {
        "basic": ("基础制作/导出", ["python310", "ffmpeg", "ffprobe", "libx264"]),
        "library": ("建库/分类/文字检索", ["python310"]),
        "reference": ("本地参考拆解", ["python310", "ffmpeg", "ffprobe", "node18"]),
        "analysis": ("本地分析证据", ["python310", "ffmpeg", "ffprobe", "numpy>=1.26,<3"]),
        "voice": ("配音依赖（不验证账号）", ["python310", "ffmpeg", "ffprobe", "websockets>=15,<17"]),
        "music": ("音乐依赖（不验证账号）", ["python310", "ffmpeg", "ffprobe"]),
        "review": ("打标运行依赖（不验证宿主连接）", ["node20", "npm", "review_bundle", "review_dependencies"]),
    }
    features = {}
    for name, (label, needed) in requirements.items():
        missing = [item for item in needed if not checks[item]]
        features[name] = {"label": label, "runtimeReady": not missing, "missing": missing}
    return {
        "python": sys.version.split()[0],
        "pythonExecutable": sys.executable,
        "nodeMajor": node_major or None,
        "moduleVersions": versions,
        "features": features,
        "recommendedCertifiInstalled": modules["certifi"],
        "services": {
            "googleMusicKey": {
                "environmentVariableSet": any(name in os.environ for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY")),
                "keychain": "not_read; saved key may exist",
            },
            "doubaoVoiceKey": {
                "environmentVariableSet": "DOUBAO_TTS_API_KEY" in os.environ,
                "keychain": "not_read; saved key may exist",
            },
            "googleCloud": {
                "gcloudOnPath": bool(tools["gcloud"]),
                "projectEnvironmentVariableSet": "GOOGLE_CLOUD_PROJECT" in os.environ,
                "adcLogin": "not_checked",
            },
        },
        "cloudRequests": 0,
        "credentialsRead": False,
        "meaning": "Runtime presence only. Keys, account permissions, billing, host AI and video quality are not verified.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="首次安装只读自检：不读密钥、不登录、不发请求、不修改配置。")
    sub = parser.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor")
    doctor.add_argument("--feature", choices=["basic", "library", "reference", "analysis", "voice", "music", "review", "all"], default="basic")
    doctor.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = inspect_environment()
    selected = list(report["features"]) if args.feature == "all" else [args.feature]
    report["requestedFeatures"] = selected
    report["requestedRuntimeReady"] = all(report["features"][name]["runtimeReady"] for name in selected)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("首次安装检查（只读，无云端调用）")
        print("当前 Python：" + report["pythonExecutable"])
        for name, value in report["features"].items():
            state = "依赖齐全" if value["runtimeReady"] else "缺少 " + ", ".join(value["missing"])
            print(value["label"] + "：" + state)
        print("以上只检查运行依赖；未读取钥匙串、未验证密钥/登录/权限/额度。")
        print("首次做片可只用已有素材，不需要配音/音乐/分析服务密钥。")
        print("下一步：阅读 docs/首次使用.md；服务配置见 docs/密钥与服务配置.md。")
    return 0 if report["requestedRuntimeReady"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
