# actions/flow.py
from tkinter import simpledialog, messagebox, colorchooser
from utils import parse_wait_time

def get_flow_actions(nexus):
    def add_loop_times():
        count = simpledialog.askinteger("Loop Count", "Times to loop (0 = infinite):", initialvalue=10)
        if count is None: return
        nexus.script.append({"type": "loop_times", "count": count, "delay": 0.0})
        nexus.script.append({"type": "end_loop", "delay": 0.0})
        nexus.refresh_tree()

    def add_loop_until():
        x = simpledialog.askinteger("Until Pixel X", "X:")
        y = simpledialog.askinteger("Until Pixel Y", "Y:")
        if x is None or y is None: return
        color = colorchooser.askcolor(title="Target color")[0]
        if not color: return
        tolerance = simpledialog.askinteger("Tolerance", "Color tolerance:", initialvalue=30)
        if tolerance is None: return
        nexus.script.append({
            "type": "loop_until",
            "condition": {"type": "pixel", "x": x, "y": y, "color": color, "tolerance": tolerance},
            "delay": 0.0
        })
        nexus.script.append({"type": "end_loop", "delay": 0.0})
        nexus.refresh_tree()

    def add_wait_for_time():
        time_str = simpledialog.askstring(
            "Wait Until Time",
            "Absolute: YYYY-MM-DD HH:MM:SS\nRelative: +1h30m, +2d5h, +45s"
        )
        if not time_str: return
        try:
            parse_wait_time(time_str)
        except:
            messagebox.showerror("Error", "Invalid format")
            return
        nexus.script.append({
            "type": "wait_for_time",
            "time": time_str.strip(),
            "delay": 0.1
        })
        nexus.refresh_tree()

    return {
        "add_loop_times": add_loop_times,
        "add_loop_until": add_loop_until,
        "add_wait_for_time": add_wait_for_time,
    }