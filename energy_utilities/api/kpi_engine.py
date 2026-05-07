import frappe
from frappe.utils import nowdate

@frappe.whitelist()
def compute_kpis(vertical=None, period_days=1):
    """Run all KPIs for a vertical based on its config."""
    filters = {"active": 1}
    if vertical: filters["name"] = vertical
    for v in frappe.get_all("Industry Vertical", filters=filters, pluck="name"):
        cfg = frappe.get_all("Vertical Config", filters={"vertical": v}, limit=1)
        if not cfg: continue
        cfg_doc = frappe.get_doc("Vertical Config", cfg[0].name)
        for kpi in cfg_doc.kpi_table:
            try:
                value = evaluate_formula(kpi.formula, v, period_days)
                frappe.get_doc({
                    "doctype": "KPI Log",
                    "vertical": v, "kpi_name": kpi.kpi_name,
                    "value": value, "target": kpi.target_value,
                    "unit": kpi.unit, "log_date": nowdate()
                }).insert(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(str(e), f"KPI {kpi.kpi_name} failed")

def evaluate_formula(formula, vertical, period_days):
    """Sandboxed evaluator."""
    ctx = build_context(vertical, period_days)
    # Be careful with eval in production, this is a demonstration
    return eval(formula, {"__builtins__": {}}, ctx)

def build_context(vertical, period_days):
    from frappe.utils import add_days
    start = add_days(nowdate(), -period_days)
    sums = frappe.db.sql("""
        SELECT parameter, SUM(delta_value) total
        FROM `tabOperational Reading`
        WHERE vertical=%s AND docstatus=1 AND reading_date >= %s
        GROUP BY parameter
    """, (vertical, start), as_dict=True)
    return {row.parameter: row.total or 0 for row in sums}
