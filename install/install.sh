apt-get update 
apt-get install ffmpeg madplay mosquitto mosquitto-clients -y

cp install/mosquitto.conf /etc/mosquitto/conf.d/mosquitto.conf
cp install/mqtt.service /lib/systemd/system/mqtt.service
cp install/projects_bathroom_button.service /lib/systemd/system/projects_bathroom_button.service

sudo chmod 644 /lib/systemd/system/mqtt.service
sudo chmod 644 /lib/systemd/system/projects_bathroom_button.service

sudo systemctl daemon-reload
sudo systemctl daemon-reexec

sudo systemctl enable mqtt.service
sudo systemctl enable projects_bathroom_button.service