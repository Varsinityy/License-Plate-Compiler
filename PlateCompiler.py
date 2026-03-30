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
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageTk
from io import BytesIO
import customtkinter as ctk
from tkinter import filedialog, messagebox

def resourcePath(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.normpath(os.path.join(base_path, relative_path))

try:
    from ctypes import windll, c_int, byref, sizeof
except ImportError:
    windll = None

ctk.set_appearance_mode("Dark")

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

APP_VERSION = "1.4.1"

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
    "plate_us2_base_nrml_556f2b0f-4117-4d2c-8350-36b737784fe7.swatchbin"
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

class MaskPainter(ctk.CTkToplevel):
    def __init__(self, master, source_path, mask_path, callback):
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
            except: pass

        self.callback = callback
        self.brush_size = 15
        
        self.draw_color = "red"
        self.mask_color = "black"

        self.container = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"], corner_radius=0, border_width=0)
        self.container.pack(fill="both", expand=True, padx=2, pady=2)

        self.titlebar = ctk.CTkFrame(self.container, fg_color=COLORS["bg_secondary"], height=40, corner_radius=0)
        self.titlebar.pack(fill="x", side="top")
        self.titlebar.pack_propagate(False)
        self.titlebar.bind("<ButtonPress-1>", self.startMove)
        self.titlebar.bind("<B1-Motion>", self.doMove)

        left_frame = ctk.CTkFrame(self.titlebar, fg_color="transparent")
        left_frame.pack(side="left", padx=10, fill="y")
        left_frame.bind("<ButtonPress-1>", self.startMove)
        left_frame.bind("<B1-Motion>", self.doMove)

        try:
            logo_img = master.title_icon_label.cget("image")
            self.title_icon_label = ctk.CTkLabel(left_frame, text="", image=logo_img)
        except Exception:
            self.title_icon_label = ctk.CTkLabel(left_frame, text="🖌️", font=ctk.CTkFont(size=16))
            
        self.title_icon_label.pack(side="left", padx=(5, 5))
        self.title_icon_label.bind("<ButtonPress-1>", self.startMove)
        self.title_icon_label.bind("<B1-Motion>", self.doMove)

        title_label = ctk.CTkLabel(left_frame, text="Draw Custom Mask", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_primary"])
        title_label.pack(side="left", padx=5)
        title_label.bind("<ButtonPress-1>", self.startMove)
        title_label.bind("<B1-Motion>", self.doMove)

        # Close button
        close_btn = ctk.CTkButton(self.titlebar, text="✕", width=45, height=40, fg_color="transparent", hover_color=COLORS["accent_danger"], command=self.destroy, corner_radius=0)
        close_btn.pack(side="right")

        min_btn = ctk.CTkButton(self.titlebar, text="—", width=45, height=40, fg_color="transparent", hover_color=COLORS["bg_card"], command=self.minimizeWindow, corner_radius=0)
        min_btn.pack(side="right")

        self.source_img = Image.open(source_path).convert("RGBA")
        w, h = self.source_img.size
        scale = 800 / w if w > 800 else 1
        self.new_w, self.new_h = int(w * scale), int(h * scale)
        
        self.visual_img = self.source_img.resize((self.new_w, self.new_h)).convert("RGBA")
        
        # Load existing mask and reconstruct the brush strokes
        if mask_path and os.path.exists(mask_path):
            loaded_mask = Image.open(mask_path).convert("L")
            self.mask_img = loaded_mask.resize((self.new_w, self.new_h), Image.NEAREST)
            
            red_layer = Image.new("RGBA", self.visual_img.size, "red")
            white_layer = Image.new("RGBA", self.visual_img.size, "white")
            
            black_mask = self.mask_img.point(lambda p: 255 if p < 10 else 0, mode="L")
            white_mask = self.mask_img.point(lambda p: 255 if p > 245 else 0, mode="L")
            
            self.visual_img.paste(red_layer, (0,0), black_mask)
            self.visual_img.paste(white_layer, (0,0), white_mask)
        else:
            self.mask_img = self.visual_img.copy().convert("L")

        self.visual_draw = ImageDraw.Draw(self.visual_img)
        self.mask_draw = ImageDraw.Draw(self.mask_img)

        self.history = []

        ctrl = ctk.CTkFrame(self.container, fg_color="transparent")
        ctrl.pack(fill="x", padx=10, pady=10)

        # Drawing Mode Buttons
        self.btn_black = ctk.CTkButton(
            ctrl, 
            text=" Black (Inward)", 
            image=self.master.loadIcon("paintbrush.png", size=16),
            fg_color="#1c1c21", 
            border_width=2, 
            border_color=COLORS["accent_primary"], 
            command=lambda: self.setColor("red", "black")
        )
        self.btn_black.pack(side="left", padx=5)
        
        self.btn_white = ctk.CTkButton(
            ctrl, 
            text=" White (Outward)", 
            image=self.master.loadIcon("paintbrush.png", size=16),
            fg_color="#a1a1aa", 
            text_color="black", 
            border_width=2, 
            border_color=COLORS["bg_primary"], 
            command=lambda: self.setColor("white", "white")
        )
        self.btn_white.pack(side="left", padx=5)
        
        self.slider = ctk.CTkSlider(ctrl, from_=2, to=80, command=self.setSize)
        self.slider.set(15)
        self.slider.pack(side="left", padx=10)

        # Action Buttons
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

        self.canvas = ctk.CTkCanvas(self.container, width=self.new_w, height=self.new_h, cursor="crosshair", highlightthickness=0, bg=COLORS["bg_primary"])
        self.canvas.pack(pady=(0, 10), padx=10)

        self.tk_img = ImageTk.PhotoImage(self.visual_img)
        self.canvas_img_id = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        self.canvas.bind("<ButtonPress-1>", self.startPaint)
        self.canvas.bind("<B1-Motion>", self.paint)
        
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-Z>", lambda e: self.undo()) 
        self.canvas.bind("<Control-z>", lambda e: self.undo())
        self.canvas.bind("<Control-Z>", lambda e: self.undo())

    def startMove(self, event):
        self.x = event.x
        self.y = event.y

    def doMove(self, event):
        x = self.winfo_x() + (event.x - self.x)
        y = self.winfo_y() + (event.y - self.y)
        self.geometry(f"+{x}+{y}")

    def minimizeWindow(self):
        try:
            if windll:
                hwnd = windll.user32.GetParent(self.winfo_id())
                windll.user32.ShowWindow(hwnd, 6) 
            else:
                self.iconify()
        except Exception:
            self.iconify()

    def setColor(self, v_color, m_color):
        self.draw_color = v_color
        self.mask_color = m_color
        
        if m_color == "black":
            self.btn_black.configure(border_color=COLORS["accent_primary"])
            self.btn_white.configure(border_color=COLORS["bg_primary"])
        else:
            self.btn_white.configure(border_color=COLORS["accent_primary"])
            self.btn_black.configure(border_color=COLORS["bg_primary"])

    def setSize(self, val): 
        self.brush_size = int(val)

    def startPaint(self, event):
        self.canvas.focus_set() # Ctrl+z undo
        
        if len(self.history) > 20: 
            self.history.pop(0)
        self.history.append((self.visual_img.copy(), self.mask_img.copy()))
        
        self.canvas.delete("brush_stroke")
        self.tk_img = ImageTk.PhotoImage(self.visual_img)
        self.canvas.itemconfig(self.canvas_img_id, image=self.tk_img)
        
        self.paint(event)

    def paint(self, event):
        x, y = event.x, event.y
        r = self.brush_size
        
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=self.draw_color, outline=self.draw_color, tags="brush_stroke")
        
        self.visual_draw.ellipse([x-r, y-r, x+r, y+r], fill=self.draw_color)
        self.mask_draw.ellipse([x-r, y-r, x+r, y+r], fill=self.mask_color)
        
    def undo(self):
        if not self.history:
            return
            
        prev_visual, prev_mask = self.history.pop()
        
        self.visual_img = prev_visual
        self.visual_draw = ImageDraw.Draw(self.visual_img)
        
        self.mask_img = prev_mask
        self.mask_draw = ImageDraw.Draw(self.mask_img)
        
        self.canvas.delete("brush_stroke")
        self.tk_img = ImageTk.PhotoImage(self.visual_img)
        self.canvas.itemconfig(self.canvas_img_id, image=self.tk_img)

    def apply(self):
        temp = os.path.join(tempfile.gettempdir(), "custom_drawn_mask.png")
        final_mask = self.mask_img.resize(self.source_img.size, Image.NEAREST)
        final_mask.save(temp)
        self.callback(temp)
        self.destroy()

class NormalPainter(ctk.CTkToplevel):
    def __init__(self, master, base_img, callback):
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
            except: pass

        self.callback = callback
        self.brush_size = 20
        self.draw_color = "#8080ff" 

        self.container = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"], corner_radius=0, border_width=0)
        self.container.pack(fill="both", expand=True, padx=2, pady=2)

        self.titlebar = ctk.CTkFrame(self.container, fg_color=COLORS["bg_secondary"], height=40, corner_radius=0)
        self.titlebar.pack(fill="x", side="top")
        self.titlebar.pack_propagate(False)
        self.titlebar.bind("<ButtonPress-1>", self.startMove)
        self.titlebar.bind("<B1-Motion>", self.doMove)

        left_frame = ctk.CTkFrame(self.titlebar, fg_color="transparent")
        left_frame.pack(side="left", padx=10, fill="y")
        left_frame.bind("<ButtonPress-1>", self.startMove)
        left_frame.bind("<B1-Motion>", self.doMove)

        title_label = ctk.CTkLabel(left_frame, text="🖌️ Paint Normal Map", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_primary"])
        title_label.pack(side="left", padx=5)
        title_label.bind("<ButtonPress-1>", self.startMove)
        title_label.bind("<B1-Motion>", self.doMove)

        close_btn = ctk.CTkButton(self.titlebar, text="✕", width=45, height=40, fg_color="transparent", hover_color=COLORS["accent_danger"], command=self.destroy, corner_radius=0)
        close_btn.pack(side="right")

        self.full_img = base_img.copy()
        w, h = self.full_img.size
        scale = 800 / w if w > 800 else 1
        self.new_w, self.new_h = int(w * scale), int(h * scale)
        self.scale_factor = 1 / scale
        
        self.visual_img = self.full_img.resize((self.new_w, self.new_h)).convert("RGBA")
        self.visual_draw = ImageDraw.Draw(self.visual_img)
        self.full_draw = ImageDraw.Draw(self.full_img)

        self.history = []

        ctrl = ctk.CTkFrame(self.container, fg_color="transparent")
        ctrl.pack(fill="x", padx=10, pady=10)

        # Mode Button
        self.btn_flat = ctk.CTkButton(
            ctrl, 
            text=" Flatten Area", 
            image=self.master.loadIcon("paintbrush.png", size=16),
            fg_color="#8080ff", 
            text_color="black", 
            hover_color="#6b6bfa", 
            border_width=2, 
            border_color=COLORS["accent_primary"]
        )
        self.btn_flat.pack(side="left", padx=5)
        
        # Action Buttons
        ctk.CTkButton(
            ctrl, 
            text=" Undo", 
            image=self.master.loadIcon("undo.png", size=16),
            width=80, 
            fg_color=COLORS["bg_card"], 
            command=self.undo
        ).pack(side="left", padx=5)

        self.btn_send_comp = ctk.CTkButton(
            ctrl, 
            text=" Send to Compiler", 
            image=self.master.loadIcon("package-plus.png", size=18),
            fg_color=COLORS["accent_primary"], 
            command=lambda: self.apply(send_to_compiler=True)
        )
        self.btn_send_comp.pack(side="right", padx=5)

        self.btn_save = ctk.CTkButton(
            ctrl, 
            text=" Save Changes", 
            image=self.master.loadIcon("square-check-big.png", size=18),
            fg_color="#10b981", 
            command=lambda: self.apply(send_to_compiler=False)
        )
        self.btn_save.pack(side="right", padx=5)

        self.canvas = ctk.CTkCanvas(self.container, width=self.new_w, height=self.new_h, cursor="crosshair", highlightthickness=0, bg=COLORS["bg_primary"])
        self.canvas.pack(pady=(0, 10), padx=10)

        self.tk_img = ImageTk.PhotoImage(self.visual_img)
        self.canvas_img_id = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        self.canvas.bind("<ButtonPress-1>", self.startPaint)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-Z>", lambda e: self.undo()) 
        self.canvas.bind("<Control-z>", lambda e: self.undo())
        self.canvas.bind("<Control-Z>", lambda e: self.undo())

    def startMove(self, event):
        self.x = event.x
        self.y = event.y

    def doMove(self, event):
        x = self.winfo_x() + (event.x - self.x)
        y = self.winfo_y() + (event.y - self.y)
        self.geometry(f"+{x}+{y}")

    def setSize(self, val): 
        self.brush_size = int(val)

    def startPaint(self, event):
        self.canvas.focus_set() 
        if len(self.history) > 20: 
            self.history.pop(0)
        self.history.append((self.visual_img.copy(), self.full_img.copy()))
        
        self.canvas.delete("brush_stroke")
        self.tk_img = ImageTk.PhotoImage(self.visual_img)
        self.canvas.itemconfig(self.canvas_img_id, image=self.tk_img)
        self.paint(event)

    def paint(self, event):
        x, y = event.x, event.y
        r = self.brush_size
        
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=self.draw_color, outline=self.draw_color, tags="brush_stroke")
        self.visual_draw.ellipse([x-r, y-r, x+r, y+r], fill=self.draw_color)
        
        fx, fy = x * self.scale_factor, y * self.scale_factor
        fr = r * self.scale_factor
        self.full_draw.ellipse([fx-fr, fy-fr, fx+fr, fy+fr], fill=self.draw_color)
        
    def undo(self):
        if not self.history: return
        prev_visual, prev_full = self.history.pop()
        
        self.visual_img = prev_visual
        self.full_img = prev_full
        self.visual_draw = ImageDraw.Draw(self.visual_img)
        self.full_draw = ImageDraw.Draw(self.full_img)
        
        self.canvas.delete("brush_stroke")
        self.tk_img = ImageTk.PhotoImage(self.visual_img)
        self.canvas.itemconfig(self.canvas_img_id, image=self.tk_img)

    def apply(self, send_to_compiler=False):
        # Pass both the image and the choice back to the app
        self.callback(self.full_img, send_to_compiler)
        self.destroy()

class DropZone(ctk.CTkFrame):
    def __init__(self, master, label_text, file_types, dir_key, app_ref, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.file_types = file_types
        self.dir_key = dir_key
        self.app_ref = app_ref
        self.command = command
        self.configure(fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=2, border_color=COLORS["border"])
        
        self.inner_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.inner_frame.pack(expand=True, fill="both", padx=3, pady=20)
        
        # Placeholder icon
        self.placeholder_icon = self.app_ref.loadIcon("image.png", size=36)
        self.icon_label = ctk.CTkLabel(self.inner_frame, text="", image=self.placeholder_icon)
        self.icon_label.pack(pady=(10, 5))
        
        self.text_label = ctk.CTkLabel(self.inner_frame, text=label_text, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_secondary"])
        self.text_label.pack(pady=(0, 0))
        
        self.region_label = ctk.CTkLabel(self.inner_frame, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["accent_primary"])
        self.region_label.pack(pady=(0, 5))
        
        self.path_entry = ctk.CTkEntry(self.inner_frame, placeholder_text="No file selected...", height=40, fg_color=COLORS["bg_primary"], border_color=COLORS["border"], justify="center")
        self.path_entry.pack(fill="x", padx=20, pady=(5, 20))
        
        for widget in [self, self.inner_frame, self.icon_label, self.text_label, self.region_label]:
            widget.bind("<Button-1>", self.OnClick)
            
    def updatePreview(self, path):
        try:
            img = Image.open(path)
            w, h = img.size
            aspect = w / h
            target_h = 60
            target_w = int(target_h * aspect)
            if target_w > 180: target_w = 180
            
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(target_w, target_h))
            self.icon_label.configure(image=ctk_img, text="")
        except:
            self.icon_label.configure(text="❌", text_color=COLORS["accent_danger"])

    def OnClick(self, event):
        initial = self.app_ref.last_dirs.get(self.dir_key, "/")
        path = filedialog.askopenfilename(filetypes=self.file_types, initialdir=initial)
        if not path: return

        # Aspect ratio check
        if self.dir_key == "img":
            try:
                img = Image.open(path)
                w, h = img.size
                ratio = w / h
                region = self.app_ref.region_var.get()

                if region == "EU & UK" and ratio < 3.0:
                    messagebox.showerror("Ratio Error", f"It appears you may have inputted a US plate, please input an EU plate or switch the region.\nRegion: {region}")
                    return
                elif region == "US & MX" and ratio > 3.0:
                    messagebox.showerror("Ratio Error", f"It appears you may have inputted an EU plate, please input a US plate or switch the region.\nRegion: {region}")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Could not read image: {e}")
                return

        self.app_ref.last_dirs[self.dir_key] = os.path.dirname(path)
        self.app_ref.saveConfig(silent=True)
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, path)
        self.configure(border_color=COLORS["accent_success"])
        self.updatePreview(path)
        
        if self.command:
            self.command(path)

    def getPath(self):
        return self.path_entry.get().strip('"')

class GradientFrame(ctk.CTkCanvas):
    def __init__(self, master, color1, color2, **kwargs):
        super().__init__(master, highlightthickness=0, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self.DrawGradient)

    def DrawGradient(self, event=None):
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
        self.bind("<Configure>", self.DrawGradient)

    def DrawGradient(self, event=None):
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

class PlateMakerApp(ctk.CTk):
    def __init__(self):
        if windll:
            try: windll.shcore.SetProcessDpiAwareness(1)
            except: pass

        super().__init__()
        
        self.adobe_icons = {"ps": None, "ai": None}
        self.config_file = os.path.join(os.path.expanduser("~"), "varsinity_plate_maker.json")
        self.template_urls = {
            "eu": "https://codehs.com/uploads/b344dbee8c88a9e6ea0afb7d2ef96557",
            "us": "https://codehs.com/uploads/ad7830d1aca402908e58d305be678ea8"
        }

        self.title("Varsinity's Plate Compiler")
        self.geometry("900x750")
        self.configure(fg_color=COLORS["bg_primary"])
        self.overrideredirect(True)
        self.image_cache = {}

        # Initialize UI queue
        self.ui_queue = queue.Queue()
        self.processUiQueue() # Start the listener
        
        self.update_idletasks()
        self.forceTaskbarPresence()
        
        self.after(10, self.applyRoundedCorners)

        self.icon_url = "https://codehs.com/uploads/0da061a56c66f4e0b1a43b52f7341515" 
        self.logo_url = "https://codehs.com/uploads/fd81d80c9192d13a66ec9620d278a1ce" 
        self.ps_icon_url = "https://codehs.com/uploads/4bd09762b019512ffaea5eef10aa673a"
        self.ai_icon_url = "https://codehs.com/uploads/5cd274be304300c4f1db5fdade1dd41a"
        
        self.temp_icon_path = os.path.join(tempfile.gettempdir(), "varsinity_icon_cached.ico")
        
        if os.path.exists(self.temp_icon_path):
            try: self.iconbitmap(self.temp_icon_path)
            except: pass
            
        self.mm_preview_thumb = None
        
        self.mm_preview_thumb = None
        self.mm_preview_job = None

        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.setupTitlebar()
        self.setupSidebar()
        
        # Main view container
        self.view_container = ctk.CTkFrame(self, fg_color=COLORS["bg_content"], corner_radius=15)
        self.view_container.grid(row=1, column=1, sticky="nsew", padx=25, pady=25)
        self.view_container.grid_columnconfigure(0, weight=1)
        self.view_container.grid_rowconfigure(0, weight=1)
        
        self.generator_page = ctk.CTkScrollableFrame(self.view_container, fg_color=COLORS["bg_primary"])
        self.map_maker_page = ctk.CTkScrollableFrame(self.view_container, fg_color=COLORS["bg_primary"])
        self.templates_page = ctk.CTkScrollableFrame(self.view_container, fg_color=COLORS["bg_primary"])
        self.settings_page = ctk.CTkScrollableFrame(self.view_container, fg_color=COLORS["bg_primary"])
        self.editor_page = ctk.CTkScrollableFrame(self.view_container, fg_color=COLORS["bg_primary"])

        self.history = []
        self.cart = {"eu": None, "us": None}
        self.total_compiled = 0
        self.create_backups_var = ctk.BooleanVar(value=True)
        self.silent_mode_var = ctk.BooleanVar(value=False)
        self.last_dirs = {"img": "/", "nrml": "/", "out": "/", "mm_source": "/"} 
        
        self.setupGeneratorPage()
        self.setupTemplatesPage()
        self.setupMapMakerPage()
        self.setupSettingsPage()
        self.setupEditorPage()

        self.current_frame = None
        self.loadConfig()
        
        self.showPage("dashboard")
        
        self.after(100, self.loadAssetsSafe)

        self.toggleHelpText(self.version_var.get())

        self.after(3000, self.checkForUpdates) # Checks 3 seconds after opening
        self.attributes("-alpha", 0.0)
        self.animateOpen()

    def animateClose(self, alpha=1.0):
        if alpha > 0:
            alpha -= 0.1 
            self.attributes("-alpha", alpha)
            self.after(10, lambda: self.animateClose(alpha))
        else:
            self.destroy()

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
                
            # Bind a check to see when the user clicks the taskbar icon
            self.bind("<FocusIn>", self.OnRestore)

    def OnRestore(self, event):
        self.unbind("<FocusIn>")
        
        if not windll:
            self.overrideredirect(True)
            
        # Fade back in
        self.animateOpen(0.0)

    def applyRoundedCorners(self):
        if windll:
            try:
                HWND = windll.user32.GetParent(self.winfo_id())
                windll.dwmapi.DwmSetWindowAttribute(HWND, 33, byref(c_int(2)), sizeof(c_int(2)))
            except: pass

    def loadAssetsSafe(self):
        try:
            response = requests.get(self.icon_url, timeout=3)
            if response.status_code == 200:
                img_data = response.content
                icon_img = Image.open(BytesIO(img_data))
                icon_img.save(self.temp_icon_path, format='ICO', sizes=[(32, 32), (64, 64), (128, 128)])
                try: self.iconbitmap(self.temp_icon_path)
                except: pass
                logo_small = ctk.CTkImage(light_image=icon_img, dark_image=icon_img, size=(20, 20))
                if hasattr(self, 'title_icon_label'):
                    self.title_icon_label.configure(image=logo_small, text="")
        except: pass
            
        try:
            response = requests.get(self.logo_url, timeout=3)
            if response.status_code == 200:
                img_data = response.content
                logo_img = Image.open(BytesIO(img_data))
                target_width = 158
                orig_w, orig_h = logo_img.size
                ratio = orig_h / orig_w
                target_height = int(target_width * ratio)
                logo_image = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(target_width, target_height))
                if hasattr(self, 'logo_label'):
                    self.logo_label.configure(image=logo_image, text="")
        except: pass

        urls = {"ps": self.ps_icon_url, "ai": self.ai_icon_url}
        for key, url in urls.items():
            try:
                res = requests.get(url, timeout=3)
                if res.status_code == 200:
                    img = Image.open(BytesIO(res.content))
                    self.adobe_icons[key] = ctk.CTkImage(light_image=img, dark_image=img, size=(24, 24))
                    if key == "ps":
                        self.ps_btn_eu.configure(image=self.adobe_icons["ps"], text="")
                        self.ps_btn_us.configure(image=self.adobe_icons["ps"], text="")
                        self.ps_btn_outline.configure(image=self.adobe_icons["ps"], text="") 
                        self.ps_btn_outline_eu.configure(image=self.adobe_icons["ps"], text="")
                        self.ps_btn_preview.configure(image=self.adobe_icons["ps"], text="")
                    else:
                        self.ai_btn_eu.configure(image=self.adobe_icons["ai"], text="")
                        self.ai_btn_us.configure(image=self.adobe_icons["ai"], text="")
                        self.ai_btn_outline.configure(image=self.adobe_icons["ai"], text="") 
                        self.ai_btn_outline_eu.configure(image=self.adobe_icons["ai"], text="")
                        self.ai_btn_preview.configure(image=self.adobe_icons["ai"], text="")
            except: pass

        # Template Previews for main EU and US plates
        for key, url in self.template_urls.items():
            try:
                res = requests.get(url, timeout=3)
                if res.status_code == 200:
                    img = Image.open(BytesIO(res.content))
                    orig_w, orig_h = img.size
                    target_w = 250 if key == "eu" else 200 
                    aspect_ratio = orig_h / orig_w
                    target_h = int(target_w * aspect_ratio)
                    preview_img = ctk.CTkImage(light_image=img, dark_image=img, size=(target_w, target_h))
        
                    if key == "eu":
                        self.eu_preview_label.configure(image=preview_img, text="")
                    else:
                        self.us_preview_label.configure(image=preview_img, text="")
            except: pass
            
        # Template Preview for US Outline
        try:
            outline_path = resourcePath("outline.png")
            if os.path.exists(outline_path):
                img = Image.open(outline_path)
                orig_w, orig_h = img.size
                target_w = 200
                target_h = int(target_w * (orig_h / orig_w))
                preview_img = ctk.CTkImage(light_image=img, dark_image=img, size=(target_w, target_h))
                if hasattr(self, 'outline_preview_label'):
                    self.outline_preview_label.configure(image=preview_img, text="")
        except: pass

        # Template Preview for EU Outline
        try:
            outline_eu_path = resourcePath("outline eu.png")
            if os.path.exists(outline_eu_path):
                img = Image.open(outline_eu_path)
                orig_w, orig_h = img.size
                target_w = 250
                target_h = int(target_w * (orig_h / orig_w))
                preview_img = ctk.CTkImage(light_image=img, dark_image=img, size=(target_w, target_h))
                if hasattr(self, 'outline_eu_preview_label'):
                    self.outline_eu_preview_label.configure(image=preview_img, text="")
        except: pass

    def forceTaskbarPresence(self):
        try:
            if not windll: return
            myappid = 'varsinity.platemaker.tool'
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            hwnd = windll.user32.GetParent(self.winfo_id())
            style = windll.user32.GetWindowLongW(hwnd, -20)
            style = style & ~0x00000080 
            style = style | 0x00040000  
            windll.user32.SetWindowLongW(hwnd, -20, style)
            if os.path.exists(self.temp_icon_path):
                self.iconbitmap(self.temp_icon_path)
            self.withdraw()
            self.deiconify()
            self.focus_force()
        except: pass

    def setupTitlebar(self):
        self.titlebar = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=40, corner_radius=0)
        self.titlebar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.titlebar.grid_propagate(False)
        self.titlebar.bind("<ButtonPress-1>", self.startMove)
        self.titlebar.bind("<B1-Motion>", self.doMove)

        left_frame = ctk.CTkFrame(self.titlebar, fg_color="transparent")
        left_frame.pack(side="left", padx=10, fill="y")
        left_frame.bind("<ButtonPress-1>", self.startMove)
        left_frame.bind("<B1-Motion>", self.doMove)

        self.title_icon_label = ctk.CTkLabel(left_frame, text="🚗", font=ctk.CTkFont(size=16))
        self.title_icon_label.pack(side="left", padx=(5, 5))
        
        self.title_icon_label.bind("<ButtonPress-1>", self.startMove)
        self.title_icon_label.bind("<B1-Motion>", self.doMove)

        title_label = ctk.CTkLabel(left_frame, text="Varsinity's Plate Compiler", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_primary"])
        title_label.pack(side="left", padx=5)
        
        title_label.bind("<ButtonPress-1>", self.startMove)
        title_label.bind("<B1-Motion>", self.doMove)

        # Close button
        close_btn = ctk.CTkButton(
            self.titlebar, 
            text="✕", 
            width=45, 
            height=40, 
            fg_color="transparent", 
            hover_color=COLORS["accent_danger"], 
            command=self.animateClose, 
            corner_radius=0
        )
        close_btn.pack(side="right")

        min_btn = ctk.CTkButton(self.titlebar, text="—", width=45, height=40, fg_color="transparent", hover_color=COLORS["bg_card"], command=self.animateMinimize, corner_radius=0)
        min_btn.pack(side="right")

    def minimizeWindow(self):
        try:
            from ctypes import windll
            hwnd = windll.user32.GetParent(self.winfo_id())
            windll.user32.ShowWindow(hwnd, 6)
        except Exception:
            self.iconify()

    def startMove(self, event):
        self.x = event.x
        self.y = event.y

    def doMove(self, event):
        x = self.winfo_x() + (event.x - self.x)
        y = self.winfo_y() + (event.y - self.y)
        self.geometry(f"+{x}+{y}")

    def loadIcon(self, filename, size=20):
        if not hasattr(self, "app_icons"):
            self.app_icons = {}
            
        if filename in self.app_icons:
            return self.app_icons[filename]
            
        path = resourcePath(filename)
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA")
                
                r, g, b, a = img.split()
                img = Image.new("RGBA", img.size, "white")
                img.putalpha(a)
                

                ctk_icon = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
                self.app_icons[filename] = ctk_icon
                return ctk_icon
            except Exception as e:
                print(f"Failed to load icon {filename}: {e}")
                
        return None

    def setupSidebar(self):
        self.nav_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["bg_secondary"], width=200)
        self.nav_frame.grid(row=1, column=0, sticky="nsew")

        # Gradient sidebar
        self.sidebar_gradient = GradientFrame(self.nav_frame, color1="#0f0f12", color2="#18181b")
        self.sidebar_gradient.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Sliding indicator
        self.tab_indicator = ctk.CTkFrame(self.nav_frame, width=4, height=40, corner_radius=2, fg_color=COLORS["accent_primary"])
        self.tab_gradient = HorizontalGradientFrame(self.nav_frame, color1=COLORS["accent_primary"], color2=COLORS["bg_primary"])
        
        # Logo header area
        self.logo_container = ctk.CTkFrame(self.nav_frame, fg_color="transparent", height=80)
        self.logo_container.pack_propagate(False)
        self.logo_container.pack(fill="x", pady=(20, 10))

        self.logo_label = ctk.CTkLabel(self.logo_container, text="PLATE MAKER", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["accent_primary"])
        self.logo_label.pack(pady=25, padx=20)

        # Base style for all page tabs
        tab_style = {
            "anchor": "w", 
            "height": 48, 
            "fg_color": COLORS["bg_primary"], 
            "hover_color": COLORS["border"],
            "corner_radius": 8,
            "font": ctk.CTkFont(size=13, weight="bold"),
            "border_width": 1,                      
            "border_color": COLORS["bg_primary"]    
        }

        self.btn_dashboard = ctk.CTkButton(self.nav_frame, text=" Dashboard", image=self.loadIcon("layout-dashboard.png"), command=lambda: self.showPage("dashboard"), **tab_style)
        self.btn_dashboard.pack(fill="x", padx=15, pady=3)

        self.btn_generator = ctk.CTkButton(self.nav_frame, text=" Compiler", image=self.loadIcon("package-plus.png"), command=lambda: self.showPage("compiler"), **tab_style)
        self.btn_generator.pack(fill="x", padx=15, pady=3)
        
        self.btn_templates = ctk.CTkButton(self.nav_frame, text=" Plate Templates", image=self.loadIcon("book-dashed.png"), command=lambda: self.showPage("templates"), **tab_style)
        self.btn_templates.pack(fill="x", padx=15, pady=3)

        self.btn_editor = ctk.CTkButton(self.nav_frame, text=" Plate Designer", image=self.loadIcon("square-pen.png"), command=lambda: self.showPage("editor"), **tab_style)
        self.btn_editor.pack(fill="x", padx=15, pady=3)

        self.btn_map_maker = ctk.CTkButton(self.nav_frame, text=" 3D Map Maker", image=self.loadIcon("map.png"), command=lambda: self.showPage("map_maker"), **tab_style)
        self.btn_map_maker.pack(fill="x", padx=15, pady=3)

        self.btn_history = ctk.CTkButton(self.nav_frame, text=" History", image=self.loadIcon("history.png"), command=lambda: self.showPage("history"), **tab_style)
        self.btn_history.pack(fill="x", padx=15, pady=3)

        self.btn_presets = ctk.CTkButton(self.nav_frame, text=" Presets", image=self.loadIcon("star.png"), command=lambda: self.showPage("presets"), **tab_style)
        self.btn_presets.pack(fill="x", padx=15, pady=3)

        self.btn_settings = ctk.CTkButton(self.nav_frame, text=" Settings", image=self.loadIcon("settings.png"), command=lambda: self.showPage("settings"), **tab_style)
        self.btn_settings.pack(fill="x", padx=15, pady=3)

        # Bottom version info and status
        self.footer = ctk.CTkFrame(self.nav_frame, fg_color="#18181b")
        self.footer.pack(side="bottom", fill="x", pady=20, padx=20)

        # Container for the version and button
        ver_container = ctk.CTkFrame(self.footer, fg_color="transparent")
        ver_container.pack(fill="x")

        self.status_dot = ctk.CTkLabel(ver_container, text="●", text_color=COLORS["accent_success"], font=ctk.CTkFont(size=14), fg_color="transparent")
        self.status_dot.pack(side="left")
        
        self.is_online = True
        self.animateStatusDot() # Start the animation

        self.status_text = ctk.CTkLabel(ver_container, text=" ONLINE", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_secondary"], fg_color="transparent")
        self.status_text.pack(side="left", padx=2)

        self.ver_label = ctk.CTkLabel(ver_container, text=f"v{APP_VERSION}", font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"], fg_color="transparent")
        self.ver_label.pack(side="right")

        # Update button
        self.btn_update = ctk.CTkButton(
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
        self.btn_update.pack(fill="x", pady=(8, 0))

    def showPage(self, page_name):
        # Prevent spam clicking tabs from breaking the animation
        if getattr(self, "is_animating", False):
            return

        page_order = ["dashboard", "compiler", "templates", "editor", "map_maker", "history", "presets", "settings"]
        
        if not hasattr(self, "current_page_name"):
            self.current_page_name = "compiler"
            
        current_idx = page_order.index(self.current_page_name)
        target_idx = page_order.index(page_name)
        
        direction = 1 if target_idx >= current_idx else -1 

        target_frame = None
        target_btn = None

        if page_name == "dashboard":
            target_frame = self.dashboard_page
            target_btn = self.btn_dashboard
            self.after(250, self.refreshDashboard)
        elif page_name == "compiler":
            target_frame = self.generator_page
            target_btn = self.btn_generator
        elif page_name == "map_maker":
            target_frame = self.map_maker_page
            target_btn = self.btn_map_maker
        elif page_name == "templates":
            target_frame = self.templates_page
            target_btn = self.btn_templates
        elif page_name == "history":
            target_frame = self.history_page
            target_btn = self.btn_history
            self.after(250, self.refreshHistory) 
        elif page_name == "presets":
            target_frame = self.presets_page
            target_btn = self.btn_presets
        elif page_name == "editor":
            target_frame = self.editor_page
            target_btn = self.btn_editor
        elif page_name == "settings":
            target_frame = self.settings_page
            target_btn = self.btn_settings

        if getattr(self, "current_frame", None) == target_frame:
            return

        all_tabs = [self.btn_dashboard, self.btn_generator, self.btn_templates, self.btn_editor, self.btn_map_maker, self.btn_history, self.btn_presets, self.btn_settings]
        for btn in all_tabs:
            btn.configure(border_color=COLORS["bg_primary"])
            
        # Border color for the active tab
        if target_btn:
            target_btn.configure(border_color=COLORS["text_muted"])

        self.is_animating = True
        self.animateIndicator(target_btn)
        self.animateTransition(getattr(self, "current_frame", None), target_frame, direction)

        self.current_page_name = page_name
        self.current_frame = target_frame

    def animateIndicator(self, target_widget, start_time=None, start_y=None, target_y=None):
        duration = 0.25 
        
        if start_time is None:
            self.nav_frame.update_idletasks() 
            if target_widget.winfo_y() <= 10:
                self.after(20, lambda: self.animateIndicator(target_widget, start_time, start_y, target_y))
                return
                
            target_y = target_widget.winfo_y() + 4
            if not self.tab_indicator.winfo_ismapped():
                self.tab_indicator.place(x=8, y=target_y) 
                return
                
            start_y = float(self.tab_indicator.place_info()['y'])
            start_time = time.time()
            
        elapsed = time.time() - start_time
        progress = min(elapsed / duration, 1.0)
        ease = 1 - (1 - progress) ** 3 
        
        current_y = start_y + (target_y - start_y) * ease
        self.tab_indicator.place(x=8, y=current_y) 
        
        if progress < 1.0:
            self.after(5, lambda: self.animateIndicator(target_widget, start_time, start_y, target_y))

    def animateTransition(self, old_frame, new_frame, direction=1, start_time=None):
        if not getattr(self, "animations_var", ctk.BooleanVar(value=True)).get():
            new_frame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
            new_frame.lift()
            self.update_idletasks()
            
            if old_frame:
                old_frame.place_forget()
                
            self.is_animating = False
            return

        duration = 0.25
        
        if start_time is None:
            new_frame.place(relx=0.0, rely=1.0 * direction, relwidth=1.0, relheight=1.0)
            start_time = time.time()
            
        elapsed = time.time() - start_time
        progress = min(elapsed / duration, 1.0)
        ease = 1 - (1 - progress) ** 3 
        
        if old_frame:
            old_frame.place(rely=-ease * direction)
            
        new_frame.place(rely=(1.0 - ease) * direction)
        
        if progress < 1.0:
            self.after(5, lambda: self.animateTransition(old_frame, new_frame, direction, start_time))
        else:
            if old_frame:
                old_frame.place_forget()
            new_frame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
            self.is_animating = False

    def setupGeneratorPage(self):
        header = ctk.CTkLabel(self.generator_page, text="License Plate Compiler", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"), text_color=COLORS["text_primary"])
        header.pack(anchor="w", pady=(0, 15))

        region_frame = ctk.CTkFrame(self.generator_page, fg_color="transparent")
        region_frame.pack(fill="x", pady=(0, 15))

        version_frame = ctk.CTkFrame(self.generator_page, fg_color="transparent")
        version_frame.pack(fill="x", pady=(0, 15))
        
        version_label = ctk.CTkLabel(version_frame, text="GAME VERSION:", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_muted"])
        version_label.pack(side="left", padx=(0, 15))

        self.version_var = ctk.StringVar(value="Latest (Direct Zip)")
        self.version_selector = ctk.CTkSegmentedButton(
            version_frame, values=["Latest (Direct Zip)", "1.634.818.0"], 
            variable=self.version_var, fg_color=COLORS["bg_secondary"], 
            selected_color=COLORS["accent_primary"], text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=12, weight="bold"), height=32,
            command=lambda v: (self.toggleHelpText(v), self.saveConfig(silent=True))
        )

        self.version_selector.pack(side="left")
        
        region_label = ctk.CTkLabel(region_frame, text="Step 1: Select Target Region:", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_muted"])
        region_label.pack(side="left", padx=(0, 15))
        
        self.region_var = ctk.StringVar(value="EU & UK")
        self.region_selector = ctk.CTkSegmentedButton(
            region_frame, values=["EU & UK", "US & MX"], variable=self.region_var,
            fg_color=COLORS["bg_secondary"], selected_color=COLORS["accent_primary"],
            selected_hover_color=COLORS["accent_secondary"], text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=12, weight="bold"), height=32,
            command=self.updateDropzoneRegions
        )
        self.region_selector.pack(side="left")

        drop_container = ctk.CTkFrame(self.generator_page, fg_color="transparent")
        drop_container.pack(fill="x", pady=(5, 15))
        drop_container.grid_columnconfigure(0, weight=1); drop_container.grid_columnconfigure(1, weight=1)
        
        self.image_drop_zone = DropZone(drop_container, "Step 2: Drop Source Image", [("Images", "*.png *.jpg *.jpeg")], "img", self)
        self.image_drop_zone.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        self.nrml_drop_zone = DropZone(drop_container, "Step 3: Drop 3D Map (Optional)", [("Images", "*.png *.jpg *.jpeg")], "nrml", self)
        self.nrml_drop_zone.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        self.updateDropzoneRegions(self.region_var.get())

        # Generator Output Selection
        output_frame = ctk.CTkFrame(self.generator_page, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        output_frame.pack(fill="x", pady=(5, 15), ipadx=20, ipady=15)
        
        ctk.CTkLabel(output_frame, text="Step 4: Output Location", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(5, 10))
        
        self.gen_output_dir_var = ctk.StringVar(value="Not Selected")

        self.history_page = ctk.CTkScrollableFrame(self.view_container, fg_color=COLORS["bg_primary"])
        self.setupHistoryPage()

        self.dashboard_page = ctk.CTkScrollableFrame(self.view_container, fg_color=COLORS["bg_primary"])
        self.setupDashboardPage()

        # Preset data
        self.preset_data = [
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

        self.preset_cart = {"eu": None, "us": None}
        self.presets_page = ctk.CTkScrollableFrame(self.view_container, fg_color=COLORS["bg_primary"])
        self.setupPresetsPage()
        
        
        self.output_label = ctk.CTkLabel(output_frame, text="Textures.zip Path:", font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"])
        self.output_label.pack(anchor="w", padx=20)
        
        self.help_text_label = ctk.CTkLabel(
            output_frame, 
            text=r"Select your original Textures.zip file in Forza Horizon 5\Content\media\cars\_library", 
            font=ctk.CTkFont(size=11), 
            text_color=COLORS["text_muted"],
            wraplength=500,
            justify="left"
        )
        self.help_text_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        gen_dir_row = ctk.CTkFrame(output_frame, fg_color="transparent")
        gen_dir_row.pack(fill="x", padx=20, pady=(0, 5))
        
        self.gen_dir_entry = ctk.CTkEntry(gen_dir_row, textvariable=self.gen_output_dir_var, fg_color=COLORS["bg_primary"], border_color=COLORS["border"])
        self.gen_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.gen_dir_entry.bind("<Button-1>", lambda e: self.BrowseGenOutputDir())
        
        gen_dir_btn = ctk.CTkButton(gen_dir_row, text="Browse", width=80, fg_color=COLORS["bg_card"], command=self.BrowseGenOutputDir)
        gen_dir_btn.pack(side="right")

        self.sub_help_text_label = ctk.CTkLabel(output_frame, text="", font=ctk.CTkFont(size=11, slant="italic"), text_color=COLORS["text_muted"])

        # Compiler action buttons
        self.btn_generate = ctk.CTkButton(
            self.generator_page, 
            text=" COMPILE PLATES", 
            image=self.loadIcon("package-plus.png", size=24),
            fg_color=COLORS["accent_primary"], 
            height=60,
            width=0,
            font=ctk.CTkFont(size=16, weight="bold"), 
            command=self.runGeneration
        )
        self.btn_generate.pack(fill="x", padx=0, pady=20, expand=True)

        self.btn_restore = ctk.CTkButton(
            self.generator_page, 
            text=" RESTORE ORIGINALS", 
            image=self.loadIcon("undo.png", size=18),
            fg_color=COLORS["bg_card"], 
            hover_color=COLORS["accent_danger"], 
            height=40, 
            width=0,
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=self.runRestore
        )
        self.btn_restore.pack(fill="x", padx=0, pady=(0, 20), expand=True)

        self.log_area = ctk.CTkTextbox(self.generator_page, fg_color=COLORS["bg_secondary"], font=("Consolas", 12), height=150)
        self.log_area.pack(fill="both", expand=True)

    def BrowseGenOutputDir(self):
        initial = self.last_dirs.get("out", "/")
        if self.version_var.get() == "Latest (Direct Zip)":
            file = filedialog.askopenfilename(filetypes=[("Zip Archives", "*.zip")], initialdir=initial)
            if file: 
                self.last_dirs["out"] = os.path.dirname(file)
                self.gen_output_dir_var.set(os.path.normpath(file))
                self.saveConfig(silent=True)
        else:
            folder = filedialog.askdirectory(initialdir=initial)
            if folder: 
                self.last_dirs["out"] = folder
                self.gen_output_dir_var.set(os.path.normpath(folder))
                self.saveConfig(silent=True)

    def setupMapMakerPage(self):
        header_frame = ctk.CTkFrame(self.map_maker_page, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="3D Map Maker", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"), text_color=COLORS["text_primary"]).pack(side="left")
        
        right_header_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_header_frame.pack(side="right")

        self.advanced_mode_var = ctk.BooleanVar(value=False)
        
        # Advanced mode switch
        self.adv_switch = ctk.CTkSwitch(
            right_header_frame, 
            text="Advanced Mode", 
            variable=self.advanced_mode_var, 
            command=self.toggleMmAdvanced, 
            button_color=COLORS["accent_primary"]
        )
        self.adv_switch.pack(side="top", anchor="e")
        
        # Info label for advanced mode
        self.adv_info_label = ctk.CTkLabel(right_header_frame, text="", font=ctk.CTkFont(size=10, slant="italic"), text_color=COLORS["text_muted"])
        self.adv_info_label.pack(side="top", anchor="e")

        # Bind hover events to change the info text
        self.adv_switch.bind("<Enter>", lambda e: self.adv_info_label.configure(text="Unlocks masks to control depth for different parts.   "))
        self.adv_switch.bind("<Leave>", lambda e: self.adv_info_label.configure(text=""))

        # Map Maker Instructions
        guide_frame = ctk.CTkFrame(self.map_maker_page, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        guide_frame.pack(fill="x", pady=(0, 20))

        # Main instructions
        guide_text = (
            "Generate a 3D Normal Map to give your plate realistic depth in-game.\n\n"
            "1. Drop your plate image into the 'Source Image' box.\n"
            "2. Adjust Intensity and Smoothness until the preview looks right.\n"
            "3. Use 'Paint Map' to flatten areas (like stickers or bolt holes) that shouldn't extrude."
        )
        ctk.CTkLabel(guide_frame, text=guide_text, font=ctk.CTkFont(size=13), text_color=COLORS["text_secondary"], justify="left", wraplength=580).pack(anchor="w", padx=20, pady=(15, 10))

        # Tip with icon
        ctk.CTkLabel(
            guide_frame, 
            text=" Tip: Toggle 'Advanced Mode' to unlock masking.", 
            image=self.loadIcon("lightbulb.png", size=16), 
            compound="left", # Force image to sit to the left of the text
            font=ctk.CTkFont(size=13, weight="bold"), 
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=20, pady=(0, 15))

        self.mm_drop_container = ctk.CTkFrame(self.map_maker_page, fg_color="transparent")
        self.mm_drop_container.pack(fill="x", pady=(0, 10))
        self.mm_drop_container.grid_columnconfigure(0, weight=1)
        self.mm_drop_container.grid_columnconfigure(1, weight=1)

        # Source image drop zone
        self.mm_drop_zone = DropZone(self.mm_drop_container, "Source Image", [("Images", "*.png *.jpg *.jpeg")], "mm_source", self, command=self.LoadPreviewImage)
        self.mm_drop_zone.grid(row=0, column=0, sticky="nsew", padx=2, columnspan=2)

        self.mm_mask_drop_zone = DropZone(self.mm_drop_container, "B&W Mask", [("Images", "*.png *.jpg *.jpeg")], "nrml", self, command=self.SchedulePreviewUpdate)

        self.preview_frame = ctk.CTkFrame(self.map_maker_page, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"], height=160)
        self.preview_frame.pack(fill="x", pady=(0, 10))
        self.preview_frame.pack_propagate(False)

        # Adobe Launch Buttons for Preview
        self.preview_adobe_bar = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        self.preview_adobe_bar.place(relx=0.98, rely=0.05, anchor="ne")

        self.ps_btn_preview = ctk.CTkButton(self.preview_adobe_bar, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchPreviewInAdobe("photoshop"))
        self.ps_btn_preview.pack(side="right", padx=2)

        self.ai_btn_preview = ctk.CTkButton(self.preview_adobe_bar, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchPreviewInAdobe("illustrator"))
        self.ai_btn_preview.pack(side="right", padx=2)

        self.preview_label = ctk.CTkLabel(self.preview_frame, text="Drop an image to see preview...", text_color=COLORS["text_muted"])
        self.preview_label.pack(expand=True)

        # Settings box
        self.settings_box = ctk.CTkFrame(self.map_maker_page, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.settings_box.pack(fill="x", padx=3, pady=(0, 10))

        # Tab toggle
        self.mm_tab_var = ctk.StringVar(value="Black")
        self.mm_tab_toggle = ctk.CTkSegmentedButton(
            self.settings_box, values=["Black", "White"],
            variable=self.mm_tab_var, fg_color=COLORS["bg_primary"],
            selected_color=COLORS["accent_primary"], command=self.switchMmTabs
        )

        self.slider_container = ctk.CTkFrame(self.settings_box, fg_color="transparent")
        self.slider_container.pack(fill="x", padx=3, pady=(10, 5))

        # Base Sliders
        self.base_slider_frame = ctk.CTkFrame(self.slider_container, fg_color="transparent")
        self.base_slider_frame.pack(fill="x")

        self.base_extrude = ctk.StringVar(value="Inward")
        ctk.CTkLabel(self.base_slider_frame, text="Extrusion Direction", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(0, 0))
        ctk.CTkSegmentedButton(self.base_slider_frame, values=["Inward", "Outward"], variable=self.base_extrude, fg_color=COLORS["bg_primary"], selected_color=COLORS["accent_primary"], command=self.SchedulePreviewUpdate).pack(fill="x", padx=20, pady=(5, 10))
        
        ctk.CTkLabel(self.base_slider_frame, text="Intensity (Depth)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.base_intensity = ctk.CTkSlider(self.base_slider_frame, from_=0.1, to=10.0, button_color=COLORS["accent_primary"], command=self.SchedulePreviewUpdate)
        self.base_intensity.set(2.0)
        self.base_intensity.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(self.base_slider_frame, text="Smoothness (Blur)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.base_blur = ctk.CTkSlider(self.base_slider_frame, from_=0.0, to=5.0, button_color=COLORS["accent_primary"], command=self.SchedulePreviewUpdate)
        self.base_blur.set(0.5)
        self.base_blur.pack(fill="x", padx=20, pady=(0, 10))

        # Mask Sliders (Hidden by default)
        self.mask_slider_frame = ctk.CTkFrame(self.slider_container, fg_color="transparent")

        self.mask_extrude = ctk.StringVar(value="Outward")
        ctk.CTkLabel(self.mask_slider_frame, text="Extrusion Direction", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(0, 0))
        ctk.CTkSegmentedButton(self.mask_slider_frame, values=["Inward", "Outward"], variable=self.mask_extrude, fg_color=COLORS["bg_primary"], selected_color=COLORS["accent_primary"], command=self.SchedulePreviewUpdate).pack(fill="x", padx=20, pady=(5, 10))
        
        ctk.CTkLabel(self.mask_slider_frame, text="Intensity (Depth)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.mask_intensity = ctk.CTkSlider(self.mask_slider_frame, from_=0.1, to=10.0, button_color=COLORS["accent_primary"], command=self.SchedulePreviewUpdate)
        self.mask_intensity.set(5.0)
        self.mask_intensity.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(self.mask_slider_frame, text="Smoothness (Blur)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.mask_blur = ctk.CTkSlider(self.mask_slider_frame, from_=0.0, to=5.0, button_color=COLORS["accent_primary"], command=self.SchedulePreviewUpdate)
        self.mask_blur.set(1.0)
        self.mask_blur.pack(fill="x", padx=20, pady=(0, 10))

        # Export settings
        export_settings_frame = ctk.CTkFrame(self.map_maker_page, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        export_settings_frame.pack(fill="x", pady=(0, 10), ipadx=20, ipady=15)

        ctk.CTkLabel(export_settings_frame, text="Export Settings", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(5, 10))

        self.mm_filename_var = ctk.StringVar(value="plate_nrml")
        ctk.CTkLabel(export_settings_frame, text="File Name:", font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20)
        self.mm_filename_entry = ctk.CTkEntry(export_settings_frame, textvariable=self.mm_filename_var, fg_color=COLORS["bg_primary"], border_color=COLORS["border"])
        self.mm_filename_entry.pack(fill="x", padx=20, pady=(0, 10))

        self.mm_export_dir_var = ctk.StringVar(value="Not Selected")
        ctk.CTkLabel(export_settings_frame, text="Export Folder:", font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20)
        
        dir_row = ctk.CTkFrame(export_settings_frame, fg_color="transparent")
        dir_row.pack(fill="x", padx=20, pady=(0, 5))
        
        self.mm_dir_entry = ctk.CTkEntry(dir_row, textvariable=self.mm_export_dir_var, fg_color=COLORS["bg_primary"], border_color=COLORS["border"])
        self.mm_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        dir_btn = ctk.CTkButton(dir_row, text="Browse", width=80, fg_color=COLORS["bg_card"], command=self.BrowseMmExportDir)
        dir_btn.pack(side="right")

        # The export buttons
        export_btn_frame = ctk.CTkFrame(self.map_maker_page, fg_color="transparent")
        export_btn_frame.pack(fill="x", pady=(0, 5))

        # Export map button
        self.btn_generate_map = ctk.CTkButton(
            export_btn_frame, 
            text=" EXPORT MAP", 
            image=self.loadIcon("download.png", size=20),
            fg_color=COLORS["accent_secondary"], 
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=self.runNormalMapGen
        )
        self.btn_generate_map.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_paint_map = ctk.CTkButton(
            export_btn_frame, 
            text=" PAINT MAP", 
            image=self.loadIcon("paintbrush.png", size=20),
            fg_color=COLORS["accent_secondary"],
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=self.openNormalPainter
        )
        self.btn_paint_map.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Send to compiler button
        self.btn_send_to_compiler = ctk.CTkButton(
            self.map_maker_page, 
            text=" SEND TO COMPILER", 
            image=self.loadIcon("package-plus.png", size=20), 
            fg_color=COLORS["accent_primary"], 
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            command=self.SendMapToCompiler
        )
        self.btn_send_to_compiler.pack(fill="x", padx=0, pady=(5, 15))

        # Hover Info Text
        self.map_action_info = ctk.CTkLabel(self.map_maker_page, text="", font=ctk.CTkFont(size=11, slant="italic"), text_color=COLORS["text_muted"])
        self.map_action_info.pack(pady=(2, 0))

        self.btn_paint_map.bind("<Enter>", lambda e: self.map_action_info.configure(text="Manually flatten areas of the map you don't want to be 3D.  "))
        self.btn_paint_map.bind("<Leave>", lambda e: self.map_action_info.configure(text=""))
        
        self.btn_generate_map.bind("<Enter>", lambda e: self.map_action_info.configure(text="Save the finished 3D map to your computer.  "))
        self.btn_generate_map.bind("<Leave>", lambda e: self.map_action_info.configure(text=""))

        self.btn_send_to_compiler.bind("<Enter>", lambda e: self.map_action_info.configure(text="Sends source image and normal map to the compiler."))
        self.btn_send_to_compiler.bind("<Leave>", lambda e: self.map_action_info.configure(text=""))

        self.mm_status_label = ctk.CTkLabel(self.map_maker_page, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.mm_status_label.pack(pady=(5, 15))

    def BrowseMmExportDir(self):
        initial = self.last_dirs.get("mm_out", "/") # Use specific memory key for map maker export directory
        folder = filedialog.askdirectory(initialdir=initial)
        if folder:
            self.last_dirs["mm_out"] = folder # Remember this specific location
            self.mm_export_dir_var.set(os.path.normpath(folder))
            self.saveConfig(silent=True)

    def LoadPreviewImage(self, path):
        try:
            img = Image.open(path)
            self.mm_preview_thumb = img.copy()
            self.mm_preview_thumb.thumbnail((400, 150))
            self.UpdatePreview()
        except: messagebox.showerror("Error", "Failed to load preview.")

    def SchedulePreviewUpdate(self, _=None):
        if self.mm_preview_job: self.after_cancel(self.mm_preview_job)
        self.mm_preview_job = self.after(150, self.UpdatePreview)

    def UpdatePreview(self):
        if not self.mm_preview_thumb: return
        mask_path = self.mm_mask_drop_zone.getPath() if self.advanced_mode_var.get() else None
        threading.Thread(target=self.GeneratePreviewThread, args=(
            self.base_intensity.get(), self.base_blur.get(), self.base_extrude.get(),
            self.mask_intensity.get(), self.mask_blur.get(), self.mask_extrude.get(), mask_path
        ), daemon=True).start()

    def GeneratePreviewThread(self, b_str, b_blur, b_dir, m_str, m_blur, m_dir, mask_path):
        base_map = self.CreateNormalMapData(self.mm_preview_thumb, b_str, b_blur, b_dir)
        
        if mask_path and os.path.exists(mask_path):
            try:
                mask_img = Image.open(mask_path).convert('L').resize(base_map.size)
                mask_map = self.CreateNormalMapData(self.mm_preview_thumb, m_str, m_blur, m_dir)
                res_img = Image.composite(mask_map, base_map, mask_img)
            except:
                res_img = base_map 
        else:
            res_img = base_map

        ctk_img = ctk.CTkImage(light_image=res_img, dark_image=res_img, size=res_img.size)
        self.after(0, lambda: self.preview_label.configure(image=ctk_img, text=""))

    def CreateNormalMapData(self, img, strength, blur, direction):
        width, height = img.size
        scale_factor = width / 400.0
        adj_strength, adj_blur = strength * scale_factor, blur * scale_factor
        img_l = img.convert('L')
        if adj_blur > 0: img_l = img_l.filter(ImageFilter.GaussianBlur(adj_blur))
        pixels = img_l.load()
        normal_img = Image.new('RGB', (width, height))
        normal_pixels = normal_img.load()
        dir_mult = -1 if direction == "Inward" else 1
        for y in range(height):
            for x in range(width):
                l, r = (x-1 if x>0 else 0), (x+1 if x<width-1 else width-1)
                t, b = (y-1 if y>0 else 0), (y+1 if y<height-1 else height-1)
                dx, dy = (pixels[r, y]-pixels[l, y])*adj_strength*dir_mult, (pixels[x, b]-pixels[x, t])*adj_strength*dir_mult
                dz = 255.0; norm = math.sqrt(dx**2 + dy**2 + dz**2)
                normal_pixels[x, y] = (int((dx/norm+1)*127.5), int((dy/norm+1)*127.5), int((dz/norm+1)*127.5))
        return normal_img

    def runNormalMapGen(self):
        img_path = self.mm_drop_zone.getPath()
        mask_path = self.mm_mask_drop_zone.getPath() if self.advanced_mode_var.get() else None
        save_dir = self.mm_export_dir_var.get()
        filename = self.mm_filename_var.get()

        if not os.path.isfile(img_path): return
        if save_dir == "Not Selected": return

        self.btn_generate_map.configure(state="disabled")
        self.mm_status_label.configure(text="⏳ Exporting High-Res Map... Please wait", text_color=COLORS["accent_secondary"])

        threading.Thread(target=self.ProcessNormalMap, args=(
            img_path, mask_path, 
            self.base_intensity.get(), self.base_blur.get(), self.base_extrude.get(),
            self.mask_intensity.get(), self.mask_blur.get(), self.mask_extrude.get(),
            save_dir, filename
        ), daemon=True).start()

    # Export and paint map buttons
        export_btn_frame = ctk.CTkFrame(self.map_maker_page, fg_color="transparent")
        export_btn_frame.pack(fill="x", pady=(0, 5))

        self.btn_generate_map = ctk.CTkButton(export_btn_frame, text="EXPORT", fg_color=COLORS["accent_secondary"], height=50, font=ctk.CTkFont(size=14, weight="bold"), command=self.runNormalMapGen)
        self.btn_generate_map.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_paint_map = ctk.CTkButton(export_btn_frame, text="PAINT MAP", fg_color=COLORS["accent_primary"], height=50, font=ctk.CTkFont(size=14, weight="bold"), command=self.openNormalPainter)
        self.btn_paint_map.pack(side="left", fill="x", expand=True, padx=(5, 0))

    def ProcessNormalMap(self, img_path, mask_path, b_str, b_blur, b_dir, m_str, m_blur, m_dir, save_dir, filename):
        try:
            img = Image.open(img_path)
            base_map = self.CreateNormalMapData(img, b_str, b_blur, b_dir)
            
            if mask_path and os.path.exists(mask_path):
                mask_img = Image.open(mask_path).convert('L').resize(base_map.size)
                mask_map = self.CreateNormalMapData(img, m_str, m_blur, m_dir)
                final_img = Image.composite(mask_map, base_map, mask_img)
            else:
                final_img = base_map

            if not filename.lower().endswith(".png"): filename += ".png"
            out = os.path.join(save_dir, filename)
            final_img.save(out, format="PNG")
            
            self.after(0, lambda: self.OnExportComplete(True, out))
        except Exception as e: 
            self.after(0, lambda: self.OnExportComplete(False, str(e)))

    def OnExportComplete(self, success, message):
        self.btn_generate_map.configure(state="normal")
        
        if success:
            self.mm_status_label.configure(text="✅ Export Complete!", text_color=COLORS["accent_success"])
            messagebox.showinfo("Success", f"Saved to:\n{message}")
        else:
            self.mm_status_label.configure(text="❌ Export Failed!", text_color=COLORS["accent_danger"])
            messagebox.showerror("Error", message)
            
        self.after(4000, lambda: self.mm_status_label.configure(text=""))

    def setupTemplatesPage(self):
        header = ctk.CTkLabel(self.templates_page, text="Plate Templates", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"))
        header.pack(anchor="w", pady=(0, 20))

        cards_frame = ctk.CTkFrame(self.templates_page, fg_color="transparent")
        cards_frame.pack(fill="x")
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)

        # EU Card (Top Left)
        self.eu_card = ctk.CTkFrame(cards_frame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.eu_card.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 0))

        self.eu_preview_label = ctk.CTkLabel(self.eu_card, text="Loading EU Preview...")
        self.eu_preview_label.pack(pady=(20, 10), padx=10, fill="both", expand=True)
        
        self.ps_btn_eu = ctk.CTkButton(self.eu_card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("eu", "photoshop"))
        self.ps_btn_eu.place(relx=0.96, rely=0.04, anchor="ne")

        self.ai_btn_eu = ctk.CTkButton(self.eu_card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("eu", "illustrator"))
        self.ai_btn_eu.place(relx=0.84, rely=0.04, anchor="ne")

        ctk.CTkLabel(self.eu_card, text="EU & UK Plate", font=ctk.CTkFont(size=14, weight="bold")).pack()
        ctk.CTkButton(self.eu_card, text="Download", fg_color=COLORS["accent_primary"], command=lambda: self.downloadTemplate("eu")).pack(pady=20, padx=20, fill="x")

        # US Card (Top Right)
        self.us_card = ctk.CTkFrame(cards_frame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.us_card.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 0))

        self.us_preview_label = ctk.CTkLabel(self.us_card, text="Loading US Preview...")
        self.us_preview_label.pack(pady=(20, 10), padx=10, fill="both", expand=True)
        
        self.ps_btn_us = ctk.CTkButton(self.us_card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("us", "photoshop"))
        self.ps_btn_us.place(relx=0.96, rely=0.04, anchor="ne")

        self.ai_btn_us = ctk.CTkButton(self.us_card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("us", "illustrator"))
        self.ai_btn_us.place(relx=0.84, rely=0.04, anchor="ne")

        ctk.CTkLabel(self.us_card, text="US & MX Plate", font=ctk.CTkFont(size=14, weight="bold")).pack()
        ctk.CTkButton(self.us_card, text="Download", fg_color=COLORS["accent_primary"], command=lambda: self.downloadTemplate("us")).pack(pady=20, padx=20, fill="x")

        # EU Outline Card (Bottom Left)
        self.outline_eu_card = ctk.CTkFrame(cards_frame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.outline_eu_card.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(15, 0))

        self.outline_eu_preview_label = ctk.CTkLabel(self.outline_eu_card, text="Loading Preview...")
        self.outline_eu_preview_label.pack(pady=(20, 10), padx=10, fill="both", expand=True)
        
        self.ps_btn_outline_eu = ctk.CTkButton(self.outline_eu_card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("outline_eu", "photoshop"))
        self.ps_btn_outline_eu.place(relx=0.96, rely=0.04, anchor="ne")

        self.ai_btn_outline_eu = ctk.CTkButton(self.outline_eu_card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("outline_eu", "illustrator"))
        self.ai_btn_outline_eu.place(relx=0.84, rely=0.04, anchor="ne")

        ctk.CTkLabel(self.outline_eu_card, text="EU White Outline", font=ctk.CTkFont(size=14, weight="bold")).pack()
        ctk.CTkButton(self.outline_eu_card, text="Download", fg_color=COLORS["accent_primary"], command=lambda: self.downloadTemplate("outline_eu")).pack(pady=20, padx=20, fill="x")

        # US Outline Card (Bottom Right)
        self.outline_card = ctk.CTkFrame(cards_frame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.outline_card.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(15, 0))

        self.outline_preview_label = ctk.CTkLabel(self.outline_card, text="Loading Preview...")
        self.outline_preview_label.pack(pady=(20, 10), padx=10, fill="both", expand=True)
        
        self.ps_btn_outline = ctk.CTkButton(self.outline_card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("outline", "photoshop"))
        self.ps_btn_outline.place(relx=0.96, rely=0.04, anchor="ne")

        self.ai_btn_outline = ctk.CTkButton(self.outline_card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launchTemplate("outline", "illustrator"))
        self.ai_btn_outline.place(relx=0.84, rely=0.04, anchor="ne")

        ctk.CTkLabel(self.outline_card, text="US White Outline", font=ctk.CTkFont(size=14, weight="bold")).pack()
        ctk.CTkButton(self.outline_card, text="Download", fg_color=COLORS["accent_primary"], command=lambda: self.downloadTemplate("outline")).pack(pady=20, padx=20, fill="x")

    def setupSettingsPage(self):
        header = ctk.CTkLabel(self.settings_page, text="Settings", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"))
        header.pack(anchor="w", pady=(0, 20))
        
        path_frame = ctk.CTkFrame(self.settings_page, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        path_frame.pack(fill="x", pady=0, ipady=10)
        
        self.ps_path_var = ctk.StringVar(value=r"C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe")
        self.createPathSetting(path_frame, "Photoshop EXE Path:", self.ps_path_var, mode="exe")
        
        self.ai_path_var = ctk.StringVar(value=r"C:\Program Files\Adobe\Adobe Illustrator 2026\Support Files\Contents\Windows\Illustrator.exe")
        self.createPathSetting(path_frame, "Illustrator EXE Path:", self.ai_path_var, mode="exe")
        
        # Check for bundled 7za.exe first, fall back to standard path if missing
        bundled_7z = resourcePath("7za.exe")
        default_7z = bundled_7z if os.path.exists(bundled_7z) else r"C:\Program Files\7-Zip\7z.exe"
        
        self.sz_path_var = ctk.StringVar(value=default_7z)
        self.createPathSetting(path_frame, "7-Zip EXE Path: (Now built in)", self.sz_path_var, mode="exe")
        
        comp_frame = ctk.CTkFrame(self.settings_page, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        comp_frame.pack(fill="x", pady=(10, 0), ipady=5)
        
        # Default output paths
        self.default_out_latest_var = ctk.StringVar(value="C:\XboxGames\Forza Horizon 5\Content\media\cars\_library\Textures.zip")
        self.createPathSetting(comp_frame, "Default Output - Latest (_library Textures.zip):", self.default_out_latest_var, mode="zip")
        
        self.default_out_var = ctk.StringVar(value="C:\Games\Forza Horizon 5\media\Stripped\MediaOverride\RC0\Cars\_library")
        self.createPathSetting(comp_frame, "Default Output - v1.634 (_library Folder):", self.default_out_var, mode="dir")
        
        row = ctk.CTkFrame(comp_frame, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(row, text="Compression:").pack(side="left", padx=(0, 10))
        self.comp_level_var = ctk.StringVar(value="Normal (-mx5)")
        ctk.CTkOptionMenu(row, variable=self.comp_level_var, values=["Fast (-mx1)", "Normal (-mx5)", "Ultra (-mx9)"], fg_color=COLORS["bg_primary"]).pack(side="left")
        
        # Silent Mode Row
        silent_row = ctk.CTkFrame(row, fg_color="transparent")
        silent_row.pack(side="right")

        self.silent_info_label = ctk.CTkLabel(silent_row, text="", font=ctk.CTkFont(size=10, slant="italic"), text_color=COLORS["text_muted"])
        self.silent_info_label.pack(side="top", anchor="e")

        self.silent_mode_var = ctk.BooleanVar(value=False)
        self.silent_switch = ctk.CTkSwitch(silent_row, text="Silent Mode", variable=self.silent_mode_var, button_color=COLORS["accent_primary"])
        self.silent_switch.pack(side="bottom", anchor="e")

        # Bind hover events
        self.silent_switch.bind("<Enter>", lambda e: self.silent_info_label.configure(text="Disables success popups after compiling"))
        self.silent_switch.bind("<Leave>", lambda e: self.silent_info_label.configure(text=""))

        # Settings backup toggle
        backup_row = ctk.CTkFrame(comp_frame, fg_color="transparent")
        backup_row.pack(fill="x", padx=20, pady=(0, 10))
        self.settings_backup_switch = ctk.CTkSwitch(
            backup_row, text="Create Backups during Compilation", 
            variable=self.create_backups_var, button_color=COLORS["accent_primary"], 
            command=lambda: self.saveConfig(silent=True)
        )
        self.settings_backup_switch.pack(side="left")

        # Animations toggle
        self.animations_var = ctk.BooleanVar(value=True)
        anim_row = ctk.CTkFrame(comp_frame, fg_color="transparent")
        anim_row.pack(fill="x", padx=20, pady=(0, 10))
        self.animations_switch = ctk.CTkSwitch(
            anim_row, text="Enable Buggy Page Transitions", 
            variable=self.animations_var, button_color=COLORS["accent_primary"], 
            command=lambda: self.saveConfig(silent=True)
        )
        self.animations_switch.pack(side="left")
        
        # Action buttons
        bottom_row = ctk.CTkFrame(self.settings_page, fg_color="transparent")
        bottom_row.pack(fill="x", pady=20)
        
        ctk.CTkButton(bottom_row, text=" Clear Plate History", image=self.loadIcon("trash.png"), command=self.clearHistory, fg_color=COLORS["bg_card"], hover_color=COLORS["accent_danger"], height=40).pack(side="left")
        ctk.CTkButton(bottom_row, text=" Clear Zip Backups", image=self.loadIcon("brush-cleaning.png"), command=self.promptClearBackups, fg_color=COLORS["bg_card"], hover_color=COLORS["accent_danger"], height=40).pack(side="left", padx=(10, 0))
        ctk.CTkButton(bottom_row, text=" Save Settings", image=self.loadIcon("save.png"), command=self.saveConfig, fg_color=COLORS["accent_success"], height=40).pack(side="right")

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
            self.cart_status.configure(text="Cart Empty")
            self.saveConfig(silent=True)

    def loadConfig(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.total_compiled = data.get("total_compiled", len(getattr(self, "history", [])))
                    
                    if hasattr(self, 'ps_path_var'): self.ps_path_var.set(data.get("ps_path", r"C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe"))
                    if hasattr(self, 'ai_path_var'): self.ai_path_var.set(data.get("ai_path", r"C:\Program Files\Adobe\Adobe Illustrator 2026\Support Files\Contents\Windows\Illustrator.exe"))
                    if hasattr(self, 'sz_path_var'): self.sz_path_var.set(data.get("sz_path", r"C:\Program Files\7-Zip\7z.exe"))
                    
                    if hasattr(self, 'default_out_latest_var'): self.default_out_latest_var.set(data.get("default_out_latest", r"C:\XboxGames\Forza Horizon 5\Content\media\cars\_library\Textures.zip"))
                    if hasattr(self, 'default_out_var'): self.default_out_latest_var.set(data.get("default_out_latest", r"C:\Games\Forza Horizon 5\media\Stripped\MediaOverride\RC0\Cars\_library"))
                    
                    if hasattr(self, 'comp_level_var'): self.comp_level_var.set(data.get("comp_level", "Normal (-mx5)"))
                    if hasattr(self, 'silent_mode_var'): self.silent_mode_var.set(data.get("silent_mode", False))
                    if hasattr(self, 'create_backups_var'): self.create_backups_var.set(data.get("create_backups", True))
                    if hasattr(self, 'animations_var'): self.animations_var.set(data.get("animations", True))
                    
                    self.history = data.get("history", [])
                    self.last_dirs = data.get("last_dirs", {"img": "/", "nrml": "/", "out": "/", "mm_source": "/"})
                    
                    if hasattr(self, 'version_var'): self.version_var.set(data.get("version", self.version_var.get()))
            except Exception as e: 
                messagebox.showerror("Save File Error", f"Your save file got corrupted and could not be loaded. It has been reset.\n\nError: {e}")
                self.last_dirs = {"img": "/", "nrml": "/", "out": "/", "mm_source": "/"}
        else: 
            self.last_dirs = {"img": "/", "nrml": "/", "out": "/", "mm_source": "/"}

        # Apply correct default output directory on startup
        if hasattr(self, 'gen_output_dir_var'):
            if self.version_var.get() == "Latest (Direct Zip)":
                if hasattr(self, 'default_out_latest_var') and self.default_out_latest_var.get() != "Not Selected":
                    self.gen_output_dir_var.set(self.default_out_latest_var.get())
            else:
                if hasattr(self, 'default_out_var') and self.default_out_var.get() != "Not Selected":
                    self.gen_output_dir_var.set(self.default_out_var.get())

    def saveConfig(self, silent=False):
        try:
            with open(self.config_file, 'w') as f:
                json.dump({
                    "total_compiled": getattr(self, "total_compiled", 0),
                    "ps_path": getattr(self, "ps_path_var", ctk.StringVar()).get(), 
                    "ai_path": getattr(self, "ai_path_var", ctk.StringVar()).get(),
                    "sz_path": getattr(self, "sz_path_var", ctk.StringVar(value=r"C:\Program Files\7-Zip\7z.exe")).get(),
                    "default_out_latest": getattr(self, "default_out_latest_var", ctk.StringVar(value=r"C:\XboxGames\Forza Horizon 5\Content\media\cars\_library\Textures.zip")).get(),
                    "default_out": getattr(self, "default_out_var", ctk.StringVar(value=r"C:\Games\Forza Horizon 5\media\Stripped\MediaOverride\RC0\Cars\_library")).get(),
                    "comp_level": getattr(self, "comp_level_var", ctk.StringVar(value="Normal (-mx5)")).get(),
                    "silent_mode": getattr(self, "silent_mode_var", ctk.BooleanVar(value=False)).get(),
                    "create_backups": getattr(self, "create_backups_var", ctk.BooleanVar(value=True)).get(),
                    "animations": getattr(self, "animations_var", ctk.BooleanVar(value=True)).get(),
                    "history": getattr(self, "history", []),
                    "last_dirs": getattr(self, "last_dirs", {"img": "/", "nrml": "/", "out": "/", "mm_source": "/"}),
                    "version": getattr(self, "version_var", ctk.StringVar(value="Latest (Direct Zip)")).get()
                }, f)
            if not silent and not getattr(self, "silent_mode_var", ctk.BooleanVar(value=False)).get(): 
                messagebox.showinfo("Success", "Settings saved!")
        except Exception as e: 
            if not silent: 
                messagebox.showerror("Error", f"Failed to save settings to {self.config_file}.\n\nError: {e}")

    def launchTemplate(self, t_type, tool):
        def Task():
            try:
                exe = self.ps_path_var.get().strip('"') if tool == "photoshop" else self.ai_path_var.get().strip('"')
                
                # Check for the local outline files
                if t_type == "outline":
                    path = resourcePath("outline.png")
                    if not os.path.exists(path):
                        self.after(0, lambda: messagebox.showerror("Error", "outline.png not found in the app folder."))
                        return
                elif t_type == "outline_eu":
                    path = resourcePath("outline eu.png")
                    if not os.path.exists(path):
                        self.after(0, lambda: messagebox.showerror("Error", "outline eu.png not found in the app folder."))
                        return
                else:
                    # Otherwise, download the web templates
                    r = requests.get(self.template_urls[t_type])
                    path = os.path.join(tempfile.gettempdir(), f"{t_type}_plate.png")
                    with open(path, "wb") as f: f.write(r.content)
                
                if os.path.isfile(exe):
                    subprocess.Popen([exe, path])
                else:
                    os.startfile(path)
            except Exception as e: self.after(0, lambda: messagebox.showerror("Error", str(e)))
        threading.Thread(target=Task, daemon=True).start()

    def downloadTemplate(self, t_type):
        dir_p = filedialog.askdirectory(); 
        if dir_p: threading.Thread(target=self.ExecuteDownload, args=(dir_p, t_type), daemon=True).start()

    def ExecuteDownload(self, d, t):
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
                    r = requests.get(self.template_urls[key])
                    with open(os.path.join(d, f"{key.upper()}_Plate_Template.png"), "wb") as f: f.write(r.content)
            self.after(0, lambda: messagebox.showinfo("Success", "Done!"))
        except Exception as e: 
            self.after(0, lambda: messagebox.showerror("Error", str(e)))

    def log(self, msg): self.after(0, lambda: (self.log_area.insert("end", f"{msg}\n"), self.log_area.see("end")))

    def runGeneration(self):
        img_path = self.image_drop_zone.getPath()
        nrml_path = self.nrml_drop_zone.getPath()
        output_base = self.gen_output_dir_var.get()

        self.history.append({
            "region": self.region_var.get(), 
            "img": self.image_drop_zone.getPath(), 
            "nrml": self.nrml_drop_zone.getPath()
        })

        self.saveConfig(silent=True)
        
        if not img_path and not nrml_path:
            messagebox.showerror("Error", "Please select at least one file to generate.")
            return
            
        if output_base == "Not Selected" or (self.version_var.get() == "1.634.818.0" and not os.path.isdir(output_base)) or (self.version_var.get() == "Latest (Direct Zip)" and not os.path.isfile(output_base)):
            messagebox.showerror("Error", "Please select a valid output folder or Textures.zip file.")
            return

        self.log("Starting plate generation...")
        self.is_compiling = True
        self.spinner_frame = 0
        self.animateButton()
        threading.Thread(target=self.ProcessFiles, args=(img_path, nrml_path, output_base), daemon=True).start()

    def ProcessFiles(self, img_path, nrml_path, out_dir, silent=False):
        try:
            output_base = out_dir
            selected_region = self.region_var.get()
            target_files = EU_UK_FILES if selected_region == "EU & UK" else US_MX_FILES
            atlas_files = EU_UK_ATLAS_FILES if selected_region == "EU & UK" else US_MX_ATLAS_FILES
            is_latest = self.version_var.get() == "Latest (Direct Zip)"
            
            sz_path = self.sz_path_var.get().strip('"')
            comp_flag = "-mx1" if "mx1" in self.comp_level_var.get() else "-mx9" if "mx9" in self.comp_level_var.get() else "-mx5"
            is_silent = silent or self.silent_mode_var.get()

            if not os.path.exists(sz_path):
                sz_path = resourcePath("7za.exe")

            if not os.path.exists(sz_path): 
                raise FileNotFoundError(f"7-Zip not found. Checked settings and portable fallback.")

            if is_latest:
                # Fallback to portable 7-Zip if settings path is broken
                if not os.path.exists(sz_path):
                    sz_path = resourcePath("7za.exe")

                if not os.path.exists(sz_path): 
                    raise FileNotFoundError(f"7-Zip not found. Checked settings and portable fallback.")
                temp_dir = tempfile.mkdtemp()
                
                self.log("Extracting Textures.zip (this may take a minute)...")
                subprocess.run([sz_path, "x", output_base, f"-o{temp_dir}"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)

                swatches_dir = os.path.join(temp_dir, "plates", "swatches")
                os.makedirs(swatches_dir, exist_ok=True)

                # Backup existing originals if enabled
                if getattr(self, "create_backups_var", ctk.BooleanVar(value=True)).get():
                    self.log("Backing up existing originals to .bak...")
                    for f in target_files + atlas_files:
                        target_file = os.path.join(swatches_dir, f)
                        if os.path.exists(target_file):
                            os.replace(target_file, target_file + ".bak")

                self.log("Generating new plates...")
                if img_path and os.path.isfile(img_path): self.GenerateSwatches(img_path, target_files, False, swatches_dir)
                if nrml_path and os.path.isfile(nrml_path): self.GenerateSwatches(nrml_path, target_files, True, swatches_dir)

                blank = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
                for a in atlas_files: blank.save(os.path.join(swatches_dir, a), format="PNG")

                self.log(f"Rebuilding Textures.zip with {comp_flag} compression...")
                os.remove(output_base)
                subprocess.run([sz_path, "a", "-tzip", comp_flag, output_base, f"{temp_dir}\\*"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)

                shutil.rmtree(temp_dir)
                self.is_compiling = False
                self.total_compiled += 1
                self.saveConfig(silent=True)
                self.log("Build complete!")
                if not is_silent: self.after(0, lambda: messagebox.showinfo("Success", "Successfully extracted, updated, and rebuilt Textures.zip!"))
            else:
                if not os.path.exists(sz_path): raise FileNotFoundError(f"7-Zip not found at {sz_path}")

                target_zip = os.path.join(output_base, "Textures.zip")
                temp_dir = tempfile.mkdtemp()
                
                swatches_dir = os.path.join(temp_dir, "plates", "swatches")
                os.makedirs(swatches_dir, exist_ok=True)

                if os.path.exists(target_zip):
                    self.log("Existing Textures.zip found. Extracting and merging...")
                    subprocess.run([sz_path, "x", target_zip, f"-o{temp_dir}"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    # Backup existing originals if enabled
                    if getattr(self, "create_backups_var", ctk.BooleanVar(value=True)).get():
                        self.log("Backing up originals to .bak...")
                        for f in target_files + atlas_files:
                            target_file = os.path.join(swatches_dir, f)
                            if os.path.exists(target_file):
                                os.replace(target_file, target_file + ".bak")
                else:
                    self.log("No Textures.zip found. Creating a new one...")

                self.log("Generating new plates...")
                if img_path and os.path.isfile(img_path): self.GenerateSwatches(img_path, target_files, False, swatches_dir)
                if nrml_path and os.path.isfile(nrml_path): self.GenerateSwatches(nrml_path, target_files, True, swatches_dir)

                blank = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
                for a in atlas_files: blank.save(os.path.join(swatches_dir, a), format="PNG")

                self.log("Zipping plates folder...")
                if os.path.exists(target_zip): os.remove(target_zip)
                subprocess.run([sz_path, "a", "-tzip", comp_flag, target_zip, f"{temp_dir}\\*"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)

                shutil.rmtree(temp_dir)
                self.is_compiling = False
                self.log("Build complete!")
                if not is_silent:
                    self.after(0, lambda: messagebox.showinfo("Success", "Generation Complete!"))
                
        except Exception as e:
            self.is_compiling = False
            self.after(0, lambda err=e: messagebox.showerror("Generation Error", f"An error occurred:\n{err}"))

    def GenerateSwatches(self, p, t, is_n, out):
        for s in [f for f in t if ("nrml" in f) == is_n]:
            try: 
                shutil.copyfile(p, os.path.join(out, s))
                self.log(f"✓ {s}")
            except: pass

    def runRestore(self):
        output_base = self.gen_output_dir_var.get()
        if self.version_var.get() != "Latest (Direct Zip)" or not os.path.isfile(output_base):
            messagebox.showerror("Error", "Please select your Textures.zip file in 'Latest' mode first.")
            return
            
        threading.Thread(target=self.ProcessRestore, args=(output_base,), daemon=True).start()

    def ProcessRestore(self, output_base):
        try:
            self.log("Starting restore process...")
            sz_path = self.sz_path_var.get().strip('"')

            # Fallback to portable 7-Zip if settings path is broken
            if not os.path.exists(sz_path):
                sz_path = resourcePath("7za.exe")

            if not os.path.exists(sz_path): 
                raise FileNotFoundError(f"7-Zip not found. Checked settings and portable fallback.")
            
            selected_region = self.region_var.get()
            target_files = EU_UK_FILES if selected_region == "EU & UK" else US_MX_FILES
            atlas_files = EU_UK_ATLAS_FILES if selected_region == "EU & UK" else US_MX_ATLAS_FILES

            temp_dir = tempfile.mkdtemp()
            
            self.log("Extracting Textures.zip...")
            subprocess.run([sz_path, "x", output_base, f"-o{temp_dir}"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)

            swatches_dir = os.path.join(temp_dir, "plates", "swatches")
            
            self.log("Restoring .bak files...")
            for f in target_files + atlas_files:
                target_file = os.path.join(swatches_dir, f)
                bak_file = target_file + ".bak"
                
                if os.path.exists(target_file): os.remove(target_file)
                if os.path.exists(bak_file): os.rename(bak_file, target_file)

            self.log("Rebuilding Textures.zip...")
            os.remove(output_base)
            comp_flag = "-mx1" if "mx1" in self.comp_level_var.get() else "-mx9" if "mx9" in self.comp_level_var.get() else "-mx5"
            subprocess.run([sz_path, "a", "-tzip", comp_flag, output_base, f"{temp_dir}\\*"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)

            shutil.rmtree(temp_dir)
            self.log("Restore complete!")
            self.after(0, lambda: messagebox.showinfo("Success", "Original plates restored!"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Restore Error", str(e)))

    def animateButton(self):
        if not getattr(self, "is_compiling", False):
            self.btn_generate.configure(
                text=" COMPILE PLATES", 
                image=self.loadIcon("package-plus.png", size=24), 
                state="normal"
            )
            return
        
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.btn_generate.configure(text=f"{frames[self.spinner_frame % len(frames)]} COMPILING... (This may take a minute)", state="disabled")
        self.spinner_frame += 1
        self.after(100, self.animateButton)

    def toggleHelpText(self, value):
        if value == "Latest (Direct Zip)":
            self.output_label.configure(text="Textures.zip Path:")
            self.help_text_label.configure(text=r"Select your original Textures.zip file in Forza Horizon 5\Content\media\cars\_library")
            self.sub_help_text_label.place_forget()
            
            if hasattr(self, 'default_out_latest_var'):
                latest_def = self.default_out_latest_var.get()
                self.gen_output_dir_var.set(latest_def if latest_def != "Not Selected" else "Not Selected")

        else:
            self.output_label.configure(text="Export Folder:")
            self.help_text_label.configure(text=r"Select your _library folder at Forza Horizon 5\media\Stripped\MediaOverride\RC0\Cars\_library.     If you don't have a Cars folder in RC0, you must create one along with the '_library' folder inside of it.")
            self.sub_help_text_label.configure(text="Automatically merges into any existing Textures.zip you might have from other mods. ")
            self.sub_help_text_label.place(x=20, rely=0.82)
            
            # Swap to 1.634 default output directory
            if hasattr(self, 'default_out_var'):
                old_def = self.default_out_var.get()
                self.gen_output_dir_var.set(old_def if old_def != "Not Selected" else "Not Selected")

    def setupHistoryPage(self):
        ctk.CTkLabel(self.history_page, text="Plate History", font=ctk.CTkFont(size=32, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(
            self.history_page, 
            text="View your previous exports and use them as presets. You can select one EU and one US plate to bundle them into a single compilation.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            wraplength=587,
            justify="left"
        ).pack(anchor="w", padx=(0, 20), pady=(0, 20))
        
        self.cart_status = ctk.CTkLabel(self.history_page, text="No Plates Selected", font=ctk.CTkFont(size=14), text_color=COLORS["accent_primary"])
        self.cart_status.pack(anchor="w", pady=(0, 10))

        settings_frame = ctk.CTkFrame(self.history_page, fg_color="transparent")
        settings_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(settings_frame, text="Version:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 10))
        
        ctk.CTkOptionMenu(
            settings_frame, 
            variable=self.version_var, 
            values=["Latest (Direct Zip)", "1.634.818.0"], 
            width=170, 
            fg_color=COLORS["bg_secondary"], 
            button_color=COLORS["bg_secondary"], 
            button_hover_color=COLORS["border"], 
            dropdown_fg_color=COLORS["bg_card"], 
            dropdown_hover_color=COLORS["border"], 
            dropdown_text_color=COLORS["text_primary"], 
            corner_radius=6,
            command=lambda _: self.saveConfig(silent=True)
        ).pack(side="left", padx=(0, 20))

        ctk.CTkLabel(settings_frame, text="Output:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 10))
        
        self.history_dir_entry = ctk.CTkEntry(settings_frame, textvariable=self.gen_output_dir_var, fg_color=COLORS["bg_secondary"], border_color=COLORS["border"])
        self.history_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.history_dir_entry.bind("<Button-1>", lambda e: self.BrowseGenOutputDir())
        
        ctk.CTkButton(settings_frame, text="Browse", width=80, fg_color=COLORS["bg_secondary"], hover_color=COLORS["border"], command=self.BrowseGenOutputDir).pack(side="left")

        # Compile selected button
        self.cart_btn = ctk.CTkButton(
            self.history_page, 
            text=" COMPILE SELECTED", 
            image=self.loadIcon("package-plus.png", size=20), 
            command=self.compileCart, 
            fg_color=COLORS["accent_secondary"], 
            height=50,
            width=1200,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.cart_btn.pack(fill="x", padx=0, pady=(0, 20))
        
        self.history_list = ctk.CTkFrame(self.history_page, fg_color="transparent")
        self.history_list.pack(fill="both", expand=True)

    def refreshHistory(self):
        for widget in self.history_list.winfo_children(): widget.destroy()
        
        for item in reversed(self.history):
            card = ctk.CTkFrame(self.history_list, fg_color=COLORS["bg_secondary"], corner_radius=8)
            card.pack(fill="x", pady=5, ipadx=10, ipady=10)
            
            img_label = ctk.CTkLabel(card, text="⌛", font=ctk.CTkFont(size=24))
            img_label.pack(side="left", padx=(10, 5))
            
            img_path = item.get('img') or item.get('nrml')
            if img_path and os.path.exists(img_path):
                threading.Thread(target=self.LoadHistoryThumbnail, args=(img_path, img_label), daemon=True).start()
            else:
                # Fallback icon
                img_label.configure(image=self.loadIcon("image.png", size=24), text="")

            if item.get('is_preset'):
                img_name = f"{item['name']} (Preset)"
            else:
                img_name = os.path.basename(item['img']) if item.get('img') else "No Image"
                
            ctk.CTkLabel(card, text=f"{item['region']} - {img_name}").pack(side="left", padx=10)
            
            is_selected = item in self.cart.values()
            region_key = 'us' if item['region'] == "US & MX" else 'eu'
            is_blocked = self.cart[region_key] is not None and self.cart[region_key] != item
            
            btn_text = "Remove" if is_selected else "Select"
            btn_state = "disabled" if is_blocked else "normal"
            btn_color = COLORS["accent_danger"] if is_selected else COLORS["accent_primary"]
            
            # Remove button
            ctk.CTkButton(
                card, 
                text="", 
                image=self.loadIcon("trash.png", size=18),
                width=30, 
                height=30, 
                fg_color="transparent", 
                hover_color=COLORS["accent_danger"], 
                command=lambda i=item: self.deleteHistoryItem(i)
            ).pack(side="right", padx=(0, 10)) # Align remove button

            # Select/Remove Button
            ctk.CTkButton(
                card, 
                text=btn_text, 
                state=btn_state, 
                fg_color=btn_color, 
                command=lambda i=item: self.toggleCart(i)
            ).pack(side="right", padx=10)

    def LoadHistoryThumbnail(self, path, label):
        try:
            pil_img = Image.open(path)
            w, h = pil_img.size
            new_w = int(40 * (w / h))
            pil_img.thumbnail((new_w, 40)) 
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(new_w, 40))
            self.after(0, lambda: label.configure(image=ctk_img, text=""))
        except:
            # Fallback icon
            self.after(0, lambda: label.configure(image=self.loadIcon("image.png", size=24), text=""))

    def toggleCart(self, item):
        region_key = 'us' if item['region'] == "US & MX" else 'eu'
        self.cart[region_key] = None if self.cart[region_key] == item else item
        
        eu_name = os.path.basename(self.cart['eu']['img']) if self.cart['eu'] and self.cart['eu']['img'] else "None"
        us_name = os.path.basename(self.cart['us']['img']) if self.cart['us'] and self.cart['us']['img'] else "None"
        self.cart_status.configure(text=f"EU: {eu_name}  |  US: {us_name}")
        self.refreshHistory()

    def compileCart(self):
        out_dir = self.gen_output_dir_var.get()
        
        if out_dir == "Not Selected" or not out_dir:
            messagebox.showerror("Error", "Please select an output location.")
            return
            
        self.cart_btn.configure(state="disabled", text="⏳ COMPILING...")
        
        def process():
            try:
                if self.cart['eu']: 
                    self.region_var.set("EU & UK")
                    self.ProcessFiles(self.cart['eu']['img'], self.cart['eu']['nrml'], out_dir, silent=True)
                if self.cart['us']: 
                    self.region_var.set("US & MX")
                    self.ProcessFiles(self.cart['us']['img'], self.cart['us']['nrml'], out_dir, silent=True)
                
                self.after(0, lambda: messagebox.showinfo("Success", "Cart compiled successfully!"))
            except Exception as e:
                self.after(0, lambda err=e: messagebox.showerror("Generation Error", f"An error occurred:\n{err}"))
            finally:
                self.after(0, lambda: self.cart_btn.configure(state="normal", text="⚙️ COMPILE CART"))
                
        threading.Thread(target=process, daemon=True).start()

    def deleteHistoryItem(self, item):
        if item in self.history:
            self.history.remove(item)
            
        if self.cart.get('eu') == item: self.cart['eu'] = None
        if self.cart.get('us') == item: self.cart['us'] = None
        
        self.saveConfig(silent=True)
        
        eu_item = self.cart.get('eu')
        us_item = self.cart.get('us')
        
        eu_name = f"{eu_item['name']} (Preset)" if eu_item and eu_item.get('is_preset') else (os.path.basename(eu_item.get('img', '')) if eu_item and eu_item.get('img') else "None")
        us_name = f"{us_item['name']} (Preset)" if us_item and us_item.get('is_preset') else (os.path.basename(us_item.get('img', '')) if us_item and us_item.get('img') else "None")
        
        self.cart_status.configure(text=f"EU: {eu_name}  |  US: {us_name}")
        self.refreshHistory()

    def updateDropzoneRegions(self, *args):
        region = getattr(self, "region_var", None)
        if not region:
            return
            
        region_text = region.get()
        if hasattr(self, 'image_drop_zone') and self.image_drop_zone:
            self.image_drop_zone.region_label.configure(text=f"Target: {region_text}")
        if hasattr(self, 'nrml_drop_zone') and self.nrml_drop_zone:
            self.nrml_drop_zone.region_label.configure(text=f"Target: {region_text}")

    def switchMmTabs(self, tab_name):
        if tab_name == "Black":
            self.mask_slider_frame.pack_forget()
            self.base_slider_frame.pack(fill="x")
        else:
            self.base_slider_frame.pack_forget()
            self.mask_slider_frame.pack(fill="x")

    def toggleMmAdvanced(self):
        if self.advanced_mode_var.get():
            self.mm_drop_zone.grid(row=0, column=0, sticky="nsew", padx=(0, 5), columnspan=1)
            self.mm_mask_drop_zone.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

            # Split into two buttons for new and edit
            if not hasattr(self, 'mask_btns_frame'):
                self.mask_btns_frame = ctk.CTkFrame(self.mm_drop_container, fg_color="transparent")
                
                self.btn_draw_mask = ctk.CTkButton(self.mask_btns_frame, text="🖌️ New Mask", fg_color=COLORS["bg_card"], hover_color=COLORS["border"], command=lambda: self.openMaskPainter(edit=False))
                self.btn_draw_mask.pack(side="left", fill="x", expand=True, padx=(0, 5))

                self.btn_edit_mask = ctk.CTkButton(self.mask_btns_frame, text="✏️ Edit Mask", fg_color=COLORS["bg_card"], hover_color=COLORS["border"], command=lambda: self.openMaskPainter(edit=True))
                self.btn_edit_mask.pack(side="left", fill="x", expand=True, padx=(5, 0))

            self.mask_btns_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="ew")
            
            # Contextual EU tip
            if not hasattr(self, 'eu_tip_label'):
                self.eu_tip_label = ctk.CTkLabel(
                    self.mm_drop_container, 
                    text="Tip For EU Plates - Elements are often too close for masking. It is recommended to export two maps (one inward, one outward) and merge them in an external tool instead.", 
                    font=ctk.CTkFont(size=11, slant="italic"), 
                    text_color=COLORS["accent_secondary"],
                    wraplength=580
                )
            self.eu_tip_label.grid(row=2, column=0, columnspan=2, pady=(10, 0))

            self.mm_tab_toggle.pack(before=self.slider_container, fill="x", padx=20, pady=(15, 5))
        else:
            self.mm_mask_drop_zone.grid_forget()
            self.mm_drop_zone.grid(row=0, column=0, sticky="nsew", padx=2, columnspan=2)

            if hasattr(self, 'mask_btns_frame'):
                self.mask_btns_frame.grid_forget()
                
            # Hide the EU tip when Advanced Mode is off
            if hasattr(self, 'eu_tip_label'):
                self.eu_tip_label.grid_forget()
            
            self.mm_tab_toggle.pack_forget()
            self.mm_tab_var.set("Base Settings")
            self.switchMmTabs("Base Settings")
            
        self.SchedulePreviewUpdate()

    def launchPreviewInAdobe(self, tool):
        if not self.mm_preview_thumb:
            messagebox.showwarning("Warning", "No preview image to open!")
            return

        def Task():
            try:
                exe = self.ps_path_var.get().strip('"') if tool == "photoshop" else self.ai_path_var.get().strip('"')
                
                img_path = self.mm_drop_zone.getPath()
                if not img_path: return
                
                # Get current settings
                b_str, b_blur, b_dir = self.base_intensity.get(), self.base_blur.get(), self.base_extrude.get()
                m_str, m_blur, m_dir = self.mask_intensity.get(), self.mask_blur.get(), self.mask_extrude.get()
                mask_path = self.mm_mask_drop_zone.getPath() if self.advanced_mode_var.get() else None
                
                # Load the full resolution source image
                source_img = Image.open(img_path)
                
                base_map = self.CreateNormalMapData(source_img, b_str, b_blur, b_dir)
                
                if mask_path and os.path.exists(mask_path):
                    mask_img = Image.open(mask_path).convert('L').resize(base_map.size)
                    mask_map = self.CreateNormalMapData(source_img, m_str, m_blur, m_dir)
                    final_img = Image.composite(mask_map, base_map, mask_img)
                else:
                    final_img = base_map

                path = os.path.join(tempfile.gettempdir(), f"map_fullres_adobe_export.png")
                final_img.save(path)
                
                if os.path.isfile(exe):
                    subprocess.Popen([exe, path])
                else:
                    os.startfile(path)
            except Exception as e: 
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to launch {tool}: {e}"))

        threading.Thread(target=Task, daemon=True).start()

    def checkForUpdates(self, manual=False):
        def SetStatus(online):
            self.is_online = online
            if hasattr(self, 'status_text'):
                self.status_text.configure(text=" ONLINE" if online else " OFFLINE")

        def Task():
            try:
                import requests
                import webbrowser
                import re
                
                api_url = "https://api.github.com/repos/Varsinityy/License-Plate-Compiler/releases/latest"
                response = requests.get(api_url, timeout=5)
                
                if response.status_code == 200:
                    self.after(0, lambda: SetStatus(True))
                    
                    data = response.json()
                    latest_tag = data.get("tag_name", f"v{APP_VERSION}")
                    
                    latest_nums = [int(n) for n in re.findall(r'\d+', latest_tag)]
                    current_nums = [int(n) for n in re.findall(r'\d+', APP_VERSION)]
                    
                    while len(latest_nums) < 3: latest_nums.append(0)
                    while len(current_nums) < 3: current_nums.append(0)
                    
                    latest_tuple = tuple(latest_nums[:3])
                    current_tuple = tuple(current_nums[:3])
                    
                    if latest_tuple > current_tuple:
                        def promptUpdate():
                            from PIL import ImageGrab, ImageFilter, ImageEnhance

                            x, y = self.winfo_rootx(), self.winfo_rooty()
                            w, h = self.winfo_width(), self.winfo_height()

                            # Snapshot the app, blur it, and darken it
                            try:
                                screen = ImageGrab.grab(bbox=(x, y, x + w, y + h))
                                # Apply blur
                                blurred = screen.filter(ImageFilter.GaussianBlur(radius=6))
                                darkened = ImageEnhance.Brightness(blurred).enhance(0.6)
                                
                                # Use CTkImage for HighDPI support
                                self.overlay_bg = ctk.CTkImage(light_image=darkened, dark_image=darkened, size=(w, h))
                            except Exception:
                                self.overlay_bg = None

                            # Create the overlay
                            overlay = ctk.CTkToplevel(self)
                            overlay.overrideredirect(True)
                            overlay.geometry(f"{w}x{h}+{x}+{y}")
                            overlay.transient(self)
                            
                            if getattr(self, "overlay_bg", None):
                                bg_label = ctk.CTkLabel(overlay, image=self.overlay_bg, text="")
                                bg_label.pack(fill="both", expand=True)
                            else:
                                overlay.attributes('-alpha', 0.7)
                                overlay.configure(fg_color="#000000")
                            
                            # Create the dialog
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
                                except: pass

                            container = ctk.CTkFrame(dialog, fg_color=COLORS["bg_secondary"], corner_radius=0, border_width=0)
                            container.pack(fill="both", expand=True, padx=2, pady=2)

                            ctk.CTkLabel(container, text="✨ Update Available", font=ctk.CTkFont(size=24, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=(30, 5))
                            
                            badge = ctk.CTkFrame(container, fg_color=COLORS["accent_primary"], corner_radius=6)
                            badge.pack(pady=(0, 15))
                            ctk.CTkLabel(badge, text=f"Version {latest_tag}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#ffffff").pack(padx=10, pady=2)
                            
                            ctk.CTkLabel(container, text="Would you like to install it now?\nThe app will restart automatically.", font=ctk.CTkFont(size=14), text_color=COLORS["text_secondary"], justify="center").pack(pady=(0, 25))

                            btn_frame = ctk.CTkFrame(container, fg_color="transparent")
                            btn_frame.pack(fill="x", pady=(0, 20))

                            def onYes():
                                dialog.destroy()
                                overlay.destroy()
                                exe_url = None
                                for asset in data.get("assets", []):
                                    if asset.get("name", "").endswith(".exe"):
                                        exe_url = asset.get("browser_download_url")
                                        break
                                
                                if exe_url:
                                    threading.Thread(target=self.ExecuteAutoUpdate, args=(exe_url,), daemon=True).start()
                                else:
                                    messagebox.showerror("Error", "Could not find the .exe file in the latest release.")

                            def onNo():
                                dialog.destroy()
                                overlay.destroy()

                            ctk.CTkButton(btn_frame, text="Not Now", width=120, fg_color=COLORS["bg_card"], hover_color=COLORS["border"], command=onNo).pack(side="left", expand=True, padx=(20, 10))
                            ctk.CTkButton(btn_frame, text="Install Update", width=120, fg_color=COLORS["accent_success"], hover_color="#059669", command=onYes).pack(side="right", expand=True, padx=(10, 20))

                        self.after(0, promptUpdate)
                        
                    elif manual:
                        self.after(0, lambda: messagebox.showinfo("Up to Date", "You are running the latest version."))
                else:
                    self.after(0, lambda: SetStatus(False)) # Set Offline on bad status code
                    if manual:
                        self.after(0, lambda: messagebox.showerror("Update Error", "Could not connect to GitHub."))
            except Exception as e:
                self.after(0, lambda: SetStatus(False)) # Set Offline on crash/no internet
                if manual: self.after(0, lambda err=e: messagebox.showerror("Update Error", f"An error occurred: {err}"))

        import threading
        threading.Thread(target=Task, daemon=True).start()

    def ExecuteAutoUpdate(self, download_url):
        try:
            self.after(0, lambda: self.btn_update.configure(text="Preparing...", state="disabled"))
            
            if not getattr(sys, 'frozen', False):
                self.after(0, lambda: messagebox.showinfo("Notice", "Auto-update only works when running the compiled .exe file."))
                self.after(0, lambda: self.btn_update.configure(text="Check for Updates", state="normal"))
                return

            import requests
            import subprocess
            import os
            import time

            current_exe = sys.executable
            base_dir = os.path.dirname(current_exe)
            
            # Generate a unique old_exe name
            old_exe_name = f"PlateCompiler_old_{int(time.time())}.exe"
            old_exe = os.path.join(base_dir, old_exe_name)
            new_exe = os.path.join(base_dir, "PlateCompiler.exe")

            # Rename the running app to free up the filename
            os.rename(current_exe, old_exe)

            # Download the new version with progress tracking
            self.after(0, lambda: self.btn_update.configure(text="Downloading 0%..."))
            
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            last_pct = -1
            
            with open(new_exe, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            pct = int((downloaded / total_size) * 100)
                            if pct != last_pct and pct % 5 == 0:
                                self.after(0, lambda p=pct: self.btn_update.configure(text=f"Downloading {p}%..."))
                                last_pct = pct

            self.after(0, lambda: self.btn_update.configure(text="Installing..."))

            # Create the updater batch script to launch the app cleanly
            bat_path = os.path.join(base_dir, "update_cleanup.bat")
            bat_content = f"""@echo off
timeout /t 3 /nobreak > NUL
del "{old_exe_name}"
explorer.exe "{new_exe}"
del "%~f0"
"""
            with open(bat_path, "w") as f:
                f.write(bat_content)

            # Launch the batch file
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(["cmd.exe", "/c", "update_cleanup.bat"], cwd=base_dir, creationflags=CREATE_NO_WINDOW)

            os._exit(0)

        except Exception as e:
            try:
                if 'old_exe' in locals() and 'current_exe' in locals():
                    if os.path.exists(old_exe) and not os.path.exists(current_exe):
                        os.rename(old_exe, current_exe)
            except Exception:
                pass 
                
            self.after(0, lambda err=e: messagebox.showerror("Update Error", f"Failed to update:\n{err}"))
            self.after(0, lambda: self.btn_update.configure(text="Check for Updates", state="normal"))

    def setupEditorPage(self):
        header = ctk.CTkLabel(self.editor_page, text="Plate Designer", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"))
        header.pack(anchor="w", pady=(0, 20))

        # Controls
        controls_frame = ctk.CTkFrame(self.editor_page, fg_color=COLORS["bg_secondary"], corner_radius=12)
        controls_frame.pack(fill="x", pady=(0, 20), ipadx=20, ipady=20)

        self.state_var = ctk.StringVar(value="Utah (Black)")
        ctk.CTkLabel(controls_frame, text="Select State Template:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        self.state_dropdown = ctk.CTkOptionMenu(controls_frame, variable=self.state_var, values=list(PLATE_TEMPLATES.keys()), command=self.OnStateChange)
        self.state_dropdown.pack(fill="x", padx=20)

        self.plate_text_var = ctk.StringVar(value="EXAMPLE")
        self.char_limit_label = ctk.CTkLabel(controls_frame, text="Plate Text (Max 8 chars):", font=ctk.CTkFont(weight="bold"))
        self.char_limit_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.plate_text_var.trace_add("write", self.OnTextChange)
        self.text_entry = ctk.CTkEntry(controls_frame, textvariable=self.plate_text_var, font=ctk.CTkFont(size=16), height=40)
        self.text_entry.pack(fill="x", padx=20, pady=(0, 10))

        # Registration Tags Toggle
        self.show_tags_var = ctk.BooleanVar(value=True)
        self.tags_switch = ctk.CTkSwitch(
            controls_frame, 
            text="Show Registration Tags", 
            variable=self.show_tags_var, 
            command=self.UpdateEditorPreview, 
            button_color=COLORS["accent_primary"]
        )
        self.tags_switch.pack(anchor="w", padx=20, pady=(10, 0))

        # Outline toggle
        self.show_outline_var = ctk.BooleanVar(value=True)
        self.outline_switch = ctk.CTkSwitch(
            controls_frame, 
            text="Outline", 
            variable=self.show_outline_var, 
            command=self.UpdateEditorPreview, 
            button_color=COLORS["accent_primary"]
        )



        # COBB overlay toggle
        self.show_cobb_var = ctk.BooleanVar(value=True)
        self.cobb_switch = ctk.CTkSwitch(
            controls_frame, 
            text="COBB Logo", 
            variable=self.show_cobb_var, 
            command=self.UpdateEditorPreview, 
            button_color=COLORS["accent_primary"]
        )

        # Preview Area
        self.editor_preview_label = ctk.CTkLabel(self.editor_page, text="Loading Preview...")
        self.editor_preview_label.pack(pady=20)

        # Export plate button
        self.btn_save_custom = ctk.CTkButton(
            self.editor_page, 
            text=" EXPORT PLATE", 
            image=self.loadIcon("download.png", size=20), 
            fg_color=COLORS["accent_secondary"], 
            height=50, 
            width=1200,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.SaveCustomPlate
        )
        self.btn_save_custom.pack(fill="x", padx=0, pady=(20, 10)) # Adjust padding

        # Open in map maker button
        self.btn_send_to_mm = ctk.CTkButton(
            self.editor_page, 
            text=" OPEN IN 3D MAP MAKER", 
            image=self.loadIcon("map.png", size=20), 
            fg_color=COLORS["accent_primary"], 
            height=50, 
            width=1200,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.SendToMapMaker
        )
        self.btn_send_to_mm.pack(fill="x", padx=0, pady=(0, 20))

        # Initial render to check default state toggles
        self.OnStateChange(self.state_var.get())

    def OnStateChange(self, choice):
        config = PLATE_TEMPLATES.get(choice)
        if not config: return

        # Update the character limit label
        char_limit = 10 if "EU" in choice else 8
        if hasattr(self, 'char_limit_label'):
            self.char_limit_label.configure(text=f"Plate Text (Max {char_limit} chars):")

        # Hide all switches to reset their order
        self.tags_switch.pack_forget()
        self.outline_switch.pack_forget()
        self.cobb_switch.pack_forget()

        # Check and show tags toggle 
        if config.get("has_tags_option", True):
            self.show_tags_var.set(True)
            self.tags_switch.pack(anchor="w", padx=20, pady=(10, 0))
        else:
            self.show_tags_var.set(False) 

        # Check and show outline toggle
        if config.get("has_outline_option"):
            self.show_outline_var.set(True)
            self.outline_switch.pack(anchor="w", padx=20, pady=(10, 0))
        else:
            self.show_outline_var.set(False)

        # Check and show COBB toggle
        if config.get("has_cobb_option"):
            self.show_cobb_var.set(True)
            self.cobb_switch.pack(anchor="w", padx=20, pady=(10, 0))
        else:
            self.show_cobb_var.set(False)
            
        self.UpdateEditorPreview()

    def OnTextChange(self, *args):
        text = self.plate_text_var.get().upper()
        selected_state = self.state_var.get()
        
        # Set limit to 10 if "EU" is in the template name, otherwise 8
        char_limit = 10 if "EU" in selected_state else 8
        
        if len(text) > char_limit:
            text = text[:char_limit]
            
        self.plate_text_var.set(text)
        
        if hasattr(self, '_render_job') and self._render_job:
            self.after_cancel(self._render_job)
        self._render_job = self.after(300, self.UpdateEditorPreview)

    def GeneratePlateImage(self):
        state = self.state_var.get()
        text = self.plate_text_var.get()
        config = PLATE_TEMPLATES.get(state)
        
        if not config:
            return None

        # Figure out which image key to use based on the toggles
        has_tags = getattr(self, "show_tags_var", ctk.BooleanVar(value=True)).get()
        has_outline = config.get("has_outline_option") and getattr(self, "show_outline_var", ctk.BooleanVar(value=False)).get()

        if has_tags and has_outline:
            image_key = "image_tags_outline"
        elif has_tags and not has_outline:
            image_key = "image_tags"
        elif not has_tags and has_outline:
            image_key = "image_no_tags_outline"
        else:
            image_key = "image_no_tags"

        # Wrap the image path
        image_path = resourcePath(config.get(image_key))
        
        if not image_path or not os.path.exists(image_path):
            return None

        try:
            # Load the selected base image
            base_img = Image.open(image_path).convert("RGBA")

            # Paste the COBB overlay if toggled
            if config.get("has_cobb_option") and getattr(self, "show_cobb_var", ctk.BooleanVar(value=False)).get():
                cobb_path = resourcePath(config.get("cobb_overlay"))
                if cobb_path and os.path.exists(cobb_path):
                    cobb_img = Image.open(cobb_path).convert("RGBA")
                    coords = config.get("cobb_coords", (0, 0))
                    # The third argument is the mask, which keeps the transparent background transparent
                    base_img.paste(cobb_img, coords, cobb_img)

            draw = ImageDraw.Draw(base_img)
            
            # Wrap the font path
            font_path = resourcePath(config["font_file"])
            try:
                font = ImageFont.truetype(font_path, config["font_size"])
            except IOError:
                font = ImageFont.load_default()
                print("Custom font not found. Using default.")

            left, top, right, bottom = font.getbbox(text)
            text_width = right - left
            text_height = bottom - top
            
            x = config["coords"][0] - (text_width / 2)
            y = config["coords"][1] - (text_height / 2)

            draw.text((x, y), text, font=font, fill=config["text_color"])
            return base_img
            
        except Exception as e:
            print(f"Render error: {e}")
            return None

    def UpdateEditorPreview(self, *args):
        img = self.GeneratePlateImage()
        if img:
            # Scale down for the UI preview
            w, h = img.size
            aspect = h / w
            preview_w = 400
            preview_h = int(preview_w * aspect)
            
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(preview_w, preview_h))
            self.editor_preview_label.configure(image=ctk_img, text="")
        else:
            self.editor_preview_label.configure(text="Missing template image.", image="")

    def SaveCustomPlate(self):
        img = self.GeneratePlateImage()
        if not img:
            messagebox.showerror("Error", "Could not generate plate.")
            return
            
        initial_dir = self.last_dirs.get("editor_out", "/") # Use specific memory key for map maker export directory
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            initialdir=initial_dir,
            initialfile=f"{self.plate_text_var.get()}_plate.png"
        )
        
        if save_path:
            # Remember export directory
            self.last_dirs["editor_out"] = os.path.dirname(save_path)
            self.saveConfig(silent=True)
            
            img.save(save_path, format="PNG")
            messagebox.showinfo("Success", f"Plate saved to:\n{save_path}")

    def SendToMapMaker(self):
        img = self.GeneratePlateImage()
        if not img:
            messagebox.showerror("Error", "Could not generate plate.")
            return

        # Use a normalized path to ensure the system finds the file correctly
        temp_path = os.path.normpath(os.path.join(tempfile.gettempdir(), "varsinity_designer_transfer.png"))
        img.save(temp_path)

        # Update the path entry
        self.mm_drop_zone.path_entry.delete(0, "end")
        self.mm_drop_zone.path_entry.insert(0, temp_path)
        
        # Update the visual icon in the drop zone
        self.mm_drop_zone.updatePreview(temp_path)
        self.mm_drop_zone.configure(border_color=COLORS["accent_success"])

        # Load the preview and switch tabs
        self.LoadPreviewImage(temp_path)
        self.showPage("map_maker")
        
        # Force a refresh after the tab animation finishes
        # This re-links the sliders to the new thumbnail image
        self.after(350, self.SchedulePreviewUpdate)

    def SendMapToCompiler(self):
        source_path = self.mm_drop_zone.getPath()
        if not source_path or not os.path.exists(source_path):
            messagebox.showerror("Error", "No source image found in Map Maker!")
            return

        if not hasattr(self, 'last_mm_map') or not os.path.exists(self.last_mm_map):
            self.mm_status_label.configure(text="⏳ Generating high-res map...", text_color=COLORS["accent_secondary"])
            
            # Use a temp path for the generated map
            map_path = os.path.normpath(os.path.join(tempfile.gettempdir(), "generated_compiler_map.png"))
            
            # Re-use your existing generation logic to save a high-res copy
            img = Image.open(source_path)
            final_map = self.CreateNormalMapData(img, self.base_intensity.get(), self.base_blur.get(), self.base_extrude.get())
            final_map.save(map_path)
            self.last_mm_map = map_path

        # Auto-detect target region
        try:
            img = Image.open(source_path)
            ratio = img.size[0] / img.size[1]
            
            target_region = "EU & UK" if ratio > 3.0 else "US & MX"
            
            self.region_var.set(target_region)
            self.updateDropzoneRegions()
        except Exception:
            pass # Failsafe in case the image is corrupted

        # Inject into Compiler Drop Zones
        self.image_drop_zone.path_entry.delete(0, "end")
        self.image_drop_zone.path_entry.insert(0, source_path)
        self.image_drop_zone.updatePreview(source_path)

        self.nrml_drop_zone.path_entry.delete(0, "end")
        self.nrml_drop_zone.path_entry.insert(0, self.last_mm_map)
        self.nrml_drop_zone.updatePreview(self.last_mm_map)

        # Finish up
        self.image_drop_zone.configure(border_color=COLORS["accent_success"])
        self.nrml_drop_zone.configure(border_color=COLORS["accent_success"])
        self.showPage("compiler")

    def setupPresetsPage(self):
        ctk.CTkLabel(self.presets_page, text="Preset Plates", font=ctk.CTkFont(size=32, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(
            self.presets_page, 
            text="Ready-to-use custom plates. Select one EU and one US plate to bundle into a single compilation. DMs are always open for suggestions.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            wraplength=587,
            justify="left"
        ).pack(anchor="w", padx=(0, 20), pady=(0, 20))
        
        self.preset_cart_status = ctk.CTkLabel(self.presets_page, text="No Presets Selected", font=ctk.CTkFont(size=14), text_color=COLORS["accent_primary"])
        self.preset_cart_status.pack(anchor="w", pady=(0, 10))

        settings_frame = ctk.CTkFrame(self.presets_page, fg_color="transparent")
        settings_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(settings_frame, text="Version:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 10))
        
        ctk.CTkOptionMenu(
            settings_frame, variable=self.version_var, values=["Latest (Direct Zip)", "1.634.818.0"], 
            width=170, fg_color=COLORS["bg_secondary"], button_color=COLORS["bg_secondary"], 
            button_hover_color=COLORS["border"], dropdown_fg_color=COLORS["bg_card"], 
            dropdown_hover_color=COLORS["border"], dropdown_text_color=COLORS["text_primary"], 
            corner_radius=6, command=lambda _: self.saveConfig(silent=True)
        ).pack(side="left", padx=(0, 20))

        ctk.CTkLabel(settings_frame, text="Output:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 10))
        
        self.preset_dir_entry = ctk.CTkEntry(settings_frame, textvariable=self.gen_output_dir_var, fg_color=COLORS["bg_secondary"], border_color=COLORS["border"])
        self.preset_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.preset_dir_entry.bind("<Button-1>", lambda e: self.BrowseGenOutputDir())
        
        ctk.CTkButton(settings_frame, text="Browse", width=80, fg_color=COLORS["bg_secondary"], hover_color=COLORS["border"], command=self.BrowseGenOutputDir).pack(side="left")

        # Compile presets button
        self.preset_cart_btn = ctk.CTkButton(
            self.presets_page, 
            text=" COMPILE PRESETS", 
            image=self.loadIcon("package-plus.png", size=20), 
            command=self.compilePresets, 
            fg_color=COLORS["accent_secondary"], 
            height=50,
            width=0,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.preset_cart_btn.pack(fill="x", padx=0, pady=(0, 20))
        
        self.presets_list = ctk.CTkFrame(self.presets_page, fg_color="transparent")
        self.presets_list.pack(fill="both", expand=True)
        self.presets_list.grid_columnconfigure(0, weight=1)
        self.presets_list.grid_columnconfigure(1, weight=1)

        # Build the list once at startup
        self.refreshPresets()

    def refreshPresets(self, force=False):
        # If not forcing a reload and widgets already exist, stop here
        if not force and self.presets_list.winfo_children():
            return
            
        for widget in self.presets_list.winfo_children(): 
            widget.destroy()
        
        row_idx = 0
        col_idx = 0
        
        for item in self.preset_data:
            card = ctk.CTkFrame(self.presets_list, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
            card.grid(row=row_idx, column=col_idx, sticky="nsew", padx=10, pady=10)
            
            img_label = ctk.CTkLabel(card, text="Loading...")
            img_label.pack(pady=(20, 10), padx=10, fill="both", expand=True)
            
            img_path = item.get('img')
            # Check cache immediately on the main thread
            if img_path in self.image_cache:
                img_label.configure(image=self.image_cache[img_path], text="")
            elif img_path and os.path.exists(img_path):
                threading.Thread(target=self.LoadPresetPreview, args=(img_path, img_label, item['region']), daemon=True).start()
            else:
                img_label.configure(image=self.loadIcon("image.png", size=32), text="")

            # Stacked text in the middle
            ctk.CTkLabel(card, text=item['name'], font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 2))
            ctk.CTkLabel(card, text=item['region'], font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(pady=(0, 15))
            
            is_selected = item in self.preset_cart.values()
            region_key = 'us' if item['region'] == "US & MX" else 'eu'
            is_blocked = self.preset_cart[region_key] is not None and self.preset_cart[region_key] != item
            
            btn_text = "Remove" if is_selected else "Select"
            btn_state = "disabled" if is_blocked else "normal"
            btn_color = COLORS["accent_danger"] if is_selected else COLORS["accent_primary"]
            
            ctk.CTkButton(card, text=btn_text, state=btn_state, fg_color=btn_color, command=lambda i=item: self.togglePresetCart(i)).pack(pady=(0, 20), padx=20, fill="x")

            # Wrap to the next row after 2 columns
            col_idx += 1
            if col_idx > 1:
                col_idx = 0
                row_idx += 1

    def LoadPresetPreview(self, path, label, region):
        def BackgroundTask():
            try:
                with open(path, "rb") as f:
                    img_data = f.read()
            
                # Process the image in the background to keep the app fast
                pil_img = Image.open(io.BytesIO(img_data)).convert("RGBA")
                w, h = pil_img.size
                target_w = 250 if "EU" in region else 200
                target_h = int(target_w * (h / w))
                pil_img.thumbnail((target_w, target_h), Image.LANCZOS)

                # Put the UI update into the queue
                self.ui_queue.put(lambda: self.FinalizePresetUi(pil_img, path, label))
            
            except Exception as e:
                print(f"Background disk error for {path}: {e}")

        threading.Thread(target=BackgroundTask, daemon=True).start()

    def FinalizePresetUi(self, pil_img, path, label):
        try:
            if label.winfo_exists():
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                self.image_cache[path] = ctk_img
                label.configure(image=ctk_img, text="")
        except Exception as e:
            print(f"UI Update error: {e}")

    def HandlePresetError(self, label):
        try:
            if label.winfo_exists():
                error_icon = self.loadIcon("image.png", size=32)
                label.configure(image=error_icon, text="")
        except:
            pass

    def toggleCart(self, item):
        region_key = 'us' if item['region'] == "US & MX" else 'eu'
        self.cart[region_key] = None if self.cart[region_key] == item else item
        
        eu_item = self.cart.get('eu')
        us_item = self.cart.get('us')
        
        eu_name = f"{eu_item['name']} (Preset)" if eu_item and eu_item.get('is_preset') else (os.path.basename(eu_item.get('img', '')) if eu_item and eu_item.get('img') else "None")
        us_name = f"{us_item['name']} (Preset)" if us_item and us_item.get('is_preset') else (os.path.basename(us_item.get('img', '')) if us_item and us_item.get('img') else "None")
        
        self.cart_status.configure(text=f"EU: {eu_name}  |  US: {us_name}")
        self.refreshHistory()

    def togglePresetCart(self, item):
        region_key = 'us' if item['region'] == "US & MX" else 'eu'
        self.preset_cart[region_key] = None if self.preset_cart[region_key] == item else item
        
        eu_name = self.preset_cart['eu']['name'] if self.preset_cart['eu'] else "None"
        us_name = self.preset_cart['us']['name'] if self.preset_cart['us'] else "None"
        self.preset_cart_status.configure(text=f"EU: {eu_name}  |  US: {us_name}")
        
        # Force the UI to rebuild to update button state
        self.refreshPresets(force=True)

    def compilePresets(self):
        out_dir = self.gen_output_dir_var.get()
        
        if out_dir == "Not Selected" or not out_dir:
            messagebox.showerror("Error", "Please select an output location.")
            return
            
        self.preset_cart_btn.configure(state="disabled", text=" COMPILING...")
        
        def process():
            try:
                added_to_history = False
                
                if self.preset_cart['eu']: 
                    self.region_var.set("EU & UK")
                    self.ProcessFiles(self.preset_cart['eu']['img'], self.preset_cart['eu']['nrml'], out_dir, silent=True)
                    # Add to history
                    self.history.append({
                        "region": "EU & UK", 
                        "img": self.preset_cart['eu']['img'], 
                        "nrml": self.preset_cart['eu']['nrml'],
                        "name": self.preset_cart['eu']['name'], # Preset name
                        "is_preset": True # Preset flag
                    })
                    added_to_history = True
                    
                if self.preset_cart['us']: 
                    self.region_var.set("US & MX")
                    self.ProcessFiles(self.preset_cart['us']['img'], self.preset_cart['us']['nrml'], out_dir, silent=True)
                    # Add to history
                    self.history.append({
                        "region": "US & MX", 
                        "img": self.preset_cart['us']['img'], 
                        "nrml": self.preset_cart['us']['nrml'],
                        "name": self.preset_cart['us']['name'], # Preset name
                        "is_preset": True # Preset flag
                    })
                    added_to_history = True
                
                # Save the new history data if a preset was compiled
                if added_to_history:
                    self.saveConfig(silent=True)
                
                self.after(0, lambda: messagebox.showinfo("Success", "Presets compiled successfully!"))
            except Exception as e:
                self.after(0, lambda err=e: messagebox.showerror("Generation Error", f"An error occurred:\n{err}"))
            finally:
                self.after(0, lambda: self.preset_cart_btn.configure(state="normal", text=" COMPILE PRESETS"))
                
        threading.Thread(target=process, daemon=True).start()

    def setupDashboardPage(self):
        # Header
        header = ctk.CTkLabel(
            self.dashboard_page, 
            text="Welcome back! ", 
            image=self.loadIcon("hello.png", size=32),
            compound="right",
            font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"), 
            text_color=COLORS["text_primary"]
        )
        header.pack(anchor="w", pady=(0, 20))

        # Stats Cards
        stats_frame = ctk.CTkFrame(self.dashboard_page, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)

        # Active Compiler Settings Card
        self.stat_settings = ctk.CTkFrame(stats_frame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.stat_settings.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        settings_inner = ctk.CTkFrame(self.stat_settings, fg_color="transparent")
        settings_inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(settings_inner, text="Compiler Settings", font=ctk.CTkFont(weight="bold"), text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 10))
        
        # Grid for settings
        set_grid = ctk.CTkFrame(settings_inner, fg_color="transparent")
        set_grid.pack(fill="x")
        set_grid.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(set_grid, text="Compression:", font=ctk.CTkFont(size=13)).grid(row=0, column=0, sticky="w", pady=2)
        self.dash_comp_label = ctk.CTkLabel(set_grid, text="--", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["accent_primary"])
        self.dash_comp_label.grid(row=0, column=1, sticky="e", pady=2)

        ctk.CTkLabel(set_grid, text="Silent Mode:", font=ctk.CTkFont(size=13)).grid(row=1, column=0, sticky="w", pady=2)
        self.dash_silent_switch = ctk.CTkSwitch(
            set_grid, text="", variable=self.silent_mode_var, width=35,
            button_color=COLORS["accent_primary"], command=lambda: self.saveConfig(silent=True)
        )
        self.dash_silent_switch.grid(row=1, column=1, sticky="e", pady=2)

        ctk.CTkLabel(set_grid, text="Create Backups:", font=ctk.CTkFont(size=13)).grid(row=2, column=0, sticky="w", pady=2)
        self.dash_backup_switch = ctk.CTkSwitch(
            set_grid, text="", variable=self.create_backups_var, width=35,
            button_color=COLORS["accent_primary"], command=lambda: self.saveConfig(silent=True)
        )
        self.dash_backup_switch.grid(row=2, column=1, sticky="e", pady=2)

        # System Health Card 
        self.stat_health = ctk.CTkFrame(stats_frame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.stat_health.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        health_inner = ctk.CTkFrame(self.stat_health, fg_color="transparent")
        health_inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(health_inner, text="System Readiness", font=ctk.CTkFont(weight="bold"), text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 10))
        
        status_grid = ctk.CTkFrame(health_inner, fg_color="transparent")
        status_grid.pack(fill="x")
        status_grid.columnconfigure(1, weight=1) 

        ctk.CTkLabel(status_grid, text="Photoshop", font=ctk.CTkFont(size=13)).grid(row=0, column=0, sticky="w", pady=2)
        self.health_ps_status = ctk.CTkLabel(status_grid, text="--", font=ctk.CTkFont(size=13, weight="bold"))
        self.health_ps_status.grid(row=0, column=1, sticky="e", pady=2) 

        ctk.CTkLabel(status_grid, text="Illustrator", font=ctk.CTkFont(size=13)).grid(row=1, column=0, sticky="w", pady=2)
        self.health_ai_status = ctk.CTkLabel(status_grid, text="--", font=ctk.CTkFont(size=13, weight="bold"))
        self.health_ai_status.grid(row=1, column=1, sticky="e", pady=2) 

        ctk.CTkLabel(status_grid, text="7-Zip", font=ctk.CTkFont(size=13)).grid(row=2, column=0, sticky="w", pady=2)
        self.health_sz_status = ctk.CTkLabel(status_grid, text="--", font=ctk.CTkFont(size=13, weight="bold"))
        self.health_sz_status.grid(row=2, column=1, sticky="e", pady=2) 

        # Quick Start Guide
        guide_frame = ctk.CTkFrame(self.dashboard_page, fg_color="transparent")
        guide_frame.pack(fill="x", pady=(10, 20))
        
        ctk.CTkLabel(guide_frame, text="Getting Started", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 10))
        
        guide_text = (
            "1. Need a blank plate? Go to 'Plate Templates' to download base files.\n"
            "2. Want to design a plate yourself? Go to 'Plate Designer' to type your text on a supported template.\n"
            "3. Need a 3D effect on your plate? Use the '3D Map Maker' to generate normal maps.\n"
            "4. Have both the plate design and height map? Go to 'Compiler' to inject your images into the game files."
        )
        ctk.CTkLabel(guide_frame, text=guide_text, font=ctk.CTkFont(size=13), text_color=COLORS["text_secondary"], justify="left").pack(anchor="w", padx=(10, 0))

        # Active Plates
        ctk.CTkLabel(self.dashboard_page, text="Active Plates", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(10, 10))
        self.active_plates_frame = ctk.CTkFrame(self.dashboard_page, fg_color="transparent")
        self.active_plates_frame.pack(fill="x")
        self.active_plates_frame.grid_columnconfigure(0, weight=1)
        self.active_plates_frame.grid_columnconfigure(1, weight=1)
        
        self.active_eu_label = ctk.CTkLabel(self.active_plates_frame, text="Loading EU...", height=80, fg_color=COLORS["bg_secondary"], corner_radius=12)
        self.active_eu_label.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.active_us_label = ctk.CTkLabel(self.active_plates_frame, text="Loading US...", height=80, fg_color=COLORS["bg_secondary"], corner_radius=12)
        self.active_us_label.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # Changelog
        ctk.CTkLabel(
            self.dashboard_page, 
            text=f"Recent Additions (v{APP_VERSION})", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(20, 10))
        
        self.changelog_frame = ctk.CTkFrame(self.dashboard_page, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.changelog_frame.pack(fill="x", pady=(0, 10))
        self.changelog_frame.grid_columnconfigure(1, weight=1)

        changes = [
            ("New Buttons", "Added 'Send to Compiler' and 'Open in Map Maker' shortcut buttons to quickly jump between tabs without saving files manually."),
            ("Window Animations", "The app now fades in and out when opening or closing."),
            ("Built-In 7-Zip", "7-Zip is now fully integrated. If your custom path breaks or is missing, the app automatically falls back to a bundled portable version."),
            ("UI & Icon Updates", "Replaced outdated emojis high quality icons. Added better guidance across the app."),
            ("Performance Optimizations", "The Presets tab now loads without flickering every time you click it. Taskbar icon caching was also rewritten in turn. Although the page switching looks glitchy and I don't know of any ways to fix it due to Tkinter's limitations."),
            ("Revamped Auto-Updater", "The app will now automatically download the latest, clean up the old executable, and restart itself upon user consent."),
            ("Toggle Page Transitions", "Added a toggle to turn the buggy page transitions on or off.")
        ]

        for idx, (title, desc) in enumerate(changes):
            ctk.CTkLabel(self.changelog_frame, text=f"• {title}:", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["accent_primary"]).grid(row=idx, column=0, sticky="nw", padx=(15, 10), pady=8)
            ctk.CTkLabel(self.changelog_frame, text=desc, font=ctk.CTkFont(size=13), text_color=COLORS["text_secondary"], justify="left", wraplength=370).grid(row=idx, column=1, sticky="nw", padx=(0, 15), pady=8)

        # Recent Activity
        ctk.CTkLabel(self.dashboard_page, text="Recent Activity", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(20, 10))
        self.dash_history_list = ctk.CTkFrame(self.dashboard_page, fg_color="transparent")
        self.dash_history_list.pack(fill="both", expand=True)

    def refreshDashboard(self):
        # Active settings check
        comp_val = self.comp_level_var.get()
        # Clean up the text to say "Normal"
        clean_comp = comp_val.split(" ")[0] if " " in comp_val else comp_val
        self.dash_comp_label.configure(text=clean_comp)
        
        # System health check
        checks = [
            (self.ps_path_var.get().strip('"'), self.health_ps_status),
            (self.ai_path_var.get().strip('"'), self.health_ai_status),
            (self.sz_path_var.get().strip('"'), self.health_sz_status)
        ]
        
        for path, label in checks:
            exists = os.path.exists(path) if path else False
            
            # If the primary 7-Zip path is missing, check the portable fallback
            if label == self.health_sz_status and not exists:
                exists = os.path.exists(resourcePath("7za.exe"))

            status_text = "Ready" if exists else "Missing"
            status_color = COLORS["accent_success"] if exists else COLORS["accent_danger"]
            
            label.configure(text=status_text, text_color=status_color)

        threading.Thread(target=self.LoadActivePlates, daemon=True).start()

        # Update Recent Activity List
        for widget in self.dash_history_list.winfo_children(): widget.destroy()
        recent_items = list(reversed(self.history))[:3] 
        if not recent_items:
            ctk.CTkLabel(self.dash_history_list, text="No plates compiled yet.", text_color=COLORS["text_muted"]).pack(anchor="w", pady=10)
            return
        for item in recent_items:
            card = ctk.CTkFrame(self.dash_history_list, fg_color=COLORS["bg_secondary"], corner_radius=8)
            card.pack(fill="x", pady=5, ipadx=15, ipady=12)
            
            if item.get('is_preset'):
                img_name = f"{item['name']} (Preset)"
            else:
                img_name = os.path.basename(item['img']) if item.get('img') else "No Image"
                
            ctk.CTkLabel(card, text="✅", font=ctk.CTkFont(size=16)).pack(side="left")
            ctk.CTkLabel(card, text=f"You compiled a {item['region']} plate: {img_name}", text_color=COLORS["text_secondary"]).pack(side="left", padx=10)

    def loadLastProject(self):
        if not self.history: 
            return
            
        last = self.history[-1]
        
        # Set the region toggle
        self.region_var.set(last["region"])
        self.updateDropzoneRegions()
        
        # Check if the images still exist on the user's computer, then load them in
        img = last.get("img", "")
        if img and os.path.exists(img):
            self.image_drop_zone.path_entry.delete(0, "end")
            self.image_drop_zone.path_entry.insert(0, img)
            self.image_drop_zone.updatePreview(img)
            self.image_drop_zone.configure(border_color=COLORS["accent_success"])
            
        nrml = last.get("nrml", "")
        if nrml and os.path.exists(nrml):
            self.nrml_drop_zone.path_entry.delete(0, "end")
            self.nrml_drop_zone.path_entry.insert(0, nrml)
            self.nrml_drop_zone.updatePreview(nrml)
            self.nrml_drop_zone.configure(border_color=COLORS["accent_success"])
            
        # Swap to the compiler page
        self.showPage("compiler")

    def promptClearBackups(self):
        target_zip = filedialog.askopenfilename(filetypes=[("Zip Archives", "*.zip")], title="Select Textures.zip to clean")
        if not target_zip: return
        
        if messagebox.askyesno("Confirm", "This will search the 'plates' folder inside this zip and delete ALL backup (.bak) files.\n\nContinue?"):
            threading.Thread(target=self.ProcessClearBackups, args=(target_zip,), daemon=True).start()

    def ProcessClearBackups(self, target_zip):
        try:
            sz_path = self.sz_path_var.get().strip('"')

            # Fallback to portable 7-Zip if settings path is broken
            if not os.path.exists(sz_path):
                sz_path = resourcePath("7za.exe")

            if not os.path.exists(sz_path): 
                raise FileNotFoundError(f"7-Zip not found. Checked settings and portable fallback.")
            
            temp_dir = tempfile.mkdtemp()
            
            # Extract zip
            subprocess.run([sz_path, "x", target_zip, f"-o{temp_dir}"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Target the plates folder
            plates_dir = os.path.join(temp_dir, "plates")
            bak_count = 0
            
            if os.path.exists(plates_dir):
                for root, dirs, files in os.walk(plates_dir):
                    for f in files:
                        if f.endswith(".bak"):
                            os.remove(os.path.join(root, f))
                            bak_count += 1
            
            if bak_count == 0:
                shutil.rmtree(temp_dir)
                self.after(0, lambda: messagebox.showinfo("Clean Complete", "No .bak files were found in the plates folder of this zip!"))
                return
                
            # Repack zip
            os.remove(target_zip)
            comp_flag = "-mx1" if "mx1" in self.comp_level_var.get() else "-mx9" if "mx9" in self.comp_level_var.get() else "-mx5"
            subprocess.run([sz_path, "a", "-tzip", comp_flag, target_zip, f"{temp_dir}\\*"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            shutil.rmtree(temp_dir)
            self.after(0, lambda: messagebox.showinfo("Success", f"Successfully deleted {bak_count} backup file(s) from the plates folder and repacked the zip!"))
            
        except Exception as e:
            self.after(0, lambda err=e: messagebox.showerror("Error", f"Failed to clear backups:\n{err}"))

    def LoadActivePlates(self):
        import zipfile
        try:
            out_path = getattr(self, "gen_output_dir_var", ctk.StringVar()).get()
            if out_path == "Not Selected" or not out_path:
                self.SetActivePlateUi("eu", None, "No Output Selected")
                self.SetActivePlateUi("us", None, "No Output Selected")
                return

            if getattr(self, "version_var", ctk.StringVar()).get() == "Latest (Direct Zip)":
                target_zip = out_path
            else:
                target_zip = os.path.join(out_path, "Textures.zip")

            if not os.path.exists(target_zip) or not os.path.isfile(target_zip):
                self.SetActivePlateUi("eu", None, "Textures.zip not found")
                self.SetActivePlateUi("us", None, "Textures.zip not found")
                return

            eu_img, us_img = None, None

            with zipfile.ZipFile(target_zip, 'r') as z:
                eu_entry = next((name for name in z.namelist() if "plate_eu1_base_diff" in name and not name.endswith(".bak")), None)
                us_entry = next((name for name in z.namelist() if "plate_mx1_base_diff" in name and not name.endswith(".bak")), None)
                
                if eu_entry:
                    with z.open(eu_entry) as f: eu_img = Image.open(BytesIO(f.read())).copy()
                if us_entry:
                    with z.open(us_entry) as f: us_img = Image.open(BytesIO(f.read())).copy()

            self.SetActivePlateUi("eu", eu_img, "Default EU Plate")
            self.SetActivePlateUi("us", us_img, "Default US Plate")
            
        except zipfile.BadZipFile:
            self.SetActivePlateUi("eu", None, "Invalid Textures.zip")
            self.SetActivePlateUi("us", None, "Invalid Textures.zip")
        except Exception as e:
            self.SetActivePlateUi("eu", None, "Error Reading Plates")
            self.SetActivePlateUi("us", None, "Error Reading Plates")
            
    def SetActivePlateUi(self, region, img, fallback_text):
        label = getattr(self, f"active_{region}_label", None)
        if not label: return
        
        if img:
            try:
                w, h = img.size
                aspect = w / h
                target_h = 60
                target_w = int(target_h * aspect)
                if target_w > 250: target_w = 250
                
                img.thumbnail((target_w, target_h))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(target_w, target_h))
                self.after(0, lambda: label.configure(image=ctk_img, text=""))
            except:
                self.after(0, lambda: label.configure(image="", text="Preview Error"))
        else:
            self.after(0, lambda: label.configure(image="", text=fallback_text))

    def animateStatusDot(self):
        t = time.time() * 2.5 
        intensity = (math.sin(t) + 1) / 2 
        
        if getattr(self, "is_online", True):
            # Online
            r = int(22 + (16 - 22) * intensity)
            g = int(56 + (185 - 56) * intensity)
            b = int(47 + (129 - 47) * intensity)
        else:
            # Offline
            r = int(30 + (239 - 30) * intensity)
            g = int(15 + (68 - 15) * intensity)
            b = int(15 + (68 - 15) * intensity)
            
        try:
            if self.status_dot.winfo_exists():
                self.status_dot.configure(text_color=f"#{r:02x}{g:02x}{b:02x}")
                self.after(50, self.animateStatusDot)
        except Exception:
            pass

    def openMaskPainter(self, edit=False):
        source = self.mm_drop_zone.getPath()
        if not source or not os.path.exists(source):
            messagebox.showerror("Error", "Drop a Source Image first!")
            return
            
        mask = None
        if edit:
            mask = self.mm_mask_drop_zone.getPath()
            if not mask or not os.path.exists(mask):
                messagebox.showerror("Error", "No mask found to edit! Drop a mask or draw a new one first.")
                return
                
        MaskPainter(self, source, mask, self.ApplyDrawnMask)

    def ApplyDrawnMask(self, mask_path):
        self.mm_mask_drop_zone.path_entry.delete(0, "end")
        self.mm_mask_drop_zone.path_entry.insert(0, mask_path)
        self.mm_mask_drop_zone.updatePreview(mask_path)
        self.mm_mask_drop_zone.configure(border_color=COLORS["accent_success"])
        self.SchedulePreviewUpdate()

    def openNormalPainter(self):
        img_path = self.mm_drop_zone.getPath()
        if not img_path or not os.path.isfile(img_path):
            messagebox.showerror("Error", "Drop a Source Image first to generate the map.")
            return

        self.btn_paint_map.configure(state="disabled", text=" OPENING...")

        def Prepare():
            try:
                img = Image.open(img_path)
                b_str, b_blur, b_dir = self.base_intensity.get(), self.base_blur.get(), self.base_extrude.get()
                m_str, m_blur, m_dir = self.mask_intensity.get(), self.mask_blur.get(), self.mask_extrude.get()
                mask_path = self.mm_mask_drop_zone.getPath() if self.advanced_mode_var.get() else None

                base_map = self.CreateNormalMapData(img, b_str, b_blur, b_dir)

                if mask_path and os.path.exists(mask_path):
                    mask_img = Image.open(mask_path).convert('L').resize(base_map.size)
                    mask_map = self.CreateNormalMapData(img, m_str, m_blur, m_dir)
                    final_img = Image.composite(mask_map, base_map, mask_img)
                else:
                    final_img = base_map

                self.after(0, lambda: NormalPainter(self, final_img, self.SavePaintedNormalMap))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to load map: {e}"))
            finally:
                self.after(0, lambda: self.btn_paint_map.configure(state="normal", text=" PAINT MAP"))

        threading.Thread(target=Prepare, daemon=True).start()

    def SavePaintedNormalMap(self, final_img, send_to_compiler=False):
        temp_path = os.path.normpath(os.path.join(tempfile.gettempdir(), "last_painted_map.png"))
        
        try:
            final_img.save(temp_path, format="PNG")
            self.last_mm_map = temp_path 
            
            if send_to_compiler:
                self.SendMapToCompiler() 
            else:
                self.mm_status_label.configure(text="✅ Changes Saved Internally!", text_color=COLORS["accent_success"])
                self.after(4000, lambda: self.mm_status_label.configure(text=""))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def processUiQueue(self):
        try:
            while True:
                task = self.ui_queue.get_nowait()
                task()
                self.ui_queue.task_done()
        except queue.Empty:
            pass
        self.after(100, self.processUiQueue)

if __name__ == "__main__":
    # Clean up the old .exe if an update just finished
    if getattr(sys, 'frozen', False):
        old_exe = os.path.join(os.path.dirname(sys.executable), "PlateCompiler_old.exe")
        if os.path.exists(old_exe):
            try:
                os.remove(old_exe)
            except Exception:
                pass 

    app = PlateMakerApp()
    app.mainloop()