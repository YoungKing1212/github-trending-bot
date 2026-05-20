#!/usr/bin/env python3
"""
Summarize GitHub repo with SiliconFlow API in Chinese.
Uses OpenAI-compatible API via SiliconFlow.
API key is read from SILICONFLOW_API_KEY environment variable.
"""

import os
import sys
import json
import time
from openai import OpenAI


def get_client():
    """Create OpenAI client pointing to SiliconFlow API."""
    api_key = os.environ.get("SILICONFLOW_API_KEY")
    if not api_key:
        print("Error: SILICONFLOW_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    return OpenAI(
        api_key=api_key,
        base_url="https://api.siliconflow.cn/v1",
        timeout=120.0,
        max_retries=3,
    )


def summarize_repo(client, name, description, language):
    """Use SiliconFlow API to generate Chinese summary."""

    prompt = f"""你是一个技术项目分析专家。请用中文简要概括以下GitHub项目，控制在3句话以内：

项目名：{name}
语言：{language}
英文描述：{description or '无'}

要求：
1. 输出必须是中文
2. 不要保留英文描述原文，必须翻译并提炼成中文
3. 请按以下格式输出：
【定位】一句话说明这是什么项目
【解决的问题】它主要解决什么痛点
【亮点】核心技术特点或优势"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V4-Flash",
                max_tokens=4096,
                messages=[
                    {"role": "system", "content": "你是一个专业的技术项目分析专家，必须用中文输出，不要保留英文原文。"},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"SiliconFlow API error for {name} (attempt {attempt+1}/3): {e}", file=sys.stderr)
            if attempt < 2:
                time.sleep(2 ** attempt)
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python summarize.py <trending_json_file>")
        sys.exit(1)

    client = get_client()

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Only summarize overall top 10 (to avoid timeout)
    repos_to_summarize = data.get('overall', [])[:10]

    for repo in repos_to_summarize:
        print(f"Summarizing {repo['name']}...", file=sys.stderr)
        summary = summarize_repo(
            client,
            repo['name'],
            repo['description'],
            repo['language']
        )
        repo['summary'] = summary or repo['description']

    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
