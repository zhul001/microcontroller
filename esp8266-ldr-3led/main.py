import network
import time
import urequests
import machine

# WiFi configuration
SSID = "NAMA_WIFI_ANDA"
PASS = "PASSWORD_WIFI_ANDA"

# Proxy server configuration
SERVER_IP = "IP_SERVER_PROXY_ANDA"
SERVER_PORT = "8888"

# Telegram chat ID
CHAT_ID = "CHAT_ID_TELEGRAM_ANDA"

# Connect to WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASS)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(0.5)
print("WiFi connected", wifi.ifconfig())

# Sensor and LED setup
ldr = machine.ADC(0)
led_red = machine.Pin(12, machine.Pin.OUT)
led_yellow = machine.Pin(13, machine.Pin.OUT)
led_white = machine.Pin(14, machine.Pin.OUT)

# Timer for sending alerts
last_send = 0

# Send alert to Telegram
def send_alert(value):
    url = "http://" + SERVER_IP + ":" + SERVER_PORT + "/"
    message = "Alert. Darkness detected. LDR value " + str(value)
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = urequests.post(url, json=payload, timeout=8)
        print("Telegram status", response.status_code)
        response.close()
    except Exception as e:
        print("Failed to send alert", e)

# Main loop
while True:
    value = ldr.read()
    print("LDR", value)

    # LED indicator
    if value < 300:
        led_white.on()
        led_yellow.off()
        led_red.off()
    elif value <= 800:
        led_white.off()
        led_yellow.on()
        led_red.off()
    else:
        led_white.off()
        led_yellow.off()
        led_red.on()

        now = time.ticks_ms()
        if now - last_send > 30000:
            send_alert(value)
            last_send = now

    time.sleep(2)
