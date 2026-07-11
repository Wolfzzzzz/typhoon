# 台风实时位置 · Typhoon Realtime

基于中央气象台 (nmc) 官方数据的台风实时追踪地图，部署在 GitHub Pages。

## 为什么用「同源快照」
浏览器直接跨域请求 nmc 在部分网络/浏览器下会被拦截（CORS 或境外 IP 限制），公共 CORS 代理也大多不可用。
因此架构改为：**由一台可访问 nmc 的机器（你的 Mac）定时抓取数据 → 解析为 JSON → 推送到仓库 → 前端从 GitHub Pages 同源读取**。
前端永远只请求同源的 `data/<id>.json`，必然可达，告别「数据加载失败」。

## 特性
- 🌀 实时台风位置、强度、移动方向（脉冲标记）
- 📍 实况轨迹 + 官方预报路径（BABJ）
- 🌪 风圈半径可视化
- 📏 距昆山距离实时计算
- 🗺 高德 / OpenStreetMap / 卫星影像 底图切换
- 🔄 页面每 60 秒刷新；数据快照每 10 分钟由 Mac 更新一次

## 使用
访问：

https://wolfzzzzz.github.io/typhoon/

切换台风：URL 后加 `?id=<台风编号>`，例如 `?id=3257931`。
（快照中已有的编号直接命中；否则前端会尝试直连 nmc 兜底。）

## 目录结构
- `index.html` —— 前端（Leaflet + 高德底图，同源读取 `data/*.json`）
- `build_data.py` —— 抓取 nmc 并生成 `data/*.json` 快照
- `data/3257931.json` —— 巴威 BAVI 的快照数据
- `_api_push.py` —— 通过 GitHub API 推送（读 `~/.typhoon_github_token`）

## 本地预览
```bash
cd site
python3 build_data.py          # 生成 data/
python3 -m http.server 8765    # 打开 http://127.0.0.1:8765
```

## 让数据保持新鲜（Mac 定时任务）
本机运行（需代理可访问 nmc，且 `~/.typhoon_github_token` 已写入 PAT）：
```bash
launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.wolfzzzzz.typhoon.plist
```
该 plist 每 10 分钟执行 `build_data.py` + `_api_push.py`，自动更新仓库数据。
