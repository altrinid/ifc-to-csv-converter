#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IFC → CSV Converter
-------------------
Exports IFC elements and their data (attributes + Psets/Qto) into CSV.
"""

import argparse
import csv
import os
from typing import List, Dict, Any

try:
    import ifcopenshell
except ImportError:
    raise SystemExit("Please install ifcopenshell: pip install ifcopenshell")

def get_name(entity) -> str:
    for attr in ("Name", "GlobalId", "Tag"):
        v = getattr(entity, attr, None)
        if v:
            return str(v)
    return f"{entity.is_a()}_{entity.id()}"

def get_level(entity) -> str:
    try:
        for inv in getattr(entity, "IsContainedIn", []) or []:
            if inv.is_a("IfcRelContainedInSpatialStructure") and inv.RelatingStructure:
                return get_name(inv.RelatingStructure)
    except Exception:
        pass
    return ""

def normalize(val):
    if val is None:
        return ""
    if hasattr(val, "wrappedValue"):
        return val.wrappedValue
    return str(val)

def get_psets_flat(entity) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        from ifcopenshell.util.element import get_psets  # type: ignore
        psets = get_psets(entity, include_inherited=True)
        flat = {}
        for grp, vals in psets.items():
            if isinstance(vals, dict):
                for k, v in vals.items():
                    flat[f"{grp}:{k}"] = v
            else:
                flat[grp] = vals
        out.update(flat)
        return out
    except Exception:
        pass
    try:
        for rel in getattr(entity, "IsDefinedBy", []) or []:
            ps = getattr(rel, "RelatingPropertyDefinition", None)
            if not ps:
                continue
            if ps.is_a("IfcPropertySet"):
                for p in ps.HasProperties or []:
                    key = f"{ps.Name}:{p.Name}"
                    val = getattr(p, "NominalValue", getattr(p, "Description", None))
                    out[key] = getattr(val, "wrappedValue", val)
            elif ps.is_a("IfcElementQuantity"):
                for q in ps.Quantities or []:
                    val = None
                    for f in ("LengthValue","AreaValue","VolumeValue","CountValue","WeightValue","TimeValue"):
                        if hasattr(q, f) and getattr(q, f) is not None:
                            val = getattr(q, f)
                            break
                    out[f"{ps.Name}:{q.Name}"] = val
    except Exception:
        pass
    return out

def gather_elements(model, classes: List[str]) -> List[Any]:
    if not classes or classes == ["*"]:
        return [e for e in model if hasattr(e, "GlobalId") and getattr(e, "GlobalId", None)]
    out = []
    for c in classes:
        try:
            out.extend(model.by_type(c))
        except Exception:
            pass
    return out

def extract_rows(ifc_path: str, classes: List[str], top_props: List[str], limit: int = 0):
    model = ifcopenshell.open(ifc_path)
    elements = gather_elements(model, classes)
    if limit and limit > 0:
        elements = elements[:limit]

    base_cols = ["GlobalId", "Entity", "Name", "Level"]
    rows = []
    dyn_keys = set()

    for e in elements:
        try:
            row = {
                "GlobalId": getattr(e, "GlobalId", ""),
                "Entity": e.is_a(),
                "Name": get_name(e),
                "Level": get_level(e),
            }
            for p in top_props:
                row[p] = normalize(getattr(e, p, ""))
            pflat = get_psets_flat(e)
            for k, v in pflat.items():
                if v is None:
                    continue
                k = str(k)
                row[k] = normalize(v)
                dyn_keys.add(k)
            rows.append(row)
        except Exception:
            continue

    dyn_cols = sorted(dyn_keys)
    extra_top = [p for p in top_props if p not in base_cols and p not in dyn_cols]
    header = base_cols + extra_top + dyn_cols
    return header, rows

def write_csv(header, rows, out_csv: str):
    os.makedirs(os.path.dirname(os.path.abspath(out_csv)) or ".", exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in header})

def main():
    ap = argparse.ArgumentParser(description="IFC → CSV converter (attributes + Psets/Qto)")
    ap.add_argument("ifc", help="Path to IFC file")
    ap.add_argument("-o", "--out", default="ifc_elements.csv", help="Output CSV path")
    ap.add_argument("-c", "--classes", default="IfcWall,IfcDoor,IfcWindow",
                    help='Comma-separated IFC classes (use "*" for all).')
    ap.add_argument("-p", "--props", default="PredefinedType,Tag",
                    help="Comma-separated top-level attributes")
    ap.add_argument("--limit", type=int, default=0, help="Limit number of elements")

    args = ap.parse_args()
    classes = [c.strip() for c in args.classes.split(",")] if args.classes else []
    props = [p.strip() for p in args.props.split(",")] if args.props else []

    header, rows = extract_rows(args.ifc, classes, props, args.limit)
    write_csv(header, rows, args.out)
    print(f"[OK] Exported {len(rows)} elements → {args.out}")

if __name__ == "__main__":
    main()
