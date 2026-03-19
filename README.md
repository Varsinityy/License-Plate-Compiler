# License-Plate-Compiler
A simple tool designed to build and efficiently organize license plate swatches for plate mods. Instead of manually renaming files and creating folders, this tool "compiles" your source images into the exact directory structure the game requires. 
**Now fully supports the latest version of FH5.**

## Features
* **Version Support:** Toggle between the latest game version and 1.634.818.0.
* **Direct Zip Merging:** Automatically injects your new plates straight into your `Textures.zip` file.
* **Auto Backups & Restore:** Creates `.bak` backups of your original plates inside the zip and includes a one-click restore button to easily undo changes.
* **Automated Compilation:** Instantly generates the full `.swatchbin` file set for both EU/UK and US/MX regions.
* **Built-in 3D Map Maker:** Generate high-quality Normal maps directly from source images with granular control over intensity, blur, and extrusion direction.
* **Standardized Directory Structure:** Automatically builds the `Textures > plates > swatches` hierarchy.
* **Adobe Integration:** Quick-launch shortcuts for Photoshop and Illustrator with direct access to official plate templates.
* **Persistent Settings:** Saves your custom Adobe executable paths for a seamless, one-click workflow.
* **Live Status:** Integrated version tracking and online status indicator.

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
> **7-Zip Requirement:** This tool requires **7-Zip** to be installed at its default location (`C:\Program Files\7-Zip\7z.exe`) to automatically package and merge your files into the game's archives.

---

## Requirements
* **Windows 10/11**
* **7-Zip** (installed at default location)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Developed by Varsinity**
