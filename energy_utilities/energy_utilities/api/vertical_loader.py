import frappe

DEFAULT_VERTICALS = [
    {"vertical_code": "POWER_GEN", "vertical_name": "Power Generation", "category": "Generation", "icon": "lightning", "color": "#FFB400"},
    {"vertical_code": "TND",       "vertical_name": "Transmission & Distribution", "category": "Distribution", "icon": "plug", "color": "#1E88E5"},
    {"vertical_code": "OIL_GAS",   "vertical_name": "Oil & Gas",     "category": "Midstream",   "icon": "droplet", "color": "#6D4C41"},
    {"vertical_code": "WATER",     "vertical_name": "Water Utility", "category": "Water",        "icon": "water", "color": "#039BE5"},
    {"vertical_code": "SOLAR",     "vertical_name": "Solar Power",   "category": "Renewable",    "icon": "sun", "color": "#FDD835"},
    {"vertical_code": "WIND",      "vertical_name": "Wind Power",    "category": "Renewable",    "icon": "wind", "color": "#26A69A"},
    {"vertical_code": "METERING",  "vertical_name": "Smart Metering","category": "Metering",     "icon": "dashboard", "color": "#43A047"},
    {"vertical_code": "DISTRICT",  "vertical_name": "District Heating/Cooling", "category": "Distribution", "icon": "thermometer", "color": "#E64A19"},
    {"vertical_code": "EV",        "vertical_name": "EV Charging Network",       "category": "Distribution", "icon": "battery-full", "color": "#00ACC1"},
    {"vertical_code": "HYDROGEN",  "vertical_name": "Hydrogen Plant","category": "Generation",   "icon": "flask", "color": "#7E57C2"},
]

DEFAULT_CONFIGS = [
    {
        "config_key": "POWER_GEN_CFG", "vertical": "POWER_GEN",
        "asset_types": "Boiler,Turbine,Generator,Cooling Tower",
        "incident_types": "Trip,Forced Outage,Planned Shutdown,Derating",
        "reading_unit": "kWh", "secondary_unit": "MW",
        "kpi_table": [
            {"kpi_name": "PLF", "formula": "actual_gen/(capacity*hours)*100", "target_value": 85, "unit": "%"},
            {"kpi_name": "Heat Rate", "formula": "fuel_kcal/gen_kwh", "target_value": 2400, "unit": "kcal/kWh"}
        ]
    },
    {
        "config_key": "TND_CFG", "vertical": "TND",
        "asset_types": "Substation,Feeder,Transformer,Pole",
        "incident_types": "Outage,Voltage Sag,Trip,Vandalism",
        "reading_unit": "kWh",
        "kpi_table": [
            {"kpi_name": "SAIDI", "formula": "sum(duration*affected)/total", "target_value": 60, "unit": "min/customer"},
            {"kpi_name": "SAIFI", "formula": "sum(affected)/total", "target_value": 1.5, "unit": "events/customer"},
            {"kpi_name": "AT&C Loss", "formula": "(input-billed)/input*100", "target_value": 12, "unit": "%"}
        ]
    },
    {
        "config_key": "OIL_GAS_CFG", "vertical": "OIL_GAS",
        "asset_types": "Well,Pipeline,Compressor Station,Storage Tank,Refinery Unit",
        "incident_types": "Leak,Spill,Pressure Drop,Pigging Failure,Fire",
        "reading_unit": "bbl", "secondary_unit": "MMSCFD",
        "kpi_table": [
            {"kpi_name": "Throughput", "formula": "flow_total/period", "unit": "bbl/day"},
            {"kpi_name": "Pipeline Integrity", "formula": "1-leak_count/length_km", "unit": "score"}
        ]
    }
]

def install_defaults():
    for v in DEFAULT_VERTICALS:
        if not frappe.db.exists("Industry Vertical", v["vertical_code"]):
            frappe.get_doc({"doctype": "Industry Vertical", **v}).insert(ignore_permissions=True)

    for c in DEFAULT_CONFIGS:
        if not frappe.db.exists("Vertical Config", c["config_key"]):
            doc = frappe.new_doc("Vertical Config")
            doc.update({k: v for k, v in c.items() if k != "kpi_table"})
            for kpi in c.get("kpi_table", []):
                doc.append("kpi_table", kpi)
            doc.insert(ignore_permissions=True)
    frappe.db.commit()
