# actions/conditions.py
from tkinter import simpledialog, messagebox, colorchooser

def get_condition_actions(nexus):
    def add_if_pixel():
        x = simpledialog.askinteger("Pixel X", "X coordinate:")
        y = simpledialog.askinteger("Pixel Y", "Y coordinate:")
        if x is None or y is None: return
        color = colorchooser.askcolor(title="Target color")[0]
        if not color: return
        tolerance = simpledialog.askinteger("Tolerance", "Color tolerance (0-255):", initialvalue=30)
        if tolerance is None: return

        nexus.script.append({
            "type": "if_pixel",
            "x": x, "y": y,
            "color": color,
            "tolerance": tolerance,
            "delay": 0.1
        })
        nexus.script.append({"type": "end_if", "delay": 0.0})
        nexus.refresh_tree()

    def add_if_multi_pixel():
        conditions = []
        while True:
            x = simpledialog.askinteger("Multi-Pixel If - X", "X (cancel to finish):")
            if x is None: break
            y = simpledialog.askinteger("Multi-Pixel If - Y", "Y coordinate:")
            if y is None: break
            color = colorchooser.askcolor(title="Target color")[0]
            if not color: break
            tolerance = simpledialog.askinteger("Tolerance", "Color tolerance:", initialvalue=30)
            if tolerance is None: break
            conditions.append({"x": x, "y": y, "color": color, "tolerance": tolerance})
        if not conditions: return
        logic = messagebox.askyesnocancel("Logic", "Yes = AND (all match)\nNo = OR (any match)\nCancel = abort")
        if logic is None: return
        nexus.script.append({
            "type": "if_multi_pixel",
            "conditions": conditions,
            "logic": "AND" if logic else "OR",
            "delay": 0.1
        })
        nexus.script.append({"type": "end_if", "delay": 0.0})
        nexus.refresh_tree()

    def add_wait_for_pixel():
        x = simpledialog.askinteger("Wait Pixel X", "X:")
        y = simpledialog.askinteger("Wait Pixel Y", "Y:")
        if x is None or y is None: return
        color = colorchooser.askcolor(title="Target color")[0]
        if not color: return
        tolerance = simpledialog.askinteger("Tolerance", "Color tolerance:", initialvalue=30)
        if tolerance is None: return
        timeout = simpledialog.askinteger("Timeout (s)", "Max wait (0 = infinite):", initialvalue=60)
        if timeout is None: return
        nexus.script.append({
            "type": "wait_for_pixel",
            "x": x, "y": y,
            "color": color,
            "tolerance": tolerance,
            "timeout": 999999 if timeout == 0 else timeout,
            "delay": 0.1
        })
        nexus.script.append({"type": "end_wait", "delay": 0.0})
        nexus.refresh_tree()

    def add_if_text_contains():
        var_name = simpledialog.askstring("Variable", "Variable with text:")
        if not var_name: return
        contains = simpledialog.askstring("Contains", "Text to look for:")
        if contains is None: return
        nexus.script.append({
            "type": "if_text_contains",
            "variable": var_name,
            "contains": contains,
            "delay": 0.1
        })
        nexus.script.append({"type": "end_if", "delay": 0.0})
        nexus.refresh_tree()

    def add_if_number_compare():
        left = simpledialog.askstring("Left", "Left side (variable or expression):")
        if not left: return
        operator = simpledialog.askstring("Operator", "Operator:", initialvalue=">")
        if operator not in [">", "<", ">=", "<=", "==", "!="]:
            messagebox.showerror("Error", "Invalid operator")
            return
        right = simpledialog.askstring("Right", "Right side (value or expression):")
        if right is None: return
        nexus.script.append({
            "type": "if_number_compare",
            "left": left,
            "operator": operator,
            "right": right,
            "delay": 0.1
        })
        nexus.script.append({"type": "end_if", "delay": 0.0})
        nexus.refresh_tree()

    def add_else():
        sel = nexus.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select an If/Wait condition first")
            return
        idx = nexus.tree.index(sel[0])
        action = nexus.script[idx]
        valid_types = ["if_pixel", "if_multi_pixel", "if_text_contains", "if_number_compare",
                       "wait_for_pixel", "wait_for_multi_pixel", "wait_for_text", "wait_for_number"]
        if action["type"] not in valid_types:
            messagebox.showwarning("Invalid", "Else only after If or Wait")
            return
        nexus.script.insert(idx + 1, {"type": "else", "delay": 0.0})
        nexus.refresh_tree()

    return {
        "add_if_pixel": add_if_pixel,
        "add_if_multi_pixel": add_if_multi_pixel,
        "add_wait_for_pixel": add_wait_for_pixel,
        "add_if_text_contains": add_if_text_contains,
        "add_if_number_compare": add_if_number_compare,
        "add_else": add_else,
    }