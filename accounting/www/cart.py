import frappe


def get_context(context):
    user = frappe.session.user

    if user == "Guest":
        frappe.local.flags.redirect_location = "/login"

    if frappe.db.exists("Cart", user):
        cart = frappe.get_doc("Cart", user)

        items = []
        total_amount = 0

        for item in cart.items:
            item_properties = frappe.get_doc("Item", item.item)
            amount = item.rate * item.qty  # Need to Implement in DocType
            items.append(
                {
                    "name": item_properties.item_name,
                    "rate": item.rate,
                    "qty": item.qty,
                    "amount": amount,
                }
            )
            total_amount += amount

            context.items = items
            context.total_amount = total_amount

    return context
