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
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 150},
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
        `items`.`supplier` AS `supplier`,
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
            `tabItem Supplier`.`supplier` AS `supplier`,
            `tabSupplier`.`default_currency` AS `currency`
        FROM `tabPurchase Order Item`
        LEFT JOIN `tabPurchase Order` ON `tabPurchase Order`.`name` = `tabPurchase Order Item`.`parent`
        LEFT JOIN `tabItem Supplier` ON (
            `tabItem Supplier`.`parent` = `tabPurchase Order Item`.`item_code`
            AND `tabItem Supplier`.`idx` = 1)
        LEFT JOIN `tabSupplier` ON `tabSupplier`.`name` = `tabItem Supplier`.`supplier`
        WHERE 
            `tabPurchase Order`.`docstatus` = 1
            AND `tabPurchase Order`.`transaction_date` >= DATE_SUB(NOW(), INTERVAL 180 DAY)
            AND `tabItem Supplier`.`supplier` IS NOT NULL
        GROUP BY `tabItem Supplier`.`supplier`
    ) AS `items`
    LEFT JOIN 
        (SELECT 
            `tSI1`.`supplier` AS `supplier`,
            SUM(`tiP1`.`stock_qty`) AS `qty`,
            AVG(`tiP1`.`base_rate`) AS `rate`,
            MAX(`tP1`.`transaction_date`) AS `last_order`,
            SUM(`tiP1`.`base_amount`) AS `volume`,
            `tiP1`.`stock_uom` AS `stock_uom`
         FROM `tabPurchase Order Item` AS `tiP1`
         LEFT JOIN `tabPurchase Order` AS `tP1` ON `tP1`.`name` = `tiP1`.`parent`
         LEFT JOIN `tabItem Supplier` AS `tSI1` ON (
            `tSI1`.`parent` = `tiP1`.`item_code`
            AND `tSI1`.`idx` = 1)
         WHERE 
            `tP1`.`docstatus` = 1
            AND `tP1`.`transaction_date` >= "{p1_from}"
            AND `tP1`.`transaction_date` <= "{p1_to}"
         GROUP BY `tSI1`.`supplier`
        ) AS `data_P1` ON `data_P1`.`supplier` = `items`.`supplier`
    LEFT JOIN 
        (SELECT 
            `tSI2`.`supplier` AS `supplier`,
            SUM(`tiP2`.`stock_qty`) AS `qty`,
            AVG(`tiP2`.`base_rate`) AS `rate`,
            MAX(`tP2`.`transaction_date`) AS `last_order`,
            SUM(`tiP2`.`base_amount`) AS `volume`,
            `tiP2`.`stock_uom` AS `stock_uom`
         FROM `tabPurchase Order Item` AS `tiP2`
         LEFT JOIN `tabPurchase Order` AS `tP2` ON `tP2`.`name` = `tiP2`.`parent`
         LEFT JOIN `tabItem Supplier` AS `tSI2` ON (
            `tSI2`.`parent` = `tiP2`.`item_code`
            AND `tSI2`.`idx` = 1)
         WHERE 
            `tP2`.`docstatus` = 1
            AND `tP2`.`transaction_date` >= "{p2_from}"
            AND `tP2`.`transaction_date` <= "{p2_to}"
         GROUP BY `tSI2`.`supplier`
        ) AS `data_P2` ON `data_P2`.`supplier` = `items`.`supplier`
      ;
      """.format(
        p1_from=filters['p1_from_date'], 
        p1_to=filters['p1_to_date'],
        p2_from=filters['p2_from_date'],
        p2_to=filters['p2_to_date']
    )
    
    data = frappe.db.sql(sql_query, as_dict=1)

    return data
