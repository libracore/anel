# Copyright (c) 2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Parent Territory"), "fieldname": "parent_territory", "fieldtype": "Link", "options": "Territory", "width": 100},
        {"label": _("Territory"), "fieldname": "territory", "fieldtype": "Link", "options": "Territory", "width": 100},
        {"label": _("UOM"), "fieldname": "uom", "fieldtype": "Link", "options": "UOM", "width": 50},
        {"label": _("Menge P1"), "fieldname": "qty_p1", "fieldtype": "Float", "width": 100},
        {"label": _("Menge P2"), "fieldname": "qty_p2", "fieldtype": "Float", "width": 100},
        {"label": _("P1 pro Mt"), "fieldname": "qty_p1_mt", "fieldtype": "Float", "width": 100},
        {"label": _("P2 pro Mt"), "fieldname": "qty_p2_mt", "fieldtype": "Float", "width": 100},
        {"label": _("Änderung"), "fieldname": "change", "fieldtype": "Percent", "width": 100},
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("Currency"), "fieldname": "currency", "fieldtype": "Link", "options": "Currency", "width": 80},
        {"label": _("Volume P1"), "fieldname": "volume_p1", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("Volume P2"), "fieldname": "volume_p2", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("Volume Diff"), "fieldname": "volume_diff", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("Last order (P1)"), "fieldname": "last_order", "fieldtype": "Date",  "width": 100},
        {"label": _("Days since (P1)"), "fieldname": "days_since", "fieldtype": "Int", "width": 80},
        {"label": "", "fieldname": "blank", "fieldtype": "Data", "width": 20}
    ]

def get_data(filters):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
   
    # prepare query
    sql_query = """SELECT 
        `items`.`parent_territory` AS `parent_territory`,
        `items`.`territory` AS `territory`,
        `data_P2`.`stock_uom` AS `uom`,
        `data_P1`.`qty` AS `qty_p1`,
        `data_P2`.`qty` AS `qty_p2`,
        (`data_P1`.`qty` / ABS((DATEDIFF("{p1_from}", "{p1_to}")) / 30)) AS `qty_p1_mt`,
        (`data_P2`.`qty` / ABS((DATEDIFF("{p2_from}", "{p2_to}")) / 30)) AS `qty_p2_mt`,
        (100 * `data_P1`.`qty`) / (`data_P2`.`qty`) AS `change`,
        `data_P2`.`rate` AS `rate`,
        `items`.`currency` AS `currency`,
        `data_P1`.`volume` AS `volume_p1`,
        `data_P2`.`volume` AS `volume_p2`,
        `data_P1`.`volume` - `data_P2`.`volume` AS `volume_diff`,
        `data_P1`.`last_order` AS `last_order`,
        DATEDIFF( DATE(NOW()), `data_P1`.`last_order`) AS `days_since`,
        "" AS `:Data:20`
    FROM 
    (
        SELECT 
            `tabSales Order Item`.`item_code`,
            `tabCustomer`.`name` AS `customer`,
            `tabCustomer`.`customer_name` AS `customer_name`,
            `tabCustomer`.`parent_territory` AS `parent_territory`,
            `tabCustomer`.`territory` AS `territory`,
            `tabCustomer`.`default_currency` AS `currency`
        FROM `tabSales Order Item`
        LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabSales Order Item`.`parent`
        LEFT JOIN `tabCustomer` ON `tabCustomer`.`name` = `tabSales Order`.`customer`
        WHERE 
            `tabSales Order`.`docstatus` = 1
            AND `tabSales Order`.`transaction_date` >= DATE_SUB(NOW(), INTERVAL 7300 DAY)
        GROUP BY `tabCustomer`.`territory`
    ) AS `items`
    LEFT JOIN 
        (SELECT 
            `tC1`.`territory` AS `territory`,
            SUM(`tiP1`.`stock_qty`) AS `qty`,
            AVG(`tiP1`.`rate`) AS `rate`,
            MAX(`tP1`.`transaction_date`) AS `last_order`,
            SUM(`tiP1`.`amount`) AS `volume`,
            `tiP1`.`stock_uom` AS `stock_uom`,
            `tiP1`.`item_name` AS `item_name`
         FROM `tabSales Order Item` AS `tiP1`
         LEFT JOIN `tabSales Order` AS `tP1` ON `tP1`.`name` = `tiP1`.`parent`
         LEFT JOIN `tabCustomer` AS `tC1` ON `tC1`.`name` = `tP1`.`customer`
         WHERE 
            `tP1`.`docstatus` = 1
            AND `tP1`.`transaction_date` >= "{p1_from}"
            AND `tP1`.`transaction_date` <= "{p1_to}"
         GROUP BY `tC1`.`territory`
        ) AS `data_P1` ON `items`.`territory` = `data_P1`.`territory`
    LEFT JOIN 
        (SELECT 
            `tC2`.`territory` AS `territory`,
            SUM(`tiP2`.`stock_qty`) AS `qty`,
            AVG(`tiP2`.`rate`) AS `rate`,
            MAX(`tP2`.`transaction_date`) AS `last_order`,
            SUM(`tiP2`.`amount`) AS `volume`,
            `tiP2`.`stock_uom` AS `stock_uom`,
            `tiP2`.`item_name` AS `item_name`
         FROM `tabSales Order Item` AS `tiP2`
         LEFT JOIN `tabSales Order` AS `tP2` ON `tP2`.`name` = `tiP2`.`parent`
         LEFT JOIN `tabCustomer` AS `tC2` ON `tC2`.`name` = `tP2`.`customer`
         WHERE 
            `tP2`.`docstatus` = 1
            AND `tP2`.`transaction_date` >= "{p2_from}"
            AND `tP2`.`transaction_date` <= "{p2_to}"
         GROUP BY `tC2`.`territory`
        ) AS `data_P2` ON `items`.`territory` = `data_P2`.`territory`
      ;
      """.format(
        p1_from=filters['p1_from_date'], 
        p1_to=filters['p1_to_date'],
        p2_from=filters['p2_from_date'],
        p2_to=filters['p2_to_date']
    )
    
    data = frappe.db.sql(sql_query, as_dict=1)

    return data
