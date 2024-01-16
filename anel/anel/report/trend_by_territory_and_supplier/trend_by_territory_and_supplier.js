// Copyright (c) 2022-2024, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Trend by Territory and Supplier"] = {
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
    ],
    "onload": (report) => {
        var inner_toolbars = document.getElementsByClassName("form-inner-toolbar");
        if (inner_toolbars) {
            for (var i = 0; i < inner_toolbars.length; i++) {
                inner_toolbars[i].innerHTML = "<div class=\"form-message text-muted small blue\">Absatz auf Stufe Ausgangsrechnung</div>";
            }
        }
    }
};
