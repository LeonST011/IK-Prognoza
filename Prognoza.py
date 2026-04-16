import requests
import tkinter as tk
from tkinter import messagebox
import os
import json
from PIL import Image, ImageTk

API_KEY = "cff80932a002105f087e3fc650faa2cc"

APP_DIR = os.path.join(os.getenv("APPDATA"), "IK_prognoza")
ICON_DIR = os.path.join(APP_DIR, "icons")
SAVE_FILE = os.path.join(APP_DIR, "config.json")

os.makedirs(ICON_DIR, exist_ok=True)

# 🌐 ICONS
ICONS = {
    "clear": "https://cdn-icons-png.flaticon.com/512/869/869869.png",
    "clouds": "https://cdn-icons-png.flaticon.com/512/414/414927.png",
    "rain": "https://cdn-icons-png.flaticon.com/512/3351/3351979.png",
    "snow": "https://cdn-icons-png.flaticon.com/512/642/642000.png",
    "mist": "https://cdn-icons-png.flaticon.com/512/4005/4005901.png"
}

# 💾 CITY SAVE
def save_city(city):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump({"city": city}, f)

def load_city():
    if os.path.exists(SAVE_FILE):
        return json.load(open(SAVE_FILE, encoding="utf-8")).get("city", "")
    return ""

# 📥 ICON DOWNLOAD
def get_icon_file(name, url):
    path = os.path.join(ICON_DIR, f"{name}.png")
    if not os.path.exists(path):
        r = requests.get(url, timeout=10)
        with open(path, "wb") as f:
            f.write(r.content)
    return path

# 🎯 FIXED WEATHER PARSER (GLAVNI FIX)
def map_icon(weather_main):
    w = (weather_main or "").lower()

    if w == "rain" or w == "drizzle" or w == "thunderstorm":
        return get_icon_file("rain", ICONS["rain"])

    if w == "clouds":
        return get_icon_file("clouds", ICONS["clouds"])

    if w == "snow":
        return get_icon_file("snow", ICONS["snow"])

    if w in ["mist", "fog", "haze"]:
        return get_icon_file("mist", ICONS["mist"])

    return get_icon_file("clear", ICONS["clear"])

# 🧩 ROW UI
def row(parent, icon_path, text):
    frame = tk.Frame(parent)

    img = Image.open(icon_path).resize((30, 30))
    img = ImageTk.PhotoImage(img)

    icon = tk.Label(frame, image=img)
    icon.image = img
    icon.pack(side="left")

    tk.Label(frame, text=text, font=("Arial", 10)).pack(side="left", padx=6)

    frame.pack(anchor="w", pady=2)

# 🌦️ WEATHER
def get_weather():
    city = entry.get().strip()

    if not city:
        messagebox.showwarning("Greška", "Unesi grad!")
        return

    save_city(city)

    for w in frame.winfo_children():
        w.destroy()

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "sr"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        if str(data.get("cod")) != "200":
            row(frame, get_icon_file("clear", ICONS["clear"]), f"Greška: {data.get('message')}")
            return

        # 🌡️ CURRENT
        cur = data["list"][0]
        main0 = cur["weather"][0]["main"]
        temp0 = cur["main"]["temp"]
        hum0 = cur["main"]["humidity"]

        row(frame,
            map_icon(main0),
            f"Trenutno: {temp0}°C | Vlažnost: {hum0}% | {main0}")

        # 📅 DAYS
        tk.Label(frame, text="\n📅 DANI", font=("Arial", 12, "bold")).pack(anchor="w")

        for i in range(0, len(data["list"]), 8):
            item = data["list"][i]
            main = item["weather"][0]["main"]
            temp = item["main"]["temp"]
            date = item["dt_txt"].split(" ")[0]

            row(frame, map_icon(main), f"{date} | {temp}°C | {main}")

        # ⏱️ HOURS
        tk.Label(frame, text="\n⏱️ SATI", font=("Arial", 12, "bold")).pack(anchor="w")

        for i in range(6):
            item = data["list"][i]
            main = item["weather"][0]["main"]
            temp = item["main"]["temp"]
            time = item["dt_txt"].split(" ")[1][:5]

            row(frame, map_icon(main), f"{time} | {temp}°C | {main}")

        app.update_idletasks()
        app.geometry(f"520x{min(700, frame.winfo_reqheight() + 120)}")

    except Exception as e:
        row(frame, get_icon_file("clear", ICONS["clear"]), f"Error: {e}")

# 🚀 INIT
os.makedirs(ICON_DIR, exist_ok=True)

# 🪟 UI
app = tk.Tk()
app.title("IK WEATHER FINAL")
app.geometry("520x200")

tk.Label(app, text="IK WEATHER", font=("Arial", 16)).pack(pady=10)

entry = tk.Entry(app, font=("Arial", 12))
entry.pack()

tk.Button(app, text="Prikaži prognozu", command=get_weather).pack(pady=10)

frame = tk.Frame(app)
frame.pack(fill="both", expand=True)

# 🔁 LAST CITY
last = load_city()
if last:
    entry.insert(0, last)

app.mainloop()