import frappe
from frappe.utils import now_datetime

@frappe.whitelist(allow_guest=False)
def ingest(payload):
    """
    Universal IoT/SCADA ingestion endpoint.
    """
    if isinstance(payload, str):
        import json; payload = json.loads(payload)

    # 1. Log raw IoT event
    evt = frappe.get_doc({
        "doctype": "IoT Event",
        "asset": payload.get("asset"),
        "vertical": payload.get("vertical"),
        "parameter": payload.get("parameter"),
        "value": payload.get("value"),
        "uom": payload.get("uom"),
        "event_time": payload.get("timestamp") or now_datetime()
    }).insert(ignore_permissions=True)

    # 2. Threshold check
    check_thresholds(evt)

    # 3. Persist as Operational Reading if it's a meter param
    if payload.get("is_meter"):
        frappe.get_doc({
            "doctype": "Operational Reading",
            "vertical": payload["vertical"],
            "asset": payload["asset"],
            "reading_source": "SCADA",
            "parameter": payload["parameter"],
            "current_value": payload["value"],
            "uom": payload.get("uom"),
            "reading_date": evt.event_time
        }).insert(ignore_permissions=True).submit()

    return {"ok": True, "event": evt.name}

def check_thresholds(evt):
    """Compare against Vertical Config thresholds."""
    cfg = frappe.get_all("Vertical Config", filters={"vertical": evt.vertical}, limit=1)
    if not cfg:
        return
    cfg_doc = frappe.get_doc("Vertical Config", cfg[0].name)
    for t in cfg_doc.threshold_table:
        if t.parameter != evt.parameter:
            continue
        breached = False
        if t.min_value is not None and evt.value < t.min_value: breached = True
        if t.max_value is not None and evt.value > t.max_value: breached = True
        if breached:
            handle_breach(evt, t)

def handle_breach(evt, threshold):
    if threshold.action == "Create Incident":
        frappe.get_doc({
            "doctype": "Operational Incident",
            "vertical": evt.vertical,
            "asset": evt.asset,
            "incident_type": f"Auto-{threshold.parameter}-breach",
            "severity": threshold.alert_level if threshold.alert_level != "Warning" else "Medium",
            "start_time": evt.event_time,
            "root_cause": f"{threshold.parameter}={evt.value} breached limits"
        }).insert(ignore_permissions=True)
    elif threshold.action == "Shutdown Asset":
        frappe.db.set_value("Asset Node", evt.asset, "operational_status", "Shutdown")
    
    frappe.publish_realtime("threshold_breach", evt.as_dict())

def check_thresholds_hook(doc, method):
    check_thresholds(doc)

def poll_external_sources():
    """Placeholder for external SCADA polling"""
    pass
