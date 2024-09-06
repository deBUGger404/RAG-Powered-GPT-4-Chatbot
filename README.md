# RAG-Powered GPT-4 Chatbot: AI-Based Knowledge Retrieval

🚀 Revolutionize data interaction with a chatbot built using **Retrieval-Augmented Generation (RAG)** and **OpenAI’s GPT-4**. Upload documents, create custom knowledge bases, and get precise, contextual answers for research, business operations, and customer support.

## Table of Contents
1. [Introduction](#introduction)
2. [Key Features](#key-features)
3. [Use Cases](#use-cases)
4. [How It Works](#how-it-works)
5. [Getting Started](#getting-started)
6. [File Structure](#file-structure)
7. [Contributing](#contributing)
8. [License](#license)

## Introduction
The RAG-powered chatbot combines retrieval and generative AI to help users access specific information from custom data sources. By uploading your documents, the chatbot can pull the most relevant data from your files, ensuring high accuracy and up-to-date answers.

## Key Features
- **Upload Documents**: Add PDFs or other documents that will be chunked into manageable parts and stored as vectors in a database.
- **Custom Knowledge Base**: Create a searchable knowledge base from your uploaded files.
- **Persistent Database**: Save, retrieve, and reuse your knowledge base at any time.
- **Accurate Responses**: Get context-aware answers based on the data in your custom knowledge base.

## Use Cases
- **Research**: Analyze large datasets, studies, and research papers by querying relevant information.
- **Business Operations**: Access internal documents and policies quickly for better decision-making.
- **Customer Support**: Create a chatbot that instantly pulls data from FAQs or product manuals.
- **Training & Onboarding**: Provide new hires with instant access to key internal documents and training materials.

## How It Works
1. **Upload Documents**:
   - Upload PDF or text files to the system.
   - The files are automatically split into smaller sections and converted into vectors for efficient searching.
  
2. **Create Knowledge Base**:
   - The system builds a custom knowledge base from the uploaded documents.
   - This knowledge base can be searched using natural language queries.

3. **Query Knowledge Base**:
   - Use the chatbot interface to ask questions.
   - The system retrieves the most relevant information from the knowledge base using semantic search.

4. **Persistent Database**:
   - Save your uploaded files and databases for future access.
   - Reuse or modify the knowledge base without the need to re-upload files.

## Getting Started

### Prerequisites
- **Python 3.x**
- **OpenAI API Key** for GPT-4 integration

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/rag-powered-gpt4-chatbot.git
    cd rag-powered-gpt4-chatbot
    ```

2. **Set up a virtual environment**:
    ```bash
    python -m venv ragvenv
    source ragvenv/bin/activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure API keys**:
   - Add your OpenAI API key to `config.env`:
     ```bash
     OPENAI_API_KEY="your-api-key"
     ```

5. **Run the application**:
    ```bash
    python app.py
    ```

6. **Access the application**:
   - Open your browser and go to `http://localhost:5000`.

### Using the Application

1. **Upload a file**:
   - Navigate to the "Upload File" section of the app.
   - Select a PDF or other document to upload.
   
2. **Create a knowledge base**:
   - The uploaded document will be processed and split into chunks.
   - A custom knowledge base is created from these chunks and stored for future queries.

3. **Query the chatbot**:
   - Type your questions in the chatbot input field.
   - The chatbot will retrieve relevant information from the custom knowledge base based on your query.

4. **Access previous databases**:
   - Use the dropdown menu to access and query previously created databases.

## File Structure

```plaintext
📂 rag-powered-gpt4-chatbot/
├── app.py               # Main application script
├── config.env           # Configuration file for API keys
├── database/            # Folder for storing database files
├── rag_app.log          # Log file for tracking application events
├── requirements.txt     # Python dependencies
├── static/              # Static files like CSS
│   └── styles.css       # CSS file for basic styling
├── templates/           # HTML templates for the app interface
│   └── index.html       # Main page of the app
├── upload_file/         # Directory for storing uploaded files
├── utils.py             # Utility functions

Contributing 
------------ 
Contributions are welcome! Please open an issue or submit a pull request if you'd like to add new features or fix bugs. 

License 
------- 
This project is licensed under the MIT License.

*** Happy coding! 🤖 Let's bring AI closer to the knowledge that matters most to you.