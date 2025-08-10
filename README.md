# IFC → CSV Converter

Python tool to export IFC elements and their data to **CSV**.

## Features
- Base attributes: GlobalId, Entity, Name, Level
- Include top-level attributes via `--props`
- Export all Property Sets (Pset) and Quantities (Qto) as flat columns
- Filter by IFC classes or `*` for all

## Install
```bash
python -m venv .venv && . .venv/bin/activate
pip install ifcopenshell
```

## Usage
```bash
python ifc_to_csv.py model.ifc
python ifc_to_csv.py model.ifc -c "*" -o all.csv
```
