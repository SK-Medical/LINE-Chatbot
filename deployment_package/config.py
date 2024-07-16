import os
import logging

# Set up logging for configuration related operations
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Helper function to read environment variables with optional defaults and required checks
def get_env_var(name, default=None, required=True):
    value = os.getenv(name, default)
    if required and value is None:
        logger.error(f"Required environment variable '{name}' is not set.")
        raise EnvironmentError(f"Required environment variable '{name}' is not set")
    return value

# Group related configuration variables into dictionaries
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
