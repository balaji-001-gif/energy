import frappe
from frappe.model.document import Document

class OperationalReading(Document):
    def validate(self):
        self.fetch_previous()
        self.calc_delta()
        self.calc_amount()

    def fetch_previous(self):
        scope_field = "consumer" if self.consumer else "asset"
        scope_value = self.consumer or self.asset
        if not scope_value:
            return
        last = frappe.db.sql(f"""
            SELECT current_value FROM `tabOperational Reading`
            WHERE {scope_field}=%s AND parameter=%s AND name!=%s AND docstatus=1
            ORDER BY reading_date DESC LIMIT 1
        """, (scope_value, self.parameter, self.name or ""))
        self.previous_value = last[0][0] if last else 0

    def calc_delta(self):
        self.delta_value = (self.current_value or 0) - (self.previous_value or 0)

    def calc_amount(self):
        if self.tariff and self.delta_value:
            # Assuming Service Tariff has a calculate method
            try:
                tariff = frappe.get_doc("Service Tariff", self.tariff)
                if hasattr(tariff, "calculate"):
                    self.amount = tariff.calculate(self.delta_value)
            except Exception:
                pass
