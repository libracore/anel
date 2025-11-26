# -*- coding: utf-8 -*- 
# Copyright (c) 2025, libracore (https://www.libracore.com) and contributors 
# For license information, please see license.txt

import frappe
from frappe.utils.background_jobs import enqueue
import json
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

@frappe.whitelist()
def async_create_invoices(sales_orders):
    kwargs={
      'sales_orders': sales_orders
    }
    
    enqueue("anel.anel.utils.create_invoices",
        queue='long',
        timeout=15000,
        **kwargs)
    return
    
@frappe.whitelist()
def create_invoices(sales_orders):
    if type(sales_orders) == str:
        sales_orders = json.loads(sales_orders)
    
    for sales_order in sales_orders:
        si = make_sales_invoice(sales_order, ignore_permissions=True)
        si.insert(ignore_mandatory=True, ignore_permissions=True)
        frappe.db.commit()
        
    return
