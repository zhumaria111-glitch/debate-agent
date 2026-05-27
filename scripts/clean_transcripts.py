"""Clean raw AI subtitle transcripts into debate_01.txt format.

Usage:
    export ANTHROPIC_API_KEY=sk-xxx
    python3 scripts/clean_transcripts.py

Processes all .txt files in data/eval/ and writes cleaned versions
as *_cleaned.txt in the same directory.
"""

import os
import sys
from pathlib import Path

import anthropic

# Load .env file if present (prefer env vars over .env)
def _load_env():
    """Load environment variables from project root .env file."""
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        if key not in os.environ:
            os.environ[key] = val

_load_env()

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

if not API_KEY:
    print("Error: ANTHROPIC_API_KEY not set.")
    sys.exit(1)

client = anthropic.Anthropic(api_key=API_KEY, base_url=BASE_URL)

CLEANING_PROMPT = """你是一个专业的辩论文字稿整理专家。你的任务是把 AI 语音识别生成的原始字幕整理成结构化的辩论文字稿。

原始字幕的问题：
- 没有标点符号
- 按字幕时间切分，不是按语义切分，句子碎片化
- 没有发言人标注
- 混杂了主持人闲聊、广告口播等非辩论内容

你需要输出的格式：

1. 删除开场闲聊、广告口播、主持人寒暄（直接跳到辩论开始）
2. 将碎片化的字幕行合并为完整的、有标点符号的段落
3. 根据上下文推断发言人角色，标注为：正方一辩/正二/正三/正四 或 反方一辩/反二/反三/反四
4. 标注辩论环节：正方一辩陈词、反四质询正一、正方二辩陈词、反一质询正二...自由辩论、正方结辩、反方结辩
5. 每段发言保持完整，不要再次碎片化

参考输出格式：

cut-off
正方一辩陈词：
谢谢主席，大家好。当我方说起...(完整的立论内容)...

cut-off
反四质询正一：
反四：(问题)
正一：(回答)
反四：(追问)
正一：(回答)

请直接输出整理后的文字稿，不要输出任何解释性文字。"""


def clean_transcript(raw_text: str) -> str:
    """Send raw transcript to Claude for cleaning."""
    # If text is short enough, do it in one pass
    if len(raw_text) < 25000:
        return _call_claude(raw_text)

    # For long transcripts, split into chunks and process
    chunks = _split_into_chunks(raw_text, chunk_size=20000)
    cleaned_chunks = []
    for i, chunk in enumerate(chunks):
        print(f"  Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
        chunk_prompt = CLEANING_PROMPT + (
            f"\n注意：这是一场辩论的第 {i+1}/{len(chunks)} 部分。"
            f"请只整理这一部分的文字稿。"
        )
        result = _call_claude(chunk, system=chunk_prompt)
        cleaned_chunks.append(result)

    return "\n\n".join(cleaned_chunks)


def _call_claude(text: str, system: str = "") -> str:
    """Call Claude API to clean text."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=system or CLEANING_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    # Handle both TextBlock and ThinkingBlock in response
    for block in response.content:
        if getattr(block, "type", "") == "text":
            return block.text
    # Fallback for older SDK versions
    return response.content[0].text


def _split_into_chunks(text: str, chunk_size: int = 20000) -> list[str]:
    """Split text into roughly equal chunks at paragraph boundaries."""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) < chunk_size:
            current += para + "\n\n"
        else:
            if current:
                chunks.append(current.strip())
            current = para + "\n\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


def main():
    # Use path relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    eval_dir = os.path.join(project_root, "data", "eval")
    files = sorted([
        f for f in os.listdir(eval_dir)
        if f.endswith(".txt") and "_clean" not in f and "cleaned" not in f
    ])

    for filename in files:
        filepath = os.path.join(eval_dir, filename)

        # Skip files that are already clean (like debate_01.txt)
        with open(filepath, "r") as f:
            first_line = f.readline()
        if "文字稿复盘" in first_line or "cut-off" in first_line:
            print(f"Skipping {filename} (already clean)")
            continue

        print(f"Cleaning {filename}...")
        with open(filepath, "r") as f:
            raw_text = f.read()

        cleaned = clean_transcript(raw_text)

        out_name = filename.replace(".txt", "_cleaned.txt")
        out_path = os.path.join(eval_dir, out_name)
        with open(out_path, "w") as f:
            f.write(cleaned)
        print(f"  -> {out_path} ({len(cleaned)} chars)")


if __name__ == "__main__":
    main()
