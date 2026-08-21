#!/bin/sh
# ═══════════════════════════════════════════════════════════════════
# Movie Hunter — NAS Docker 部署脚本
# 用法:
#   1. SSH 到 NAS
#   2. 把整个 movie-hunter 文件夹上传到 NAS
#   3. 执行: bash deploy.sh
# ═══════════════════════════════════════════════════════════════════

cd "$(dirname "$0")"

# Check Docker
if ! command -v docker >/dev/null 2>&1; then
  echo "❌ 未找到 Docker，请先安装"
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  DCMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  DCMD="docker-compose"
else
  echo "❌ 未找到 docker-compose"
  exit 1
fi

echo "🎬 Movie Hunter — NAS Docker 部署"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Docker: $($DCMD version --short 2>/dev/null)"
echo ""

# Build
echo "📦 构建镜像..."
$DCMD build --no-cache -t movie-hunter . 2>&1
echo "✅ 镜像构建完成"
echo ""

# Up
echo "🚀 启动容器..."
$DCMD up -d
echo ""

# Health check
echo "⏳ 等待服务启动..."
sleep 3
for i in 1 2 3 4 5; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://localhost:8765/ 2>/dev/null)
  if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 服务正常 (HTTP 200)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎬 部署成功！"
    echo ""
    echo "   NAS 地址: http://<NAS_IP>:8765"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "⚙️  浏览器打开后:"
    echo "   1. 右上角 ⚙️ 填入 TMDB API Key"
    echo "   2. 开始搜索 🎬"
    echo ""
    echo "📌 常用命令:"
    echo "   docker compose down      # 停止"
    echo "   docker compose up -d     # 启动"
    echo "   docker compose logs -f   # 日志"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
  fi
  echo "  等待... ($i/5)"
  sleep 2
done

echo "❌ 启动超时，查看: docker compose logs"
exit 1
