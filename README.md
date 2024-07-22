# LINE Chatbot Integration with OpenAI for SK-Medical

This project is a LINE messaging chatbot designed for SK-Medical, a Thai medical distribution company.
Customers can prompt the chatbot over the LINE messaging app to create or sign into an account, search for products, and place orders using natural language, making the interaction intuitive and user-friendly.

The chatbot can be messaged at LINE ID @225yfsmj

### Author

This project was created by Ayden Lamparski during my Summer 2024 internship in Korea at Undernamu Consulting Company.

## Description

The chatbot leverages the following technologies:
- **OpenAI Assistants:** Utilizes OpenAI's conversational AI to understand and respond to user queries. The assistant can intellegently decide to use function calls to connect to SK-Medicals Odoo database.
- **LINE API:** Uses LINE's messaging platform to interact with users, sending and receiving messages through the LINE app.
- **Odoo API:** Integrates with Odoo ERP via function tool calls to retrieve product information, retrieve account information, create accounts, and create invoices.
- **AWS Lambda:** Utilizes AWS Lambda to host the chatbot asynchronously, enabling automatic scaling to handle varying workloads. Integrates with an API endpoint to connect to the LINE API via a webhook.
- **AWS DynamoDB:** Employs a DynamoDB table to map LINE IDs to their respective conversational contexts, ensuring seamless and personalized user interactions by maintaining state across sessions.

## File Structure


```
├── requirements.txt
├── venv/
├── functions.json
├── deployment_package.zip
├── deployment_package/
│   ├── config.py
│   ├── lambda_function.py
│   ├── assistant.py
│   ├── database.py
│   ├── odoo.py
│   ├── utils.py
```

### Description of Files

- **config.py:**
  Handles the configuration settings and environment variables for the project. Defines necessary configurations for OpenAI, AWS, and LINE.

- **lambda_function.py:**
  Contains the main AWS Lambda handler that processes incoming LINE messages, verifies signatures, and sends responses. It coordinates the flow between receiving a message and sending a reply.

- **assistant.py:**
  Interfaces with the OpenAI API to create threads, manage runs, and retrieve messages. Contains functions to initiate and manage interactions with the OpenAI assistant.

- **database.py:**
  Manages interactions with AWS DynamoDB to store and retrieve thread IDs associated with LINE user IDs. Ensures initial messages sent automatically by LINE are contained in the conversational context.

- **odoo.py:**
  Integrates with the Odoo ERP system to interact with its XML-RPC API. Contains functions to retrieve product information based on specified criteria, create invoices in the Odoo system, retrieve partner (account) information based on specified criteria, and create new partners in the Odoo database.

- **utils.py:**
  Provides utility functions to support various operations. Includes make_request to handle HTTP requests and process responses, and log_message to facilitate logging messages at different levels (info and error).

- **functions.json:**
  Contains the instructions provided to the chatbot and detailed descriptions of the function tool calls used in the system. This file is manually entered into the OpenAI Assistant through their website to guide the chatbot's behavior and interactions with the Odoo ERP system.
