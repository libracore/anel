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
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 100},
        {"label": _("Customer name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 100},
        {"label": _("Parent Territory"), "fieldname": "parent_territory", "fieldtype": "Link", "options": "Territory", "width": 100},
        {"label": _("Territory"), "fieldname": "territory", "fieldtype": "Link", "options": "Territory", "width": 100},
        {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": _("Item name"), "fieldname": "item_name", "fieldtype": "Data", "width": 150},
        {"label": _("Key"), "fieldname": "key", "fieldtype": "Data", "width": 100},
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
        {"label": _(""), "fieldname": "blank", "fieldtype": "Data", "width": 20}
    ]

def get_data(filters):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
   
    # prepare query
    sql_query = """SELECT 
        `tabCustomer`.`name` AS `customer`,
        `tabCustomer`.`customer_name` AS `customer_name`,
        `tabCustomer`.`parent_territory` AS `parent_territory`,
        `tabCustomer`.`territory` AS `territory`,
        `items`.`item_code` AS `item_code`,
        `tabItem`.`item_name` AS `item_name`,
        `items`.`key` AS `key`,
        `data_P2`.`stock_uom` AS `uom`,
        `data_P1`.`qty` AS `qty_p1`,
        `data_P2`.`qty` AS `qty_p2`,
        (`data_P1`.`qty` / ABS((DATEDIFF("{p1_from}", "{p1_to}")) / 30)) AS `qty_p1_mt`,
        (`data_P2`.`qty` / ABS((DATEDIFF("{p2_from}", "{p2_to}")) / 30)) AS `qty_p2_mt`,
        (100 * `data_P1`.`qty`) / (`data_P2`.`qty`) AS `change`,
        `data_P2`.`rate` AS `rate`,
        `tabCustomer`.`default_currency` AS `currency`,
        `data_P1`.`volume` AS `volume_p1`,
        `data_P2`.`volume` AS `volume_p2`,
        `data_P1`.`volume` - `data_P2`.`volume` AS `volume_diff`,
        `data_P1`.`last_order` AS `last_order`,
        DATEDIFF( DATE(NOW()), `data_P1`.`last_order`) AS `days_since`,
        "" AS `:Data:20`
    FROM 
    (
        /*SELECT 
            `items`.`customer`,
            `items`.`item_code`,
            `items`.`key`,
            IFNULL((SELECT SUM(`tiP1`.`stock_qty`)
                FROM `tabSales Order Item` AS `tiP1`
                LEFT JOIN `tabSales Order` AS `tP1` ON `tP1`.`name` = `tiP1`.`parent`
                WHERE 
                    `tP1`.`docstatus` = 1
                    AND `tP1`.`customer` = `items`.`customer`
                    AND `tiP1`.`item_code` = `items`.`item_code`
                    AND `tP1`.`transaction_date` >= "{p1_from}"
                    AND `tP1`.`transaction_date` <= "{p1_to}"
                ), 0) AS `qty`,
            IFNULL((SELECT SUM(`tiP1`.`stock_qty`)
                FROM `tabSales Order Item` AS `tiP1`
                LEFT JOIN `tabSales Order` AS `tP1` ON `tP1`.`name` = `tiP1`.`parent`
                WHERE 
                    `tP1`.`docstatus` = 1
                    AND `tP1`.`customer` = `items`.`customer`
                    AND `tiP1`.`item_code` = `items`.`item_code`
                    AND `tP1`.`transaction_date` >= "{p1_from}"
                    AND `tP1`.`transaction_date` <= "{p1_to}"
                ), 0) AS `qty`
        FROM
        ( */
            SELECT 
                `tabSales Order`.`customer`,
                `tabSales Order Item`.`item_code`,
                CONCAT(`tabSales Order`.`customer`, "::", `tabSales Order Item`.`item_code`) AS `key`
            FROM `tabSales Order Item`
            LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabSales Order Item`.`parent`
            WHERE 
                `tabSales Order`.`docstatus` = 1
                AND `tabSales Order`.`transaction_date` >= DATE_SUB(NOW(), INTERVAL 180 DAY)
            GROUP BY `key`
        ) AS `items`
    /* ) AS `data_P1` */
    LEFT JOIN `tabCustomer` ON `tabCustomer`.`name` = `items`.`customer`
    LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `items`.`item_code`
    LEFT JOIN 
        (SELECT 
            CONCAT(`tP1`.`customer`, "::", `tiP1`.`item_code`) AS `key`,
            SUM(`tiP1`.`stock_qty`) AS `qty`,
            AVG(`tiP1`.`rate`) AS `rate`,
            MAX(`tP1`.`transaction_date`) AS `last_order`,
            SUM(`tiP1`.`amount`) AS `volume`,
            `tiP1`.`stock_uom` AS `stock_uom`,
            `tiP1`.`item_name` AS `item_name`
         FROM `tabSales Order Item` AS `tiP1`
         LEFT JOIN `tabSales Order` AS `tP1` ON `tP1`.`name` = `tiP1`.`parent`
         WHERE 
            `tP1`.`docstatus` = 1
            AND `tP1`.`transaction_date` >= "{p1_from}"
            AND `tP1`.`transaction_date` <= "{p1_to}"
         GROUP BY `key`
        ) AS `data_P1` ON `data_P1`.`key` = `data_P1`.`key`
    LEFT JOIN 
        (SELECT 
            CONCAT(`tP2`.`customer`, "::", `tiP2`.`item_code`) AS `key`,
            SUM(`tiP2`.`stock_qty`) AS `qty`,
            AVG(`tiP2`.`rate`) AS `rate`,
            MAX(`tP2`.`transaction_date`) AS `last_order`,
            SUM(`tiP2`.`amount`) AS `volume`,
            `tiP2`.`stock_uom` AS `stock_uom`,
            `tiP2`.`item_name` AS `item_name`
         FROM `tabSales Order Item` AS `tiP2`
         LEFT JOIN `tabSales Order` AS `tP2` ON `tP2`.`name` = `tiP2`.`parent`
         WHERE 
            `tP2`.`docstatus` = 1
            AND `tP2`.`transaction_date` >= "{p2_from}"
            AND `tP2`.`transaction_date` <= "{p2_to}"
         GROUP BY `key`
        ) AS `data_P2` ON `data_P2`.`key` = `data_P1`.`key`
      ;
      """.format(
        p1_from=filters['p1_from_date'], 
        p1_to=filters['p1_to_date'],
        p2_from=filters['p2_from_date'],
        p2_to=filters['p2_to_date']
    )
    
    data = frappe.db.sql(sql_query, as_dict=1)

    return data
