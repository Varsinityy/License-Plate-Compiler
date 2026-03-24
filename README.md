# License-Plate-Compiler
A simple tool designed to build and efficiently organize license plate swatches for plate mods. Instead of manually renaming files and creating folders, this tool "compiles" your source images into the exact directory structure the game requires. 
**Now fully supports the latest version of FH5.**

## **Features**
* **Automated Compilation** - Generates the full `.swatchbin` file set for EU/UK and US/MX regions.
* **Direct Zip Merging** - Injects new plates straight into your `Textures.zip`.
* **Auto Backups & Restore** - Creates `.bak` backups of original plates with a one-click restore button.
* **Cumulative Compilation** - Compile US/MX and EU/UK plates to the same base folder to build a unified texture pack in one session.
* **History Tab** - A dedicated tab to view and manage your previously compiled plates, along with the ability to use them as presets to merge previous plate mods.
* **Built-in 3D Map Maker** - Generate Normal maps from source images with control over intensity, blur, and extrusion. Includes an **Advanced Toggle** to unlock mask image inputs and secondary map controls.
* **Adobe Integration** - Quick launch Photoshop or Illustrator with direct access to templates, and send your live 3D map previews directly to either program at full resolution.
* **Live Image Previews** - The drag-and-drop boxes now display a real thumbnail of your selected image instead of a generic icon.
* **Aspect Ratio Protection** - The main compiler will safely block you and show a warning if you try to accidentally load an EU image for a US plate (and vice versa).
* **Game Version Support & Memory** - Toggle between the latest game version and 1.634.818.0. The app will automatically remember your last selected version.
* **Smarter Path Memory** - Each drop-box and output path now remembers the file path of its last instance, entirely independent from each other.
* **Expanded Settings** - Customize your workflow with default output folders, 7-Zip compression levels, custom 7-Zip exe paths, and a Silent Mode toggle to bypass success popups.
* **Auto-Update Checker** - Automatically checks GitHub on startup and notifies you if a newer version is available.

## How to Use
1.  **Download:** Grab the latest `PlateCompiler.exe` from the [Releases](https://github.com/Varsinityy/License-Plate-Compiler/releases) page.
2.  **Select Game Version:** Choose "Latest (Direct Zip)" or "1.634.818.0" depending on your install.
3.  **Configure Region:** Select your target region (EU/UK or US/MX) in the Compiler tab.
4.  **Import Assets:** Drag and drop your Diff/Mask image or Normal map into the respective zones.
5.  **Select Path:** Follow the on-screen instructions to select your `Textures.zip` file or your `_library` folder.
6.  **Compile:** Click **Compile Plates**. The tool will automatically handle the file generation, zipping, merging, and backups.

## Cumulative Compilation
The tool is designed to be additive. You can compile US/MX plates, then switch regions and compile EU/UK plates to the **same path**. The compiler will merge the new files directly into your existing `Textures.zip` or folder structure rather than overwriting your previous work, allowing you to build a unified texture pack in one session.

## 3D Map Maker
The integrated Map Maker allows you to create depth maps without leaving the tool:
* **Real-time Preview:** See how your adjustments affect the depth map before exporting.
* **Adjustable Parameters:** Fine-tune **Intensity** for depth and **Smoothness** for surface blur.
* **Extrusion Control:** Toggle between **Inward** and **Outward** extrusion based on your mod's requirements.

---

> [!IMPORTANT]
> **7-Zip Requirement:** This tool requires **7-Zip** to be installed to automatically package and merge your files into the game's archives.

---

## Requirements
* **Windows 10/11**
* **7-Zip**

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Developed by Varsinity**
