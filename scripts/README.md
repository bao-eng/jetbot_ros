# OLED service setup

copy oled.service to /lib/systemd/system/

```
sudo systemctl daemon-reload
sudo systemctl enable oled
sudo systemctl start oled
sudo systemctl status oled
```
