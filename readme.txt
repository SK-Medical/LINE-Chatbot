# LINE Chatbot Integration with OpenAI for SK-Medical

This project is a chatbot designed for SK-Medical, a Thai medical distribution company.
Customers can prompt the chatbot over the LINE messaging app to search for products and place orders using natural language, making the interaction intuitive and user-friendly.

## Description

The chatbot leverages the following technologies:
- **OpenAI Assistants:** Utilizes OpenAI's conversational AI to understand and respond to user queries, providing intelligent and context-aware interactions.
- **LINE API:** Uses LINE's messaging platform to interact with users, sending and receiving messages through the LINE app.
- **Odoo API:** Integrates with Odoo ERP to retrieve product information and create invoices.

Customers can prompt the chatbot over the LINE messaging app to search for products and place orders using natural language, making the interaction intuitive and user-friendly.

### Author

This project was created by Ayden Lamparski during my Summer 2024 internship in Korea at Undernamu Consulting Company.

## File Structure

\`\`\`
.
├── requirements.txt
├── venv/
├── functions.json
├── deployment_package.zip
├── deployment_package/
│ ├── config.py
│ ├── lambda_function.py
│ ├── assistant.py
│ ├── database.py
│ ├── odoo.py
│ ├── utils.py

\`\`\`

### Description of .py Files

- **config.py:**
  Handles the configuration settings and environment variables for the project. Defines necessary configurations for OpenAI, AWS, and LINE.

- **lambda_function.py:**
  Contains the main AWS Lambda handler that processes incoming LINE messages, verifies signatures, and sends responses. It coordinates the flow between receiving a message and sending a reply.

- **assistant.py:**
  Interfaces with the OpenAI API to create threads, manage runs, and retrieve messages. Contains functions to initiate and manage interactions with the OpenAI assistant.

- **database.py:**
  Manages interactions with AWS DynamoDB to store and retrieve thread IDs associated with LINE user IDs. Ensures initial messages are sent to new users.

- **odoo.py:**
  Integrates with Odoo ERP system to retrieve product information and create invoices. Contains functions to interact with Odoo's XML-RPC API.

- **utils.py:**
  Provides utility functions, including `make_request`, to handle HTTP requests and process responses.
