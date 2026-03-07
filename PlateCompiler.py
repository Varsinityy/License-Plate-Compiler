import os
import shutil
import requests
import tempfile
import threading
import math
import subprocess
import json
from PIL import Image, ImageFilter
from io import BytesIO
import customtkinter as ctk
from tkinter import filedialog, messagebox

try:
    from ctypes import windll, c_int, byref, sizeof
except ImportError:
    windll = None

ctk.set_appearance_mode("Dark")

COLORS = {
    "bg_primary": "#09090b",
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

# --- FILENAME LISTS ---
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

class DropZone(ctk.CTkFrame):
    def __init__(self, master, label_text, file_types, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.file_types = file_types
        self.command = command
        self.configure(fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=2, border_color=COLORS["border"])
        
        self.inner_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.inner_frame.pack(expand=True, fill="both", padx=3, pady=20)
        
        self.icon_label = ctk.CTkLabel(self.inner_frame, text="      🖼️", font=ctk.CTkFont(size=32))
        self.icon_label.pack(pady=(10, 5))
        
        self.text_label = ctk.CTkLabel(self.inner_frame, text=label_text, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_secondary"])
        self.text_label.pack(pady=(0, 5))
        
        self.path_entry = ctk.CTkEntry(self.inner_frame, placeholder_text="No file selected...", height=40, fg_color=COLORS["bg_primary"], border_color=COLORS["border"], justify="center")
        self.path_entry.pack(fill="x", padx=20, pady=(10, 20))
        
        self.bind("<Button-1>", self._on_click)
        self.inner_frame.bind("<Button-1>", self._on_click)
        self.icon_label.bind("<Button-1>", self._on_click)
        self.text_label.bind("<Button-1>", self._on_click)
        
    def _on_click(self, event):
        path = filedialog.askopenfilename(filetypes=self.file_types)
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)
            self.icon_label.configure(text="✅", text_color=COLORS["accent_success"])
            self.configure(border_color=COLORS["accent_success"])
            if self.command:
                self.command(path)

    def get_path(self):
        return self.path_entry.get().strip('"')

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
        self.after(10, self.apply_rounded_corners)

        self.icon_url = "https://codehs.com/uploads/24cd9d070606620795f9a393dafaa62a" 
        self.logo_url = "https://codehs.com/uploads/fd81d80c9192d13a66ec9620d278a1ce" 
        self.ps_icon_url = "https://codehs.com/uploads/4bd09762b019512ffaea5eef10aa673a"
        self.ai_icon_url = "https://codehs.com/uploads/5cd274be304300c4f1db5fdade1dd41a"
        self.temp_icon_path = os.path.join(tempfile.gettempdir(), f"varsinity_icon_{os.getpid()}.ico")
        
        self.mm_preview_thumb = None
        self.mm_preview_job = None

        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.setup_titlebar()
        self.setup_sidebar()
        
        self.view_container = ctk.CTkFrame(self, fg_color="transparent")
        self.view_container.grid(row=1, column=1, sticky="nsew", padx=40, pady=40)
        self.view_container.grid_columnconfigure(0, weight=1)
        self.view_container.grid_rowconfigure(0, weight=1)
        
        self.generator_page = ctk.CTkScrollableFrame(self.view_container, fg_color="transparent")
        self.map_maker_page = ctk.CTkScrollableFrame(self.view_container, fg_color="transparent")
        self.templates_page = ctk.CTkScrollableFrame(self.view_container, fg_color="transparent")
        self.settings_page = ctk.CTkScrollableFrame(self.view_container, fg_color="transparent")
        
        self.setup_generator_page()
        self.setup_templates_page()
        self.setup_map_maker_page()
        self.setup_settings_page()
        
        self.load_config()
        self.show_page("compiler")
        
        self.after(100, self.load_assets_safe)
        self.after(200, self.force_taskbar_presence)

    def apply_rounded_corners(self):
        if windll:
            try:
                HWND = windll.user32.GetParent(self.winfo_id())
                windll.dwmapi.DwmSetWindowAttribute(HWND, 33, byref(c_int(2)), sizeof(c_int(2)))
            except: pass

    def load_assets_safe(self):
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
                target_width = 180
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
                    else:
                        self.ai_btn_eu.configure(image=self.adobe_icons["ai"], text="")
                        self.ai_btn_us.configure(image=self.adobe_icons["ai"], text="")
            except: pass

            # Template Previews
            for key, url in self.template_urls.items():
                try:
                    res = requests.get(url, timeout=3)
                    if res.status_code == 200:
                        img = Image.open(BytesIO(res.content))
                        orig_w, orig_h = img.size
            
                        # Use different widths so the boxy US plate doesn't dominate the long EU plate
                        target_w = 280 if key == "eu" else 220 
            
                        # Calculate height based on the specific image's aspect ratio
                        aspect_ratio = orig_h / orig_w
                        target_h = int(target_w * aspect_ratio)
            
                        preview_img = ctk.CTkImage(light_image=img, dark_image=img, size=(target_w, target_h))
            
                        if key == "eu":
                            self.eu_preview_label.configure(image=preview_img, text="")
                        else:
                            self.us_preview_label.configure(image=preview_img, text="")
                except:
                    pass

    def force_taskbar_presence(self):
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

    def setup_titlebar(self):
        self.titlebar = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=40, corner_radius=0)
        self.titlebar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.titlebar.grid_propagate(False)
        self.titlebar.bind("<ButtonPress-1>", self.start_move)
        self.titlebar.bind("<B1-Motion>", self.do_move)

        left_frame = ctk.CTkFrame(self.titlebar, fg_color="transparent")
        left_frame.pack(side="left", padx=10, fill="y")
        left_frame.bind("<ButtonPress-1>", self.start_move)
        left_frame.bind("<B1-Motion>", self.do_move)

        self.title_icon_label = ctk.CTkLabel(left_frame, text="🚗", font=ctk.CTkFont(size=16))
        self.title_icon_label.pack(side="left", padx=(5, 5))

        title_label = ctk.CTkLabel(left_frame, text="Varsinity's Plate Compiler", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_primary"])
        title_label.pack(side="left", padx=5)

        close_btn = ctk.CTkButton(self.titlebar, text="✕", width=45, height=40, fg_color="transparent", hover_color=COLORS["accent_danger"], command=self.quit, corner_radius=0)
        close_btn.pack(side="right")

        min_btn = ctk.CTkButton(self.titlebar, text="—", width=45, height=40, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.state('iconic'), corner_radius=0)
        min_btn.pack(side="right")

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = self.winfo_x() + (event.x - self.x)
        y = self.winfo_y() + (event.y - self.y)
        self.geometry(f"+{x}+{y}")

    def setup_sidebar(self):
        self.nav_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["bg_secondary"], width=200)
        self.nav_frame.grid(row=1, column=0, sticky="nsew")
        
        self.logo_container = ctk.CTkFrame(self.nav_frame, fg_color="transparent", height=120)
        self.logo_container.pack(fill="x", pady=(30, 20))

        self.logo_label = ctk.CTkLabel(self.logo_container, text="PLATE MAKER", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["accent_primary"])
        self.logo_label.pack(pady=30, padx=20)

        self.btn_generator = ctk.CTkButton(self.nav_frame, text="🎨     Compiler", anchor="w", height=48, fg_color=COLORS["bg_secondary"], font=ctk.CTkFont(size=13, weight="bold"), command=lambda: self.show_page("compiler"))
        self.btn_generator.pack(fill="x", padx=15, pady=5)
        
        self.btn_templates = ctk.CTkButton(self.nav_frame, text="📥     Plate Templates", anchor="w", height=48, fg_color=COLORS["bg_secondary"], font=ctk.CTkFont(size=13, weight="bold"), command=lambda: self.show_page("templates"))
        self.btn_templates.pack(fill="x", padx=15, pady=5)

        self.btn_map_maker = ctk.CTkButton(self.nav_frame, text="🗺️ 3D Map Maker", anchor="w", height=48, fg_color=COLORS["bg_secondary"], font=ctk.CTkFont(size=13, weight="bold"), command=lambda: self.show_page("map_maker"))
        self.btn_map_maker.pack(fill="x", padx=15, pady=5)

        self.btn_settings = ctk.CTkButton(self.nav_frame, text="⚙️     Settings", anchor="w", height=48, fg_color=COLORS["bg_secondary"], font=ctk.CTkFont(size=13, weight="bold"), command=lambda: self.show_page("settings"))
        self.btn_settings.pack(fill="x", padx=15, pady=5)

        # Bottom Version Info & Status
        self.footer = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        self.footer.pack(side="bottom", fill="x", pady=20, padx=20)

        self.status_dot = ctk.CTkLabel(self.footer, text="●", text_color=COLORS["accent_success"], font=ctk.CTkFont(size=14))
        self.status_dot.pack(side="left")

        self.status_text = ctk.CTkLabel(self.footer, text=" ONLINE", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_secondary"])
        self.status_text.pack(side="left", padx=2)

        self.ver_label = ctk.CTkLabel(self.footer, text="v1.0.4", font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"])
        self.ver_label.pack(side="right")
        
    def show_page(self, page_name):
        self.generator_page.pack_forget()
        self.map_maker_page.pack_forget()
        self.templates_page.pack_forget()
        self.settings_page.pack_forget()
        
        self.btn_generator.configure(fg_color=COLORS["bg_secondary"])
        self.btn_map_maker.configure(fg_color=COLORS["bg_secondary"])
        self.btn_templates.configure(fg_color=COLORS["bg_secondary"])
        self.btn_settings.configure(fg_color=COLORS["bg_secondary"])

        if page_name == "compiler":
            self.generator_page.pack(fill="both", expand=True)
            self.btn_generator.configure(fg_color=COLORS["accent_primary"])
        elif page_name == "map_maker":
            self.map_maker_page.pack(fill="both", expand=True)
            self.btn_map_maker.configure(fg_color=COLORS["accent_primary"])
        elif page_name == "templates":
            self.templates_page.pack(fill="both", expand=True)
            self.btn_templates.configure(fg_color=COLORS["accent_primary"])
        elif page_name == "settings":
            self.settings_page.pack(fill="both", expand=True)
            self.btn_settings.configure(fg_color=COLORS["accent_primary"])

    def setup_generator_page(self):
        header = ctk.CTkLabel(self.generator_page, text="License Plate Compiler", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"), text_color=COLORS["text_primary"])
        header.pack(anchor="w", pady=(0, 15))

        region_frame = ctk.CTkFrame(self.generator_page, fg_color="transparent")
        region_frame.pack(fill="x", pady=(0, 15))
        
        region_label = ctk.CTkLabel(region_frame, text="TARGET REGION:", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_muted"])
        region_label.pack(side="left", padx=(0, 15))
        
        self.region_var = ctk.StringVar(value="EU & UK")
        self.region_selector = ctk.CTkSegmentedButton(
            region_frame, values=["EU & UK", "US & MX"], variable=self.region_var,
            fg_color=COLORS["bg_secondary"], selected_color=COLORS["accent_primary"],
            selected_hover_color=COLORS["accent_secondary"], text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=12, weight="bold"), height=32
        )
        self.region_selector.pack(side="left")

        drop_container = ctk.CTkFrame(self.generator_page, fg_color="transparent")
        drop_container.pack(fill="x", pady=(5, 15))
        drop_container.grid_columnconfigure(0, weight=1); drop_container.grid_columnconfigure(1, weight=1)
        
        self.image_drop_zone = DropZone(drop_container, "Source Image (Diff/Mask)", [("Images", "*.png *.jpg *.jpeg")])
        self.image_drop_zone.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        self.nrml_drop_zone = DropZone(drop_container, "3D Map (Nrml)", [("Images", "*.png *.jpg *.jpeg")])
        self.nrml_drop_zone.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        # Generator Output Selection
        output_frame = ctk.CTkFrame(self.generator_page, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        output_frame.pack(fill="x", pady=(5, 15), ipadx=20, ipady=15)
        
        ctk.CTkLabel(output_frame, text="Compiler Output Settings", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(5, 10))
        
        self.gen_output_dir_var = ctk.StringVar(value="Not Selected")
        ctk.CTkLabel(output_frame, text="Base Export Folder:", font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20)
        
        gen_dir_row = ctk.CTkFrame(output_frame, fg_color="transparent")
        gen_dir_row.pack(fill="x", padx=20, pady=(0, 5))
        
        self.gen_dir_entry = ctk.CTkEntry(gen_dir_row, textvariable=self.gen_output_dir_var, fg_color=COLORS["bg_primary"], border_color=COLORS["border"])
        self.gen_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        gen_dir_btn = ctk.CTkButton(gen_dir_row, text="Browse", width=80, fg_color=COLORS["bg_card"], command=self._browse_gen_output_dir)
        gen_dir_btn.pack(side="right")

        self.btn_generate = ctk.CTkButton(self.generator_page, text="⚙️ COMPILE PLATES", fg_color=COLORS["accent_primary"], height=60, font=ctk.CTkFont(size=16, weight="bold"), command=self.run_generation)
        self.btn_generate.pack(fill="x", pady=20)

        self.log_area = ctk.CTkTextbox(self.generator_page, fg_color=COLORS["bg_secondary"], font=("Consolas", 12), height=150)
        self.log_area.pack(fill="both", expand=True)

    def _browse_gen_output_dir(self):
        folder = filedialog.askdirectory()
        if folder:
            self.gen_output_dir_var.set(os.path.normpath(folder))

    def setup_map_maker_page(self):
        header = ctk.CTkLabel(self.map_maker_page, text="3D Map Maker", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"), text_color=COLORS["text_primary"])
        header.pack(anchor="w", pady=(0, 20))

        self.mm_drop_zone = DropZone(self.map_maker_page, "Drop Source Image Here", [("Images", "*.png *.jpg *.jpeg")], command=self._load_preview_image)
        self.mm_drop_zone.pack(fill="x", pady=(0, 10))

        self.preview_frame = ctk.CTkFrame(self.map_maker_page, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"], height=160)
        self.preview_frame.pack(fill="x", pady=(0, 10))
        self.preview_frame.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(self.preview_frame, text="Drop an image to see preview...", text_color=COLORS["text_muted"])
        self.preview_label.pack(expand=True)

        sliders_frame = ctk.CTkFrame(self.map_maker_page, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        sliders_frame.pack(fill="x", pady=(0, 10), ipadx=20, ipady=10)

        ctk.CTkLabel(sliders_frame, text="Extrusion Direction", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(5, 0))
        self.extrude_var = ctk.StringVar(value="Inward")
        self.extrude_selector = ctk.CTkSegmentedButton(
            sliders_frame, values=["Inward", "Outward"], variable=self.extrude_var,
            fg_color=COLORS["bg_primary"], selected_color=COLORS["accent_primary"], command=self._schedule_preview_update
        )
        self.extrude_selector.pack(fill="x", padx=20, pady=(5, 10))

        ctk.CTkLabel(sliders_frame, text="Intensity (Depth)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(5, 0))
        self.intensity_slider = ctk.CTkSlider(sliders_frame, from_=0.1, to=10.0, button_color=COLORS["accent_primary"], command=self._schedule_preview_update)
        self.intensity_slider.set(2.0)
        self.intensity_slider.pack(fill="x", padx=20, pady=(5, 10))

        ctk.CTkLabel(sliders_frame, text="Smoothness (Blur)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.blur_slider = ctk.CTkSlider(sliders_frame, from_=0.0, to=5.0, button_color=COLORS["accent_primary"], command=self._schedule_preview_update)
        self.blur_slider.set(0.5)
        self.blur_slider.pack(fill="x", padx=20, pady=(5, 5))

        # --- EXPORT SETTINGS FOR MAP MAKER ---
        export_settings_frame = ctk.CTkFrame(self.map_maker_page, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        export_settings_frame.pack(fill="x", pady=(0, 10), ipadx=20, ipady=15)

        ctk.CTkLabel(export_settings_frame, text="3D Map Export Settings", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(5, 10))

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
        
        dir_btn = ctk.CTkButton(dir_row, text="Browse", width=80, fg_color=COLORS["bg_card"], command=self._browse_mm_export_dir)
        dir_btn.pack(side="right")

        self.btn_generate_map = ctk.CTkButton(self.map_maker_page, text="⚙️ EXPORT FULL RESOLUTION", fg_color=COLORS["accent_secondary"], height=50, font=ctk.CTkFont(size=14, weight="bold"), command=self.run_normal_map_gen)
        self.btn_generate_map.pack(fill="x", pady=(0, 20))

    def _browse_mm_export_dir(self):
        folder = filedialog.askdirectory()
        if folder:
            self.mm_export_dir_var.set(os.path.normpath(folder))

    def _load_preview_image(self, path):
        try:
            img = Image.open(path)
            self.mm_preview_thumb = img.copy()
            self.mm_preview_thumb.thumbnail((400, 150))
            self._update_preview()
        except: messagebox.showerror("Error", "Failed to load preview.")

    def _schedule_preview_update(self, _=None):
        if self.mm_preview_job: self.after_cancel(self.mm_preview_job)
        self.mm_preview_job = self.after(150, self._update_preview)

    def _update_preview(self):
        if not self.mm_preview_thumb: return
        threading.Thread(target=self._generate_preview_thread, args=(self.intensity_slider.get(), self.blur_slider.get(), self.extrude_var.get()), daemon=True).start()

    def _generate_preview_thread(self, strength, blur, direction):
        res_img = self._create_normal_map_data(self.mm_preview_thumb, strength, blur, direction)
        ctk_img = ctk.CTkImage(light_image=res_img, dark_image=res_img, size=res_img.size)
        self.after(0, lambda: self.preview_label.configure(image=ctk_img, text=""))

    def _create_normal_map_data(self, img, strength, blur, direction):
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

    def run_normal_map_gen(self):
        img_path = self.mm_drop_zone.get_path()
        save_dir = self.mm_export_dir_var.get()
        filename = self.mm_filename_var.get()

        if not os.path.isfile(img_path): return
        if save_dir == "Not Selected": return
        threading.Thread(target=self._process_normal_map, args=(img_path, self.intensity_slider.get(), self.blur_slider.get(), self.extrude_var.get(), save_dir, filename), daemon=True).start()

    def _process_normal_map(self, img_path, strength, blur, direction, save_dir, filename):
        try:
            img = Image.open(img_path)
            normal_img = self._create_normal_map_data(img, strength, blur, direction)
            if not filename.lower().endswith(".png"): filename += ".png"
            out = os.path.join(save_dir, filename); normal_img.save(out, format="PNG")
            self.after(0, lambda: messagebox.showinfo("Success", f"Saved to:\n{out}"))
        except Exception as e: self.after(0, lambda: messagebox.showerror("Error", str(e)))

    def setup_templates_page(self):
        header = ctk.CTkLabel(self.templates_page, text="Plate Templates", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"))
        header.pack(anchor="w", pady=(0, 20))

        cards_frame = ctk.CTkFrame(self.templates_page, fg_color="transparent")
        cards_frame.pack(fill="x")
        cards_frame.grid_columnconfigure(0, weight=1); cards_frame.grid_columnconfigure(1, weight=1)

        # EU Card
        self.eu_card = ctk.CTkFrame(cards_frame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.eu_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.eu_preview_label = ctk.CTkLabel(self.eu_card, text="Loading EU Preview...")
        self.eu_preview_label.pack(pady=(20, 10), padx=10, fill="both", expand=True)
        
        self.ps_btn_eu = ctk.CTkButton(self.eu_card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launch_template("eu", "photoshop"))
        self.ps_btn_eu.place(relx=0.96, rely=0.04, anchor="ne")

        self.ai_btn_eu = ctk.CTkButton(self.eu_card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launch_template("eu", "illustrator"))
        self.ai_btn_eu.place(relx=0.84, rely=0.04, anchor="ne")

        ctk.CTkLabel(self.eu_card, text="EU & UK Plate Template", font=ctk.CTkFont(size=16, weight="bold")).pack()
        ctk.CTkButton(self.eu_card, text="Download EU Template", fg_color=COLORS["accent_primary"], command=lambda: self.download_template("eu")).pack(pady=20, padx=20, fill="x")

        # US Card
        self.us_card = ctk.CTkFrame(cards_frame, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.us_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.us_preview_label = ctk.CTkLabel(self.us_card, text="Loading US Preview...")
        self.us_preview_label.pack(pady=(20, 10), padx=10, fill="both", expand=True)
        
        self.ps_btn_us = ctk.CTkButton(self.us_card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launch_template("us", "photoshop"))
        self.ps_btn_us.place(relx=0.96, rely=0.04, anchor="ne")

        self.ai_btn_us = ctk.CTkButton(self.us_card, text="", width=30, height=30, fg_color="transparent", hover_color=COLORS["bg_card"], command=lambda: self.launch_template("us", "illustrator"))
        self.ai_btn_us.place(relx=0.84, rely=0.04, anchor="ne")

        ctk.CTkLabel(self.us_card, text="US & MX Plate Template", font=ctk.CTkFont(size=16, weight="bold")).pack()
        ctk.CTkButton(self.us_card, text="Download US Template", fg_color=COLORS["accent_primary"], command=lambda: self.download_template("us")).pack(pady=20, padx=20, fill="x")

    def setup_settings_page(self):
        header = ctk.CTkLabel(self.settings_page, text="Settings", font=ctk.CTkFont(family="Ubuntu", size=32, weight="bold"))
        header.pack(anchor="w", pady=(0, 20))
        
        path_frame = ctk.CTkFrame(self.settings_page, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        path_frame.pack(fill="x", pady=0, ipady=15)
        
        self.ps_path_var = ctk.StringVar(value=r"C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe")
        self.create_path_setting(path_frame, "Photoshop EXE Path:", self.ps_path_var)
        self.ai_path_var = ctk.StringVar(value=r"C:\Program Files\Adobe\Adobe Illustrator 2024\Support Files\Contents\Windows\Illustrator.exe")
        self.create_path_setting(path_frame, "Illustrator EXE Path:", self.ai_path_var)
        
        ctk.CTkButton(self.settings_page, text="Save Settings", command=self.save_config, fg_color=COLORS["accent_success"], height=40).pack(pady=20)

    def create_path_setting(self, master, label, variable):
        ctk.CTkLabel(master, text=label, text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20, pady=(10,0))
        row = ctk.CTkFrame(master, fg_color="transparent"); row.pack(fill="x", padx=20, pady=5)
        ctk.CTkEntry(row, textvariable=variable, fg_color=COLORS["bg_primary"]).pack(side="left", fill="x", expand=True, padx=(0,10))
        ctk.CTkButton(row, text="Browse", width=80, command=lambda: self.browse_exe(variable)).pack(side="right")

    def browse_exe(self, var):
        path = filedialog.askopenfilename(filetypes=[("Executable", "*.exe")])
        if path: var.set(os.path.normpath(path))

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.ps_path_var.set(data.get("ps_path", self.ps_path_var.get()))
                    self.ai_path_var.set(data.get("ai_path", self.ai_path_var.get()))
            except: pass

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump({"ps_path": self.ps_path_var.get(), "ai_path": self.ai_path_var.get()}, f)
            messagebox.showinfo("Success", "Settings saved!")
        except: messagebox.showerror("Error", "Failed to save settings.")

    def launch_template(self, t_type, tool):
        def _task():
            try:
                exe = self.ps_path_var.get().strip('"') if tool == "photoshop" else self.ai_path_var.get().strip('"')
                r = requests.get(self.template_urls[t_type])
                path = os.path.join(tempfile.gettempdir(), f"{t_type}_plate.png")
                with open(path, "wb") as f: f.write(r.content)
                
                if os.path.isfile(exe):
                    subprocess.Popen([exe, path])
                else:
                    os.startfile(path)
            except Exception as e: self.after(0, lambda: messagebox.showerror("Error", str(e)))
        threading.Thread(target=_task, daemon=True).start()

    def download_template(self, t_type):
        dir_p = filedialog.askdirectory(); 
        if dir_p: threading.Thread(target=self._execute_download, args=(dir_p, t_type), daemon=True).start()

    def _execute_download(self, d, t):
        try:
            for key in (["eu", "us"] if t == "both" else [t]):
                r = requests.get(self.template_urls[key])
                with open(os.path.join(d, f"{key.upper()}_Plate_Template.png"), "wb") as f: f.write(r.content)
            self.after(0, lambda: messagebox.showinfo("Success", "Done!"))
        except: pass

    def log(self, msg): self.after(0, lambda: (self.log_area.insert("end", f"{msg}\n"), self.log_area.see("end")))

    def run_generation(self):
        img_path = self.image_drop_zone.get_path()
        nrml_path = self.nrml_drop_zone.get_path()
        output_base = self.gen_output_dir_var.get()
        
        if not img_path and not nrml_path:
            messagebox.showerror("Error", "Please select at least one file to generate.")
            return
            
        if output_base == "Not Selected" or not os.path.isdir(output_base):
            messagebox.showerror("Error", "Please select a valid base output folder.")
            return

        self.log("Starting plate generation...")
        # Only start ONE thread here
        threading.Thread(target=self._process_files, args=(img_path, nrml_path, output_base), daemon=True).start()

    def _process_files(self, img_path, nrml_path, output_base):
        try:
            selected_region = self.region_var.get()
            target_files = EU_UK_FILES if selected_region == "EU & UK" else US_MX_FILES
            atlas_files = EU_UK_ATLAS_FILES if selected_region == "EU & UK" else US_MX_ATLAS_FILES
            region = "EU/UK" if selected_region == "EU & UK" else "US/MX"

            # Create the required folder structure
            swatches_dir = os.path.join(output_base, "Textures", "plates", "swatches")
            if not os.path.exists(swatches_dir): 
                os.makedirs(swatches_dir)

            if img_path and os.path.isfile(img_path):
                self.log(f"Processing {region} Diff/Mask images...")
                self._generate_swatches(img_path, target_files, False, swatches_dir)

            if nrml_path and os.path.isfile(nrml_path):
                self.log(f"Processing {region} Normal 3D maps...")
                self._generate_swatches(nrml_path, target_files, True, swatches_dir)

            self.log("Generating blank Atlas maps...")
            blank = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
            for a in atlas_files:
                try:
                    blank.save(os.path.join(swatches_dir, a), format="PNG")
                    self.log(f"✓ Created blank atlas: {a}")
                except Exception as e:
                    self.log(f"✗ Error creating {a}: {e}")
            
            self.log("Generation complete!")
            
            # 1. Open the folder immediately
            path_to_open = os.path.normpath(output_base)
            subprocess.Popen(['explorer', path_to_open])
            
            # 2. Show ONLY ONE popup on the main thread
            self.after(0, lambda: messagebox.showinfo("Zip Required", "Plate generation complete!\n\nPlease remember to zip the 'Textures' folder using 7-Zip."))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Generation Error", f"An error occurred:\n{e}"))

    def _generate_swatches(self, p, t, is_n, out):
        for s in [f for f in t if ("nrml" in f) == is_n]:
            try: 
                shutil.copyfile(p, os.path.join(out, s))
                self.log(f"✓ {s}")
            except: pass

    def __del__(self):
        try: os.unlink(self.temp_icon_path)
        except: pass

if __name__ == "__main__":
    app = PlateMakerApp()
    app.mainloop()