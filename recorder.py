# recorder.py
import pyautogui
import time
import tkinter as tk
from pynput import mouse as pynput_mouse
from pynput import keyboard as pynput_keyboard

class Recorder:
    def __init__(self, nexus):
        self.nexus = nexus
        self.mouse_listener = None
        self.typing_listener = None
        self.overlay = None          # Invisible full-screen listener for swipe start
        self.swipe_canvas = None     # Visible canvas for drawing swipe path
        self.current_swipe = []      # List of (x, y) points
        self.swipe_line = None       # Canvas line object

    def create_overlay(self):
        """Creates invisible full-screen overlay to capture swipe start"""
        if self.overlay is not None:
            return

        self.overlay = tk.Toplevel()
        self.overlay.overrideredirect(True)
        self.overlay.geometry("1x1+0+0")
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.0)  # Fully transparent
        self.overlay.config(bg="black", cursor="cross")
        self.overlay.bind("<Button-1>", self.start_swipe)
        self.overlay.bind("<B1-Motion>", self.draw_swipe)
        self.overlay.bind("<ButtonRelease-1>", self.end_swipe)
        self.overlay.withdraw()  # Hidden until recording starts

    def start_recording(self):
        self.nexus.script.clear()
        self.nexus.refresh_tree()
        self.nexus.last_action_time = time.time()

        # Show overlay and start listeners
        if self.overlay is None:
            self.create_overlay()
        self.overlay.deiconify()
        self.overlay.focus_force()

        self._start_mouse_listener()
        self._start_keyboard_listener()

        self.nexus.status.config(text="RECORDING... Click, type, scroll, or swipe!")

    def stop_recording(self):
        if self.overlay:
            try:
                self.overlay.withdraw()
            except:
                pass

        self._stop_mouse_listener()
        self._stop_keyboard_listener()
        self.cleanup_swipe_canvas()

        self.nexus.status.config(text=f"Recording stopped — {len(self.nexus.script)} actions captured")

    def _start_mouse_listener(self):
        def on_click(x, y, button, pressed):
            if not pressed or not self.nexus.recording or self.current_swipe:
                return

            now = time.time()
            delay = round(now - self.nexus.last_action_time, 3)
            btn_map = {
                pynput_mouse.Button.left: "left",
                pynput_mouse.Button.right: "right",
                pynput_mouse.Button.middle: "middle"
            }
            btn = btn_map.get(button, "left")

            self.nexus.script.append({
                "type": "click",
                "x": x,
                "y": y,
                "button": btn,
                "duration": 0.05,
                "delay": delay
            })
            self.nexus.last_action_time = now
            self.nexus.root.after(0, self.nexus.refresh_tree)

        def on_scroll(x, y, dx, dy):
            if not self.nexus.recording:
                return

            now = time.time()
            delay = round(now - self.nexus.last_action_time, 3)

            self.nexus.script.append({
                "type": "scroll",
                "x": x,
                "y": y,
                "amount": dy,
                "delay": delay
            })
            self.nexus.last_action_time = now
            self.nexus.root.after(0, self.nexus.refresh_tree)

        self.mouse_listener = pynput_mouse.Listener(on_click=on_click, on_scroll=on_scroll)
        self.mouse_listener.start()

    def _start_keyboard_listener(self):
        def on_press(key):
            if not self.nexus.recording:
                return

            try:
                # Regular character
                char = key.char
                if char:
                    now = time.time()
                    delay = round(now - self.nexus.last_action_time, 3)
                    self.nexus.script.append({
                        "type": "type",
                        "text": char,
                        "delay": delay
                    })
                    self.nexus.last_action_time = now
                    self.nexus.root.after(0, self.nexus.refresh_tree)
            except AttributeError:
                # Special keys
                key_name = str(key).replace("Key.", "")
                if key_name in ["enter", "space", "backspace", "tab", "esc", "shift", "ctrl", "alt"]:
                    now = time.time()
                    delay = round(now - self.nexus.last_action_time, 3)
                    self.nexus.script.append({
                        "type": "key",
                        "key": key_name,
                        "delay": delay
                    })
                    self.nexus.last_action_time = now
                    self.nexus.root.after(0, self.nexus.refresh_tree)

        self.typing_listener = pynput_keyboard.Listener(on_press=on_press)
        self.typing_listener.start()

    def _stop_mouse_listener(self):
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except:
                pass
            self.mouse_listener = None

    def _stop_keyboard_listener(self):
        if self.typing_listener:
            try:
                self.typing_listener.stop()
            except:
                pass
            self.typing_listener = None

    # === SWIPE RECORDING ===

    def start_swipe(self, event=None):
        if not self.nexus.recording or self.swipe_canvas:
            return

        # Create full-screen transparent canvas for visual feedback
        screen_w, screen_h = pyautogui.size()
        self.swipe_canvas = tk.Toplevel()
        self.swipe_canvas.overrideredirect(True)
        self.swipe_canvas.geometry(f"{screen_w}x{screen_h}+0+0")
        self.swipe_canvas.attributes("-topmost", True)
        self.swipe_canvas.attributes("-transparentcolor", "black")
        self.swipe_canvas.config(bg="black")

        canvas = tk.Canvas(self.swipe_canvas, bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        x, y = pyautogui.position()
        self.current_swipe = [(x, y)]
        self.swipe_line = canvas.create_line(x, y, x, y,
                                             fill="#ff0066",
                                             width=10,
                                             capstyle="round",
                                             smooth=True)

    def draw_swipe(self, event=None):
        if not self.swipe_canvas or not self.current_swipe:
            return

        x, y = pyautogui.position()
        self.current_swipe.append((x, y))

        # Update line smoothly
        canvas = self.swipe_canvas.winfo_children()[0]
        flat_coords = [coord for point in self.current_swipe for coord in point]
        canvas.coords(self.swipe_line, *flat_coords)

    def end_swipe(self, event=None):
        if not self.current_swipe:
            self.cleanup_swipe_canvas()
            return

        point_count = len(self.current_swipe)

        # Only record meaningful swipes (more than a few points)
        if point_count > 8 and self.nexus.recording:
            now = time.time()
            delay = round(now - self.nexus.last_action_time, 3)
            duration = max(0.3, round(point_count / 120, 2))  # Realistic duration

            self.nexus.script.append({
                "type": "swipe",
                "points": self.current_swipe.copy(),
                "duration": duration,
                "delay": delay
            })
            self.nexus.last_action_time = now
            self.nexus.root.after(0, self.nexus.refresh_tree)

        # Clean up
        self.cleanup_swipe_canvas()
        self.current_swipe = []

    def cleanup_swipe_canvas(self):
        if self.swipe_canvas:
            try:
                self.swipe_canvas.destroy()
            except:
                pass
            self.swipe_canvas = None
        self.swipe_line = None

    def cleanup(self):
        """Call on app close"""
        self.stop_recording()
        if self.overlay:
            try:
                self.overlay.destroy()
            except:
                pass
            self.overlay = None