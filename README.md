# 🎬 Movie Hunter — 影视猎手

输入影视名称（支持模糊搜索），即刻获取来自 **TMDB** 的详细资料。

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![TMDB API](https://img.shields.io/badge/API-TMDB%20v3-02a4d4.svg)](https://www.themoviedb.org/documentation/api)

## ✨ 功能特性

- 🔍 **模糊搜索** — 电影、电视剧、人物一网打尽
- 📋 **详细资料** — 剧情简介、演员表、幕后团队、票房、相似影片
- 📺 **剧集详情** — 按季浏览，单集详情、剧照
- 👤 **人物档案** — 个人简介、参演作品
- ⚙️ **灵活配置** — TMDB API Key + 代理设置，支持 HTTP/HTTPS/SOCKS5
- 🔐 **管理员密码保护** — 进入设置前需验证密码，密码哈希存储，安全防泄密
- 👁️ **敏感信息隐藏** — API Key 与密码默认密码样式显示，可切换显隐
- 💾 **本地缓存** — 自动缓存 API 响应，减少重复请求（TTL 1 小时）
- 🖼️ **图片代理** — 所有 TMDB 图片经后端代理中转，内网/被墙环境也能正常加载
- 🌐 **双版本** — 网页版 + Windows 桌面版（pywebview）+ 独立 EXE
- 🐳 **Docker 部署** — 一行命令部署到 NAS 或服务器
- 🎨 **精美 UI** — 深色电影风格，毛玻璃效果，流畅动画

## 🚀 快速开始

### 网页版（推荐 NAS/服务器）

```bash
# Docker Compose（推荐）
git clone https://github.com/zixiang0520/movie-hunter.git
cd movie-hunter
docker compose up -d

# 访问 http://your-server-ip:8765
```

### 网页版（本地开发）

```bash
git clone https://github.com/zixiang0520/movie-hunter.git
cd movie-hunter
pip install -r requirements.txt
python backend/main.py
# 访问 http://localhost:8765
```

### Windows 桌面版

```bash
git clone https://github.com/zixiang0520/movie-hunter.git
cd movie-hunter
pip install -r requirements.txt
python desktop.py
```

### Windows EXE（免安装，推荐）

直接下载 [Releases](https://github.com/zixiang0520/movie-hunter/releases) 页面预编译的 `MovieHunter.exe`，双击即可运行，无需安装 Python。

> 如果需要从源码自行打包，见下方 [EXE 打包](#-exe-打包) 章节。

## 📁 项目结构

```
movie-hunter/
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI 主应用（API 路由 + 图片代理 + 静态文件服务）
│   ├── models.py        # Pydantic 数据模型（TMDB 数据 + 应用设置）
│   ├── service.py       # 业务逻辑层（聚合 TMDB 数据为详情对象）
│   ├── tmdb_client.py   # TMDB API 客户端（代理支持 + 本地缓存）
│   └── settings.py      # 配置读写（settings.json）
├── web/
│   ├── index.html       # 网页入口（含密码验证弹窗 + 设置弹窗）
│   ├── style.css        # 样式表（深色电影主题）
│   └── app.js           # 前端交互逻辑
├── desktop.py           # Windows 桌面版启动器（pywebview）
├── build_exe.py         # PyInstaller 打包脚本（Windows 使用）
├── requirements.txt     # Python 依赖
├── Dockerfile           # Docker 镜像
├── docker-compose.yml   # Docker Compose 配置
├── deploy.sh            # NAS Docker 部署脚本
├── config/              # 运行时自动生成（不提交到 Git）
│   └── settings.json    # 用户配置（含 API Key、代理、密码哈希）
└── cache/               # API 响应缓存目录（不提交到 Git）
```

## ⚙️ 配置说明

首次启动后访问设置页面（右上角 ⚙️ 按钮），需要配置：

### 1. TMDB API Key（必填）

1. 访问 [TMDB 网站](https://www.themoviedb.org/signup) 注册账号
2. 前往 [API 设置页面](https://www.themoviedb.org/settings/api) 申请 Key
3. 在 Movie Hunter 设置页填入 Key（默认密码样式显示，点击 👁️ 可显隐）

### 2. 代理设置（可选）

国内用户如果无法直连 TMDB，可以配置代理。Movie Hunter 支持：

| 代理类型 | 说明 |
|---------|------|
| HTTP / HTTPS | 适用于 v2raya、Clash、Privoxy 等 |
| SOCKS5 / SOCKS5h | 适用于 Shadowsocks、Hysteria 等 |

> 所有 TMDB 图片也通过代理中转，不会出现图片加载失败的问题。

### 3. 管理员密码

在设置页底部的「修改管理员密码」中输入密码：

- 设置后，每次进入设置页面都会先弹出密码验证框
- 密码使用 **PBKDF2-SHA256** 哈希存储（100,000 轮迭代），明文不入库
- 密码错误时弹窗提示，不会暴露任何配置信息
- 可在设置页中修改或清除密码

## 🖥️ EXE 打包

在 **Windows** 环境下执行以下步骤，将桌面版打包为独立 EXE 文件：

```bat
:: 1. 安装 PyInstaller
pip install pyinstaller

:: 2. 运行打包脚本
python build_exe.py

:: 3. 打包完成后，EXE 位于 dist/MovieHunter.exe
```

生成的 `MovieHunter.exe` 双击即可运行，无需安装 Python 或任何依赖。

> **注意**：打包脚本使用了 PyInstaller 隐藏所有后端依赖，EXE 文件较大（约 30-50MB），这是正常的。

## 🔧 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MH_HOST` | `0.0.0.0` | 监听地址（桌面版固定为 `127.0.0.1`） |
| `MH_PORT` | `8765` | 监听端口（桌面版固定为 `8766`） |

## 🐳 Docker 部署

### 单机 Docker Compose

```yaml
version: "3.8"

services:
  movie-hunter:
    build: .
    container_name: movie-hunter
    restart: unless-stopped
    ports:
      - "8765:8765"
    volumes:
      - ./config:/app/config
      - ./cache:/app/cache
```

```bash
docker compose up -d
```

### NAS 部署注意事项

NAS 环境通常使用代理（如 v2raya）走科学上网，Docker 容器内需要额外配置才能访问宿主机代理：

```yaml
    extra_hosts:
      - "host.docker.internal:host-gateway"
      - "<your-nas-domain>:host-gateway"
```

代理地址使用 `host.docker.internal` 或宿主机 IP，协议选择 **HTTP**（v2raya 为 HTTP 代理，非 SOCKS5）。

### 使用 deploy.sh（推荐）

```bash
# 将项目上传到 NAS 后，直接运行：
bash deploy.sh
```

脚本会自动检查 Docker、构建镜像、启动容器、健康检查。

## 🛠️ 技术栈

- **后端**: Python 3.11+, FastAPI, httpx, Pydantic v2, Uvicorn
- **前端**: 原生 HTML/CSS/JavaScript（零框架依赖）
- **桌面版**: pywebview
- **打包**: PyInstaller
- **容器化**: Docker / Docker Compose
- **数据源**: [TMDB v3 API](https://www.themoviedb.org/documentation/api)
- **密码安全**: PBKDF2-SHA256（100,000 轮迭代）

## 📄 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/search?q={query}` | 模糊搜索 |
| GET | `/api/movie/{id}` | 电影详情 |
| GET | `/api/tv/{id}` | 电视剧详情 |
| GET | `/api/person/{id}` | 人物详情 |
| GET | `/api/image/{size}/{path}` | 图片代理 |
| GET | `/api/settings` | 获取设置（含 `has_password` 标记） |
| POST | `/api/settings` | 保存设置（需密码验证） |
| GET | `/api/settings/check-password` | 校验管理员密码 |

## 🔒 安全说明

- `config/settings.json` 已加入 `.gitignore`，不会被提交到 Git
- TMDB API Key 在 UI 中默认密码样式显示
- 管理员密码以 PBKDF2 哈希存储，不传输明文
- 图片 URL 经后端代理中转，不在前端暴露 `image.tmdb.org` 直连地址

## 📄 许可证

[MIT License](https://opensource.org/licenses/MIT) — 自由使用、修改和分发。

---

⭐ 如果喜欢这个项目，欢迎给个 Star！