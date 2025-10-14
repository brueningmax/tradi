# Optional Notification Setup for TraderAgent

This directory contains optional notification integrations for TraderAgent GitHub Actions workflows.

## Available Notifications

### Discord Webhook (Recommended)
Simple, free Discord notifications for trading updates.

1. Create a Discord webhook in your server
2. Add `DISCORD_WEBHOOK_URL` to your GitHub repository secrets
3. Uncomment the Discord notification step in `.github/workflows/trading.yml`

### Slack Webhook
Professional Slack notifications for team monitoring.

1. Create a Slack app with incoming webhooks
2. Add `SLACK_WEBHOOK_URL` to your GitHub repository secrets
3. Uncomment the Slack notification step in `.github/workflows/trading.yml`

### Email Notifications
GitHub Actions native email notifications.

1. Go to your GitHub repository settings
2. Enable email notifications for workflow failures
3. No additional setup required

## Usage

Uncomment the desired notification block in `.github/workflows/trading.yml`:

```yaml
# Optional: Discord notification
- name: 📢 Send Discord notification
  if: always()
  uses: ./.github/actions/discord-notify
  with:
    webhook-url: ${{ secrets.DISCORD_WEBHOOK_URL }}
    status: ${{ job.status }}
    trading-mode: ${{ steps.trading.outputs.trading_mode }}
```

## Security Note

Never commit webhook URLs or API keys to your repository. Always use GitHub Secrets.