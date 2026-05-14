# GitHub Trending → 飞书

每日自动抓取 GitHub 热点项目，推送到飞书群。

## 文件结构

```
.
├── .github/workflows/daily-trending.yml   # GitHub Actions 定时任务
├── scripts/
│   ├── fetch_trending.py                  # 抓取 GitHub Trending
│   └── feishu_bot.py                      # 推送到飞书
└── README.md
```

## 部署步骤

### 1. 创建 GitHub 仓库

把本代码 push 到一个新的 GitHub 仓库（可以私有）。

### 2. 配置 Secrets

在仓库 Settings → Secrets and variables → Actions → New repository secret，添加：

| Secret Name | Value |
|------------|-------|
| `FEISHU_APP_ID` | cli_aa8f995946399bc4 |
| `FEISHU_APP_SECRET` | RC4s0qNUSUQcvGAb7yVlPgK6L2fxJKrR |
| `FEISHU_CHAT_ID` | oc_ad0f378be1d9edbb35879c62a1587dbb |
| `GITHUB_TOKEN` | （可选）你的 GitHub Personal Access Token，提高 API 限流 |

### 3. 确认飞书应用权限

在飞书开发者后台确保：
- 应用已发布
- 机器人能力已启用
- 权限 `im:message:send_as_bot` 已开通
- 应用已添加到「github热点追踪」群

### 4. 测试

进入 Actions 页面，手动触发 workflow，检查是否成功推送到飞书。

### 5. 定时运行

默认每天北京时间早上 9 点自动推送。

## 自定义

编辑 `scripts/fetch_trending.py` 中的关键词列表，调整分类规则。
