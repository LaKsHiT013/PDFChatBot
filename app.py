from flask import Flask, request, render_template, redirect, url_for, session
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import Pinecone as PC
import os
from google.api_core.exceptions import InternalServerError, GoogleAPIError

# Load environment variables
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")  # Secret key for session management

# Configure Google Generative AI
def configure_google_genai():
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    except InternalServerError as e:
        print(f"Internal Server Error while configuring Google API: {e}")
    except GoogleAPIError as e:
        print(f"Google API Error while configuring: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during configuration: {e}")

configure_google_genai()

# Configure Pinecone
os.environ['PINECONE_API_KEY'] = os.getenv("PINECONE_API_KEY")

def Pine():
    from pinecone import Pinecone, ServerlessSpec

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "testing"

    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
    return index_name

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    index_name = Pine()
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    try:
        docsearch = PC.from_texts([t for t in text_chunks], embedding, index_name=index_name)
    except InternalServerError as e:
        print(f"Internal Server Error while creating vector store: {e}")
        docsearch = None
    except GoogleAPIError as e:
        print(f"Google API Error while creating vector store: {e}")
        docsearch = None
    except Exception as e:
        print(f"An unexpected error occurred while creating vector store: {e}")
        docsearch = None
    return index_name if docsearch else None


class SmartAgent:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def should_call_vectordb(self, query):
        trivial_queries = ['hello', 'hi', 'how are you', 'who are you']
        return query.lower() not in trivial_queries

    def decide_action(self, query):
        if "summarize" in query.lower():
            return self.summarize_pdf
        elif "calculate" in query.lower():
            return self.calculate
        else:
            return self.query_vectordb

    def summarize_pdf(self, query):
        return "Here's a brief summary of the PDF content."

    def calculate(self, query):
        try:
            return str(eval(query.split("calculate")[1].strip()))
        except Exception as e:
            return f"Error in calculation: {e}"

    def query_vectordb(self, query):
        try:
            llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-pro-latest", temperature=0.9)
            from langchain.chains import RetrievalQA
            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever()
            )
            return qa(query)["result"]
        except InternalServerError as e:
            print(f"Internal Server Error while querying VectorDB: {e}")
            return "An internal error occurred while processing your request."
        except GoogleAPIError as e:
            print(f"Google API Error while querying VectorDB: {e}")
            return "An error occurred with the Google API."
        except Exception as e:
            print(f"An unexpected error occurred while querying VectorDB: {e}")
            return "An unexpected error occurred."

    def handle_query(self, query):
        action = self.decide_action(query)
        return action(query)

# In your index route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'pdf_files' not in request.files:
            return render_template("index.html", error="No files uploaded.")

        pdf_files = request.files.getlist('pdf_files')
        raw_text = get_pdf_text(pdf_files)
        text_chunks = get_text_chunks(raw_text)
        index_name = get_vector_store(text_chunks)
        if index_name is None:
            return render_template("index.html", error="Failed to process the documents.")
        session["index_name"] = index_name
        return redirect(url_for('chat'))

    return render_template("index.html")

# In your chat route
@app.route("/chat", methods=["GET", "POST"])
def chat():
    response = None
    index_name = session.get("index_name")
    if index_name:
        embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        docsearch = PC.from_existing_index(index_name, embedding)
        if request.method == "POST":
            user_question = request.form.get("user_question")
            if user_question:
                agent = SmartAgent(docsearch)
                if agent.should_call_vectordb(user_question):
                    response = agent.handle_query(user_question)
                else:
                    response = "No need to call the VectorDB for this query."
    else:
        return redirect(url_for('index'))
    return render_template("chat.html", response=response)


if __name__ == "__main__":
    app.run(debug=True)