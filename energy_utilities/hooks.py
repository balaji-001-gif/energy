app_name = "energy_utilities"
app_title = "Energy & Utilities"
app_publisher = "Your Company"
app_description = "Universal Energy & Utilities Operations Suite"
app_version = "1.0.0"
required_apps = ["frappe", "erpnext"]

after_install = "energy_utilities.api.vertical_loader.install_defaults"
after_migrate = ["energy_utilities.api.vertical_loader.install_defaults"]

scheduler_events = {
    "cron": {
        "*/15 * * * *": ["energy_utilities.api.iot_gateway.poll_external_sources"]
    },
    "hourly": [
        "energy_utilities.api.kpi_engine.compute_kpis",
        "energy_utilities.api.incident_engine.recalc_durations"
    ],
    "daily": [
        "energy_utilities.api.billing_engine.run_daily_billing"
    ]
}

doc_events = {
    "Operational Reading": {
        "on_submit": "energy_utilities.api.billing_engine.try_invoice"
    },
    "Operational Incident": {
        "on_submit": "energy_utilities.api.incident_engine.notify_stakeholders"
    },
    "IoT Event": {
        "after_insert": "energy_utilities.api.iot_gateway.check_thresholds_hook"
    }
}

fixtures = [
    {"dt": "Industry Vertical"},
    {"dt": "Vertical Config"},
    {"dt": "Workflow", "filters": [["name", "like", "EU-%"]]},
    {"dt": "Notification", "filters": [["module", "=", "Energy Utilities"]]},
    {"dt": "Workspace", "filters": [["module", "=", "Energy Utilities"]]},
    {"dt": "Role", "filters": [["name", "like", "EU %"]]}
]
