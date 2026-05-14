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
    """Build Feishu interactive card with better visuals."""
    from datetime import datetime, timedelta
    date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Color mapping for categories
    cat_colors = {
        'overall': 'blue',
        'ai_infra': 'purple',
        'middleware': 'green', 
        'other': 'grey'
    }
    
    # Language icons
    lang_icons = {
        'Python': '🐍',
        'Go': '🔵',
        'Rust': '⚙️',
        'TypeScript': '📘',
        'JavaScript': '🟨',
        'Java': '☕',
        'Swift': '🍎',
        'C++': '⚡',
        'C': '🔧',
        'Ruby': '💎',
        'Jupyter Notebook': '📓'
    }
    
    elements = []
    
    # Header with gradient-like style
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"**📊 GitHub Trending {date_str}**"
        }
    })
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"<font color='grey'>每日自动推送 · 共 {len(trending_data.get('overall', [])) + len(trending_data.get('ai_infra', [])) + len(trending_data.get('middleware', [])) + len(trending_data.get('other', []))} 个项目</font>"
        }
    })
    elements.append({"tag": "hr"})
    
    def add_repo_section(repo, color='blue'):
        """Add a single repo card."""
        desc = repo.get('summary', repo.get('description', ''))
        desc = desc.replace('\n', ' ').strip()
        if len(desc) > 150:
            desc = desc[:147] + '...'
        
        lang = repo.get('language', 'Unknown')
        lang_icon = lang_icons.get(lang, '📁')
        
        # Star count with color
        stars = repo['stars']
        
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": (
                    f"{lang_icon} **[{repo['name']}]({repo['url']})**  <font color='orange'>⭐{stars}</font>\n"
                    f"<font color='grey'>{desc}</font>\n"
                    f"`{lang}`"
                )
            }
        })
    
    # Overall top 10
    overall = trending_data.get('overall', [])
    if overall:
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**🔥 总榜 Top {len(overall)}**"
            }
        })
        
        for repo in overall:
            add_repo_section(repo, 'blue')
        
        elements.append({"tag": "hr"})
    
    # Categories with colored headers
    categories = [
        ('ai_infra', '🤖 AI Infra', 'purple'),
        ('middleware', '🖥️ 后端中间件', 'green'),
        ('other', '📌 其他值得关注', 'grey')
    ]
    
    for key, title, color in categories:
        repos = trending_data.get(key, [])
        if not repos:
            continue
        
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{title}** <font color='{color}'>({len(repos)})</font>"
            }
        })
        
        for repo in repos:
            add_repo_section(repo, color)
        
        elements.append({"tag": "hr"})
    
    # Footer
    elements.append({
        "tag": "note",
        "elements": [
            {
                "tag": "plain_text",
                "content": "🤖 自动推送 · 数据来源 GitHub · 项目概括由 AI 生成"
            }
        ]
    })
    
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "template": "blue",
            "title": {
                "tag": "plain_text",
                "content": f"GitHub Trending {date_str}"
            }
        },
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
