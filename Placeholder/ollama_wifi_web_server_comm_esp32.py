import requests

ESP32_IP = "192.168.1.88" # Referring to our ESP32 IP address from Serial Monitor


def turn_on_led():
    requests.get(f"http://{ESP32_IP}/led/on")
    return "LED turned ON"


def turn_off_led():
    requests.get(f"http://{ESP32_IP}/led/off")
    return "LED turned OFF"


def start_motor():
    requests.get(f"http://{ESP32_IP}/motor/on")
    return "Motor started"


def stop_motor():
    requests.get(f"http://{ESP32_IP}/motor/off")
    return "Motor stopped"
