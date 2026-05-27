#!/usr/bin/env python3
"""
B站视频 AI 字幕 → 逐字稿文字稿

用法:
    python3 bili_to_txt.py "https://www.bilibili.com/video/BV1uY4y1m7hb"            # 单P视频
    python3 bili_to_txt.py "https://www.bilibili.com/video/BV1uo4y1f7Ba?p=2"        # 指定分P
    python3 bili_to_txt.py BV1uY4y1m7hb -o debate_custom.txt                        # 自定义输出
    python3 bili_to_txt.py "https://www.bilibili.com/video/BVxxx" --json             # 仅获取信息

依赖: yt-dlp, Python 3.9+
前置: 将 B站 Cookie 写入 data/cookies/bilibili.txt（Netscape 格式）
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COOKIE_FILE = PROJECT_ROOT / "data" / "cookies" / "bilibili.txt"
EVAL_DIR = PROJECT_ROOT / "data" / "eval"
TEMP_DIR = PROJECT_ROOT / "data" / "temp"

BILI_API_VIEW = "https://api.bilibili.com/x/web-interface/view"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def load_cookies() -> str:
    """从文件加载 Cookie，转为 curl 可用的 header 值。"""
    if not COOKIE_FILE.exists():
        print(f"[错误] Cookie 文件不存在: {COOKIE_FILE}")
        print("请创建该文件，写入浏览器中 bilibili.com 的 Cookie（Netscape 或 key=value 格式均可）")
        sys.exit(1)

    text = COOKIE_FILE.read_text()
    # Netscape 格式: 跳过注释行和空行
    if text.startswith("# Netscape"):
        cookies = []
        for line in text.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 7:
                cookies.append(f"{parts[5]}={parts[6]}")
        return "; ".join(cookies)
    # 纯 key=value 格式（每行一个或分号分隔）
    return text.replace("\n", "; ")


def extract_bv_page(url: str) -> tuple[str, int]:
    """从 B站 URL 提取 BV 号和分 P 号。"""
    bv_match = re.search(r"(BV[a-zA-Z0-9]+)", url)
    if not bv_match:
        # 可能直接传了 BV 号
        if url.startswith("BV"):
            return url, 1
        raise ValueError(f"无法从 URL 中提取 BV 号: {url}")

    bv = bv_match.group(1)
    p_match = re.search(r"[?&]p=(\d+)", url)
    page = int(p_match.group(1)) if p_match else 1
    return bv, page


def api_get(url: str, cookie_str: str) -> dict:
    """带 Cookie 的 GET 请求，返回 JSON。"""
    req = urllib.request.Request(url, headers={
        "Cookie": cookie_str,
        "Referer": "https://www.bilibili.com",
        "User-Agent": UA,
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_meta(bv: str, page: int, cookie_str: str) -> dict:
    """获取视频元信息和指定分P的 cid。"""
    data = api_get(f"{BILI_API_VIEW}?bvid={bv}", cookie_str)["data"]

    pages = data.get("pages", [data])
    if page > len(pages):
        raise ValueError(f"分P号 {page} 超出范围（共 {len(pages)} 个分P）")

    target = pages[page - 1]
    return {
        "aid": data["aid"],
        "bvid": bv,
        "cid": target["cid"],
        "title": data["title"],
        "part": target.get("part", data["title"]),
        "duration": target["duration"],
        "owner": data["owner"]["name"],
        "page": page,
        "total_pages": len(pages),
    }


def download_subs(bv: str, page: int, output_stem: Path) -> Path:
    """用 yt-dlp 下载 AI 字幕，返回 .srt 文件路径。"""
    url = f"https://www.bilibili.com/video/{bv}"
    if page > 1:
        url += f"?p={page}"

    cmd = [
        "yt-dlp",
        "--cookies", str(COOKIE_FILE),
        "--write-auto-subs",
        "--sub-lang", "ai-zh",
        "--skip-download",
        "-o", str(output_stem),
        url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[yt-dlp 错误]", result.stderr[-500:])
        raise RuntimeError("字幕下载失败")

    srt_path = Path(str(output_stem) + ".ai-zh.srt")
    if not srt_path.exists():
        raise FileNotFoundError(f"字幕文件未生成: {srt_path}")
    return srt_path


def srt_to_text(srt_path: Path) -> str:
    """SRT → 纯文本，保留段落空行。"""
    content = srt_path.read_text()
    lines = content.split("\n")
    text_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            if text_lines and text_lines[-1] != "":
                text_lines.append("")
            continue
        if re.match(r"^\d+$", line):
            continue
        if re.match(r"^\d{2}:\d{2}:\d{2},\d{3} -->", line):
            continue
        text_lines.append(line)

    text = "\n".join(text_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def build_header(meta: dict, url: str) -> str:
    """根据元信息生成文件头。"""
    lines = [
        f"# {meta['title']}丨{meta['part']}",
        "",
        f"视频链接：{url}",
        f"上传者：{meta['owner']}",
        f"时长：{meta['duration'] // 60} 分 {meta['duration'] % 60} 秒",
        f"字幕类型：AI自动生成字幕（中文）",
        "说明：以下为AI语音识别生成的逐字稿，不含标点符号和发言人标注。",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="B站视频 AI 字幕 → 逐字稿")
    parser.add_argument("url", help="B站视频链接 或 BV 号")
    parser.add_argument("-o", "--output", help="输出文件路径（默认: data/eval/debate_XX.txt）")
    parser.add_argument("--json", action="store_true", help="仅打印视频元信息，不下载字幕")
    parser.add_argument("--keep-srt", action="store_true", help="保留中间 .srt 文件")
    args = parser.parse_args()

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/5] 加载 Cookie...")
    cookie_str = load_cookies()

    print("[2/5] 解析 URL...")
    bv, page = extract_bv_page(args.url)

    print("[3/5] 获取视频信息...")
    meta = fetch_meta(bv, page, cookie_str)
    print(f"      标题: {meta['title']}")
    print(f"      分P: {meta['page']}/{meta['total_pages']} — {meta['part']}")
    print(f"      时长: {meta['duration'] // 60} 分 {meta['duration'] % 60} 秒")
    print(f"      上传者: {meta['owner']}")

    if args.json:
        print(json.dumps(meta, ensure_ascii=False, indent=2))
        return

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        # 自动编号: data/eval/debate_XX.txt
        existing = sorted(EVAL_DIR.glob("debate_*.txt"))
        next_num = len(existing) + 1
        output_path = EVAL_DIR / f"debate_{next_num:02d}.txt"

    stem = TEMP_DIR / output_path.stem

    print("[4/5] 下载 AI 字幕 (yt-dlp)...")
    srt_path = download_subs(bv, page, stem)

    print("[5/5] 清洗文本...")
    text = srt_to_text(srt_path)

    header = build_header(meta, url := f"https://www.bilibili.com/video/{bv}" +
                          (f"?p={page}" if meta["total_pages"] > 1 else ""))

    output_path.write_text(header + text)
    print(f"      已写入: {output_path} ({len(text):,} 字)")

    # 清理临时文件
    if not args.keep_srt:
        srt_path.unlink(missing_ok=True)
        print("      已清理临时 .srt")


if __name__ == "__main__":
    main()
