import flet as ft
import requests
import threading
import time

def main(page: ft.Page):
    page.title = "Smart Home Controller"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # Removed unnecessary app.run line
    SERVER_URL = "http://192.168.151.96:5000"

    # Create controls with initial values
    brightness = ft.Text("🔦 Brightness: Loading...")
    motion = ft.Text("🚨 Motion: Loading...")
    fan_pot = ft.Text("🎛️ Fan Pot: Loading...")
    
    led_switch = ft.Switch(label="LED", value=False)
    brightness_slider = ft.Slider(min=0, max=255, value=0, label="{value}%")
    fan_switch = ft.Switch(label="Fan", value=False)
    fan_speed = ft.Slider(min=0, max=255, value=0, label="Speed: {value}")

    def send_controls(e):
        data = {
            "led_enabled": led_switch.value,
            "brightness": int(brightness_slider.value),
            "fan_enabled": fan_switch.value,
            "fan_speed": int(fan_speed.value)
        }
        try:
            requests.post(f"{SERVER_URL}/flet/update", json=data, timeout=2)
        except Exception as e:
            print("Control update failed:", e)

    def update_sensors():
        while True:
            try:
                response = requests.get(f"{SERVER_URL}/api/status", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    brightness.value = f"🔦 Brightness: {data['sensors']['analog_input']}"
                    motion.value = f"🚨 Motion: {'Detected' if data['sensors']['button'] else 'None'}"
                    fan_pot.value = f"🎛️ Fan Pot: {data['sensors']['fan_pot']}"
                    page.update()
            except Exception as e:
                print("Sensor update failed:", e)
            time.sleep(1)

    # Layout
    controls = ft.Column([
        ft.Text("💡 LED Control", size=20, weight=ft.FontWeight.BOLD),
        led_switch,
        ft.Text("🔆 Brightness Control"),
        brightness_slider,
        ft.Divider(height=20),
        ft.Text("🌀 Fan Control", size=20, weight=ft.FontWeight.BOLD),
        fan_switch,
        ft.Text("🎚️ Fan Speed Control"),
        fan_speed,
    ], spacing=10)

    sensors = ft.Column([
        ft.Text("📡 Live Sensor Data", size=20, weight=ft.FontWeight.BOLD),
        brightness,
        motion,
        fan_pot,
    ], spacing=10)

    page.add(
        ft.Row([
            ft.Card(
                content=ft.Container(controls, padding=15),
                elevation=5
            ),
            ft.Card(
                content=ft.Container(sensors, padding=15),
                elevation=5
            )
        ], spacing=20)
    )

    # Set up event handlers
    for control in [led_switch, brightness_slider, fan_switch, fan_speed]:
        control.on_change = send_controls

    # Start sensor update thread
    threading.Thread(target=update_sensors, daemon=True).start()

ft.app(target=main)