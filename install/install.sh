set -e

CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "✅ Installing system dependencies media tools and Python dev headers (needed for GPIO bindings.)"
sudo apt-get update
sudo apt-get install -y python3-dev build-essential vlc ffmpeg

echo "✅ Installing uv (Python package manager)"
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
else
    echo "✅ uv is already installed. Updating to latest version."
    uv self update
fi

echo "✅ Installing project dependencies with uv"
uv sync

service_name=$(uv run config --project-name)

echo "📋 Configuration:"
{
    uv run config --all | while IFS='=' read -r key value; do
        echo -e "   ${CYAN}${key}${NC}|${YELLOW}${value}${NC}"
    done
} | column -t -s '|'

echo "✅ Copying service file to systemd directory"
sudo cp install/projects_${service_name}.service /lib/systemd/system/projects_${service_name}.service

# echo "✅ Copying mosquitto config"
# sudo cp install/mosquitto.conf /etc/mosquitto/conf.d/mosquitto.conf
# echo "✅ Copying mqtt service"
# sudo cp install/mqtt.service /lib/systemd/system/mqtt.service

echo "✅ Setting permissions for the service file"
sudo chmod 644 /lib/systemd/system/projects_${service_name}.service
# sudo chmod 644 /lib/systemd/system/mqtt.service
echo "✅ Reloading systemd daemon"
sudo systemctl daemon-reload
sudo systemctl daemon-reexec

echo "✅ Enabling the service: projects_${service_name}.service"
sudo systemctl enable projects_${service_name}.service
# sudo systemctl enable mqtt.service
sudo systemctl restart projects_${service_name}.service
# sudo systemctl restart mqtt.service
sudo systemctl status projects_${service_name}.service --no-pager
# sudo systemctl status mqtt.service --no-pager

echo "✅ Setup completed successfully! 🎉"
