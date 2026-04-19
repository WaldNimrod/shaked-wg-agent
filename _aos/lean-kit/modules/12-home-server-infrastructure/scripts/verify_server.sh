#!/bin/bash
# AOS Module 12 — Server health check
# Usage: ssh nimrodw@server './verify_server.sh'
# Comprehensive health check across all services

set -euo pipefail

echo "🏥 AOS Server Health Check"
echo "=========================="
echo ""

# 1. System Information
echo "📊 System Information"
echo "---"
uname -a
echo ""

# 2. Disk Space
echo "💾 Disk Space"
echo "---"
df -h | grep -E "^/dev|^Filesystem"
echo ""

# 3. Memory & CPU
echo "⚙️  Memory & CPU"
echo "---"
free -h | head -2
uptime
echo ""

# 4. Docker Containers
echo "🐳 Docker Containers"
echo "---"
if command -v docker &> /dev/null; then
  docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || echo "⚠️  Docker not running"
else
  echo "⚠️  Docker not installed"
fi
echo ""

# 5. Systemd Services
echo "🔧 Systemd Services (AOS-related)"
echo "---"
systemctl list-units --type=service --state=running 2>/dev/null | grep -E "aos|dispatch|postgres" || echo "No AOS services found"
echo ""

# 6. Ports in Use
echo "🔌 Ports in Use (top 15)"
echo "---"
ss -tlnp 2>/dev/null | head -16 || echo "⚠️  ss command failed"
echo ""

# 7. Agent Communication Directories
echo "📬 Agent Communication"
echo "---"
if [[ -d "$HOME/agent_comm" ]]; then
  echo "Inbox:  $(ls -1 $HOME/agent_comm/inbox 2>/dev/null | wc -l) messages"
  echo "Outbox: $(ls -1 $HOME/agent_comm/outbox 2>/dev/null | wc -l) responses"
else
  echo "⚠️  Agent communication directories not found"
fi
echo ""

# 8. Database Connectivity
echo "🗄️  Database Check"
echo "---"
if command -v psql &> /dev/null; then
  psql -U postgres -h localhost -p 5434 -l 2>/dev/null | head -3 || echo "⚠️  PostgreSQL not responding"
else
  echo "⚠️  PostgreSQL client not installed"
fi
echo ""

echo "✅ Health check complete"
