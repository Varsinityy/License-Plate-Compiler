import sys
import os
import shutil
import requests
import tempfile
import threading
import math
import subprocess
import time
import json
import sys
import io
import queue
import socket
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageTk
from io import BytesIO
import customtkinter as ctk
from tkinter import filedialog, messagebox

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

APP_VERSION = "1.6.1"

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

    def apply(self, sendToCompiler=False):
        self.callback(self.fullImg, sendToCompiler)
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

    def onClick(self, event):
        if hasattr(event.widget, 'master') and event.widget.master == self.pathEntry.master:
            return

        initial = self.appRef.lastDirs.get(self.dirKey, "/")
        path = filedialog.askopenfilename(filetypes=self.fileTypes, initialdir=initial)
        if not path: return

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

class PlateMakerApp(DraggableMixin, ctk.CTk):
    def __init__(self):
        if windll:
            try: windll.shcore.SetProcessDpiAwareness(1)
            except (AttributeError, OSError):
                pass

        super().__init__()
        
        self.adobeIcons = {"ps": None, "ai": None}
        self.configFile = os.path.join(os.path.expanduser("~"), "varsinity_plate_maker.json")
        self.templateUrls = {
            "eu": "https://codehs.com/uploads/b344dbee8c88a9e6ea0afb7d2ef96557",
            "us": "https://codehs.com/uploads/ad7830d1aca402908e58d305be678ea8"
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
        self.lastDirs = {"img": "/", "nrml": "/", "out": "/", "mm_source": "/"} 
        self.mmBlurEnabledVar = ctk.BooleanVar(value=False)
        self.animationsVar = ctk.BooleanVar(value=False)
        
        self.setupGeneratorPage()
        self.setupTemplatesPage()
        self.setupMapMakerPage()
        self.setupSettingsPage()
        self.setupEditorPage()

        self.currentFrame = None
        self.loadConfig()
        self.updateRestoreButtonsVisibility()
        
        self.showPage("dashboard")
        
        self.after(100, self.loadAssetsSafe)

        self.toggleHelpText(self.versionVar.get())

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
                    if key == "ps":
                        self.psBtnEu.configure(image=self.adobeIcons["ps"], text="")
                        self.psBtnUs.configure(image=self.adobeIcons["ps"], text="")
                        self.psBtnOutline.configure(image=self.adobeIcons["ps"], text="") 
                        self.psBtnOutlineEu.configure(image=self.adobeIcons["ps"], text="")
                        self.psBtnPreview.configure(image=self.adobeIcons["ps"], text="")
                    else:
                        self.aiBtnEu.configure(image=self.adobeIcons["ai"], text="")
                        self.aiBtnUs.configure(image=self.adobeIcons["ai"], text="")
                        self.aiBtnOutline.configure(image=self.adobeIcons["ai"], text="") 
                        self.aiBtnOutlineEu.configure(image=self.adobeIcons["ai"], text="")
                        self.aiBtnPreview.configure(image=self.adobeIcons["ai"], text="")
            except (requests.RequestException, OSError, ValueError):
                pass

        for key, url in self.templateUrls.items():
            try:
                res = requests.get(url, timeout=3)
                if res.status_code == 200:
                    img = Image.open(BytesIO(res.content))
                    origW, origH = img.size
                    targetW = 250 if key == "eu" else 200 
                    aspectRatio = origH / origW
                    targetH = int(targetW * aspectRatio)
                    previewImg = ctk.CTkImage(light_image=img, dark_image=img, size=(targetW, targetH))
        
                    if key == "eu":
                        self.euPreviewLabel.configure(image=previewImg, text="")
                    else:
                        self.usPreviewLabel.configure(image=previewImg, text="")
            except (requests.RequestException, OSError, ValueError):
                pass
            
        try:
            outlinePath = resourcePath("outline.png")
            if os.path.exists(outlinePath):
                img = Image.open(outlinePath)
                origW, origH = img.size
                targetW = 200
                targetH = int(targetW * (origH / origW))
                previewImg = ctk.CTkImage(light_image=img, dark_image=img, size=(targetW, targetH))
                if hasattr(self, 'outlinePreviewLabel'):
                    self.outlinePreviewLabel.configure(image=previewImg, text="")
        except (OSError, ValueError):
            pass

        try:
            outlineEuPath = resourcePath("outline eu.png")
            if os.path.exists(outlineEuPath):
                img = Image.open(outlineEuPath)
                origW, origH = img.size
                targetW = 250
                targetH = int(targetW * (origH / origW))
                previewImg = ctk.CTkImage(light_image=img, dark_image=img, size=(targetW, targetH))
                if hasattr(self, 'outlineEuPreviewLabel'):
                    self.outlineEuPreviewLabel.configure(image=previewImg, text="")
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

        self.btnEditor = ctk.CTkButton(self.navFrame, text=" Plate Designer", image=self.loadIcon("square-pen.png"), command=lambda: self.showPage("editor"), **tabStyle)
        self.btnEditor.pack(fill="x", padx=15, pady=3)

        self.btnMapMaker = ctk.CTkButton(self.navFrame, text=" 3D Map Maker", image=self.loadIcon("map.png"), command=lambda: self.showPage("map_maker"), **tabStyle)
        self.btnMapMaker.pack(fill="x", padx=15, pady=3)

        self.btnHistory = ctk.CTkButton(self.navFrame, text=" History", image=self.loadIcon("history.png"), command=lambda: self.showPage("history"), **tabStyle)
        self.btnHistory.pack(fill="x", padx=15, pady=3)

        self.btnPresets = ctk.CTkButton(self.navFrame, text=" Presets", image=self.loadIcon("star.png"), command=lambda: self.showPage("presets"), **tabStyle)
        self.btnPresets.pack(fill="x", padx=15, pady=3)

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

        pageOrder = ["dashboard", "compiler", "templates", "editor", "map_maker", "history", "presets", "settings"]
        
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

        allTabs = [self.btnDashboard, self.btnGenerator, self.btnTemplates, self.btnEditor, self.btnMapMaker, self.btnHistory, self.btnPresets, self.btnSettings]
        for btn in allTabs:
            btn.configure(border_color=COLORS["bg_primary"])
            
        if targetBtn:
            targetBtn.configure(border_color=COLORS["text_muted"])

        self.isAnimating = True
        self.animateIndicator(targetBtn)
        self.animateTransition(getattr(self, "currentFrame", None), targetFrame, direction)

        self.currentPageName = pageName
        self.currentFrame = targetFrame

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

    def setupGeneratorPage(self):
        header = ctk.CTkLabel(self.generatorPage, text="License Plate Compiler", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"), text_color=COLORS["text_primary"])
        header.pack(anchor="w", pady=(0, 15))

        regionFrame = ctk.CTkFrame(self.generatorPage, fg_color="transparent")
        regionFrame.pack(fill="x", pady=(0, 15))

        versionFrame = ctk.CTkFrame(self.generatorPage, fg_color="transparent")
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
        
        regionLabel = ctk.CTkLabel(regionFrame, text="Step 1: Select Target Region:", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_muted"])
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
        dropContainer.pack(fill="x", pady=(5, 15))
        dropContainer.grid_columnconfigure(0, weight=1); dropContainer.grid_columnconfigure(1, weight=1)
        
        self.imageDropZone = DropZone(dropContainer, "Step 2: Drop Source Image", [("Images", "*.png *.jpg *.jpeg")], "img", self)
        self.imageDropZone.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        self.nrmlDropZone = DropZone(dropContainer, "Step 3: Drop 3D Map (Optional)", [("Images", "*.png *.jpg *.jpeg")], "nrml", self)
        self.nrmlDropZone.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        self.updateDropzoneRegions(self.regionVar.get())

        outputFrame = ctk.CTkFrame(self.generatorPage, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        outputFrame.pack(fill="x", pady=(5, 15), ipadx=20, ipady=15)

        headerRow = ctk.CTkFrame(outputFrame, fg_color="transparent")
        headerRow.pack(fill="x", padx=20, pady=(5, 10))

        ctk.CTkLabel(headerRow, text="Step 4: Output Location", font=ctk.CTkFont(weight="bold")).pack(side="left")

        genSwitchesFrame = ctk.CTkFrame(headerRow, fg_color="transparent")
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

        self.compilerBackupSwitch = ctk.CTkSwitch(
            genSwitchesFrame,
            text="Create Backups",
            variable=self.currentBackupVar,
            button_color=COLORS["accent_primary"],
            command=self.onBackupToggle
        )
        self.compilerBackupSwitch.pack(side="left")
        
        self.outputModeVar = ctk.StringVar(value="Global")
        self.modeRow = ctk.CTkFrame(outputFrame, fg_color="transparent")
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
                "name": "Japanese Plate 1", 
                "region": "US & MX", 
                "img": resourcePath("japanese plate 1 diff.png"), 
                "nrml": resourcePath("japanese plate 1 nrml.png")
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
            }
        ]

        self.presetCart = {"eu": None, "us": None}
        self.presetsPage = ctk.CTkScrollableFrame(self.viewContainer, fg_color=COLORS["bg_primary"])
        self.setupPresetsPage()
        
        
        self.outputLabel = ctk.CTkLabel(outputFrame, text="Textures.zip Path:", font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"])
        self.outputLabel.pack(anchor="w", padx=20)
        
        self.helpTextLabel = ctk.CTkLabel(
            outputFrame, 
            text=r"Select your original Textures.zip file in Forza Horizon 5\Content\media\cars\_library", 
            font=ctk.CTkFont(size=11), 
            text_color=COLORS["text_muted"],
            wraplength=500,
            justify="left"
        )
        self.helpTextLabel.pack(anchor="w", padx=20, pady=(0, 5))
        
        genDirRow = ctk.CTkFrame(outputFrame, fg_color="transparent")
        genDirRow.pack(fill="x", padx=20, pady=(0, 5))
        
        self.genDirEntry = ctk.CTkEntry(genDirRow, textvariable=self.genOutputDirVar, fg_color=COLORS["bg_primary"], border_color=COLORS["border"])
        self.genDirEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.genDirEntry.bind("<Button-1>", lambda e: self.browseGenOutputDir())
        
        genDirBtn = ctk.CTkButton(genDirRow, text="Browse", width=80, fg_color=COLORS["bg_card"], command=self.browseGenOutputDir)
        genDirBtn.pack(side="right")

        self.materialsLabel = ctk.CTkLabel(outputFrame, text="Materials.zip Path:", font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"])
        
        self.materialsHelp = ctk.CTkLabel(
            outputFrame, 
            text=r"Select your original Materials.zip file in Forza Horizon 5\Content\media\cars\_library", 
            font=ctk.CTkFont(size=11), 
            text_color=COLORS["text_muted"],
            wraplength=500,
            justify="left"
        )

        self.materialsInputRow = ctk.CTkFrame(outputFrame, fg_color="transparent")

        self.materialsZipEntry = ctk.CTkEntry(self.materialsInputRow, textvariable=self.materialsZipVar, fg_color=COLORS["bg_primary"], border_color=COLORS["border"])
        self.materialsZipEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.materialsZipEntry.bind("<Button-1>", lambda e: self.browseMaterialsZip())
        ctk.CTkButton(self.materialsInputRow, text="Browse", width=80, fg_color=COLORS["bg_card"], command=self.browseMaterialsZip).pack(side="right")

        self.subHelpTextLabel = ctk.CTkLabel(outputFrame, text="", font=ctk.CTkFont(size=11, slant="italic"), text_color=COLORS["text_muted"])

        self.btnGenerate = ctk.CTkButton(
            self.generatorPage, 
            text=" COMPILE PLATES", 
            image=self.loadIcon("package-plus.png", size=24),
            fg_color=COLORS["accent_primary"], 
            height=60,
            width=0,
            font=ctk.CTkFont(size=16, weight="bold"), 
            command=self.runGeneration
        )
        self.btnGenerate.pack(fill="x", padx=0, pady=20, expand=True)

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
            self.outputLabel.configure(text="Car.zip Path:")
            if hasattr(self, "historyOutputLabel"): self.historyOutputLabel.configure(text="Car.zip Path:")
            if hasattr(self, "presetOutputLabel"): self.presetOutputLabel.configure(text="Car.zip Path:")
            self.helpTextLabel.configure(text="Select the .zip file of the car mod you want to apply this plate to.")
            self.subHelpTextLabel.place_forget()
            self.genOutputDirVar.set("Not Selected")
        else:
            self.toggleHelpText(self.versionVar.get())
        self.updateBackupToggleState()
        self.updateMaterialsZipVisibility()

    def browseGenOutputDir(self):
        isCarSpecific = getattr(self, "outputModeVar", None) and self.outputModeVar.get() == "Car-Specific (Car.zip)"
        initial = self.lastDirs.get("out", "/")
        
        if isCarSpecific:
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
            os.makedirs(tempDir, existOk=True)

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

        self.psBtnPreview = ctk.CTkButton(self.previewAdobeBar, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchPreviewInAdobe("photoshop"))
        self.psBtnPreview.pack(side="right", padx=2)

        self.aiBtnPreview = ctk.CTkButton(self.previewAdobeBar, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchPreviewInAdobe("illustrator"))
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

        self.btnSendToCompiler = ctk.CTkButton(
            self.mapMakerPage, 
            text=" SEND TO COMPILER", 
            image=self.loadIcon("package-plus.png", size=20), 
            fg_color=COLORS["accent_primary"], 
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=self.sendMapToCompiler
        )
        self.btnSendToCompiler.pack(fill="x", padx=0, pady=(5, 15))

        self.mapActionInfo = ctk.CTkLabel(self.mapMakerPage, text="", font=ctk.CTkFont(size=11, slant="italic"), text_color=COLORS["text_muted"])
        self.mapActionInfo.pack(pady=(2, 0))

        self.btnPaintMap.bind("<Enter>", lambda e: self.mapActionInfo.configure(text="Manually flatten areas of the map you don't want to be 3D.  "))
        self.btnPaintMap.bind("<Leave>", lambda e: self.mapActionInfo.configure(text=""))
        
        self.btnGenerateMap.bind("<Enter>", lambda e: self.mapActionInfo.configure(text="Save the finished 3D map to your computer.  "))
        self.btnGenerateMap.bind("<Leave>", lambda e: self.mapActionInfo.configure(text=""))

        self.btnSendToCompiler.bind("<Enter>", lambda e: self.mapActionInfo.configure(text="Sends source image and normal map to the compiler."))
        self.btnSendToCompiler.bind("<Leave>", lambda e: self.mapActionInfo.configure(text=""))

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

    def setupTemplatesPage(self):
        header = ctk.CTkLabel(self.templatesPage, text="Plate Templates", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"))
        header.pack(anchor="w", pady=(0, 20))

        cardsFrame = ctk.CTkFrame(self.templatesPage, fg_color="transparent")
        cardsFrame.pack(fill="x")
        cardsFrame.grid_columnconfigure(0, weight=1)
        cardsFrame.grid_columnconfigure(1, weight=1)

        self.euCard = ctk.CTkFrame(cardsFrame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.euCard.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 0))

        self.euPreviewLabel = ctk.CTkLabel(self.euCard, text="Loading EU Preview...")
        self.euPreviewLabel.pack(pady=(20, 10), padx=10, fill="both", expand=True)
        
        self.psBtnEu = ctk.CTkButton(self.euCard, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("eu", "photoshop"))
        self.psBtnEu.place(relx=0.96, rely=0.04, anchor="ne")

        self.aiBtnEu = ctk.CTkButton(self.euCard, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("eu", "illustrator"))
        self.aiBtnEu.place(relx=0.84, rely=0.04, anchor="ne")

        ctk.CTkLabel(self.euCard, text="EU & UK Plate", font=ctk.CTkFont(size=14, weight="bold")).pack()
        ctk.CTkButton(self.euCard, text="Download", fg_color=COLORS["accent_primary"], command=lambda: self.downloadTemplate("eu")).pack(pady=20, padx=20, fill="x")

        self.usCard = ctk.CTkFrame(cardsFrame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.usCard.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 0))

        self.usPreviewLabel = ctk.CTkLabel(self.usCard, text="Loading US Preview...")
        self.usPreviewLabel.pack(pady=(20, 10), padx=10, fill="both", expand=True)
        
        self.psBtnUs = ctk.CTkButton(self.usCard, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("us", "photoshop"))
        self.psBtnUs.place(relx=0.96, rely=0.04, anchor="ne")

        self.aiBtnUs = ctk.CTkButton(self.usCard, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("us", "illustrator"))
        self.aiBtnUs.place(relx=0.84, rely=0.04, anchor="ne")

        ctk.CTkLabel(self.usCard, text="US & MX Plate", font=ctk.CTkFont(size=14, weight="bold")).pack()
        ctk.CTkButton(self.usCard, text="Download", fg_color=COLORS["accent_primary"], command=lambda: self.downloadTemplate("us")).pack(pady=20, padx=20, fill="x")

        self.outlineEuCard = ctk.CTkFrame(cardsFrame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.outlineEuCard.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(15, 0))

        self.outlineEuPreviewLabel = ctk.CTkLabel(self.outlineEuCard, text="Loading Preview...")
        self.outlineEuPreviewLabel.pack(pady=(20, 10), padx=10, fill="both", expand=True)
        
        self.psBtnOutlineEu = ctk.CTkButton(self.outlineEuCard, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("outline_eu", "photoshop"))
        self.psBtnOutlineEu.place(relx=0.96, rely=0.04, anchor="ne")

        self.aiBtnOutlineEu = ctk.CTkButton(self.outlineEuCard, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("outline_eu", "illustrator"))
        self.aiBtnOutlineEu.place(relx=0.84, rely=0.04, anchor="ne")

        ctk.CTkLabel(self.outlineEuCard, text="EU White Outline", font=ctk.CTkFont(size=14, weight="bold")).pack()
        ctk.CTkButton(self.outlineEuCard, text="Download", fg_color=COLORS["accent_primary"], command=lambda: self.downloadTemplate("outline_eu")).pack(pady=20, padx=20, fill="x")

        self.outlineCard = ctk.CTkFrame(cardsFrame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.outlineCard.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(15, 0))

        self.outlinePreviewLabel = ctk.CTkLabel(self.outlineCard, text="Loading Preview...")
        self.outlinePreviewLabel.pack(pady=(20, 10), padx=10, fill="both", expand=True)
        
        self.psBtnOutline = ctk.CTkButton(self.outlineCard, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("outline", "photoshop"))
        self.psBtnOutline.place(relx=0.96, rely=0.04, anchor="ne")

        self.aiBtnOutline = ctk.CTkButton(self.outlineCard, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("outline", "illustrator"))
        self.aiBtnOutline.place(relx=0.84, rely=0.04, anchor="ne")

        ctk.CTkLabel(self.outlineCard, text="US White Outline", font=ctk.CTkFont(size=14, weight="bold")).pack()
        ctk.CTkButton(self.outlineCard, text="Download", fg_color=COLORS["accent_primary"], command=lambda: self.downloadTemplate("outline")).pack(pady=20, padx=20, fill="x")

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
        
        self.defaultOutLatestVar = ctk.StringVar(value=r"C:\XboxGames\Forza Horizon 5\Content\media\cars\_library\Textures.zip")
        self.createPathSetting(compFrame, "Default Output - Latest (_library Textures.zip):", self.defaultOutLatestVar, mode="zip")
        
        self.defaultOutVar = ctk.StringVar(value=r"C:\Games\Forza Horizon 5\media\Stripped\MediaOverride\RC0\Cars\_library")
        self.createPathSetting(compFrame, "Default Output - v1.634 (_library Folder):", self.defaultOutVar, mode="dir")
        
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
        ctk.CTkEntry(row, textvariable=variable, fg_color=COLORS["bg_primary"]).pack(side="left", fill="x", expand=True, padx=(0,10))
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
                    
                    if hasattr(self, 'defaultOutLatestVar'): self.defaultOutLatestVar.set(data.get("default_out_latest", r"C:\XboxGames\Forza Horizon 5\Content\media\cars\_library\Textures.zip"))
                    if hasattr(self, 'defaultOutVar'): self.defaultOutVar.set(data.get("default_out", r"C:\Games\Forza Horizon 5\media\Stripped\MediaOverride\RC0\Cars\_library"))
                    
                    if hasattr(self, 'compLevelVar'): self.compLevelVar.set(data.get("comp_level", "Normal (-mx5)"))
                    if hasattr(self, 'silentModeVar'): self.silentModeVar.set(data.get("silent_mode", False))
                    if hasattr(self, 'animationsVar'): self.animationsVar.set(data.get("animations", True))
                    if hasattr(self, 'materialsZipVar'): self.materialsZipVar.set(data.get("materialsZip", "Not Selected"))
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
                        self.versionVar.set(data.get("version", self.versionVar.get()))

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
                    "default_out_latest": getattr(self, "defaultOutLatestVar", ctk.StringVar(value=r"C:\XboxGames\Forza Horizon 5\Content\media\cars\_library\Textures.zip")).get(),
                    "default_out": getattr(self, "defaultOutVar", ctk.StringVar(value=r"C:\Games\Forza Horizon 5\media\Stripped\MediaOverride\RC0\Cars\_library")).get(),
                    "comp_level": getattr(self, "compLevelVar", ctk.StringVar(value="Normal (-mx5)")).get(),
                    "silent_mode": getattr(self, "silentModeVar", ctk.BooleanVar(value=False)).get(),
                    "backupStates": getattr(self, "backupStates", {}),
                    "animations": getattr(self, "animationsVar", ctk.BooleanVar(value=True)).get(),
                    "materialsZip": getattr(self, "materialsZipVar", ctk.StringVar(value="Not Selected")).get(),
                    "glossy_finish": getattr(self, "glossyVar", ctk.BooleanVar(value=False)).get(),
                    "history": getattr(self, "history", []),
                    "lastDirs": getattr(self, "lastDirs", {"img": "/", "nrml": "/", "out": "/", "mm_source": "/"}),
                    "version": getattr(self, "versionVar", ctk.StringVar(value="Latest (Direct Zip)")).get()
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
                
                if tType == "outline":
                    path = resourcePath("outline.png")
                    if not os.path.exists(path):
                        self.after(0, lambda: messagebox.showerror("Error", "outline.png not found in the app folder."))
                        return
                elif tType == "outline_eu":
                    path = resourcePath("outline eu.png")
                    if not os.path.exists(path):
                        self.after(0, lambda: messagebox.showerror("Error", "outline eu.png not found in the app folder."))
                        return
                else:
                    r = requests.get(self.templateUrls[tType])
                    path = os.path.join(tempfile.gettempdir(), f"{tType}_plate.png")
                    with open(path, "wb") as f: f.write(r.content)
                
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
            if t == "outline":
                src = resourcePath("outline.png")
                if os.path.exists(src):
                    shutil.copyfile(src, os.path.join(d, "US_Blank_Outline_Template.png"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", "outline.png not found."))
                    return
            elif t == "outline_eu":
                src = resourcePath("outline eu.png")
                if os.path.exists(src):
                    shutil.copyfile(src, os.path.join(d, "EU_Blank_Outline_Template.png"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", "outline eu.png not found."))
                    return
            else:
                for key in (["eu", "us"] if t == "both" else [t]):
                    r = requests.get(self.templateUrls[key])
                    with open(os.path.join(d, f"{key.upper()}_Plate_Template.png"), "wb") as f: f.write(r.content)
            self.after(0, lambda: messagebox.showinfo("Success", "Done!"))
        except Exception as e: 
            self.after(0, lambda e=e: messagebox.showerror("Error", str(e)))

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

    def runGeneration(self):
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

        if isCarSpecific:
            if outputBase == "Not Selected" or not os.path.isfile(outputBase) or not outputBase.lower().endswith('.zip'):
                messagebox.showerror("Error", "Please select a valid Car.zip file.")
                return
        else:
            if outputBase == "Not Selected" or (self.versionVar.get() == "1.634.818.0" and not os.path.isdir(outputBase)) or (self.versionVar.get() == "Latest (Direct Zip)" and not os.path.isfile(outputBase)):
                messagebox.showerror("Error", "Please select a valid output folder or Textures.zip file.")
                return

        self.log("Starting plate generation...")
        self.isCompiling = True
        self.spinnerFrame = 0
        self.animateButton()
        threading.Thread(target=self.processFiles, args=(imgPath, nrmlPath, outputBase), daemon=True).start()

    def processFiles(self, imgPath, nrmlPath, outDir, silent=False):
        try:
            outputBase = outDir
            selectedRegion = self.regionVar.get()
            targetFiles = EU_UK_FILES if selectedRegion == "EU & UK" else US_MX_FILES
            atlasFiles = EU_UK_ATLAS_FILES if selectedRegion == "EU & UK" else US_MX_ATLAS_FILES
            isLatest = self.versionVar.get() == "Latest (Direct Zip)"
            szPath = self.szPathVar.get().strip('"')
            compFlag = "-mx1" if "mx1" in self.compLevelVar.get() else "-mx9" if "mx9" in self.compLevelVar.get() else "-mx5"
            isSilent = silent or self.silentModeVar.get()
            isCarSpecific = getattr(self, "outputModeVar", None) and self.outputModeVar.get() == "Car-Specific (Car.zip)"

            if not os.path.exists(szPath):
                szPath = resourcePath("7za.exe")

            if not os.path.exists(szPath): 
                raise FileNotFoundError(f"7-Zip not found.")

            if isCarSpecific:
                self.log("Extracting Car Mod Zip...")
                tempDir = tempfile.mkdtemp()
                subprocess.run([szPath, "x", outputBase, f"-o{tempDir}", "-y"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                carId = os.path.splitext(os.path.basename(outputBase))[0]
                texturesDir = os.path.join(tempDir, "textures")
                materialsDir = os.path.join(tempDir, "materials")
                os.makedirs(texturesDir, existOk=True)
                os.makedirs(materialsDir, existOk=True)
                prefix = "euplate" if selectedRegion == "EU & UK" else "usplate"
                if imgPath and os.path.isfile(imgPath):
                    shutil.copyfile(imgPath, os.path.join(texturesDir, f"{prefix}_diff.swatchbin"))
                if nrmlPath and os.path.isfile(nrmlPath):
                    shutil.copyfile(nrmlPath, os.path.join(texturesDir, f"{prefix}_nrml.swatchbin"))
                isGlossy = getattr(self, "glossyVar", ctk.BooleanVar(value=False)).get()
                sourceMatName = ("eu_glossy.materialbin" if selectedRegion == "EU & UK" else "us_glossy.materialbin") if isGlossy else ("eu.materialbin" if selectedRegion == "EU & UK" else "us.materialbin")
                baseMatPath = resourcePath(sourceMatName)
                if os.path.exists(baseMatPath):
                    destMatName = "eu.materialbin" if selectedRegion == "EU & UK" else "us.materialbin"
                    shutil.copy(baseMatPath, os.path.join(materialsDir, destMatName))
                    modelPath = None
                    for root, dirs, files in os.walk(tempDir):
                        for f in files:
                            if f.lower() == ("PlateEU_a.modelbin" if selectedRegion == "EU & UK" else "PlateUS_a.modelbin").lower():
                                modelPath = os.path.join(root, f)
                                break
                        if modelPath: break
                    if modelPath:
                        if self.currentBackupVar.get():
                            bakPath = modelPath + ".bak"
                            if not os.path.exists(bakPath): shutil.copy2(modelPath, bakPath)
                        self.patchBinaryRegex(modelPath, b'Game:\\\\[mM]edia\\\\cars\\\\[a-zA-Z0-9_\\\\.\\s-]+?\\.materialbin', lambda s, l: f"Game:\\Media\\cars\\{carId}\\materials\\{destMatName}" if any(x in s.lower() for x in ["_base.materialbin", "us.materialbin", "eu.materialbin", "plateus_.materialbin", "plateeu_.materialbin"]) else None)
                    self.patchBinaryRegex(os.path.join(materialsDir, destMatName), b'Game:\\\\[mM]edia\\\\cars\\\\_library\\\\[a-zA-Z0-9_\\\\.\\s-]+?\\.swatchbin', lambda s, l: (f"Game:\\Media\\cars\\{carId}\\textures\\{prefix}_diff.swatchbin" if "diff" in s.lower() else f"Game:\\Media\\cars\\{carId}\\textures\\{prefix}_nrml.swatchbin" if "nrml" in s.lower() else None))
                os.remove(outputBase)
                subprocess.run([szPath, "a", "-tzip", compFlag, outputBase, f"{tempDir}\\*"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                shutil.rmtree(tempDir)
                self.isCompiling = False
                self.totalCompiled += 1
                self.saveConfig(silent=True)
                self.log("Car-specific build complete!")
                if not isSilent: self.after(0, lambda: messagebox.showinfo("Success", "Successfully modified the car mod!"))
                return

            if isLatest:
                libDir = os.path.dirname(outputBase)
                targetTexZip = outputBase
            else:
                libDir = outputBase
                targetTexZip = os.path.join(libDir, "Textures.zip")
            
            targetMatZip = os.path.join(libDir, "Materials.zip")

            self.log(f"Processing {os.path.basename(targetTexZip)}...")
            texTemp = tempfile.mkdtemp()
            if os.path.exists(targetTexZip):
                subprocess.run([szPath, "x", targetTexZip, f"-o{texTemp}", "-y"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            swatchesDir = os.path.join(texTemp, "plates", "swatches")
            os.makedirs(swatchesDir, existOk=True)
            
            if self.currentBackupVar.get():
                for f in targetFiles + atlasFiles:
                    targetFile = os.path.join(swatchesDir, f)
                    if os.path.exists(targetFile): os.replace(targetFile, targetFile + ".bak")
            
            if imgPath and os.path.isfile(imgPath): self.generateSwatches(imgPath, targetFiles, False, swatchesDir)
            if nrmlPath and os.path.isfile(nrmlPath): self.generateSwatches(nrmlPath, targetFiles, True, swatchesDir)
            
            blank = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
            for a in atlasFiles: blank.save(os.path.join(swatchesDir, a), format="PNG")
            
            if os.path.exists(targetTexZip): os.remove(targetTexZip)
            subprocess.run([szPath, "a", "-tzip", compFlag, targetTexZip, "."], cwd=texTemp, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            shutil.rmtree(texTemp)

            if getattr(self, "glossyVar", ctk.BooleanVar(value=False)).get():
                self.log(f"Processing {os.path.basename(targetMatZip)}...")
                matTemp = tempfile.mkdtemp()
                
                if os.path.exists(targetMatZip):
                    subprocess.run([szPath, "x", targetMatZip, f"-o{matTemp}", "-y"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                platesDir = os.path.join(matTemp, "plates")
                os.makedirs(platesDir, existOk=True)
                
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
                    if os.path.exists(targetMatZip): os.remove(targetMatZip)
                    subprocess.run([szPath, "a", "-tzip", compFlag, targetMatZip, "."], cwd=matTemp, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
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
        outputBase = self.genOutputDirVar.get()
        isCarSpecific = getattr(self, "outputModeVar", None) and self.outputModeVar.get() == "Car-Specific (Car.zip)"
        
        if isCarSpecific:
            if outputBase == "Not Selected" or not os.path.isfile(outputBase) or not outputBase.lower().endswith('.zip'):
                messagebox.showerror("Error", "Please select a valid Car.zip file first.")
                return
        else:
            if self.versionVar.get() != "Latest (Direct Zip)" or not os.path.isfile(outputBase):
                messagebox.showerror("Error", "Please select your Textures.zip file in 'Latest' mode first.")
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
                self.log("Extracting Car Mod Zip...")
                subprocess.run([szPath, "x", outputBase, f"-o{tempDir}", "-y"], check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.log("Restoring .bak files in Car Mod...")
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
                    self.log("Rebuilding Car Mod Zip...")
                    compFlag = "-mx1" if "mx1" in self.compLevelVar.get() else "-mx9" if "mx9" in self.compLevelVar.get() else "-mx5"
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
                text=" COMPILE PLATES", 
                image=self.loadIcon("package-plus.png", size=24), 
                state="normal"
            )
            return
        
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.btnGenerate.configure(text=f"{frames[self.spinnerFrame % len(frames)]} COMPILING... (This may take a minute)", state="disabled")
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
        if value == "Latest (Direct Zip)":
            if hasattr(self, "modeRow"):
                self.modeRow.pack_forget()
            if hasattr(self, "historyModeContainer"):
                self.historyModeContainer.pack_forget()
            if hasattr(self, "presetModeContainer"):
                self.presetModeContainer.pack_forget()
                
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

            if getattr(self, "outputModeVar", None) and self.outputModeVar.get() != "Global":
                self.outputModeVar.set("Global")
                self.toggleOutputMode("Global")
        else:
            if hasattr(self, "modeRow") and hasattr(self, "outputLabel") and not self.modeRow.winfo_manager():
                self.modeRow.pack(fill="x", padx=20, pady=(0, 10), before=self.outputLabel)
                
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
            return
            
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
            self.outputLabel.configure(text="Export Folder:")
            if hasattr(self, "historyOutputLabel"): self.historyOutputLabel.configure(text="Export Folder:")
            if hasattr(self, "presetOutputLabel"): self.presetOutputLabel.configure(text="Export Folder:")
            
            self.helpTextLabel.configure(text=r"Select your _library folder at Forza Horizon 5\media\Stripped\MediaOverride\RC0\Cars\_library.     If you don't have a Cars folder in RC0, you must create one along with the '_library' folder inside of it.")
            self.subHelpTextLabel.configure(text="Automatically merges into any existing Textures.zip/Materials.zip you might have from other mods. ")
            self.subHelpTextLabel.place(x=20, rely=0.84)
            
            if hasattr(self, 'defaultOutVar'):
                oldDef = self.defaultOutVar.get()
                self.genOutputDirVar.set(oldDef if oldDef != "Not Selected" else "Not Selected")
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

        ctk.CTkLabel(self.historyTopRow, text="Version:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 10))
        
        historyVersionBorder = ctk.CTkFrame(self.historyTopRow, fg_color=COLORS["bg_secondary"], border_width=2, border_color=COLORS["border"], corner_radius=6)
        historyVersionBorder.pack(side="left", padx=(0, 20))
        
        ctk.CTkOptionMenu(
            historyVersionBorder, 
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
        
        ctk.CTkButton(historyTexRow, text="Browse", width=80, fg_color=COLORS["bg_secondary"], hover_color=COLORS["border"], command=self.browseGenOutputDir).pack(side="left", padx=(0, 10))

        self.histMaterialsZipRow = ctk.CTkFrame(self.historyOutputContainer, fg_color="transparent")
        
        histMatLabel = ctk.CTkLabel(self.histMaterialsZipRow, text="Materials.zip Path:", font=ctk.CTkFont(size=13, weight="bold"))
        histMatLabel.pack(side="left", padx=(0, 10))
        
        self.histMaterialsEntry = ctk.CTkEntry(self.histMaterialsZipRow, textvariable=self.materialsZipVar, fg_color=COLORS["bg_secondary"], border_color=COLORS["border"])
        self.histMaterialsEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.histMaterialsEntry.bind("<Button-1>", lambda e: self.browseMaterialsZip())
        
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
                
            ctk.CTkLabel(card, text=f"{item['region']} - {imgName}").pack(side="left", padx=10)
            
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
            
        regionText = region.get()
        if hasattr(self, 'imageDropZone') and self.imageDropZone:
            self.imageDropZone.regionLabel.configure(text=f"Target: {regionText}")
        if hasattr(self, 'nrmlDropZone') and self.nrmlDropZone:
            self.nrmlDropZone.regionLabel.configure(text=f"Target: {regionText}")

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
            if hasattr(self, 'status_text'):
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
                for chunk in response.iterContent(chunkSize=8192):
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
                if 'old_exe' in locals() and 'current_exe' in locals():
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

        self.stateVar = ctk.StringVar(value="Utah (Black)")
        ctk.CTkLabel(controlsFrame, text="Select State Template:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        self.stateDropdown = ctk.CTkOptionMenu(controlsFrame, variable=self.stateVar, values=list(PLATE_TEMPLATES.keys()), command=self.onStateChange)
        self.stateDropdown.pack(fill="x", padx=20)

        self.plateTextVar = ctk.StringVar(value="EXAMPLE")
        self.charLimitLabel = ctk.CTkLabel(controlsFrame, text="Plate Text (Max 8 chars):", font=ctk.CTkFont(weight="bold"))
        self.charLimitLabel.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.plateTextVar.trace_add("write", self.onTextChange)
        self.textEntry = ctk.CTkEntry(controlsFrame, textvariable=self.plateTextVar, font=ctk.CTkFont(size=16), height=40)
        self.textEntry.pack(fill="x", padx=20, pady=(0, 10))

        self.showTagsVar = ctk.BooleanVar(value=True)
        self.tagsSwitch = ctk.CTkSwitch(
            controlsFrame, 
            text="Show Registration Tags", 
            variable=self.showTagsVar, 
            command=self.updateEditorPreview, 
            button_color=COLORS["accent_primary"]
        )
        self.tagsSwitch.pack(anchor="w", padx=20, pady=(10, 0))

        self.showOutlineVar = ctk.BooleanVar(value=True)
        self.outlineSwitch = ctk.CTkSwitch(
            controlsFrame, 
            text="Outline", 
            variable=self.showOutlineVar, 
            command=self.updateEditorPreview, 
            button_color=COLORS["accent_primary"]
        )

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

        self.btnSendToMm = ctk.CTkButton(
            self.editorPage, 
            text=" OPEN IN 3D MAP MAKER", 
            image=self.loadIcon("map.png", size=20), 
            fg_color=COLORS["accent_primary"], 
            height=50, 
            width=1200,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.sendToMapMaker
        )
        self.btnSendToMm.pack(fill="x", padx=0, pady=(0, 10))

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
            text=" SEND RECOMMENDED TO COMPILER", 
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

        self.onStateChange(self.stateVar.get())

    def onStateChange(self, choice):
        config = PLATE_TEMPLATES.get(choice)
        if not config: return

        charLimit = 10 if "EU" in choice else 8
        if hasattr(self, 'charLimitLabel'):
            self.charLimitLabel.configure(text=f"Plate Text (Max {charLimit} chars):")

        self.tagsSwitch.pack_forget()
        self.outlineSwitch.pack_forget()
        self.cobbSwitch.pack_forget()

        if config.get("has_tags_option", True):
            self.showTagsVar.set(True)
            self.tagsSwitch.pack(anchor="w", padx=20, pady=(10, 0))
        else:
            self.showTagsVar.set(False) 

        if config.get("has_outline_option"):
            self.showOutlineVar.set(True)
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
                font = ImageFont.loadDefault()
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
            
            img.save(savePath, format="PNG")
            messagebox.showinfo("Success", f"Plate saved to:\n{savePath}")

    def sendToMapMaker(self):
        img = self.generatePlateImage()
        if not img:
            messagebox.showerror("Error", "Could not generate plate.")
            return

        tempPath = os.path.normpath(os.path.join(tempfile.gettempdir(), "designer_transfer.png"))
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
            strength, blur, direction = 9.0, 2.0, "Outward"
        else:
            strength, blur, direction = 10.0, 2.5, "Outward"

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
                textMapBase = Image.new("RGBA", baseImg.size, (0, 0, 0, 255))
                draw = ImageDraw.Draw(textMapBase)
                
                fontPath = resourcePath(config["font_file"])
                try:
                    font = ImageFont.truetype(fontPath, config["font_size"])
                except IOError:
                    font = ImageFont.loadDefault()

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
                
                nrmlMap.save(savePath, format="PNG")
                self.uiQueue.put(lambda: messagebox.showinfo("Success", f"Recommended 3D map saved to:\n{savePath}"))
                
            except Exception as e:
                self.uiQueue.put(lambda err=e: messagebox.showerror("Error", f"Could not generate recommended map: {err}"))
            finally:
                self.uiQueue.put(lambda: self.btnDownloadRec.configure(state="normal", text=" DOWNLOAD RECOMMENDED MAP"))

        threading.Thread(target=process, daemon=True).start()

    def sendRecommendedToCompiler(self):
        self.btnSendRecComp.configure(state="disabled", text="⏳ PREPARING...")
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
                strength, blur, direction = (9.0, 2.0, "Outward") if isEu else (10.0, 2.5, "Outward")
                imagePath = resourcePath(config.get("image_no_tags"))
                if not imagePath or not os.path.exists(imagePath):
                    self.uiQueue.put(lambda: messagebox.showerror("Error", "Template not found."))
                    return
                baseImg = Image.open(imagePath)
                textMapBase = Image.new("RGBA", baseImg.size, (0, 0, 0, 255))
                draw = ImageDraw.Draw(textMapBase)
                fontPath = resourcePath(config["font_file"])
                try:
                    font = ImageFont.truetype(fontPath, config["font_size"])
                except IOError:
                    font = ImageFont.loadDefault()
                left, top, right, bottom = font.getbbox(text)
                textWidth, textHeight = right - left, bottom - top
                x, y = config["coords"][0] - (textWidth / 2), config["coords"][1] - (textHeight / 2)
                draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
                nrmlMap = self.createNormalMapData(textMapBase, strength, blur, direction)
                radius = self.getDynamicBlurRadius(strength, blur, baseImg.size[0])
                if radius > 0:
                    nrmlMap = nrmlMap.filter(ImageFilter.GaussianBlur(radius=radius))
                tempImgPath = os.path.normpath(os.path.join(tempfile.gettempdir(), "designer_img.png"))
                tempNrmlPath = os.path.normpath(os.path.join(tempfile.gettempdir(), "designer_rec_map.png"))
                img.save(tempImgPath)
                nrmlMap.save(tempNrmlPath)
                def updateUi():
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
                self.uiQueue.put(updateUi)
            except Exception as e:
                self.uiQueue.put(lambda err=e: messagebox.showerror("Error", f"Could not send recommended map: {err}"))
            finally:
                self.uiQueue.put(lambda: self.btnSendRecComp.configure(state="normal", text=" SEND RECOMMENDED TO COMPILER"))
        threading.Thread(target=process, daemon=True).start()

    def sendMapToCompiler(self):
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
                self.uiQueue.put(updateUi)
            except Exception as e:
                self.uiQueue.put(lambda e=e: messagebox.showerror("Error", f"Failed to generate map: {e}"))
        threading.Thread(target=process, daemon=True).start()

    def updateMaterialsZipVisibility(self, *args):
        isLatest = self.versionVar.get() == "Latest (Direct Zip)"
        isGlobal = getattr(self, "outputModeVar", None) and self.outputModeVar.get() == "Global"
        isGlossy = getattr(self, "glossyVar", ctk.BooleanVar(value=False)).get()
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
                self.histMaterialsZipRow.pack(fill="x", pady=(10, 0), before=self.cartBtn)
            elif not showRow and self.histMaterialsZipRow.winfo_manager():
                self.histMaterialsZipRow.pack_forget()

        if hasattr(self, "presetMaterialsZipRow"):
            if showRow and not self.presetMaterialsZipRow.winfo_manager():
                self.presetMaterialsZipRow.pack(fill="x", pady=(10, 0), before=self.presetCartBtn)
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

        ctk.CTkLabel(self.presetTopRow, text="Version:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 10))
        
        presetVersionBorder = ctk.CTkFrame(self.presetTopRow, fg_color=COLORS["bg_secondary"], border_width=2, border_color=COLORS["border"], corner_radius=6)
        presetVersionBorder.pack(side="left", padx=(0, 20))
        
        ctk.CTkOptionMenu(
            presetVersionBorder, variable=self.versionVar, values=["Latest (Direct Zip)", "1.634.818.0"], 
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
        
        ctk.CTkButton(presetTexRow, text="Browse", width=80, fg_color=COLORS["bg_secondary"], hover_color=COLORS["border"], command=self.browseGenOutputDir).pack(side="left", padx=(0, 10))

        self.presetMaterialsZipRow = ctk.CTkFrame(self.presetOutputContainer, fg_color="transparent")
        
        presetMatLabel = ctk.CTkLabel(self.presetMaterialsZipRow, text="Materials.zip Path:", font=ctk.CTkFont(size=13, weight="bold"))
        presetMatLabel.pack(side="left", padx=(0, 10))
        
        self.presetMaterialsEntry = ctk.CTkEntry(self.presetMaterialsZipRow, textvariable=self.materialsZipVar, fg_color=COLORS["bg_secondary"], border_color=COLORS["border"])
        self.presetMaterialsEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.presetMaterialsEntry.bind("<Button-1>", lambda e: self.browseMaterialsZip())
        
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
        
        rowIdx = 0
        colIdx = 0
        
        for item in self.presetData:
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

            colIdx += 1
            if colIdx > 1:
                colIdx = 0
                rowIdx += 1

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

        self.btnOpenOutput = ctk.CTkButton(
            setGrid,
            text=" Open Output Folder",
            image=self.loadIcon("folder.png", size=14),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["border"],
            height=28,
            command=self.openOutputFolder
        )
        self.btnOpenOutput.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 2))

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

        ctk.CTkLabel(self.dashboardPage, text="Active Plates", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(10, 10))
        self.activePlatesFrame = ctk.CTkFrame(self.dashboardPage, fg_color="transparent")
        self.activePlatesFrame.pack(fill="x")
        self.activePlatesFrame.grid_columnconfigure(0, weight=1)
        self.activePlatesFrame.grid_columnconfigure(1, weight=1)
        
        self.activeEuLabel = ctk.CTkLabel(self.activePlatesFrame, text="Loading EU...", height=80, fg_color=COLORS["bg_secondary"], corner_radius=12)
        self.activeEuLabel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.activeUsLabel = ctk.CTkLabel(self.activePlatesFrame, text="Loading US...", height=80, fg_color=COLORS["bg_secondary"], corner_radius=12)
        self.activeUsLabel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        ctk.CTkLabel(
            self.dashboardPage, 
            text=f"Recent Additions (v{APP_VERSION})", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(20, 10))
        
        self.changelogFrame = ctk.CTkFrame(self.dashboardPage, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.changelogFrame.pack(fill="x", pady=(0, 10))
        self.changelogFrame.grid_columnconfigure(1, weight=1)

        changes = [
            ("New 'Glossy Plates' Toggle", "Added an option to apply a glossy finish to plates, which can be toggled anywhere you compile plates."),
            ("Improved Car-Specific Logic", "Enhanced the logic for the path naming. Now works with cars that have long file names. (Technically only up to a certain point, but you should be good)"),
        ]

        for idx, (title, desc) in enumerate(changes):
            ctk.CTkLabel(self.changelogFrame, text=f"• {title}:", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["accent_primary"]).grid(row=idx, column=0, sticky="nw", padx=(15, 10), pady=8)
            ctk.CTkLabel(self.changelogFrame, text=desc, font=ctk.CTkFont(size=13), text_color=COLORS["text_secondary"], justify="left", wraplength=370).grid(row=idx, column=1, sticky="nw", padx=(0, 15), pady=8)

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
                ctkImg = ctk.CTkImage(light_image=img, dark_image=img, size=(targetW, targetH))
                
                self.uiQueue.put(lambda: self.applyActivePlateUI(label, ctkImg))
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
            isLatest = self.versionVar.get() == "Latest (Direct Zip)"
            
            if isLatest:
                targetZip = self.defaultOutLatestVar.get()
            else:
                outPath = self.defaultOutVar.get()
                if outPath != "Not Selected" and outPath:
                    targetZip = os.path.join(outPath, "Textures.zip")
                else:
                    targetZip = "Not Selected"

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

    def savePaintedNormalMap(self, finalImg, sendToCompiler=False):
        tempPath = os.path.normpath(os.path.join(tempfile.gettempdir(), "last_painted_map.png"))
        
        try:
            finalImg.save(tempPath, format="PNG")
            self.lastMmMap = tempPath 
            
            if sendToCompiler:
                self.sendMapToCompiler() 
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
    
    app.mainloop()
