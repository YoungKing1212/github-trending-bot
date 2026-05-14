#!/usr/bin/env python3
"""
Fetch GitHub Trending repositories and categorize them.
"""

import requests
import re
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import json

# Categories based on topics and description keywords
AI_INFRA_KEYWORDS = [
    'llm', 'inference', 'vllm', 'sglang', 'ollama', 'transformer',
    'model-serving', 'gpu', 'cuda', 'triton', 'onnx', 'tensorrt',
    'langchain', 'llama', 'mistral', 'openai', 'anthropic',
    'embedding', 'vector', 'rag', 'fine-tune', 'peft', 'lora',
    'quantization', 'kv-cache', 'speculative', 'parallel',
    'ai-engineering', 'mlops', 'model-registry', 'diffusion',
    'stable-diffusion', 'comfyui', 'flux', 'mcp'
]

MIDDLEWARE_KEYWORDS = [
    'microservice', 'service-mesh', 'service-discovery', 'config',
    'gateway', 'load-balancer', 'proxy', 'rpc', 'grpc', 'dubbo',
    'nacos', 'consul', 'etcd', 'zookeeper', 'sentinel', 'hystrix',
    'circuit-breaker', 'rate-limit', 'middleware', 'message-queue',
    'kafka', 'rocketmq', 'rabbitmq', 'pulsar', 'redis', 'database',
    'cache', 'sharding', 'distributed', 'cluster', 'orchestration',
    'kubernetes', 'k8s', 'docker', 'container', 'istio', 'envoy',
    'prometheus', 'observability', 'tracing', 'logging'
]


def fetch_trending():
    """Fetch trending repos from GitHub Trending page."""
    import os
    
    headers = {
        'Accept': 'text/html',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    # Fetch daily trending for multiple languages
    all_repos = []
    urls = [
        'https://github.com/trending?since=daily',
        'https://github.com/trending/python?since=daily',
        'https://github.com/trending/go?since=daily',
        'https://github.com/trending/rust?since=daily',
        'https://github.com/trending/typescript?since=daily',
        'https://github.com/trending/java?since=daily',
    ]
    
    seen = set()
    for url in urls:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        # Parse HTML to extract repo info
        # GitHub trending page structure: <article class="Box-row">
        articles = resp.text.split('<article class="Box-row">')[1:]
        
        for article in articles:
            # Extract repo name
            match = re.search(r'<h2[^>]*>\s*<a[^>]*href="/([^/]+/[^/"]+)"', article)
            if not match:
                continue
            
            repo_name = match.group(1)
            if repo_name in seen:
                continue
            seen.add(repo_name)
            
            # Extract description
            desc_match = re.search(r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>', article, re.DOTALL)
            description = ''
            if desc_match:
                description = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()
            
            # Extract language
            lang_match = re.search(r'<span[^>]*itemprop="programmingLanguage"[^>]*>(.*?)</span>', article)
            language = lang_match.group(1).strip() if lang_match else 'Unknown'
            
            # Extract stars today
            stars_match = re.search(r'([\d,]+)\s*stars?\s*today', article, re.IGNORECASE)
            stars_today = stars_match.group(1) if stars_match else '?'
            
            all_repos.append({
                'full_name': repo_name,
                'html_url': f'https://github.com/{repo_name}',
                'description': description,
                'language': language,
                'stars_today': stars_today,
                'topics': [],
                'stargazers_count': 0  # Will be filled later if needed
            })
    
    return all_repos


def categorize_repo(repo):
    """Categorize a repo based on topics and description."""
    text = ' '.join([
        repo.get('description', '') or '',
        ' '.join(repo.get('topics', [])),
        repo.get('name', '')
    ]).lower()
    
    ai_score = sum(1 for k in AI_INFRA_KEYWORDS if k in text)
    mw_score = sum(1 for k in MIDDLEWARE_KEYWORDS if k in text)
    
    if ai_score > mw_score and ai_score > 0:
        return 'ai_infra'
    elif mw_score > ai_score and mw_score > 0:
        return 'middleware'
    else:
        return 'other'


def format_repo(repo):
    """Format a repo for output."""
    stars_str = repo.get('stars_today', '?')
    
    description = repo.get('description', '') or 'No description'
    if len(description) > 120:
        description = description[:117] + '...'
    
    topics = repo.get('topics', [])[:3]
    topics_str = ' '.join([f'[{t}]' for t in topics]) if topics else ''
    
    return {
        'name': repo.get('full_name', 'unknown/repo'),
        'url': repo.get('html_url', ''),
        'stars': f"+{stars_str}",
        'description': description,
        'topics': topics_str,
        'language': repo.get('language', '') or 'Unknown'
    }


def main():
    """Main entry point."""
    pass


def run_fetch():
    """Fetch and return trending data."""
    try:
        repos = fetch_trending()
    except Exception as e:
        print(f"Error fetching trending: {e}", file=sys.stderr)
        return {}
    
    categories = defaultdict(list)
    
    for repo in repos:
        cat = categorize_repo(repo)
        categories[cat].append(format_repo(repo))
    
    # Limit each category to top 5
    result = {}
    for cat in ['ai_infra', 'middleware', 'other']:
        result[cat] = categories[cat][:5]
    
    return result


if __name__ == '__main__':
    print(f"Fetching GitHub trending for {(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}...", file=sys.stderr)
    result = run_fetch()
    print(json.dumps(result, ensure_ascii=False, indent=2))
