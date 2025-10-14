#!/bin/bash
# run.sh - Run TraderAgent in different modes

set -e

# Default values
MODE="paper"
DETACHED=""
OPENAI_KEY="${OPENAI_API_KEY}"

# Function to show usage
show_help() {
    echo "🤖 TraderAgent Docker Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -m, --mode MODE     Trading mode: paper, live, dev (default: paper)"
    echo "  -d, --detached      Run in detached mode (background)"
    echo "  -k, --key KEY       OpenAI API key (or set OPENAI_API_KEY env var)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Paper trading (interactive)"
    echo "  $0 -m paper -d                       # Paper trading (background)"
    echo "  $0 -m dev                            # Development mode"
    echo "  $0 -m live -k sk-xxx...              # Live trading with API key"
    echo ""
    echo "⚠️  WARNING: Live mode uses real money! Use with extreme caution."
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -d|--detached)
            DETACHED="-d"
            shift
            ;;
        -k|--key)
            OPENAI_KEY="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate OpenAI API key
if [ -z "$OPENAI_KEY" ]; then
    echo "❌ Error: OpenAI API key is required!"
    echo "   Set OPENAI_API_KEY environment variable or use -k option"
    exit 1
fi

# Validate mode
case "$MODE" in
    paper)
        echo "📊 Starting TraderAgent in PAPER TRADING mode..."
        docker run $DETACHED --rm --name trader-paper \
            -e OPENAI_API_KEY="$OPENAI_KEY" \
            -v "$(pwd)/data:/app/data" \
            traderagent:latest python main.py --live --paper
        ;;
    live)
        echo "⚠️  Starting TraderAgent in LIVE TRADING mode..."
        echo "⚠️  THIS WILL USE REAL MONEY!"
        echo ""
        read -p "Are you sure? Type 'YES' to continue: " confirm
        if [ "$confirm" != "YES" ]; then
            echo "Cancelled."
            exit 0
        fi
        docker run $DETACHED --rm --name trader-live \
            -e OPENAI_API_KEY="$OPENAI_KEY" \
            -v "$(pwd)/data:/app/data" \
            traderagent:latest python main.py --live
        ;;
    dev)
        echo "🛠️  Starting TraderAgent in DEVELOPMENT mode..."
        docker-compose --profile dev up traderagent-dev
        ;;
    *)
        echo "❌ Error: Invalid mode '$MODE'. Valid modes: paper, live, dev"
        exit 1
        ;;
esac