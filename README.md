# 台风实时位置 · Typhoon Realtime

基于中央气象台 (nmc) 官方数据的台风实时追踪地图。纯静态前端，浏览器**直连 nmc**，无需任何后端服务器。

## 特性
- 🌀 实时台风位置、强度、移动方向（脉冲标记）
- 📍 实况轨迹 + 官方预报路径（BABJ）
- 🌪 风圈半径可视化
- 📏 距昆山距离实时计算
- 🗺 高德 / OpenStreetMap / 卫星影像 底图切换
- 🔄 每 60 秒自动刷新

## 使用
访问已部署站点：

https://wolfzzzzz.github.io/typhoon/

切换台风：在 URL 后加 `?id=<台风编号>`，例如 `?id=3257931`。

## 数据源
中央气象台台风实况接口：`https://typhoon.nmc.cn/weatherservice/typhoon/jsons/view_<id>`

前端直接 `fetch` 该接口（nmc 已开启 CORS），并在浏览器内完成 JSONP 解析与轨迹转换，因此无需自建代理或服务器。

## 本地预览
```bash
cd typhoon-realtime
python3 -m http.server 8765
# 打开 http://127.0.0.1:8765
```

> 需要本地代理版本（自托管后端、带缓存）可参考 `proxy_server.py`。
