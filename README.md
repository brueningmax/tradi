# TraderAgent 🤖💰

An advanced AI-powered cryptocurrency trading bot with GPT-5 integration, supporting sophisticated position management, risk controls, and volume analysis.

## 🎯 Features

- **AI-Powered Trading**: GPT-5 integration with volume-enhanced decision making
- **Advanced Position Management**: Long/short positions with stop losses and take profits
- **Volume Analysis**: Market conviction insights through volume trend analysis
- **Paper Trading Safety**: Default paper trading mode for safe testing
- **Risk Management**: Margin accounting, position sizing, and safety checks
- **Comprehensive Testing**: 58 tests covering all functionality

## 📁 Project Structure

```
TraderAgent/
├── 📜 main.py                 # Main entry point
├── 📜 demo_volume.py          # Volume analysis demonstration
├── 📁 src/traderagent/        # Core trading package
│   ├── 📜 __init__.py         # Package exports
│   ├── 📜 advanced_trader.py  # Advanced trading system
│   ├── 📜 ai_decision.py      # GPT-5 AI decision engine
│   ├── 📜 data_fetcher.py     # Market data and volume fetching
│   ├── 📜 trader.py           # Basic trading utilities
│   ├── 📜 utils.py            # Helper functions
│   └── 📜 config.py           # Configuration management
├── 📁 tests/                  # Comprehensive test suite
│   ├── 📜 test_advanced_trader.py
│   ├── 📜 test_ai_decision.py
│   ├── 📜 test_data_fetcher.py
│   ├── 📜 test_volume_analysis.py
│   ├── 📜 test_balance_operations.py
│   ├── 📜 test_integration.py
│   └── 📜 test_config.py
├── 📁 scripts/                # Utility scripts
│   └── 📜 run_tests.py        # Test runner
├── 📁 data/                   # Trading data
│   ├── 📜 balance.json        # Live trading balance
│   └── 📜 paper_balance.json  # Paper trading balance
├── 📁 config/                 # Configuration files
│   └── 📜 environment.yml     # Python environment
└── 📜 .env                    # API keys (create this)
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Install dependencies (if using conda)
conda env create -f config/environment.yml
conda activate traderagent
```

### 2. Run Tests

```bash
# Run all tests to verify setup
python scripts/run_tests.py
```

### 3. Start Trading

```bash
# Paper trading with volume analysis (recommended)
python main.py --paper

# Backtest with volume analysis
python main.py --backtest

# Price-only mode (disable volume analysis)
python main.py --backtest --no-volume

# Live trading (⚠️ REAL MONEY - use with caution)
python main.py --live
```

## 🧠 AI Decision System

The TraderAgent uses GPT-5 for intelligent trading decisions with:

### **Volume-Enhanced Analysis** 
- **HIGH volume**: Strong conviction moves, good for trend following
- **ELEVATED volume**: Moderate conviction, smaller positions
- **NORMAL volume**: Standard market activity, regular sizing
- **LOW volume**: Weak conviction, consider waiting

### **Available Actions**
- `BUY_LONG [%] [stop_loss] [take_profit]` - Open long position
- `SELL_SHORT [%] [stop_loss] [take_profit]` - Open short position  
- `CLOSE_LONG [%]` - Close long position
- `CLOSE_SHORT [%]` - Close short position
- `BUY [%]` / `SELL [%]` - Legacy spot trading
- `HOLD` - Do nothing (wait for better opportunities)

## 📊 Volume Analysis Demo

```bash
# Run volume analysis demonstration
python demo_volume.py
```

This shows:
- Real-time volume trend analysis
- AI decision comparison (with/without volume)
- Market conviction insights
- Trading signal enhancement

## 🔧 Configuration

### Command Line Options

| Flag | Description |
|------|-------------|
| `--paper` | Paper trading mode (safe, default) |
| `--live` | Live trading mode (⚠️ real money) |
| `--backtest` | Run historical backtesting |
| `--no-volume` | Disable volume analysis |

### Environment Variables

Create a `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## 🧪 Testing

The project includes comprehensive testing with **separate test suites**:

### **Regular Tests (Free)**
```bash
# Run all free tests (no API costs)
python scripts/run_tests.py

# 59 tests covering:
# - AI decision making (mocked responses)
# - Advanced trading operations (18 tests) 
# - Balance management (12 tests)
# - Data fetching (6 tests)
# - Volume analysis (8 tests)
# - Integration workflows (6 tests)
```

### **Real API Tests (Costs Money)**
```bash
# Run API connectivity tests (uses OpenAI credits)
python scripts/run_real_api_tests.py
```

## 🤖 GitHub Actions Automated Trading

Deploy TraderAgent to run automatically every hour using GitHub Actions - completely free!

### **Setup Instructions**

1. **Fork this repository** to your GitHub account

2. **Add your OpenAI API key as a repository secret:**
   - Go to: Repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (starts with `sk-`)

3. **Enable GitHub Actions:**
   - Go to: Repository → Actions tab
   - Click "I understand my workflows and want to enable them"

4. **The bot will automatically:**
   - ✅ Run every hour (at the start of each hour)
   - 📊 Execute in safe paper trading mode by default
   - 💰 Track balance and trading performance
   - 📈 Use volume analysis for smarter decisions
   - 📋 Generate detailed execution reports

### **Manual Execution**

You can manually trigger the trading bot anytime:

1. Go to: Repository → Actions → "TraderAgent Hourly Trading"
2. Click "Run workflow"
3. Choose options:
   - **Trading mode**: `paper` (safe) or `live` (⚠️ real money)
   - **Volume analysis**: `true` (recommended) or `false`

### **Monitoring Your Bot**

**View Execution Reports:**
- Each run generates a detailed summary with:
  - 💰 Current balance and P&L
  - 📈 Open positions and recent trades  
  - 🧠 AI decisions and market analysis
  - ⏱️ Execution time and status

**Download Trading Logs:**
- Go to any completed workflow run
- Download the "trading-logs" artifact
- Contains full execution logs and balance snapshots

**Example Output:**
```
🤖 === TraderAgent Execution ===
📅 Start Time: 2025-10-14 14:00:15
🎯 Mode: paper trading (with volume analysis)  
🌍 Environment: CI/CD

💰 Current Market Prices:
  BTC: $67,234.50
  SOL: $142.18

💳 Current Balance:
  USD: $10,000.00
  Available Margin: $10,000.00
  Realized P&L: $0.00

🧠 Getting AI trading decision...
🎯 AI Decisions:
  BTC: BUY_LONG 25% [TP: $70,000.00]
  SOL: HOLD

📊 EXECUTION SUMMARY
💰 Final USD Balance: $9,749.12
📈 Realized P&L: $0.00
📊 Unrealized P&L: $250.88
🎯 Total P&L: $250.88
```

### **Safety Features**

- 🛡️ **Paper trading by default** - No real money at risk
- ⏰ **10-minute timeout** - Prevents hanging workflows
- 🔐 **Secure API key handling** - Uses GitHub secrets
- 📊 **Comprehensive logging** - Full audit trail
- ❌ **Failure notifications** - Alerts when issues occur

### **Going Live (⚠️ REAL MONEY)**

To enable live trading with real money:

1. **Test thoroughly in paper mode first!**
2. **Manually run with live mode** to verify everything works
3. **Modify the workflow file** to change the default from `paper` to `live`
4. **Set up notifications** to monitor your bot closely

**⚠️ WARNING:** Live mode uses real money! Only enable after extensive testing.

### **Cost Analysis**

**GitHub Actions:** Completely FREE
- 2,000 minutes/month for public repositories
- Each execution takes ~2-3 minutes
- Supports 24/7 trading (720 executions/month)

**OpenAI API:** ~$1-5/month
- ~$0.02-0.10 per trading decision
- 720 hourly decisions = ~$15-72/month
- Volume analysis may increase costs slightly

### **Troubleshooting**

**Common Issues:**
- ❌ API key not working → Check repository secrets
- ❌ Workflow not running → Enable GitHub Actions
- ❌ Execution failing → Check recent commits for errors
- ❌ No trading decisions → Verify OpenAI API quota

**Test Locally:**
```bash
# Test GitHub Actions simulation locally
python scripts/test_github_actions.py
```

## 🐳 Docker Deployment

TraderAgent is fully containerized for easy deployment to cloud platforms.

### **Quick Start with Docker**

1. **Build the image:**
```bash
# Windows
docker\build.bat

# Linux/macOS  
chmod +x docker/build.sh && docker/build.sh
```

2. **Run paper trading:**
```bash
# Set your API key
export OPENAI_API_KEY="your_api_key_here"

# Windows
docker\run.bat -m paper

# Linux/macOS
./docker/run.sh -m paper
```

### **Production Deployment**

1. **Copy environment template:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

2. **Start with Docker Compose:**
```bash
# Paper trading (safe default)
docker-compose up

# Development environment
docker-compose --profile dev up traderagent-dev

# Live trading (⚠️ REAL MONEY!)
docker-compose --profile live up traderagent-live
```

### **Cloud Deployment Options**

**AWS ECS / Fargate:**
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag traderagent:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/traderagent:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/traderagent:latest
```

**Google Cloud Run:**
```bash
# Build and deploy to Cloud Run
gcloud run deploy traderagent \
  --image gcr.io/PROJECT-ID/traderagent:latest \
  --platform managed \
  --set-env-vars OPENAI_API_KEY=your_key_here
```

**Digital Ocean Apps:**
```yaml
# app.yaml
name: traderagent
services:
- name: trader
  source_dir: /
  github:
    repo: your-username/TraderAgent
    branch: main
  run_command: python main.py --live --paper
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: OPENAI_API_KEY
    value: your_api_key_here
```

### **Security Best Practices**

- **API Keys**: Use Docker secrets or environment variables, never hardcode
- **Non-root user**: Container runs as user `trader` (UID 1000)  
- **Read-only filesystems**: Mount config as read-only
- **Resource limits**: Set memory/CPU limits in production
- **Health checks**: Built-in health monitoring
- **Network isolation**: Uses custom Docker networks

### **Monitoring & Logs**

```bash
# View container logs
docker logs -f traderagent-prod

# Monitor container health
docker inspect traderagent-prod | grep Health -A 10

# View trading history in real-time
docker exec -it traderagent-prod tail -f /app/data/paper_balance.json
```

## ⚙️ Advanced Configuration

### **Balance Structure**
- **USD**: Available cash balance
- **Positions**: Long/short positions with stop losses
- **Margin**: Available and used margin tracking  
- **P&L**: Realized profit/loss tracking
- **History**: Complete audit trail of all trades

### **Risk Management**
- **No Leverage**: Maximum 1:1 position sizing for safety
- **Stop Losses**: Automatic position closure on adverse moves
- **Take Profits**: Automatic profit realization at targets
- **Position Sizing**: Percentage-based risk management
- **Margin Limits**: Prevents over-exposure

## 📈 Performance
# Test actual OpenAI API connectivity (⚠️ COSTS MONEY)
python scripts/run_real_api_tests.py

# Or run individual real API tests:
python tests/test_ai_decision_real_api.py
python scripts/test_openai_api.py

# Set environment variable to include in regular test run:
set RUN_REAL_API_TESTS=true
python scripts/run_tests.py
```

**Why separate?** Real API tests make actual OpenAI API calls and consume credits. The regular test suite uses mocked responses to test all functionality without costs.

## 📈 Trading Features

### **Position Management**
- Long and short positions
- Margin accounting and tracking
- Position averaging and partial closes
- Real-time P&L calculation

### **Risk Management**
- Stop loss and take profit orders
- Position size limits
- Margin utilization monitoring
- Paper trading safety defaults

### **Market Data**
- Real-time price feeds from Binance API
- Volume analysis and trend detection
- Historical data for backtesting
- Error handling and retry logic

## 🔒 Safety Features

- **Paper Trading Default**: All operations default to simulation mode
- **Confirmation Prompts**: Live trading requires explicit confirmation
- **Balance Validation**: Prevents invalid trades and overexposure
- **Error Recovery**: Graceful handling of API failures and malformed data
- **Comprehensive Testing**: 58 tests ensure reliability

## 🛠 Development

### Adding New Features

1. Add implementation to `src/traderagent/`
2. Add tests to `tests/test_*.py`
3. Run tests: `python scripts/run_tests.py`
4. Update documentation

### Supported Cryptocurrencies

Currently supports:
- **BTC** (Bitcoin)
- **SOL** (Solana)

To add more cryptocurrencies, update the data fetcher and AI decision prompts.

## ⚠️ Important Notes

1. **Paper Trading First**: Always test with paper trading before using real money
2. **API Keys**: Keep your OpenAI API key secure in the `.env` file
3. **Risk Management**: Set appropriate stop losses and position sizes
4. **Market Hours**: Cryptocurrency markets operate 24/7
5. **Backtesting**: Historical performance doesn't guarantee future results

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is for educational and research purposes. Use at your own risk when trading with real money.

---

**Happy Trading! 🚀📈**

*Remember: The best trade is sometimes no trade at all. The AI's HOLD option exists for a reason!*