IFC to CSV Converter
This Python tool extracts element data (attributes + properties) from IFC models and exports them to CSV or Excel.
Created as part of my BIM automation portfolio project to demonstrate skills in IFC data handling, Python scripting, and digital construction workflows.

Features
Supports IFC2x3 and IFC4 models.

Filter by specific IFC classes (e.g., IfcWall, IfcDoor) or export all.

Extracts base attributes (GlobalId, Name, Level, Entity) plus all Pset/Qto properties.

Outputs clean CSV or Excel for further analysis.

Prerequisites
Python 3.11+

ifcopenshell

pandas (optional, for Excel export)

Install dependencies:

bash
Kopieren
Bearbeiten
pip install -r requirements.txt
Usage
bash
Kopieren
Bearbeiten
python ifc_to_csv.py model.ifc -o output.csv
Optional:

bash
Kopieren
Bearbeiten
python ifc_to_csv.py model.ifc -o output.xlsx
Example Output
GlobalId	Entity	Name	Level	Pset_WallCommon:FireRating	Qto_WallBaseQuantities:Length
2hjlX6f...	IfcWall	Basic 200mm	Level 1	REI60	12.3

Credits
Author: Rodion Dykhanov
