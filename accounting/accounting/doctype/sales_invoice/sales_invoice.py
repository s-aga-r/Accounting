# Copyright (c) 2021, Sagar Sharma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from frappe.model.mapper import get_mapped_doc


class SalesInvoice(Document):
    def validate(self):
        if not self.validate_customer():
            frappe.throw("Select a valid Customer.")
        if getdate(self.posting_date) > getdate(self.payment_due_date):
            frappe.throw(
                "Posting Date should be earlier than Payment Due Date.")
        self.validate_items()
        if not self.validate_debit_to():
            frappe.throw("Debit To account should be of type Receivable.")
        if not self.validate_income_account():
            frappe.throw("Income Account parent should be of type Income.")

    def on_submit(self):
        items = self.validate_items()
        for item_name, item_qty in items.items():
            item = frappe.get_doc("Item", item_name)
            item.in_stock -= item_qty
            item.save()

    # Helper Method's
    def validate_customer(self):
        party = frappe.get_doc("Party", self.customer)
        return party.party_type == "Customer"

    def validate_debit_to(self):
        account = frappe.get_doc("Account", self.debit_to)
        return account.account_type == "Receivable"

    def validate_income_account(self):
        account = frappe.get_doc("Account", self.income_account)
        return account.root_type == "Income"

    def validate_items(self):
        items = self.get_filtered_items()
        for item_name, item_qty in items.items():
            item = frappe.get_doc("Item", item_name)
            if item.in_stock < item_qty:
                if item.in_stock == 0:
                    frappe.throw(
                        f"{item.item_name} ({item.name}) is out of stock.")
                else:
                    frappe.throw(
                        f"Only {item.in_stock} {item.item_name} ({item.name}) are in the stock."
                    )
        return items

    def get_filtered_items(self):
        items = {}
        for item in self.items:
            if item.item not in items:
                items[item.item] = item.qty
            else:
                items[item.item] += item.qty
        return items


@frappe.whitelist(allow_guest=False)
def generate_invoice(sales_order_name):
    s_inv = get_mapped_doc("Sales Order", sales_order_name,	{
        "Sales Order": {
            "doctype": "Sales Invoice",
            "field_no_map": ["naming_series"]
        },
    })
    s_inv.insert()
    s_inv.submit()

    return s_inv.name
