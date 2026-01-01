# main.py
import ttkbootstrap as ttkb
from core import NexusClicker

if __name__ == "__main__":
    root = ttkb.Window(themename="superhero")
    app = NexusClicker(root)
    root.mainloop()