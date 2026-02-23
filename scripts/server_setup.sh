#!/usr/bin/env bash
# scripts/server_setup.sh
# Подготовка чистого сервера Ubuntu 22.04/24.04 для TaxReport Pro
# Запуск: sudo bash scripts/server_setup.sh

set -euo pipefail

echo "=== TaxReport Pro: подготовка сервера ==="

# Обновление системы
apt-get update && apt-get upgrade -y

# Базовые утилиты
apt-get install -y curl wget git unzip nano ufw fail2ban

# ── Docker ────────────────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo "→ Установка Docker..."
  curl -fsSL https://get.docker.com | sh
  usermod -aG docker "$SUDO_USER" || true
fi

# ── Docker Compose v2 ─────────────────────────────────────────────────────────
if ! docker compose version &>/dev/null; then
  echo "→ Установка Docker Compose v2..."
  COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f4)
  curl -SL "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-x86_64" \
    -o /usr/local/lib/docker/cli-plugins/docker-compose
  chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
fi

# ── UFW Firewall ──────────────────────────────────────────────────────────────
echo "→ Настройка фаервола..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# ── Fail2ban ──────────────────────────────────────────────────────────────────
systemctl enable fail2ban
systemctl start fail2ban

# ── Директория проекта ────────────────────────────────────────────────────────
mkdir -p /opt/taxreportpro
chown "$SUDO_USER":"$SUDO_USER" /opt/taxreportpro 2>/dev/null || true

echo ""
echo "✅ Сервер готов!"
echo "Следующий шаг:"
echo "  cd /opt/taxreportpro"
echo "  git clone https://github.com/YOUR_ORG/taxreportpro.git ."
echo "  cp .env.example .env && nano .env"
echo "  ./scripts/deploy.sh --first-run"
