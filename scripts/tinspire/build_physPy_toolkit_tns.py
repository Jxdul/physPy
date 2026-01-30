#!/usr/bin/env python3
# Builds a TI-Nspire .tns document containing the physPy toolkit scripts.
# Requires TI-Nspire Student Software installed (for libphoenix.dylib).
#
# Run (Apple Silicon):
#   arch -x86_64 python3 -B scripts/tinspire/build_physPy_toolkit_tns.py
#
# Output:
#   scripts/tinspire/physPy_toolkit.tns

from __future__ import print_function

import ctypes
import os
import struct
import sys
import platform
import tempfile
import zlib


TEMPLATE_TNS = (
    "/Applications/TI-Nspire CX CAS Student Software.app/"
    "Contents/Resources/res/documents/examples/en/Getting Started Python.tns"
)
LIBPHOENIX = (
    "/Applications/TI-Nspire CX CAS Student Software.app/"
    "Contents/MacOS/libphoenix.dylib"
)


def _read_file(path):
    with open(path, "rb") as f:
        return f.read()


def _find_local_entry(tns_bytes, filename):
    # Find the PK local header matching filename and return (pk_off, header, data_off).
    # Works for the template, even when TI uses a 6-byte preheader before PK.
    target = filename.encode("utf-8")
    i = 0
    while True:
        pk = tns_bytes.find(b"PK\x03\x04", i)
        if pk < 0:
            return None
        hdr = tns_bytes[pk : pk + 30]
        if len(hdr) < 30:
            return None
        sig, ver, gpf, method, mtime, mdate, crc, comp, uncomp, fnlen, extralen = struct.unpack(
            "<IHHHHHIIIHH", hdr
        )
        name = tns_bytes[pk + 30 : pk + 30 + fnlen]
        if name == target:
            data_off = pk + 30 + fnlen + extralen
            return pk, {
                "sig": sig,
                "ver": ver,
                "gpf": gpf,
                "method": method,
                "mtime": mtime,
                "mdate": mdate,
                "crc": crc,
                "comp": comp,
                "uncomp": uncomp,
                "fnlen": fnlen,
                "extralen": extralen,
                "name": name,
            }, data_off
        i = pk + 4


def _load_phoenix():
    if not os.path.exists(LIBPHOENIX):
        raise RuntimeError("libphoenix not found: %s" % LIBPHOENIX)
    lib = ctypes.CDLL(LIBPHOENIX)

    lib.TI_ZP_Open.restype = ctypes.c_void_p
    lib.TI_ZP_Open.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

    lib.TI_ZP_Close.restype = ctypes.c_int
    lib.TI_ZP_Close.argtypes = [ctypes.c_void_p]

    # int TI_ZP_FindAndReadFile(zip, char** out, filename, max_len)
    lib.TI_ZP_FindAndReadFile.restype = ctypes.c_int
    lib.TI_ZP_FindAndReadFile.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_char_p,
        ctypes.c_int,
    ]

    # int TI_ZP_Write(zip, data_ptr, data_len, filename, flags)
    lib.TI_ZP_Write.restype = ctypes.c_int
    lib.TI_ZP_Write.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
    ]

    lib.TI_SR_newArchive.restype = ctypes.c_void_p
    lib.TI_SR_newArchive.argtypes = []

    lib.TI_SR_deleteArchive.restype = None
    lib.TI_SR_deleteArchive.argtypes = [ctypes.POINTER(ctypes.c_void_p)]

    lib.write_n_to_archive.restype = None
    lib.write_n_to_archive.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]

    lib.TI_XML_Decompress.restype = ctypes.c_void_p
    lib.TI_XML_Decompress.argtypes = [ctypes.c_void_p]

    lib.TI_SR_ArchiveToString.restype = ctypes.c_void_p
    lib.TI_SR_ArchiveToString.argtypes = [ctypes.c_void_p]

    return lib


def _decompress_problem1_xml(lib, tns_bytes):
    found = _find_local_entry(tns_bytes, "Problem1.xml")
    if not found:
        raise RuntimeError("Problem1.xml not found in template")
    pk, hdr, data_off = found
    comp = hdr["comp"]
    if comp <= 0:
        raise RuntimeError("Problem1.xml has empty compressed payload")
    compdata = tns_bytes[data_off : data_off + comp]
    if len(compdata) != comp:
        raise RuntimeError("Problem1.xml payload truncated")

    arch = lib.TI_SR_newArchive()
    if not arch:
        raise RuntimeError("TI_SR_newArchive failed")

    try:
        buf = ctypes.create_string_buffer(compdata)
        lib.write_n_to_archive(arch, buf, len(compdata))
        arch2 = lib.TI_XML_Decompress(arch)
        if not arch2:
            raise RuntimeError("TI_XML_Decompress failed")
        try:
            s_ptr = lib.TI_SR_ArchiveToString(arch2)
            if not s_ptr:
                raise RuntimeError("TI_SR_ArchiveToString failed")
            # Read a bit more than expected; then trim at closing tag.
            text = ctypes.string_at(s_ptr, hdr["uncomp"] + 1024).decode("utf-8", "replace")
            end = text.find("</prob>")
            if end != -1:
                text = text[: end + len("</prob>")]
            return text
        finally:
            p2 = ctypes.c_void_p(arch2)
            lib.TI_SR_deleteArchive(ctypes.byref(p2))
    finally:
        p1 = ctypes.c_void_p(arch)
        lib.TI_SR_deleteArchive(ctypes.byref(p1))


def _extract_deflate_raw(tns_bytes, filename):
    found = _find_local_entry(tns_bytes, filename)
    if not found:
        raise RuntimeError("%s not found in template" % filename)
    pk, hdr, data_off = found
    if hdr["method"] != 8:
        raise RuntimeError("%s expected method 8, got %s" % (filename, hdr["method"]))
    comp = hdr["comp"]
    compdata = tns_bytes[data_off : data_off + comp]
    if len(compdata) != comp:
        raise RuntimeError("%s payload truncated" % filename)
    return zlib.decompress(compdata, -15)


def _find_first_local_name_ending_with(tns_bytes, suffix):
    suf = suffix.encode("utf-8")
    i = 0
    while True:
        pk = tns_bytes.find(b"PK\x03\x04", i)
        if pk < 0:
            return None
        hdr = tns_bytes[pk : pk + 30]
        if len(hdr) < 30:
            return None
        _sig, _ver, _gpf, _method, _mtime, _mdate, _crc, _comp, _uncomp, fnlen, _extralen = struct.unpack(
            "<IHHHHHIIIHH", hdr
        )
        name = tns_bytes[pk + 30 : pk + 30 + fnlen]
        if name.endswith(suf):
            return name.decode("utf-8", "replace")
        i = pk + 4


def _parse_timlp_document_entry(tns_bytes):
    # TIMLP header: "*TIMLP0901" + local header (no PK sig) + filename + data
    if not tns_bytes.startswith(b"*TIMLP"):
        raise RuntimeError("Template does not start with TIMLP header")
    sig = tns_bytes[:10]
    hdr = tns_bytes[10 : 10 + 26]
    if len(hdr) != 26:
        raise RuntimeError("TIMLP header too short")
    ver, gpf, method, mtime, mdate, crc, comp, uncomp, fnlen, extralen = struct.unpack(
        "<HHHHHIIIHH", hdr
    )
    name = tns_bytes[10 + 26 : 10 + 26 + fnlen]
    data_off = 10 + 26 + fnlen + extralen
    data_end = data_off + comp
    if len(name) != fnlen:
        raise RuntimeError("TIMLP filename length mismatch")
    if data_end > len(tns_bytes):
        raise RuntimeError("TIMLP data truncated")
    entry = {
        "sig": sig,
        "ver": ver,
        "gpf": gpf,
        "method": method,
        "mtime": mtime,
        "mdate": mdate,
        "crc": crc,
        "comp": comp,
        "uncomp": uncomp,
        "fnlen": fnlen,
        "extralen": extralen,
        "name": name,
        "data_off": data_off,
        "data_end": data_end,
    }
    return entry


def _compress_xml_via_temp(lib, filename, xml_bytes):
    # Use TI_ZP_Write to compress XML into TIMLP format, then parse bytes.
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".tns")
    os.close(tmp_fd)
    try:
        h = lib.TI_ZP_Open(tmp_path.encode("utf-8"), b"w+b")
        if not h:
            raise RuntimeError("TI_ZP_Open failed for temp")
        try:
            n = lib.TI_ZP_Write(h, xml_bytes, len(xml_bytes), filename.encode("utf-8"), 2)
            if n <= 0:
                raise RuntimeError("TI_ZP_Write temp XML failed: %s" % n)
        finally:
            lib.TI_ZP_Close(h)

        with open(tmp_path, "rb") as f:
            data = f.read()
        entry = _parse_timlp_document_entry(data)
        if entry["name"].decode("utf-8", "replace") != filename:
            raise RuntimeError("Temp TIMLP entry mismatch")
        compdata = data[entry["data_off"] : entry["data_end"]]
        return entry, compdata
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def _deflate_raw(data):
    comp = zlib.compressobj(level=9, wbits=-15)
    out = comp.compress(data) + comp.flush()
    return out


def _local_header(name, method, mtime, mdate, crc, comp_size, uncomp_size, gpf=0, ver=20):
    name_b = name.encode("utf-8")
    return struct.pack(
        "<IHHHHHIIIHH",
        0x04034B50,
        ver,
        gpf,
        method,
        mtime,
        mdate,
        crc,
        comp_size,
        uncomp_size,
        len(name_b),
        0,
    ) + name_b


def _central_header(name, method, mtime, mdate, crc, comp_size, uncomp_size, lhoff, gpf=0, ver=20):
    name_b = name.encode("utf-8")
    return struct.pack(
        "<IHHHHHHIIIHHHHHII",
        0x02014B50,
        ver,
        ver,
        gpf,
        method,
        mtime,
        mdate,
        crc,
        comp_size,
        uncomp_size,
        len(name_b),
        0,  # extra
        0,  # comment
        0,  # disk
        0,  # internal attr
        0,  # external attr
        lhoff,
    ) + name_b


def _make_help_script(title, lines):
    # Keep it tiny; no math, no heavy helpers.
    out = []
    out.append("# %s" % title)
    out.append("")
    out.append("def pause():")
    out.append("    try:")
    out.append("        input('Press Enter...')")  # TI uses input()
    out.append("    except:")
    out.append("        pass")
    out.append("")
    out.append("def main():")
    out.append("    print('%s')" % title.replace("'", "\\'"))
    out.append("    print('')")  # blank line
    for s in lines:
        out.append("    print('%s')" % s.replace("'", "\\'"))
    out.append("    print('')")  # blank line
    out.append("    pause()")
    out.append("")
    out.append("main()")
    out.append("")
    return ("\n".join(out)).encode("utf-8")


def main():
    if platform.machine().startswith("arm"):
        print("ERROR: This script must run under Rosetta (x86_64).")
        print("Run: arch -x86_64 python3 -B scripts/tinspire/build_physPy_toolkit_tns.py")
        return 2
    if not os.path.exists(TEMPLATE_TNS):
        print("Template .tns not found:", TEMPLATE_TNS)
        return 2

    here = os.path.dirname(os.path.abspath(__file__))
    proj_scripts = os.path.abspath(os.path.join(here, ".."))

    # Main apps (source files in repo).
    apps = {
        "fields_app.py": os.path.join(proj_scripts, "fields_app.py"),
        "gauss_flux_app.py": os.path.join(proj_scripts, "gauss_flux_app.py"),
        "potential_energy_app.py": os.path.join(proj_scripts, "potential_energy_app.py"),
        "motion_app.py": os.path.join(proj_scripts, "motion_app.py"),
    }

    for name, path in apps.items():
        if not os.path.exists(path):
            print("Missing source:", path)
            return 2

    # Rename the template's 7 PythonEditor scripts into 4 apps + 3 optional helpers.
    name_map = {
        "hello.py": "fields_app.py",
        "loop_example.py": "gauss_flux_app.py",
        "heads_or_tails.py": "potential_energy_app.py",
        "plotting.py": "motion_app.py",
        "drawing.py": "zz_help.py",
        "image.py": "zz_units.py",
        "hub.py": "zz_coords.py",
    }

    lib = _load_phoenix()

    template_bytes = _read_file(TEMPLATE_TNS)
    prob1 = _decompress_problem1_xml(lib, template_bytes)

    for old, new in name_map.items():
        prob1 = prob1.replace(old, new)

    # Basic sanity: no old names left.
    for old in sorted(name_map.keys()):
        if old in prob1:
            raise RuntimeError("Problem1.xml still contains: %s" % old)

    # --- build output bytes manually to preserve valid TIMLP structure ---
    # Document.xml TIMLP header + compressed data from template.
    doc_entry = _parse_timlp_document_entry(template_bytes)
    doc_prefix = template_bytes[: doc_entry["data_end"]]

    # BMP resource (compressed bytes from template).
    bmp_name = _find_first_local_name_ending_with(template_bytes, ".BMP")
    if not bmp_name:
        raise RuntimeError("Could not find a .BMP entry in the template")
    bmp_found = _find_local_entry(template_bytes, bmp_name)
    if not bmp_found:
        raise RuntimeError("BMP local header not found")
    bmp_pk, bmp_hdr, bmp_data_off = bmp_found
    bmp_comp = template_bytes[bmp_data_off : bmp_data_off + bmp_hdr["comp"]]

    # Problem1.xml compressed bytes via temp TIMLP.
    prob1_bytes = prob1.encode("utf-8")
    prob_entry, prob_comp = _compress_xml_via_temp(lib, "Problem1.xml", prob1_bytes)

    # Optional small helpers (also zlib).
    helpers = {
        "zz_help.py": _make_help_script(
            "physPy Toolkit - Quick Start",
            [
                "Run one of the 4 apps:",
                "  fields_app.py",
                "  gauss_flux_app.py",
                "  potential_energy_app.py",
                "  motion_app.py",
                "",
                "Tips:",
                "  Enter coords as x,y or (x,y)",
                "  Units accepted: 5uC, 2cm, 1kV, 3uC/m^2",
                "  If no unit: uses the prompt's unit",
            ],
        ),
        "zz_units.py": _make_help_script(
            "physPy Toolkit - Units",
            [
                "Examples you can type:",
                "  5uC   120nC   -3mC",
                "  2cm   0.50m   12mm",
                "  3kV   120V",
                "  4uC/m   2nC/m",
                "  6uC/m^2  1nC/m^2",
                "  0.02m^2",
            ],
        ),
        "zz_coords.py": _make_help_script(
            "physPy Toolkit - Coords",
            [
                "Vector/point entry:",
                "  x,y",
                "  (x,y)",
                "",
                "Examples:",
                "  2,3",
                "  -1.5, 0",
                "  (0, -4)",
            ],
        ),
    }

    # Build PK entries list (name, method, mtime, mdate, crc, comp_bytes, uncomp_len).
    entries = []

    # Problem1.xml (method 13).
    prob_crc = prob_entry["crc"]
    entries.append(
        {
            "name": "Problem1.xml",
            "method": prob_entry["method"],
            "mtime": prob_entry["mtime"],
            "mdate": prob_entry["mdate"],
            "crc": prob_crc,
            "comp": prob_comp,
            "uncomp": prob_entry["uncomp"],
        }
    )

    # BMP (reuse template header values).
    entries.append(
        {
            "name": bmp_name,
            "method": bmp_hdr["method"],
            "mtime": bmp_hdr["mtime"],
            "mdate": bmp_hdr["mdate"],
            "crc": bmp_hdr["crc"],
            "comp": bmp_comp,
            "uncomp": bmp_hdr["uncomp"],
        }
    )

    # Scripts (.py) and helpers (deflate raw).
    # Use hello.py mod time/date from template as a consistent timestamp.
    hello_hdr = _find_local_entry(template_bytes, "hello.py")[1]
    ts_mtime = hello_hdr["mtime"]
    ts_mdate = hello_hdr["mdate"]

    for name, path in apps.items():
        data = _read_file(path)
        comp = _deflate_raw(data)
        crc = zlib.crc32(data) & 0xFFFFFFFF
        entries.append(
            {
                "name": name,
                "method": 8,
                "mtime": ts_mtime,
                "mdate": ts_mdate,
                "crc": crc,
                "comp": comp,
                "uncomp": len(data),
            }
        )

    for name, data in helpers.items():
        comp = _deflate_raw(data)
        crc = zlib.crc32(data) & 0xFFFFFFFF
        entries.append(
            {
                "name": name,
                "method": 8,
                "mtime": ts_mtime,
                "mdate": ts_mdate,
                "crc": crc,
                "comp": comp,
                "uncomp": len(data),
            }
        )

    # Build output bytes
    out = bytearray()
    out += doc_prefix

    # local headers for PK entries
    central = []
    for e in entries:
        lhoff = len(out)
        lh = _local_header(
            e["name"],
            e["method"],
            e["mtime"],
            e["mdate"],
            e["crc"],
            len(e["comp"]),
            e["uncomp"],
        )
        out += lh
        out += e["comp"]
        central.append(
            _central_header(
                e["name"],
                e["method"],
                e["mtime"],
                e["mdate"],
                e["crc"],
                len(e["comp"]),
                e["uncomp"],
                lhoff,
            )
        )

    # Central directory (include Document.xml too).
    # Document.xml is at local header offset 0 in TIMLP.
    central_doc = _central_header(
        doc_entry["name"].decode("utf-8", "replace"),
        doc_entry["method"],
        doc_entry["mtime"],
        doc_entry["mdate"],
        doc_entry["crc"],
        doc_entry["comp"],
        doc_entry["uncomp"],
        0,
        doc_entry["gpf"],
        doc_entry["ver"],
    )

    # Place Document.xml first to mimic template order.
    central_all = [central_doc] + central
    cd_offset = len(out)
    cd_size = sum(len(c) for c in central_all)
    for c in central_all:
        out += c

    # TIPD end record (EOCD equivalent with TI signature).
    # Structure mirrors EOCD: disk, disk_start, entries_disk, entries_total,
    # cd_size, cd_offset, comment_len.
    out += b"TIPD"
    out += struct.pack(
        "<HHHHIIH",
        0,
        0,
        len(central_all),
        len(central_all),
        cd_size,
        cd_offset,
        0,
    )

    # Write output file
    out_tns = os.path.join(here, "physPy_toolkit.tns")
    with open(out_tns, "wb") as f:
        f.write(out)

    print("Wrote:", out_tns)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print("ERROR:", e)
        raise
