# ui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import json
from actions import register_all_actions

def build_ui(nexus):
    nexus.root.title("NEXUS CLICKER v7.3 — CLEAN UI")
    nexus.root.geometry("1350x920")
    nexus.root.configure(bg="#0d1117")

    # Header
    header = ttk.Label(nexus.root, text="NEXUS CLICKER v7.3", font=("Impact", 44, "bold"), bootstyle="danger inverse")
    header.pack(pady=(20, 10))

    # Top bar
    top_bar = ttk.Frame(nexus.root)
    top_bar.pack(pady=10, fill="x", padx=20)

    # Main controls
    main_ctrl = ttk.Frame(top_bar)
    main_ctrl.pack(side="left", padx=30)

    nexus.record_btn = ttk.Button(main_ctrl, text="RECORD (F6)", bootstyle="warning-outline", width=18, command=nexus.toggle_record)
    nexus.record_btn.pack(side="left", padx=8)

    nexus.play_btn = ttk.Button(main_ctrl, text="PLAY (F7)", bootstyle="success", width=18, command=nexus.play_script)
    nexus.play_btn.pack(side="left", padx=8)

    nexus.stop_btn = ttk.Button(main_ctrl, text="STOP (F8)", bootstyle="danger", width=18, command=nexus.stop_all)
    nexus.stop_btn.pack(side="left", padx=8)

    ttk.Separator(main_ctrl, orient="vertical", bootstyle="secondary").pack(side="left", fill="y", padx=20)

    ttk.Button(main_ctrl, text="Save Script", bootstyle="info-outline", width=14, command=nexus.save_script).pack(side="left", padx=5)
    ttk.Button(main_ctrl, text="Load Script", bootstyle="secondary-outline", width=14, command=nexus.load_script).pack(side="left", padx=5)

    ttk.Label(main_ctrl, text="Loops:", font=("Consolas", 11)).pack(side="left", padx=(50, 8))
    nexus.loop_var = tk.IntVar(value=0)
    ttk.Spinbox(main_ctrl, from_=0, to=999999, textvariable=nexus.loop_var, width=12).pack(side="left", padx=5)
    ttk.Label(main_ctrl, text="(0 = Infinite)", foreground="#888").pack(side="left", padx=8)

    # Add Action Menu
    menu_btn = ttk.Menubutton(top_bar, text="Add Action ▼", bootstyle="primary", width=24)
    menu_btn.pack(side="right", padx=40)

    menu = tk.Menu(menu_btn, tearoff=0)
    menu_btn["menu"] = menu

    # Submenus
    basic_menu = tk.Menu(menu, tearoff=0)
    cond_menu = tk.Menu(menu, tearoff=0)
    ocr_menu = tk.Menu(menu, tearoff=0)
    selenium_menu = tk.Menu(menu, tearoff=0)
    trading_menu = tk.Menu(menu, tearoff=0)
    flow_menu = tk.Menu(menu, tearoff=0)

    menu.add_cascade(label="Basic Actions", menu=basic_menu)
    menu.add_cascade(label="Conditional (If / Wait)", menu=cond_menu)
    menu.add_cascade(label="OCR & Variables", menu=ocr_menu)
    menu.add_cascade(label="Browser (Selenium)", menu=selenium_menu)
    menu.add_cascade(label="Trading Actions", menu=trading_menu)
    menu.add_cascade(label="Loops & Flow", menu=flow_menu)
    menu.add_separator()
    menu.add_command(label="📖 Instructions / Help", command=nexus.show_instructions)

    # Register all actions
    actions = register_all_actions(nexus)

    # Populate menus
    basic_menu.add_command(label="Add Click", command=actions["add_click_here"])
    basic_menu.add_command(label="Add Text", command=actions["add_text_action"])
    basic_menu.add_command(label="Add Delay", command=actions["add_delay_action"])

    cond_menu.add_command(label="If Pixel Color", command=actions["add_if_pixel"])
    cond_menu.add_command(label="If Multi-Pixel", command=actions["add_if_multi_pixel"])
    cond_menu.add_command(label="Wait For Pixel", command=actions["add_wait_for_pixel"])
    cond_menu.add_command(label="If Text Contains", command=actions["add_if_text_contains"])
    cond_menu.add_command(label="If Number Compare", command=actions["add_if_number_compare"])
    cond_menu.add_separator()
    cond_menu.add_command(label="Add Else", command=actions["add_else"])

    ocr_menu.add_command(label="OCR Read Text → Variable", command=actions["add_ocr_read_text"])
    ocr_menu.add_command(label="OCR Read Number → Variable", command=actions["add_ocr_read_number"])
    ocr_menu.add_separator()
    ocr_menu.add_command(label="Wait For Text", command=actions["add_wait_for_text"])
    ocr_menu.add_command(label="Wait For Number", command=actions["add_wait_for_number"])
    ocr_menu.add_separator()
    ocr_menu.add_command(label="Generate Random → Variable", command=actions["add_random_number"])
    ocr_menu.add_command(label="Set Variable", command=actions["add_set_variable"])

    selenium_menu.add_command(label="Open URL", command=actions["add_selenium_open"])
    selenium_menu.add_command(label="Click Element (XPath)", command=actions["add_selenium_click"])
    selenium_menu.add_command(label="Type Text (XPath)", command=actions["add_selenium_type"])
    selenium_menu.add_command(label="Wait For Element (XPath)", command=actions["add_selenium_wait_element"])

    trading_menu.add_command(label="Buy Market", command=actions["add_trading_buy_market"])
    trading_menu.add_command(label="Sell Market", command=actions["add_trading_sell_market"])
    trading_menu.add_command(label="Buy Limit Order", command=actions["add_trading_buy_limit"])
    trading_menu.add_command(label="Sell Limit Order", command=actions["add_trading_sell_limit"])
    trading_menu.add_command(label="Confirm Order", command=actions["add_trading_confirm"])
    trading_menu.add_separator()
    trading_menu.add_command(label="Calculate Position Size", command=actions["calc_position_size"])
    trading_menu.add_command(label="Monitor SL/TP (OCR)", command=actions["add_monitor_sl_tp"])

    flow_menu.add_command(label="Loop N Times", command=actions["add_loop_times"])
    flow_menu.add_command(label="Loop Until Pixel", command=actions["add_loop_until"])
    flow_menu.add_separator()
    flow_menu.add_command(label="Wait Until Time / Date", command=actions["add_wait_for_time"])

    # Script Editor
    editor_frame = ttk.LabelFrame(nexus.root, text=" Script Editor – Right-click cells to edit ", bootstyle="primary")
    editor_frame.pack(fill="both", expand=True, padx=40, pady=20)

    columns = ("#", "Type", "X", "Y", "Text/Key", "Delay (s)")
    nexus.tree = ttk.Treeview(editor_frame, columns=columns, show="headings", height=24)
    for col in columns:
        nexus.tree.heading(col, text=col)
        nexus.tree.column(col, width=180, anchor="center")
    nexus.tree.column("#", width=60)
    nexus.tree.column("Type", width=220)
    nexus.tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(editor_frame, orient="vertical", command=nexus.tree.yview)
    scrollbar.pack(side="right", fill="y")
    nexus.tree.config(yscrollcommand=scrollbar.set)

    nexus.tree.bind("<Button-3>", nexus.right_click_edit)

    # Bottom bar
    bottom_bar = ttk.Frame(nexus.root)
    bottom_bar.pack(pady=20)

    ttk.Button(bottom_bar, text="Delete Selected", bootstyle="danger-outline", width=18, command=nexus.delete_selected).pack(side="left", padx=20)
    ttk.Button(bottom_bar, text="Clear All Script", bootstyle="dark", width=18, command=nexus.clear_script).pack(side="left", padx=10)

    # Status bar
    nexus.status = ttk.Label(nexus.root, text="Status: Ready – Modular UI loaded!", relief="sunken", font=("Consolas", 11), bootstyle="inverse")
    nexus.status.pack(side="bottom", fill="x")

    # Floating panel
    nexus.create_floating_panel()

def create_floating_panel(nexus):
    nexus.floating = tk.Toplevel()
    nexus.floating.overrideredirect(True)
    nexus.floating.geometry("280x110+50+50")
    nexus.floating.attributes("-topmost", True)
    nexus.floating.config(bg="#161b22", bd=2, relief="raised")

    ttk.Label(nexus.floating, text="NEXUS v7.3", font=("Arial", 16, "bold"), background="#161b22", foreground="#39ff14").pack(pady=10)

    row = ttk.Frame(nexus.floating)
    row.pack(pady=8)
    ttk.Button(row, text="REC F6", width=8, bootstyle="danger-outline", command=nexus.toggle_record).pack(side="left", padx=8)
    ttk.Button(row, text="PLAY F7", width=8, bootstyle="success", command=nexus.play_script).pack(side="left", padx=8)
    ttk.Button(row, text="STOP F8", width=8, bootstyle="danger", command=nexus.stop_all).pack(side="left", padx=8)

    # Drag to move
    def start_drag(e):
        nexus.floating.x = e.x
        nexus.floating.y = e.y

    def drag(e):
        x = nexus.floating.winfo_x() + (e.x - nexus.floating.x)
        y = nexus.floating.winfo_y() + (e.y - nexus.floating.y)
        nexus.floating.geometry(f"+{x}+{y}")

    nexus.floating.bind("<Button-1>", start_drag)
    nexus.floating.bind("<B1-Motion>", drag)