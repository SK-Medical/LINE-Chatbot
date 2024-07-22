import os
from typing import Optional
from utils import log_message

def get_env_var(name: str, default: Optional[str] = None, required: bool = True) -> str:
    """
    Read environment variables with optional defaults and required checks.

    Args:
        name (str): The name of the environment variable.
        default (Optional[str]): The default value if the variable is not set.
        required (bool): Whether the variable is required.

    Returns:
        str: The value of the environment variable.

    Raises:
        EnvironmentError: If a required variable is not set.
    """
    value = os.getenv(name, default)
    if required and value is None:
        log_message('error', f"Required environment variable '{name}' is not set.")
        raise EnvironmentError(f"Required environment variable '{name}' is not set")
    log_message('info', f"Environment variable '{name}' is set to '{value}'")
    return value

# Define the initial message for new conversations
INITIAL_MESSAGE = '''
    สวัสดีค่ะ! ฉันคือแชทบอทของบริษัท SK-Medical คุณสามารถพูดคุยกับฉันได้เหมือนคุยกับคนจริงๆ เลยค่ะ ฉันสามารถช่วยคุณสร้างบัญชีใหม่หรือค้นหาบัญชีที่มีอยู่ ค้นหาผลิตภัณฑ์ตามชื่อ ราคา และความพร้อมในการจัดส่ง และช่วยเปรียบเทียบตัวเลือก เมื่อคุณตัดสินใจสั่งซื้อ ฉันสามารถสร้างใบสั่งซื้อให้คุณได้

    คุณเคยสั่งซื้อสินค้ากับเรามาก่อนไหม? ถ้าเคย คุณสามารถใช้บัญชีเดิมได้ ถ้าไม่ คุณจะต้องสร้างบัญชีใหม่ โปรดบอกว่าคุณต้องการใช้บัญชีเดิมหรือสร้างบัญชีใหม่
    If you would like to speak to me in English, simply ask me.
'''
ODOO_CONFIG = {
    'url': get_env_var('ODOO_URL'),
    'db': get_env_var('ODOO_DB'),
    'username': get_env_var('ODOO_USERNAME'),
    'password': get_env_var('ODOO_PASSWORD')
}

OPENAI_CONFIG = {
    'api_key': get_env_var('OPENAI_API_KEY'),
    'assistant_id': get_env_var('OPENAI_ASSISTANT_ID')
}

AWS_CONFIG = {
    'region_name': get_env_var('AWS_REGION_NAME'),
    'table_name': get_env_var('AWS_TABLE_NAME')
}

LINE_CONFIG = {
    'channel_secret': get_env_var('LINE_CHANNEL_SECRET'),
    'access_token': get_env_var('LINE_CHANNEL_ACCESS_TOKEN')
}
