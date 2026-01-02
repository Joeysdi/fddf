# actions/ocr.py
from tkinter import simpledialog, messagebox
import random
import re

def get_ocr_actions(nexus):
    def add_ocr_read_text():
        region = simpledialog.askstring("Region", "left,top,width,height:")
        if not region: return
        try:
            left, top, width, height = map(int, region.split(','))
        except:
            messagebox.showerror("Error", "Invalid region format")
            return
        var_name = simpledialog.askstring("Variable", "Store text in variable:")
        if not var_name: return
        nexus.script.append({
            "type": "ocr_read_text",
            "region": (left, top, width, height),
            "variable": var_name,
            "delay": 0.5
        })
        nexus.refresh_tree()

    def add_ocr_read_number():
        region = simpledialog.askstring("Region", "left,top,width,height:")
        if not region: return
        try:
            left, top, width, height = map(int, region.split(','))
        except:
            messagebox.showerror("Error", "Invalid region format")
            return
        var_name = simpledialog.askstring("Variable", "Store number in variable:")
        if not var_name: return
        nexus.script.append({
            "type": "ocr_read_number",
            "region": (left, top, width, height),
            "variable": var_name,
            "delay": 0.5
        })
        nexus.refresh_tree()

    def add_wait_for_text():
        region = simpledialog.askstring("Region", "left,top,width,height:")
        if not region: return
        try:
            map(int, region.split(','))
        except:
            messagebox.showerror("Error", "Invalid region")
            return
        contains = simpledialog.askstring("Text", "Wait for text containing:")
        if contains is None: return
        timeout = simpledialog.askinteger("Timeout", "Max wait seconds (0=infinite):", initialvalue=60)
        if timeout is None: return
        nexus.script.append({
            "type": "wait_for_text",
            "region": tuple(map(int, region.split(','))),
            "contains": contains,
            "timeout": 999999 if timeout == 0 else timeout,
            "delay": 0.1
        })
        nexus.script.append({"type": "end_wait", "delay": 0.0})
        nexus.refresh_tree()

    def add_wait_for_number():
        region = simpledialog.askstring("Region", "left,top,width,height:")
        if not region: return
        try:
            map(int, region.split(','))
        except:
            messagebox.showerror("Error", "Invalid region")
            return
        operator = simpledialog.askstring("Operator", "Condition (> < >= <= == !=):")
        if operator not in [">", "<", ">=", "<=", "==", "!="]:
            messagebox.showerror("Error", "Invalid operator")
            return
        value = simpledialog.askfloat("Value", f"Wait until number {operator} this value:")
        if value is None: return
        timeout = simpledialog.askinteger("Timeout", "Max wait seconds (0=infinite):", initialvalue=60)
        if timeout is None: return
        nexus.script.append({
            "type": "wait_for_number",
            "region": tuple(map(int, region.split(','))),
            "operator": operator,
            "value": value,
            "timeout": 999999 if timeout == 0 else timeout,
            "delay": 0.1
        })
        nexus.script.append({"type": "end_wait", "delay": 0.0})
        nexus.refresh_tree()

    def add_random_number():
        var_name = simpledialog.askstring("Variable", "Store random number in variable:")
        if not var_name: return
        min_val = simpledialog.askfloat("Min", "Minimum value:", initialvalue=0.0)
        if min_val is None: return
        max_val = simpledialog.askfloat("Max", "Maximum value:", initialvalue=100.0)
        if max_val is None or max_val <= min_val:
            messagebox.showerror("Error", "Max must be > min")
            return
        is_int = messagebox.askyesno("Type", "Generate integer? (Yes = int, No = float)")
        nexus.script.append({
            "type": "random_number",
            "variable": var_name,
            "min": min_val,
            "max": max_val,
            "is_int": is_int,
            "delay": 0.1
        })
        nexus.refresh_tree()

    def add_set_variable():
        var_name = simpledialog.askstring("Variable Name", "Variable to set:")
        if not var_name: return
        value = simpledialog.askstring("Value", "Value or expression (use variables):")
        if value is None: return
        nexus.script.append({
            "type": "set_variable",
            "variable": var_name,
            "value": value,
            "delay": 0.1
        })
        nexus.refresh_tree()

    return {
        "add_ocr_read_text": add_ocr_read_text,
        "add_ocr_read_number": add_ocr_read_number,
        "add_wait_for_text": add_wait_for_text,
        "add_wait_for_number": add_wait_for_number,
        "add_random_number": add_random_number,
        "add_set_variable": add_set_variable,
    }