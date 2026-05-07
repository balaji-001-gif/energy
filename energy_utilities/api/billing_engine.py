import frappe

def run_daily_billing():
    """Daily job to generate invoices for active connections"""
    pass

def try_invoice(doc, method):
    """Hook to try auto-invoicing when a reading is submitted"""
    settings = frappe.get_single("Energy Utilities Settings")
    if settings.auto_invoice and doc.consumer and doc.amount:
        create_sales_invoice(doc)

def create_sales_invoice(reading):
    # Logic to create ERPNext Sales Invoice
    pass
