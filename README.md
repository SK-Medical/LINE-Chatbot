# LINE Chatbot for SK-Medical

This project is a LINE messaging chatbot designed for SK-Medical, a Thai medical distribution company. Customers can prompt the chatbot over the LINE messaging app to create or sign into an account, search for products, and place orders using natural language.

### Author

Ayden Lamparski - contact at ayden@lamparski.com
This project was created for my 2024 summer internship in Seoul, Korea at Undernamu consulting company.

## Table of Contents
1. [Architecture and Functionality Overview](#architecture-and-functionality-overview)
2. [Prerequisites](#prerequisites)
3. [Setup Instructions](#setup-instructions)
   - [Clone the Repository](#clone-the-repository)
   - [Environment Variables](#environment-variables)
   - [Installing Dependencies](#installing-dependencies)
   - [Deploying the Lambda Function](#deploying-the-lambda-function)
   - [Creating OpenAI Assistant](#creating-openai-assistant)
   - [Creating LINE Chatbot](#creating-line-chatbot)
   - [Setting Permissions](#setting-permissions)
4. [File Structure](#file-structure)
5. [Detailed File Descriptions](#detailed-file-descriptions)
6. [Logging and Error Handling](#logging-and-error-handling)
7. [Maintenance](#maintenance)
8. [Troubleshooting](#troubleshooting)

## Architecture and Functionality Overview
- **OpenAI Assistants:** Utilizes OpenAI's conversational AI to understand and respond to user queries, intelligently deciding to use function calls to connect to SK-Medical's Odoo database.
- **LINE API:** Uses LINE's messaging platform to interact with users, sending and receiving messages through the LINE app.
- **Odoo API:** Integrates with Odoo ERP via function tool calls to retrieve product information, retrieve account information, create accounts, and create invoices.
- **AWS Lambda:** Utilizes AWS Lambda to host the chatbot asynchronously, enabling automatic scaling to handle varying workloads. Integrates with an API endpoint to connect to the LINE API via a webhook.
- **AWS DynamoDB:** Employs a DynamoDB table to map LINE IDs to their respective conversational contexts, ensuring seamless and personalized user interactions by maintaining state across sessions.

## Prerequisites
- AWS CLI
- Python 3.x
- pip
- Git
- Access to AWS account
- Access to OpenAI API
- LINE Developers account
- Odoo account

## Setup Instructions

### Clone the Repository
```sh
git clone https://github.com/AydenLamp/Chatbot.git
cd LINE-Chatbot
```

### Environment Variables
The following environment variables must be set for the Lambda function in the AWS console:

- `ODOO_URL`: The URL for the Odoo ERP system.
- `ODOO_DB`: The database name for the Odoo ERP system.
- `ODOO_USERNAME`: The username for the Odoo ERP system.
- `ODOO_PASSWORD`: The password for the Odoo ERP system.
- `OPENAI_API_KEY`: The API key for accessing OpenAI.
- `OPENAI_ASSISTANT_ID`: The assistant ID for OpenAI.
- `AWS_REGION_NAME`: The AWS region name.
- `AWS_TABLE_NAME`: The DynamoDB table name.
- `LINE_CHANNEL_SECRET`: The secret key for the LINE channel.
- `LINE_CHANNEL_ACCESS_TOKEN`: The access token for the LINE channel.

### Installing Dependencies
```sh
pip install -r requirements.txt
```

### Deploying the Lambda Function
1. Enter the virtual environment and navigate to the deployment package directory:
```sh
source venv/bin/activate
cd deployment_package
```

2. Zip the contents:
```sh
zip -r ../deployment_package.zip .
```

3. The resultant `deployment_package.zip` file should be uploaded to the Lambda function through the AWS Lambda console.

### Creating OpenAI Assistant
1. Create an OpenAI assistant using GPT-4.
2. Enter the instructions from `assistant_instructions.txt`.
3. Enter the function tool call descriptions from the JSON files in the `Function_descriptions_for_assistant` directory.

### Creating LINE Chatbot
1. Create a LINE chatbot with the initial message found in `config.py`.
2. Set the webhook URL to connect to an AWS API Gateway that triggers the Lambda function.

### Setting Permissions
1. Ensure the Lambda function has permission to access the AWS DynamoDB table.
2. Ensure the Lambda function has permission to log to CloudWatch.
3. Ensure the Lambda function has permission to access the API Gateway.
4. Ensure the Odoo account has the appropriate permissions to perform necessary actions like retrieving product information and creating invoices.

## File Structure

```
├── requirements.txt
├── venv/
├── assistant_instructions.txt
├── Function_descriptions_for_assistant/
│   ├── create_invoice_descrption.json
│   ├── create_partner_description.json
│   ├── get_partner_info_by_criteria_description.json
│   ├── get_product_info_by_criteria_description.json
├── deployment_package.zip
├── deployment_package/
│   ├── config.py
│   ├── lambda_function.py
│   ├── assistant.py
│   ├── database.py
│   ├── odoo.py
│   ├── utils.py
```

## Detailed File Descriptions

### config.py
Manages the configuration settings and environment variables for the project, defining necessary configurations for OpenAI, AWS, and LINE. It also holds the initial LINE message.

### lambda_function.py
Contains the main AWS Lambda handler that processes incoming LINE messages, verifies signatures, and sends responses. It coordinates the flow between receiving a message and sending a reply.

### assistant.py
Interfaces with the OpenAI API to create threads, manage runs, and retrieve messages. Contains functions to initiate and manage interactions with the OpenAI assistant.

### database.py
Manages interactions with AWS DynamoDB to store and retrieve thread IDs associated with LINE user IDs. Ensures initial messages sent automatically by LINE are contained in the conversational context.

### odoo.py
Integrates with the Odoo ERP system to interact with its XML-RPC API. Contains functions to retrieve product information based on specified criteria, create invoices, retrieve partner (account) information, and create new partners in the Odoo database.

### utils.py
Provides utility functions, including `make_request` for handling HTTP requests and responses, and `log_message` for facilitating logging at different levels (info, error, etc.).

### assistant_instructions.txt
Contains the instructions provided to the OpenAI assistant to guide the chatbot's behavior and interactions with the Odoo ERP system.

### Function_descriptions_for_assistant
A directory containing JSON files with detailed descriptions of the function tool calls used in the system. Each function's description is provided in a separate JSON file.

### deployment_package.zip
The zip file that contains all necessary files and dependencies to be uploaded to AWS Lambda.

## Logging and Error Handling
The project uses a logging mechanism to capture and store log messages at various levels (info, error, etc.), ensuring that errors can be tracked and debugged efficiently. These logs can be viewed on AWS CloudWatch.

## Maintenance
- Ensure the OpenAI account remains funded to avoid run failures. If the account is not funded, the chatbot will likely respond with "Sorry, something went wrong," and the logs will show a failed run.
- Monitor the system to ensure it is functioning as expected. This can be done through:
  - LINE Developers Console: Check the status and interactions of the chatbot.
  - OpenAI Console: Monitor API usage and performance.
  - AWS CloudWatch: View logs for detailed information on the Lambda function's performance and any errors that occur.

## Troubleshooting
Logs will usually contain detailed error descriptions, and an OpenAI run failure may be the result of the account running out of funding. Check the logs in AWS CloudWatch for specific error messages to help diagnose issues.
