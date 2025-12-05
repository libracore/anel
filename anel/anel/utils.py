# -*- coding: utf-8 -*-
# Copyright (c) 2025, libracore AG and contributors
# For license information, please see license.txt

from erpnextswiss.scripts.esr_qr_tools import get_esr_raw_from_document_name, add_check_digit_to_esr_reference

def sales_invoice_before_save(doc, event):
    reference_raw = get_esr_raw_from_document_name(doc.name)
    reference = add_check_digit_to_esr_reference(reference_raw, True)
    doc.esr_reference = reference
    return

"""
Add missing esr references patch
Run as 
    $ bench execute anel.anel.utils.add_missing_esr_references
"""
def add_missing_esr_references():
    missing_esrs = frappe.db.sql("""
        SELECT `name`
        FROM `tabSales Invoice`
        WHERE `docstatus` = 1
          AND `esr_reference` IS NULL;
        """,
        as_dict=True)

    for sinv in missing_esrs:
        reference_raw = get_esr_raw_from_document_name(sinv['name'])
        reference = add_check_digit_to_esr_reference(reference_raw, True)
        print("Updating {0} to {1}".format(sinv['name'], reference))
        frappe.db.sql("""
            UPDATE `tabSales Invoice`
            SET `esr_reference` = %(ref)s
            WHERE `name` = %(name)s;""",
            {
                'ref': reference,
                'name': sinv['name']
            }
        )
        frappe.db.commit()
    
    return