#!/bin/bash
# build.sh - Build TraderAgent Docker image

set -e

echo "🏗️  Building TraderAgent Docker image..."

# Get version from git tag or use 'latest'
VERSION=$(git describe --tags --always 2>/dev/null || echo "latest")

# Build the image
docker build -t traderagent:${VERSION} -t traderagent:latest .

echo "✅ Successfully built traderagent:${VERSION}"
echo ""
echo "Available commands:"
echo "  Paper trading:  docker run -d --name trader-paper -e OPENAI_API_KEY=\$OPENAI_API_KEY traderagent:latest"
echo "  Development:    docker-compose --profile dev up traderagent-dev"
echo "  Live trading:   docker-compose --profile live up traderagent-live"
echo ""
echo "💡 Don't forget to set your OPENAI_API_KEY environment variable!"