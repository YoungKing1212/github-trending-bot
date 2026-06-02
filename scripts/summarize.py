#!/usr/bin/env python3
"""
Summarize GitHub repo with MiniMax API in Chinese.
API key is read from MINIMAX_API_KEY environment variable.
"""

import os
import sys
import json
import time
import requests


def get_api_key():
    """Get MiniMax API key from environment."""
    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        print("Error: MINIMAX_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    return api_key


def summarize_repo(api_key, name, description, language):
    """Use MiniMax API to generate Chinese summary."""

    prompt = f"""你是一个技术项目分析专家。请用中文简要概括以下GitHub项目，控制在3句话以内：

项目名：{name}
语言：{language}
英文描述：{description or '无'}

要求：
1. 输出必须是中文
2. 不要保留英文描述原文，必须翻译并提炼成中文
3. 输出控制在150字以内，不要换行
4. 请按以下格式输出：
【定位】一句话说明这是什么项目
【解决的问题】它主要解决什么痛点
【亮点】核心技术特点或优势"""

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'MiniMax-M2.7',
        'messages': [
            {'role': 'system', 'content': '你是一个简洁的技术项目分析助手，必须用中文输出，不要保留英文原文，输出控制在150字以内，不要换行。'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.3,
        'max_tokens': 300
    }

    for attempt in range(3):
        try:
            resp = requests.post(
                'https://api.minimaxi.com/v1/text/chatcompletion_v2',
                headers=headers,
                json=payload,
                timeout=60
            )
            resp.raise_for_status()
            data = resp.json()

            # Check for API errors
            base_resp = data.get('base_resp', {})
            if base_resp.get('status_code') != 0:
                error_msg = base_resp.get('status_msg', 'Unknown error')
                print(f"MiniMax API error for {name}: {error_msg} (attempt {attempt+1}/3)", file=sys.stderr)
                if attempt < 2:
                    time.sleep(2 ** attempt)
                continue

            choices = data.get('choices', [])
            if choices and len(choices) > 0:
                content = choices[0].get('message', {}).get('content', '')
                return content.strip()

        except Exception as e:
            print(f"MiniMax API error for {name} (attempt {attempt+1}/3): {e}", file=sys.stderr)
            if attempt < 2:
                time.sleep(2 ** attempt)

    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python summarize.py <trending_json_file>")
        sys.exit(1)

    api_key = get_api_key()

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Collect all unique repos to summarize (overall + all categories)
    # Use a dict to deduplicate by repo name
    repos_dict = {}
    
    # Add overall repos
    for repo in data.get('overall', []):
        repos_dict[repo['name']] = repo
    
    # Add category repos
    for category in ['ai_infra', 'middleware', 'other']:
        for repo in data.get(category, []):
            repos_dict[repo['name']] = repo
    
    repos_to_summarize = list(repos_dict.values())
    
    print(f"Summarizing {len(repos_to_summarize)} unique repos...", file=sys.stderr)

    for repo in repos_to_summarize:
        print(f"Summarizing {repo['name']}...", file=sys.stderr)
        summary = summarize_repo(
            api_key,
            repo['name'],
            repo['description'],
            repo['language']
        )
        repo['summary'] = summary or repo['description']

    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
