# License-Plate-Compiler
A simple tool designed to build and efficiently organize license plate swatches for vehicle mods. Instead of manually renaming files and creating folders, this tool "compiles" your source images into the exact directory structure the game requires.

## Features
* **Automated Compilation:** Instantly generates the full `.swatchbin` file set for both EU/UK and US/MX regions.
* **Built-in 3D Map Maker:** Generate high-quality Normal maps directly from source images with granular control over intensity, blur, and extrusion direction.
* **Standardized Directory Structure:** Automatically builds the `Textures > plates > swatches` hierarchy for easy packaging.
* **Adobe Integration:** Quick-launch shortcuts for Photoshop and Illustrator with direct access to official plate templates.
* **Persistent Settings:** Saves your custom Adobe executable paths for a seamless, one-click workflow.
* **Live Status:** Integrated version tracking and online status indicator.

## How to Use
1.  **Download:** Grab the latest `PlateCompiler.exe` from the [Releases](https://github.com/Varsinityy/License-Plate-Compiler/releases) page.
2.  **Configure Region:** Select your target region (EU/UK or US/MX) in the Compiler tab.
3.  **Import Assets:** Drag and drop your Diff/Mask image or 3D Nrml map into the respective zones.
4.  **Select Export Path:** Set your base export folder.
5.  **Compile:** Click **Compile Plates**. The tool will organize your assets and automatically open the directory for you.
6.  **Note:** You can compile **both** US and EU plates into the same output folder. The tool will automatically merge the files into the existing folder structure rather than overwriting them, so you can build your entire project in a single export session.

## 3D Map Maker
The integrated Map Maker allows you to create depth maps without leaving the tool:
* **Real-time Preview:** See how your adjustments affect the depth map before exporting.
* **Adjustable Parameters:** Fine-tune **Intensity** for depth and **Smoothness** for surface blur.
* **Extrusion Control:** Toggle between **Inward** and **Outward** extrusion based on your mod's requirements.

---

> [!IMPORTANT]
> **Zip Requirement:** After compilation, ensure you zip the final `Textures` folder using **7-Zip** before moving it to your project directory. (Forza Horizon 5\media\Stripped\MediaOverride\RC0\Cars\_library)

---

## Requirements
* **Windows 10/11**
* **7-Zip** (for final packaging)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Developed by Varsinity**
