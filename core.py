# core.py
import tkinter as tk
from tkinter import messagebox, colorchooser, simpledialog
import ttkbootstrap as ttkb
import threading
import time
import json
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from pynput import keyboard as pynput_keyboard
from ui import build_ui, create_floating_panel
from recorder import Recorder
from playback import execute_playback
from remote import start_remote_server
from actions import register_all_actions
from utils import interpolate_text

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

class NexusClicker:
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Core state
        self.script = []
        self.variables = {}
        self.driver = None
        self.recording = False
        self.playing = False
        self.click_count = 0
        self.start_time = None
        self.last_action_time = None
        self._loop_counters = {}

        # Components
        self.recorder = Recorder(self)
        self.recorder.create_overlay()

        self.hotkey_listener = None

        # Build UI
        build_ui(self)
        create_floating_panel(self)

        # Start services
        self.start_global_hotkeys()
        start_remote_server(self)

    def start_browser(self):
        if self.driver is None:
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )
            self.driver.maximize_window()

    def toggle_record(self):
        if self.recording:
            self.recording = False
            self.record_btn.config(bootstyle="warning-outline")
            self.recorder.stop_recording()
        else:
            self.recording = True
            self.playing = False
            self.play_btn.config(state="normal")
            self.recorder.start_recording()
            self.record_btn.config(bootstyle="danger")

    def play_script(self):
        if self.playing or not self.script:
            if not self.script:
                messagebox.showinfo("Empty Script", "Record or load a script first!")
            return

        self.playing = True
        self.click_count = 0
        self.start_time = time.time()
        self.play_btn.config(state="disabled")
        self.recording = False
        self.record_btn.config(bootstyle="warning-outline")

        loops = self.loop_var.get()
        threading.Thread(target=execute_playback, args=(self, loops), daemon=True).start()

    def stop_all(self):
        self.playing = False
        self.recording = False

        if hasattr(self, 'play_btn'):
            self.play_btn.config(state="normal")
        if hasattr(self, 'record_btn'):
            self.record_btn.config(bootstyle="warning-outline")

        self.recorder.stop_recording()
        self._loop_counters.clear()

        self.status.config(text="Stopped by user")

    def delete_selected(self):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            del self.script[idx]
            self.refresh_tree()

    def clear_script(self):
        if messagebox.askyesno("Clear All", "Delete entire script?"):
            self.script.clear()
            self.refresh_tree()

    def save_script(self):
        f = filedialog.asksaveasfilename(
            defaultextension=".nxs",
            filetypes=[("Nexus Script", "*.nxs"), ("JSON", "*.json")]
        )
        if f:
            try:
                with open(f, "w") as file:
                    json.dump(self.script, file, indent=2)
                messagebox.showinfo("Saved", "Script saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

    def load_script(self):
        f = filedialog.askopenfilename(
            filetypes=[("Nexus Script", "*.nxs"), ("JSON", "*.json")]
        )
        if f:
            try:
                with open(f, "r") as file:
                    self.script = json.load(file)
                self.refresh_tree()
                messagebox.showinfo("Loaded", f"Loaded {len(self.script)} actions")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {e}")

    def right_click_edit(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        item = self.tree.identify_row(event.y)
        if not item:
            return
        column = self.tree.identify_column(event.x)
        idx = self.tree.index(item)
        action = self.script[idx]

        col_idx = int(column.replace("#", "")) - 1
        fields = ["#", "Type", "X", "Y", "Text/Key", "Delay (s)"]
        field = fields[col_idx]

        if field in ["#", "Type"]:
            return

        if field == "X" and "x" in action:
            val = simpledialog.askinteger("Edit X", "New X:", initialvalue=action["x"])
            if val is not None:
                action["x"] = val

        elif field == "Y" and "y" in action:
            val = simpledialog.askinteger("Edit Y", "New Y:", initialvalue=action["y"])
            if val is not None:
                action["y"] = val

        elif field == "Text/Key":
            if action["type"] == "type":
                val = simpledialog.askstring("Edit Text", "New text:", initialvalue=action["text"])
                if val is not None:
                    action["text"] = val
            elif action["type"] == "key":
                val = simpledialog.askstring("Edit Key", "New key:", initialvalue=action["key"])
                if val is not None:
                    action["key"] = val.lower()
            elif action["type"] == "scroll":
                cur_amt = action["amount"]
                new_amt = simpledialog.askinteger("Scroll Amount", "New amount:", initialvalue=abs(cur_amt))
                if new_amt is not None:
                    action["amount"] = new_amt if cur_amt > 0 else -new_amt
            elif action["type"] in ["if_pixel", "wait_for_pixel"]:
                color = colorchooser.askcolor(initialvalue=action["color"])[0]
                if color:
                    action["color"] = color
                tol = simpledialog.askinteger("Tolerance", "New tolerance:", initialvalue=action["tolerance"])
                if tol is not None:
                    action["tolerance"] = tol

        elif field == "Delay (s)":
            val = simpledialog.askfloat("Edit Delay", "Delay (seconds):", initialvalue=action["delay"])
            if val is not None and val >= 0:
                action["delay"] = val

        self.refresh_tree()

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, a in enumerate(self.script, 1):
            delay_str = f"{a.get('delay', 0):.3f}"

            if a["type"] == "click":
                vals = (i, "CLICK", a["x"], a["y"], a["button"], delay_str)
            elif a["type"] == "type":
                text_preview = a["text"] if len(a["text"]) < 20 else a["text"][:17] + "..."
                vals = (i, "TYPE", "—", "—", f"'{text_preview}'", delay_str)
            elif a["type"] == "key":
                vals = (i, "KEY", "—", "—", a["key"], delay_str)
            elif a["type"] == "scroll":
                dir_text = "up" if a["amount"] > 0 else "down"
                vals = (i, "SCROLL", a["x"], a["y"], f"{dir_text} {abs(a['amount'])}", delay_str)
            elif a["type"] == "swipe":
                vals = (i, "SWIPE", len(a["points"]), "points", f"~{a['duration']:.2f}s", delay_str)
            elif a["type"] == "delay":
                vals = (i, "DELAY", "—", "—", f"{a['delay']:.2f}s", delay_str)
            elif a["type"] == "wait_for_time":
                vals = (i, "WAIT TIME", "—", "—", a["time"], delay_str)
            elif a["type"] == "random_number":
                t = "INT" if a["is_int"] else "FLOAT"
                vals = (i, f"RANDOM {t}", a["min"], a["max"], f"→ {a['variable']}", delay_str)
            elif a["type"] == "set_variable":
                vals = (i, "SET VAR", a["variable"], "←", a["value"], delay_str)
            elif a["type"] == "if_pixel":
                r, g, b = map(int, a["color"])
                vals = (i, "IF PIXEL", a["x"], a["y"], f"RGB({r},{g},{b}) ±{a['tolerance']}", delay_str)
            elif a["type"] == "wait_for_pixel":
                r, g, b = map(int, a["color"])
                vals = (i, "WAIT PIXEL", a["x"], a["y"], f"RGB({r},{g},{b}) ±{a['tolerance']}", delay_str)
            elif a["type"] == "ocr_read_text":
                r = a["region"]
                vals = (i, "OCR TEXT", f"{r[0]},{r[1]}", f"{r[2]}x{r[3]}", f"→ {a['variable']}", delay_str)
            elif a["type"] == "selenium_open":
                url = a["url"][:40] + "..." if len(a["url"]) > 40 else a["url"]
                vals = (i, "OPEN URL", "—", "—", url, delay_str)
            elif a["type"] == "loop_times":
                count = "Infinite" if a["count"] == 0 else a["count"]
                vals = (i, f"LOOP {count}x", "—", "—", "→", delay_str)
            elif a["type"] == "end_loop":
                vals = (i, "END LOOP", "—", "—", "←", delay_str)
            elif a["type"] == "else":
                vals = (i, "ELSE", "—", "—", "↳", delay_str)
            elif a["type"] in ["end_if", "end_wait"]:
                vals = (i, f"END {a['type'].upper().replace('END_', '')}", "—", "—", "←", delay_str)
            else:
                vals = (i, a["type"].upper(), "-", "-", "-", delay_str)

            self.tree.insert("", "end", values=vals)

    def start_global_hotkeys(self):
        def on_press(key):
            try:
                if key == pynput_keyboard.Key.f6:
                    self.root.after(0, self.toggle_record)
                elif key == pynput_keyboard.Key.f7:
                    self.root.after(0, self.play_script)
                elif key == pynput_keyboard.Key.f8:
                    self.root.after(0, self.stop_all)
            except:
                pass

        self.hotkey_listener = pynput_keyboard.Listener(on_press=on_press)
        self.hotkey_listener.start()

    def show_instructions(self):
        instructions = """
NEXUS CLICKER v7.3 — MODULAR EDITION

🎯 HOW TO USE:
• F6 = Record • F7 = Play • F8 = Stop
• Record actions → Edit script → Add advanced logic via menu
• Use phone remote (link in status bar)
• Right-click rows to edit values

🔥 FEATURES:
• Full conditional logic, loops, variables
• OCR text/number reading
• Selenium browser automation
• Trading helpers
• Calendar scheduling (Wait Until Time)
• Swipe recording with visual feedback
• Remote control from phone

💡 Move mouse to top-left corner for PyAutoGUI failsafe

Enjoy your powerful automation tool!
        """
        messagebox.showinfo("NEXUS CLICKER — Help", instructions.strip())

    def on_close(self):
        self.stop_all()
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        if hasattr(self, 'floating') and self.floating:
            try:
                self.floating.destroy()
            except:
                pass
        self.recorder.cleanup()
        self.root.destroy()