import xmlrpc.client
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import ODOO_CONFIG
from utils import connect_and_authenticate, log_message

def get_tool_output(tool_name: str, parameters: Dict[str, Any]) -> str:
    """
    Executes the tool and returns its output, with logging.

    Args:
        tool_name (str): The name of the tool.
        parameters (Dict[str, Any]): The parameters to be used by the tool.

    Returns:
        str: The output from the tool.
    """
    try:
        if tool_name == "get_product_info_by_criteria":
            name = parameters.get("name")
            min_price = parameters.get("min_price")
            max_price = parameters.get("max_price")
            product_id = parameters.get("product_id")
            in_stock = parameters.get("in_stock")
            result = get_product_info_by_criteria(name, min_price, max_price, product_id, in_stock)
        elif tool_name == "create_invoice":
            partner_id = parameters.get("partner_id")
            product_ids = parameters.get("product_ids")
            quantities = parameters.get("quantities")
            if partner_id is None or product_ids is None or quantities is None:
                result = "Missing required parameters for create_invoice."
            else:
                result = create_invoice(partner_id, product_ids, quantities)
        elif tool_name == "get_partner_info_by_criteria":
            partner_id = parameters.get("partner_id")
            name = parameters.get("name")
            email = parameters.get("email")
            phone = parameters.get("phone")
            result = get_partner_info_by_criteria(partner_id, name, email, phone)
        elif tool_name == "create_partner":
            name = parameters.get("name")
            street = parameters.get("street")
            city = parameters.get("city")
            email = parameters.get("email")
            phone = parameters.get("phone")
            zip = parameters.get("zip")
            if name is None or street is None or city is None or email is None:
                result = "Missing required parameters for create_partner."
            else:
                result = create_partner(name, street, city, email, phone, zip)
        else:
            result = f"Unknown tool: {tool_name}"

        # Log the tool call, parameters, and result
        log_message('info', f"Tool call: {tool_name}, Parameters: {json.dumps(parameters)}, Result: {result}")

        return result
    except Exception as e:
        error_message = f"Error, please make sure you made the correct tool call: {str(e)}"
        log_message('error', f"Tool call: {tool_name}, Parameters: {json.dumps(parameters)}, Error: {error_message}")
        return error_message

def get_product_info_by_criteria(
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    product_id: Optional[str] = None,
    in_stock: Optional[bool] = None
) -> str:
    """
    Retrieves product information based on the given criteria from an Odoo server.

    Args:
        name (Optional[str]): The name or partial name of the product.
        min_price (Optional[float]): The minimum price of the product.
        max_price (Optional[float]): The maximum price of the product.
        reference (Optional[str]): The internal reference or code of the product.
        in_stock (Optional[bool]): Whether to search for products that are currently in stock.

    Returns:
        str: Formatted information about matching products or an error message.
    """
    models, uid, error = connect_and_authenticate()
    if error:
        return error

    fields_of_interest = [
        'id', 'name', 'list_price', 'description', 'description_sale',
        'description_purchase', 'qty_available'
    ]

    domain = []
    if name:
        domain.append(['name', 'ilike', name])
    if min_price:
        domain.append(['list_price', '>=', min_price])
    if max_price:
        domain.append(['list_price', '<=', max_price])
    if product_id:
        domain.append(['id', '=', product_id])
    if in_stock is not None:
        domain.append(['qty_available', '>', 0])

    try:
        products = models.execute_kw(
            ODOO_CONFIG['db'], uid, ODOO_CONFIG['password'],
            'product.product', 'search_read',
            [domain], {'fields': fields_of_interest, 'limit': 20}
        )

        if not products:
            return "No products found with the given criteria."
        else:
            return json.dumps(products, indent=4)
    except Exception as e:
        return f"Failed to retrieve products: {e}"

def get_partner_info_by_criteria(
    partner_id: Optional[int] = None,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
) -> str:
    """
    Retrieves partner (contact) information based on the given criteria from an Odoo server.

    Args:
        partner_id (Optional[int]): The ID of the partner.
        name (Optional[str]): The name or partial name of the partner.
        email (Optional[str]): The email address of the partner.
        phone (Optional[str]): The phone number of the partner.

    Returns:
        str: Formatted information about matching partners or an error message.
    """
    models, uid, error = connect_and_authenticate()
    if error:
        return error

    fields_of_interest = [
        'name', 'email', 'phone', 'is_company', 'street', 'city', 'state_id', 'country_id'
    ]

    domain = []
    if partner_id is not None:
        domain.append(['id', '=', partner_id])
    if name:
        domain.append(['name', 'ilike', name])
    if email:
        domain.append(['email', 'ilike', email])
    if phone:
        domain.append(['phone', 'ilike', phone])

    try:
        partners = models.execute_kw(
            ODOO_CONFIG['db'], uid, ODOO_CONFIG['password'],
            'res.partner', 'search_read',
            [domain], {'fields': fields_of_interest, 'limit': 20}
        )

        if not partners:
            return "No partners found with the given criteria."
        else:
            return json.dumps(partners, indent=4)
    except Exception as e:
        return f"Failed to retrieve partners: {e}"

def create_invoice(partner_id: int, product_ids: List[int], quantities: List[float]) -> str:
    """
    Creates an invoice in the Odoo system and returns the created invoice information.

    Args:
        partner_id (int): The ID of the partner (customer).
        product_ids (List[int]): A list of product IDs to be included in the invoice.
        quantities (List[float]): A list of quantities corresponding to each product ID in the invoice.

    Returns:
        str: Formatted information about the created invoice or an error message.
    """
    models, uid, error = connect_and_authenticate()
    if error:
        return error

    try:
        invoice_lines = [(0, 0, {
            'product_id': product_id,
            'quantity': quantity,
            'price_unit': models.execute_kw(
                ODOO_CONFIG['db'], uid, ODOO_CONFIG['password'],
                'product.product', 'read',
                [[product_id]], {'fields': ['list_price']}
            )[0]['list_price']
        }) for product_id, quantity in zip(product_ids, quantities)]

        invoice_id = models.execute_kw(
            ODOO_CONFIG['db'], uid, ODOO_CONFIG['password'],
            'account.move', 'create', [{
                'partner_id': partner_id,
                'invoice_date': datetime.today().strftime('%Y-%m-%d'),
                'move_type': 'out_invoice',  # Specify the type of invoice
                'invoice_line_ids': invoice_lines,
                'invoice_origin': 'Created by chatbot'
            }]
        )

        invoice_info = models.execute_kw(
            ODOO_CONFIG['db'], uid, ODOO_CONFIG['password'],
            'account.move', 'read', [[invoice_id]], {'fields': ['id', 'name', 'partner_id', 'invoice_line_ids']}
        )

        return json.dumps(invoice_info, indent=4)
    except Exception as e:
        return f"Failed to create invoice: {e}"

def create_partner(
    name: str,
    street: str,
    city: str,
    email: str,
    phone: Optional[str] = None,
    zip: Optional[str] = None
) -> str:
    """
    Creates a partner in the Odoo database.

    Args:
        name (str): The name of the partner.
        street (str): The street address of the partner.
        city (str): The city of the partner.
        email (str): The email address of the partner.
        phone (Optional[str]): The phone number of the partner.
        zip (Optional[str]): The zip code of the partner.

    Returns:
        str: A message indicating the result of the operation, including the partner details.
    """
    models, uid, error = connect_and_authenticate()
    if error:
        return error

    comment = f"Created by the chatbot on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    partner_data: Dict[str, Any] = {
        'name': name,
        'street': street,
        'city': city,
        'email': email,
        'comment': comment
    }

    if phone:
        partner_data['phone'] = phone
    if zip:
        partner_data['zip'] = zip

    try:
        partner_id = models.execute_kw(
            ODOO_CONFIG['db'], uid, ODOO_CONFIG['password'],
            'res.partner', 'create', [partner_data]
        )

        partner_info = models.execute_kw(
            ODOO_CONFIG['db'], uid, ODOO_CONFIG['password'],
            'res.partner', 'read', [[partner_id]], {'fields': ['id', 'name']}
        )

        return json.dumps(partner_info, indent=4)
    except Exception as e:
        return f"Failed to create partner: {e}"
