import os
import time
import logging  # Import the logging module
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from flask_cors import CORS
from openai import AzureOpenAI
from utils import *

# Configure logging
logging.basicConfig(filename='rag_app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed to use Flask sessions
CORS(app)

# Load environment variables from the .env file
load_dotenv('config.env')

# Assign the variables
azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
azure_openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
azure_api_version = os.getenv('API_VERSION')

# Base folder path where the databases are stored
BASE_FOLDER_PATH = "database"

# File folder path where the uploaded file are Saved
File_FOLDER_PATH = "upload_file"

client = AzureOpenAI(
    api_key=azure_openai_api_key,  
    api_version=azure_api_version,
    azure_endpoint=azure_openai_endpoint
)

@app.route('/')
def home():
    logging.info("Rendering home page")
    return render_template('index.html')

# Function to get files from a selected database (Placeholder for your logic)
def get_files_from_database(database_name):
    CHROMA_PATH = os.path.join(BASE_FOLDER_PATH, database_name)
    logging.info(f"Fetching files from database: {database_name}")
    
    try:
        db = Chroma(persist_directory=CHROMA_PATH)
        all_items = db.get(include=["metadatas"])
        file_list = list(set(i['source'].split(os.sep)[-1] for i in all_items['metadatas']))
        return file_list

    except Exception as e:
        logging.error(f"Error accessing the database {database_name}: {e}")
        return []

# Route to fetch all root folders (databases)
@app.route('/api/get-databases', methods=['GET'])
def get_databases():
    try:
        logging.info("Fetching list of databases")
        databases = [{'name': folder, 'id': folder} for folder in os.listdir(BASE_FOLDER_PATH) if os.path.isdir(os.path.join(BASE_FOLDER_PATH, folder))]
        return jsonify({'databases': databases})
    except Exception as e:
        logging.error(f"Error fetching databases: {e}")
        return jsonify({'error': str(e)}), 500

# API to fetch files based on the selected database
@app.route('/api/get-files', methods=['POST'])
def get_files():
    try:
        data = request.json
        database_name = data.get('database_name')
        if not database_name:
            logging.warning("No database name provided in request")
            return jsonify({'error': 'Database name is required'}), 400
        
        files = get_files_from_database(database_name)
        logging.info(f"Returning files for database: {database_name}")
        return jsonify({'files': files})
    except Exception as e:
        logging.error(f"Error fetching files for database {database_name}: {e}")
        return jsonify({'error': str(e)}), 500

# API to set the database in the session
@app.route('/api/set-database', methods=['POST'])
def set_database():
    data = request.json
    database_name = data.get('database_name')
    # files = data.get('files', [])

    if not database_name:# or not files:
        logging.warning("No database name provided while setting the database")
        return jsonify({'error': 'Database name and files are required'}), 400

    session['database_name'] = database_name
    # session['files'] = files
    session.modified = True
    logging.info(f"Database {database_name} set successfully in session")

    return jsonify({'message': 'Database set successfully'}), 200

@app.route('/api/upload-files', methods=['POST'])
def upload_files():
    try:
        # Get database name and files from the form data
        database_name = request.form.get('database_name')
        files = request.files.getlist('files[]')
        if not database_name:
            logging.warning("No database name provided during file upload")
            return jsonify({'error': 'Database name is required'}), 400

        if not files:
            logging.warning("No files provided during file upload")
            return jsonify({'error': 'No files uploaded'}), 400

        logging.info(f"Uploading files for database: {database_name}")
        # Placeholder: Process files and create the database
        file_folder_path = os.path.join(File_FOLDER_PATH, database_name)
        os.makedirs(file_folder_path, exist_ok=True)  # Create database folder if it doesn't exist

        db_folder_path = os.path.join(BASE_FOLDER_PATH, database_name)
        os.makedirs(db_folder_path, exist_ok=True)

        for file in files:
            logging.warning("No files provided during file upload")
            file_path = os.path.join(file_folder_path, file.filename)
            file.save(file_path)  # Save each uploaded file to the folder
            logging.info(f"File {file.filename} saved at {file_path}")
        
        # Placeholder for further processing, e.g., reading, chunking, indexing the files
        documents = load_documents(file_folder_path)
        chunks = split_documents(documents)
        embedding_function = get_embedding_function()
        add_to_chroma(db_folder_path, embedding_function, chunks)
        # Set the new database in session
        session['database_name'] = database_name
        session.modified = True

        logging.info(f"Database {database_name} created and set in session successfully")

        return jsonify({'message': 'Database created successfully!', 'database_name': database_name}), 200

    except Exception as e:
        logging.error(f"Error during file upload or database creation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    start_time = time.time()
    
    # Check if database is set in the session
    if 'database_name' not in session:
        logging.warning("Attempted to chat without setting a database")
        return jsonify({'error': 'Database not set yet! Please set the database first.'}), 400
    
    user_input = request.json.get('message')
    logging.info(f"User message received: {user_input}")

    if 'chat_history' not in session:
        session['chat_history'] = []
    
    session['chat_history'].append({"role": "user", "content": user_input})
    session.modified = True

    limited_history = session['chat_history'][-4:]

    embedding_function = get_embedding_function()
    CHROMA_PATH = os.path.join(BASE_FOLDER_PATH, session['database_name'])
    logging.info(f"Using CHROMA_PATH: {CHROMA_PATH}")
    
    try:
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        results = db.similarity_search_with_score(user_input, k=5)
        logging.info(f"Results found for query: {user_input}")
    except Exception as e:
        logging.error(f"Error during similarity search: {e}")
        return jsonify({'error': str(e)}), 500
    # print('results',results)
    response_text, pricing = azureopenai(client, results, limited_history, user_input)

    session['chat_history'].append({"role": "assistant", "content": response_text})
    session.modified = True
    
    end_time = time.time()
    time_taken = end_time - start_time

    logging.info(f"Response sent to user. Time taken: {time_taken:.2f}s, Cost: ${pricing:.2f}")

    return jsonify({'response': response_text, 'pricing': pricing, 'time_taken': time_taken, 'history': session['chat_history']})

def get_embedding_function():
    embeddings = AzureOpenAIEmbeddings(
        model="text-embedding-ada-002-v2",
        azure_endpoint=azure_openai_endpoint,
        api_key=azure_openai_api_key,
        openai_api_version=azure_api_version
    )
    return embeddings
    
def azureopenai(client, results, limited_history, query_text):
    prompt = DOCSEARCH_PROMPT.format(context=results, question=query_text)

    messages = [{"role": "system", "content": "Assistant is a large language model trained by OpenAI."}]
    messages.extend(limited_history)
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="test-quant-gpt-4o",
            messages=messages
        )
        pricing = get_openai_callback(response.usage.prompt_tokens, response.usage.completion_tokens)
        logging.info(f"Response generated by Azure OpenAI for query: {query_text}")
        return response.choices[0].message.content, pricing
    except Exception as e:
        logging.error(f"Error generating OpenAI response: {e}")
        return "Error generating response", 0

@app.route('/chat/reset', methods=['POST'])
def reset_chat():
    session.pop('chat_history', None)
    logging.info("Chat history reset")
    return jsonify({'status': 'Chat reset'}), 200
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
