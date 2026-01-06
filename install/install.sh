service_name="bathroom_button"
service_name_underscore="bathroom_button"
service_port=5006


set -e  # Exit immediately if a command exits with a non-zero status

echo "✅ Installing system dependencies media tools and Python dev headers (needed for GPIO bindings.)"
sudo apt-get update
sudo apt-get install -y python3-dev build-essential vlc ffmpeg

echo "✅ Installing uv (Python package manager)"
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "✅ uv is already installed. Updating to latest version."
    uv self update
fi

echo "✅ Installing project dependencies with uv"
uv sync

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
