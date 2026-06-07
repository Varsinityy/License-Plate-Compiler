import sys
import os

if "--splash" in sys.argv:
    try:
        import tkinter as _tk
        import itertools
        _splash = _tk.Tk()
        _splash.overrideredirect(True)
        _splash_width = 400
        _splash_height = 200
        _screen_width = _splash.winfo_screenwidth()
        _screen_height = _splash.winfo_screenheight()
        _x = (_screen_width / 2) - (_splash_width / 2)
        _y = (_screen_height / 2) - (_splash_height / 2)
        _splash.geometry(f'{_splash_width}x{_splash_height}+{int(_x)}+{int(_y)}')
        _splash.configure(bg="#09090b")
        
        _label = _tk.Label(_splash, text="Loading Varsinity's Plate Compiler...", fg="#fafafa", bg="#09090b", font=("Helvetica", 12, "bold"))
        _label.pack(expand=True, pady=(40, 10))
        
        _spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        _sub = _tk.Label(_splash, text="Initializing Resources... ⠋", fg="#71717a", bg="#09090b", font=("Helvetica", 10))
        _sub.pack(pady=(0, 40))
        
        def _animate():
            _sub.configure(text=f"Initializing Resources... {next(_spinner)}")
            _splash.after(80, _animate)
            
        _animate()
        _splash.mainloop()
    except Exception:
        pass
    sys.exit(0)

import subprocess
try:
    if getattr(sys, 'frozen', False):
        _splash_proc = subprocess.Popen([sys.executable, "--splash"])
    else:
        _splash_proc = subprocess.Popen([sys.executable, __file__, "--splash"])
except Exception:
    _splash_proc = None

import shutil
import requests
import tempfile
import threading
import math
import subprocess
import time
import json
import io
import queue
import socket
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_TKDND = True
except ImportError:
    HAS_TKDND = False
    class TkinterDnD:
        class DnDWrapper:
            pass
    DND_FILES = None
try:
    from pypresence import Presence
    HAS_DISCORD = True
except ImportError:
    HAS_DISCORD = False
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageTk
from io import BytesIO
import customtkinter as ctk
from tkinter import filedialog, messagebox

try:
    from viewport3d import Viewport3D, HAS_OPENGL
    from modelbin_parser import parseModelbin
except ImportError:
    HAS_OPENGL = False

def resourcePath(relativePath):
    try:
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(basePath, relativePath))

try:
    from ctypes import windll, c_int, byref, sizeof
except ImportError:
    windll = None

ctk.set_appearance_mode("Dark")

class DraggableMixin:
    def startMove(self, event):
        self.x = event.x
        self.y = event.y

    def doMove(self, event):
        x = self.winfo_x() + (event.x - self.x)
        y = self.winfo_y() + (event.y - self.y)
        self.geometry(f"+{x}+{y}")

COLORS = {
    "bg_primary": "#09090b", 
    "bg_content": "#040405",
    "bg_secondary": "#0f0f12",
    "bg_glass": "#18181b",
    "bg_card": "#1c1c21",
    "border": "#27272a",
    "accent_primary": "#6366f1",    
    "accent_secondary": "#8b5cf6",
    "accent_success": "#10b981",    
    "accent_danger": "#ef4444",     
    "text_primary": "#fafafa",
    "text_secondary": "#a1a1aa",
    "text_muted": "#71717a",
}

APP_VERSION = "1.9.1"

EU_UK_FILES = [
    "plate_eu1_base_diff_82ddf780-5958-4917-807d-31a9a76e08fc.swatchbin",
    "plate_eu1_base_mask_5220040e-6dac-4569-9ac7-c258b8e0324f.swatchbin",
    "plate_eu1_base_nrml_49d025f0-f90c-4d68-9d39-70f82c990ba7.swatchbin",
    "plate_eu2_base_diff_1ff3ad60-d18f-4a99-bf74-9a960ae65f9a.swatchbin",
    "plate_eu2_base_mask_a4cf0380-6e6a-4c56-a82e-88f2d47db004.swatchbin",
    "plate_eu2_base_nrml_c54b9f27-ef27-4b5c-a21e-68e4aea7b4f3.swatchbin",
    "plate_eu_fm1_base_diff_82ddf780-5958-4917-807d-31a9a76e08fc.swatchbin",
    "plate_eu_fm1_base_mask_5220040e-6dac-4569-9ac7-c258b8e0324f.swatchbin",
    "plate_eu_fm1_base_nrml_49d025f0-f90c-4d68-9d39-70f82c990ba7.swatchbin",
    "plate_eu_fm2_base_diff_1ff3ad60-d18f-4a99-bf74-9a960ae65f9a.swatchbin",
    "plate_eu_fm2_base_mask_a4cf0380-6e6a-4c56-a82e-88f2d47db004.swatchbin",
    "plate_eu_fm2_base_nrml_c54b9f27-ef27-4b5c-a21e-68e4aea7b4f3.swatchbin",
    "plate_uk_front_diff_e257da84-3e8f-461b-8a6e-bcf53e35c9fb.swatchbin",
    "plate_uk_front_mask_543937d9-230f-4fc8-a52c-6859325b0fd1.swatchbin",
    "plate_uk_front_nrml_f6ad73ba-07ae-448e-91af-b2f47fc97f2d.swatchbin"
]

EU_UK_ATLAS_FILES = [
    "plate_eu1_atlas_opac_4887f700-955a-41f4-8af4-1a57bd737d6f.swatchbin",
    "plate_eu1_atlas_diff_6b219b24-3b6f-4602-a889-a2179445bae9.swatchbin",
    "plate_eu2_atlas_diff_b1933fbb-8206-4042-86cc-2ff8c586403e.swatchbin"
]

US_MX_FILES = [
    "plate_mx1_base_diff_b94b25a0-e249-474c-aed5-f5f12f86c619.swatchbin",
    "plate_mx1_base_mask_74462cfb-1183-4107-893e-7d8937b56ba8.swatchbin",
    "plate_mx1_base_nrml_9f0909ee-0a46-4187-8430-6066bb55bf98.swatchbin",
    "plate_mx_front_base_diff_f1f25da7-b539-48e0-92f2-664081c8a716.swatchbin",
    "plate_mx_front_base_mask_6f622e53-b251-449e-8dc2-b328a9863246.swatchbin",
    "plate_us2_base_diff_eeb5bd05-1328-4c59-9797-c894e1bf52c6.swatchbin",
    "plate_us2_base_mask_e8ffc6dc-c3a5-47b3-8f2a-f2420faa4827.swatchbin",
    "plate_us2_base_nrml_556f2b0f-4117-4d2c-8350-36b737784fe7.swatchbin",
    "plate_mx_front_base_nrml_156822c2-2d3b-4426-a975-77592427813f.swatchbin"
]

US_MX_ATLAS_FILES = [
    "plate_mx_front_atlas_opac_7c7402c4-c592-46d2-90d5-67cdb8f15d2f.swatchbin",
    "plate_mx_front_atlas_diff_4eb38075-5664-468d-bf1e-08c442c07293.swatchbin",
    "plate_mx1_atlas_opac_98045415-4af6-4960-a3ae-dd4cf0759a5c.swatchbin",
    "plate_mx1_atlas_nrml_226f19e0-7e12-4b82-997c-676d1b023f3f.swatchbin",
    "plate_mx1_atlas_diff_127e70b2-4da6-49c7-a64e-820fa8f57067.swatchbin"
]

PLATE_TEMPLATES = {
    "Utah (Black)": {
        "image_tags": "utah template without outline.png", 
        "image_no_tags": "utah template without outline no tags.png",
        "image_tags_outline": "utah template with outline.png",
        "image_no_tags_outline": "utah template with outline no tags.png",
        "has_outline_option": True,
        "cobb_overlay": "cobb logo.png",
        "cobb_coords": (0, 0),
        "has_cobb_option": True,
        "font_file": "DriverGothic.ttf",
        "font_size": 1150,
        "text_color": "#ffffff",
        "coords": (2000, 700),
    },
    "California (Standard)": {
        "image_tags": "cali template.png",
        "image_no_tags": "cali template no tags.png",
        "has_outline_option": False,
        "font_file": "DriverGothic.ttf",
        "font_size": 1150,
        "text_color": "#2a2a81",
        "coords": (2000, 700),
    },
    "California (Black)": {
        "image_tags": "cali template black.png",
        "image_no_tags": "cali template black no tags.png",
        "image_tags_outline": "cali template black tags.png",
        "image_no_tags_outline": "cali template black outline tags.png",
        "has_outline_option": True,
        "font_file": "DriverGothic.ttf",
        "font_size": 1150,
        "text_color": "#fdcc02",
        "coords": (2000, 700),
    },
    "Texas (Standard)": {
        "image_no_tags": "texas template standard.png",
        "image_no_tags_outline": "texas standard outline.png",
        "has_tags_option": False,
        "has_outline_option": True,
        "font_file": "DriverGothic.ttf",
        "font_size": 1150,
        "text_color": "#000000",
        "coords": (2000, 750),
    },
    "Texas (Black)": {
        "image_no_tags": "texas template black.png",
        "image_no_tags_outline": "texas black outline.png",
        "has_tags_option": False,
        "has_outline_option": True,
        "font_file": "DriverGothic.ttf",
        "font_size": 1150,
        "text_color": "#ffffff",
        "coords": (2000, 750),
    },
    "Custom Black EU": {
        "image_no_tags": "custom black eu outline.png",
        "has_tags_option": False,
        "has_outline_option": False,
        "font_file": "LicensePlate.ttf",
        "font_size": 710,
        "text_color": "#ffffff",
        "coords": (2134, 460),
    },
    "Japan": {
        "image_no_tags": "JPN_Template.png",
        "has_tags_option": False,
        "has_outline_option": True,
        "is_japan": True
    }
}

class MaskPainter(DraggableMixin, ctk.CTkToplevel):
    def __init__(self, master, sourcePath, maskPath, callback):
        super().__init__(master)
        
        self.overrideredirect(True)
        self.configure(fg_color=COLORS["border"])
        
        self.transient(master)  
        self.grab_set()         
        self.focus_force()      
        
        if windll:
            try:
                self.update() 
                HWND = windll.user32.GetParent(self.winfo_id())
                windll.dwmapi.DwmSetWindowAttribute(HWND, 33, byref(c_int(2)), sizeof(c_int(2)))
            except (AttributeError, OSError):
                pass

        self.callback = callback
        self.brushSize = 15
        
        self.drawColor = "red"
        self.maskColor = "black"

        self.container = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"], corner_radius=0, border_width=0)
        self.container.pack(fill="both", expand=True, padx=2, pady=2)

        self.titlebar = ctk.CTkFrame(self.container, fg_color=COLORS["bg_secondary"], height=40, corner_radius=0)
        self.titlebar.pack(fill="x", side="top")
        self.titlebar.pack_propagate(False)
        self.titlebar.bind("<ButtonPress-1>", self.startMove)
        self.titlebar.bind("<B1-Motion>", self.doMove)

        leftFrame = ctk.CTkFrame(self.titlebar, fg_color="transparent")
        leftFrame.pack(side="left", padx=10, fill="y")
        leftFrame.bind("<ButtonPress-1>", self.startMove)
        leftFrame.bind("<B1-Motion>", self.doMove)

        try:
            logoImg = master.titleIconLabel.cget("image")
            self.titleIconLabel = ctk.CTkLabel(leftFrame, text="", image=logoImg)
        except Exception:
            self.titleIconLabel = ctk.CTkLabel(leftFrame, text="🖌️", font=ctk.CTkFont(size=16))
            
        self.titleIconLabel.pack(side="left", padx=(5, 5))
        self.titleIconLabel.bind("<ButtonPress-1>", self.startMove)
        self.titleIconLabel.bind("<B1-Motion>", self.doMove)

        titleLabel = ctk.CTkLabel(leftFrame, text="Draw Custom Mask", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_primary"])
        titleLabel.pack(side="left", padx=5)
        titleLabel.bind("<ButtonPress-1>", self.startMove)
        titleLabel.bind("<B1-Motion>", self.doMove)

        closeBtn = ctk.CTkButton(self.titlebar, text="✕", width=45, height=40, fg_color="transparent", hover_color=COLORS["accent_danger"], command=self.destroy, corner_radius=0)
        closeBtn.pack(side="right")

        minBtn = ctk.CTkButton(self.titlebar, text="—", width=45, height=40, fg_color="transparent", hover_color=COLORS["bg_card"], command=self.minimizeWindow, corner_radius=0)
        minBtn.pack(side="right")

        self.sourceImg = Image.open(sourcePath).convert("RGBA")
        w, h = self.sourceImg.size
        scale = 800 / w if w > 800 else 1
        self.newW, self.newH = int(w * scale), int(h * scale)
        
        self.visualImg = self.sourceImg.resize((self.newW, self.newH)).convert("RGBA")
        
        if maskPath and os.path.exists(maskPath):
            loadedMask = Image.open(maskPath).convert("L")
            self.maskImg = loadedMask.resize((self.newW, self.newH), Image.NEAREST)
            
            redLayer = Image.new("RGBA", self.visualImg.size, "red")
            whiteLayer = Image.new("RGBA", self.visualImg.size, "white")
            
            blackMask = self.maskImg.point(lambda p: 255 if p < 10 else 0, mode="L")
            whiteMask = self.maskImg.point(lambda p: 255 if p > 245 else 0, mode="L")
            
            self.visualImg.paste(redLayer, (0,0), blackMask)
            self.visualImg.paste(whiteLayer, (0,0), whiteMask)
        else:
            self.maskImg = self.visualImg.copy().convert("L")

        self.visualDraw = ImageDraw.Draw(self.visualImg)
        self.maskDraw = ImageDraw.Draw(self.maskImg)

        self.history = []

        ctrl = ctk.CTkFrame(self.container, fg_color="transparent")
        ctrl.pack(fill="x", padx=10, pady=10)

        self.btnBlack = ctk.CTkButton(
            ctrl, 
            text=" Black (Inward)", 
            image=self.master.loadIcon("paintbrush.png", size=16),
            fg_color="#1c1c21", 
            border_width=2, 
            border_color=COLORS["accent_primary"], 
            command=lambda: self.setColor("red", "black")
        )
        self.btnBlack.pack(side="left", padx=5)
        
        self.btnWhite = ctk.CTkButton(
            ctrl, 
            text=" White (Outward)", 
            image=self.master.loadIcon("paintbrush.png", size=16),
            fg_color="#a1a1aa", 
            text_color="black", 
            border_width=2, 
            border_color=COLORS["bg_primary"], 
            command=lambda: self.setColor("white", "white")
        )
        self.btnWhite.pack(side="left", padx=5)
        
        self.slider = ctk.CTkSlider(ctrl, from_=2, to=80, command=self.setSize)
        self.slider.set(15)
        self.slider.pack(side="left", padx=10)

        ctk.CTkButton(
            ctrl, 
            text=" Undo", 
            image=self.master.loadIcon("undo.png", size=16),
            width=80, 
            fg_color=COLORS["bg_card"], 
            command=self.undo
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            ctrl, 
            text=" Apply Mask", 
            image=self.master.loadIcon("square-check-big.png", size=18),
            fg_color="#10b981", 
            command=self.apply
        ).pack(side="right", padx=5)

        self.canvas = ctk.CTkCanvas(self.container, width=self.newW, height=self.newH, cursor="crosshair", highlightthickness=0, bg=COLORS["bg_primary"])
        self.canvas.pack(pady=(0, 10), padx=10)

        self.tkImg = ImageTk.PhotoImage(self.visualImg)
        self.canvasImgId = self.canvas.create_image(0, 0, anchor="nw", image=self.tkImg)

        self.canvas.bind("<ButtonPress-1>", self.startPaint)
        self.canvas.bind("<B1-Motion>", self.paint)
        
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-Z>", lambda e: self.undo()) 
        self.canvas.bind("<Control-z>", lambda e: self.undo())
        self.canvas.bind("<Control-Z>", lambda e: self.undo())

    def minimizeWindow(self):
        try:
            if windll:
                hwnd = windll.user32.GetParent(self.winfo_id())
                windll.user32.ShowWindow(hwnd, 6) 
            else:
                self.iconify()
        except Exception:
            self.iconify()

    def setColor(self, vColor, mColor):
        self.drawColor = vColor
        self.maskColor = mColor
        
        if mColor == "black":
            self.btnBlack.configure(border_color=COLORS["accent_primary"])
            self.btnWhite.configure(border_color=COLORS["bg_primary"])
        else:
            self.btnWhite.configure(border_color=COLORS["accent_primary"])
            self.btnBlack.configure(border_color=COLORS["bg_primary"])

    def setSize(self, val): 
        self.brushSize = int(val)

    def startPaint(self, event):
        self.canvas.focus_set()
        
        if len(self.history) > 20: 
            self.history.pop(0)
        self.history.append((self.visualImg.copy(), self.maskImg.copy()))
        
        self.canvas.delete("brush_stroke")
        self.tkImg = ImageTk.PhotoImage(self.visualImg)
        self.canvas.itemconfig(self.canvasImgId, image=self.tkImg)
        
        self.paint(event)

    def paint(self, event):
        x, y = event.x, event.y
        r = self.brushSize
        
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=self.drawColor, outline=self.drawColor, tags="brush_stroke")
        
        self.visualDraw.ellipse([x-r, y-r, x+r, y+r], fill=self.drawColor)
        self.maskDraw.ellipse([x-r, y-r, x+r, y+r], fill=self.maskColor)
        
    def undo(self):
        if not self.history:
            return
            
        prevVisual, prevMask = self.history.pop()
        
        self.visualImg = prevVisual
        self.visualDraw = ImageDraw.Draw(self.visualImg)
        
        self.maskImg = prevMask
        self.maskDraw = ImageDraw.Draw(self.maskImg)
        
        self.canvas.delete("brush_stroke")
        self.tkImg = ImageTk.PhotoImage(self.visualImg)
        self.canvas.itemconfig(self.canvasImgId, image=self.tkImg)

    def apply(self):
        temp = os.path.join(tempfile.gettempdir(), "custom_drawn_mask.png")
        finalMask = self.maskImg.resize(self.sourceImg.size, Image.NEAREST)
        finalMask.save(temp)
        self.callback(temp)
        self.destroy()

class NormalPainter(DraggableMixin, ctk.CTkToplevel):
    def __init__(self, master, baseImg, callback):
        super().__init__(master)
        self.overrideredirect(True)
        self.configure(fg_color=COLORS["border"])
        self.transient(master)  
        self.grab_set()         
        self.focus_force()      
        
        if windll:
            try:
                self.update() 
                HWND = windll.user32.GetParent(self.winfo_id())
                windll.dwmapi.DwmSetWindowAttribute(HWND, 33, byref(c_int(2)), sizeof(c_int(2)))
            except (AttributeError, OSError):
                pass

        self.callback = callback
        self.brushSize = 20
        self.drawColor = "#8080ff" 

        self.container = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"], corner_radius=0, border_width=0)
        self.container.pack(fill="both", expand=True, padx=2, pady=2)

        self.titlebar = ctk.CTkFrame(self.container, fg_color=COLORS["bg_secondary"], height=40, corner_radius=0)
        self.titlebar.pack(fill="x", side="top")
        self.titlebar.pack_propagate(False)
        self.titlebar.bind("<ButtonPress-1>", self.startMove)
        self.titlebar.bind("<B1-Motion>", self.doMove)

        leftFrame = ctk.CTkFrame(self.titlebar, fg_color="transparent")
        leftFrame.pack(side="left", padx=10, fill="y")
        leftFrame.bind("<ButtonPress-1>", self.startMove)
        leftFrame.bind("<B1-Motion>", self.doMove)

        titleLabel = ctk.CTkLabel(leftFrame, text="🖌️ Paint Normal Map", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_primary"])
        titleLabel.pack(side="left", padx=5)
        titleLabel.bind("<ButtonPress-1>", self.startMove)
        titleLabel.bind("<B1-Motion>", self.doMove)

        closeBtn = ctk.CTkButton(self.titlebar, text="✕", width=45, height=40, fg_color="transparent", hover_color=COLORS["accent_danger"], command=self.destroy, corner_radius=0)
        closeBtn.pack(side="right")

        self.fullImg = baseImg.copy()
        w, h = self.fullImg.size
        scale = 800 / w if w > 800 else 1
        self.newW, self.newH = int(w * scale), int(h * scale)
        self.scaleFactor = 1 / scale
        
        self.visualImg = self.fullImg.resize((self.newW, self.newH)).convert("RGBA")
        self.visualDraw = ImageDraw.Draw(self.visualImg)
        self.fullDraw = ImageDraw.Draw(self.fullImg)

        self.history = []

        ctrl = ctk.CTkFrame(self.container, fg_color="transparent")
        ctrl.pack(fill="x", padx=10, pady=10)

        self.btnFlat = ctk.CTkButton(
            ctrl, 
            text=" Flatten Area", 
            image=self.master.loadIcon("paintbrush.png", size=16),
            fg_color="#8080ff", 
            text_color="black", 
            hover_color="#6b6bfa", 
            border_width=2, 
            border_color=COLORS["accent_primary"]
        )
        self.btnFlat.pack(side="left", padx=5)
        
        ctk.CTkButton(
            ctrl, 
            text=" Undo", 
            image=self.master.loadIcon("undo.png", size=16),
            width=80, 
            fg_color=COLORS["bg_card"], 
            command=self.undo
        ).pack(side="left", padx=5)

        self.btnSendComp = ctk.CTkButton(
            ctrl, 
            text=" Send to Compiler", 
            image=self.master.loadIcon("package-plus.png", size=18),
            fg_color=COLORS["accent_primary"], 
            command=lambda: self.apply(sendToCompiler=True)
        )
        self.btnSendComp.pack(side="right", padx=5)

        self.btnSendPreview = ctk.CTkButton(
            ctrl, 
            text=" Send to Viewport", 
            image=self.master.loadIcon("view.png", size=18),
            fg_color=COLORS["accent_primary"], 
            command=lambda: self.apply(sendToPreview=True)
        )
        self.btnSendPreview.pack(side="right", padx=5)

        self.btnSave = ctk.CTkButton(
            ctrl, 
            text=" Save Changes", 
            image=self.master.loadIcon("square-check-big.png", size=18),
            fg_color="#10b981", 
            command=lambda: self.apply(sendToCompiler=False)
        )
        self.btnSave.pack(side="right", padx=5)

        self.canvas = ctk.CTkCanvas(self.container, width=self.newW, height=self.newH, cursor="crosshair", highlightthickness=0, bg=COLORS["bg_primary"])
        self.canvas.pack(pady=(0, 10), padx=10)

        self.tkImg = ImageTk.PhotoImage(self.visualImg)
        self.canvasImgId = self.canvas.create_image(0, 0, anchor="nw", image=self.tkImg)

        self.canvas.bind("<ButtonPress-1>", self.startPaint)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-Z>", lambda e: self.undo()) 
        self.canvas.bind("<Control-z>", lambda e: self.undo())
        self.canvas.bind("<Control-Z>", lambda e: self.undo())

    def setSize(self, val): 
        self.brushSize = int(val)

    def startPaint(self, event):
        self.canvas.focus_set() 
        if len(self.history) > 20: 
            self.history.pop(0)
        self.history.append((self.visualImg.copy(), self.fullImg.copy()))
        
        self.canvas.delete("brush_stroke")
        self.tkImg = ImageTk.PhotoImage(self.visualImg)
        self.canvas.itemconfig(self.canvasImgId, image=self.tkImg)
        self.paint(event)

    def paint(self, event):
        x, y = event.x, event.y
        r = self.brushSize
        
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=self.drawColor, outline=self.drawColor, tags="brush_stroke")
        self.visualDraw.ellipse([x-r, y-r, x+r, y+r], fill=self.drawColor)
        
        fx, fy = x * self.scaleFactor, y * self.scaleFactor
        fr = r * self.scaleFactor
        self.fullDraw.ellipse([fx-fr, fy-fr, fx+fr, fy+fr], fill=self.drawColor)
        
    def undo(self):
        if not self.history: return
        prevVisual, prevFull = self.history.pop()
        
        self.visualImg = prevVisual
        self.fullImg = prevFull
        self.visualDraw = ImageDraw.Draw(self.visualImg)
        self.fullDraw = ImageDraw.Draw(self.fullImg)
        
        self.canvas.delete("brush_stroke")
        self.tkImg = ImageTk.PhotoImage(self.visualImg)
        self.canvas.itemconfig(self.canvasImgId, image=self.tkImg)

    def apply(self, sendToCompiler=False, sendToPreview=False):
        self.callback(self.fullImg, sendToCompiler, sendToPreview)
        self.destroy()

class DropZone(ctk.CTkFrame):
    def __init__(self, master, labelText, fileTypes, dirKey, appRef, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.fileTypes = fileTypes
        self.dirKey = dirKey
        self.appRef = appRef
        self.command = command
        self.configure(fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=2, border_color=COLORS["border"])
        
        self.innerFrame = ctk.CTkFrame(self, fg_color="transparent")
        self.innerFrame.pack(expand=True, fill="both", padx=3, pady=20)
        
        self.placeholderIcon = self.appRef.loadIcon("image.png", size=36)
        self.iconLabel = ctk.CTkLabel(self.innerFrame, text="", image=self.placeholderIcon)
        self.iconLabel.pack(pady=(10, 5))
        
        self.textLabel = ctk.CTkLabel(self.innerFrame, text=labelText, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_secondary"])
        self.textLabel.pack(pady=(0, 0))
        
        self.regionLabel = ctk.CTkLabel(self.innerFrame, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["accent_primary"])
        self.regionLabel.pack(pady=(0, 5))
        
        entryRow = ctk.CTkFrame(self.innerFrame, fg_color="transparent")
        entryRow.pack(fill="x", padx=20, pady=(5, 10))

        self.pathEntry = ctk.CTkEntry(entryRow, placeholder_text="No file selected...", height=40, fg_color=COLORS["bg_primary"], border_color=COLORS["border"], justify="center")
        self.pathEntry.pack(fill="x", expand=True, side="left", padx=(0, 10))

        clearIcon = self.appRef.loadIcon("x.png", size=16)
        self.clearBtn = ctk.CTkButton(entryRow, text="", image=clearIcon, command=self.clear, width=40, height=40, fg_color=COLORS["bg_card"], hover_color=COLORS["accent_danger"])
        self.clearBtn.pack(side="right")
        
        for widget in [self, self.innerFrame, self.iconLabel, self.textLabel, self.regionLabel]:
            widget.bind("<Button-1>", self.onClick)
            
        try:
            if HAS_TKDND:
                self.drop_target_register(DND_FILES)
                self.dnd_bind('<<Drop>>', self.onDrop)
        except Exception:
            pass
            
    def clear(self, event=None):
        self.pathEntry.delete(0, "end")
        self.configure(border_color=COLORS["border"])
        self.updatePreview("")
        if self.command:
            self.command("")

    def updatePreview(self, path):
        if not path:
            self.iconLabel.configure(image=self.placeholderIcon, text="")
            return
        try:
            img = Image.open(path)
            w, h = img.size
            aspect = w / h
            targetH = 60
            targetW = int(targetH * aspect)
            if targetW > 180: targetW = 180
            
            ctkImg = ctk.CTkImage(light_image=img, dark_image=img, size=(targetW, targetH))
            self.iconLabel.configure(image=ctkImg, text="")
        except (AttributeError, ValueError, OSError):
            self.iconLabel.configure(image=self.placeholderIcon, text="❌")

    def onDrop(self, event):
        import re
        if '{' in event.data:
            files = re.findall(r'{([^}]+)}', event.data)
        else:
            files = event.data.split()
            
        if files:
            self.processPath(files[0])

    def onClick(self, event):
        if hasattr(event.widget, 'master') and event.widget.master == self.pathEntry.master:
            return

        initial = self.appRef.lastDirs.get(self.dirKey, "/")
        path = filedialog.askopenfilename(filetypes=self.fileTypes, initialdir=initial)
        if path:
            self.processPath(path)
            
    def processPath(self, path):

        if self.dirKey == "img":
            try:
                img = Image.open(path)
                w, h = img.size
                ratio = w / h
                region = self.appRef.regionVar.get()

                if region == "EU & UK" and ratio < 3.0:
                    messagebox.showerror("Ratio Error", f"It appears you may have inputted a US plate, please input an EU plate or switch the region.\nRegion: {region}")
                    return
                elif region == "US & MX" and ratio > 3.0:
                    messagebox.showerror("Ratio Error", f"It appears you may have inputted an EU plate, please input a US plate or switch the region.\nRegion: {region}")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Could not read image: {e}")
                return

        self.appRef.lastDirs[self.dirKey] = os.path.dirname(path)
        self.appRef.saveConfig(silent=True)
        self.pathEntry.delete(0, "end")
        self.pathEntry.insert(0, path)
        self.configure(border_color=COLORS["accent_success"])
        self.updatePreview(path)
        
        if self.command:
            self.command(path)

    def getPath(self):
        return self.pathEntry.get().strip('"')

class GradientFrame(ctk.CTkCanvas):
    def __init__(self, master, color1, color2, **kwargs):
        super().__init__(master, highlightthickness=0, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self.drawGradient)

    def drawGradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        
        limit = height
        for i in range(limit):
            nr = int(int(self.color1[1:3], 16) * (limit - i) / limit + int(self.color2[1:3], 16) * i / limit)
            ng = int(int(self.color1[3:5], 16) * (limit - i) / limit + int(self.color2[3:5], 16) * i / limit)
            nb = int(int(self.color1[5:7], 16) * (limit - i) / limit + int(self.color2[5:7], 16) * i / limit)
            color = f"#{nr:02x}{ng:02x}{nb:02x}"
            self.create_line(0, i, width, i, tags=("gradient",), fill=color)
        self.tag_lower("gradient")

class HorizontalGradientFrame(ctk.CTkCanvas):
    def __init__(self, master, color1, color2, **kwargs):
        super().__init__(master, highlightthickness=0, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self.drawGradient)

    def drawGradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1: return
        limit = width
        for i in range(limit):
            nr = int(int(self.color1[1:3], 16) * (limit - i) / limit + int(self.color2[1:3], 16) * i / limit)
            ng = int(int(self.color1[3:5], 16) * (limit - i) / limit + int(self.color2[3:5], 16) * i / limit)
            nb = int(int(self.color1[5:7], 16) * (limit - i) / limit + int(self.color2[5:7], 16) * i / limit)
            color = f"#{nr:02x}{ng:02x}{nb:02x}"
            self.create_line(i, 0, i, height, tags=("gradient",), fill=color)
        self.tag_lower("gradient")

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tw = None
        self.afterId = None
        self.widget.bind("<Enter>", self.enter, add="+")
        self.widget.bind("<Leave>", self.leave, add="+")

    def enter(self, event=None):
        if self.afterId:
            self.widget.after_cancel(self.afterId)
            self.afterId = None
        self.show()

    def show(self):
        if self.tw:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tw = ctk.CTkToplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        self.tw.attributes("-topmost", True)
        label = ctk.CTkLabel(self.tw, text=self.text, fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"], corner_radius=6)
        label.pack(ipadx=10, ipady=5)
        self.tw.bind("<Leave>", self.leave, add="+")
        label.bind("<Leave>", self.leave, add="+")

    def leave(self, event=None):
        if self.afterId:
            self.widget.after_cancel(self.afterId)
        self.afterId = self.widget.after(100, self.hide)

    def hide(self):
        if self.tw:
            self.tw.destroy()
            self.tw = None
        self.afterId = None

class PlateMakerApp(DraggableMixin, ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        if windll:
            try: windll.shcore.SetProcessDpiAwareness(1)
            except (AttributeError, OSError):
                pass

        super().__init__()
        if HAS_TKDND:
            try:
                self.TkdndVersion = TkinterDnD._require(self)
            except Exception:
                pass
        
        self.discordRPC = None
        self.discordConnected = False
        if HAS_DISCORD:
            threading.Thread(target=self.initDiscord, daemon=True).start()
        
        self.adobeIcons = {"ps": None, "ai": None}
        self.configFile = os.path.join(os.path.expanduser("~"), "varsinity_plate_maker.json")
        self.templateUrls = {
            "eu": "https://codehs.com/uploads/b344dbee8c88a9e6ea0afb7d2ef96557",
            "us": "https://codehs.com/uploads/ad7830d1aca402908e58d305be678ea8"
        }
        self.localTemplates = {
            "my_eu_template": "eu template.png",
            "my_template": "us template.png",
            "eu1": "EU1.png",
            "eu2": "EU2.png",
            "eu_fm2": "EU FM2.png",
            "uk": "UK.png",
            "us_fm1": "US FM1.png",
            "us2": "US2.png",
            "ushw": "USHW.png",
            "outline": "outline.png",
            "outline_eu": "outline eu.png",
            "japan": "JPN_Template.png"
        }

        self.title("Varsinity's Plate Compiler")
        self.geometry("900x750")
        self.configure(fg_color=COLORS["bg_primary"])
        self.overrideredirect(True)
        self.imageCache = {}

        self.uiQueue = queue.Queue()
        self.processUIQueue()
        
        self.update_idletasks()
        self.forceTaskbarPresence()
        
        self.after(10, self.applyRoundedCorners)

        self.iconUrl = "https://codehs.com/uploads/0da061a56c66f4e0b1a43b52f7341515" 
        self.logoUrl = "https://codehs.com/uploads/fd81d80c9192d13a66ec9620d278a1ce" 
        self.psIconUrl = "https://codehs.com/uploads/4bd09762b019512ffaea5eef10aa673a"
        self.aiIconUrl = "https://codehs.com/uploads/5cd274be304300c4f1db5fdade1dd41a"
        
        self.tempIconPath = os.path.join(tempfile.gettempdir(), "icon_cached.ico")
        
        if os.path.exists(self.tempIconPath):
            try: self.iconbitmap(self.tempIconPath)
            except (AttributeError, OSError):
                pass
            
        self.mmPreviewThumb = None
        self.mmPreviewJob = None

        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.gameVar = ctk.StringVar(value="FH5")
        self.setupTitlebar()
        self.setupSidebar()
        
        self.viewContainer = ctk.CTkFrame(self, fg_color=COLORS["bg_content"], corner_radius=15)
        self.viewContainer.grid(row=1, column=1, sticky="nsew", padx=25, pady=25)
        self.viewContainer.grid_columnconfigure(0, weight=1)
        self.viewContainer.grid_rowconfigure(0, weight=1)
        
        self.generatorPage = ctk.CTkScrollableFrame(self.viewContainer, fg_color=COLORS["bg_primary"])
        self.mapMakerPage = ctk.CTkScrollableFrame(self.viewContainer, fg_color=COLORS["bg_primary"])
        self.templatesPage = ctk.CTkScrollableFrame(self.viewContainer, fg_color=COLORS["bg_primary"])
        self.settingsPage = ctk.CTkScrollableFrame(self.viewContainer, fg_color=COLORS["bg_primary"])
        self.editorPage = ctk.CTkScrollableFrame(self.viewContainer, fg_color=COLORS["bg_primary"])
        self.viewportPage = ctk.CTkFrame(self.viewContainer, fg_color=COLORS["bg_primary"])

        self.history = []
        self.cart = {"eu": None, "us": None}
        self.totalCompiled = 0
        
        self.backupStates = {
            "Latest (Direct Zip)_Global": True,
            "Latest (Direct Zip)_Car-Specific (Car.zip)": True,
            "1.634.818.0_Global": True,
            "1.634.818.0_Car-Specific (Car.zip)": True
        }
        self.currentBackupVar = ctk.BooleanVar(value=True)
        self.silentModeVar = ctk.BooleanVar(value=False)
        self.autoResolvePathsVar = ctk.BooleanVar(value=True)

        self.lastDirs = {"img": "/", "nrml": "/", "out": "/", "mm_source": "/"} 
        self.mmBlurEnabledVar = ctk.BooleanVar(value=False)
        self.animationsVar = ctk.BooleanVar(value=False)
        
        self.setupGeneratorPage()
        self.setupTemplatesPage()
        self.setupMapMakerPage()
        self.setupSettingsPage()
        self.setupEditorPage()
        self.setupViewportPage()

        self.currentFrame = None
        self.loadConfig()
        self.updateRestoreButtonsVisibility()
        
        self.showPage("dashboard")
        
        self.after(100, self.loadAssetsSafe)

        self.toggleHelpText(self.versionVar.get())
        self.onGlobalGameToggle(self.gameVar.get())

        self.after(3000, self.checkForUpdates)
        self.attributes("-alpha", 0.0)
        self.animateOpen()

        if len(sys.argv) > 1:
            passedFile = sys.argv[1]
            if passedFile.lower().endswith(".plate"):
                self.after(800, lambda: self.importPlatePack(passedFile))

    def associateExtension(self):
        try:
            import winreg
            
            if getattr(sys, 'frozen', False):
                commandStr = f'"{sys.executable}" "%1"'
                iconStr = f'"{sys.executable}",0'
            else:
                pythonExe = sys.executable
                scriptPath = os.path.abspath(__file__)
                commandStr = f'"{pythonExe}" "{scriptPath}" "%1"'
                iconStr = f'"{pythonExe}",0'
                
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.plate")
            winreg.SetValue(key, "", winreg.REG_SZ, "Varsinity.PlatePack")
            winreg.CloseKey(key)

            key2 = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\Varsinity.PlatePack\shell\open\command")
            winreg.SetValue(key2, "", winreg.REG_SZ, commandStr)
            winreg.CloseKey(key2)

            key3 = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\Varsinity.PlatePack\DefaultIcon")
            winreg.SetValue(key3, "", winreg.REG_SZ, iconStr)
            winreg.CloseKey(key3)

            messagebox.showinfo("Success", ".plate files will now automatically open in this app!")
        except Exception as e:
            messagebox.showerror("Registry Error", f"Could not associate file type:\n{e}")

    def initDiscord(self):
        try:
            import asyncio
            try:
                asyncio.get_event_loop()
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())
                
            self.discordRPC = Presence("1368735235805544498") 
            self.discordRPC.connect()
            self.discordConnected = True
            self.discordStartTime = int(time.time())
            self.updateDiscordRPC(state="In Dashboard", details="Browsing")
        except Exception as e:
            self.discordConnected = False

    def updateDiscordRPC(self, state=None, details=None):
        if not self.discordConnected or not self.discordRPC:
            return
        try:
            self.discordRPC.update(state=state, details=details, start=self.discordStartTime, large_image="logo", large_text="Varsinity Plate Compiler")
        except Exception:
            pass

    def animateClose(self, alpha=1.0):
        if alpha > 0:
            alpha -= 0.1 
            self.attributes("-alpha", alpha)
            self.after(10, lambda: self.animateClose(alpha))
        else:
            self.destroy()
            os._exit(0)

    def animateOpen(self, alpha=0.0):
        if alpha < 1.0:
            alpha += 0.1
            self.attributes("-alpha", alpha)
            self.after(10, lambda: self.animateOpen(alpha))

    def animateMinimize(self, alpha=1.0):
        if alpha > 0:
            alpha -= 0.1
            self.attributes("-alpha", alpha)
            self.after(10, lambda: self.animateMinimize(alpha))
        else:
            if windll:
                hwnd = windll.user32.GetParent(self.winfo_id())
                windll.user32.ShowWindow(hwnd, 6)
            else:
                self.overrideredirect(False)
                self.iconify()
                
            self.bind("<FocusIn>", self.onRestore)

    def onRestore(self, event):
        self.unbind("<FocusIn>")
        
        if not windll:
            self.overrideredirect(True)
            
        self.animateOpen(0.0)

    def applyRoundedCorners(self):
        if windll:
            try:
                HWND = windll.user32.GetParent(self.winfo_id())
                windll.dwmapi.DwmSetWindowAttribute(HWND, 33, byref(c_int(2)), sizeof(c_int(2)))
            except (AttributeError, OSError):
                pass

    def loadAssetsSafe(self):
        try:
            response = requests.get(self.iconUrl, timeout=3)
            if response.status_code == 200:
                imgData = response.content
                iconImg = Image.open(BytesIO(imgData))
                iconImg.save(self.tempIconPath, format='ICO', sizes=[(32, 32), (64, 64), (128, 128)])
                try: self.iconbitmap(self.tempIconPath)
                except (AttributeError, OSError):
                    pass
                logoSmall = ctk.CTkImage(light_image=iconImg, dark_image=iconImg, size=(20, 20))
                if hasattr(self, 'titleIconLabel'):
                    self.titleIconLabel.configure(image=logoSmall, text="")
        except (requests.RequestException, OSError, ValueError):
            pass
            
        try:
            response = requests.get(self.logoUrl, timeout=3)
            if response.status_code == 200:
                imgData = response.content
                logoImg = Image.open(BytesIO(imgData))
                targetWidth = 158
                origW, origH = logoImg.size
                ratio = origH / origW
                targetHeight = int(targetWidth * ratio)
                logoImage = ctk.CTkImage(light_image=logoImg, dark_image=logoImg, size=(targetWidth, targetHeight))
                if hasattr(self, 'logoLabel'):
                    self.logoLabel.configure(image=logoImage, text="")
        except (requests.RequestException, OSError, ValueError):
            pass

        urls = {"ps": self.psIconUrl, "ai": self.aiIconUrl}
        for key, url in urls.items():
            try:
                res = requests.get(url, timeout=3)
                if res.status_code == 200:
                    img = Image.open(BytesIO(res.content))
                    self.adobeIcons[key] = ctk.CTkImage(light_image=img, dark_image=img, size=(24, 24))
                    for tType in list(self.templateUrls.keys()) + list(self.localTemplates.keys()):
                        btn = getattr(self, f"{tType}{key.capitalize()}Btn", None)
                        if btn and btn.winfo_exists():
                            btn.configure(image=self.adobeIcons[key], text="")
                    btnPreview = getattr(self, f"{key}BtnPreview", None)
                    if btnPreview and btnPreview.winfo_exists():
                        btnPreview.configure(image=self.adobeIcons[key], text="")
            except (requests.RequestException, OSError, ValueError):
                pass

        for tType, url in self.templateUrls.items():
            try:
                res = requests.get(url, timeout=3)
                if res.status_code == 200:
                    img = Image.open(BytesIO(res.content))
                    origW, origH = img.size
                    targetW = 250 if "eu" in tType else 200 
                    aspectRatio = origH / origW
                    targetH = int(targetW * aspectRatio)
                    previewImg = ctk.CTkImage(light_image=img, dark_image=img, size=(targetW, targetH))
        
                    label = getattr(self, f"{tType}PreviewLabel", None)
                    if label and label.winfo_exists():
                        label.configure(image=previewImg, text="")
            except (requests.RequestException, OSError, ValueError):
                pass
            
        for tType, filename in self.localTemplates.items():
            try:
                path = resourcePath(filename)
                if os.path.exists(path):
                    img = Image.open(path)
                    origW, origH = img.size
                    targetW = 250 if "eu" in tType or "uk" in tType else 200
                    targetH = int(targetW * (origH / origW))
                    previewImg = ctk.CTkImage(light_image=img, dark_image=img, size=(targetW, targetH))
                    
                    label = getattr(self, f"{tType}PreviewLabel", None)
                    if label and label.winfo_exists():
                        label.configure(image=previewImg, text="")
            except (OSError, ValueError):
                pass

    def forceTaskbarPresence(self):
        try:
            if not windll: return
            myappid = 'platecompiler.tool'
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            hwnd = windll.user32.GetParent(self.winfo_id())
            style = windll.user32.GetWindowLongW(hwnd, -20)
            style = style & ~0x00000080 
            style = style | 0x00040000  
            windll.user32.SetWindowLongW(hwnd, -20, style)
            if os.path.exists(self.tempIconPath):
                self.iconbitmap(self.tempIconPath)
            self.withdraw()
            self.deiconify()
            self.focus_force()
        except (AttributeError, OSError):
            pass

    def setupTitlebar(self):
        self.titlebar = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=40, corner_radius=0)
        self.titlebar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.titlebar.grid_propagate(False)
        self.titlebar.bind("<ButtonPress-1>", self.startMove)
        self.titlebar.bind("<B1-Motion>", self.doMove)

        leftFrame = ctk.CTkFrame(self.titlebar, fg_color="transparent")
        leftFrame.pack(side="left", padx=10, fill="y")
        leftFrame.bind("<ButtonPress-1>", self.startMove)
        leftFrame.bind("<B1-Motion>", self.doMove)

        self.titleIconLabel = ctk.CTkLabel(leftFrame, text="🚗", font=ctk.CTkFont(size=16))
        self.titleIconLabel.pack(side="left", padx=(5, 5))
        
        self.titleIconLabel.bind("<ButtonPress-1>", self.startMove)
        self.titleIconLabel.bind("<B1-Motion>", self.doMove)

        titleLabel = ctk.CTkLabel(leftFrame, text="Varsinity's Plate Compiler", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_primary"])
        titleLabel.pack(side="left", padx=5)
        
        titleLabel.bind("<ButtonPress-1>", self.startMove)
        titleLabel.bind("<B1-Motion>", self.doMove)

        centerFrame = ctk.CTkFrame(self.titlebar, fg_color="transparent")
        centerFrame.pack(side="left", expand=True, fill="both", padx=10)
        centerFrame.bind("<ButtonPress-1>", self.startMove)
        centerFrame.bind("<B1-Motion>", self.doMove)

        self.globalGameSelector = ctk.CTkSegmentedButton(
            centerFrame, values=["FH5", "FH6"], variable=self.gameVar,
            fg_color=COLORS["bg_secondary"], selected_color=COLORS["accent_primary"],
            text_color=COLORS["text_primary"], font=ctk.CTkFont(size=12, weight="bold"), height=26,
            command=self.onGlobalGameToggle
        )
        self.globalGameSelector.pack(side="top", pady=(7, 0))

        closeBtn = ctk.CTkButton(
            self.titlebar, 
            text="✕", 
            width=45, 
            height=40, 
            fg_color="transparent", 
            hover_color=COLORS["accent_danger"], 
            command=self.animateClose, 
            corner_radius=0
        )
        closeBtn.pack(side="right")

        minBtn = ctk.CTkButton(self.titlebar, text="—", width=45, height=40, fg_color="transparent", hover_color=COLORS["bg_card"], command=self.animateMinimize, corner_radius=0)
        minBtn.pack(side="right")

    def minimizeWindow(self):
        try:
            from ctypes import windll
            hwnd = windll.user32.GetParent(self.winfo_id())
            windll.user32.ShowWindow(hwnd, 6)
        except Exception:
            self.iconify()

    def loadIcon(self, filename, size=20):
        if not hasattr(self, "appIcons"):
            self.appIcons = {}
            
        if filename in self.appIcons:
            return self.appIcons[filename]
            
        path = resourcePath(filename)
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA")
                
                r, g, b, a = img.split()
                img = Image.new("RGBA", img.size, "white")
                img.putalpha(a)
                

                ctkIcon = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
                self.appIcons[filename] = ctkIcon
                return ctkIcon
            except Exception as e:
                print(f"Failed to load icon {filename}: {e}")
                
        return None

    def setupEntryDrop(self, widget, stringVar):
        try:
            if HAS_TKDND:
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind('<<Drop>>', lambda e, var=stringVar: self.onEntryDrop(e, var))
        except Exception:
            pass

    def onEntryDrop(self, event, stringVar):
        import re
        if '{' in event.data:
            files = re.findall(r'{([^}]+)}', event.data)
        else:
            files = event.data.split()
            
        if files:
            path = files[0].strip('"')
            stringVar.set(os.path.normpath(path))
            self.saveConfig(silent=True)

    def setupSidebar(self):
        self.navFrame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["bg_secondary"], width=200)
        self.navFrame.grid(row=1, column=0, sticky="nsew")

        self.sidebarGradient = GradientFrame(self.navFrame, color1="#0f0f12", color2="#18181b")
        self.sidebarGradient.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.tabIndicator = ctk.CTkFrame(self.navFrame, width=4, height=40, corner_radius=2, fg_color=COLORS["accent_primary"])
        self.tabGradient = HorizontalGradientFrame(self.navFrame, color1=COLORS["accent_primary"], color2=COLORS["bg_primary"])
        
        self.logoContainer = ctk.CTkFrame(self.navFrame, fg_color="transparent", height=80)
        self.logoContainer.pack_propagate(False)
        self.logoContainer.pack(fill="x", pady=(20, 10))

        self.logoLabel = ctk.CTkLabel(self.logoContainer, text="PLATE MAKER", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["accent_primary"])
        self.logoLabel.pack(pady=25, padx=20)

        tabStyle = {
            "anchor": "w", 
            "height": 48, 
            "fg_color": COLORS["bg_primary"], 
            "hover_color": COLORS["border"],
            "corner_radius": 8,
            "font": ctk.CTkFont(size=13, weight="bold"),
            "border_width": 1,                      
            "border_color": COLORS["bg_primary"]    
        }

        self.btnDashboard = ctk.CTkButton(self.navFrame, text=" Dashboard", image=self.loadIcon("layout-dashboard.png"), command=lambda: self.showPage("dashboard"), **tabStyle)
        self.btnDashboard.pack(fill="x", padx=15, pady=3)

        self.btnGenerator = ctk.CTkButton(self.navFrame, text=" Compiler", image=self.loadIcon("package-plus.png"), command=lambda: self.showPage("compiler"), **tabStyle)
        self.btnGenerator.pack(fill="x", padx=15, pady=3)
        
        self.btnTemplates = ctk.CTkButton(self.navFrame, text=" Plate Templates", image=self.loadIcon("book-dashed.png"), command=lambda: self.showPage("templates"), **tabStyle)
        self.btnTemplates.pack(fill="x", padx=15, pady=3)

        self.btnPresets = ctk.CTkButton(self.navFrame, text=" Presets", image=self.loadIcon("star.png"), command=lambda: self.showPage("presets"), **tabStyle)
        self.btnPresets.pack(fill="x", padx=15, pady=3)

        self.btnEditor = ctk.CTkButton(self.navFrame, text=" Plate Designer", image=self.loadIcon("square-pen.png"), command=lambda: self.showPage("editor"), **tabStyle)
        self.btnEditor.pack(fill="x", padx=15, pady=3)

        self.btnMapMaker = ctk.CTkButton(self.navFrame, text=" 3D Map Maker", image=self.loadIcon("map.png"), command=lambda: self.showPage("map_maker"), **tabStyle)
        self.btnMapMaker.pack(fill="x", padx=15, pady=3)

        self.btn3DPreview = ctk.CTkButton(self.navFrame, text=" 3D Viewport", image=self.loadIcon("view.png"), command=lambda: self.showPage("3d_preview"), **tabStyle)
        self.btn3DPreview.pack(fill="x", padx=15, pady=3)

        self.btnHistory = ctk.CTkButton(self.navFrame, text=" History", image=self.loadIcon("history.png"), command=lambda: self.showPage("history"), **tabStyle)
        self.btnHistory.pack(fill="x", padx=15, pady=3)

        self.btnSettings = ctk.CTkButton(self.navFrame, text=" Settings", image=self.loadIcon("settings.png"), command=lambda: self.showPage("settings"), **tabStyle)
        self.btnSettings.pack(fill="x", padx=15, pady=3)

        self.footer = ctk.CTkFrame(self.navFrame, fg_color="#18181b")
        self.footer.pack(side="bottom", fill="x", pady=20, padx=20)

        verContainer = ctk.CTkFrame(self.footer, fg_color="transparent")
        verContainer.pack(fill="x")

        self.statusDot = ctk.CTkLabel(verContainer, text="●", text_color=COLORS["accent_success"], font=ctk.CTkFont(size=14), fg_color="transparent")
        self.statusDot.pack(side="left")
        
        self.isOnline = True
        self.animateStatusDot()

        self.statusText = ctk.CTkLabel(verContainer, text=" ONLINE", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_secondary"], fg_color="transparent")
        self.statusText.pack(side="left", padx=2)

        self.verLabel = ctk.CTkLabel(verContainer, text=f"v{APP_VERSION}", font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"], fg_color="transparent")
        self.verLabel.pack(side="right")

        self.btnUpdate = ctk.CTkButton(
            self.footer, 
            text=" Check for Updates", 
            image=self.loadIcon("rss.png", size=14),
            font=ctk.CTkFont(size=10, weight="bold"),
            height=26,
            corner_radius=6,
            fg_color=COLORS["bg_primary"], 
            hover_color=COLORS["border"],
            border_width=1,                      
            border_color=COLORS["text_muted"],   
            command=lambda: self.checkForUpdates(manual=True)
        )
        self.btnUpdate.pack(fill="x", pady=(8, 0))

    def showPage(self, pageName):
        if getattr(self, "isAnimating", False):
            return

        pageOrder = ["dashboard", "compiler", "templates", "presets", "editor", "map_maker", "3d_preview", "history", "settings"]
        
        if not hasattr(self, "currentPageName"):
            self.currentPageName = "compiler"
            
        currentIdx = pageOrder.index(self.currentPageName)
        targetIdx = pageOrder.index(pageName)
        
        direction = 1 if targetIdx >= currentIdx else -1 

        targetFrame = None
        targetBtn = None

        if pageName == "dashboard":
            targetFrame = self.dashboardPage
            targetBtn = self.btnDashboard
            self.after(250, self.refreshDashboard)
        elif pageName == "compiler":
            targetFrame = self.generatorPage
            targetBtn = self.btnGenerator
        elif pageName == "map_maker":
            targetFrame = self.mapMakerPage
            targetBtn = self.btnMapMaker
        elif pageName == "3d_preview":
            targetFrame = self.viewportPage
            targetBtn = self.btn3DPreview
        elif pageName == "templates":
            targetFrame = self.templatesPage
            targetBtn = self.btnTemplates
        elif pageName == "history":
            targetFrame = self.historyPage
            targetBtn = self.btnHistory
            self.after(250, self.refreshHistory) 
        elif pageName == "presets":
            targetFrame = self.presetsPage
            targetBtn = self.btnPresets
        elif pageName == "editor":
            targetFrame = self.editorPage
            targetBtn = self.btnEditor
        elif pageName == "settings":
            targetFrame = self.settingsPage
            targetBtn = self.btnSettings

        if getattr(self, "currentFrame", None) == targetFrame:
            return

        allTabs = [self.btnDashboard, self.btnGenerator, self.btnTemplates, self.btnEditor, self.btnMapMaker, self.btn3DPreview, self.btnHistory, self.btnPresets, self.btnSettings]
        for btn in allTabs:
            btn.configure(border_color=COLORS["bg_primary"])
            
        if targetBtn:
            targetBtn.configure(border_color=COLORS["text_muted"])

        self.isAnimating = True
        self.animateIndicator(targetBtn)
        self.animateTransition(getattr(self, "currentFrame", None), targetFrame, direction)

        self.currentPageName = pageName
        self.currentFrame = targetFrame
        
        pageTitles = {
            "dashboard": "Dashboard",
            "compiler": "Compiler",
            "templates": "Plate Templates",
            "presets": "Presets",
            "editor": "Plate Designer",
            "map_maker": "3D Map Maker",
            "3d_preview": "3D Viewport",
            "history": "History",
            "settings": "Settings"
        }
        self.updateDiscordRPC(state=f"In {pageTitles.get(pageName, 'App')}", details="Browsing")

    def animateIndicator(self, targetWidget, startTime=None, startY=None, targetY=None):
        duration = 0.25 
        
        if startTime is None:
            if hasattr(self, 'IndicatorJob') and self.IndicatorJob:
                self.after_cancel(self.IndicatorJob)
                self.IndicatorJob = None
                
            self.navFrame.update_idletasks() 

            if targetWidget.winfo_y() <= 10:
                self.IndicatorJob = self.after(20, lambda: self.animateIndicator(targetWidget))
                return
                
            targetY = targetWidget.winfo_y() + 4
            
            if not self.tabIndicator.winfo_ismapped():
                self.tabIndicator.place(x=8, y=targetY) 
                return
                
            startY = float(self.tabIndicator.place_info()['y'])
            startTime = time.time()
            
        elapsed = time.time() - startTime
        progress = min(elapsed / duration, 1.0)
        ease = 1 - (1 - progress) ** 3 
        
        currentY = startY + (targetY - startY) * ease
        self.tabIndicator.place(x=8, y=currentY) 
        
        if progress < 1.0:
            self.IndicatorJob = self.after(5, lambda: self.animateIndicator(targetWidget, startTime, startY, targetY))
        else:
            self.IndicatorJob = None

    def animateTransition(self, oldFrame, newFrame, direction=1, startTime=None):
        if not getattr(self, "animationsVar", ctk.BooleanVar(value=True)).get():
            newFrame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
            newFrame.lift()
            self.update_idletasks()
            
            if oldFrame:
                oldFrame.place_forget()
                
            self.isAnimating = False
            return

        duration = 0.25
        
        if startTime is None:
            newFrame.place(relx=0.0, rely=1.0 * direction, relwidth=1.0, relheight=1.0)
            startTime = time.time()
            
        elapsed = time.time() - startTime
        progress = min(elapsed / duration, 1.0)
        ease = 1 - (1 - progress) ** 3 
        
        if oldFrame:
            oldFrame.place(rely=-ease * direction)
            
        newFrame.place(rely=(1.0 - ease) * direction)
        
        if progress < 1.0:
            self.after(5, lambda: self.animateTransition(oldFrame, newFrame, direction, startTime))
        else:
            if oldFrame:
                oldFrame.place_forget()
            newFrame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
            self.isAnimating = False

    
    def onGlobalGameToggle(self, game):
        if game == "FH6":
            if hasattr(self, "regionFrame"): self.regionFrame.pack_forget()
            if hasattr(self, "versionFrame"): self.versionFrame.pack_forget()
            if hasattr(self, "modeRow"): self.modeRow.pack_forget()
            
            if hasattr(self, "glossySwitch"): self.glossySwitch.pack_forget()
            if hasattr(self, "deleteBracketToggle"): self.deleteBracketToggle.pack(side="left", padx=(0, 15), before=self.compilerBackupSwitch)
            if hasattr(self, "deleteScrewToggle"): self.deleteScrewToggle.pack(side="left", padx=(0, 15), before=self.compilerBackupSwitch)
            
            if hasattr(self, "historyGlossySwitch"): self.historyGlossySwitch.pack_forget()
            if hasattr(self, "historyDeleteBracketToggle"): self.historyDeleteBracketToggle.pack(side="left", padx=(0, 15), before=self.historyBackupSwitch)
            if hasattr(self, "historyDeleteScrewToggle"): self.historyDeleteScrewToggle.pack(side="left", padx=(0, 15), before=self.historyBackupSwitch)
            
            if hasattr(self, "presetGlossySwitch"): self.presetGlossySwitch.pack_forget()
            if hasattr(self, "presetDeleteBracketToggle"): self.presetDeleteBracketToggle.pack(side="left", padx=(0, 15), before=self.presetBackupSwitch)
            if hasattr(self, "presetDeleteScrewToggle"): self.presetDeleteScrewToggle.pack(side="left", padx=(0, 15), before=self.presetBackupSwitch)
            
            self.regionVar.set("us")
            self.outputModeVar.set("Car-Specific (Car.zip)")
            if hasattr(self, "subHelpTextLabel"):
                self.subHelpTextLabel.place_forget()
                self.subHelpTextLabel.pack_forget()
            self.toggleOutputMode("Car-Specific (Car.zip)")
            self.toggleHelpText("FH6")
        else:
            if hasattr(self, "deleteBracketToggle"): self.deleteBracketToggle.pack_forget()
            if hasattr(self, "deleteScrewToggle"): self.deleteScrewToggle.pack_forget()
            if hasattr(self, "glossySwitch") and not self.glossySwitch.winfo_manager():
                self.glossySwitch.pack(side="left", padx=(0, 15), before=self.compilerBackupSwitch)
                
            if hasattr(self, "historyDeleteBracketToggle"): self.historyDeleteBracketToggle.pack_forget()
            if hasattr(self, "historyDeleteScrewToggle"): self.historyDeleteScrewToggle.pack_forget()
            if hasattr(self, "historyGlossySwitch") and not self.historyGlossySwitch.winfo_manager():
                self.historyGlossySwitch.pack(side="left", padx=(0, 15), before=self.historyBackupSwitch)

            if hasattr(self, "presetDeleteBracketToggle"): self.presetDeleteBracketToggle.pack_forget()
            if hasattr(self, "presetDeleteScrewToggle"): self.presetDeleteScrewToggle.pack_forget()
            if hasattr(self, "presetGlossySwitch") and not self.presetGlossySwitch.winfo_manager():
                self.presetGlossySwitch.pack(side="left", padx=(0, 15), before=self.presetBackupSwitch)
                
            if self.regionVar.get() == "us":
                self.regionVar.set("EU & UK")
            if hasattr(self, "versionFrame") and not self.versionFrame.winfo_manager():
                self.versionFrame.pack(fill="x", pady=(0, 15), before=self.dropContainer if hasattr(self, "dropContainer") else None)
            if hasattr(self, "regionFrame") and not self.regionFrame.winfo_manager():
                self.regionFrame.pack(fill="x", pady=(0, 15), before=self.versionFrame if hasattr(self, "versionFrame") else None)
            if hasattr(self, "modeRow") and not self.modeRow.winfo_manager():
                self.modeRow.pack(fill="x", padx=20, pady=(0, 10), after=self.outputHeaderRow if hasattr(self, "outputHeaderRow") else None)
            self.toggleHelpText(self.versionVar.get())
            self.toggleOutputMode(self.outputModeVar.get())
            
        self.updateDropzoneRegions()
        self.saveConfig(silent=True)
        
        if hasattr(self, "btnOpenOutput"):
            if game == "FH6":
                self.btnOpenOutput.configure(text=" Open Mods Folder", command=self.openFH6ModsFolder)
                if hasattr(self, "activePlatesFrame") and self.activePlatesFrame.winfo_manager():
                    self.activePlatesFrame.pack_forget()
                if hasattr(self, "activePlatesLabel") and self.activePlatesLabel.winfo_manager():
                    self.activePlatesLabel.pack_forget()
            else:
                self.btnOpenOutput.configure(text=" Open Output Folder", command=self.openOutputFolder)
                if hasattr(self, "activePlatesFrame") and not self.activePlatesFrame.winfo_manager():
                    _before = self.changelogFrame if hasattr(self, "changelogFrame") else None
                    _cl = self.changelogLabel if hasattr(self, "changelogLabel") else _before
                    if hasattr(self, "activePlatesLabel"): 
                        self.activePlatesLabel.pack(anchor="w", pady=(10, 10), before=_cl)
                    self.activePlatesFrame.pack(fill="x", before=_cl)
                    
        if hasattr(self, "refreshTemplatesPage"):
            self.refreshTemplatesPage()
            
        if hasattr(self, "presetVersionLabel"):
            if game == "FH6":
                if hasattr(self, "presetVersionLabel"): self.presetVersionLabel.pack_forget()
                if hasattr(self, "presetVersionBorder"): self.presetVersionBorder.pack_forget()
            else:
                if hasattr(self, "presetVersionLabel") and not self.presetVersionLabel.winfo_manager():
                    _before = None
                    if hasattr(self, "presetModeContainer") and self.presetModeContainer.winfo_manager():
                        _before = self.presetModeContainer
                    elif hasattr(self, "presetOutputContainer") and self.presetOutputContainer.winfo_manager():
                        try:
                            if str(self.presetOutputContainer.pack_info().get('in')) == str(self.presetTopRow):
                                _before = self.presetOutputContainer
                        except: pass
                    self.presetVersionLabel.pack(side="left", padx=(0, 10), before=_before)
                if hasattr(self, "presetVersionBorder") and not self.presetVersionBorder.winfo_manager():
                    _before = None
                    if hasattr(self, "presetModeContainer") and self.presetModeContainer.winfo_manager():
                        _before = self.presetModeContainer
                    elif hasattr(self, "presetOutputContainer") and self.presetOutputContainer.winfo_manager():
                        try:
                            if str(self.presetOutputContainer.pack_info().get('in')) == str(self.presetTopRow):
                                _before = self.presetOutputContainer
                        except: pass
                    self.presetVersionBorder.pack(side="left", padx=(0, 20), before=_before)
                    
        if hasattr(self, "refreshPresets"):
            self.refreshPresets(force=True)

        if hasattr(self, "stateDropdown"):
            fh5_templates = [k for k in PLATE_TEMPLATES.keys() if k != "Japan"]
            if game == "FH6":
                self.stateDropdown.configure(values=["Japan"])
                if self.stateVar.get() != "Japan":
                    self.stateVar.set("Japan")
                    if hasattr(self, "onStateChange"): self.onStateChange("Japan")
            else:
                self.stateDropdown.configure(values=fh5_templates)
                if self.stateVar.get() not in fh5_templates:
                    self.stateVar.set("Utah (Black)")
                    if hasattr(self, "onStateChange"): self.onStateChange("Utah (Black)")
        
        if hasattr(self, "historyVersionLabel"):
            if game == "FH6":
                if hasattr(self, "historyVersionLabel"): self.historyVersionLabel.pack_forget()
                if hasattr(self, "historyVersionBorder"): self.historyVersionBorder.pack_forget()
            else:
                if hasattr(self, "historyVersionLabel") and not self.historyVersionLabel.winfo_manager():
                    _before = None
                    if hasattr(self, "historyModeContainer") and self.historyModeContainer.winfo_manager():
                        _before = self.historyModeContainer
                    elif hasattr(self, "historyOutputContainer") and self.historyOutputContainer.winfo_manager():
                        try:
                            if str(self.historyOutputContainer.pack_info().get('in')) == str(self.historyTopRow):
                                _before = self.historyOutputContainer
                        except: pass
                    self.historyVersionLabel.pack(side="left", padx=(0, 10), before=_before)
                if hasattr(self, "historyVersionBorder") and not self.historyVersionBorder.winfo_manager():
                    _before = None
                    if hasattr(self, "historyModeContainer") and self.historyModeContainer.winfo_manager():
                        _before = self.historyModeContainer
                    elif hasattr(self, "historyOutputContainer") and self.historyOutputContainer.winfo_manager():
                        try:
                            if str(self.historyOutputContainer.pack_info().get('in')) == str(self.historyTopRow):
                                _before = self.historyOutputContainer
                        except: pass
                    self.historyVersionBorder.pack(side="left", padx=(0, 20), before=_before)

    def openFH6ModsFolder(self):
        try:
            fh6Out = os.path.join(self.fh6GameDirVar.get(), "MediaPC", "Cars")
            os.makedirs(fh6Out, exist_ok=True)
            os.startfile(fh6Out)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open mods folder:\n{e}")

    def setupGeneratorPage(self):
        header = ctk.CTkLabel(self.generatorPage, text="License Plate Compiler", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"), text_color=COLORS["text_primary"])
        header.pack(anchor="w", pady=(0, 15))

        regionFrame = ctk.CTkFrame(self.generatorPage, fg_color="transparent")
        self.regionFrame = regionFrame
        regionFrame.pack(fill="x", pady=(0, 15))

        versionFrame = ctk.CTkFrame(self.generatorPage, fg_color="transparent")
        self.versionFrame = versionFrame
        versionFrame.pack(fill="x", pady=(0, 15))
        
        versionLabel = ctk.CTkLabel(versionFrame, text="GAME VERSION:", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_muted"])
        versionLabel.pack(side="left", padx=(0, 15))

        self.versionVar = ctk.StringVar(value="Latest (Direct Zip)")
        self.versionSelector = ctk.CTkSegmentedButton(
            versionFrame, values=["Latest (Direct Zip)", "1.634.818.0"], 
            variable=self.versionVar, fg_color=COLORS["bg_secondary"], 
            selected_color=COLORS["accent_primary"], text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=12, weight="bold"), height=32,
            command=lambda v: (self.toggleHelpText(v), self.updateBackupToggleState(), self.saveConfig(silent=True))
        )

        self.versionSelector.pack(side="left")
        
        regionLabel = ctk.CTkLabel(regionFrame, text="TARGET REGION:", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_muted"])
        regionLabel.pack(side="left", padx=(0, 15))
        
        self.regionVar = ctk.StringVar(value="EU & UK")
        self.regionSelector = ctk.CTkSegmentedButton(
            regionFrame, values=["EU & UK", "US & MX"], variable=self.regionVar,
            fg_color=COLORS["bg_secondary"], selected_color=COLORS["accent_primary"],
            selected_hover_color=COLORS["accent_secondary"], text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=12, weight="bold"), height=32,
            command=self.updateDropzoneRegions
        )
        self.regionSelector.pack(side="left")

        importBtn = ctk.CTkButton(
            regionFrame, 
            text=" Import Plate Pack", 
            image=self.loadIcon("download.png", size=14),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["border"],
            height=32,
            command=self.importPlatePack
        )
        importBtn.pack(side="right", padx=(10, 0))

        dropContainer = ctk.CTkFrame(self.generatorPage, fg_color="transparent")
        self.dropContainer = dropContainer
        dropContainer.pack(fill="x", pady=(5, 15))
        dropContainer.grid_columnconfigure(0, weight=1); dropContainer.grid_columnconfigure(1, weight=1)
        
        self.imageDropZone = DropZone(dropContainer, "Drop Source Image", [("Images", "*.png *.jpg *.jpeg")], "img", self)
        self.imageDropZone.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        self.nrmlDropZone = DropZone(dropContainer, "Drop 3D Map (Optional)", [("Images", "*.png *.jpg *.jpeg")], "nrml", self)
        self.nrmlDropZone.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        self.updateDropzoneRegions(self.regionVar.get())

        self.outputFrame = ctk.CTkFrame(self.generatorPage, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.outputFrame.pack(fill="x", pady=(5, 15), ipadx=20, ipady=15)

        self.outputHeaderRow = ctk.CTkFrame(self.outputFrame, fg_color="transparent")
        self.outputHeaderRow.pack(fill="x", padx=20, pady=(5, 10))

        self.outputHeaderLabel = ctk.CTkLabel(self.outputHeaderRow, text="Step 4: Output Location", font=ctk.CTkFont(weight="bold"))
        self.outputHeaderLabel.pack(side="left")

        genSwitchesFrame = ctk.CTkFrame(self.outputHeaderRow, fg_color="transparent")
        genSwitchesFrame.pack(side="right")

        self.glossyVar = ctk.BooleanVar(value=False)
        self.glossySwitch = ctk.CTkSwitch(
            genSwitchesFrame, 
            text="Glossy Finish", 
            variable=self.glossyVar, 
            button_color=COLORS["accent_primary"],
            command=self.updateMaterialsZipVisibility
        )
        self.glossySwitch.pack(side="left", padx=(0, 15))

        self.deleteBracketVar = ctk.BooleanVar(value=False)
        self.deleteBracketToggle = ctk.CTkSwitch(
            genSwitchesFrame, 
            text="Delete Seal", variable=self.deleteBracketVar,
            button_color=COLORS["accent_primary"]
        )
        
        self.deleteScrewVar = ctk.BooleanVar(value=False)
        self.deleteScrewToggle = ctk.CTkSwitch(
            genSwitchesFrame, 
            text="Delete Plate Screw", variable=self.deleteScrewVar,
            button_color=COLORS["accent_primary"]
        )

        self.compilerBackupSwitch = ctk.CTkSwitch(
            genSwitchesFrame,
            text="Create Backups",
            variable=self.currentBackupVar,
            button_color=COLORS["accent_primary"],
            command=self.onBackupToggle
        )
        self.compilerBackupSwitch.pack(side="left")
        
        self.outputModeVar = ctk.StringVar(value="Global")
        self.modeRow = ctk.CTkFrame(self.outputFrame, fg_color="transparent")
        self.modeRow.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(self.modeRow, text="Output Mode:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 10))
        self.modeSelector = ctk.CTkSegmentedButton(
            self.modeRow, values=["Global", "Car-Specific (Car.zip)"], 
            variable=self.outputModeVar, fg_color=COLORS["bg_primary"], 
            selected_color=COLORS["accent_primary"], text_color=COLORS["text_primary"],
            command=self.toggleOutputMode
        )
        self.modeSelector.pack(side="left")
        
        self.genOutputDirVar = ctk.StringVar(value="Not Selected")
        self.materialsZipVar = ctk.StringVar(value="Not Selected")

        self.historyPage = ctk.CTkScrollableFrame(self.viewContainer, fg_color=COLORS["bg_primary"])
        self.setupHistoryPage()

        self.dashboardPage = ctk.CTkScrollableFrame(self.viewContainer, fg_color=COLORS["bg_primary"])
        self.setupDashboardPage()

        self.presetData = [
            {
                "name": "Quiet Plate 1", 
                "region": "US & MX", 
                "img": resourcePath("quiet plate 1 diff.png"),
                "nrml": resourcePath("quiet plate 1 nrml.png")
            },
            {
                "name": "Quiet Plate 2", 
                "region": "US & MX", 
                "img": resourcePath("quiet plate 2 diff.png"), 
                "nrml": resourcePath("quiet plate 2 nrml.png")
            },
            {
                "name": "Quiet Plate 3", 
                "region": "US & MX", 
                "img": resourcePath("quiet plate 3 diff.png"), 
                "nrml": resourcePath("quiet plate 3 nrml.png")
            },
            {
                "name": "Japanese Plate 1", 
                "region": "US & MX", 
                "img": resourcePath("japanese plate 1 diff.png"), 
                "nrml": resourcePath("japanese plate 1 nrml.png")
            },
            {
                "name": "Japanese Plate 2", 
                "region": "US & MX", 
                "img": resourcePath("japanese plate 2 diff.png"), 
                "nrml": resourcePath("japanese plate 2 nrml.png")
            },
            {
                "name": "Black Japanese Temp Plate", 
                "region": "US & MX", 
                "img": resourcePath("japanese temp plate 2 black diff.png"), 
                "nrml": resourcePath("japanese plate nrml.png")
            },
            {
                "name": "White Japanese Temp Plate", 
                "region": "US & MX", 
                "img": resourcePath("japanese temp plate 2 white diff.png"), 
                "nrml": resourcePath("japanese plate nrml.png")
            },
            {
                "name": "Texas Plate White", 
                "region": "US & MX", 
                "img": resourcePath("texas plate white.png"), 
                "nrml": resourcePath("texas white nrml.png")
            },
            {
                "name": "Texas Plate Black", 
                "region": "US & MX", 
                "img": resourcePath("texas plate black.png"), 
                "nrml": resourcePath("texas white nrml.png")
            },
            {
                "name": "French Plate", 
                "region": "EU & UK", 
                "img": resourcePath("france diff.png"), 
                "nrml": resourcePath("france nrml.png")
            },
            {
                "name": "Japanese Outline",
                "region": "FH6 (JPN)",
                "img": resourcePath("jpn_outline_diff.png"),
                "nrml": resourcePath("jpn_outline_nrml.png")
            },
            {
                "name": "Japanese Temporary",
                "region": "FH6 (JPN)",
                "img": resourcePath("jpn_temp_outline_diff.png"),
                "nrml": resourcePath("jpn_temp_outline_nrml.png")
            }
        ]

        self.presetCart = {"eu": None, "us": None}
        self.presetsPage = ctk.CTkScrollableFrame(self.viewContainer, fg_color=COLORS["bg_primary"])
        self.setupPresetsPage()
        
        
        self.outputLabel = ctk.CTkLabel(self.outputFrame, text="Textures.zip Path:", font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"])
        self.outputLabel.pack(anchor="w", padx=20)
        
        self.helpTextLabel = ctk.CTkLabel(
            self.outputFrame, 
            text=r"Select your original Textures.zip file in Forza Horizon 5\Content\media\cars\_library", 
            font=ctk.CTkFont(size=11), 
            text_color=COLORS["text_muted"],
            wraplength=500,
            justify="left"
        )
        self.helpTextLabel.pack(anchor="w", padx=20, pady=(0, 5))
        
        genDirRow = ctk.CTkFrame(self.outputFrame, fg_color="transparent")
        self.genDirRow = genDirRow
        genDirRow.pack(fill="x", padx=20, pady=(0, 5))
        
        self.genDirEntry = ctk.CTkEntry(genDirRow, textvariable=self.genOutputDirVar, fg_color=COLORS["bg_primary"], border_color=COLORS["border"])
        self.genDirEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.genDirEntry.bind("<Button-1>", lambda e: self.browseGenOutputDir())
        self.setupEntryDrop(self.genDirEntry, self.genOutputDirVar)
        
        self.genDirBtn = ctk.CTkButton(genDirRow, text="Browse .zip", width=80, fg_color=COLORS["bg_card"], command=lambda: self.browseGenOutputDir(isFolder=False))
        self.genDirBtn.pack(side="right")
        
        self.genDirFolderBtn = ctk.CTkButton(genDirRow, text="Browse Folder", width=100, fg_color=COLORS["bg_card"], command=lambda: self.browseGenOutputDir(isFolder=True))

        self.materialsLabel = ctk.CTkLabel(self.outputFrame, text="Materials.zip Path:", font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"])
        
        self.materialsHelp = ctk.CTkLabel(
            self.outputFrame, 
            text=r"Select your original Materials.zip file in Forza Horizon 5\Content\media\cars\_library", 
            font=ctk.CTkFont(size=11), 
            text_color=COLORS["text_muted"],
            wraplength=500,
            justify="left"
        )

        self.materialsInputRow = ctk.CTkFrame(self.outputFrame, fg_color="transparent")

        self.materialsZipEntry = ctk.CTkEntry(self.materialsInputRow, textvariable=self.materialsZipVar, fg_color=COLORS["bg_primary"], border_color=COLORS["border"])
        self.materialsZipEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.materialsZipEntry.bind("<Button-1>", lambda e: self.browseMaterialsZip())
        self.setupEntryDrop(self.materialsZipEntry, self.materialsZipVar)
        ctk.CTkButton(self.materialsInputRow, text="Browse", width=80, fg_color=COLORS["bg_card"], command=self.browseMaterialsZip).pack(side="right")

        self.subHelpTextLabel = ctk.CTkLabel(self.outputFrame, text="", font=ctk.CTkFont(size=11, slant="italic"), text_color=COLORS["text_muted"])

        self.btnActionRow = ctk.CTkFrame(self.generatorPage, fg_color="transparent")
        self.btnActionRow.pack(fill="x", padx=0, pady=20, expand=True)
        
        self.btnGenerate = ctk.CTkButton(
            self.btnActionRow, 
            text=" COMPILE TO GAME", 
            image=self.loadIcon("package-plus.png", size=24),
            fg_color=COLORS["accent_primary"], 
            height=60,
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=self.runGeneration
        )
        self.btnGenerate.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btnExport = ctk.CTkButton(
            self.btnActionRow, 
            text=" EXPORT ZIP...", 
            image=self.loadIcon("download.png", size=24),
            fg_color=COLORS["accent_secondary"], 
            height=60,
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=lambda: self.runExportAs(exportIsFolder=False)
        )
        self.btnExport.pack(side="left", fill="x", expand=True, padx=(5, 5))

        self.btnExportFolder = ctk.CTkButton(
            self.btnActionRow, 
            text=" EXPORT FOLDER...", 
            image=self.loadIcon("download.png", size=24),
            fg_color=COLORS["accent_secondary"], 
            height=60,
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=lambda: self.runExportAs(exportIsFolder=True)
        )
        self.btnExportFolder.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.btnRestore = ctk.CTkButton(
            self.generatorPage, 
            text=" RESTORE ORIGINALS", 
            image=self.loadIcon("undo.png", size=18),
            fg_color=COLORS["bg_card"], 
            hover_color=COLORS["accent_danger"], 
            height=40, 
            width=0,
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=self.runRestore
        )

        self.logArea = ctk.CTkTextbox(self.generatorPage, fg_color=COLORS["bg_secondary"], font=("Consolas", 12), height=150)
        self.logArea.pack(fill="both", expand=True)

    def updateBackupToggleState(self, *args):
        key = f"{self.versionVar.get()}_{self.outputModeVar.get()}"
        state = self.backupStates.get(key, True)
        self.currentBackupVar.set(state)
        self.updateRestoreButtonsVisibility()

    def onBackupToggle(self):
        key = f"{self.versionVar.get()}_{self.outputModeVar.get()}"
        self.backupStates[key] = self.currentBackupVar.get()
        self.saveConfig(silent=True)
        self.updateRestoreButtonsVisibility()

    def toggleOutputMode(self, value):
        if value == "Car-Specific (Car.zip)":
            isFH6 = getattr(self, "gameVar", None) and self.gameVar.get() == "FH6"
            label = "Input Car (.zip or Folder):" if isFH6 else "Car Path (.zip or Folder):"
            
            self.outputLabel.configure(text=label)
            if not self.outputLabel.winfo_manager(): self.outputLabel.pack(anchor="w", padx=20)
            if hasattr(self, "historyOutputLabel"): self.historyOutputLabel.configure(text=label)
            if hasattr(self, "presetOutputLabel"): self.presetOutputLabel.configure(text=label)
            
            help_msg = "Select the FH6 car of your choice." if isFH6 else "Select the .zip/folder of the car you want to apply this plate to."
            self.helpTextLabel.configure(text=help_msg)
            if not self.helpTextLabel.winfo_manager(): self.helpTextLabel.pack(anchor="w", padx=20, pady=(0, 5))
            
            if isFH6:
                self.subHelpTextLabel.configure(text="The patched car will automatically be exported into your game if the directory is set up in settings.", text_color=COLORS["text_muted"])
                self.subHelpTextLabel.pack_forget()
                self.subHelpTextLabel.place(x=20, rely=1.0, y=-5, anchor="sw")
            else:
                self.subHelpTextLabel.place_forget()
                self.subHelpTextLabel.pack_forget()
                
            self.genOutputDirVar.set("Not Selected")
            if hasattr(self, "genDirBtn"):
                self.genDirBtn.configure(text="Browse .zip")
            if hasattr(self, "genDirRow") and not self.genDirRow.winfo_manager():
                self.genDirRow.pack(fill="x", padx=20, pady=(0, 5))
            if hasattr(self, "genDirFolderBtn") and not self.genDirFolderBtn.winfo_manager():
                self.genDirFolderBtn.pack(side="right", padx=(10, 10))
            self.toggleHelpText(self.versionVar.get())
        else:
            if hasattr(self, "genDirFolderBtn") and self.genDirFolderBtn.winfo_manager():
                self.genDirFolderBtn.pack_forget()
            if hasattr(self, "genDirBtn"):
                self.genDirBtn.configure(text="Browse")
                
            isAutoResolve = getattr(self, "autoResolvePathsVar", ctk.BooleanVar(value=True)).get()
            if isAutoResolve:
                if hasattr(self, "outputLabel") and self.outputLabel.winfo_manager():
                    self.outputLabel.pack_forget()
                if hasattr(self, "helpTextLabel") and self.helpTextLabel.winfo_manager():
                    self.helpTextLabel.pack_forget()
                if hasattr(self, "genDirRow") and self.genDirRow.winfo_manager():
                    self.genDirRow.pack_forget()
                if hasattr(self, "historyOutputContainer") and self.historyOutputContainer.winfo_manager():
                    self.historyOutputContainer.pack_forget()
                if hasattr(self, "presetOutputContainer") and self.presetOutputContainer.winfo_manager():
                    self.presetOutputContainer.pack_forget()
            else:
                if hasattr(self, "outputLabel") and not self.outputLabel.winfo_manager():
                    self.outputLabel.pack(anchor="w", padx=20)
                if hasattr(self, "helpTextLabel") and not self.helpTextLabel.winfo_manager():
                    self.helpTextLabel.pack(anchor="w", padx=20, pady=(0, 5))
                if hasattr(self, "genDirRow") and not self.genDirRow.winfo_manager():
                    self.genDirRow.pack(fill="x", padx=20, pady=(0, 5))
                    
            self.toggleHelpText(self.versionVar.get())
        self.updateBackupToggleState()
        self.updateMaterialsZipVisibility()

    def onAutoResolveToggle(self):
        self.saveConfig(silent=True)
        if hasattr(self, "versionVar"):
            self.toggleHelpText(self.versionVar.get())
        if hasattr(self, "outputModeVar"):
            self.toggleOutputMode(self.outputModeVar.get())

    def browseGenOutputDir(self, isFolder=False):
        isCarSpecific = getattr(self, "outputModeVar", None) and self.outputModeVar.get() == "Car-Specific (Car.zip)"
        isFH6 = getattr(self, "gameVar", None) and self.gameVar.get() == "FH6"
        initial = self.lastDirs.get("out", "/")
        
        if isCarSpecific or isFH6:
            if isFolder:
                file = filedialog.askdirectory(initialdir=initial, title="Select Car Folder")
                if file:
                    self.lastDirs["out"] = file
                    self.genOutputDirVar.set(os.path.normpath(file))
                    self.saveConfig(silent=True)
            else:
                file = filedialog.askopenfilename(filetypes=[("Zip Archives", "*.zip")], initialdir=initial, title="Select Car.zip")
                if file: 
                    self.lastDirs["out"] = os.path.dirname(file)
                    self.genOutputDirVar.set(os.path.normpath(file))
                    self.saveConfig(silent=True)
            return
            
        if self.versionVar.get() == "Latest (Direct Zip)":
            file = filedialog.askopenfilename(filetypes=[("Zip Archives", "*.zip")], initialdir=initial)
            if file: 
                self.lastDirs["out"] = os.path.dirname(file)
                self.genOutputDirVar.set(os.path.normpath(file))
                self.saveConfig(silent=True)
        else:
            folder = filedialog.askdirectory(initialdir=initial)
            if folder: 
                self.lastDirs["out"] = folder
                self.genOutputDirVar.set(os.path.normpath(folder))
                self.saveConfig(silent=True)

    def importPlatePack(self, filePath=None):
        import zipfile
        
        if not filePath:
            initial = self.lastDirs.get("out", "/")
            filePath = filedialog.askopenfilename(
                initialdir=initial,
                title="Import Plate Pack",
                filetypes=[("Plate Pack", "*.plate"), ("Zip Archives", "*.zip")]
            )
            
        if not filePath: return

        self.lastDirs["out"] = os.path.dirname(filePath)
        self.saveConfig(silent=True)

        try:
            tempDir = os.path.join(tempfile.gettempdir(), "imported_plate_pack")
            if os.path.exists(tempDir):
                shutil.rmtree(tempDir)
            os.makedirs(tempDir, exist_ok=True)

            with zipfile.ZipFile(filePath, 'r') as zf:
                zf.extractall(tempDir)

            metaPath = os.path.join(tempDir, "meta.json")
            diffPath = os.path.join(tempDir, "diff.png")
            nrmlPath = os.path.join(tempDir, "nrml.png")

            if not os.path.exists(metaPath) or not os.path.exists(diffPath):
                messagebox.showerror("Error", "Invalid .plate file. Missing metadata or base image.")
                return

            with open(metaPath, 'r') as f:
                meta = json.load(f)

            region = meta.get("region", "US & MX")
            if region in ["EU & UK", "US & MX"]:
                self.regionVar.set(region)
                self.updateDropzoneRegions()

            self.glossyVar.set(meta.get("glossy", False))
            self.updateMaterialsZipVisibility()

            self.imageDropZone.pathEntry.delete(0, "end")
            self.imageDropZone.pathEntry.insert(0, diffPath)
            self.imageDropZone.updatePreview(diffPath)
            self.imageDropZone.configure(border_color=COLORS["accent_success"])

            self.nrmlDropZone.pathEntry.delete(0, "end")
            if os.path.exists(nrmlPath):
                self.nrmlDropZone.pathEntry.insert(0, nrmlPath)
                self.nrmlDropZone.updatePreview(nrmlPath)
                self.nrmlDropZone.configure(border_color=COLORS["accent_success"])
            else:
                self.nrmlDropZone.updatePreview("")
                self.nrmlDropZone.configure(border_color=COLORS["border"])

            self.showPage("compiler")
            
            self.after(400, lambda: messagebox.showinfo("Success", f"Plate Pack loaded successfully!\nRegion auto-set to: {region}"))

        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to read .plate file:\n{e}")

    def exportPlatePack(self, item):
        import zipfile
        initialDir = self.lastDirs.get("out", "/")
        savePath = filedialog.asksaveasfilename(
            initialdir=initialDir,
            title="Export Plate Pack",
            defaultextension=".plate",
            filetypes=[("Plate Pack", "*.plate")]
        )
        if not savePath: return

        self.lastDirs["out"] = os.path.dirname(savePath)
        self.saveConfig(silent=True)

        def process():
            try:
                with zipfile.ZipFile(savePath, 'w', zipfile.ZIP_DEFLATED) as zf:
                    meta = {
                        "region": item['region'],
                        "glossy": item.get('glossy', self.glossyVar.get())
                    }
                    zf.writestr("meta.json", json.dumps(meta))
                    
                    imgPath = item.get('img')
                    if imgPath and os.path.exists(imgPath):
                        zf.write(imgPath, "diff.png")
                        
                    nrmlPath = item.get('nrml')
                    if nrmlPath and os.path.exists(nrmlPath):
                        zf.write(nrmlPath, "nrml.png")
                        
                self.uiQueue.put(lambda: messagebox.showinfo("Success", f"Plate Pack exported to:\n{savePath}"))
            except Exception as e:
                self.uiQueue.put(lambda err=e: messagebox.showerror("Error", f"Failed to export plate pack:\n{err}"))
                
        threading.Thread(target=process, daemon=True).start()

    def loadExternalFile(self, filePath):
        if filePath.lower().endswith(".plate"):
            self.showPage("compiler")
            self.importPlatePack(filePath)
            
            self.deiconify()
            if windll:
                try:
                    hwnd = windll.user32.GetParent(self.winfo_id())
                    windll.user32.ShowWindow(hwnd, 9)
                    windll.user32.SetForegroundWindow(hwnd)
                except Exception:
                    pass
            self.lift()
            self.focus_force()

    def setupMapMakerPage(self):
        headerFrame = ctk.CTkFrame(self.mapMakerPage, fg_color="transparent")
        headerFrame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(headerFrame, text="3D Map Maker", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"), text_color=COLORS["text_primary"]).pack(side="left")
        
        rightHeaderFrame = ctk.CTkFrame(headerFrame, fg_color="transparent")
        rightHeaderFrame.pack(side="right")

        self.advancedModeVar = ctk.BooleanVar(value=False)
        
        self.advSwitch = ctk.CTkSwitch(
            rightHeaderFrame, 
            text="Advanced Mode", 
            variable=self.advancedModeVar, 
            command=self.toggleMmAdvanced, 
            button_color=COLORS["accent_primary"]
        )
        self.advSwitch.pack(side="top", anchor="e")
        
        self.advInfoLabel = ctk.CTkLabel(rightHeaderFrame, text="", font=ctk.CTkFont(size=10, slant="italic"), text_color=COLORS["text_muted"])
        self.advInfoLabel.pack(side="top", anchor="e")

        self.advSwitch.bind("<Enter>", lambda e: self.advInfoLabel.configure(text="Unlocks masks to control depth for different parts.   "))
        self.advSwitch.bind("<Leave>", lambda e: self.advInfoLabel.configure(text=""))

        guideFrame = ctk.CTkFrame(self.mapMakerPage, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        guideFrame.pack(fill="x", pady=(0, 20))

        guideText = (
            "Generate a 3D Normal Map to give your plate realistic depth in-game.\n\n"
            "1. Drop your plate image into the 'Source Image' box.\n"
            "2. Adjust Intensity and Smoothness until the preview looks right.\n"
            "3. Use 'Paint Map' to flatten areas (like stickers or bolt holes) that shouldn't extrude."
        )
        ctk.CTkLabel(guideFrame, text=guideText, font=ctk.CTkFont(size=13), text_color=COLORS["text_secondary"], justify="left", wraplength=580).pack(anchor="w", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            guideFrame, 
            text=" Tip: Toggle 'Advanced Mode' to unlock masking.", 
            image=self.loadIcon("lightbulb.png", size=16), 
            compound="left",
            font=ctk.CTkFont(size=13, weight="bold"), 
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=20, pady=(0, 15))

        self.mmDropContainer = ctk.CTkFrame(self.mapMakerPage, fg_color="transparent")
        self.mmDropContainer.pack(fill="x", pady=(0, 10))
        self.mmDropContainer.grid_columnconfigure(0, weight=1)
        self.mmDropContainer.grid_columnconfigure(1, weight=1)

        self.mmDropZone = DropZone(self.mmDropContainer, "Source Image", [("Images", "*.png *.jpg *.jpeg")], "mm_source", self, command=self.loadPreviewImage)
        self.mmDropZone.grid(row=0, column=0, sticky="nsew", padx=2, columnspan=2)

        self.mmMaskDropZone = DropZone(self.mmDropContainer, "B&W Mask", [("Images", "*.png *.jpg *.jpeg")], "nrml", self, command=self.schedulePreviewUpdate)

        self.previewFrame = ctk.CTkFrame(self.mapMakerPage, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"], height=160)
        self.previewFrame.pack(fill="x", pady=(0, 10))
        self.previewFrame.pack_propagate(False)

        self.previewAdobeBar = ctk.CTkFrame(self.previewFrame, fg_color="transparent")
        self.previewAdobeBar.place(relx=0.98, rely=0.05, anchor="ne")

        self.psBtnPreview = ctk.CTkButton(self.previewAdobeBar, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], image=self.adobeIcons.get("ps"), command=lambda: self.launchPreviewInAdobe("photoshop"))
        self.psBtnPreview.pack(side="right", padx=2)

        self.aiBtnPreview = ctk.CTkButton(self.previewAdobeBar, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], image=self.adobeIcons.get("ai"), command=lambda: self.launchPreviewInAdobe("illustrator"))
        self.aiBtnPreview.pack(side="right", padx=2)

        self.previewLabel = ctk.CTkLabel(self.previewFrame, text="Drop an image to see preview...", text_color=COLORS["text_muted"])
        self.previewLabel.pack(expand=True)

        self.settingsBox = ctk.CTkFrame(self.mapMakerPage, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.settingsBox.pack(fill="x", padx=3, pady=(0, 10))

        self.mmTabVar = ctk.StringVar(value="Black")
        self.mmTabToggle = ctk.CTkSegmentedButton(
            self.settingsBox, values=["Black", "White"],
            variable=self.mmTabVar, fg_color=COLORS["bg_primary"],
            selected_color=COLORS["accent_primary"], command=self.switchMmTabs
        )

        blurRow = ctk.CTkFrame(self.settingsBox, fg_color="transparent")
        blurRow.pack(fill="x", padx=20, pady=(15, 5))

        self.mmBlurSwitch = ctk.CTkSwitch(
            blurRow, 
            text="Apply Slight Blur to Map (Dynamic)", 
            variable=self.mmBlurEnabledVar, 
            command=self.schedulePreviewUpdate,
            button_color=COLORS["accent_primary"]
        )
        self.mmBlurSwitch.pack(side="left")

        self.blurInfoLabel = ctk.CTkLabel(
            blurRow, 
            text="", 
            font=ctk.CTkFont(size=10, slant="italic"), 
            text_color=COLORS["text_muted"]
        )
        self.blurInfoLabel.pack(side="left", padx=(10, 0))

        self.mmBlurSwitch.bind("<Enter>", lambda e: self.blurInfoLabel.configure(text="Helps remove the pixely look. Still in development, may not even work currently. "))
        self.mmBlurSwitch.bind("<Leave>", lambda e: self.blurInfoLabel.configure(text=""))

        self.sliderContainer = ctk.CTkFrame(self.settingsBox, fg_color="transparent")
        self.sliderContainer.pack(fill="x", padx=3, pady=(10, 5))

        self.baseSliderFrame = ctk.CTkFrame(self.sliderContainer, fg_color="transparent")
        self.baseSliderFrame.pack(fill="x")

        self.baseExtrude = ctk.StringVar(value="Inward")
        ctk.CTkLabel(self.baseSliderFrame, text="Extrusion Direction", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(0, 0))
        ctk.CTkSegmentedButton(self.baseSliderFrame, values=["Inward", "Outward"], variable=self.baseExtrude, fg_color=COLORS["bg_primary"], selected_color=COLORS["accent_primary"], command=self.schedulePreviewUpdate).pack(fill="x", padx=20, pady=(5, 10))
        
        ctk.CTkLabel(self.baseSliderFrame, text="Intensity (Depth)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.baseIntensity = ctk.CTkSlider(self.baseSliderFrame, from_=0.1, to=10.0, button_color=COLORS["accent_primary"], command=self.schedulePreviewUpdate)
        self.baseIntensity.set(2.0)
        self.baseIntensity.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(self.baseSliderFrame, text="Smoothness (Blur)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.baseBlur = ctk.CTkSlider(self.baseSliderFrame, from_=0.0, to=5.0, button_color=COLORS["accent_primary"], command=self.schedulePreviewUpdate)
        self.baseBlur.set(0.5)
        self.baseBlur.pack(fill="x", padx=20, pady=(0, 10))

        self.maskSliderFrame = ctk.CTkFrame(self.sliderContainer, fg_color="transparent")

        self.maskExtrude = ctk.StringVar(value="Outward")
        ctk.CTkLabel(self.maskSliderFrame, text="Extrusion Direction", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(0, 0))
        ctk.CTkSegmentedButton(self.maskSliderFrame, values=["Inward", "Outward"], variable=self.maskExtrude, fg_color=COLORS["bg_primary"], selected_color=COLORS["accent_primary"], command=self.schedulePreviewUpdate).pack(fill="x", padx=20, pady=(5, 10))
        
        ctk.CTkLabel(self.maskSliderFrame, text="Intensity (Depth)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.maskIntensity = ctk.CTkSlider(self.maskSliderFrame, from_=0.1, to=10.0, button_color=COLORS["accent_primary"], command=self.schedulePreviewUpdate)
        self.maskIntensity.set(5.0)
        self.maskIntensity.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(self.maskSliderFrame, text="Smoothness (Blur)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.maskBlur = ctk.CTkSlider(self.maskSliderFrame, from_=0.0, to=5.0, button_color=COLORS["accent_primary"], command=self.schedulePreviewUpdate)
        self.maskBlur.set(1.0)
        self.maskBlur.pack(fill="x", padx=20, pady=(0, 10))

        exportBtnFrame = ctk.CTkFrame(self.mapMakerPage, fg_color="transparent")
        exportBtnFrame.pack(fill="x", pady=(0, 5))

        self.btnGenerateMap = ctk.CTkButton(
            exportBtnFrame, 
            text=" EXPORT MAP", 
            image=self.loadIcon("download.png", size=20),
            fg_color=COLORS["accent_secondary"], 
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=self.runNormalMapGen
        )
        self.btnGenerateMap.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btnPaintMap = ctk.CTkButton(
            exportBtnFrame, 
            text=" PAINT MAP", 
            image=self.loadIcon("paintbrush.png", size=20),
            fg_color=COLORS["accent_secondary"],
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=self.openNormalPainter
        )
        self.btnPaintMap.pack(side="left", fill="x", expand=True, padx=(5, 0))

        sendFrame = ctk.CTkFrame(self.mapMakerPage, fg_color="transparent")
        sendFrame.pack(fill="x", padx=0, pady=(5, 15))

        self.btnSendToCompiler = ctk.CTkButton(
            sendFrame, 
            text=" SEND TO COMPILER", 
            image=self.loadIcon("package-plus.png", size=20), 
            fg_color=COLORS["accent_primary"], 
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=self.sendMapToCompiler
        )
        self.btnSendToCompiler.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btnSendToPreview = ctk.CTkButton(
            sendFrame, 
            text=" SEND TO VIEWPORT", 
            image=self.loadIcon("view.png", size=20), 
            fg_color=COLORS["accent_primary"], 
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=self.sendMapToPreview
        )
        self.btnSendToPreview.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.mapActionInfo = ctk.CTkLabel(self.mapMakerPage, text="", font=ctk.CTkFont(size=11, slant="italic"), text_color=COLORS["text_muted"])
        self.mapActionInfo.pack(pady=(2, 0))

        self.btnPaintMap.bind("<Enter>", lambda e: self.mapActionInfo.configure(text="Manually flatten areas of the map you don't want to be 3D.  "))
        self.btnPaintMap.bind("<Leave>", lambda e: self.mapActionInfo.configure(text=""))
        
        self.btnGenerateMap.bind("<Enter>", lambda e: self.mapActionInfo.configure(text="Save the finished 3D map to your computer.  "))
        self.btnGenerateMap.bind("<Leave>", lambda e: self.mapActionInfo.configure(text=""))

        self.btnSendToCompiler.bind("<Enter>", lambda e: self.mapActionInfo.configure(text="Sends source image and normal map to the compiler."))
        self.btnSendToCompiler.bind("<Leave>", lambda e: self.mapActionInfo.configure(text=""))

        self.btnSendToPreview.bind("<Enter>", lambda e: self.mapActionInfo.configure(text="Sends source image and normal map to the 3D Viewport."))
        self.btnSendToPreview.bind("<Leave>", lambda e: self.mapActionInfo.configure(text=""))

        self.mmStatusLabel = ctk.CTkLabel(self.mapMakerPage, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.mmStatusLabel.pack(pady=(5, 15))

    def loadPreviewImage(self, path):
        if not path:
            self.mmPreviewThumb = None
            if hasattr(self, 'previewLabel'):
                self.previewLabel.configure(image=None, text="Drop an image to see preview...")
            self.schedulePreviewUpdate()
            return
            
        try:
            img = Image.open(path)
            self.mmPreviewThumb = img.copy()
            self.mmPreviewThumb.thumbnail((400, 150))
            
            thumbCopy = self.mmPreviewThumb.copy()
            
            ctkImg = ctk.CTkImage(light_image=thumbCopy, dark_image=thumbCopy, size=thumbCopy.size)
            self.previewLabel.configure(image=ctkImg, text="")
            
            self.schedulePreviewUpdate()
        except (OSError, ValueError) as e:
            messagebox.showerror("Error", f"Failed to load preview: {e}")

    def schedulePreviewUpdate(self, _=None):
        self.lastMmMap = None 
        if self.mmPreviewJob: self.after_cancel(self.mmPreviewJob)
        self.mmPreviewJob = self.after(150, self.updatePreview)

    def updatePreview(self):
        if not self.mmPreviewThumb: return
        maskPath = self.mmMaskDropZone.getPath() if self.advancedModeVar.get() else None
        threading.Thread(target=self.generatePreviewThread, args=(
            self.baseIntensity.get(), self.baseBlur.get(), self.baseExtrude.get(),
            self.maskIntensity.get(), self.maskBlur.get(), self.maskExtrude.get(), maskPath
        ), daemon=True).start()

    def generatePreviewThread(self, bStr, bBlur, bDir, mStr, mBlur, mDir, maskPath):
        baseMap = self.createNormalMapData(self.mmPreviewThumb, bStr, bBlur, bDir)
        if maskPath and os.path.exists(maskPath):
            try:
                maskImg = Image.open(maskPath).convert('L').resize(baseMap.size)
                maskMap = self.createNormalMapData(self.mmPreviewThumb, mStr, mBlur, mDir)
                resImg = Image.composite(maskMap, baseMap, maskImg)
            except (OSError, ValueError):
                resImg = baseMap 
        else:
            resImg = baseMap
        
        resImg = self.applyOutputBlur(resImg, bStr, bBlur)
        ctkImg = ctk.CTkImage(light_image=resImg, dark_image=resImg, size=resImg.size)
        self.uiQueue.put(lambda: self.previewLabel.configure(image=ctkImg, text=""))

    def createNormalMapData(self, img, strength, blur, direction):
        width, height = img.size
        scaleFactor = width / 400.0
        adjStrength, adjBlur = strength * scaleFactor, blur * scaleFactor
        imgL = img.convert('L')
        if adjBlur > 0: imgL = imgL.filter(ImageFilter.GaussianBlur(adjBlur))
        pixels = imgL.load()
        normalImg = Image.new('RGB', (width, height))
        normalPixels = normalImg.load()
        dirMult = -1 if direction == "Inward" else 1
        for y in range(height):
            for x in range(width):
                l, r = (x-1 if x>0 else 0), (x+1 if x<width-1 else width-1)
                t, b = (y-1 if y>0 else 0), (y+1 if y<height-1 else height-1)
                dx, dy = (pixels[r, y]-pixels[l, y])*adjStrength*dirMult, (pixels[x, b]-pixels[x, t])*adjStrength*dirMult
                dz = 255.0; norm = math.sqrt(dx**2 + dy**2 + dz**2)
                normalPixels[x, y] = (int((dx/norm+1)*127.5), int((dy/norm+1)*127.5), int((dz/norm+1)*127.5))
        return normalImg

    def runNormalMapGen(self):
        imgPath = self.mmDropZone.getPath()

        if not imgPath or not os.path.isfile(imgPath):
            messagebox.showerror("Error", "Please select a valid source image first.")
            return

        maskPath = self.mmMaskDropZone.getPath() if self.advancedModeVar.get() else None

        initialDir = self.lastDirs.get("mm_out", "/")
        savePath = filedialog.asksaveasfilename(
            initialdir=initialDir,
            title="Save Normal Map",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile="plate_nrml.png"
        )
        if not savePath:
            return

        self.lastDirs["mm_out"] = os.path.dirname(savePath)
        self.saveConfig(silent=True)

        self.btnGenerateMap.configure(state="disabled")
        self.mmStatusLabel.configure(text="⏳ Exporting High-Res Map... Please wait", text_color=COLORS["accent_secondary"])

        threading.Thread(target=self.processNormalMap, args=(
            imgPath, maskPath, 
            self.baseIntensity.get(), self.baseBlur.get(), self.baseExtrude.get(),
            self.maskIntensity.get(), self.maskBlur.get(), self.maskExtrude.get(),
            savePath
        ), daemon=True).start()

    def processNormalMap(self, imgPath, maskPath, bStr, bBlur, bDir, mStr, mBlur, mDir, savePath):
        try:
            img = Image.open(imgPath)
            baseMap = self.createNormalMapData(img, bStr, bBlur, bDir)

            if maskPath and os.path.exists(maskPath):
                maskImg = Image.open(maskPath).convert('L').resize(baseMap.size)
                maskMap = self.createNormalMapData(img, mStr, mBlur, mDir)
                finalMap = Image.composite(maskMap, baseMap, maskImg)
            else:
                finalMap = baseMap

            finalMap = self.applyOutputBlur(finalMap, bStr, bBlur)
            finalMap.save(savePath)

            self.uiQueue.put(lambda: self.onExportComplete(True, savePath))
        except Exception as e:
            self.uiQueue.put(lambda err=e: self.onExportComplete(False, str(err)))

    def exportPaintedMap(self, sourcePath, destPath):
        try:
            shutil.copy2(sourcePath, destPath)
            self.after(0, lambda: self.onExportComplete(True, destPath))
        except Exception as e:
            self.after(0, lambda e=e: self.onExportComplete(False, str(e)))

    def getDynamicBlurRadius(self, intensity, smoothness, width):
        if not self.mmBlurEnabledVar.get():
            return 0
        resScale = width / 4000.0
        return (intensity / 10.0) * (smoothness / 2.5) * 7.0 * resScale

    def onExportComplete(self, success, message):
        self.btnGenerateMap.configure(state="normal")
        
        if success:
            self.mmStatusLabel.configure(text="✅ Export Complete!", text_color=COLORS["accent_success"])
            messagebox.showinfo("Success", f"Saved to:\n{message}")
        else:
            self.mmStatusLabel.configure(text="❌ Export Failed!", text_color=COLORS["accent_danger"])
            messagebox.showerror("Error", message)
            
        self.after(4000, lambda: self.mmStatusLabel.configure(text=""))

    def createTemplateCard(self, parent, row, col, name, tType):
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        pad_x = (0, 5) if col == 0 else (5, 0)
        pad_y = (15, 0) if row > 0 else (0, 0)
        card.grid(row=row, column=col, sticky="nsew", padx=pad_x, pady=pad_y)

        previewLabel = ctk.CTkLabel(card, text=f"Loading Preview...")
        previewLabel.pack(pady=(20, 10), padx=10, fill="both", expand=True)
        
        vpBtn = ctk.CTkButton(card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], image=self.loadIcon("view.png", size=18), command=lambda t=tType: self.viewTemplateInViewport(t))
        vpBtn.place(relx=0.04, rely=0.04, anchor="nw")

        psBtn = ctk.CTkButton(card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], image=self.adobeIcons.get("ps"), command=lambda t=tType: self.launchTemplate(t, "photoshop"))
        psBtn.place(relx=0.96, rely=0.04, anchor="ne")

        aiBtn = ctk.CTkButton(card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], image=self.adobeIcons.get("ai"), command=lambda t=tType: self.launchTemplate(t, "illustrator"))
        aiBtn.place(relx=0.84, rely=0.04, anchor="ne")

        ctk.CTkLabel(card, text=name, font=ctk.CTkFont(size=14, weight="bold")).pack()
        ctk.CTkButton(card, text="Download", fg_color=COLORS["accent_primary"], command=lambda t=tType: self.downloadTemplate(t)).pack(pady=20, padx=20, fill="x")

        setattr(self, f"{tType}PreviewLabel", previewLabel)
        setattr(self, f"{tType}PsBtn", psBtn)
        setattr(self, f"{tType}AiBtn", aiBtn)
        return card

    def setupTemplatesPage(self):
        header = ctk.CTkLabel(self.templatesPage, text="Plate Templates", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"))
        header.pack(anchor="w", pady=(0, 20))

        self.fh6TemplatesCardsFrame = ctk.CTkFrame(self.templatesPage, fg_color="transparent")
        self.fh6TemplatesCardsFrame.grid_columnconfigure(0, weight=1)
        self.fh6TemplatesCardsFrame.grid_columnconfigure(1, weight=1)
        
        self.createTemplateCard(self.fh6TemplatesCardsFrame, 0, 0, "Japan Template", "japan")

        self.templatesCardsFrame = ctk.CTkFrame(self.templatesPage, fg_color="transparent")
        self.templatesCardsFrame.pack(fill="x")
        self.templatesCardsFrame.grid_columnconfigure(0, weight=1)
        self.templatesCardsFrame.grid_columnconfigure(1, weight=1)

        templates = [
            ("My EU Template", "my_eu_template"),
            ("My US Template", "my_template"),
            ("EU FM1 Plate", "eu"),
            ("US FM1 Plate", "us_fm1"),
            ("EU FM2 Plate", "eu_fm2"),
            ("US2 Plate", "us2"),
            ("EU1 Plate", "eu1"),
            ("USHW Plate", "ushw"),
            ("EU2 Plate", "eu2"),
            ("US & MX Mask", "us"),
            ("UK Plate", "uk"),
            ("US White Outline", "outline"),
            ("EU White Outline", "outline_eu")
        ]

        row = 0
        col = 0
        for name, tType in templates:
            self.createTemplateCard(self.templatesCardsFrame, row, col, name, tType)
            col += 1
            if col > 1:
                col = 0
                row += 1

        self.refreshTemplatesPage()

    def refreshTemplatesPage(self):
        if getattr(self, "gameVar", None) and self.gameVar.get() == "FH6":
            if hasattr(self, "templatesCardsFrame"): self.templatesCardsFrame.pack_forget()
            if hasattr(self, "fh6TemplatesCardsFrame") and not self.fh6TemplatesCardsFrame.winfo_manager():
                self.fh6TemplatesCardsFrame.pack(fill="x")
        else:
            if hasattr(self, "fh6TemplatesCardsFrame"): self.fh6TemplatesCardsFrame.pack_forget()
            if hasattr(self, "templatesCardsFrame") and not self.templatesCardsFrame.winfo_manager(): 
                self.templatesCardsFrame.pack(fill="x")
                
        if hasattr(self.templatesPage, "_parent_canvas"):
            self.templatesPage._parent_canvas.yview_moveto(0)

    def setupSettingsPage(self):
        header = ctk.CTkLabel(self.settingsPage, text="Settings", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"))
        header.pack(anchor="w", pady=(0, 20))
        
        pathFrame = ctk.CTkFrame(self.settingsPage, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        pathFrame.pack(fill="x", pady=0, ipady=10)
        
        self.psPathVar = ctk.StringVar(value=r"C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe")
        self.createPathSetting(pathFrame, "Photoshop EXE Path:", self.psPathVar, mode="exe")
        
        self.aiPathVar = ctk.StringVar(value=r"C:\Program Files\Adobe\Adobe Illustrator 2026\Support Files\Contents\Windows\Illustrator.exe")
        self.createPathSetting(pathFrame, "Illustrator EXE Path:", self.aiPathVar, mode="exe")
        
        bundled7Z = resourcePath("7za.exe")
        default7Z = bundled7Z if os.path.exists(bundled7Z) else r"C:\Program Files\7-Zip\7z.exe"
        
        self.szPathVar = ctk.StringVar(value=default7Z)
        self.createPathSetting(pathFrame, "7-Zip EXE Path: (Now built in)", self.szPathVar, mode="exe")
        
        compFrame = ctk.CTkFrame(self.settingsPage, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        compFrame.pack(fill="x", pady=(10, 0), ipady=5)
        
        self.fh5GameDirVar = ctk.StringVar(value="Not Selected")
        self.createPathSetting(compFrame, "Forza Horizon 5 Game Directory:", self.fh5GameDirVar, mode="dir")

        self.fh6GameDirVar = ctk.StringVar(value="Not Selected")
        self.createPathSetting(compFrame, "Forza Horizon 6 Game Directory:", self.fh6GameDirVar, mode="dir")

        self.defaultOutLatestVar = ctk.StringVar(value=r"C:\XboxGames\Forza Horizon 5\Content\media\cars\_library\Textures.zip")
        self.defaultMatLatestVar = ctk.StringVar(value=r"C:\XboxGames\Forza Horizon 5\Content\media\cars\_library\Materials.zip")
        self.defaultOutVar = ctk.StringVar(value=r"C:\Games\Forza Horizon 5\media\Stripped\MediaOverride\RC0\Cars\_library")
        
        compRow = ctk.CTkFrame(compFrame, fg_color="transparent")
        compRow.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(compRow, text="Compression:").pack(side="left", padx=(0, 10))
        self.compLevelVar = ctk.StringVar(value="Normal (-mx5)")
        ctk.CTkOptionMenu(compRow, variable=self.compLevelVar, values=["Fast (-mx1)", "Normal (-mx5)", "Ultra (-mx9)"], fg_color=COLORS["bg_primary"]).pack(side="left")
        
        silentRow = ctk.CTkFrame(compFrame, fg_color="transparent")
        silentRow.pack(fill="x", padx=20, pady=(0, 10))
        self.silentModeVar = ctk.BooleanVar(value=False)
        self.silentSwitch = ctk.CTkSwitch(silentRow, text="Silent Mode", variable=self.silentModeVar, button_color=COLORS["accent_primary"])
        self.silentSwitch.pack(side="left")

        self.silentInfoLabel = ctk.CTkLabel(silentRow, text="", font=ctk.CTkFont(size=10, slant="italic"), text_color=COLORS["text_muted"])
        self.silentInfoLabel.pack(side="left", padx=(10, 0))
        self.silentSwitch.bind("<Enter>", lambda e: self.silentInfoLabel.configure(text="(Disables success popups) "))
        self.silentSwitch.bind("<Leave>", lambda e: self.silentInfoLabel.configure(text=""))

        self.animationsVar = ctk.BooleanVar(value=False)
        animRow = ctk.CTkFrame(compFrame, fg_color="transparent")
        animRow.pack(fill="x", padx=20, pady=(0, 10))
        self.animationsSwitch = ctk.CTkSwitch(
            animRow, text="Enable Buggy Page Transitions", 
            variable=self.animationsVar, button_color=COLORS["accent_primary"], 
            command=lambda: self.saveConfig(silent=True)
        )
        self.animationsSwitch.pack(side="left")
        
        assocRow = ctk.CTkFrame(compFrame, fg_color="transparent")
        assocRow.pack(fill="x", padx=20, pady=(10, 10))
        
        ctk.CTkLabel(assocRow, text="File Association:").pack(side="left", padx=(0, 10))
        
        self.btnAssociate = ctk.CTkButton(
            assocRow,
            text=" Make this app the default for .plate files",
            image=self.loadIcon("package-plus.png", size=16),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["border"],
            command=self.associateExtension
        )
        self.btnAssociate.pack(side="left")

        bottomRow = ctk.CTkFrame(self.settingsPage, fg_color="transparent")
        bottomRow.pack(fill="x", pady=20)
        
        ctk.CTkButton(bottomRow, text=" Clear Plate History", image=self.loadIcon("trash.png"), command=self.clearHistory, fg_color=COLORS["bg_card"], hover_color=COLORS["accent_danger"], height=40).pack(side="left")
        ctk.CTkButton(bottomRow, text=" Clear Zip Backups", image=self.loadIcon("brush-cleaning.png"), command=self.promptClearBackups, fg_color=COLORS["bg_card"], hover_color=COLORS["accent_danger"], height=40).pack(side="left", padx=(10, 0))
        ctk.CTkButton(bottomRow, text=" Save Settings", image=self.loadIcon("save.png"), command=self.saveConfig, fg_color=COLORS["accent_success"], height=40).pack(side="right")

    def createPathSetting(self, master, label, variable, mode="exe"):
        ctk.CTkLabel(master, text=label, text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20, pady=(10,0))
        row = ctk.CTkFrame(master, fg_color="transparent"); row.pack(fill="x", padx=20, pady=5)
        entry = ctk.CTkEntry(row, textvariable=variable, fg_color=COLORS["bg_primary"])
        entry.pack(side="left", fill="x", expand=True, padx=(0,10))
        self.setupEntryDrop(entry, variable)
        ctk.CTkButton(row, text="Browse", width=80, command=lambda: self.browsePath(variable, mode)).pack(side="right")

    def browsePath(self, var, mode):
        if mode == "dir":
            path = filedialog.askdirectory()
        elif mode == "zip":
            path = filedialog.askopenfilename(filetypes=[("Zip Archives", "*.zip")])
        else:
            path = filedialog.askopenfilename(filetypes=[("Executable", "*.exe")])
            
        if path: var.set(os.path.normpath(path))

    def clearHistory(self):
        if messagebox.askyesno("Confirm", "Clear all history and cart?"):
            self.history = []
            self.cart = {"eu": None, "us": None}
            self.refreshHistory()
            self.cartStatus.configure(text="Cart Empty")
            self.saveConfig(silent=True)

    def loadConfig(self):
        self.IsLoading = True
            
        if os.path.exists(self.configFile):
            try:
                with open(self.configFile, 'r') as f:
                    data = json.load(f)
                    self.totalCompiled = data.get("totalCompiled", len(getattr(self, "history", [])))
                    
                    if hasattr(self, 'psPathVar'): self.psPathVar.set(data.get("ps_path", r"C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe"))
                    if hasattr(self, 'aiPathVar'): self.aiPathVar.set(data.get("ai_path", r"C:\Program Files\Adobe\Adobe Illustrator 2026\Support Files\Contents\Windows\Illustrator.exe"))
                    if hasattr(self, 'szPathVar'): self.szPathVar.set(data.get("sz_path", r"C:\Program Files\7-Zip\7z.exe"))
                    
                    if hasattr(self, 'fh5GameDirVar'): self.fh5GameDirVar.set(data.get('fh5_game_dir', 'Not Selected'))
                    if hasattr(self, 'fh6GameDirVar'): self.fh6GameDirVar.set(data.get('fh6_game_dir', 'Not Selected'))
                    if hasattr(self, 'defaultOutLatestVar'): self.defaultOutLatestVar.set(data.get("default_out_latest", r"C:\XboxGames\Forza Horizon 5\Content\media\cars\_library\Textures.zip"))
                    if hasattr(self, 'defaultOutVar'): self.defaultOutVar.set(data.get("default_out", r"C:\Games\Forza Horizon 5\media\Stripped\MediaOverride\RC0\Cars\_library"))
                    if hasattr(self, 'defaultMatLatestVar'): self.defaultMatLatestVar.set(data.get("default_mat_latest", r"C:\XboxGames\Forza Horizon 5\Content\media\cars\_library\Materials.zip"))
                    
                    if hasattr(self, 'compLevelVar'): self.compLevelVar.set(data.get("comp_level", "Normal (-mx5)"))
                    if hasattr(self, 'silentModeVar'): self.silentModeVar.set(data.get("silent_mode", False))
                    if hasattr(self, 'autoResolvePathsVar'): self.autoResolvePathsVar.set(data.get("auto_resolve_paths", True))
                    
                    if hasattr(self, 'materialsZipVar'):
                        savedMat = data.get("materialsZip", "Not Selected")
                        if savedMat == "Not Selected" and hasattr(self, 'defaultMatLatestVar'):
                            defaultMat = self.defaultMatLatestVar.get()
                            if os.path.isfile(defaultMat):
                                savedMat = defaultMat
                        self.materialsZipVar.set(savedMat)
                    if hasattr(self, 'glossyVar'): self.glossyVar.set(data.get("glossy_finish", False))
                    
                    loadedBackups = data.get("backupStates")
                    if loadedBackups is None:
                        oldVal = data.get("create_backups", True)
                        self.backupStates = {
                            "Latest (Direct Zip)_Global": oldVal,
                            "Latest (Direct Zip)_Car-Specific (Car.zip)": oldVal,
                            "1.634.818.0_Global": oldVal,
                            "1.634.818.0_Car-Specific (Car.zip)": oldVal
                        }
                    else:
                        self.backupStates = loadedBackups
                    
                    self.history = data.get("history", [])
                    self.lastDirs = data.get("lastDirs", {"img": "/", "nrml": "/", "out": "/", "mm_source": "/"})
                    
                    if hasattr(self, 'versionVar'): 
                        ver = data.get("version", self.versionVar.get())
                        if ver == "FH6":
                            ver = "Latest (Direct Zip)"
                            if hasattr(self, 'gameVar'): self.gameVar.set("FH6")
                        self.versionVar.set(ver)
                        
                    if hasattr(self, 'gameVar') and data.get("game"):
                        self.gameVar.set(data.get("game"))

                    self.updateBackupToggleState()
                    
                    if hasattr(self, 'refreshHistory'):
                        self.refreshHistory()
                        
            except Exception as e: 
                messagebox.showerror("Save File Error", f"Your save file got corrupted and could not be loaded. It has been reset.\n\nError: {e}")
                self.lastDirs = {"img": "/", "nrml": "/", "out": "/", "mm_source": "/"}
        else: 
            self.lastDirs = {"img": "/", "nrml": "/", "out": "/", "mm_source": "/"}

        if hasattr(self, 'genOutputDirVar'):
            if self.versionVar.get() == "Latest (Direct Zip)":
                if hasattr(self, 'defaultOutLatestVar') and self.defaultOutLatestVar.get() != "Not Selected":
                    self.genOutputDirVar.set(self.defaultOutLatestVar.get())
            else:
                if hasattr(self, 'defaultOutVar') and self.defaultOutVar.get() != "Not Selected":
                    self.genOutputDirVar.set(self.defaultOutVar.get())
                    
        self.IsLoading = False

    def saveConfig(self, silent=False):
        if getattr(self, 'IsLoading', False):
            return
            
        try:
            with open(self.configFile, 'w') as f:
                json.dump({
                    "totalCompiled": getattr(self, "totalCompiled", 0),
                    "ps_path": getattr(self, "psPathVar", ctk.StringVar()).get(), 
                    "ai_path": getattr(self, "aiPathVar", ctk.StringVar()).get(),
                    "sz_path": getattr(self, "szPathVar", ctk.StringVar(value=r"C:\Program Files\7-Zip\7z.exe")).get(),
                    "fh5_game_dir": getattr(self, "fh5GameDirVar", ctk.StringVar(value="Not Selected")).get(),
                    "fh6_game_dir": getattr(self, "fh6GameDirVar", ctk.StringVar(value="Not Selected")).get(),
                    "default_out_latest": getattr(self, "defaultOutLatestVar", ctk.StringVar(value=r"C:\XboxGames\Forza Horizon 5\Content\media\cars\_library\Textures.zip")).get(),
                    "default_out": getattr(self, "defaultOutVar", ctk.StringVar(value=r"C:\Games\Forza Horizon 5\media\Stripped\MediaOverride\RC0\Cars\_library")).get(),
                    "default_mat_latest": getattr(self, "defaultMatLatestVar", ctk.StringVar(value=r"C:\XboxGames\Forza Horizon 5\Content\media\cars\_library\Materials.zip")).get(),
                    "comp_level": getattr(self, "compLevelVar", ctk.StringVar(value="Normal (-mx5)")).get(),
                    "silent_mode": getattr(self, "silentModeVar", ctk.BooleanVar(value=False)).get(),
                    "auto_resolve_paths": getattr(self, "autoResolvePathsVar", ctk.BooleanVar(value=True)).get(),
                    "backupStates": getattr(self, "backupStates", {}),
                    "animations": getattr(self, "animationsVar", ctk.BooleanVar(value=True)).get(),
                    "materialsZip": getattr(self, "materialsZipVar", ctk.StringVar(value="Not Selected")).get(),
                    "glossy_finish": getattr(self, "glossyVar", ctk.BooleanVar(value=False)).get(),
                    "history": getattr(self, "history", []),
                    "lastDirs": getattr(self, "lastDirs", {"img": "/", "nrml": "/", "out": "/", "mm_source": "/"}),
                    "version": getattr(self, "versionVar", ctk.StringVar(value="Latest (Direct Zip)")).get(),
                    "game": getattr(self, "gameVar", ctk.StringVar(value="FH5")).get()
                }, f)
            if not silent and not getattr(self, "silentModeVar", ctk.BooleanVar(value=False)).get(): 
                messagebox.showinfo("Success", "Settings saved!")
        except Exception as e: 
            if not silent: 
                messagebox.showerror("Error", f"Failed to save settings to {self.config_file}.\n\nError: {e}")

    def launchTemplate(self, tType, tool):
        def task():
            try:
                exe = self.psPathVar.get().strip('"') if tool == "photoshop" else self.aiPathVar.get().strip('"')
                
                if tType in self.localTemplates:
                    path = resourcePath(self.localTemplates[tType])
                    if not os.path.exists(path):
                        self.after(0, lambda: messagebox.showerror("Error", f"{self.localTemplates[tType]} not found in the app folder."))
                        return
                elif tType in self.templateUrls:
                    r = requests.get(self.templateUrls[tType])
                    path = os.path.join(tempfile.gettempdir(), f"{tType}_plate.png")
                    with open(path, "wb") as f: f.write(r.content)
                else:
                    return
                
                if os.path.isfile(exe):
                    subprocess.Popen([exe, path])
                else:
                    os.startfile(path)
            except Exception as e: self.after(0, lambda e=e: messagebox.showerror("Error", str(e)))
        threading.Thread(target=task, daemon=True).start()

    def downloadTemplate(self, tType):
        dirP = filedialog.askdirectory(); 
        if dirP: threading.Thread(target=self.executeDownload, args=(dirP, tType), daemon=True).start()

    def executeDownload(self, d, t):
        try:
            if t == "both":
                keys = ["eu", "us"]
            else:
                keys = [t]
            
            for key in keys:
                if key in self.localTemplates:
                    src = resourcePath(self.localTemplates[key])
                    if os.path.exists(src):
                        outName = f"{key.upper()}_Blank_Outline_Template.png" if "outline" in key else f"{key.upper()}_Plate_Template.png"
                        shutil.copyfile(src, os.path.join(d, outName))
                    else:
                        self.after(0, lambda k=key: messagebox.showerror("Error", f"{self.localTemplates[k]} not found."))
                        return
                elif key in self.templateUrls:
                    r = requests.get(self.templateUrls[key])
                    with open(os.path.join(d, f"{key.upper()}_Plate_Template.png"), "wb") as f: f.write(r.content)
            self.after(0, lambda: messagebox.showinfo("Success", "Done!"))
        except Exception as e: 
            self.after(0, lambda e=e: messagebox.showerror("Error", str(e)))

    def viewTemplateInViewport(self, tType):
        if getattr(self, "gameVar", None) and self.gameVar.get() == "FH6":
            if hasattr(self, "viewportRegionVar") and self.viewportRegionVar.get() != "FH6 (JPN)":
                self.viewportRegionVar.set("FH6 (JPN)")
                self.onViewportRegionChange("FH6 (JPN)")
                
        self.showPage("3d_preview")
        
        def doLoad(p):
            self.sendToPreview(p, isNormal=False)
            
        if tType in self.localTemplates:
            p = resourcePath(self.localTemplates[tType])
            if os.path.exists(p):
                self.after(300, lambda path=p: doLoad(path))
            else:
                self.after(300, lambda: messagebox.showerror("Error", f"{self.localTemplates[tType]} not found."))
        elif tType in self.templateUrls:
            def fetchAndLoad():
                try:
                    r = requests.get(self.templateUrls[tType])
                    tempPath = os.path.join(tempfile.gettempdir(), f"preview_template_{tType}.png")
                    with open(tempPath, "wb") as f:
                        f.write(r.content)
                    self.after(0, lambda: doLoad(tempPath))
                except Exception as e:
                    self.after(0, lambda e=e: messagebox.showerror("Error", str(e)))
            threading.Thread(target=fetchAndLoad, daemon=True).start()

    def log(self, msg): self.after(0, lambda: (self.logArea.insert("end", f"{msg}\n"), self.logArea.see("end")))

    def patchBinaryPath(self, filepath, oldPathStr, newPathStr):
        with open(filepath, 'rb') as f:
            data = bytearray(f.read())

        oldBytes = oldPathStr.encode('ascii')
        newBytes = newPathStr.encode('ascii')

        lowerData = data.lower()
        lowerOld = oldBytes.lower()

        if lowerOld not in lowerData:
            return False 

        start = 0
        replaced = False
        while True:
            idx = lowerData.find(lowerOld, start)
            if idx == -1:
                break
            
            replaced = True
            overwriteLen = max(len(oldBytes), len(newBytes))
            paddedNew = newBytes.ljust(overwriteLen, b'\x00')
            for i in range(overwriteLen):
                if idx + i < len(data):
                    data[idx + i] = paddedNew[i]
            start = idx + overwriteLen

        if replaced:
            with open(filepath, 'wb') as f:
                f.write(data)
            return True
        return False

    def patchBinaryRegex(self, filepath, pattern, replaceFunc):
        import re
        with open(filepath, 'rb') as f:
            data = bytearray(f.read())
            
        matches = list(re.finditer(pattern, data, flags=re.IGNORECASE))
        if not matches:
            return None
            
        finalAppliedStr = None
        for match in reversed(matches):
            oldBytes = match.group(0)
            oldStr = oldBytes.decode('ascii', errors='ignore').split('\x00')[0]
            
            newStr = replaceFunc(oldStr, len(oldBytes))
            
            if newStr:
                newBytes = newStr.encode('ascii', errors='ignore')
                
                if len(newBytes) > len(oldBytes):
                    extIdx = newStr.rfind('.')
                    extension = newStr[extIdx:] if extIdx != -1 else ""
                    basePart = newStr[:extIdx] if extIdx != -1 else newStr
                    
                    while len(newBytes) > len(oldBytes) and len(basePart) > 1:
                        basePart = basePart[:-1]
                        newBytes = (basePart + extension).encode('ascii', errors='ignore')
                    newStr = basePart + extension
                
                paddedNew = newBytes.ljust(len(oldBytes), b'\x00')
                start, end = match.span()
                data[start:end] = paddedNew
                finalAppliedStr = newStr
                
        if finalAppliedStr:
            with open(filepath, 'wb') as f:
                f.write(data)
            return finalAppliedStr
        return None

    def runExportAs(self, exportIsFolder=False):
        if getattr(self, "isCompiling", False):
            return

        isCarSpecific = getattr(self, "outputModeVar", None) and self.outputModeVar.get() == "Car-Specific (Car.zip)"
        isFH6 = getattr(self, "gameVar", None) and self.gameVar.get() == "FH6"

        initialDir = self.lastDirs.get("out", "/")

        if isCarSpecific or isFH6:
            if exportIsFolder:
                savePath = filedialog.askdirectory(
                    initialdir=initialDir,
                    title="Select Folder to Patch / Export To"
                )
                if not savePath:
                    return
                self.lastDirs["out"] = savePath
                exportTarget = savePath
            else:
                outputBase = self.genOutputDirVar.get()
                defaultName = os.path.basename(outputBase) if outputBase and outputBase != "Not Selected" else "Patched_Car.zip"
                if not defaultName.endswith(".zip"): defaultName += ".zip"
                
                savePath = filedialog.asksaveasfilename(
                    initialdir=initialDir,
                    title="Export Patched Car",
                    defaultextension=".zip",
                    filetypes=[("Zip Archives", "*.zip")],
                    initialfile=defaultName
                )
                if not savePath:
                    return
                self.lastDirs["out"] = os.path.dirname(savePath)
                exportTarget = savePath
        else:
            savePath = filedialog.askdirectory(
                initialdir=initialDir,
                title="Select Export Folder (Will create Textures.zip and Materials.zip)"
            )
            if not savePath:
                return
            self.lastDirs["out"] = savePath
            exportTarget = savePath
            exportIsFolder = False
            
        self.runGeneration(customExportPath=exportTarget, exportIsFolder=exportIsFolder)

    def runGeneration(self, customExportPath=None, exportIsFolder=False):
        if getattr(self, "isCompiling", False):
            return

        imgPath = self.imageDropZone.getPath()
        nrmlPath = self.nrmlDropZone.getPath()
        outputBase = self.genOutputDirVar.get()

        self.history.append({
            "region": self.regionVar.get(), 
            "img": self.imageDropZone.getPath(), 
            "nrml": self.nrmlDropZone.getPath(),
            "glossy": self.glossyVar.get()
        })

        self.saveConfig(silent=True)
        
        if not imgPath and not nrmlPath:
            messagebox.showerror("Error", "Please select at least one file to generate.")
            return
            
        isCarSpecific = getattr(self, "outputModeVar", None) and self.outputModeVar.get() == "Car-Specific (Car.zip)"
        isFH6 = getattr(self, "gameVar", None) and self.gameVar.get() == "FH6"

        if isFH6:
            if outputBase == "Not Selected" or (not (os.path.isfile(outputBase) and outputBase.lower().endswith('.zip')) and not os.path.isdir(outputBase)):
                messagebox.showerror("Error", "Please select a valid FH6 Car .zip file or folder.")
                return
            if not customExportPath:
                if not hasattr(self, 'fh6GameDirVar') or self.fh6GameDirVar.get() == "Not Selected" or not os.path.isdir(self.fh6GameDirVar.get()):
                    messagebox.showerror("Error", "Please configure your FH6 Game Directory in Settings.")
                    return
        elif isCarSpecific:
            if outputBase == "Not Selected" or (not (os.path.isfile(outputBase) and outputBase.lower().endswith('.zip')) and not os.path.isdir(outputBase)):
                messagebox.showerror("Error", "Please select a valid Car.zip file or folder.")
                return
        else:
            isAutoResolve = getattr(self, "autoResolvePathsVar", ctk.BooleanVar(value=True)).get()
            if isAutoResolve:
                if not hasattr(self, 'fh5GameDirVar') or self.fh5GameDirVar.get() == "Not Selected" or not os.path.isdir(self.fh5GameDirVar.get()):
                    messagebox.showerror("Error", "Please configure your FH5 Game Directory in Settings.")
                    return
                    
                fh5GameDir = self.fh5GameDirVar.get()
                if self.versionVar.get() == "Latest (Direct Zip)":
                    outputBase = os.path.join(fh5GameDir, "Content", "media", "cars", "_library", "Textures.zip")
                else:
                    outputBase = os.path.join(fh5GameDir, "media", "Stripped", "MediaOverride", "RC0", "Cars", "_library")
            else:
                if outputBase == "Not Selected":
                    messagebox.showerror("Error", "Please select an output Textures.zip location.")
                    return
                    
            if not customExportPath:
                if self.versionVar.get() == "1.634.818.0" and not os.path.exists(outputBase) and isAutoResolve:
                    os.makedirs(outputBase, exist_ok=True)
                elif self.versionVar.get() == "Latest (Direct Zip)" and not os.path.isfile(outputBase):
                    messagebox.showerror("Error", f"Textures.zip not found at: {outputBase}")
                    return
            else:
                if self.versionVar.get() == "Latest (Direct Zip)" and not os.path.isfile(outputBase):
                    messagebox.showerror("Error", f"Base Textures.zip not found at: {outputBase} (Needed for extraction)")
                    return

        self.log("Starting plate generation...")
        self.isCompiling = True
        self.spinnerFrame = 0
        self.animateButton()
        threading.Thread(target=self.processFiles, args=(imgPath, nrmlPath, outputBase, False, customExportPath, exportIsFolder), daemon=True).start()

    def processFiles(self, imgPath, nrmlPath, outDir, silent=False, customExportPath=None, exportIsFolder=False):
        try:
            if imgPath and os.path.isfile(imgPath) and nrmlPath and os.path.isfile(nrmlPath):
                imgSize = Image.open(imgPath).size
                nrmlSize = Image.open(nrmlPath).size
                if imgSize != nrmlSize:
                    targetW = max(imgSize[0], nrmlSize[0])
                    targetH = max(imgSize[1], nrmlSize[1])
                    self.log(f"Normalizing resolutions to {targetW}x{targetH}...")
                    if imgSize != (targetW, targetH):
                        resized = Image.open(imgPath).resize((targetW, targetH), Image.LANCZOS)
                        imgPath = os.path.normpath(os.path.join(tempfile.gettempdir(), "resized_diff.png"))
                        resized.save(imgPath)
                    if nrmlSize != (targetW, targetH):
                        resized = Image.open(nrmlPath).resize((targetW, targetH), Image.LANCZOS)
                        nrmlPath = os.path.normpath(os.path.join(tempfile.gettempdir(), "resized_nrml.png"))
                        resized.save(nrmlPath)

            outputBase = outDir
            isCarSpecific = getattr(self, "outputModeVar", None) and self.outputModeVar.get() == "Car-Specific (Car.zip)"
            isLatest = self.versionVar.get() == "Latest (Direct Zip)"
            szPath = self.szPathVar.get().strip('"')
            compFlag = "-mx1" if "mx1" in self.compLevelVar.get() else "-mx9" if "mx9" in self.compLevelVar.get() else "-mx5"
            isSilent = silent or self.silentModeVar.get()

            if not os.path.exists(szPath):
                szPath = resourcePath("7za.exe")

            if not os.path.exists(szPath): 
                raise FileNotFoundError(f"7-Zip not found.")

            isFH6 = getattr(self, "gameVar", None) and self.gameVar.get() == "FH6"
            selectedRegion = "US & MX" if isFH6 else self.regionVar.get()
            targetFiles = EU_UK_FILES if selectedRegion == "EU & UK" else US_MX_FILES
            atlasFiles = EU_UK_ATLAS_FILES if selectedRegion == "EU & UK" else US_MX_ATLAS_FILES

            if isCarSpecific or isFH6:
                tempDir = tempfile.mkdtemp()
                if os.path.isdir(outputBase):
                    self.log("Copying Car Folder...")
                    shutil.copytree(outputBase, tempDir, dirs_exist_ok=True)
                else:
                    self.log("Extracting Car Zip...")
                    subprocess.run([szPath, "x", outputBase, f"-o{tempDir}", "-y"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                carId = os.path.splitext(os.path.basename(outputBase))[0]
                texturesDir = os.path.join(tempDir, "textures")
                materialsDir = os.path.join(tempDir, "materials")
                os.makedirs(texturesDir, exist_ok=True)
                os.makedirs(materialsDir, exist_ok=True)
                
                if isFH6:
                    prefix = "jpnplate"
                else:
                    prefix = "euplate" if selectedRegion == "EU & UK" else "usplate"
                
                if imgPath and os.path.isfile(imgPath):
                    shutil.copyfile(imgPath, os.path.join(texturesDir, f"{prefix}_diff.swatchbin"))
                if nrmlPath and os.path.isfile(nrmlPath):
                    shutil.copyfile(nrmlPath, os.path.join(texturesDir, f"{prefix}_nrml.swatchbin"))
                    
                isGlossy = getattr(self, "glossyVar", ctk.BooleanVar(value=False)).get()
                
                if isFH6:
                    baseMatPath = resourcePath("jpn.materialbin")
                    destMatName = "jpn.materialbin"
                    
                    if os.path.exists(baseMatPath):
                        shutil.copy(baseMatPath, os.path.join(materialsDir, destMatName))
                        
                        modelPaths = []
                        targetPlate = "platejpn"
                        for root, dirs, files in os.walk(tempDir):
                            for f in files:
                                fileName = f.lower()
                                if targetPlate in fileName and fileName.endswith(".modelbin"):
                                    modelPaths.append(os.path.join(root, f))
                                    
                        def modelPatchLogic(s, l):
                            sLower = s.lower()
                            if "base" in sLower or "jpn.materialbin" in sLower:
                                return f"Game:\\Media\\cars\\{carId}\\materials\\{destMatName}"
                            return None
                            
                        import fh6_plate_patcher
                        from pathlib import Path
                        for path in modelPaths:
                            if self.currentBackupVar.get():
                                bakPath = path + ".bak"
                                if not os.path.exists(bakPath): 
                                    shutil.copy2(path, bakPath)
                                    
                            try:
                                fh6_plate_patcher.patch_modelbin(
                                    input_path=Path(path),
                                    output_path=Path(path),
                                    material_id=None,
                                    flip_v=True,
                                    all_channels=True,
                                    dry_run=False,
                                    delete_bracket=self.deleteBracketVar.get(),
                                    delete_screw=self.deleteScrewVar.get()
                                )
                            except Exception as e:
                                self.log(f"Error patching {os.path.basename(path)}: {e}")
                                
                            self.patchBinaryRegex(path, b'Game:\\\\[mM]edia\\\\cars\\\\[a-zA-Z0-9_\\\\.\\s-]+?\\.materialbin', modelPatchLogic)
                            
                        self.patchBinaryRegex(os.path.join(materialsDir, destMatName), b'Game:\\\\[mM]edia\\\\cars\\\\_library\\\\[a-zA-Z0-9_\\\\.\\s-]+?\\.swatchbin', lambda s, l: (f"Game:\\Media\\cars\\{carId}\\textures\\{prefix}_diff.swatchbin" if "diff" in s.lower() else f"Game:\\Media\\cars\\{carId}\\textures\\{prefix}_nrml.swatchbin" if "nrml" in s.lower() else None))
                else:
                    sourceMatName = ("eu_glossy.materialbin" if selectedRegion == "EU & UK" else "us_glossy.materialbin") if isGlossy else ("eu.materialbin" if selectedRegion == "EU & UK" else "us.materialbin")
                    baseMatPath = resourcePath(sourceMatName)
                    
                    usfMatName = "usf_glossy.materialbin" if isGlossy else "usf.materialbin"
                    baseUsfMatPath = resourcePath(usfMatName)
                    
                    if os.path.exists(baseMatPath):
                        destMatName = "eu.materialbin" if selectedRegion == "EU & UK" else "us.materialbin"
                        shutil.copy(baseMatPath, os.path.join(materialsDir, destMatName))
                        
                        if selectedRegion == "US & MX" and os.path.exists(baseUsfMatPath):
                            shutil.copy(baseUsfMatPath, os.path.join(materialsDir, "usf.materialbin"))
                            self.patchBinaryRegex(os.path.join(materialsDir, "usf.materialbin"), b'Game:\\\\[mM]edia\\\\cars\\\\_library\\\\[a-zA-Z0-9_\\\\.\\s-]+?\\.swatchbin', lambda s, l: (f"Game:\\Media\\cars\\{carId}\\textures\\{prefix}_diff.swatchbin" if "diff" in s.lower() else f"Game:\\Media\\cars\\{carId}\\textures\\{prefix}_nrml.swatchbin" if "nrml" in s.lower() else None))
                        
                        modelPaths = []
                        targetPlate = "plateeu" if selectedRegion == "EU & UK" else "plateus"
                        for root, dirs, files in os.walk(tempDir):
                            for f in files:
                                fileName = f.lower()
                                if targetPlate in fileName and fileName.endswith(".modelbin"):
                                    modelPaths.append(os.path.join(root, f))
                        
                        def modelPatchLogic(s, l):
                            sLower = s.lower()
                            
                            if "atlas" in sLower:
                                return None
                                
                            if selectedRegion == "US & MX" and "front" in sLower:
                                return f"Game:\\Media\\cars\\{carId}\\materials\\usf.materialbin"
                            elif "base" in sLower or "us.materialbin" in sLower or "eu.materialbin" in sLower:
                                return f"Game:\\Media\\cars\\{carId}\\materials\\{destMatName}"
                                
                            return None
                        
                        for path in modelPaths:
                            if self.currentBackupVar.get():
                                bakPath = path + ".bak"
                                if not os.path.exists(bakPath): 
                                    shutil.copy2(path, bakPath)
                            self.patchBinaryRegex(path, b'Game:\\\\[mM]edia\\\\cars\\\\[a-zA-Z0-9_\\\\.\\s-]+?\\.materialbin', modelPatchLogic)
                            
                        self.patchBinaryRegex(os.path.join(materialsDir, destMatName), b'Game:\\\\[mM]edia\\\\cars\\\\_library\\\\[a-zA-Z0-9_\\\\.\\s-]+?\\.swatchbin', lambda s, l: (f"Game:\\Media\\cars\\{carId}\\textures\\{prefix}_diff.swatchbin" if "diff" in s.lower() else f"Game:\\Media\\cars\\{carId}\\textures\\{prefix}_nrml.swatchbin" if "nrml" in s.lower() else None))
                
                if customExportPath:
                    if exportIsFolder:
                        outputDest = customExportPath
                        if os.path.exists(outputDest) and os.path.isdir(outputDest):
                            shutil.copytree(tempDir, outputDest, dirs_exist_ok=True)
                        else:
                            shutil.copytree(tempDir, outputDest)
                        outputDest = None
                    else:
                        outputDest = customExportPath
                        if os.path.exists(outputDest):
                            if os.path.isdir(outputDest): shutil.rmtree(outputDest)
                            else: os.remove(outputDest)
                else:
                    if isFH6:
                        fh6Out = os.path.join(self.fh6GameDirVar.get(), "MediaPC", "Cars")
                        os.makedirs(fh6Out, exist_ok=True)
                        carName = os.path.basename(outputBase)
                        if not carName.lower().endswith('.zip'): carName += ".zip"
                        outputDest = os.path.join(fh6Out, carName)
                        if os.path.exists(outputDest):
                            os.remove(outputDest)
                    else:
                        outputDest = outputBase
                        if os.path.isdir(outputDest):
                            shutil.rmtree(outputDest)
                            shutil.copytree(tempDir, outputDest)
                            outputDest = None
                        else:
                            os.remove(outputBase)
                
                if outputDest:
                    subprocess.run([szPath, "a", "-tzip", compFlag, outputDest, f"{tempDir}\\*"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                shutil.rmtree(tempDir)
                self.isCompiling = False
                self.totalCompiled += 1
                self.saveConfig(silent=True)
                self.log("Car-specific build complete!")
                if not isSilent: self.after(0, lambda: messagebox.showinfo("Success", "Successfully modified the car!"))
                return

            if isLatest:
                libDir = os.path.dirname(outputBase)
                targetTexZip = outputBase
            else:
                libDir = outputBase
                targetTexZip = os.path.join(libDir, "Textures.zip")
            
            self.log(f"Processing {os.path.basename(targetTexZip)}...")
            texTemp = tempfile.mkdtemp()
            if os.path.exists(targetTexZip):
                subprocess.run([szPath, "x", targetTexZip, f"-o{texTemp}", "-y"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            swatchesDir = os.path.join(texTemp, "plates", "swatches")
            os.makedirs(swatchesDir, exist_ok=True)
            
            if self.currentBackupVar.get():
                for f in targetFiles + atlasFiles:
                    targetFile = os.path.join(swatchesDir, f)
                    if os.path.exists(targetFile): os.replace(targetFile, targetFile + ".bak")
            
            if imgPath and os.path.isfile(imgPath): self.generateSwatches(imgPath, targetFiles, False, swatchesDir)
            if nrmlPath and os.path.isfile(nrmlPath): self.generateSwatches(nrmlPath, targetFiles, True, swatchesDir)
            
            blank = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
            for a in atlasFiles: blank.save(os.path.join(swatchesDir, a), format="PNG")
            
            if customExportPath:
                outTexZip = os.path.join(customExportPath, "Textures.zip")
            else:
                outTexZip = targetTexZip
            if os.path.exists(outTexZip): os.remove(outTexZip)
            subprocess.run([szPath, "a", "-tzip", compFlag, outTexZip, "."], cwd=texTemp, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            shutil.rmtree(texTemp)

            if getattr(self, "glossyVar", ctk.BooleanVar(value=False)).get():
                self.log(f"Processing Materials.zip...")
                matTemp = tempfile.mkdtemp()
                
                targetMatZip = os.path.join(libDir, "Materials.zip")
                if os.path.exists(targetMatZip):
                    subprocess.run([szPath, "x", targetMatZip, f"-o{matTemp}", "-y"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                platesDir = os.path.join(matTemp, "plates")
                os.makedirs(platesDir, exist_ok=True)
                
                anyAdded = False
                if selectedRegion == "EU & UK":
                    euSrc = resourcePath("eu_glossy.materialbin")
                    euTargets = ["plate_base.materialbin", "plate_base_uk_front.materialbin", "plateuk_base.materialbin", "plateeu_base_he.materialbin"]
                    if os.path.exists(euSrc):
                        for name in euTargets:
                            shutil.copyfile(euSrc, os.path.join(platesDir, name))
                            self.log(f"✓ {name}")
                        anyAdded = True
                else:
                    usSrc = resourcePath("us_glossy.materialbin")
                    usTargets = ["plateus_base.materialbin", "plateus_base_he.materialbin", "plateus_base_front.materialbin"]
                    if os.path.exists(usSrc):
                        for name in usTargets:
                            shutil.copyfile(usSrc, os.path.join(platesDir, name))
                            self.log(f"✓ {name}")
                        anyAdded = True
                
                if anyAdded:
                    if customExportPath:
                        outMatZip = os.path.join(customExportPath, "Materials.zip")
                    else:
                        outMatZip = targetMatZip
                    if os.path.exists(outMatZip): os.remove(outMatZip)
                    subprocess.run([szPath, "a", "-tzip", compFlag, outMatZip, "."], cwd=matTemp, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    self.log("Materials.zip update complete!")
                shutil.rmtree(matTemp)

            self.isCompiling = False
            self.totalCompiled += 1
            self.saveConfig(silent=True)
            self.log("Build complete!")
            if not isSilent: self.after(0, lambda: messagebox.showinfo("Success", "Generation Complete!"))
        except Exception as e:
            self.isCompiling = False
            self.after(0, lambda err=e: messagebox.showerror("Generation Error", f"An error occurred:\n{err}"))

    def generateSwatches(self, p, t, isN, out):
        for s in [f for f in t if ("nrml" in f) == isN]:
            try: 
                shutil.copyfile(p, os.path.join(out, s))
                self.log(f"✓ {s}")
            except (OSError, IOError):
                pass

    def runRestore(self):
        isCarSpecific = getattr(self, "outputModeVar", None) and self.outputModeVar.get() == "Car-Specific (Car.zip)"
        isFH6 = getattr(self, "gameVar", None) and self.gameVar.get() == "FH6"

        if isFH6:
            outputBase = self.genOutputDirVar.get()
            if outputBase == "Not Selected" or (not (os.path.isfile(outputBase) and outputBase.lower().endswith('.zip')) and not os.path.isdir(outputBase)):
                messagebox.showerror("Error", "Please select a valid FH6 Car .zip file or folder first.")
                return
            fh6Out = os.path.join(self.fh6GameDirVar.get(), "MediaPC", "Cars")
            carName = os.path.basename(outputBase)
            if not carName.lower().endswith('.zip'): carName += ".zip"
            outputBase = os.path.join(fh6Out, carName)
            if not os.path.exists(outputBase):
                messagebox.showerror("Error", "Could not find patched FH6 car to restore.")
                return
        elif isCarSpecific:
            outputBase = self.genOutputDirVar.get()
            if outputBase == "Not Selected" or (not (os.path.isfile(outputBase) and outputBase.lower().endswith('.zip')) and not os.path.isdir(outputBase)):
                messagebox.showerror("Error", "Please select a valid Car.zip file or folder first.")
                return
        else:
            if not hasattr(self, 'fh5GameDirVar') or self.fh5GameDirVar.get() == "Not Selected" or not os.path.isdir(self.fh5GameDirVar.get()):
                messagebox.showerror("Error", "Please configure your FH5 Game Directory in Settings.")
                return
            fh5GameDir = self.fh5GameDirVar.get()
            if self.versionVar.get() == "Latest (Direct Zip)":
                outputBase = os.path.join(fh5GameDir, "Content", "media", "cars", "_library", "Textures.zip")
            else:
                outputBase = os.path.join(fh5GameDir, "media", "Stripped", "MediaOverride", "RC0", "Cars", "_library")
                
            if self.versionVar.get() != "Latest (Direct Zip)" or not os.path.isfile(outputBase):
                messagebox.showerror("Error", "Please make sure you are in 'Latest' mode and Textures.zip exists.")
                return
            
        threading.Thread(target=self.processRestore, args=(outputBase, isCarSpecific), daemon=True).start()

    def processRestore(self, outputBase, isCarSpecific=False):
        try:
            self.log("Starting restore process...")
            szPath = self.szPathVar.get().strip('"')

            if not os.path.exists(szPath):
                szPath = resourcePath("7za.exe")

            if not os.path.exists(szPath): 
                raise FileNotFoundError(f"7-Zip not found. Checked settings and portable fallback.")
            
            selectedRegion = self.regionVar.get()
            targetFiles = EU_UK_FILES if selectedRegion == "EU & UK" else US_MX_FILES
            atlasFiles = EU_UK_ATLAS_FILES if selectedRegion == "EU & UK" else US_MX_ATLAS_FILES

            tempDir = tempfile.mkdtemp()
            
            if isCarSpecific:
                if os.path.isdir(outputBase):
                    self.log("Copying Car Folder...")
                    shutil.copytree(outputBase, tempDir, dirs_exist_ok=True)
                else:
                    self.log("Extracting Car Zip...")
                    subprocess.run([szPath, "x", outputBase, f"-o{tempDir}", "-y"], check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.log("Restoring .bak files in Car Zip...")
                restoredAny = False
                for root, dirs, files in os.walk(tempDir):
                    for f in files:
                        if f.endswith(".bak"):
                            targetFile = os.path.join(root, f[:-4])
                            bakFile = os.path.join(root, f)
                            if os.path.exists(targetFile):
                                os.remove(targetFile)
                            os.rename(bakFile, targetFile)
                            restoredAny = True
                
                if not restoredAny:
                    self.log("No .bak files found to restore.")
                else:
                    self.log("Rebuilding Car Zip...")
                    compFlag = "-mx1" if "mx1" in self.compLevelVar.get() else "-mx9" if "mx9" in self.compLevelVar.get() else "-mx5"
                    if os.path.isdir(outputBase):
                        shutil.rmtree(outputBase)
                        shutil.copytree(tempDir, outputBase)
                    else:
                        os.remove(outputBase)
                        subprocess.run([szPath, "a", "-tzip", compFlag, outputBase, f"{tempDir}\\*"], check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                self.log("Extracting Textures.zip...")
                subprocess.run([szPath, "x", outputBase, f"-o{tempDir}", "-y"], check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

                swatchesDir = os.path.join(tempDir, "plates", "swatches")
                
                self.log("Restoring .bak files...")
                for f in targetFiles + atlasFiles:
                    targetFile = os.path.join(swatchesDir, f)
                    bakFile = targetFile + ".bak"
                    
                    if os.path.exists(targetFile): os.remove(targetFile)
                    if os.path.exists(bakFile): os.rename(bakFile, targetFile)

                self.log("Rebuilding Textures.zip...")
                os.remove(outputBase)
                compFlag = "-mx1" if "mx1" in self.compLevelVar.get() else "-mx9" if "mx9" in self.compLevelVar.get() else "-mx5"
                subprocess.run([szPath, "a", "-tzip", compFlag, outputBase, f"{tempDir}\\*"], check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

            shutil.rmtree(tempDir)
            self.log("Restore complete!")
            self.after(0, lambda: messagebox.showinfo("Success", "Original plates restored!"))
        except subprocess.CalledProcessError as e:
            self.after(0, lambda err=e: messagebox.showerror("7-Zip Error", f"Failed to process archive (Exit Code {err.returncode}).\n\nOutput:\n{err.stderr.strip() if err.stderr else err.stdout.strip()}"))
        except Exception as e:
            self.after(0, lambda e=e: messagebox.showerror("Restore Error", str(e)))

    def animateButton(self):
        if not getattr(self, "isCompiling", False):
            self.btnGenerate.configure(
                text=" COMPILE TO GAME", 
                image=self.loadIcon("package-plus.png", size=24), 
                state="normal"
            )
            if hasattr(self, "btnExport"):
                self.btnExport.configure(
                    text=" EXPORT ZIP...",
                    image=self.loadIcon("download.png", size=24),
                    state="normal"
                )
            if hasattr(self, "btnExportFolder"):
                self.btnExportFolder.configure(
                    text=" EXPORT FOLDER...",
                    image=self.loadIcon("download.png", size=24),
                    state="normal"
                )
            return
        
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        animText = f"{frames[self.spinnerFrame % len(frames)]} COMPILING..."
        self.btnGenerate.configure(text=animText, state="disabled")
        if hasattr(self, "btnExport"):
            self.btnExport.configure(text=animText, state="disabled")
        if hasattr(self, "btnExportFolder"):
            self.btnExportFolder.configure(text=animText, state="disabled")
        self.spinnerFrame += 1
        self.after(100, self.animateButton)

    def toggleBackups(self):
        self.saveConfig(silent=True)
        self.updateRestoreButtonsVisibility()

    def updateRestoreButtonsVisibility(self):
        show = self.currentBackupVar.get()
        
        if hasattr(self, 'btnRestore') and self.btnRestore.winfo_exists():
            if show:
                if not self.btnRestore.winfo_manager() and hasattr(self, 'logArea'):
                    self.btnRestore.pack(fill="x", padx=0, pady=(0, 20), expand=True, before=self.logArea)
            else:
                self.btnRestore.pack_forget()
                
        if hasattr(self, 'historyRestoreBtn') and self.historyRestoreBtn.winfo_exists():
            if show:
                if not self.historyRestoreBtn.winfo_manager() and hasattr(self, 'historyList'):
                    self.historyRestoreBtn.pack(fill="x", padx=0, pady=(0, 20), before=self.historyList)
            else:
                self.historyRestoreBtn.pack_forget()

        if hasattr(self, 'presetRestoreBtn') and self.presetRestoreBtn.winfo_exists():
            if show:
                if not self.presetRestoreBtn.winfo_manager() and hasattr(self, 'presetsList'):
                    self.presetRestoreBtn.pack(fill="x", padx=0, pady=(0, 20), before=self.presetsList)
            else:
                self.presetRestoreBtn.pack_forget()

    def toggleHelpText(self, value):
        if getattr(self, "gameVar", None) and self.gameVar.get() == "FH6":
            value = "FH6"
            
        if value == "FH6":
            if hasattr(self, "glossySwitch") and self.glossySwitch.winfo_manager():
                self.glossySwitch.pack_forget()
            if hasattr(self, "historyGlossySwitch") and self.historyGlossySwitch.winfo_manager():
                self.historyGlossySwitch.pack_forget()
            if hasattr(self, "presetGlossySwitch") and self.presetGlossySwitch.winfo_manager():
                self.presetGlossySwitch.pack_forget()
            if hasattr(self, "glossyVar"):
                self.glossyVar.set(False)
        else:
            if hasattr(self, "glossySwitch") and not self.glossySwitch.winfo_manager() and hasattr(self, "compilerBackupSwitch"):
                self.glossySwitch.pack(side="left", padx=(0, 15), before=self.compilerBackupSwitch)
            if hasattr(self, "historyGlossySwitch") and not self.historyGlossySwitch.winfo_manager() and hasattr(self, "historyBackupSwitch"):
                self.historyGlossySwitch.pack(side="left", padx=(0, 15), before=self.historyBackupSwitch)
            if hasattr(self, "presetGlossySwitch") and not self.presetGlossySwitch.winfo_manager() and hasattr(self, "presetBackupSwitch"):
                self.presetGlossySwitch.pack(side="left", padx=(0, 15), before=self.presetBackupSwitch)

        if value == "Latest (Direct Zip)" or value == "FH6":
            if hasattr(self, "modeRow"):
                self.modeRow.pack_forget()
            if hasattr(self, "historyModeContainer"):
                self.historyModeContainer.pack_forget()
            if hasattr(self, "presetModeContainer"):
                self.presetModeContainer.pack_forget()
            
            if hasattr(self, "outputLabel") and self.outputLabel.winfo_manager():
                self.outputLabel.pack_forget()
            if hasattr(self, "helpTextLabel") and self.helpTextLabel.winfo_manager():
                self.helpTextLabel.pack_forget()
            if hasattr(self, "genDirRow") and self.genDirRow.winfo_manager():
                self.genDirRow.pack_forget()
                
            if hasattr(self, "historyOutputContainer") and hasattr(self, "historyTopRow"):
                self.historyOutputContainer.pack_forget()
                if hasattr(self, "historyBottomRow"):
                    self.historyBottomRow.pack_forget()
                self.historyOutputContainer.pack(in_=self.historyTopRow, side="left", fill="x", expand=True)

            if hasattr(self, "presetOutputContainer") and hasattr(self, "presetTopRow"):
                self.presetOutputContainer.pack_forget()
                if hasattr(self, "presetBottomRow"):
                    self.presetBottomRow.pack_forget()
                self.presetOutputContainer.pack(in_=self.presetTopRow, side="left", fill="x", expand=True)

            if value == "Latest (Direct Zip)":
                if getattr(self, "outputModeVar", None) and self.outputModeVar.get() != "Global":
                    self.outputModeVar.set("Global")
                    self.toggleOutputMode("Global")
            elif value == "FH6":
                if getattr(self, "outputModeVar", None) and self.outputModeVar.get() != "Car-Specific (Car.zip)":
                    self.outputModeVar.set("Car-Specific (Car.zip)")
                    self.toggleOutputMode("Car-Specific (Car.zip)")
        else:
            if hasattr(self, "modeRow") and not self.modeRow.winfo_manager():
                self.modeRow.pack(fill="x", padx=20, pady=(0, 10), after=self.outputHeaderRow if hasattr(self, "outputHeaderRow") else None)
                
            if hasattr(self, "historyModeContainer") and not self.historyModeContainer.winfo_manager():
                self.historyModeContainer.pack(side="left")
                
            if hasattr(self, "historyOutputContainer") and hasattr(self, "historyBottomRow"):
                self.historyOutputContainer.pack_forget()
                self.historyBottomRow.pack(fill="x", pady=(10, 0))
                self.historyOutputContainer.pack(in_=self.historyBottomRow, side="left", fill="x", expand=True)

            if hasattr(self, "presetModeContainer") and not self.presetModeContainer.winfo_manager():
                self.presetModeContainer.pack(side="left")
                
            if hasattr(self, "presetOutputContainer") and hasattr(self, "presetBottomRow"):
                self.presetOutputContainer.pack_forget()
                self.presetBottomRow.pack(fill="x", pady=(10, 0))
                self.presetOutputContainer.pack(in_=self.presetBottomRow, side="left", fill="x", expand=True)

        if getattr(self, "outputModeVar", None) and self.outputModeVar.get() == "Car-Specific (Car.zip)":
            if hasattr(self, "outputLabel"):
                self.outputLabel.configure(text="Car Path (.zip or Folder):")
                if not self.outputLabel.winfo_manager(): self.outputLabel.pack(anchor="w", padx=20)
            if hasattr(self, "helpTextLabel"):
                self.helpTextLabel.configure(text="Select the .zip/folder of the car you want to apply this plate to.")
                if not self.helpTextLabel.winfo_manager(): self.helpTextLabel.pack(anchor="w", padx=20, pady=(0, 5))
            if hasattr(self, "genDirRow") and not self.genDirRow.winfo_manager():
                self.genDirRow.pack(fill="x", padx=20, pady=(0, 5))
            if hasattr(self, "historyOutputLabel"): self.historyOutputLabel.configure(text="Car Path (.zip or Folder):")
            if hasattr(self, "presetOutputLabel"): self.presetOutputLabel.configure(text="Car Path (.zip or Folder):")
            
            if hasattr(self, "subHelpTextLabel"):
                self.subHelpTextLabel.place_forget()
                self.subHelpTextLabel.pack_forget()

        else:
            isAutoResolve = getattr(self, "autoResolvePathsVar", ctk.BooleanVar(value=True)).get()
            isFH6 = getattr(self, "gameVar", None) and self.gameVar.get() == "FH6"
            
            if value == "Latest (Direct Zip)":
                self.outputLabel.configure(text="Textures.zip Path:")
                if hasattr(self, "historyOutputLabel"): self.historyOutputLabel.configure(text="Textures.zip Path:")
                if hasattr(self, "presetOutputLabel"): self.presetOutputLabel.configure(text="Textures.zip Path:")
                
                self.helpTextLabel.configure(text=r"Select your original Textures.zip file in Forza Horizon 5\Content\media\cars\_library")
                self.subHelpTextLabel.place_forget()
                
                if hasattr(self, 'defaultOutLatestVar'):
                    latestDef = self.defaultOutLatestVar.get()
                    self.genOutputDirVar.set(latestDef if latestDef != "Not Selected" else "Not Selected")

            else:
                self.outputLabel.configure(text="Output Textures.zip location:")
                if hasattr(self, "historyOutputLabel"): self.historyOutputLabel.configure(text="Output Textures.zip location:")
                if hasattr(self, "presetOutputLabel"): self.presetOutputLabel.configure(text="Output Textures.zip location:")
                
                self.helpTextLabel.configure(text=r"Select the game's Textures.zip file directly. We recommend compiling to the MediaOverride directory to avoid losing original game files:")
                if not isFH6:
                    self.subHelpTextLabel.configure(text="Automatically merges into any existing Textures.zip/Materials.zip you might have from other mods. ")
                    self.subHelpTextLabel.place_forget()
                    if not self.subHelpTextLabel.winfo_manager():
                        self.subHelpTextLabel.pack(anchor="w", padx=20, pady=(5, 10))
                
                if hasattr(self, 'defaultOutVar'):
                    oldDef = self.defaultOutVar.get()
                    self.genOutputDirVar.set(oldDef if oldDef != "Not Selected" else "Not Selected")

            if isAutoResolve:
                if hasattr(self, "outputHeaderLabel"): self.outputHeaderLabel.configure(text="Output Settings")
                if hasattr(self, "outputLabel") and self.outputLabel.winfo_manager(): self.outputLabel.pack_forget()
                if hasattr(self, "helpTextLabel") and self.helpTextLabel.winfo_manager(): self.helpTextLabel.pack_forget()
                if hasattr(self, "genDirRow") and self.genDirRow.winfo_manager(): self.genDirRow.pack_forget()
                if hasattr(self, "historyOutputContainer") and self.historyOutputContainer.winfo_manager(): self.historyOutputContainer.pack_forget()
                if hasattr(self, "presetOutputContainer") and self.presetOutputContainer.winfo_manager(): self.presetOutputContainer.pack_forget()
                if hasattr(self, "outputFrame"): self.outputFrame.pack_configure(ipady=5)
            else:
                if hasattr(self, "outputHeaderLabel"): self.outputHeaderLabel.configure(text="Step 4: Output Location")
                if hasattr(self, "outputLabel") and not self.outputLabel.winfo_manager(): self.outputLabel.pack(anchor="w", padx=20)
                if hasattr(self, "helpTextLabel") and not self.helpTextLabel.winfo_manager(): self.helpTextLabel.pack(anchor="w", padx=20, pady=(0, 5))
                if hasattr(self, "genDirRow") and not self.genDirRow.winfo_manager(): self.genDirRow.pack(fill="x", padx=20, pady=(0, 5))
                if hasattr(self, "outputFrame"): self.outputFrame.pack_configure(ipady=15)
                
        self.updateMaterialsZipVisibility()

    def setupHistoryPage(self):
        ctk.CTkLabel(self.historyPage, text="Plate History", font=ctk.CTkFont(size=32, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(
            self.historyPage, 
            text="View your previous exports and use them as presets. You can select one EU and one US plate to bundle them into a single compilation.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            wraplength=587,
            justify="left"
        ).pack(anchor="w", padx=(0, 20), pady=(0, 20))
        
        self.historyCartRow = ctk.CTkFrame(self.historyPage, fg_color="transparent")
        self.historyCartRow.pack(fill="x", pady=(0, 10))

        self.cartStatus = ctk.CTkLabel(self.historyCartRow, text="No Plates Selected", font=ctk.CTkFont(size=14), text_color=COLORS["accent_primary"])
        self.cartStatus.pack(side="left")

        histSwitchesFrame = ctk.CTkFrame(self.historyCartRow, fg_color="transparent")
        histSwitchesFrame.pack(side="right")

        self.historyGlossySwitch = ctk.CTkSwitch(
            histSwitchesFrame, text="Glossy Finish", variable=self.glossyVar,
            button_color=COLORS["accent_primary"], command=self.updateMaterialsZipVisibility
        )
        self.historyGlossySwitch.pack(side="left", padx=(0, 15))
        
        self.historyDeleteBracketToggle = ctk.CTkSwitch(
            histSwitchesFrame, text="Delete Seal", variable=self.deleteBracketVar,
            button_color=COLORS["accent_primary"]
        )
        
        self.historyDeleteScrewToggle = ctk.CTkSwitch(
            histSwitchesFrame, text="Delete Plate Screw", variable=self.deleteScrewVar,
            button_color=COLORS["accent_primary"]
        )

        self.historyBackupSwitch = ctk.CTkSwitch(
            histSwitchesFrame, text="Create Backups", variable=self.currentBackupVar,
            button_color=COLORS["accent_primary"], command=self.onBackupToggle
        )
        self.historyBackupSwitch.pack(side="left")

        self.historySettingsFrame = ctk.CTkFrame(self.historyPage, fg_color="transparent")
        self.historySettingsFrame.pack(fill="x", pady=(0, 15))

        self.historyTopRow = ctk.CTkFrame(self.historySettingsFrame, fg_color="transparent")
        self.historyTopRow.pack(fill="x")

        self.historyBottomRow = ctk.CTkFrame(self.historySettingsFrame, fg_color="transparent")

        self.historyVersionLabel = ctk.CTkLabel(self.historyTopRow, text="Version:", font=ctk.CTkFont(size=13, weight="bold"))
        self.historyVersionLabel.pack(side="left", padx=(0, 10))
        
        self.historyVersionBorder = ctk.CTkFrame(self.historyTopRow, fg_color=COLORS["bg_secondary"], border_width=2, border_color=COLORS["border"], corner_radius=6)
        self.historyVersionBorder.pack(side="left", padx=(0, 20))
        
        ctk.CTkOptionMenu(
            self.historyVersionBorder, 
            variable=self.versionVar, 
            values=["Latest (Direct Zip)", "1.634.818.0"], 
            width=170, 
            fg_color=COLORS["bg_secondary"], 
            button_color=COLORS["bg_secondary"], 
            button_hover_color=COLORS["border"], 
            dropdown_fg_color=COLORS["bg_card"], 
            dropdown_hover_color=COLORS["border"], 
            dropdown_text_color=COLORS["text_primary"], 
            corner_radius=4,
            command=lambda v: (self.toggleHelpText(v), self.saveConfig(silent=True))
        ).pack(padx=2, pady=2)

        self.historyModeContainer = ctk.CTkFrame(self.historyTopRow, fg_color="transparent")
        
        ctk.CTkLabel(self.historyModeContainer, text="Mode:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 10))
        
        historyModeBorder = ctk.CTkFrame(self.historyModeContainer, fg_color=COLORS["bg_secondary"], border_width=2, border_color=COLORS["border"], corner_radius=6)
        historyModeBorder.pack(side="left", padx=(0, 5))
        
        ctk.CTkOptionMenu(
            historyModeBorder, variable=self.outputModeVar, 
            values=["Global", "Car-Specific (Car.zip)"], width=210,
            fg_color=COLORS["bg_secondary"], button_color=COLORS["bg_secondary"], 
            button_hover_color=COLORS["border"], dropdown_fg_color=COLORS["bg_card"], 
            dropdown_hover_color=COLORS["border"], dropdown_text_color=COLORS["text_primary"], 
            corner_radius=4, command=self.toggleOutputMode
        ).pack(padx=2, pady=2)
        
        self.historyOutputContainer = ctk.CTkFrame(self.historySettingsFrame, fg_color="transparent")
        
        historyTexRow = ctk.CTkFrame(self.historyOutputContainer, fg_color="transparent")
        historyTexRow.pack(fill="x")
        
        self.historyOutputLabel = ctk.CTkLabel(historyTexRow, text="Textures.zip Path:", font=ctk.CTkFont(size=13, weight="bold"))
        self.historyOutputLabel.pack(side="left", padx=(0, 10))
        
        self.historyDirEntry = ctk.CTkEntry(historyTexRow, textvariable=self.genOutputDirVar, fg_color=COLORS["bg_secondary"], border_color=COLORS["border"])
        self.historyDirEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.historyDirEntry.bind("<Button-1>", lambda e: self.browseGenOutputDir())
        self.setupEntryDrop(self.historyDirEntry, self.genOutputDirVar)
        
        ctk.CTkButton(historyTexRow, text="Browse", width=80, fg_color=COLORS["bg_secondary"], hover_color=COLORS["border"], command=self.browseGenOutputDir).pack(side="left", padx=(0, 10))

        self.histMaterialsZipRow = ctk.CTkFrame(self.historyOutputContainer, fg_color="transparent")
        
        histMatLabel = ctk.CTkLabel(self.histMaterialsZipRow, text="Materials.zip Path:", font=ctk.CTkFont(size=13, weight="bold"))
        histMatLabel.pack(side="left", padx=(0, 10))
        
        self.histMaterialsEntry = ctk.CTkEntry(self.histMaterialsZipRow, textvariable=self.materialsZipVar, fg_color=COLORS["bg_secondary"], border_color=COLORS["border"])
        self.histMaterialsEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.histMaterialsEntry.bind("<Button-1>", lambda e: self.browseMaterialsZip())
        self.setupEntryDrop(self.histMaterialsEntry, self.materialsZipVar)
        
        ctk.CTkButton(self.histMaterialsZipRow, text="Browse", width=80, fg_color=COLORS["bg_secondary"], hover_color=COLORS["border"], command=self.browseMaterialsZip).pack(side="left", padx=(0, 10))


        
        self.cartBtn = ctk.CTkButton(
            self.historyPage, 
            text=" COMPILE SELECTED", 
            image=self.loadIcon("package-plus.png", size=20), 
            command=self.compileCart, 
            fg_color=COLORS["accent_secondary"], 
            height=50,
            width=1200,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.cartBtn.pack(fill="x", padx=0, pady=(0, 20))

        self.historyRestoreBtn = ctk.CTkButton(
            self.historyPage, 
            text=" RESTORE ORIGINALS", 
            image=self.loadIcon("undo.png", size=18),
            fg_color=COLORS["bg_card"], 
            hover_color=COLORS["accent_danger"], 
            height=40, 
            width=1200,
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=self.runRestore
        )
        
        self.historyList = ctk.CTkFrame(self.historyPage, fg_color="transparent")
        self.historyList.pack(fill="both", expand=True)

    def refreshHistory(self):
        for widget in self.historyList.winfo_children(): widget.destroy()
        
        for item in reversed(self.history):
            card = ctk.CTkFrame(self.historyList, fg_color=COLORS["bg_secondary"], corner_radius=8)
            card.pack(fill="x", pady=5, ipadx=10, ipady=10)
            
            imgLabel = ctk.CTkLabel(card, text="⌛", font=ctk.CTkFont(size=24))
            imgLabel.pack(side="left", padx=(10, 5))
            
            imgPath = item.get('img') or item.get('nrml')
            if imgPath and os.path.exists(imgPath):
                threading.Thread(target=self.loadHistoryThumbnail, args=(imgPath, imgLabel), daemon=True).start()
            else:
                imgLabel.configure(image=self.loadIcon("image.png", size=24), text="")

            if item.get('is_preset'):
                imgName = f"{item['name']} (Preset)"
            else:
                imgName = os.path.basename(item['img']) if item.get('img') else "No Image"
                
            regionText = "JPN" if (getattr(self, "gameVar", None) and self.gameVar.get() == "FH6" and "US" in item['region']) else item['region']
            ctk.CTkLabel(card, text=f"{regionText} - {imgName}").pack(side="left", padx=10)
            
            isSelected = item in self.cart.values()
            regionKey = 'us' if item['region'] == "US & MX" else 'eu'
            isBlocked = self.cart[regionKey] is not None and self.cart[regionKey] != item
            
            btnText = "Remove" if isSelected else "Select"
            btnState = "disabled" if isBlocked else "normal"
            btnColor = COLORS["accent_danger"] if isSelected else COLORS["accent_primary"]
            
            ctk.CTkButton(
                card, 
                text="", 
                image=self.loadIcon("trash.png", size=18),
                width=30, 
                height=30, 
                fg_color="transparent", 
                hover_color=COLORS["accent_danger"], 
                command=lambda i=item: self.deleteHistoryItem(i)
            ).pack(side="right", padx=(0, 10))

            ctk.CTkButton(
                card, 
                text="", 
                image=self.loadIcon("download.png", size=18),
                width=30, 
                height=30, 
                fg_color="transparent", 
                hover_color=COLORS["border"], 
                command=lambda i=item: self.exportPlatePack(i)
            ).pack(side="right", padx=(0, 10))

            ctk.CTkButton(
                card, 
                text=btnText, 
                state=btnState, 
                fg_color=btnColor, 
                command=lambda i=item: self.toggleCart(i)
            ).pack(side="right", padx=10)

    def loadHistoryThumbnail(self, path, label):
        try:
            pilImg = Image.open(path)
            w, h = pilImg.size
            newW = int(40 * (w / h))
            pilImg.thumbnail((newW, 40)) 
            ctkImg = ctk.CTkImage(light_image=pilImg, dark_image=pilImg, size=(newW, 40))
            self.uiQueue.put(lambda: self.applyHistoryThumbnail(label, ctkImg))
        except (OSError, ValueError):
            self.uiQueue.put(lambda: self.applyHistoryFallback(label))

    def applyHistoryThumbnail(self, label, img):
        if label.winfo_exists():
            label.configure(image=img, text="")

    def applyHistoryFallback(self, label):
        if label.winfo_exists():
            label.configure(image=self.loadIcon("image.png", size=24), text="")

    def toggleCart(self, item):
        regionKey = 'us' if item['region'] == "US & MX" else 'eu'
        self.cart[regionKey] = None if self.cart[regionKey] == item else item
        
        euName = os.path.basename(self.cart['eu']['img']) if self.cart['eu'] and self.cart['eu']['img'] else "None"
        usName = os.path.basename(self.cart['us']['img']) if self.cart['us'] and self.cart['us']['img'] else "None"
        self.cartStatus.configure(text=f"EU: {euName}  |  US: {usName}")
        self.refreshHistory()

    def compileCart(self):
        outDir = self.genOutputDirVar.get()
        
        if outDir == "Not Selected" or not outDir:
            messagebox.showerror("Error", "Please select an output location.")
            return
            
        self.cartBtn.configure(state="disabled", text="⏳ COMPILING...")
        
        def process():
            try:
                if self.cart['eu']: 
                    self.regionVar.set("EU & UK")
                    self.processFiles(self.cart['eu']['img'], self.cart['eu']['nrml'], outDir, silent=True)
                if self.cart['us']: 
                    self.regionVar.set("US & MX")
                    self.processFiles(self.cart['us']['img'], self.cart['us']['nrml'], outDir, silent=True)
                
                self.after(0, lambda: messagebox.showinfo("Success", "Cart compiled successfully!"))
            except Exception as e:
                self.after(0, lambda err=e: messagebox.showerror("Generation Error", f"An error occurred:\n{err}"))
            finally:
                self.after(0, lambda: self.cartBtn.configure(state="normal", text=" COMPILE CART"))
                
        threading.Thread(target=process, daemon=True).start()

    def deleteHistoryItem(self, item):
        if item in self.history:
            self.history.remove(item)
            
        if self.cart.get('eu') == item: self.cart['eu'] = None
        if self.cart.get('us') == item: self.cart['us'] = None
        
        self.saveConfig(silent=True)
        
        euItem = self.cart.get('eu')
        usItem = self.cart.get('us')
        
        euName = f"{euItem['name']} (Preset)" if euItem and euItem.get('is_preset') else (os.path.basename(euItem.get('img', '')) if euItem and euItem.get('img') else "None")
        usName = f"{usItem['name']} (Preset)" if usItem and usItem.get('is_preset') else (os.path.basename(usItem.get('img', '')) if usItem and usItem.get('img') else "None")
        
        self.cartStatus.configure(text=f"EU: {euName}  |  US: {usName}")
        self.refreshHistory()

    def updateDropzoneRegions(self, *args):
        region = getattr(self, "regionVar", None)
        if not region:
            return
            
        isFH6 = getattr(self, "gameVar", None) and self.gameVar.get() == "FH6"
        target_text = "" if isFH6 else f"Target: {region.get()}"
        
        if hasattr(self, 'imageDropZone') and self.imageDropZone:
            self.imageDropZone.regionLabel.configure(text=target_text)
        if hasattr(self, 'nrmlDropZone') and self.nrmlDropZone:
            self.nrmlDropZone.regionLabel.configure(text=target_text)

    def switchMmTabs(self, tabName):
        if tabName == "Black":
            self.maskSliderFrame.pack_forget()
            self.baseSliderFrame.pack(fill="x")
        elif tabName == "White":
            self.baseSliderFrame.pack_forget()
            self.maskSliderFrame.pack(fill="x")
        else:
            self.maskSliderFrame.pack_forget()
            self.baseSliderFrame.pack(fill="x")
            self.mmTabVar.set("Black")

    def toggleMmAdvanced(self):
        if self.advancedModeVar.get():
            self.mmDropZone.grid(row=0, column=0, sticky="nsew", padx=(0, 5), columnspan=1)
            self.mmMaskDropZone.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

            if not hasattr(self, 'maskBtnsFrame'):
                self.maskBtnsFrame = ctk.CTkFrame(self.mmDropContainer, fg_color="transparent")
                
                self.btnDrawMask = ctk.CTkButton(self.maskBtnsFrame, text="🖌️ New Mask", fg_color=COLORS["bg_card"], hover_color=COLORS["border"], command=lambda: self.openMaskPainter(edit=False))
                self.btnDrawMask.pack(side="left", fill="x", expand=True, padx=(0, 5))

                self.btnEditMask = ctk.CTkButton(self.maskBtnsFrame, text="✏️ Edit Mask", fg_color=COLORS["bg_card"], hover_color=COLORS["border"], command=lambda: self.openMaskPainter(edit=True))
                self.btnEditMask.pack(side="left", fill="x", expand=True, padx=(5, 0))

            self.maskBtnsFrame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="ew")
            
            if not hasattr(self, 'euTipLabel'):
                self.euTipLabel = ctk.CTkLabel(
                    self.mmDropContainer, 
                    text="Tip For EU Plates - Elements are often too close for masking. It is recommended to export two maps (one inward, one outward) and merge them in an external tool instead.", 
                    font=ctk.CTkFont(size=11, slant="italic"), 
                    text_color=COLORS["accent_secondary"],
                    wraplength=580
                )
            self.euTipLabel.grid(row=2, column=0, columnspan=2, pady=(10, 0))

            self.mmTabToggle.pack(before=self.sliderContainer, fill="x", padx=20, pady=(15, 5))
        else:
            self.mmMaskDropZone.grid_forget()
            self.mmDropZone.grid(row=0, column=0, sticky="nsew", padx=2, columnspan=2)

            if hasattr(self, 'maskBtnsFrame'):
                self.maskBtnsFrame.grid_forget()
                
            if hasattr(self, 'euTipLabel'):
                self.euTipLabel.grid_forget()
            
            self.mmTabToggle.pack_forget()
            self.mmTabVar.set("Black")
            self.switchMmTabs("Black")
            
        self.schedulePreviewUpdate()

    def launchPreviewInAdobe(self, tool):
        if not self.mmPreviewThumb:
            messagebox.showwarning("Warning", "No preview image to open!")
            return

        def task():
            try:
                exe = self.psPathVar.get().strip('"') if tool == "photoshop" else self.aiPathVar.get().strip('"')
                
                imgPath = self.mmDropZone.getPath()
                if not imgPath: return
                
                bStr, bBlur, bDir = self.baseIntensity.get(), self.baseBlur.get(), self.baseExtrude.get()
                mStr, mBlur, mDir = self.maskIntensity.get(), self.maskBlur.get(), self.maskExtrude.get()
                maskPath = self.mmMaskDropZone.getPath() if self.advancedModeVar.get() else None
                
                sourceImg = Image.open(imgPath)
                
                baseMap = self.createNormalMapData(sourceImg, bStr, bBlur, bDir)
                
                if maskPath and os.path.exists(maskPath):
                    maskImg = Image.open(maskPath).convert('L').resize(baseMap.size)
                    maskMap = self.createNormalMapData(sourceImg, mStr, mBlur, mDir)
                    finalImg = Image.composite(maskMap, baseMap, maskImg)
                else:
                    finalImg = baseMap

                path = os.path.join(tempfile.gettempdir(), f"map_fullres_adobe_export.png")
                finalImg.save(path)
                
                if os.path.isfile(exe):
                    subprocess.Popen([exe, path])
                else:
                    os.startfile(path)
            except Exception as e: 
                self.after(0, lambda e=e: messagebox.showerror("Error", f"Failed to launch {tool}: {e}"))

        threading.Thread(target=task, daemon=True).start()

    def checkForUpdates(self, manual=False):
        def setStatus(online):
            self.isOnline = online
            if hasattr(self, 'statusText'):
                self.statusText.configure(text=" ONLINE" if online else " OFFLINE")

        def task():
            try:
                import requests
                import webbrowser
                import re
                
                apiUrl = "https://api.github.com/repos/Varsinityy/License-Plate-Compiler/releases/latest"
                response = requests.get(apiUrl, timeout=5)
                
                if response.status_code == 200:
                    self.uiQueue.put(lambda: setStatus(True))
                    
                    data = response.json()
                    latestTag = data.get("tag_name", f"v{APP_VERSION}")
                    
                    latestNums = [int(n) for n in re.findall(r'\d+', latestTag)]
                    currentNums = [int(n) for n in re.findall(r'\d+', APP_VERSION)]
                    
                    while len(latestNums) < 3: latestNums.append(0)
                    while len(currentNums) < 3: currentNums.append(0)
                    
                    latestTuple = tuple(latestNums[:3])
                    currentTuple = tuple(currentNums[:3])
                    
                    if latestTuple > currentTuple:
                        def promptUpdate():
                            from PIL import ImageGrab, ImageFilter, ImageEnhance

                            x, y = self.winfo_rootx(), self.winfo_rooty()
                            w, h = self.winfo_width(), self.winfo_height()

                            try:
                                screen = ImageGrab.grab(bbox=(x, y, x + w, y + h))
                                blurred = screen.filter(ImageFilter.GaussianBlur(radius=6))
                                darkened = ImageEnhance.Brightness(blurred).enhance(0.6)
                                
                                self.overlayBg = ctk.CTkImage(light_image=darkened, dark_image=darkened, size=(w, h))
                            except Exception:
                                self.overlayBg = None

                            overlay = ctk.CTkToplevel(self)
                            overlay.overrideredirect(True)
                            overlay.geometry(f"{w}x{h}+{x}+{y}")
                            overlay.transient(self)
                            
                            if getattr(self, "overlayBg", None):
                                bgLabel = ctk.CTkLabel(overlay, image=self.overlayBg, text="")
                                bgLabel.pack(fill="both", expand=True)
                            else:
                                overlay.attributes('-alpha', 0.7)
                                overlay.configure(fg_color="#000000")
                            
                            dialog = ctk.CTkToplevel(self)
                            dialog.overrideredirect(True)
                            dialog.configure(fg_color=COLORS["border"])
                            
                            dw, dh = 420, 250
                            dx = x + (w // 2) - (dw // 2)
                            dy = y + (h // 2) - (dh // 2)
                            dialog.geometry(f"{dw}x{dh}+{dx}+{dy}")
                            
                            dialog.transient(self)
                            dialog.grab_set()
                            dialog.focus_force()

                            if windll:
                                try:
                                    dialog.update() 
                                    HWND = windll.user32.GetParent(dialog.winfo_id())
                                    windll.dwmapi.DwmSetWindowAttribute(HWND, 33, byref(c_int(2)), sizeof(c_int(2)))
                                except (AttributeError, OSError):
                                    pass

                            container = ctk.CTkFrame(dialog, fg_color=COLORS["bg_secondary"], corner_radius=0, border_width=0)
                            container.pack(fill="both", expand=True, padx=2, pady=2)

                            ctk.CTkLabel(container, text="✨ Update Available", font=ctk.CTkFont(size=24, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=(30, 5))
                            
                            badge = ctk.CTkFrame(container, fg_color=COLORS["accent_primary"], corner_radius=6)
                            badge.pack(pady=(0, 15))
                            ctk.CTkLabel(badge, text=f"Version {latestTag}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#ffffff").pack(padx=10, pady=2)
                            
                            ctk.CTkLabel(container, text="Would you like to install it now?\nThe app will restart automatically.", font=ctk.CTkFont(size=14), text_color=COLORS["text_secondary"], justify="center").pack(pady=(0, 25))

                            btnFrame = ctk.CTkFrame(container, fg_color="transparent")
                            btnFrame.pack(fill="x", pady=(0, 20))

                            def onYes():
                                dialog.destroy()
                                overlay.destroy()
                                exeUrl = None
                                for asset in data.get("assets", []):
                                    if asset.get("name", "").endswith(".exe"):
                                        exeUrl = asset.get("browser_download_url")
                                        break
                                
                                if exeUrl:
                                    threading.Thread(target=self.executeAutoUpdate, args=(exeUrl,), daemon=True).start()
                                else:
                                    messagebox.showerror("Error", "Could not find the .exe file in the latest release.")

                            def onNo():
                                dialog.destroy()
                                overlay.destroy()

                            ctk.CTkButton(btnFrame, text="Not Now", width=120, fg_color=COLORS["bg_card"], hover_color=COLORS["border"], command=onNo).pack(side="left", expand=True, padx=(20, 10))
                            ctk.CTkButton(btnFrame, text="Install Update", width=120, fg_color=COLORS["accent_success"], hover_color="#059669", command=onYes).pack(side="right", expand=True, padx=(10, 20))

                        self.uiQueue.put(promptUpdate)
                        
                    elif manual:
                        self.uiQueue.put(lambda: messagebox.showinfo("Up to Date", "You are running the latest version."))
                else:
                    self.uiQueue.put(lambda: setStatus(False))
                    if manual:
                        self.uiQueue.put(lambda: messagebox.showerror("Update Error", "Could not connect to GitHub."))
            except Exception as e:
                self.uiQueue.put(lambda: setStatus(False))
                if manual: self.uiQueue.put(lambda err=e: messagebox.showerror("Update Error", f"An error occurred: {err}"))

        import threading
        threading.Thread(target=task, daemon=True).start()

    def executeAutoUpdate(self, downloadUrl):
        try:
            self.uiQueue.put(lambda: self.btnUpdate.configure(text="Preparing...", state="disabled"))
            
            if not getattr(sys, 'frozen', False):
                self.uiQueue.put(lambda: messagebox.showinfo("Notice", "Auto-update only works when running the compiled .exe file."))
                self.uiQueue.put(lambda: self.btnUpdate.configure(text="Check for Updates", state="normal"))
                return

            import requests
            import subprocess
            import os
            import time

            currentExe = sys.executable
            baseDir = os.path.dirname(currentExe)
            
            oldExeName = f"PlateCompiler_old_{int(time.time())}.exe"
            oldExe = os.path.join(baseDir, oldExeName)
            newExe = os.path.join(baseDir, "PlateCompiler.exe")

            os.rename(currentExe, oldExe)

            self.uiQueue.put(lambda: self.btnUpdate.configure(text="Downloading 0%..."))
            
            response = requests.get(downloadUrl, stream=True, timeout=30)
            response.raise_for_status()
            
            totalSize = int(response.headers.get('content-length', 0))
            downloaded = 0
            lastPct = -1
            
            with open(newExe, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if totalSize > 0:
                            pct = int((downloaded / totalSize) * 100)
                            if pct != lastPct and pct % 5 == 0:
                                self.uiQueue.put(lambda p=pct: self.btnUpdate.configure(text=f"Downloading {p}%..."))
                                lastPct = pct

            self.uiQueue.put(lambda: self.btnUpdate.configure(text="Installing..."))

            batPath = os.path.join(baseDir, "update_cleanup.bat")
            batContent = f"""@echo off
timeout /t 3 /nobreak > NUL
del "{oldExeName}"
explorer.exe "{newExe}"
del "%~f0"
"""
            with open(batPath, "w") as f:
                f.write(batContent)

            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(["cmd.exe", "/c", "update_cleanup.bat"], cwd=baseDir, creationflags=CREATE_NO_WINDOW)

            os._exit(0)

        except Exception as e:
            try:
                if 'oldExe' in locals() and 'currentExe' in locals():
                    if os.path.exists(oldExe) and not os.path.exists(currentExe):
                        os.rename(oldExe, currentExe)
            except Exception:
                pass 
                
            self.uiQueue.put(lambda err=e: messagebox.showerror("Update Error", f"Failed to update:\n{err}"))
            self.uiQueue.put(lambda: self.btnUpdate.configure(text="Check for Updates", state="normal"))

    def setupEditorPage(self):
        header = ctk.CTkLabel(self.editorPage, text="Plate Designer", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"))
        header.pack(anchor="w", pady=(0, 20))

        controlsFrame = ctk.CTkFrame(self.editorPage, fg_color=COLORS["bg_secondary"], corner_radius=12)
        controlsFrame.pack(fill="x", pady=(0, 20), ipadx=20, ipady=20)

        self.stateVar = ctk.StringVar(value="Japan" if getattr(self, "gameVar", None) and self.gameVar.get() == "FH6" else "Utah (Black)")
        ctk.CTkLabel(controlsFrame, text="Select Template:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        initial_templates = ["Japan"] if getattr(self, "gameVar", None) and self.gameVar.get() == "FH6" else [k for k in PLATE_TEMPLATES.keys() if k != "Japan"]
        self.stateDropdown = ctk.CTkOptionMenu(controlsFrame, variable=self.stateVar, values=initial_templates, command=self.onStateChange)
        self.stateDropdown.pack(fill="x", padx=20)

        self.plateTextVar = ctk.StringVar(value="EXAMPLE")
        self.charLimitLabel = ctk.CTkLabel(controlsFrame, text="Plate Text (Max 8 chars):", font=ctk.CTkFont(weight="bold"))
        self.charLimitLabel.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.plateTextVar.trace_add("write", self.onTextChange)
        self.textEntry = ctk.CTkEntry(controlsFrame, textvariable=self.plateTextVar, font=ctk.CTkFont(size=16), height=40)
        self.textEntry.pack(fill="x", padx=20, pady=(0, 10))

        self.jpnControlsFrame = ctk.CTkFrame(controlsFrame, fg_color="transparent")
        
        import glob
        asset_dir = resourcePath("japanLicensePlate_Generator_assets")
        available_prefectures = []
        if os.path.exists(os.path.join(asset_dir, "issueOffice")):
            for f in glob.glob(os.path.join(asset_dir, "issueOffice", "**", "*.png"), recursive=True):
                available_prefectures.append(os.path.splitext(os.path.basename(f))[0])
            available_prefectures.sort()
            
        available_hiragana = []
        if os.path.exists(os.path.join(asset_dir, "hiragana")):
            for f in glob.glob(os.path.join(asset_dir, "hiragana", "*.svg")):
                name = os.path.splitext(os.path.basename(f))[0]
                available_hiragana.append(name.replace("hiragana_", ""))
            available_hiragana.sort()

        row0 = ctk.CTkFrame(self.jpnControlsFrame, fg_color="transparent")
        row0.pack(fill="x", pady=5)
        self.jpnPlateTypeVar = ctk.StringVar(value="Private Vehicle")
        ctk.CTkLabel(row0, text="Plate Type:").pack(side="left", padx=5)
        
        def onPlateTypeChange(*args):
            if self.jpnPlateTypeVar.get() == "Private Vehicle":
                self.row3.pack(fill="x", pady=5)
            else:
                self.row3.pack_forget()
            self.onTextChange()
            
        type_combo = ctk.CTkOptionMenu(row0, variable=self.jpnPlateTypeVar, 
                                       values=["Private Vehicle", "Commercial Vehicle", "Private Kei", "Commercial Kei", "Temporary"],
                                       command=onPlateTypeChange)
        type_combo.pack(side="left", padx=5)

        row1 = ctk.CTkFrame(self.jpnControlsFrame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        self.jpnRegionVar = ctk.StringVar(value="Shinagawa")
        ctk.CTkLabel(row1, text="Prefecture:").pack(side="left", padx=5)
        
        region_combo = ctk.CTkComboBox(row1, variable=self.jpnRegionVar, width=130)
        region_combo.pack(side="left", padx=5)
        
        try:
            from ctk_scrollable_dropdown import CTkScrollableDropdown
            CTkScrollableDropdown(region_combo, values=available_prefectures, justify="left", button_color="transparent")
        except ImportError:
            region_combo.configure(values=available_prefectures)
        
        self.jpnClassVar = ctk.StringVar(value="300")
        ctk.CTkLabel(row1, text="Class Code:").pack(side="left", padx=5)
        ctk.CTkEntry(row1, textvariable=self.jpnClassVar, width=80).pack(side="left", padx=5)
        
        row2 = ctk.CTkFrame(self.jpnControlsFrame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        self.jpnHiraganaVar = ctk.StringVar(value="さ")
        ctk.CTkLabel(row2, text="Hiragana:").pack(side="left", padx=5)
        
        hiragana_combo = ctk.CTkComboBox(row2, variable=self.jpnHiraganaVar, width=70)
        hiragana_combo.pack(side="left", padx=5)
        
        try:
            from ctk_scrollable_dropdown import CTkScrollableDropdown
            CTkScrollableDropdown(hiragana_combo, values=available_hiragana, justify="left", button_color="transparent")
        except ImportError:
            hiragana_combo.configure(values=available_hiragana)
        
        self.jpnSerialVar = ctk.StringVar(value="12-34")
        ctk.CTkLabel(row2, text="Serial:").pack(side="left", padx=5)
        ctk.CTkEntry(row2, textvariable=self.jpnSerialVar, width=100).pack(side="left", padx=5)
        
        self.row3 = ctk.CTkFrame(self.jpnControlsFrame, fg_color="transparent")
        self.row3.pack(fill="x", pady=5)
        self.jpnColorVar = ctk.StringVar(value="Green")
        ctk.CTkLabel(self.row3, text="Text Color:").pack(side="left", padx=5)
        ctk.CTkOptionMenu(self.row3, variable=self.jpnColorVar, values=["Green", "Black"]).pack(side="left", padx=5)
        
        self.jpnPlateTypeVar.trace_add("write", self.onTextChange)
        self.jpnRegionVar.trace_add("write", self.onTextChange)
        self.jpnClassVar.trace_add("write", self.onTextChange)
        self.jpnHiraganaVar.trace_add("write", self.onTextChange)
        self.jpnSerialVar.trace_add("write", self.onTextChange)
        self.jpnColorVar.trace_add("write", self.onTextChange)

        self.showTagsVar = ctk.BooleanVar(value=True)
        self.tagsSwitch = ctk.CTkSwitch(
            controlsFrame, 
            text="Show Registration Tags", 
            variable=self.showTagsVar, 
            command=self.updateEditorPreview, 
            button_color=COLORS["accent_primary"]
        )
        self.tagsSwitch.pack(anchor="w", padx=20, pady=(10, 0))

        self.outlineFrame = ctk.CTkFrame(controlsFrame, fg_color="transparent")
        self.showOutlineVar = ctk.BooleanVar(value=True)
        self.customOutlineColorVar = ctk.StringVar(value="")
        
        self.outlineSwitch = ctk.CTkSwitch(
            self.outlineFrame, 
            text="Outline", 
            variable=self.showOutlineVar, 
            command=self.updateEditorPreview, 
            button_color=COLORS["accent_primary"]
        )
        self.outlineSwitch.pack(side="left")
        
        def pickOutlineColor():
            from tkinter import colorchooser
            color_code = colorchooser.askcolor(title ="Choose color")
            if color_code and color_code[1]:
                self.customOutlineColorVar.set(color_code[1])
                self.updateEditorPreview()
                
        self.outlineColorBtn = ctk.CTkButton(self.outlineFrame, text="Color", width=50, command=pickOutlineColor)
        self.outlineColorBtn.pack(side="left", padx=10)
        
        def resetOutlineColor():
            self.customOutlineColorVar.set("")
            self.updateEditorPreview()
            
        self.outlineResetBtn = ctk.CTkButton(self.outlineFrame, text="Reset", width=50, command=resetOutlineColor)
        self.outlineResetBtn.pack(side="left")

        self.showCobbVar = ctk.BooleanVar(value=True)
        self.cobbSwitch = ctk.CTkSwitch(
            controlsFrame, 
            text="COBB Logo", 
            variable=self.showCobbVar, 
            command=self.updateEditorPreview, 
            button_color=COLORS["accent_primary"]
        )

        self.editorPreviewLabel = ctk.CTkLabel(self.editorPage, text="Loading Preview...")
        self.editorPreviewLabel.pack(pady=20)

        self.btnSaveCustom = ctk.CTkButton(
            self.editorPage, 
            text=" DOWNLOAD PLATE", 
            image=self.loadIcon("download.png", size=20), 
            fg_color=COLORS["accent_secondary"], 
            height=50, 
            width=1200,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.saveCustomPlate
        )
        self.btnSaveCustom.pack(fill="x", padx=0, pady=(20, 10))

        secondRowFrame = ctk.CTkFrame(self.editorPage, fg_color="transparent")
        secondRowFrame.pack(fill="x", padx=0, pady=(0, 10))

        self.btnSendToMm = ctk.CTkButton(
            secondRowFrame, 
            text=" OPEN IN 3D MAP MAKER", 
            image=self.loadIcon("map.png", size=20), 
            fg_color=COLORS["accent_primary"], 
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.sendToMapMaker
        )
        self.btnSendToMm.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btnSendRecViewport = ctk.CTkButton(
            secondRowFrame, 
            text=" SEND TO VIEWPORT", 
            image=self.loadIcon("view.png", size=20), 
            fg_color=COLORS["accent_primary"], 
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.sendRecommendedToViewport
        )
        self.btnSendRecViewport.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.recMapFrame = ctk.CTkFrame(self.editorPage, fg_color="transparent")
        self.recMapFrame.pack(fill="x", padx=0, pady=(0, 20))

        self.btnDownloadRec = ctk.CTkButton(
            self.recMapFrame, 
            text=" DOWNLOAD RECOMMENDED MAP", 
            image=self.loadIcon("download.png", size=20), 
            fg_color=COLORS["accent_success"], 
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.downloadRecommendedMap
        )
        self.btnDownloadRec.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btnSendRecComp = ctk.CTkButton(
            self.recMapFrame, 
            text=" SEND REC. TO COMPILER", 
            image=self.loadIcon("package-plus.png", size=20), 
            fg_color=COLORS["accent_success"], 
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.sendRecommendedToCompiler
        )
        self.btnSendRecComp.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.editorActionInfo = ctk.CTkLabel(
            self.editorPage, 
            text="", 
            font=ctk.CTkFont(size=11, slant="italic"), 
            text_color=COLORS["text_muted"]
        )
        self.editorActionInfo.pack(pady=(2, 10))

        self.btnSaveCustom.bind("<Enter>", lambda e: self.editorActionInfo.configure(text="Save the 2D plate image directly to your computer.  "))
        self.btnSaveCustom.bind("<Leave>", lambda e: self.editorActionInfo.configure(text=""))

        self.btnSendToMm.bind("<Enter>", lambda e: self.editorActionInfo.configure(text="Send this plate to the Map Maker to generate a customized height map.  "))
        self.btnSendToMm.bind("<Leave>", lambda e: self.editorActionInfo.configure(text=""))

        self.btnDownloadRec.bind("<Enter>", lambda e: self.editorActionInfo.configure(text="'Recommended' just means it generates a preset heightmap that only applies to the text.  "))
        self.btnDownloadRec.bind("<Leave>", lambda e: self.editorActionInfo.configure(text=""))

        self.btnSendRecComp.bind("<Enter>", lambda e: self.editorActionInfo.configure(text="Sends both the plate and the recommended 3D map straight to the Compiler.  "))
        self.btnSendRecComp.bind("<Leave>", lambda e: self.editorActionInfo.configure(text=""))

        self.btnSendRecViewport.bind("<Enter>", lambda e: self.editorActionInfo.configure(text="Sends both the plate and the recommended 3D map to the 3D Viewport.  "))
        self.btnSendRecViewport.bind("<Leave>", lambda e: self.editorActionInfo.configure(text=""))

        self.onStateChange(self.stateVar.get())

    def onStateChange(self, choice):
        config = PLATE_TEMPLATES.get(choice)
        if not config: return

        if config.get("is_japan"):
            self.charLimitLabel.pack_forget()
            self.textEntry.pack_forget()
            self.jpnControlsFrame.pack(fill="x", padx=20, pady=(0, 10))
        else:
            self.jpnControlsFrame.pack_forget()
            charLimit = 10 if "EU" in choice else 8
            if hasattr(self, 'charLimitLabel'):
                self.charLimitLabel.configure(text=f"Plate Text (Max {charLimit} chars):")
                self.charLimitLabel.pack(anchor="w", padx=20, pady=(15, 5))
            if hasattr(self, 'textEntry'):
                self.textEntry.pack(fill="x", padx=20, pady=(0, 10))

        self.tagsSwitch.pack_forget()
        if hasattr(self, "outlineFrame"):
            self.outlineFrame.pack_forget()
        elif hasattr(self, "outlineSwitch"):
            self.outlineSwitch.pack_forget()
        self.cobbSwitch.pack_forget()

        if config.get("has_tags_option", True):
            self.showTagsVar.set(True)
            self.tagsSwitch.pack(anchor="w", padx=20, pady=(10, 0))
        else:
            self.showTagsVar.set(False) 

        if config.get("has_outline_option"):
            self.showOutlineVar.set(True)
            if hasattr(self, "outlineFrame"):
                self.outlineFrame.pack(anchor="w", padx=20, pady=(10, 0))
                if config.get("is_japan"):
                    self.outlineColorBtn.pack(side="left", padx=10)
                    self.outlineResetBtn.pack(side="left")
                else:
                    self.outlineColorBtn.pack_forget()
                    self.outlineResetBtn.pack_forget()
            else:
                self.outlineSwitch.pack(anchor="w", padx=20, pady=(10, 0))
        else:
            self.showOutlineVar.set(False)

        if config.get("has_cobb_option"):
            self.showCobbVar.set(True)
            self.cobbSwitch.pack(anchor="w", padx=20, pady=(10, 0))
        else:
            self.showCobbVar.set(False)
            
        self.updateEditorPreview()

    def onTextChange(self, *args):
        text = self.plateTextVar.get().upper()
        selectedState = self.stateVar.get()
        
        charLimit = 10 if "EU" in selectedState else 8
        
        if len(text) > charLimit:
            text = text[:charLimit]
            
        self.plateTextVar.set(text)
        
        if hasattr(self, 'RenderJob') and self.RenderJob:
            self.after_cancel(self.RenderJob)
        self.RenderJob = self.after(300, self.updateEditorPreview)

    def generatePlateImage(self):
        state = self.stateVar.get()
        text = self.plateTextVar.get()
        config = PLATE_TEMPLATES.get(state)
        
        if not config:
            return None

        hasTags = getattr(self, "showTagsVar", ctk.BooleanVar(value=True)).get()
        hasOutline = config.get("has_outline_option") and getattr(self, "showOutlineVar", ctk.BooleanVar(value=False)).get()

        if hasTags and hasOutline:
            imageKey = "image_tags_outline"
        elif hasTags and not hasOutline:
            imageKey = "image_tags"
        elif not hasTags and hasOutline:
            imageKey = "image_no_tags_outline"
        else:
            imageKey = "image_no_tags"

        if config.get("is_japan"):
            try:
                baseImg = Image.new("RGBA", (1440, 720), "white")
                return self.compositeJapanesePlate(baseImg)
            except Exception as e:
                print(f"Render error for japan plate: {e}")
                return None
                
        imagePath = resourcePath(config.get(imageKey))
        
        if not imagePath or not os.path.exists(imagePath):
            return None

        try:
            baseImg = Image.open(imagePath).convert("RGBA")

            if config.get("has_cobb_option") and getattr(self, "showCobbVar", ctk.BooleanVar(value=False)).get():
                cobbPath = resourcePath(config.get("cobb_overlay"))
                if cobbPath and os.path.exists(cobbPath):
                    cobbImg = Image.open(cobbPath).convert("RGBA")
                    coords = config.get("cobb_coords", (0, 0))
                    baseImg.paste(cobbImg, coords, cobbImg)

            draw = ImageDraw.Draw(baseImg)
            
            fontPath = resourcePath(config["font_file"])
            try:
                font = ImageFont.truetype(fontPath, config["font_size"])
            except IOError:
                font = ImageFont.load_default()
                print("Custom font not found. Using default.")

            left, top, right, bottom = font.getbbox(text)
            textWidth = right - left
            textHeight = bottom - top
            
            x = config["coords"][0] - (textWidth / 2)
            y = config["coords"][1] - (textHeight / 2)

            draw.text((x, y), text, font=font, fill=config["text_color"])
            return baseImg
            
        except Exception as e:
            print(f"Render error: {e}")
            return None

    def compositeJapanesePlate(self, baseImg, normal_mode=False):
        try:
            try:
                import svglib
            except ImportError:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "svglib", "reportlab", "cssselect2", "rlpycairo"])
                import svglib

            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPM
            import io
            
            if not hasattr(PlateMakerApp, "svg_cache"):
                PlateMakerApp.svg_cache = {}
            
            plate_type = getattr(self, "jpnPlateTypeVar", None)
            plate_type_val = plate_type.get() if plate_type else "Private Vehicle"
            
            if normal_mode:
                other_mask = Image.new("RGBA", (1440, 720), (0,0,0,255))
                serial_mask = Image.new("RGBA", (1440, 720), (0,0,0,255))
                fill_color = "#FFFFFF"
                bg_color = None
            else:
                if plate_type_val == "Commercial Vehicle":
                    bg_color = "#276E4B"
                    fill_color = "#FFFFFF"
                elif plate_type_val == "Private Kei":
                    bg_color = "#F7D23E"
                    fill_color = "#151515"
                elif plate_type_val == "Commercial Kei":
                    bg_color = "#151515"
                    fill_color = "#F7D23E"
                elif plate_type_val == "Temporary":
                    bg_color = None
                    fill_color = "#151515"
                else:
                    bg_color = "#FFFFFF"
                    if hasattr(self, "jpnColorVar") and self.jpnColorVar.get() == "Black":
                        fill_color = "#151515"
                    else:
                        fill_color = "#00552E"

            if not normal_mode:
                if bg_color:
                    baseImg.paste(Image.new("RGBA", baseImg.size, bg_color), (0,0))
                else:
                    temp_bg_path = resourcePath("jpn_temp_bg.png")
                    if os.path.exists(temp_bg_path):
                        temp_bg = Image.open(temp_bg_path).convert("RGBA")
                        temp_bg = temp_bg.resize((1440, 720), Image.Resampling.LANCZOS)
                        baseImg.paste(temp_bg, (0, 0), temp_bg)
            
            def get_svg_mask(svg_path, target_height):
                if not os.path.exists(svg_path): return None
                cache_key = (svg_path, target_height, "mask")
                if cache_key in PlateMakerApp.svg_cache:
                    return PlateMakerApp.svg_cache[cache_key].copy()
                try:
                    drawing = svg2rlg(svg_path)
                    bio = io.BytesIO()
                    renderPM.drawToFile(drawing, bio, fmt="PNG", dpi=300)
                    bio.seek(0)
                    img = Image.open(bio).convert("RGBA")
                    aspect = img.width / img.height
                    img = img.resize((int(target_height * aspect), target_height), Image.Resampling.LANCZOS)
                    from PIL import ImageOps
                    gray = img.convert('L')
                    inverted = ImageOps.invert(gray)
                    PlateMakerApp.svg_cache[cache_key] = inverted
                    return inverted.copy()
                except Exception as e:
                    return None
                    
            def render_svg(svg_path, target_height):
                mask = get_svg_mask(svg_path, target_height)
                if not mask: return None
                colored = Image.new("RGBA", mask.size, fill_color)
                return Image.composite(colored, Image.new("RGBA", mask.size, (0,0,0,0)), mask)
            
            asset_dir = resourcePath("japanLicensePlate_Generator_assets")
            region = self.jpnRegionVar.get()
            cls_code = self.jpnClassVar.get()
            hiragana = self.jpnHiraganaVar.get()
            serial = self.jpnSerialVar.get()
            
            prefecture_path = None
            for root, dirs, files in os.walk(os.path.join(asset_dir, "issueOffice")):
                for file in files:
                    if file.lower() == f"{region.lower()}.png":
                        prefecture_path = os.path.join(root, file)
                        break
                if prefecture_path: break
                
            if prefecture_path:
                prefH = 185
                pref_cache_key = (prefecture_path, prefH, "mask")
                if pref_cache_key in PlateMakerApp.svg_cache:
                    mask_a = PlateMakerApp.svg_cache[pref_cache_key].copy()
                else:
                    rawPref = Image.open(prefecture_path).convert("RGBA")
                    prefAspect = rawPref.width / rawPref.height
                    prefW = int(prefH * prefAspect)
                    rawPref = rawPref.resize((prefW, prefH), Image.Resampling.LANCZOS)
                    
                    corner = rawPref.getpixel((0,0))
                    if corner[0] > 240 and corner[1] > 240 and corner[2] > 240 and corner[3] > 240:
                        from PIL import ImageOps
                        gray = rawPref.convert('L')
                        mask_a = ImageOps.invert(gray)
                    else:
                        _, _, _, mask_a = rawPref.split()
                        
                    PlateMakerApp.svg_cache[pref_cache_key] = mask_a
                    mask_a = mask_a.copy()
                
                coloredPref = Image.new("RGBA", mask_a.size, fill_color)
                prefImg = Image.composite(coloredPref, Image.new("RGBA", mask_a.size, (0,0,0,0)), mask_a)
                prefW = prefImg.width
                startX = 710 - prefW
                if normal_mode:
                    other_mask.paste(prefImg, (startX, 60), prefImg)
                else:
                    baseImg.paste(prefImg, (startX, 60), prefImg)

            clsX = 740
            for char in cls_code:
                if char == ' ':
                    clsX += 110
                    continue
                svg_path = os.path.join(asset_dir, "num", f"num_{char}.svg")
                charImg = render_svg(svg_path, 185)
                if charImg:
                    slot_width = 110
                    pasteX = clsX + (slot_width - charImg.width) // 2
                    if normal_mode:
                        other_mask.paste(charImg, (pasteX, 60), charImg)
                    else:
                        baseImg.paste(charImg, (pasteX, 60), charImg)
                    clsX += slot_width

            hiragana_path = os.path.join(asset_dir, "hiragana", f"hiragana_{hiragana}.svg")
            hirImg = render_svg(hiragana_path, 150)
            if hirImg:
                if normal_mode:
                    other_mask.paste(hirImg, (100, 430), hirImg)
                else:
                    baseImg.paste(hirImg, (100, 430), hirImg)

            currentX = 320
            serial_slot_width = 195
            serial_gap = 15
            for char in serial:
                if char == ' ': 
                    currentX += serial_slot_width + serial_gap
                    continue
                
                char_name = char
                svg_path = os.path.join(asset_dir, "num", f"num_{char_name}.svg")
                
                is_dash = (char == '-')
                target_h = 310 if is_dash else 345
                charImg = render_svg(svg_path, target_h)
                if charImg:
                    slot_w = 120 if is_dash else serial_slot_width
                    pasteX = currentX + (slot_w - charImg.width) // 2
                    pasteY = 320 + (345 - target_h) // 2
                    if normal_mode:
                        serial_mask.paste(charImg, (pasteX, pasteY), charImg)
                    else:
                        baseImg.paste(charImg, (pasteX, pasteY), charImg)
                
                    currentX += slot_w + serial_gap

            if not normal_mode and hasattr(self, "showOutlineVar") and self.showOutlineVar.get():
                outline_path = resourcePath("jpn_outline_asset.png")
                if os.path.exists(outline_path):
                    outline_img = Image.open(outline_path).convert("RGBA")
                    outline_img = outline_img.resize((1440, 720), Image.Resampling.LANCZOS)
                    
                    outline_color = fill_color
                    if hasattr(self, "customOutlineColorVar") and self.customOutlineColorVar.get():
                        outline_color = self.customOutlineColorVar.get()
                        
                    r, g, b, mask_a = outline_img.split()
                    colored_outline = Image.new("RGBA", mask_a.size, outline_color)
                    outline_img = Image.composite(colored_outline, Image.new("RGBA", mask_a.size, (0,0,0,0)), mask_a)
                    
                    baseImg.paste(outline_img, (0, 0), outline_img)

            if normal_mode:
                return serial_mask, other_mask

            return baseImg
        except Exception as e:
            print(f"Japan Plate Compositing failed: {e}")
            return baseImg

    def updateEditorPreview(self, *args):
        img = self.generatePlateImage()
        if img:
            w, h = img.size
            aspect = h / w
            previewW = 400
            previewH = int(previewW * aspect)
            
            ctkImg = ctk.CTkImage(light_image=img, dark_image=img, size=(previewW, previewH))
            self.editorPreviewLabel.configure(image=ctkImg, text="")
        else:
            self.editorPreviewLabel.configure(text="Missing template image.", image=None)

    def setupViewportPage(self):
        self.viewportPage.grid_rowconfigure(2, weight=1)
        self.viewportPage.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self.viewportPage, text="3D Viewport", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"), text_color=COLORS["text_primary"])
        header.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        controlsFrame = ctk.CTkFrame(self.viewportPage, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        controlsFrame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 5))

        topRow = ctk.CTkFrame(controlsFrame, fg_color="transparent")
        topRow.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(topRow, text="PLATE MODEL:", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_muted"]).pack(side="left", padx=(0, 10))

        self.viewportRegionVar = ctk.StringVar(value="US & MX")
        self.viewportRegionSelector = ctk.CTkSegmentedButton(
            topRow, values=["US & MX", "EU & UK", "FH6 (JPN)"],
            variable=self.viewportRegionVar, fg_color=COLORS["bg_card"],
            selected_color=COLORS["accent_primary"], text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=12, weight="bold"), height=32,
            command=self.onViewportRegionChange
        )
        self.viewportRegionSelector.pack(side="left", padx=(0, 15))

        self.viewportModelLabel = None

        self.btnResetCam = ctk.CTkButton(
            topRow,
            text=" Reset Camera",
            image=self.loadIcon("undo.png", size=16),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["border"],
            height=32,
            width=120,
            command=self.resetViewportCamera
        )
        self.btnResetCam.pack(side="right")

        bottomRow = ctk.CTkFrame(controlsFrame, fg_color="transparent")
        bottomRow.pack(fill="x", padx=15, pady=(0, 10))

        self.btnLoadTexture = ctk.CTkButton(
            bottomRow,
            text=" Load Texture",
            image=self.loadIcon("image_small.png", size=16),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["border"],
            height=32,
            command=self.loadViewportTexture
        )
        self.btnLoadTexture.pack(side="left", padx=(0, 10))

        self.btnLoadNormal = ctk.CTkButton(
            bottomRow,
            text=" Load Normal Map",
            image=self.loadIcon("map.png", size=16),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["border"],
            height=32,
            command=self.loadViewportNormal
        )
        self.btnLoadNormal.pack(side="left", padx=(0, 10))

        self.viewportTextureLabel = None
        self.viewportNormalLabel = None

        self.viewportSwitchesFrame = ctk.CTkFrame(bottomRow, fg_color="transparent")
        
        self.viewportSealVar = ctk.BooleanVar(value=True)
        self.viewportDeleteBracketToggle = ctk.CTkSwitch(
            self.viewportSwitchesFrame, text="Show Seal", variable=self.viewportSealVar,
            button_color=COLORS["accent_primary"], font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"], command=self.updateViewportTextureRules
        )
        self.viewportDeleteBracketToggle.pack(side="left", padx=(0, 15))

        self.viewportScrewVar = ctk.BooleanVar(value=True)
        self.viewportDeleteScrewToggle = ctk.CTkSwitch(
            self.viewportSwitchesFrame, text="Show Plate Screw", variable=self.viewportScrewVar,
            button_color=COLORS["accent_primary"], font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"], command=self.updateViewportTextureRules
        )
        self.viewportDeleteScrewToggle.pack(side="left")

        self.liveReloadVar = ctk.BooleanVar(value=True)
        
        self.currentDiffPath = None
        self.currentNrmlPath = None
        self.lastDiffMtime = 0
        self.lastNrmlMtime = 0

        viewportContainer = ctk.CTkFrame(self.viewportPage, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        viewportContainer.grid(row=2, column=0, sticky="nsew", padx=15, pady=(5, 5))
        viewportContainer.grid_rowconfigure(0, weight=1)
        viewportContainer.grid_columnconfigure(0, weight=1)

        self.viewport3d = None
        self.viewportFallbackLabel = None

        if HAS_OPENGL:
            try:
                self.viewport3d = Viewport3D(viewportContainer, width=600, height=400)
                self.viewport3d.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
            except Exception:
                self.viewport3d = None

        if self.viewport3d is None:
            self.viewportFallbackLabel = ctk.CTkLabel(
                viewportContainer,
                text="3D Viewport requires PyOpenGL and pyopengltk.\nInstall with: pip install PyOpenGL pyopengltk",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_muted"]
            )
            self.viewportFallbackLabel.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        hintLabel = ctk.CTkLabel(self.viewportPage, text="Left-click: Orbit  |  Right-click: Pan  |  Scroll: Zoom  |  Double-click: Recenter", font=ctk.CTkFont(size=10), text_color=COLORS["text_muted"])
        hintLabel.grid(row=3, column=0, sticky="w", padx=20, pady=(2, 10))

        self.after(500, lambda: self.onViewportRegionChange("US & MX"))
        self.pollLiveReload()

    def _loadJpnPerMaterialSwatchbins(self, parsed, modelDir):
        """For FH6 JPN plates, load per-mesh swatchbin textures for the seal and screw.
        The material entry names embedded in the modelbin contain the swatchbin filenames.
        These files live in the same directory as PlateJPN.modelbin.
        We scan the mesh groups, find any material whose name contains a swatchbin reference,
        and load the first matching diff swatchbin as the diffuse texture for that mesh group.
        The base plate diff/nrml are left to whatever the user has loaded manually.
        """
        if not self.viewport3d:
            return

        materialNames = getattr(parsed, "materialNames", [])
        # Collect unique non-base material entries that reference swatchbins
        # and load the first diff one we find as a secondary texture hint.
        # Since the viewport renders one texture across the whole model, we apply
        # the seal/screw diffuse only when the base plate has no user texture loaded,
        # otherwise we leave the user's texture in place.
        for matId, matName in enumerate(materialNames):
            if not matName:
                continue
            # Look for a swatchbin file with this exact name in the model directory
            swatchPath = os.path.join(modelDir, matName)
            if os.path.isfile(swatchPath):
                try:
                    img = Image.open(swatchPath)
                    if "diff" in matName.lower():
                        # Only apply if no user diffuse is already loaded
                        if not self.viewport3d.hasDiffuse:
                            self.viewport3d.setDiffuseTexture(img)
                            self._setViewportTextureStatus(f"Auto: {self._shortViewportStatusName(swatchPath)}")
                    elif "nrml" in matName.lower():
                        if not self.viewport3d.hasNormal:
                            self.viewport3d.setNormalTexture(img)
                except Exception:
                    pass

    def onViewportRegionChange(self, region):
        if region == "FH6 (JPN)":
            if hasattr(self, "viewportSwitchesFrame") and not self.viewportSwitchesFrame.winfo_manager():
                self.viewportSwitchesFrame.pack(side="right", padx=(0, 0))
        else:
            if hasattr(self, "viewportSwitchesFrame"): self.viewportSwitchesFrame.pack_forget()
        self.loadViewportPlate(region)

    def _shortViewportStatusName(self, path, maxChars=38):
        name = os.path.basename(path)
        if len(name) <= maxChars:
            return name
        keep = (maxChars - 3) // 2
        return f"{name[:keep]}...{name[-keep:]}"

    def _setViewportTextureStatus(self, text):
        if self.viewport3d:
            self.viewport3d.setStatusText(textureText=text)

    def _setViewportNormalStatus(self, text):
        if self.viewport3d:
            self.viewport3d.setStatusText(normalText=text)

    def loadViewportPlate(self, region):
        if not self.viewport3d:
            return

        if region == "US & MX":
            filename = "PlateUS.modelbin"
            skipCount = 2
            materialIds = None
        elif region == "FH6 (JPN)":
            filename = "PlateJPN.modelbin"
            skipCount = 0
            materialIds = None
        else:
            filename = "PlateEU.modelbin"
            skipCount = 2
            materialIds = None

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if not os.path.isfile(path):
            return

        def process():
            try:
                parsed = parseModelbin(path, skipMeshes=skipCount, onlyMaterialIds=materialIds)
                self.lastViewportParsed = parsed
                def applyModel():
                    self.updateViewportTextureRules()
                    self.viewport3d.uploadModel(parsed)

                    # For FH6 JPN: auto-load swatchbins referenced in material entries
                    # for meshes that carry their own textures (seal, screw, etc.)
                    if region == "FH6 (JPN)":
                        modelDir = os.path.dirname(path)
                        self._loadJpnPerMaterialSwatchbins(parsed, modelDir)

                self.uiQueue.put(applyModel)
            except Exception as e:
                self.uiQueue.put(lambda err=e: messagebox.showerror("Model Error", f"Failed to parse {filename}:\n{err}"))

        threading.Thread(target=process, daemon=True).start()

    def updateViewportTextureRules(self, *args):
        if not self.viewport3d:
            return
            
        region = self.viewportRegionVar.get()
        if region != "FH6 (JPN)":
            self.viewport3d.setMaterialTextureRules()
            return
            
        deleteSeal = not getattr(self, "viewportSealVar", ctk.BooleanVar(value=True)).get()
        deleteScrew = not getattr(self, "viewportScrewVar", ctk.BooleanVar(value=True)).get()
        
        hidden = [1] # atlas
        textured = [2] # base plate
        
        hidden_meshes = ["shadow"]
        if deleteSeal:
            hidden_meshes.extend(["bracket", "seal"])
        if deleteScrew:
            hidden_meshes.append("screw")
        
        if hasattr(self, "lastViewportParsed") and hasattr(self.lastViewportParsed, "materialNames"):
            for idx, name in enumerate(self.lastViewportParsed.materialNames):
                if not name: continue
                name_lower = name.lower()
                if deleteSeal and ("seal" in name_lower or "bracket" in name_lower):
                    hidden.append(idx)
                if deleteScrew and "screw" in name_lower:
                    hidden.append(idx)
                    
        self.viewport3d.setMaterialTextureRules(
            hiddenMaterialIds=hidden,
            texturedMaterialIds=textured,
            hiddenMeshNames=hidden_meshes
        )

    def loadViewportTexture(self):
        if not self.viewport3d:
            messagebox.showerror("Error", "3D viewport is not available.")
            return

        initial = self.lastDirs.get("img", "/")
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.psd"), ("All files", "*.*")],
            initialdir=initial,
            title="Select Texture Image"
        )
        if not path:
            return

        try:
            img = Image.open(path)
            self.viewport3d.setDiffuseTexture(img)
            self._setViewportTextureStatus(f"Texture: {self._shortViewportStatusName(path)}")
            self.currentDiffPath = path
            self.lastDiffMtime = os.path.getmtime(path)
        except Exception as e:
            messagebox.showerror("Texture Error", f"Failed to load texture:\n{e}")

    def loadViewportNormal(self):
        if not self.viewport3d:
            messagebox.showerror("Error", "3D viewport is not available.")
            return

        initial = self.lastDirs.get("nrml", "/")
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.psd"), ("All files", "*.*")],
            initialdir=initial,
            title="Select Normal Map Image"
        )
        if not path:
            return

        try:
            img = Image.open(path)
            self.viewport3d.setNormalTexture(img)
            self._setViewportNormalStatus(f"Normal: {self._shortViewportStatusName(path)}")
            self.currentNrmlPath = path
            self.lastNrmlMtime = os.path.getmtime(path)
        except Exception as e:
            messagebox.showerror("Texture Error", f"Failed to load normal map:\n{e}")

    def sendToPreview(self, imgPath, isNormal=False):
        if not self.viewport3d:
            return
        if not imgPath or not os.path.isfile(imgPath):
            return
        try:
            img = Image.open(imgPath)
            if isNormal:
                self.viewport3d.setNormalTexture(img)
                self._setViewportNormalStatus(f"Normal: {self._shortViewportStatusName(imgPath)}")
                self.currentNrmlPath = imgPath
                self.lastNrmlMtime = os.path.getmtime(imgPath)
            else:
                self.viewport3d.setDiffuseTexture(img)
                self._setViewportTextureStatus(f"Texture: {self._shortViewportStatusName(imgPath)}")
                self.currentDiffPath = imgPath
                self.lastDiffMtime = os.path.getmtime(imgPath)
        except Exception:
            pass

    def pollLiveReload(self):
        if hasattr(self, 'liveReloadVar') and self.liveReloadVar.get():
            try:
                if self.currentDiffPath and os.path.exists(self.currentDiffPath):
                    mtime = os.path.getmtime(self.currentDiffPath)
                    if mtime != self.lastDiffMtime:
                        self.lastDiffMtime = mtime
                        img = Image.open(self.currentDiffPath)
                        if self.viewport3d:
                            self.viewport3d.setDiffuseTexture(img)
                            
                if self.currentNrmlPath and os.path.exists(self.currentNrmlPath):
                    mtime = os.path.getmtime(self.currentNrmlPath)
                    if mtime != self.lastNrmlMtime:
                        self.lastNrmlMtime = mtime
                        img = Image.open(self.currentNrmlPath)
                        if self.viewport3d:
                            self.viewport3d.setNormalTexture(img)
            except Exception:
                pass
                
        self.after(1000, self.pollLiveReload)

    def resetViewportCamera(self):
        if self.viewport3d:
            self.viewport3d.resetCamera()


    def saveCustomPlate(self):
        img = self.generatePlateImage()
        if not img:
            messagebox.showerror("Error", "Could not generate plate.")
            return
            
        initialDir = self.lastDirs.get("editor_out", "/")
        savePath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            initialdir=initialDir,
            initialfile=f"{self.plateTextVar.get()}_plate.png"
        )
        
        if savePath:
            self.lastDirs["editor_out"] = os.path.dirname(savePath)
            self.saveConfig(silent=True)
            
            img = img.resize((4000, 2000), Image.Resampling.LANCZOS)
            img.save(savePath, format="PNG")
            messagebox.showinfo("Success", f"Plate saved to:\n{savePath}")

    def sendToMapMaker(self):
        img = self.generatePlateImage()
        if not img:
            messagebox.showerror("Error", "Could not generate plate.")
            return

        tempPath = os.path.normpath(os.path.join(tempfile.gettempdir(), "designer_transfer.png"))
        img = img.resize((4000, 2000), Image.Resampling.LANCZOS)
        img.save(tempPath)

        self.mmDropZone.pathEntry.delete(0, "end")
        self.mmDropZone.pathEntry.insert(0, tempPath)
        
        self.mmDropZone.updatePreview(tempPath)
        self.mmDropZone.configure(border_color=COLORS["accent_success"])

        self.loadPreviewImage(tempPath)
        self.showPage("map_maker")
        
        self.after(350, self.schedulePreviewUpdate)

    def downloadRecommendedMap(self):
        state = self.stateVar.get()
        text = self.plateTextVar.get()
        config = PLATE_TEMPLATES.get(state)
        
        if not config:
            return

        isEu = "EU" in state
        if isEu:
            strength, blur, direction = 7.0, 1.5, "Outward"
        else:
            strength, blur, direction = 8.0, 1.8, "Outward"

        imagePath = resourcePath(config.get("image_no_tags"))
        if not imagePath or not os.path.exists(imagePath):
            messagebox.showerror("Error", "Template not found.")
            return

        initialDir = self.lastDirs.get("editor_out", "/")
        savePath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            initialdir=initialDir,
            initialfile=f"{text}_3d_map.png"
        )
        
        if not savePath:
            return

        self.lastDirs["editor_out"] = os.path.dirname(savePath)
        self.saveConfig(silent=True)

        self.btnDownloadRec.configure(state="disabled", text="⏳ GENERATING MAP...")

        def process():
            try:
                baseImg = Image.open(imagePath)
                if config.get("is_japan"):
                    serial_mask, other_mask = self.compositeJapanesePlate(None, normal_mode=True)
                    serial_nrml = self.createNormalMapData(serial_mask, 10.0, 1.5, "Outward")
                    other_nrml = self.createNormalMapData(other_mask, 10.0, 1.2, "Outward")
                    
                    rad_serial = self.getDynamicBlurRadius(10.0, 1.5, baseImg.size[0])
                    if rad_serial > 0:
                        serial_nrml = serial_nrml.filter(ImageFilter.GaussianBlur(radius=rad_serial))
                    serial_nrml = serial_nrml.filter(ImageFilter.GaussianBlur(radius=2.5))

                    rad_other = self.getDynamicBlurRadius(10.0, 1.2, baseImg.size[0])
                    if rad_other > 0:
                        other_nrml = other_nrml.filter(ImageFilter.GaussianBlur(radius=rad_other))
                    other_nrml = other_nrml.filter(ImageFilter.GaussianBlur(radius=2.5))
                    
                    from PIL import ImageChops
                    flat = Image.new("RGB", other_nrml.size, (127, 127, 255))
                    diff = ImageChops.difference(other_nrml, flat)
                    mask = diff.convert("L").point(lambda p: 255 if p > 0 else 0)
                    nrmlMap = Image.composite(other_nrml, serial_nrml, mask)
                else:
                    textMapBase = Image.new("RGBA", baseImg.size, (0, 0, 0, 255))
                    draw = ImageDraw.Draw(textMapBase)
                    
                    fontPath = resourcePath(config["font_file"])
                    try:
                        font = ImageFont.truetype(fontPath, config["font_size"])
                    except IOError:
                        font = ImageFont.load_default()

                    left, top, right, bottom = font.getbbox(text)
                    textWidth = right - left
                    textHeight = bottom - top
                    
                    x = config["coords"][0] - (textWidth / 2)
                    y = config["coords"][1] - (textHeight / 2)

                    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

                    nrmlMap = self.createNormalMapData(textMapBase, strength, blur, direction)
                    
                    radius = self.getDynamicBlurRadius(strength, blur, baseImg.size[0])
                    if radius > 0:
                        nrmlMap = nrmlMap.filter(ImageFilter.GaussianBlur(radius=radius))
                    nrmlMap = nrmlMap.filter(ImageFilter.GaussianBlur(radius=5))
                
                nrmlMap.save(savePath, format="PNG")
                self.uiQueue.put(lambda: messagebox.showinfo("Success", f"Recommended 3D map saved to:\n{savePath}"))
                
            except Exception as e:
                self.uiQueue.put(lambda err=e: messagebox.showerror("Error", f"Could not generate recommended map: {err}"))
            finally:
                self.uiQueue.put(lambda: self.btnDownloadRec.configure(state="normal", text=" DOWNLOAD RECOMMENDED MAP"))

        threading.Thread(target=process, daemon=True).start()

    def sendRecommendedToCompiler(self):
        self._sendRecommendedTo("compiler")

    def sendRecommendedToViewport(self):
        self._sendRecommendedTo("viewport")

    def _sendRecommendedTo(self, target):
        btn = self.btnSendRecComp if target == "compiler" else self.btnSendRecViewport
        btn.configure(state="disabled", text="⏳ PREPARING...")
        def process():
            try:
                img = self.generatePlateImage()
                if not img:
                    self.uiQueue.put(lambda: messagebox.showerror("Error", "Could not generate plate."))
                    return
                state = self.stateVar.get()
                text = self.plateTextVar.get()
                config = PLATE_TEMPLATES.get(state)
                if not config: return
                isEu = "EU" in state
                strength, blur, direction = (7.0, 1.5, "Outward") if isEu else (8.0, 1.8, "Outward")
                imagePath = resourcePath(config.get("image_no_tags"))
                if not imagePath or not os.path.exists(imagePath):
                    self.uiQueue.put(lambda: messagebox.showerror("Error", "Template not found."))
                    return
                baseImg = Image.open(imagePath)
                if config.get("is_japan"):
                    serial_mask, other_mask = self.compositeJapanesePlate(None, normal_mode=True)
                    serial_nrml = self.createNormalMapData(serial_mask, 10.0, 1.5, "Outward")
                    other_nrml = self.createNormalMapData(other_mask, 10.0, 1.2, "Outward")
                    
                    rad_serial = self.getDynamicBlurRadius(10.0, 1.5, baseImg.size[0])
                    if rad_serial > 0:
                        serial_nrml = serial_nrml.filter(ImageFilter.GaussianBlur(radius=rad_serial))
                    serial_nrml = serial_nrml.filter(ImageFilter.GaussianBlur(radius=2.5))

                    rad_other = self.getDynamicBlurRadius(10.0, 1.2, baseImg.size[0])
                    if rad_other > 0:
                        other_nrml = other_nrml.filter(ImageFilter.GaussianBlur(radius=rad_other))
                    other_nrml = other_nrml.filter(ImageFilter.GaussianBlur(radius=2.5))
                    
                    from PIL import ImageChops
                    flat = Image.new("RGB", other_nrml.size, (127, 127, 255))
                    diff = ImageChops.difference(other_nrml, flat)
                    mask = diff.convert("L").point(lambda p: 255 if p > 0 else 0)
                    nrmlMap = Image.composite(other_nrml, serial_nrml, mask)
                else:
                    textMapBase = Image.new("RGBA", baseImg.size, (0, 0, 0, 255))
                    draw = ImageDraw.Draw(textMapBase)
                    fontPath = resourcePath(config["font_file"])
                    try:
                        font = ImageFont.truetype(fontPath, config["font_size"])
                    except IOError:
                        font = ImageFont.load_default()
                    left, top, right, bottom = font.getbbox(text)
                    textWidth, textHeight = right - left, bottom - top
                    x, y = config["coords"][0] - (textWidth / 2), config["coords"][1] - (textHeight / 2)
                    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
                    nrmlMap = self.createNormalMapData(textMapBase, strength, blur, direction)
                    radius = self.getDynamicBlurRadius(strength, blur, baseImg.size[0])
                    if radius > 0:
                        nrmlMap = nrmlMap.filter(ImageFilter.GaussianBlur(radius=radius))
                    nrmlMap = nrmlMap.filter(ImageFilter.GaussianBlur(radius=5))
                tempImgPath = os.path.normpath(os.path.join(tempfile.gettempdir(), "designer_img.png"))
                tempNrmlPath = os.path.normpath(os.path.join(tempfile.gettempdir(), "designer_rec_map.png"))
                img.save(tempImgPath)
                nrmlMap.save(tempNrmlPath)
                def updateUi():
                    if target == "compiler":
                        if config.get("is_japan"):
                            targetRegion = "FH6 (JPN)"
                        else:
                            ratio = img.size[0] / img.size[1]
                            targetRegion = "EU & UK" if ratio > 3.0 else "US & MX"
                        self.regionVar.set(targetRegion)
                        self.updateDropzoneRegions()
                        self.imageDropZone.pathEntry.delete(0, "end")
                        self.imageDropZone.pathEntry.insert(0, tempImgPath)
                        self.imageDropZone.updatePreview(tempImgPath)
                        self.nrmlDropZone.pathEntry.delete(0, "end")
                        self.nrmlDropZone.pathEntry.insert(0, tempNrmlPath)
                        self.nrmlDropZone.updatePreview(tempNrmlPath)
                        self.imageDropZone.configure(border_color=COLORS["accent_success"])
                        self.nrmlDropZone.configure(border_color=COLORS["accent_success"])
                        self.showPage("compiler")
                    elif target == "viewport":
                        if config.get("is_japan"):
                            targetRegion = "FH6 (JPN)"
                        else:
                            ratio = img.size[0] / img.size[1]
                            targetRegion = "EU & UK" if ratio > 3.0 else "US & MX"
                        self.viewportRegionVar.set(targetRegion)
                        self.onViewportRegionChange(targetRegion)
                        self.sendToPreview(tempImgPath, isNormal=False)
                        self.sendToPreview(tempNrmlPath, isNormal=True)
                        self.showPage("3d_preview")
                self.uiQueue.put(updateUi)
            except Exception as e:
                self.uiQueue.put(lambda err=e: messagebox.showerror("Error", f"Could not send recommended map: {err}"))
            finally:
                def resetBtn():
                    if target == "compiler":
                        self.btnSendRecComp.configure(state="normal", text=" SEND REC. TO COMPILER")
                    else:
                        self.btnSendRecViewport.configure(state="normal", text=" SEND REC. TO VIEWPORT")
                self.uiQueue.put(resetBtn)
        threading.Thread(target=process, daemon=True).start()

    def sendMapToCompiler(self):
        self._sendMapTo("compiler")

    def sendMapToPreview(self):
        self._sendMapTo("preview")

    def _sendMapTo(self, target):
        sourcePath = self.mmDropZone.getPath()
        if not sourcePath or not os.path.exists(sourcePath):
            messagebox.showerror("Error", "No source image found in Map Maker!")
            return
        self.mmStatusLabel.configure(text="⏳ Generating high-res map...", text_color=COLORS["accent_secondary"])
        mapPath = os.path.normpath(os.path.join(tempfile.gettempdir(), "generated_compiler_map.png"))
        def process():
            try:
                img = Image.open(sourcePath)
                bStr, bBlur, bDir = self.baseIntensity.get(), self.baseBlur.get(), self.baseExtrude.get()
                mStr, mBlur, mDir = self.maskIntensity.get(), self.maskBlur.get(), self.maskExtrude.get()
                maskPath = self.mmMaskDropZone.getPath() if self.advancedModeVar.get() else None
                baseMap = self.createNormalMapData(img, bStr, bBlur, bDir)
                if maskPath and os.path.exists(maskPath):
                    maskImg = Image.open(maskPath).convert('L').resize(baseMap.size)
                    maskMap = self.createNormalMapData(img, mStr, mBlur, mDir)
                    finalMap = Image.composite(maskMap, baseMap, maskImg)
                else:
                    finalMap = baseMap
                
                finalMap = self.applyOutputBlur(finalMap, bStr, bBlur)
                finalMap.save(mapPath)
                self.lastMmMap = mapPath
                def updateUi():
                    if target == "compiler":
                        ratio = img.size[0] / img.size[1]
                        targetRegion = "EU & UK" if ratio > 3.0 else "US & MX"
                        self.regionVar.set(targetRegion)
                        self.updateDropzoneRegions()
                        self.imageDropZone.pathEntry.delete(0, "end")
                        self.imageDropZone.pathEntry.insert(0, sourcePath)
                        self.imageDropZone.updatePreview(sourcePath)
                        self.nrmlDropZone.pathEntry.delete(0, "end")
                        self.nrmlDropZone.pathEntry.insert(0, self.lastMmMap)
                        self.nrmlDropZone.updatePreview(self.lastMmMap)
                        self.imageDropZone.configure(border_color=COLORS["accent_success"])
                        self.nrmlDropZone.configure(border_color=COLORS["accent_success"])
                        self.mmStatusLabel.configure(text="")
                        self.showPage("compiler")
                    elif target == "preview":
                        ratio = img.size[0] / img.size[1]
                        targetRegion = "EU & UK" if ratio > 3.0 else "US & MX"
                        self.viewportRegionVar.set(targetRegion)
                        self.onViewportRegionChange(targetRegion)
                        self.mmStatusLabel.configure(text="")
                        self.sendToPreview(sourcePath, isNormal=False)
                        self.sendToPreview(self.lastMmMap, isNormal=True)
                        self.showPage("3d_preview")
                self.uiQueue.put(updateUi)
            except Exception as e:
                self.uiQueue.put(lambda e=e: messagebox.showerror("Error", f"Failed to generate map: {e}"))
        threading.Thread(target=process, daemon=True).start()

    def updateMaterialsZipVisibility(self, *args):
        isLatest = self.versionVar.get() == "Latest (Direct Zip)"
        isGlobal = getattr(self, "outputModeVar", None) and self.outputModeVar.get() == "Global"
        isGlossy = getattr(self, "glossyVar", ctk.BooleanVar(value=False)).get()
        isAutoResolve = getattr(self, "autoResolvePathsVar", ctk.BooleanVar(value=True)).get()
        
        # Hide materials fields if we are globally auto-resolving
        if isGlobal and isAutoResolve:
            showRow = False
        else:
            showRow = isLatest and isGlobal and isGlossy

        if hasattr(self, "materialsInputRow"):
            if showRow and not self.materialsInputRow.winfo_manager():
                self.materialsLabel.pack(anchor="w", padx=20, pady=(5, 0), after=self.genDirEntry.master)
                self.materialsHelp.pack(anchor="w", padx=20, pady=(0, 5), after=self.materialsLabel)
                self.materialsInputRow.pack(fill="x", padx=20, after=self.materialsHelp)
            elif not showRow and self.materialsInputRow.winfo_manager():
                self.materialsLabel.pack_forget()
                self.materialsHelp.pack_forget()
                self.materialsInputRow.pack_forget()

        if hasattr(self, "histMaterialsZipRow"):
            if showRow and not self.histMaterialsZipRow.winfo_manager():
                self.histMaterialsZipRow.pack(fill="x", pady=(10, 0))
            elif not showRow and self.histMaterialsZipRow.winfo_manager():
                self.histMaterialsZipRow.pack_forget()

        if hasattr(self, "presetMaterialsZipRow"):
            if showRow and not self.presetMaterialsZipRow.winfo_manager():
                self.presetMaterialsZipRow.pack(fill="x", pady=(10, 0))
            elif not showRow and self.presetMaterialsZipRow.winfo_manager():
                self.presetMaterialsZipRow.pack_forget()

    def browseMaterialsZip(self):
        initial = self.lastDirs.get("out", "/")
        file = filedialog.askopenfilename(filetypes=[("Zip Archives", "*.zip")], initialdir=initial, title="Select Materials.zip")
        if file:
            self.lastDirs["out"] = os.path.dirname(file)
            self.materialsZipVar.set(os.path.normpath(file))
            self.saveConfig(silent=True)

    def setupPresetsPage(self):
        ctk.CTkLabel(self.presetsPage, text="Preset Plates", font=ctk.CTkFont(size=32, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(
            self.presetsPage, 
            text="Ready-to-use custom plates. Select one EU and one US plate to bundle into a single compilation. DMs are always open for suggestions.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            wraplength=587,
            justify="left"
        ).pack(anchor="w", padx=(0, 20), pady=(0, 20))
        
        self.presetCartRow = ctk.CTkFrame(self.presetsPage, fg_color="transparent")
        self.presetCartRow.pack(fill="x", pady=(0, 10))

        self.presetCartStatus = ctk.CTkLabel(self.presetCartRow, text="No Presets Selected", font=ctk.CTkFont(size=14), text_color=COLORS["accent_primary"])
        self.presetCartStatus.pack(side="left")

        presetSwitchesFrame = ctk.CTkFrame(self.presetCartRow, fg_color="transparent")
        presetSwitchesFrame.pack(side="right")

        self.presetGlossySwitch = ctk.CTkSwitch(
            presetSwitchesFrame, text="Glossy Finish", variable=self.glossyVar,
            button_color=COLORS["accent_primary"], command=self.updateMaterialsZipVisibility
        )
        self.presetGlossySwitch.pack(side="left", padx=(0, 15))
        
        self.presetDeleteBracketToggle = ctk.CTkSwitch(
            presetSwitchesFrame, text="Delete Seal", variable=self.deleteBracketVar,
            button_color=COLORS["accent_primary"]
        )
        
        self.presetDeleteScrewToggle = ctk.CTkSwitch(
            presetSwitchesFrame, text="Delete Plate Screw", variable=self.deleteScrewVar,
            button_color=COLORS["accent_primary"]
        )

        self.presetBackupSwitch = ctk.CTkSwitch(
            presetSwitchesFrame, text="Create Backups", variable=self.currentBackupVar,
            button_color=COLORS["accent_primary"], command=self.onBackupToggle
        )
        self.presetBackupSwitch.pack(side="left")

        self.presetSettingsFrame = ctk.CTkFrame(self.presetsPage, fg_color="transparent")
        self.presetSettingsFrame.pack(fill="x", pady=(0, 15))

        self.presetTopRow = ctk.CTkFrame(self.presetSettingsFrame, fg_color="transparent")
        self.presetTopRow.pack(fill="x")

        self.presetBottomRow = ctk.CTkFrame(self.presetSettingsFrame, fg_color="transparent")

        self.presetVersionLabel = ctk.CTkLabel(self.presetTopRow, text="Version:", font=ctk.CTkFont(size=13, weight="bold"))
        self.presetVersionLabel.pack(side="left", padx=(0, 10))
        
        self.presetVersionBorder = ctk.CTkFrame(self.presetTopRow, fg_color=COLORS["bg_secondary"], border_width=2, border_color=COLORS["border"], corner_radius=6)
        self.presetVersionBorder.pack(side="left", padx=(0, 20))
        
        ctk.CTkOptionMenu(
            self.presetVersionBorder, variable=self.versionVar, values=["Latest (Direct Zip)", "1.634.818.0"], 
            width=170, fg_color=COLORS["bg_secondary"], button_color=COLORS["bg_secondary"], 
            button_hover_color=COLORS["border"], dropdown_fg_color=COLORS["bg_card"], 
            dropdown_hover_color=COLORS["border"], dropdown_text_color=COLORS["text_primary"], 
            corner_radius=4, command=lambda v: (self.toggleHelpText(v), self.saveConfig(silent=True))
        ).pack(padx=2, pady=2)

        self.presetModeContainer = ctk.CTkFrame(self.presetTopRow, fg_color="transparent")
        
        ctk.CTkLabel(self.presetModeContainer, text="Mode:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 10))
        
        presetModeBorder = ctk.CTkFrame(self.presetModeContainer, fg_color=COLORS["bg_secondary"], border_width=2, border_color=COLORS["border"], corner_radius=6)
        presetModeBorder.pack(side="left", padx=(0, 5))
        
        ctk.CTkOptionMenu(
            presetModeBorder, variable=self.outputModeVar, 
            values=["Global", "Car-Specific (Car.zip)"], width=210,
            fg_color=COLORS["bg_secondary"], button_color=COLORS["bg_secondary"], 
            button_hover_color=COLORS["border"], dropdown_fg_color=COLORS["bg_card"], 
            dropdown_hover_color=COLORS["border"], dropdown_text_color=COLORS["text_primary"], 
            corner_radius=4, command=self.toggleOutputMode
        ).pack(padx=2, pady=2)
        
        self.presetOutputContainer = ctk.CTkFrame(self.presetSettingsFrame, fg_color="transparent")
        
        presetTexRow = ctk.CTkFrame(self.presetOutputContainer, fg_color="transparent")
        presetTexRow.pack(fill="x")
        
        self.presetOutputLabel = ctk.CTkLabel(presetTexRow, text="Textures.zip Path:", font=ctk.CTkFont(size=13, weight="bold"))
        self.presetOutputLabel.pack(side="left", padx=(0, 10))
        
        self.presetDirEntry = ctk.CTkEntry(presetTexRow, textvariable=self.genOutputDirVar, fg_color=COLORS["bg_secondary"], border_color=COLORS["border"])
        self.presetDirEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.presetDirEntry.bind("<Button-1>", lambda e: self.browseGenOutputDir())
        self.setupEntryDrop(self.presetDirEntry, self.genOutputDirVar)
        
        ctk.CTkButton(presetTexRow, text="Browse", width=80, fg_color=COLORS["bg_secondary"], hover_color=COLORS["border"], command=self.browseGenOutputDir).pack(side="left", padx=(0, 10))

        self.presetMaterialsZipRow = ctk.CTkFrame(self.presetOutputContainer, fg_color="transparent")
        
        presetMatLabel = ctk.CTkLabel(self.presetMaterialsZipRow, text="Materials.zip Path:", font=ctk.CTkFont(size=13, weight="bold"))
        presetMatLabel.pack(side="left", padx=(0, 10))
        
        self.presetMaterialsEntry = ctk.CTkEntry(self.presetMaterialsZipRow, textvariable=self.materialsZipVar, fg_color=COLORS["bg_secondary"], border_color=COLORS["border"])
        self.presetMaterialsEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.presetMaterialsEntry.bind("<Button-1>", lambda e: self.browseMaterialsZip())
        self.setupEntryDrop(self.presetMaterialsEntry, self.materialsZipVar)
        
        ctk.CTkButton(self.presetMaterialsZipRow, text="Browse", width=80, fg_color=COLORS["bg_secondary"], hover_color=COLORS["border"], command=self.browseMaterialsZip).pack(side="left", padx=(0, 10))
        
        self.presetCartBtn = ctk.CTkButton(
            self.presetsPage, 
            text=" COMPILE PRESETS", 
            image=self.loadIcon("package-plus.png", size=20), 
            command=self.compilePresets, 
            fg_color=COLORS["accent_secondary"], 
            height=50,
            width=1200,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.presetCartBtn.pack(fill="x", padx=0, pady=(0, 20))

        self.presetRestoreBtn = ctk.CTkButton(
            self.presetsPage, 
            text=" RESTORE ORIGINALS", 
            image=self.loadIcon("undo.png", size=18),
            fg_color=COLORS["bg_card"], 
            hover_color=COLORS["accent_danger"], 
            height=40, 
            width=1200,
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=self.runRestore
        )
        
        self.presetsList = ctk.CTkFrame(self.presetsPage, fg_color="transparent")
        self.presetsList.pack(fill="both", expand=True)
        self.presetsList.grid_columnconfigure(0, weight=1)
        self.presetsList.grid_columnconfigure(1, weight=1)

        self.refreshPresets()

    def refreshPresets(self, force=False):
        if not force and self.presetsList.winfo_children():
            return
            
        for widget in self.presetsList.winfo_children(): 
            widget.destroy()

        is_fh6 = getattr(self, "gameVar", None) and self.gameVar.get() == "FH6"
        
        rowIdx = 0
        colIdx = 0
        
        for item in self.presetData:
            is_fh6_preset = item.get("region") == "FH6 (JPN)"
            if is_fh6 and not is_fh6_preset:
                continue
            if not is_fh6 and is_fh6_preset:
                continue

            card = ctk.CTkFrame(self.presetsList, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
            card.grid(row=rowIdx, column=colIdx, sticky="nsew", padx=10, pady=10)
            
            imgLabel = ctk.CTkLabel(card, text="Loading...")
            imgLabel.pack(pady=(20, 10), padx=10, fill="both", expand=True)
            
            imgPath = item.get('img')
            if imgPath in self.imageCache:
                imgLabel.configure(image=self.imageCache[imgPath], text="")
            elif imgPath and os.path.exists(imgPath):
                threading.Thread(target=self.loadPresetPreview, args=(imgPath, imgLabel, item['region']), daemon=True).start()
            else:
                imgLabel.configure(image=self.loadIcon("image.png", size=32), text="")

            ctk.CTkLabel(card, text=item['name'], font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 2))
            ctk.CTkLabel(card, text=item['region'], font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(pady=(0, 15))
            
            isSelected = item in self.presetCart.values()
            regionKey = 'us' if item['region'] == "US & MX" else 'eu'
            isBlocked = self.presetCart[regionKey] is not None and self.presetCart[regionKey] != item
            
            btnText = "Remove" if isSelected else "Select"
            btnState = "disabled" if isBlocked else "normal"
            btnColor = COLORS["accent_danger"] if isSelected else COLORS["accent_primary"]
            
            ctk.CTkButton(card, text=btnText, state=btnState, fg_color=btnColor, command=lambda i=item: self.togglePresetCart(i)).pack(pady=(0, 20), padx=20, fill="x")

            viewBtn = ctk.CTkButton(
                card, 
                text="", 
                image=self.loadIcon("view.png", size=16),
                width=30, height=30,
                fg_color=COLORS["bg_card"],
                hover_color=COLORS["accent_primary"],
                command=lambda i=item: self.sendPresetToViewport(i)
            )
            viewBtn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
            viewBtn.lift()

            colIdx += 1
            if colIdx > 1:
                colIdx = 0
                rowIdx += 1
                
        if hasattr(self.presetsPage, "_parent_canvas"):
            self.presetsPage._parent_canvas.yview_moveto(0)

    def sendPresetToViewport(self, item):
        targetRegion = item['region']
        if self.viewportRegionVar.get() != targetRegion:
            self.viewportRegionVar.set(targetRegion)
            self.onViewportRegionChange(targetRegion)
            
        imgPath = item.get('img')
        if imgPath and os.path.exists(imgPath):
            self.sendToPreview(imgPath, isNormal=False)
            
        nrmlPath = item.get('nrml')
        if nrmlPath and os.path.exists(nrmlPath):
            self.sendToPreview(nrmlPath, isNormal=True)
            
        self.showPage("3d_preview")

    def loadPresetPreview(self, path, label, region):
        def backgroundtask():
            try:
                with open(path, "rb") as f:
                    imgData = f.read()
            
                pilImg = Image.open(io.BytesIO(imgData)).convert("RGBA")
                w, h = pilImg.size
                targetW = 250 if "EU" in region else 200
                targetH = int(targetW * (h / w))
                pilImg.thumbnail((targetW, targetH), Image.LANCZOS)

                self.uiQueue.put(lambda: self.finalizePresetUI(pilImg, path, label))
            
            except Exception as e:
                print(f"Background disk error for {path}: {e}")

        threading.Thread(target=backgroundtask, daemon=True).start()

    def finalizePresetUI(self, pilImg, path, label):
        try:
            if label.winfo_exists():
                ctkImg = ctk.CTkImage(light_image=pilImg, dark_image=pilImg, size=pilImg.size)
                self.imageCache[path] = ctkImg
                label.configure(image=ctkImg, text="")
        except Exception as e:
            print(f"UI Update error: {e}")

    def handlePresetError(self, label):
        try:
            if label.winfo_exists():
                errorIcon = self.loadIcon("image.png", size=32)
                label.configure(image=errorIcon, text="")
        except (AttributeError, Exception):
            pass

    def toggleCart(self, item):
        regionKey = 'us' if item['region'] == "US & MX" else 'eu'
        self.cart[regionKey] = None if self.cart[regionKey] == item else item
        
        euItem = self.cart.get('eu')
        usItem = self.cart.get('us')
        
        euName = f"{euItem['name']} (Preset)" if euItem and euItem.get('is_preset') else (os.path.basename(euItem.get('img', '')) if euItem and euItem.get('img') else "None")
        usName = f"{usItem['name']} (Preset)" if usItem and usItem.get('is_preset') else (os.path.basename(usItem.get('img', '')) if usItem and usItem.get('img') else "None")
        
        self.cartStatus.configure(text=f"EU: {euName}  |  US: {usName}")
        self.refreshHistory()

    def togglePresetCart(self, item):
        regionKey = 'us' if item['region'] == "US & MX" else 'eu'
        self.presetCart[regionKey] = None if self.presetCart[regionKey] == item else item
        
        euName = self.presetCart['eu']['name'] if self.presetCart['eu'] else "None"
        usName = self.presetCart['us']['name'] if self.presetCart['us'] else "None"
        self.presetCartStatus.configure(text=f"EU: {euName}  |  US: {usName}")
        
        self.refreshPresets(force=True)

    def compilePresets(self):
        outDir = self.genOutputDirVar.get()
        
        if outDir == "Not Selected" or not outDir:
            messagebox.showerror("Error", "Please select an output location.")
            return
            
        self.presetCartBtn.configure(state="disabled", text=" COMPILING...")
        
        def process():
            try:
                addedToHistory = False
                
                if self.presetCart['eu']: 
                    self.regionVar.set("EU & UK")
                    self.processFiles(self.presetCart['eu']['img'], self.presetCart['eu']['nrml'], outDir, silent=True)
                    self.history.append({
                        "region": "EU & UK", 
                        "img": self.presetCart['eu']['img'], 
                        "nrml": self.presetCart['eu']['nrml'],
                        "name": self.presetCart['eu']['name'],
                        "is_preset": True,
                        "glossy": self.glossyVar.get()
                    })
                    addedToHistory = True
                    
                if self.presetCart['us']: 
                    self.regionVar.set("US & MX")
                    self.processFiles(self.presetCart['us']['img'], self.presetCart['us']['nrml'], outDir, silent=True)
                    self.history.append({
                        "region": "US & MX", 
                        "img": self.presetCart['us']['img'], 
                        "nrml": self.presetCart['us']['nrml'],
                        "name": self.presetCart['us']['name'],
                        "is_preset": True,
                        "glossy": self.glossyVar.get()
                    })
                    addedToHistory = True
                
                if addedToHistory:
                    self.saveConfig(silent=True)
                
                self.after(0, lambda: messagebox.showinfo("Success", "Presets compiled successfully!"))
            except Exception as e:
                self.after(0, lambda err=e: messagebox.showerror("Generation Error", f"An error occurred:\n{err}"))
            finally:
                self.after(0, lambda: self.presetCartBtn.configure(state="normal", text=" COMPILE PRESETS"))
                
        threading.Thread(target=process, daemon=True).start()

    def setupDashboardPage(self):
        header = ctk.CTkLabel(
            self.dashboardPage, 
            text="Welcome back! ", 
            image=self.loadIcon("hello.png", size=32),
            compound="right",
            font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"), 
            text_color=COLORS["text_primary"]
        )
        header.pack(anchor="w", pady=(0, 20))

        statsFrame = ctk.CTkFrame(self.dashboardPage, fg_color="transparent")
        statsFrame.pack(fill="x", pady=(0, 20))
        statsFrame.grid_columnconfigure(0, weight=1)
        statsFrame.grid_columnconfigure(1, weight=1)

        self.statSettings = ctk.CTkFrame(statsFrame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.statSettings.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        settingsInner = ctk.CTkFrame(self.statSettings, fg_color="transparent")
        settingsInner.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(settingsInner, text="Compiler Settings", font=ctk.CTkFont(weight="bold"), text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 10))
        
        setGrid = ctk.CTkFrame(settingsInner, fg_color="transparent")
        setGrid.pack(fill="x")
        setGrid.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(setGrid, text="Compression:", font=ctk.CTkFont(size=13)).grid(row=0, column=0, sticky="w", pady=2)
        self.dashCompLabel = ctk.CTkLabel(setGrid, text="--", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["accent_primary"])
        self.dashCompLabel.grid(row=0, column=1, sticky="e", pady=2)

        ctk.CTkLabel(setGrid, text="Silent Mode:", font=ctk.CTkFont(size=13)).grid(row=1, column=0, sticky="w", pady=2)
        self.dashSilentSwitch = ctk.CTkSwitch(
            setGrid, text="", variable=self.silentModeVar, width=35,
            button_color=COLORS["accent_primary"], command=lambda: self.saveConfig(silent=True)
        )
        self.dashSilentSwitch.grid(row=1, column=1, sticky="e", pady=2)

        ctk.CTkLabel(setGrid, text="Auto-Resolve Paths:", font=ctk.CTkFont(size=13)).grid(row=2, column=0, sticky="w", pady=2)
        self.dashAutoResolveSwitch = ctk.CTkSwitch(
            setGrid, text="", variable=self.autoResolvePathsVar, width=35,
            button_color=COLORS["accent_primary"], command=self.onAutoResolveToggle
        )
        self.dashAutoResolveSwitch.grid(row=2, column=1, sticky="e", pady=2)
        ToolTip(self.dashAutoResolveSwitch, "When enabled, hides manual zip inputs and uses\nyour Game Directory paths instead.")

        self.btnOpenOutput = ctk.CTkButton(
            setGrid,
            text=" Open Output Folder",
            image=self.loadIcon("folder.png", size=14),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["border"],
            height=28,
            command=self.openOutputFolder
        )
        self.btnOpenOutput.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 2))

        self.statHealth = ctk.CTkFrame(statsFrame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.statHealth.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        healthInner = ctk.CTkFrame(self.statHealth, fg_color="transparent")
        healthInner.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(healthInner, text="System Readiness", font=ctk.CTkFont(weight="bold"), text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 10))
        
        statusGrid = ctk.CTkFrame(healthInner, fg_color="transparent")
        statusGrid.pack(fill="x")
        statusGrid.columnconfigure(1, weight=1) 

        ctk.CTkLabel(statusGrid, text="Photoshop", font=ctk.CTkFont(size=13)).grid(row=0, column=0, sticky="w", pady=2)
        self.healthPsStatus = ctk.CTkLabel(statusGrid, text="--", font=ctk.CTkFont(size=13, weight="bold"))
        self.healthPsStatus.grid(row=0, column=1, sticky="e", pady=2) 

        ctk.CTkLabel(statusGrid, text="Illustrator", font=ctk.CTkFont(size=13)).grid(row=1, column=0, sticky="w", pady=2)
        self.healthAiStatus = ctk.CTkLabel(statusGrid, text="--", font=ctk.CTkFont(size=13, weight="bold"))
        self.healthAiStatus.grid(row=1, column=1, sticky="e", pady=2) 

        ctk.CTkLabel(statusGrid, text="7-Zip", font=ctk.CTkFont(size=13)).grid(row=2, column=0, sticky="w", pady=2)
        self.healthSzStatus = ctk.CTkLabel(statusGrid, text="--", font=ctk.CTkFont(size=13, weight="bold"))
        self.healthSzStatus.grid(row=2, column=1, sticky="e", pady=2) 

        ctk.CTkButton(
            statusGrid,
            text=" Setup Game Directories",
            image=self.loadIcon("settings.png", size=14),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["border"],
            height=28,
            command=lambda: self.showPage("settings")
        ).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 2))

        guideFrame = ctk.CTkFrame(self.dashboardPage, fg_color="transparent")
        guideFrame.pack(fill="x", pady=(10, 20))
        
        ctk.CTkLabel(guideFrame, text="Getting Started", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 10))
        
        guideText = (
            "1. Need a blank plate? Go to 'Plate Templates' to download base files.\n"
            "2. Want to design a plate yourself? Go to 'Plate Designer' to type your text on a supported template.\n"
            "3. Need a 3D effect on your plate? Use the '3D Map Maker' to generate normal maps.\n"
            "4. Have both the plate design and height map? Go to 'Compiler' to inject your images into the game files."
        )
        ctk.CTkLabel(guideFrame, text=guideText, font=ctk.CTkFont(size=13), text_color=COLORS["text_secondary"], justify="left").pack(anchor="w", padx=(10, 0))

        self.activePlatesLabel = ctk.CTkLabel(self.dashboardPage, text="Active Plates", font=ctk.CTkFont(size=18, weight="bold"))
        self.activePlatesLabel.pack(anchor="w", pady=(10, 10))
        self.activePlatesFrame = ctk.CTkFrame(self.dashboardPage, fg_color="transparent")
        self.activePlatesFrame.pack(fill="x")
        self.activePlatesFrame.grid_columnconfigure(0, weight=1)
        self.activePlatesFrame.grid_columnconfigure(1, weight=1)
        
        self.activeEuLabel = ctk.CTkLabel(self.activePlatesFrame, text="Loading EU...", height=80, fg_color=COLORS["bg_secondary"], corner_radius=12)
        self.activeEuLabel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.activeUsLabel = ctk.CTkLabel(self.activePlatesFrame, text="Loading US...", height=80, fg_color=COLORS["bg_secondary"], corner_radius=12)
        self.activeUsLabel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self.changelogLabel = ctk.CTkLabel(
            self.dashboardPage, 
            text=f"Recent Additions (v{APP_VERSION})", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.changelogLabel.pack(anchor="w", pady=(20, 10))
        
        self.changelogFrame = ctk.CTkFrame(self.dashboardPage, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.changelogFrame.pack(fill="x", pady=(0, 10))
        self.changelogFrame.grid_columnconfigure(1, weight=1)

        changes = [
            ("FH6 Partial Compatibility", "Added partial support for FH6. Currently only supports Car-Specific mods."),
            ("3D Viewport Updated", "Added FH6 support to the viewport as well so you can now view your texture on a plate before loading into the game."),
            ("Added Game Directory Setup", "Added 2 areas in the settings so that the app knows where your game directories are so you don't have to select your own paths."),
            ("Added Template", "Added a Japanese Template to the templates page when app toggled to FH6. Has all important areas highlighted in a color."),
            ("Added Presets", "Added 2 Japanese Presets to the presets page."),
            ("Plate Designer Revamped", "Completely overhauled the plate designer when app is toggled to FH6. Custom Japanese plate support."),
            ("Splash Screen", "Added a loading screen when launching the app instead of a long silence.") 
        ]

        for idx, (title, desc) in enumerate(changes):
            ctk.CTkLabel(self.changelogFrame, text=f"• {title}:", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["accent_primary"]).grid(row=idx, column=0, sticky="nw", padx=(15, 10), pady=8)
            ctk.CTkLabel(self.changelogFrame, text=desc, font=ctk.CTkFont(size=13), text_color=COLORS["text_secondary"], justify="left", wraplength=350).grid(row=idx, column=1, sticky="nw", padx=(0, 15), pady=8)

        ctk.CTkLabel(self.dashboardPage, text="Recent Activity", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(20, 10))
        self.dashHistoryList = ctk.CTkFrame(self.dashboardPage, fg_color="transparent")
        self.dashHistoryList.pack(fill="both", expand=True)

    def refreshDashboard(self):
        compVal = self.compLevelVar.get()
        cleanComp = compVal.split(" ")[0] if " " in compVal else compVal
        self.dashCompLabel.configure(text=cleanComp)
        
        checks = [
            (self.psPathVar.get().strip('"'), self.healthPsStatus),
            (self.aiPathVar.get().strip('"'), self.healthAiStatus),
            (self.szPathVar.get().strip('"'), self.healthSzStatus)
        ]
        
        for path, label in checks:
            exists = os.path.exists(path) if path else False
            
            if label == self.healthSzStatus and not exists:
                exists = os.path.exists(resourcePath("7za.exe"))

            statusText = "Ready" if exists else "Missing"
            statusColor = COLORS["accent_success"] if exists else COLORS["accent_danger"]
            
            label.configure(text=statusText, text_color=statusColor)

        self.after(350, lambda: threading.Thread(target=self.loadActivePlates, daemon=True).start())

        for widget in self.dashHistoryList.winfo_children(): widget.destroy()
        recentItems = list(reversed(self.history))[:3] 
        if not recentItems:
            ctk.CTkLabel(self.dashHistoryList, text="No plates compiled yet.", text_color=COLORS["text_muted"]).pack(anchor="w", pady=10)
            return
            
        for item in recentItems:
            card = ctk.CTkFrame(self.dashHistoryList, fg_color=COLORS["bg_secondary"], corner_radius=8)
            card.pack(fill="x", pady=5, ipadx=15, ipady=12)
            
            if item.get('is_preset'):
                imgName = f"{item['name']} (Preset)"
            else:
                imgName = os.path.basename(item['img']) if item.get('img') else "No Image"
                
            ctk.CTkLabel(card, text="✅", font=ctk.CTkFont(size=16)).pack(side="left")
            ctk.CTkLabel(card, text=f"You compiled a {item['region']} plate: {imgName}", text_color=COLORS["text_secondary"]).pack(side="left", padx=10)

    def setActivePlateUI(self, region, img, fallbackText):
        labelName = f"active{region.capitalize()}Label"
        label = getattr(self, labelName, None)
        
        if not label: return
        
        if img:
            try:
                w, h = img.size
                aspect = w / h
                targetH = 60
                targetW = int(targetH * aspect)
                if targetW > 250: targetW = 250
                
                img.thumbnail((targetW, targetH))
                
                def apply_img(lbl=label, i=img, tw=targetW, th=targetH):
                    try:
                        ctkImg = ctk.CTkImage(light_image=i, dark_image=i, size=(tw, th))
                        self.applyActivePlateUI(lbl, ctkImg)
                    except Exception:
                        self.applyActivePlateFallback(lbl, "Preview Error")

                self.uiQueue.put(apply_img)
            except (AttributeError, ValueError, OSError):
                self.uiQueue.put(lambda: self.applyActivePlateFallback(label, "Preview Error"))
        else:
            self.uiQueue.put(lambda: self.applyActivePlateFallback(label, fallbackText))

    def applyActivePlateUI(self, label, img):
        if label.winfo_exists():
            label.configure(image=img, text="")
            setattr(label, "_saved_image_ref", img)

    def applyActivePlateFallback(self, label, text):
        if label.winfo_exists():
            label.configure(image=None, text=text)

    def openOutputFolder(self):
        path = self.genOutputDirVar.get()
        
        if path == "Not Selected" or not path:
            messagebox.showerror("Error", "No output location selected yet.")
            return
            
        if os.path.isfile(path) or path.lower().endswith('.zip'):
            folder = os.path.dirname(path)
        else:
            folder = path
            
        if os.path.exists(folder):
            try:
                os.startfile(folder)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {e}")
        else:
            messagebox.showerror("Error", "The selected folder does not exist.")

    def loadLastProject(self):
        if not self.history: 
            return
            
        last = self.history[-1]
        
        self.regionVar.set(last["region"])
        self.updateDropzoneRegions()
        
        img = last.get("img", "")
        if img and os.path.exists(img):
            self.imageDropZone.pathEntry.delete(0, "end")
            self.imageDropZone.pathEntry.insert(0, img)
            self.imageDropZone.updatePreview(img)
            self.imageDropZone.configure(border_color=COLORS["accent_success"])
            
        nrml = last.get("nrml", "")
        if nrml and os.path.exists(nrml):
            self.nrmlDropZone.pathEntry.delete(0, "end")
            self.nrmlDropZone.pathEntry.insert(0, nrml)
            self.nrmlDropZone.updatePreview(nrml)
            self.nrmlDropZone.configure(border_color=COLORS["accent_success"])
            
        self.showPage("compiler")

    def promptClearBackups(self):
        targetZip = filedialog.askopenfilename(filetypes=[("Zip Archives", "*.zip")], title="Select Textures.zip to clean")
        if not targetZip: return
        
        if messagebox.askyesno("Confirm", "This will search the 'plates' folder inside this zip and delete ALL backup (.bak) files.\n\nContinue?"):
            threading.Thread(target=self.processClearBackups, args=(targetZip,), daemon=True).start()

    def processClearBackups(self, targetZip):
        try:
            szPath = self.szPathVar.get().strip('"')

            if not os.path.exists(szPath):
                szPath = resourcePath("7za.exe")

            if not os.path.exists(szPath): 
                raise FileNotFoundError(f"7-Zip not found. Checked settings and portable fallback.")
            
            tempDir = tempfile.mkdtemp()
            
            subprocess.run([szPath, "x", targetZip, f"-o{tempDir}"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            platesDir = os.path.join(tempDir, "plates")
            bakCount = 0
            
            if os.path.exists(platesDir):
                for root, dirs, files in os.walk(platesDir):
                    for f in files:
                        if f.endswith(".bak"):
                            os.remove(os.path.join(root, f))
                            bakCount += 1
            
            if bakCount == 0:
                shutil.rmtree(tempDir)
                self.after(0, lambda: messagebox.showinfo("Clean Complete", "No .bak files were found in the plates folder of this zip!"))
                return
                
            os.remove(targetZip)
            compFlag = "-mx1" if "mx1" in self.compLevelVar.get() else "-mx9" if "mx9" in self.compLevelVar.get() else "-mx5"
            subprocess.run([szPath, "a", "-tzip", compFlag, targetZip, f"{tempDir}\\*"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            shutil.rmtree(tempDir)
            self.after(0, lambda: messagebox.showinfo("Success", f"Successfully deleted {bakCount} backup file(s) from the plates folder and repacked the zip!"))
            
        except Exception as e:
            self.after(0, lambda err=e: messagebox.showerror("Error", f"Failed to clear backups:\n{err}"))

    def loadActivePlates(self):
        import zipfile
        try:
            isCarSpecific = getattr(self, "outputModeVar", None) and self.outputModeVar.get() == "Car-Specific (Car.zip)"
            
            if isCarSpecific:
                outPath = self.defaultOutVar.get()
                if outPath == "Not Selected" or not outPath:
                    targetZip = "Not Selected"
                else:
                    if os.path.isdir(outPath):
                        targetZip = os.path.join(outPath, "Textures.zip")
                    else:
                        targetZip = outPath
            else:
                fh5Dir = getattr(self, 'fh5GameDirVar', None)
                if not fh5Dir or fh5Dir.get() == "Not Selected":
                    targetZip = "Not Selected"
                else:
                    if self.versionVar.get() == "Latest (Direct Zip)":
                        targetZip = os.path.join(fh5Dir.get(), "Content", "media", "cars", "_library", "Textures.zip")
                    else:
                        targetZip = os.path.join(fh5Dir.get(), "media", "Stripped", "MediaOverride", "RC0", "Cars", "_library", "Textures.zip")

            if targetZip == "Not Selected" or not targetZip:
                self.setActivePlateUI("eu", None, "No Output Selected")
                self.setActivePlateUI("us", None, "No Output Selected")
                return

            if not os.path.exists(targetZip) or not os.path.isfile(targetZip):
                self.setActivePlateUI("eu", None, "Textures.zip not found")
                self.setActivePlateUI("us", None, "Textures.zip not found")
                return

            euImg, usImg = None, None

            with zipfile.ZipFile(targetZip, 'r') as z:
                euEntry = next((name for name in z.namelist() if "plate_eu1_base_diff" in name and not name.endswith(".bak")), None)
                usEntry = next((name for name in z.namelist() if "plate_mx1_base_diff" in name and not name.endswith(".bak")), None)
                
                if euEntry:
                    with z.open(euEntry) as f: euImg = Image.open(BytesIO(f.read())).copy()
                if usEntry:
                    with z.open(usEntry) as f: usImg = Image.open(BytesIO(f.read())).copy()

            self.setActivePlateUI("eu", euImg, "Default EU Plate")
            self.setActivePlateUI("us", usImg, "Default US Plate")
            
        except zipfile.BadZipFile:
            self.setActivePlateUI("eu", None, "Invalid Textures.zip")
            self.setActivePlateUI("us", None, "Invalid Textures.zip")
        except Exception as e:
            print(f"DEBUG loadActivePlates error: {e}")
            self.setActivePlateUI("eu", None, "Error Reading Plates")
            self.setActivePlateUI("us", None, "Error Reading Plates")

    def animateStatusDot(self):
        t = time.time() * 2.5 
        intensity = (math.sin(t) + 1) / 2 
        
        if getattr(self, "isOnline", True):
            r = int(22 + (16 - 22) * intensity)
            g = int(56 + (185 - 56) * intensity)
            b = int(47 + (129 - 47) * intensity)
        else:
            r = int(30 + (239 - 30) * intensity)
            g = int(15 + (68 - 15) * intensity)
            b = int(15 + (68 - 15) * intensity)
            
        try:
            if self.statusDot.winfo_exists():
                self.statusDot.configure(text_color=f"#{r:02x}{g:02x}{b:02x}")
                self.after(50, self.animateStatusDot)
        except Exception:
            pass

    def openMaskPainter(self, edit=False):
        source = self.mmDropZone.getPath()
        if not source or not os.path.exists(source):
            messagebox.showerror("Error", "Drop a Source Image first!")
            return
            
        mask = None
        if edit:
            mask = self.mmMaskDropZone.getPath()
            if not mask or not os.path.exists(mask):
                messagebox.showerror("Error", "No mask found to edit! Drop a mask or draw a new one first.")
                return
                
        MaskPainter(self, source, mask, self.applyDrawnMask)

    def applyDrawnMask(self, maskPath):
        self.mmMaskDropZone.pathEntry.delete(0, "end")
        self.mmMaskDropZone.pathEntry.insert(0, maskPath)
        self.mmMaskDropZone.updatePreview(maskPath)
        self.mmMaskDropZone.configure(border_color=COLORS["accent_success"])
        self.schedulePreviewUpdate()

    def openNormalPainter(self):
        imgPath = self.mmDropZone.getPath()
        if not imgPath or not os.path.isfile(imgPath):
            messagebox.showerror("Error", "Drop a Source Image first to generate the map.")
            return

        self.btnPaintMap.configure(state="disabled", text=" OPENING...")

        def prepare():
            try:
                img = Image.open(imgPath)
                bStr, bBlur, bDir = self.baseIntensity.get(), self.baseBlur.get(), self.baseExtrude.get()
                mStr, mBlur, mDir = self.maskIntensity.get(), self.maskBlur.get(), self.maskExtrude.get()
                maskPath = self.mmMaskDropZone.getPath() if self.advancedModeVar.get() else None

                baseMap = self.createNormalMapData(img, bStr, bBlur, bDir)

                if maskPath and os.path.exists(maskPath):
                    maskImg = Image.open(maskPath).convert('L').resize(baseMap.size)
                    maskMap = self.createNormalMapData(img, mStr, mBlur, mDir)
                    finalImg = Image.composite(maskMap, baseMap, maskImg)
                else:
                    finalImg = baseMap

                self.after(0, lambda: NormalPainter(self, finalImg, self.savePaintedNormalMap))
            except Exception as e:
                self.after(0, lambda e=e: messagebox.showerror("Error", f"Failed to load map: {e}"))
            finally:
                self.after(0, lambda: self.btnPaintMap.configure(state="normal", text=" PAINT MAP"))

        threading.Thread(target=prepare, daemon=True).start()

    def savePaintedNormalMap(self, finalImg, sendToCompiler=False, sendToPreview=False):
        tempPath = os.path.normpath(os.path.join(tempfile.gettempdir(), "last_painted_map.png"))
        
        try:
            finalImg.save(tempPath, format="PNG")
            self.lastMmMap = tempPath 
            
            if sendToCompiler:
                self.sendMapToCompiler() 
            elif sendToPreview:
                self.sendMapToPreview()
            else:
                self.mmStatusLabel.configure(text="✅ Changes Saved Internally!", text_color=COLORS["accent_success"])
                self.after(4000, lambda: self.mmStatusLabel.configure(text=""))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def processUIQueue(self):
        try:
            while True:
                task = self.uiQueue.get_nowait()
                task()
                self.uiQueue.task_done()
        except queue.Empty:
            pass
        self.after(100, self.processUIQueue)

    def applyOutputBlur(self, img, intensity, smoothness):
        radius = self.getDynamicBlurRadius(intensity, smoothness, img.size[0])
        if radius > 0:
            return img.filter(ImageFilter.GaussianBlur(radius=radius))
        return img

if __name__ == "__main__":
    INSTANCE_PORT = 47382
    
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind(('127.0.0.1', INSTANCE_PORT))
        serverSocket.listen(1)
    except socket.error as e:
        print("Socket error:", e)
        if len(sys.argv) > 1:
            try:
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientSocket.connect(('127.0.0.1', INSTANCE_PORT))
                clientSocket.sendall(sys.argv[1].encode('utf-8'))
                clientSocket.close()
            except Exception:
                pass
        sys.exit(0)

    if getattr(sys, 'frozen', False):
        oldExe = os.path.join(os.path.dirname(sys.executable), "PlateCompiler_old.exe")
        if os.path.exists(oldExe):
            try:
                os.remove(oldExe)
            except Exception:
                pass 

    app = PlateMakerApp()

    def listenForFiles():
        while True:
            try:
                conn, addr = serverSocket.accept()
                data = conn.recv(4096).decode('utf-8')
                if data:
                    app.uiQueue.put(lambda d=data: app.loadExternalFile(d))
                conn.close()
            except Exception:
                pass

    threading.Thread(target=listenForFiles, daemon=True).start()
    
    if '_splash_proc' in globals() and _splash_proc:
        try:
            _splash_proc.terminate()
        except Exception:
            pass

    app.mainloop()
