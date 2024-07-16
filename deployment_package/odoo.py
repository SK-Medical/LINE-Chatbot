import xmlrpc.client
import json
from datetime import datetime
from typing import List, Dict, Any
from config import ODOO_CONFIG

def get_product_info_by_criteria(name: str = None, min_price: float = None, max_price: float = None, category: str = None, reference: str = None, in_stock: bool = None) -> str:
    """
    Retrieves product information based on the given criteria from an Odoo server.

    Args:
        name (str, optional): The name or partial name of the product.
        min_price (float, optional): The minimum price of the product.
        max_price (float, optional): The maximum price of the product.
        category (str, optional): The category of the product.
        reference (str, optional): The internal reference or code of the product.
        in_stock (bool, optional): Whether to search for products that are currently in stock.

    Returns:
        str: Formatted information about matching products or an error message.
    """
    url = ODOO_CONFIG["url"]
    db = ODOO_CONFIG["db"]
    username = ODOO_CONFIG["username"]
    password = ODOO_CONFIG["password"]

    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    try:
        version = common.version()
    except Exception as e:
        return f"Failed to connect to the Odoo server: {e}"

    uid = common.authenticate(db, username, password, {})
    if not uid:
        return "Authentication failed"

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    fields_of_interest = [
        'name', 'list_price', 'description', 'description_sale', 
        'description_purchase', 'categ_id', 'default_code', 'code', 
        'uom_id', 'qty_available', 'x_studio_char_field_80a_1hlhqpi25'
    ]

    domain = []
    if name:
        domain.append(['name', 'ilike', name])
    if min_price:
        domain.append(['list_price', '>=', min_price])
    if max_price:
        domain.append(['list_price', '<=', max_price])
    if category:
        domain.append(['categ_id', '=', category])
    if reference:
        domain.append(['default_code', '=', reference])
    if in_stock is not None:
        domain.append(['qty_available', '>', 0])

    try:
        products = models.execute_kw(db, uid, password, 'product.product', 'search_read', 
                                     [domain], {'fields': fields_of_interest, 'limit': 10})

        if not products:
            return "No products found with the given criteria."
        else:
            return json.dumps(products, indent=4)
    except Exception as e:
        return f"Failed to retrieve products: {e}"

def create_invoice(partner_id: int, delivery_address: str, product_ids: List[int], quantities: List[float]) -> str:
    """
    Creates an invoice in the Odoo system.

    Args:
        partner_id (int): The ID of the partner (customer).
        delivery_address (str): The delivery address for the invoice.
        product_ids (List[int]): A list of product IDs to be included in the invoice.
        quantities (List[float]): A list of quantities corresponding to each product ID in the invoice.

    Returns:
        str: A message indicating the result of the operation.
    """
    url = ODOO_CONFIG["url"]
    db = ODOO_CONFIG["db"]
    username = ODOO_CONFIG["username"]
    password = ODOO_CONFIG["password"]

    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    try:
        version = common.version()
    except Exception as e:
        return f"Failed to connect to the Odoo server: {e}"

    uid = common.authenticate(db, username, password, {})
    if not uid:
        return "Authentication failed"

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    try:
        invoice_lines = [(0, 0, {
            'product_id': product_id,
            'quantity': quantity,
            'price_unit': models.execute_kw(db, uid, password, 'product.product', 'read', [[product_id]], {'fields': ['list_price']})[0]['list_price']
        }) for product_id, quantity in zip(product_ids, quantities)]

        invoice_id = models.execute_kw(db, uid, password, 'account.move', 'create', [{
            'partner_id': partner_id,
            'invoice_date': datetime.today().strftime('%Y-%m-%d'),
            'type': 'out_invoice',
            'invoice_line_ids': invoice_lines
        }])

        return f"Invoice {invoice_id} created successfully."
    except Exception as e:
        return f"Failed to create invoice: {e}"
