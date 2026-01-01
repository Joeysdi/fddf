# actions/trading.py
from tkinter import simpledialog, messagebox

def get_trading_actions(nexus):
    def add_trading_buy_market():
        xpath = simpledialog.askstring("Buy Market Button", "XPath:")
        if xpath:
            nexus.script.append({"type": "selenium_click", "xpath": xpath, "delay": 0.5})
            nexus.refresh_tree()

    def add_trading_sell_market():
        xpath = simpledialog.askstring("Sell Market Button", "XPath:")
        if xpath:
            nexus.script.append({"type": "selenium_click", "xpath": xpath, "delay": 0.5})
            nexus.refresh_tree()

    def add_trading_buy_limit():
        price_xpath = simpledialog.askstring("Price Field XPath", "Price input XPath:")
        if not price_xpath: return
        qty_xpath = simpledialog.askstring("Quantity Field XPath", "Quantity input XPath:")
        if not qty_xpath: return
        buy_xpath = simpledialog.askstring("Buy Button XPath", "Buy Limit button XPath:")
        if not buy_xpath: return
        price = simpledialog.askstring("Price", "Price (or ${var}, blank to skip):")
        qty = simpledialog.askstring("Quantity", "Quantity (or ${var}, blank to skip):")
        if price:
            nexus.script.append({"type": "selenium_type", "xpath": price_xpath, "text": price, "delay": 0.5})
        if qty:
            nexus.script.append({"type": "selenium_type", "xpath": qty_xpath, "text": qty, "delay": 0.5})
        nexus.script.append({"type": "selenium_click", "xpath": buy_xpath, "delay": 0.5})
        nexus.refresh_tree()

    def add_trading_sell_limit():
        price_xpath = simpledialog.askstring("Price Field XPath", "Price input XPath:")
        if not price_xpath: return
        qty_xpath = simpledialog.askstring("Quantity Field XPath", "Quantity input XPath:")
        if not qty_xpath: return
        sell_xpath = simpledialog.askstring("Sell Button XPath", "Sell Limit button XPath:")
        if not sell_xpath: return
        price = simpledialog.askstring("Price", "Price (or ${var}, blank to skip):")
        qty = simpledialog.askstring("Quantity", "Quantity (or ${var}, blank to skip):")
        if price:
            nexus.script.append({"type": "selenium_type", "xpath": price_xpath, "text": price, "delay": 0.5})
        if qty:
            nexus.script.append({"type": "selenium_type", "xpath": qty_xpath, "text": qty, "delay": 0.5})
        nexus.script.append({"type": "selenium_click", "xpath": sell_xpath, "delay": 0.5})
        nexus.refresh_tree()

    def add_trading_confirm():
        xpath = simpledialog.askstring("Confirm Button XPath", "Confirm/Submit XPath:")
        if xpath:
            nexus.script.append({"type": "selenium_click", "xpath": xpath, "delay": 0.5})
            nexus.refresh_tree()

    def calc_position_size():
        risk_pct = simpledialog.askfloat("Risk %", "Risk percent per trade:", initialvalue=1.0)
        if risk_pct is None: return
        sl_distance = simpledialog.askfloat("SL Distance", "Distance from entry to SL:")
        if sl_distance is None or sl_distance == 0: return
        balance = 10000.0  # hardcoded as in original
        risk_amount = balance * (risk_pct / 100)
        quantity = risk_amount / sl_distance
        messagebox.showinfo("Position Size", f"Risk ${risk_amount:.2f}\nQuantity: {quantity:.6f}")

    def add_monitor_sl_tp():
        region = simpledialog.askstring("Price Region", "left,top,width,height:")
        if not region: return
        try:
            tuple(map(int, region.split(',')))
        except:
            messagebox.showerror("Error", "Invalid region")
            return
        nexus.script.append({
            "type": "monitor_sl_tp",
            "price_region": tuple(map(int, region.split(','))),
            "delay": 1.0
        })
        nexus.refresh_tree()

    return {
        "add_trading_buy_market": add_trading_buy_market,
        "add_trading_sell_market": add_trading_sell_market,
        "add_trading_buy_limit": add_trading_buy_limit,
        "add_trading_sell_limit": add_trading_sell_limit,
        "add_trading_confirm": add_trading_confirm,
        "calc_position_size": calc_position_size,
        "add_monitor_sl_tp": add_monitor_sl_tp,
    }