#!/usr/bin/env python3
"""
Summarize GitHub repo with MiniMax API in Chinese.
"""

import os
import sys
import json
import requests

BASE_URL = os.environ.get('MINIMAX_BASE_URL', 'https://api.minimaxi.com')
API_KEY = os.environ.get('MINIMAX_API_KEY', '')


def summarize_repo(name, description, language):
    """Use MiniMax to generate Chinese summary."""
    if not API_KEY:
        return None
    
    prompt = f"""你是一个技术项目分析专家。请用中文简要概括以下GitHub项目，控制在3句话以内：

项目名：{name}
语言：{language}
英文描述：{description or '无'}

请按以下格式输出：
【定位】一句话说明这是什么项目
【解决的问题】它主要解决什么痛点
【亮点】核心技术特点或优势"""

    url = f"{BASE_URL}/v1/text/chatcompletion_v2"
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'MiniMax-M2.7',
        'messages': [
            {'role': 'system', 'content': '你是一个简洁的技术项目分析助手，输出控制在100字以内。'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.3,
        'max_tokens': 200
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        # MiniMax response format
        choices = data.get('choices', [])
        if choices and len(choices) > 0:
            content = choices[0].get('message', {}).get('content', '')
            return content.strip()
        
        return None
    except Exception as e:
        print(f"MiniMax API error: {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python summarize.py <trending_json_file>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for category in ['ai_infra', 'middleware', 'other']:
        repos = data.get(category, [])
        for repo in repos:
            print(f"Summarizing {repo['name']}...", file=sys.stderr)
            summary = summarize_repo(
                repo['name'],
                repo['description'],
                repo['language']
            )
            repo['summary'] = summary or repo['description']
    
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
