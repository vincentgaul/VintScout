# VintedScanner Web

**Modern web-based alert platform for Vinted marketplace notifications**

VintedScanner Web is a complete rewrite of the CLI-based VintedScanner with a web interface, featuring intelligent brand and category search. Get notified when new items matching your criteria appear on Vinted across 20+ countries.

## Key Features

### 🎯 Intelligent Brand & Category Search

Unlike the original CLI tool that requires finding numeric IDs manually, VintedScanner Web provides:

- **Autocomplete Brand Search**: Just type "Nike" - no need to find ID "53"
- **Visual Category Tree**: Browse categories like a file explorer
- **Smart Caching**: Popular brands load instantly
- **Multi-brand Selection**: Search for multiple brands at once

### 🌍 Multi-Country Support

Monitor Vinted marketplaces in 20+ countries:
- 🇫🇷 France
- 🇮🇪 Ireland
- 🇩🇪 Germany
- 🇬🇧 United Kingdom
- 🇪🇸 Spain
- 🇮🇹 Italy
- And many more...

### 🔔 Flexible Notifications

- Email (SMTP)
- Slack (Webhooks)
- Telegram (Bot)

### 📊 Real-Time Dashboard

- Alert management
- Item history
- Statistics and insights
- Enable/disable alerts with one click

## Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- OR Python 3.11+ and Node.js 18+ for local development

### Option 1: Use Pre-Built Docker Image (Easiest)

**Pull and run the latest image from Docker Hub:**

```bash
# Pull the latest image
docker pull yourusername/vintedscanner-web:latest

# Create a directory for data persistence
mkdir -p vintedscanner-data

# Run the container
docker run -d \
  --name vintedscanner \
  -p 3000:3000 \
  -v vintedscanner-data:/app/backend/data \
  -e JWT_SECRET=$(openssl rand -hex 32) \
  -e TELEGRAM_BOT_TOKEN=your-bot-token \
  -e TELEGRAM_CHAT_ID=your-chat-id \
  yourusername/vintedscanner-web:latest
```

Access the application:
- Web interface: http://localhost:3000
- Default login: `admin@example.com` / `admin`
- API docs: http://localhost:3000/docs

**Using docker-compose with pre-built image:**

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  vintedscanner:
    image: yourusername/vintedscanner-web:latest
    container_name: vintedscanner-web
    ports:
      - "3000:3000"
    environment:
      - JWT_SECRET=${JWT_SECRET:-change-me-in-production}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID:-}
    volumes:
      - vintedscanner-data:/app/backend/data
    restart: unless-stopped

volumes:
  vintedscanner-data:
```

Then run:
```bash
docker-compose up -d
```

### Option 2: Build From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vintedscanner-web.git
cd vintedscanner-web
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env and set your configuration
# Generate JWT_SECRET: openssl rand -hex 32
```

3. Start the application:
```bash
docker-compose up -d
```

4. Access the application:
- Web interface: http://localhost:3000
- API docs: http://localhost:3000/docs

### Local Development

#### Backend (using uv - recommended)

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

cd backend
uv pip install -r requirements.txt

# Run migrations
uv run alembic upgrade head

# Seed popular brands
uv run python -m backend.seeds.popular_brands

# Start development server
uv run uvicorn backend.main:app --reload --port 3000
```

**Alternative: Traditional method**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m backend.seeds.popular_brands
uvicorn backend.main:app --reload --port 3000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at http://localhost:5173

## Configuration

See `.env.example` for all available configuration options.

**Required settings:**
- `JWT_SECRET`: Generate with `openssl rand -hex 32`
- `DATABASE_URL`: SQLite or PostgreSQL connection string

**Optional settings:**
- Email, Slack, Telegram credentials for notifications
- Brand/category cache settings
- CORS origins

## Architecture

- **Backend**: FastAPI (Python 3.11+) with SQLAlchemy ORM
- **Frontend**: React 18+ with TypeScript, Vite, TailwindCSS
- **Database**: SQLite (self-hosted) or PostgreSQL (cloud)
- **Deployment**: Docker containers

## Development Roadmap

- [x] Project structure setup
- [ ] Backend foundation (Week 1-4)
  - [ ] Database models
  - [ ] Vinted API integration
  - [ ] Brand/category caching
  - [ ] REST API endpoints
  - [ ] Scanner service
- [ ] Frontend development (Week 5-8)
  - [ ] Authentication UI
  - [ ] Alert management
  - [ ] Brand autocomplete
  - [ ] Category tree
  - [ ] Dashboard
- [ ] Testing & Launch (Week 9-13)
  - [ ] Docker packaging
  - [ ] Documentation
  - [ ] Beta testing
  - [ ] Public release

## Acknowledgments

This project was inspired by [VintedScanner](https://github.com/drego85/VintedScanner) by Andrea Draghetti. While this is a complete rewrite with a web-based architecture, we studied the original for Vinted API integration patterns.

## Key Improvements Over Original

- **Web-based interface** (no command line required)
- **Intelligent brand search** - Just type "Nike" instead of finding ID "53"
- **Visual category tree** - Browse like a file explorer
- Multi-user support
- Real-time dashboard
- Docker deployment

## License

MIT License - see [LICENSE](LICENSE) file for details

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/vintedscanner-web/issues)
- **Documentation**: See [docs/](docs/) folder
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/vintedscanner-web/discussions)

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## Legal Notice

This tool accesses public data from Vinted websites. Use responsibly and in accordance with Vinted's Terms of Service. The authors are not responsible for misuse of this tool.
