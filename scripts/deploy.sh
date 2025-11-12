#!/bin/bash

# Temporal KB Deployment Script
# Deploys the application to a VPS using systemd service

set -e  # Exit on error

# Configuration
APP_NAME="temporal-kb"
APP_USER="${APP_USER:-kb}"
APP_DIR="${APP_DIR:-/opt/temporal-kb}"
DATA_DIR="${DATA_DIR:-/var/lib/temporal-kb}"
VENV_DIR="$APP_DIR/venv"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"

echo "====================================="
echo "Temporal KB Deployment Script"
echo "====================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Create application user if it doesn't exist
if ! id "$APP_USER" &>/dev/null; then
    echo "Creating application user: $APP_USER"
    useradd -r -s /bin/bash -d "$APP_DIR" -m "$APP_USER"
fi

# Create directories
echo "Creating directories..."
mkdir -p "$APP_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$DATA_DIR/data"
mkdir -p "$DATA_DIR/logs"
mkdir -p /etc/temporal-kb

# Clone or update repository
if [ -d "$APP_DIR/.git" ]; then
    echo "Updating repository..."
    cd "$APP_DIR"
    sudo -u "$APP_USER" git pull
else
    echo "Cloning repository..."
    sudo -u "$APP_USER" git clone https://github.com/yourusername/temporal-kb.git "$APP_DIR"
    cd "$APP_DIR"
fi

# Create virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    sudo -u "$APP_USER" python3 -m venv "$VENV_DIR"
fi

# Install dependencies
echo "Installing dependencies..."
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install -e "$APP_DIR"

# Copy configuration if it doesn't exist
if [ ! -f "/etc/temporal-kb/config.yaml" ]; then
    echo "Creating default configuration..."
    cp "$APP_DIR/config/production.yaml.example" "/etc/temporal-kb/config.yaml"
    echo "⚠️  Please edit /etc/temporal-kb/config.yaml with your settings"
fi

# Set permissions
echo "Setting permissions..."
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
chown -R "$APP_USER:$APP_USER" "$DATA_DIR"
chown -R "$APP_USER:$APP_USER" "/etc/temporal-kb"

# Create systemd service
echo "Creating systemd service..."
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Temporal Knowledge Base API
After=network.target postgresql.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="KB_DATA_DIR=$DATA_DIR/data"
Environment="KB_CONFIG_DIR=/etc/temporal-kb"
ExecStart=$VENV_DIR/bin/kb serve --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=append:$DATA_DIR/logs/kb.log
StandardError=append:$DATA_DIR/logs/kb-error.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "Reloading systemd..."
systemctl daemon-reload

# Enable and start service
echo "Enabling and starting service..."
systemctl enable "$APP_NAME"
systemctl restart "$APP_NAME"

# Check status
sleep 2
systemctl status "$APP_NAME" --no-pager

echo ""
echo "====================================="
echo "Deployment completed!"
echo "====================================="
echo ""
echo "Service: $APP_NAME"
echo "Status: systemctl status $APP_NAME"
echo "Logs: journalctl -u $APP_NAME -f"
echo "Config: /etc/temporal-kb/config.yaml"
echo ""
echo "Next steps:"
echo "1. Edit /etc/temporal-kb/config.yaml"
echo "2. Set up PostgreSQL database"
echo "3. Configure reverse proxy (nginx/caddy)"
echo "4. Set up SSL certificates"
echo "5. Run: kb init (as $APP_USER)"
echo ""
