# настройки подключения

https://chat.qwen.ai/c/b929431c-c845-47f7-bfc6-301679ab25ea



# Для LAN (enp4s0)
sudo nmcli con modify "Wired connection 1" ipv4.dhcp-client-id mac

# Для Wi-Fi (если подключение активно)
sudo nmcli con modify "MyWiFi" ipv4.dhcp-client-id mac

sudo nmcli con down "Wired connection 1"
sudo nmcli con up "Wired connection 1"