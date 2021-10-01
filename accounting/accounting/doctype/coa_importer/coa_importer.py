# Copyright (c) 2021, Sagar Sharma and contributors
# For license information, please see license.txt

import json
import frappe
from pathlib import Path
from frappe.model.document import Document
from accounting.accounting.doctype.account.account import Account


class COAImporter(Document):
    @staticmethod
    def create_chart(data):
        account_attributes = ["root_type",
                              "account_type", "account_number", "tax_rate"]

        def create_coa(children, parent, root_type):
            for account_name, child in children.items():
                if isinstance(child, dict):
                    root_type = child.get("root_type", root_type)
                    account_number = child.get("account_number", None)
                    balance = child.get("balance", 0.0)
                    account_type = child.get("account_type", None)
                    is_group = 0
                    if len(set(child.keys() - set(account_attributes))):
                        is_group = 1
                    Account.create(account_name, root_type, account_number,
                                   balance, parent, account_type, is_group)
                    create_coa(child, account_name, root_type)
        create_coa(data, None, None)


@frappe.whitelist()
def import_coa(file_url):
    file_doc = frappe.get_doc("File", {"file_url": file_url})

    name, extension = file_doc.get_extension()

    if extension != ".json":
        frappe.throw("Upload a JSON file.")

    json_str = Path(file_doc.get_full_path()).read_text()
    data = json.loads(json_str)

    COAImporter.create_chart(data)

    return "Imported successfully!"
