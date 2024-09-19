# PDFChatBot

## Overview
PDFChatbot is a Flask-based web application designed to process PDF documents and provide intelligent responses based on the content of those documents. Leveraging Google Generative AI and Pinecone for vector storage, this application allows users to upload PDF files, extract and index their text content, and interact with the content through a chat interface. The SmartAgent within the application can handle various queries, including summarizing content and performing calculations.

## Features
-> PDF Upload and Processing: Upload PDF files, extract text, and split it into manageable chunks. <br>
-> Vector Store Integration: Utilize Pinecone for indexing and querying text content. <br>
-> Smart Agent: A decision-making system that determines whether to summarize, calculate, or query the vector store based on user input. <br>
-> Chat Interface: Interact with the processed content through a chat interface. <br>


## Prerequisites
-> Python 3.7 or later <br>
-> Flask <br>
-> PyPDF2 <br>
-> LangChain <br>
-> Google Generative AI API <br>
-> Pinecone <br>

## How It Works

1) Upload PDF Files: Navigate to the home page and upload one or more PDF files. The text from these PDFs will be extracted and split into chunks. <br>

2) Indexing and Storage: The extracted text chunks are indexed using Pinecone for efficient querying. <br>

3) Chat Interface: After processing, you'll be redirected to the chat page where you can interact with the content. The SmartAgent decides whether to summarize the content, perform calculations, or query the vector store based on your input. <br>

## Future Plans
-> Enhanced Query Handling: Improve the SmartAgent's ability to handle a wider variety of queries. <br>
-> UI/UX Improvements: Enhance the user interface and experience for better usability. <br>
-> Document Summarization: Implement more advanced summarization techniques for better content understanding. <br>
-> Error Handling: Improve error handling and logging mechanisms for better reliability and debugging. <br>
