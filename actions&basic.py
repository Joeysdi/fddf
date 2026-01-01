# actions/basic.py
from tkinter import simpledialog, messagebox

def get_basic_actions(nexus):
    def add_click_here():
        try:
            x = int(simpledialog.askstring("X", "X coordinate:") or 0)
            y = int(simpledialog.askstring("Y", "Y coordinate:") or 0)
            nexus.script.append({
                "type": "click",
                "x": x,
                "y": y,
                "button": "left",
                "duration": 0.05,
                "delay": 0.1
            })
            nexus.refresh_tree()
        except:
            pass

    def add_text_action():
        text = simpledialog.askstring("Add Text", "Text to type (use ${var} for variables):")
        if text is not None:
            nexus.script.append({"type": "type", "text": text, "delay": 0.1})
            nexus.refresh_tree()

    def add_delay_action():
        d = simpledialog.askfloat("Delay", "Seconds:", minvalue=0.0, initialvalue=1.0)
        if d is not None:
            nexus.script.append({"type": "delay", "delay": d})
            nexus.refresh_tree()

    return {
        "add_click_here": add_click_here,
        "add_text_action": add_text_action,
        "add_delay_action": add_delay_action,
    }