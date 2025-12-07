# VintScout

A self-hosted web application for monitoring Vinted marketplaces. Create custom alerts and receive notifications when new items matching your criteria are listed.

## Features

- **Smart Search**: Autocomplete brand search and visual category tree navigation
- **Multi-Country Support**: Monitor Vinted marketplaces across 20+ European countries
- **Telegram Notifications**: Instant alerts when new items match your criteria
- **Self-Hosted**: Complete control of your data with SQLite or PostgreSQL
- **Docker Ready**: One-command deployment with Docker Compose

## Quick Start

**Prerequisites**: Docker and Docker Compose

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/vintscout.git
   cd vintscout
   ```

2. Start the application:
   ```bash
   docker-compose up -d
   ```

3. Access the web interface at `http://localhost:3000`
   - Default credentials: `admin@example.com` / `admin`

The application includes a pre-seeded database with popular brands and categories. Your data persists in a Docker volume.

### Unraid / Docker CLI

For Unraid or other Docker-based systems, first build or pull the image, then run:

```bash
# Option 1: Pull from Docker Hub (once published)
docker pull yourusername/vintscout:latest

# Option 2: Build locally
git clone https://github.com/yourusername/vintscout.git
cd vintscout
docker build -t vintscout:latest .
```

Then run the container:

```bash
docker run -d \
  --name=vintscout \
  -p 3000:3000 \
  -v /mnt/user/appdata/vintscout:/app/backend/data \
  -e DEPLOYMENT_MODE=self-hosted \
  -e DATABASE_URL=sqlite:////app/backend/data/vinted.db \
  -e TELEGRAM_BOT_TOKEN=your-bot-token \
  -e TELEGRAM_CHAT_ID=your-chat-id \
  -e JWT_SECRET=your-secret-here \
  --restart unless-stopped \
  vintscout:latest
```

**Unraid Web UI Configuration:**
- **Repository:** `yourusername/vintscout:latest`
- **Port:** `3000` (container) → `3000` (host)
- **Path:** `/app/backend/data` (container) → `/mnt/user/appdata/vintscout` (host)
- **Environment Variables:**
  - `DEPLOYMENT_MODE=self-hosted`
  - `DATABASE_URL=sqlite:////app/backend/data/vinted.db`
  - `TELEGRAM_BOT_TOKEN=` (your bot token)
  - `TELEGRAM_CHAT_ID=` (your chat ID)
  - `JWT_SECRET=` (generate with `openssl rand -hex 32`)

Your database file will be accessible at `/mnt/user/appdata/vintscout/vinted.db` on your Unraid server.

## Configuration

Environment variables can be configured via `.env` file. Copy `.env.example` to get started:

```bash
cp .env.example .env
```

**Key settings:**
- `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`: Telegram notifications (optional)
- `JWT_SECRET`: Generate with `openssl rand -hex 32` (recommended for production)
- `DATABASE_URL`: Defaults to SQLite, can use PostgreSQL for cloud deployments

See `.env.example` for all available options.

## Development

**Backend** (Python 3.11+):
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn backend.main:app --reload --port 3000
```

**Frontend** (Node.js 18+):
```bash
cd frontend
npm install
npm run dev
```

Frontend development server runs on `http://localhost:5173`

## Architecture

- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: React 18 with TypeScript and TailwindCSS
- **Database**: SQLite (default) or PostgreSQL
- **Notifications**: Telegram bot integration

## How It Works

1. Create an alert with search criteria (brands, categories, price range, sizes)
2. VintScout checks Vinted every few minutes for new listings
3. Receive notifications via Telegram when matching items are found
4. View your alert history and manage alerts through the web dashboard

## Supported Countries

France, Ireland, Germany, United Kingdom, Spain, Italy, Poland, Czech Republic, Lithuania, Latvia, Netherlands, Belgium, Austria, Luxembourg, Portugal, Sweden, Denmark, Finland, Norway, Hungary, Romania

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

Inspired by [VintedScanner](https://github.com/drego85/VintedScanner) by Andrea Draghetti. This is a complete rewrite with a web-based architecture.

## Legal Notice

This tool accesses public data from Vinted websites. Use responsibly and in accordance with Vinted's Terms of Service.
