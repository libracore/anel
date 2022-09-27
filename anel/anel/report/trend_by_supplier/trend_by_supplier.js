// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Trend By Supplier"] = {
    "filters": [
        {
            "fieldname":"p1_from_date",
            "label": __("From Date P1"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -2),
            "reqd": 1
        },
                {
            "fieldname":"p1_to_date",
            "label": __("To Date P1"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname":"p2_from_date",
            "label": __("From Date P2"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -6),
            "reqd": 1
        },
        {
            "fieldname":"p2_to_date",
            "label": __("To Date P2"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        }
    ]
};
