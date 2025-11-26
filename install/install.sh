
service_name="bathroom_button"
python_version="3.12"

set -e  # Exit immediately if a command exits with a non-zero status

# echo "✅ Updating package list"
# sudo apt-get update
# sudo apt-get install ffmpeg madplay mosquitto mosquitto-clients -y

echo "✅ Creating conda environment: $service_name with Python $python_version"
if ! conda env list | grep -q "^$service_name\s"; then
    conda create -n $service_name python=$python_version -y
else
    echo "✅ Conda environment '$service_name' already exists. Skipping creation."
    source /home/tinybathroom/miniconda3/etc/profile.d/conda.sh
fi

echo "✅ Activating conda environment: $service_name"
conda activate $service_name

echo "✅ Installing required Python packages"
#pip install -U poetry
poetry install --no-root

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
