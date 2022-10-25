from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
        {
            "label": _("Reports"),
            "icon": "fa fa-users",
            "items": [
                   {
                        "type": "report",
                        "name": "Customer Trend Flexdate",
                        "label": _("Customer Trend Flexdate"),
                        "doctype": "Sales Order",
                        "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "Trend By Territory",
                        "label": _("Trend By Territory"),
                        "doctype": "Sales Order",
                        "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "Trend By Customer",
                        "label": _("Trend By Customere"),
                        "doctype": "Sales Order",
                        "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "Trend By Item",
                        "label": _("Trend By Item"),
                        "doctype": "Sales Order",
                        "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "Trend By Supplier",
                        "label": _("Trend By Supplier"),
                        "doctype": "Sales Order",
                        "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "Supplier Orders",
                        "label": _("Supplier Orders"),
                        "doctype": "Purchase Order",
                        "is_query_report": True
                   },
            ]
        }
    ]
