#!/usr/bin/env python3
"""
Send GitHub Trending summary to Feishu group via self-built app.
"""

import os
import sys
import json
import requests

APP_ID = os.environ.get('FEISHU_APP_ID', '')
APP_SECRET = os.environ.get('FEISHU_APP_SECRET', '')
CHAT_ID = os.environ.get('FEISHU_CHAT_ID', '')


def get_tenant_access_token():
    """Get tenant_access_token from Feishu."""
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'app_id': APP_ID,
        'app_secret': APP_SECRET
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    if data.get('code') != 0:
        raise RuntimeError(f"Failed to get token: {data}")
    
    return data['tenant_access_token']


def send_message(token, content):
    """Send text message to Feishu group."""
    url = 'https://open.feishu.cn/open-apis/im/v1/messages'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    params = {'receive_id_type': 'chat_id'}
    
    payload = {
        'receive_id': CHAT_ID,
        'msg_type': 'interactive',
        'content': json.dumps(content)
    }
    
    resp = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    if data.get('code') != 0:
        raise RuntimeError(f"Failed to send message: {data}")
    
    return data


def build_card(trending_data):
    """Build Feishu interactive card."""
    from datetime import datetime, timedelta
    date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    elements = []
    
    # Header
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"**📊 GitHub Trending {date_str}**"
        }
    })
    elements.append({"tag": "hr"})
    
    categories = [
        ('ai_infra', '🤖 AI Infra'),
        ('middleware', '🖥️ 后端中间件'),
        ('other', '📌 其他值得关注')
    ]
    
    for key, title in categories:
        repos = trending_data.get(key, [])
        if not repos:
            continue
        
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{title} ({len(repos)})**"
            }
        })
        
        for repo in repos:
            repo_text = (
                f"• [{repo['name']}]({repo['url']})  ⭐{repo['stars']}\n"
                f"  {repo['description']}\n"
                f"  `{repo['language']}` {repo['topics']}"
            )
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": repo_text
                }
            })
        
        elements.append({"tag": "hr"})
    
    # Footer
    elements.append({
        "tag": "note",
        "elements": [
            {
                "tag": "plain_text",
                "content": "自动推送，数据来源 GitHub API"
            }
        ]
    })
    
    return {
        "config": {"wide_screen_mode": True},
        "elements": elements
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python feishu_bot.py <trending_json_file>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        trending_data = json.load(f)
    
    print("Getting Feishu token...")
    token = get_tenant_access_token()
    
    print("Building message card...")
    card = build_card(trending_data)
    
    print("Sending to Feishu...")
    send_message(token, card)
    
    print("Done!")


if __name__ == '__main__':
    main()
