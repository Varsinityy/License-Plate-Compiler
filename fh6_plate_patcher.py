from __future__ import annotations

import argparse
import shutil
import struct
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Blob:
    index: int
    tag: str
    major: int
    minor: int
    metadata_count: int
    metadata_offset: int
    data_offset: int
    data_size: int


@dataclass
class BufferInfo:
    blob: Blob
    length: int
    size: int
    stride: int
    data_offset: int


@dataclass
class MeshInfo:
    blob: Blob
    material_ids: tuple[int, int, int, int]
    index_buffer_id: int
    start_index: int
    base_vertex: int
    index_count: int
    vertex_layout_id: int
    vertex_buffers: list[tuple[int, int, int, int]]
    texcoord_transform_offset: int
    name: str = ""


class ModelbinError(Exception):
    pass


def u8(data: bytearray, offset: int) -> int:
    return data[offset]


def u16(data: bytearray, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def i16(data: bytearray, offset: int) -> int:
    return struct.unpack_from("<h", data, offset)[0]


def u32(data: bytearray, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def i32(data: bytearray, offset: int) -> int:
    return struct.unpack_from("<i", data, offset)[0]


def put_u16(data: bytearray, offset: int, value: int) -> None:
    value = max(0, min(65535, int(value)))
    struct.pack_into("<H", data, offset, value)


def put_f32(data: bytearray, offset: int, value: float) -> None:
    struct.pack_into("<f", data, offset, float(value))


def blob_tag(raw: bytes) -> str:
    return raw[::-1].decode("ascii", "replace")


def read_metadata_name(data: bytearray, blob: Blob) -> str:
    for i in range(blob.metadata_count):
        off = blob.metadata_offset + i * 8
        if off + 8 > len(data):
            continue
        tag = blob_tag(data[off : off + 4])
        packed = u16(data, off + 4)
        size = packed >> 4
        rel = u16(data, off + 6)
        value_off = off + rel
        if tag != "Name" or size <= 0 or value_off + size > len(data):
            continue
        raw = bytes(data[value_off : value_off + size])
        return raw.split(b"\x00", 1)[0].decode("utf-8", "replace")
    return ""


def read_metadata_id(data: bytearray, blob: Blob) -> int | None:
    for i in range(blob.metadata_count):
        off = blob.metadata_offset + i * 8
        if off + 8 > len(data):
            continue
        tag = blob_tag(data[off : off + 4])
        packed = u16(data, off + 4)
        size = packed >> 4
        rel = u16(data, off + 6)
        value_off = off + rel
        if tag.strip() == "Id" and size == 4 and value_off + size <= len(data):
            return i32(data, value_off)
    return None


def parse_blobs(data: bytearray) -> list[Blob]:
    if data[:4] != b"burG":
        raise ModelbinError("Not a Grub/burG modelbin bundle.")

    header_size = u32(data, 0x08)
    total_size = u32(data, 0x0C)
    blob_count = u32(data, 0x10)

    if total_size > len(data):
        raise ModelbinError(
            f"Header total size 0x{total_size:X} is larger than file size 0x{len(data):X}."
        )

    table_end = 0x14 + blob_count * 0x18
    if table_end > header_size or table_end > len(data):
        raise ModelbinError("Blob table extends past header/file.")

    blobs: list[Blob] = []
    for index in range(blob_count):
        off = 0x14 + index * 0x18
        tag = blob_tag(data[off : off + 4])
        blobs.append(
            Blob(
                index=index,
                tag=tag,
                major=u8(data, off + 4),
                minor=u8(data, off + 5),
                metadata_count=u16(data, off + 6),
                metadata_offset=u32(data, off + 8),
                data_offset=u32(data, off + 12),
                data_size=u32(data, off + 20),
            )
        )
    return blobs


def parse_vertex_buffers(data: bytearray, blobs: list[Blob]) -> list[BufferInfo]:
    buffers: list[BufferInfo] = []
    for blob in blobs:
        if blob.tag != "VerB":
            continue
        off = blob.data_offset
        length = u32(data, off)
        size = u32(data, off + 4)
        stride = u16(data, off + 8)
        data_offset = off + 0x10
        if data_offset + size > len(data):
            raise ModelbinError(f"Vertex buffer {blob.index} data extends past EOF.")
        buffers.append(BufferInfo(blob, length, size, stride, data_offset))
    return buffers


def parse_index_buffers(data: bytearray, blobs: list[Blob]) -> list[BufferInfo]:
    buffers: list[BufferInfo] = []
    for blob in blobs:
        if blob.tag != "IndB":
            continue
        off = blob.data_offset
        length = u32(data, off)
        size = u32(data, off + 4)
        stride = u16(data, off + 8)
        data_offset = off + 0x10
        if data_offset + size > len(data):
            raise ModelbinError(f"Index buffer {blob.index} data extends past EOF.")
        buffers.append(BufferInfo(blob, length, size, stride, data_offset))
    return buffers


def parse_mesh(data: bytearray, blob: Blob) -> MeshInfo:
    if blob.tag != "Mesh":
        raise ValueError("not a Mesh blob")
    if not (blob.major == 1 and blob.minor == 12):
        raise ModelbinError(
            f"Unsupported Mesh version {blob.major}.{blob.minor}; this script expects FH6 v1.12 meshes."
        )

    off = blob.data_offset
    material_ids = tuple(i16(data, off + i * 2) for i in range(4))
    index_buffer_id = i32(data, off + 0x1A)
    start_index = i32(data, off + 0x22)
    base_vertex = i32(data, off + 0x26)
    index_count = u32(data, off + 0x2A)
    vertex_layout_id = u32(data, off + 0x3E)
    vertex_buffer_count = u32(data, off + 0x42)

    vb_base = off + 0x46
    vertex_buffers: list[tuple[int, int, int, int]] = []
    for i in range(vertex_buffer_count):
        entry = vb_base + i * 0x14
        vertex_buffers.append(
            (
                i32(data, entry),
                u32(data, entry + 4),
                u32(data, entry + 8),
                u32(data, entry + 12),
            )
        )

    cursor = vb_base + vertex_buffer_count * 0x14
    texcoord_transform_offset = cursor + 0x10
    if texcoord_transform_offset + 0x50 > off + blob.data_size:
        raise ModelbinError(f"Could not locate texcoord transforms for Mesh blob {blob.index}.")

    return MeshInfo(
        blob=blob,
        material_ids=material_ids,
        index_buffer_id=index_buffer_id,
        start_index=start_index,
        base_vertex=base_vertex,
        index_count=index_count,
        vertex_layout_id=vertex_layout_id,
        vertex_buffers=vertex_buffers,
        texcoord_transform_offset=texcoord_transform_offset,
        name=read_metadata_name(data, blob),
    )


def find_slot_buffer(mesh: MeshInfo, input_slot: int) -> tuple[int, int, int] | None:
    for buffer_id, slot, stride, offset in mesh.vertex_buffers:
        if slot == input_slot:
            return buffer_id, stride, offset
    return None


def read_indices(data: bytearray, ib: BufferInfo, mesh: MeshInfo) -> list[int]:
    if ib.stride == 4:
        read_one = lambda o: u32(data, o)
    elif ib.stride == 2:
        read_one = lambda o: u16(data, o)
    else:
        raise ModelbinError(f"Unsupported index buffer stride {ib.stride}.")

    indices: list[int] = []
    for i in range(mesh.index_count):
        off = ib.data_offset + (mesh.start_index + i) * ib.stride
        if off + ib.stride > ib.data_offset + ib.size:
            raise ModelbinError(f"Mesh {mesh.blob.index} index range extends past index buffer.")
        indices.append(mesh.base_vertex + int(read_one(off)))
    return indices


def reset_texcoord_transforms(data: bytearray, mesh: MeshInfo, channels: int = 4) -> None:
    for channel in range(channels):
        off = mesh.texcoord_transform_offset + channel * 0x10
        put_f32(data, off, 0.0)
        put_f32(data, off + 4, 1.0)
        put_f32(data, off + 8, 0.0)
        put_f32(data, off + 12, 1.0)


def detect_atlas_material_ids(data: bytearray, blobs: list[Blob]) -> set[int]:
    mat_idx = 0
    atlas_ids = set()
    for blob in blobs:
        if blob.tag == "MatI":
            name = read_metadata_name(data, blob).lower()
            mati_data = data[blob.data_offset : blob.data_offset + blob.data_size].lower()
            mat_id = read_metadata_id(data, blob)
            if mat_id is None:
                mat_id = mat_idx
                
            if "atlas" in name or b"atlas" in mati_data:
                atlas_ids.add(mat_id)
            mat_idx += 1
    return atlas_ids

def detect_seal_screw_material_ids(data: bytearray, blobs: list[Blob]) -> tuple[set[int], set[int]]:
    mat_idx = 0
    seal_ids = set()
    screw_ids = set()
    for blob in blobs:
        if blob.tag == "MatI":
            name = read_metadata_name(data, blob).lower()
            mati_data = data[blob.data_offset : blob.data_offset + blob.data_size].lower()
            mat_id = read_metadata_id(data, blob)
            if mat_id is None:
                mat_id = mat_idx
                
            if "seal" in name or b"seal" in mati_data:
                seal_ids.add(mat_id)
            if "screw" in name or b"screw" in mati_data:
                screw_ids.add(mat_id)
            mat_idx += 1
    return seal_ids, screw_ids


def patch_modelbin(
    input_path: Path,
    output_path: Path,
    material_id: int | None = None,
    flip_v: bool = True,
    all_channels: bool = True,
    dry_run: bool = False,
    delete_bracket: bool = False,
    delete_screw: bool = False,
) -> str:
    data = bytearray(input_path.read_bytes())
    blobs = parse_blobs(data)
    
    atlas_ids = detect_atlas_material_ids(data, blobs)
    seal_ids, screw_ids = detect_seal_screw_material_ids(data, blobs)

    index_buffers = parse_index_buffers(data, blobs)
    vertex_buffers = parse_vertex_buffers(data, blobs)
    meshes = [parse_mesh(data, b) for b in blobs if b.tag == "Mesh"]

    if material_id is None:
        material_id = detect_plate_base_material_id(meshes)
        

    matching = []
    for m in meshes:
        name_lower = m.name.lower()
        is_atlas = bool(set(m.material_ids) & atlas_ids)
        is_base = (material_id in m.material_ids)
        is_bracket = "bracket" in name_lower or bool(set(m.material_ids) & seal_ids)
        is_screw = "screw" in name_lower or bool(set(m.material_ids) & screw_ids)

        if is_atlas or is_base or (delete_bracket and is_bracket) or (delete_screw and is_screw):
            if is_bracket and not delete_bracket:
                if not is_atlas:
                    continue
            matching.append(m)
            
    if not matching:
        raise ModelbinError(f"No meshes found using material ID {material_id} or atlas.")

    patched_meshes = 0
    patched_vertices_total = 0

    for mesh in matching:
        if mesh.index_buffer_id < 0 or mesh.index_buffer_id >= len(index_buffers):
            continue

        pos_ref = find_slot_buffer(mesh, 0)
        attr_ref = find_slot_buffer(mesh, 1)
        if pos_ref is None or attr_ref is None:
            continue

        pos_buffer_id, pos_stride_ref, pos_offset = pos_ref
        attr_buffer_id, attr_stride_ref, attr_offset = attr_ref

        if pos_buffer_id < 0 or pos_buffer_id >= len(vertex_buffers):
            continue
        if attr_buffer_id < 0 or attr_buffer_id >= len(vertex_buffers):
            continue

        pos_buffer = vertex_buffers[pos_buffer_id]
        attr_buffer = vertex_buffers[attr_buffer_id]

        if pos_buffer.stride != 8 or attr_buffer.stride < 20:
            continue

        indices = sorted(set(read_indices(data, index_buffers[mesh.index_buffer_id], mesh)))
        valid_indices = [
            i
            for i in indices
            if 0 <= i < pos_buffer.length and 0 <= i < attr_buffer.length
        ]
        if not valid_indices:
            continue

        positions: list[tuple[int, int, int]] = []
        for vi in valid_indices:
            po = pos_buffer.data_offset + pos_offset + vi * pos_buffer.stride
            positions.append((vi, i16(data, po), i16(data, po + 2)))

        xs = [p[1] for p in positions]
        ys = [p[2] for p in positions]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        is_atlas = bool(set(mesh.material_ids) & atlas_ids)
        is_base = (material_id in mesh.material_ids)
        is_bracket = "bracket" in mesh.name.lower() or bool(set(mesh.material_ids) & seal_ids)
        is_screw = "screw" in mesh.name.lower() or bool(set(mesh.material_ids) & screw_ids)
        
        is_collapsing = is_atlas or (delete_bracket and is_bracket) or (delete_screw and is_screw)
        
        if (min_x == max_x or min_y == max_y) and not is_collapsing:
            continue

        uv_offsets = [4, 8, 12, 16] if all_channels else [12]
        for vi, x, y in positions:
            if is_base and min_x != max_x and min_y != max_y:
                u = (x - min_x) / (max_x - min_x)
                v = (y - min_y) / (max_y - min_y)
                if flip_v:
                    v = 1.0 - v

                for uv_offset in uv_offsets:
                    ao = attr_buffer.data_offset + attr_offset + vi * attr_buffer.stride + uv_offset
                    put_u16(data, ao, round(u * 65535))
                    put_u16(data, ao + 2, round(v * 65535))
                    
            if is_collapsing:
                po = pos_buffer.data_offset + pos_offset + vi * pos_buffer.stride
                put_u16(data, po, 0)
                put_u16(data, po + 2, 0)
                put_u16(data, po + 4, 0)

        if is_base:
            reset_texcoord_transforms(data, mesh, channels=4 if all_channels else 3)
            patched_meshes += 1
            patched_vertices_total += len(valid_indices)

    if patched_meshes == 0:
        raise ModelbinError(
            "Found matching material IDs, but no compatible plate meshes were patched."
        )

    report = (
        f"Patched {patched_meshes} mesh(es), {patched_vertices_total} vertex references. "
        f"Material ID {material_id}, flip_v={flip_v}, all_channels={all_channels}."
    )

    if dry_run:
        return "DRY RUN: " + report

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if input_path.resolve() == output_path.resolve():
        backup = input_path.with_suffix(input_path.suffix + ".bak")
        if not backup.exists():
            shutil.copy2(input_path, backup)
        output_path.write_bytes(data)
        return report + f" Backup: {backup}"

    output_path.write_bytes(data)
    return report + f" Output: {output_path}"


def detect_plate_base_material_id(meshes: list[MeshInfo]) -> int:
    scores: dict[int, int] = {}
    max_single: dict[int, int] = {}
    for mesh in meshes:
        ids = [m for m in mesh.material_ids if m >= 0]
        if not ids or mesh.vertex_layout_id not in (0, 1) or mesh.index_count < 60:
            continue

        name_lower = mesh.name.lower()
        if "platebracket" in name_lower:
            continue
        if name_lower and "platejpn" not in name_lower:
            continue
        mat = ids[0]
        scores[mat] = scores.get(mat, 0) + mesh.index_count
        max_single[mat] = max(max_single.get(mat, 0), mesh.index_count)

    if not scores:
        raise ModelbinError("Could not auto-detect a plate base material ID.")
    return max(scores, key=lambda mat: (max_single[mat], scores[mat]))


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(input_path.stem + ".planar_plate.modelbin")


def run_gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("FH6 Plate Patcher")
    root.geometry("500x300")
    root.minsize(460, 250)

    input_var = tk.StringVar()
    output_var = tk.StringVar()
    material_var = tk.StringVar(value="auto")
    status_var = tk.StringVar(value="Choose a modelbin to patch.")

    def choose_input() -> None:
        path = filedialog.askopenfilename(
            title="Choose modelbin",
            filetypes=[("Modelbin files", "*.modelbin"), ("All files", "*.*")],
        )
        if not path:
            return
        input_var.set(path)
        output_var.set(str(default_output_path(Path(path))))
        status_var.set("Ready.")

    def choose_output() -> None:
        initial = output_var.get() or (
            str(default_output_path(Path(input_var.get()))) if input_var.get() else ""
        )
        path = filedialog.asksaveasfilename(
            title="Save patched modelbin as",
            initialfile=Path(initial).name if initial else "patched.modelbin",
            initialdir=str(Path(initial).parent) if initial else None,
            defaultextension=".modelbin",
            filetypes=[("Modelbin files", "*.modelbin"), ("All files", "*.*")],
        )
        if path:
            output_var.set(path)

    def patch_clicked() -> None:
        try:
            if not input_var.get():
                raise ModelbinError("Choose an input modelbin first.")
            input_path = Path(input_var.get())
            output_path = Path(output_var.get()) if output_var.get() else default_output_path(input_path)
            material_text = material_var.get().strip().lower()
            material_id = None if material_text in ("", "auto") else int(material_text, 0)
            status_var.set("Patching...")
            root.update_idletasks()
            result = patch_modelbin(
                input_path=input_path,
                output_path=output_path,
                material_id=material_id,
                flip_v=True,
                all_channels=True,
                dry_run=False,
            )
            status_var.set(result)
            messagebox.showinfo("Done", result)
        except Exception as exc:
            status_var.set(f"Error: {exc}")
            messagebox.showerror("Patch failed", f"{exc}\n\n{traceback.format_exc()}")

    padding = {"padx": 10, "pady": 8}
    frame = ttk.Frame(root)
    frame.pack(fill="both", expand=True, padx=14, pady=14)
    frame.columnconfigure(1, weight=1)

    ttk.Label(frame, text="Input modelbin").grid(row=0, column=0, sticky="w", **padding)
    ttk.Entry(frame, textvariable=input_var).grid(row=0, column=1, sticky="ew", **padding)
    ttk.Button(frame, text="Browse...", command=choose_input).grid(row=0, column=2, **padding)

    ttk.Label(frame, text="Output modelbin").grid(row=1, column=0, sticky="w", **padding)
    ttk.Entry(frame, textvariable=output_var).grid(row=1, column=1, sticky="ew", **padding)
    ttk.Button(frame, text="Save as...", command=choose_output).grid(row=1, column=2, **padding)

    ttk.Label(frame, text="Plate base material ID").grid(row=2, column=0, sticky="w", **padding)
    ttk.Entry(frame, textvariable=material_var, width=10).grid(row=2, column=1, sticky="w", **padding)

    ttk.Button(frame, text="Patch Modelbin", command=patch_clicked).grid(
        row=3, column=1, sticky="w", padx=10, pady=16
    )

    ttk.Separator(frame).grid(row=4, column=0, columnspan=3, sticky="ew", pady=8)

    ttk.Label(frame, textvariable=status_var, wraplength=690).grid(
        row=5, column=0, columnspan=3, sticky="w", padx=10, pady=16
    )

    root.mainloop()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Patch FH6 plate modelbin UVs.")
    parser.add_argument("input", nargs="?", help="Input .modelbin. Omit to open the GUI.")
    parser.add_argument("-o", "--output", help="Output .modelbin path.")
    parser.add_argument(
        "--material-id",
        default="auto",
        help="Plate base material ID, or 'auto'. Default: auto",
    )
    parser.add_argument("--no-flip-v", action="store_true", help="Do not flip V.")
    parser.add_argument(
        "--uv2-only",
        action="store_true",
        help="Only patch TEXCOORD2 instead of TEXCOORD0 through TEXCOORD3.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Analyze without writing.")
    args = parser.parse_args(argv)

    if not args.input:
        run_gui()
        return 0

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else default_output_path(input_path)
    result = patch_modelbin(
        input_path=input_path,
        output_path=output_path,
        material_id=None if str(args.material_id).lower() == "auto" else int(args.material_id, 0),
        flip_v=not args.no_flip_v,
        all_channels=not args.uv2_only,
        dry_run=args.dry_run,
    )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
