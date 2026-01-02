# actions/selenium.py
from tkinter import simpledialog, messagebox

def get_selenium_actions(nexus):
    def add_selenium_open():
        url = simpledialog.askstring("Open URL", "Enter URL:")
        if url:
            nexus.script.append({
                "type": "selenium_open",
                "url": url,
                "delay": 2.0
            })
            nexus.refresh_tree()

    def add_selenium_click():
        xpath = simpledialog.askstring("Click Element", "XPath:")
        if xpath:
            nexus.script.append({
                "type": "selenium_click",
                "xpath": xpath,
                "delay": 0.5
            })
            nexus.refresh_tree()

    def add_selenium_type():
        xpath = simpledialog.askstring("Type Into", "XPath of input field:")
        if not xpath: return
        text = simpledialog.askstring("Text", "Text to type (use ${var}):")
        if text is None: return
        nexus.script.append({
            "type": "selenium_type",
            "xpath": xpath,
            "text": text,
            "delay": 0.5
        })
        nexus.refresh_tree()

    def add_selenium_wait_element():
        xpath = simpledialog.askstring("Wait Element", "XPath to wait for:")
        if not xpath: return
        timeout = simpledialog.askinteger("Timeout", "Max wait seconds:", initialvalue=30)
        if timeout is None: return
        nexus.script.append({
            "type": "selenium_wait_element",
            "xpath": xpath,
            "timeout": timeout,
            "delay": 0.1
        })
        nexus.refresh_tree()

    return {
        "add_selenium_open": add_selenium_open,
        "add_selenium_click": add_selenium_click,
        "add_selenium_type": add_selenium_type,
        "add_selenium_wait_element": add_selenium_wait_element,
    }