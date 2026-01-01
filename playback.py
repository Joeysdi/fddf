# playback.py
import time
import random
import pyautogui
import cv2
import numpy as np
from PIL import Image
import pytesseract
import re
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils import interpolate_text, evaluate_expression, parse_wait_time

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

def execute_playback(nexus, loops: int):
    """
    Main playback loop — runs in a separate thread.
    Handles all action types with proper nesting (if/else, loops, waits).
    """
    cycle = 0
    infinite = loops == 0

    while nexus.playing and (infinite or cycle < loops):
        cycle += 1
        i = 0
        while i < len(nexus.script) and nexus.playing:
            action = nexus.script[i]
            delay = action.get("delay", 0.05)
            time.sleep(max(0.001, delay))

            atype = action["type"]

            # === BASIC ACTIONS ===
            if atype == "click":
                x, y = action["x"] + random.randint(-6, 6), action["y"] + random.randint(-6, 6)
                pyautogui.moveTo(x, y, duration=random.uniform(0.04, 0.14))
                pyautogui.click(button=action.get("button", "left"))
                nexus.click_count += 1

            elif atype == "type":
                text = interpolate_text(action["text"], nexus.variables)
                pyautogui.write(text, interval=0.02)

            elif atype == "key":
                pyautogui.press(action["key"])

            elif atype == "scroll":
                pyautogui.moveTo(action["x"], action["y"], duration=0)
                pyautogui.scroll(action["amount"] * 3)

            elif atype == "swipe":
                points = action["points"]
                if len(points) < 2:
                    i += 1
                    continue
                px, py = points[0]
                pyautogui.moveTo(px + random.randint(-4, 4), py + random.randint(-4, 4), duration=0.06)
                pyautogui.mouseDown()
                for j in range(1, len(points), 2):
                    if not nexus.playing:
                        break
                    px, py = points[j]
                    pyautogui.moveTo(px + random.randint(-5, 5), py + random.randint(-5, 5),
                                     duration=random.uniform(0.006, 0.016))
                pyautogui.mouseUp()

            elif atype == "delay":
                time.sleep(action["delay"])

            # === VARIABLES & MATH ===
            elif atype == "random_number":
                min_val, max_val = action["min"], action["max"]
                if action["is_int"]:
                    value = random.randint(int(min_val), int(max_val))
                else:
                    value = random.uniform(min_val, max_val)
                nexus.variables[action["variable"]] = value

            elif atype == "set_variable":
                value = evaluate_expression(action["value"], nexus.variables)
                nexus.variables[action["variable"]] = value

            # === OCR ACTIONS ===
            elif atype == "ocr_read_text":
                try:
                    region = action["region"]
                    screenshot = pyautogui.screenshot(region=region)
                    img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    text = pytesseract.image_to_string(img_cv, lang='eng').strip()
                    nexus.variables[action["variable"]] = text if text else ""
                except Exception as e:
                    print(f"[OCR Text Error] {e}")
                    nexus.variables[action["variable"]] = ""

            elif atype == "ocr_read_number":
                try:
                    region = action["region"]
                    screenshot = pyautogui.screenshot(region=region)
                    img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    text = pytesseract.image_to_string(img_cv, lang='eng')
                    numbers = re.findall(r'-?\d+\.?\d*', text)
                    value = float(numbers[0]) if numbers else 0.0
                    nexus.variables[action["variable"]] = value
                except Exception as e:
                    print(f"[OCR Number Error] {e}")
                    nexus.variables[action["variable"]] = 0.0

            # === SELENIUM ACTIONS ===
            elif atype == "selenium_open":
                if nexus.driver is None:
                    nexus.start_browser()
                nexus.driver.get(action["url"])

            elif atype == "selenium_click":
                try:
                    element = nexus.driver.find_element(By.XPATH, action["xpath"])
                    element.click()
                except Exception as e:
                    print(f"[Selenium Click Error] {e}")

            elif atype == "selenium_type":
                try:
                    element = nexus.driver.find_element(By.XPATH, action["xpath"])
                    text = interpolate_text(action["text"], nexus.variables)
                    element.clear()
                    element.send_keys(text)
                except Exception as e:
                    print(f"[Selenium Type Error] {e}")

            elif atype == "selenium_wait_element":
                try:
                    WebDriverWait(nexus.driver, action["timeout"]).until(
                        EC.presence_of_element_located((By.XPATH, action["xpath"]))
                    )
                except Exception as e:
                    print(f"[Selenium Wait Error] {e}")

            # === CONDITIONAL: IF PIXEL ===
            elif atype == "if_pixel":
                pixel = pyautogui.pixel(action["x"], action["y"])
                r, g, b = action["color"]
                tolerance = action["tolerance"]
                match = all(abs(pixel[k] - v) <= tolerance for k, v in enumerate([r, g, b]))
                if not match:
                    i = skip_to_end_if(nexus.script, i)
                    continue

            # === CONDITIONAL: IF MULTI PIXEL ===
            elif atype == "if_multi_pixel":
                conditions = action["conditions"]
                logic = action["logic"]
                matched = any_cond_match(conditions, logic)
                if not matched:
                    i = skip_to_end_if(nexus.script, i)
                    continue

            # === CONDITIONAL: IF TEXT CONTAINS ===
            elif atype == "if_text_contains":
                var_text = str(nexus.variables.get(action["variable"], ""))
                if action["contains"] not in var_text:
                    i = skip_to_else_or_end_if(nexus.script, i)
                    continue

            # === CONDITIONAL: IF NUMBER COMPARE ===
            elif atype == "if_number_compare":
                left = evaluate_expression(action["left"], nexus.variables)
                right = evaluate_expression(action["right"], nexus.variables)
                op = action["operator"]
                match = {
                    ">": left > right, "<": left < right,
                    ">=": left >= right, "<=": left <= right,
                    "==": left == right, "!=": left != right
                }[op]
                if not match:
                    i = skip_to_else_or_end_if(nexus.script, i)
                    continue

            # === WAIT ACTIONS ===
            elif atype in ["wait_for_pixel", "wait_for_multi_pixel", "wait_for_text", "wait_for_number"]:
                timeout = action.get("timeout", 999999)
                start_time = time.time()
                matched = False

                while time.time() - start_time < timeout and nexus.playing:
                    if atype == "wait_for_pixel":
                        matched = check_pixel_match(action)
                    elif atype == "wait_for_multi_pixel":
                        matched = any_cond_match(action["conditions"], action["logic"])
                    elif atype == "wait_for_text":
                        matched = check_text_contains(action["region"], action["contains"])
                    elif atype == "wait_for_number":
                        matched = check_number_condition(action["region"], action["operator"], action["value"])

                    if matched:
                        break
                    time.sleep(0.5)

                if not matched:
                    i = skip_to_else_or_end_wait(nexus.script, i)
                    continue

            # === TIME SCHEDULING ===
            elif atype == "wait_for_time":
                try:
                    target = parse_wait_time(action["time"])
                    nexus.root.after(0, lambda t=target.strftime("%Y-%m-%d %H:%M:%S"): 
                                     nexus.status.config(text=f"Waiting until {t}..."))
                    while nexus.playing and datetime.now() < target:
                        time.sleep(0.1)
                except Exception as e:
                    print(f"[Wait Time Error] {e}")

            # === LOOP CONTROL ===
            elif atype == "loop_times":
                count = action["count"]
                key = i
                if count == 0:  # infinite handled by outer loop
                    i += 1
                    continue
                if key not in nexus._loop_counters:
                    nexus._loop_counters[key] = count
                if nexus._loop_counters[key] > 1:
                    nexus._loop_counters[key] -= 1
                    i += 1
                    continue
                else:
                    del nexus._loop_counters[key]
                    i = skip_to_end_loop(nexus.script, i)
                    continue

            elif atype == "loop_until":
                cond = action["condition"]
                matched = check_pixel_match(cond) if cond["type"] == "pixel" else False
                if matched:
                    i = skip_to_end_loop(nexus.script, i)
                # else continue to next action

            elif atype == "end_loop":
                i = jump_to_loop_start(nexus.script, i)
                continue

            elif atype in ["else", "end_if", "end_wait"]:
                pass  # handled by skip functions

            i += 1

        # Update status bar
        elapsed = int(time.time() - nexus.start_time)
        status_text = f"Cycle {cycle}{' (Infinite)' if infinite else ''} • Actions: {nexus.click_count:,} • {elapsed}s"
        nexus.root.after(0, lambda: nexus.status.config(text=status_text))

    # Playback finished
    nexus.playing = False
    nexus.root.after(0, lambda: (
        nexus.play_btn.config(state="normal"),
        nexus.status.config(text="Playback finished!")
    ))


# === HELPER FUNCTIONS ===

def check_pixel_match(action):
    pixel = pyautogui.pixel(action["x"], action["y"])
    r, g, b = action["color"]
    tol = action["tolerance"]
    return all(abs(pixel[k] - v) <= tol for k, v in enumerate([r, g, b]))

def any_cond_match(conditions, logic):
    for cond in conditions:
        pixel = pyautogui.pixel(cond["x"], cond["y"])
        r, g, b = cond["color"]
        tol = cond["tolerance"]
        match = all(abs(pixel[k] - v) <= tol for k, v in enumerate([r, g, b]))
        if (logic == "OR" and match) or (logic == "AND" and not match):
            return logic == "OR"
    return logic == "AND"

def check_text_contains(region, target_text):
    try:
        screenshot = pyautogui.screenshot(region=region)
        img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        text = pytesseract.image_to_string(img_cv, lang='eng').strip()
        return target_text in text
    except:
        return False

def check_number_condition(region, operator, target_value):
    try:
        screenshot = pyautogui.screenshot(region=region)
        img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        text = pytesseract.image_to_string(img_cv, lang='eng')
        numbers = re.findall(r'-?\d+\.?\d*', text)
        if not numbers:
            return False
        value = float(numbers[0])
        return {
            ">": value > target_value, "<": value < target_value,
            ">=": value >= target_value, "<=": value <= target_value,
            "==": value == target_value, "!=": value != target_value
        }[operator]
    except:
        return False

def skip_to_else_or_end_if(script, i):
    depth = 1
    i += 1
    while i < len(script):
        if script[i]["type"] in ["if_pixel", "if_multi_pixel", "if_text_contains", "if_number_compare",
                                 "wait_for_pixel", "wait_for_multi_pixel", "wait_for_text", "wait_for_number"]:
            depth += 1
        elif script[i]["type"] == "else" and depth == 1:
            return i + 1
        elif script[i]["type"] == "end_if" and depth == 1:
            return i + 1
        elif script[i]["type"] == "end_if":
            depth -= 1
        i += 1
    return i

def skip_to_end_if(script, i):
    depth = 1
    i += 1
    while i < len(script):
        if script[i]["type"].startswith("if_"):
            depth += 1
        elif script[i]["type"] == "end_if":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return i

def skip_to_end_wait(script, i):
    depth = 1
    i += 1
    while i < len(script):
        if script[i]["type"].startswith("wait_for_"):
            depth += 1
        elif script[i]["type"] == "end_wait":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return i

def skip_to_end_loop(script, i):
    depth = 1
    i += 1
    while i < len(script):
        if script[i]["type"] in ["loop_times", "loop_until"]:
            depth += 1
        elif script[i]["type"] == "end_loop":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return i

def jump_to_loop_start(script, i):
    depth = 1
    j = i - 1
    while j >= 0:
        if script[j]["type"] == "end_loop":
            depth += 1
        elif script[j]["type"] in ["loop_times", "loop_until"]:
            depth -= 1
            if depth == 0:
                return j
        j -= 1
    return i + 1