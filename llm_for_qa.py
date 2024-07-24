# -*- coding: utf-8 -*-
"""PDF_reading_using_hf_and_pinecone.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KPt1r6Z7csSujnL_ZI7r1fM6SNZ2vumR
"""

"""##**Functions of each:** <br>
**transformers:** This library is used to work with pre-trained machine learning
models for natural language processing (NLP) tasks. It provides a powerful API for loading, fine-tuning, and using these models for tasks like text classification, question answering, and text generation.

**datasets:**This library provides tools for easily downloading, preparing, and working with large datasets commonly used in machine learning and NLP tasks. It simplifies the process of finding, loading, and processing datasets for your specific needs.

**PyPDF2**: This library allows you to work with PDF documents in Python. It provides functionalities for reading, manipulating, and writing data from and to PDF files. This could be useful for tasks like extracting text content from PDFs for further analysis.

**pinecone-client:** This library is the client library for interacting with the Pinecone vector similarity search service. Pinecone allows you to efficiently search for similar data points based on their vector representations. This library enables you to index data (potentially extracted from PDFs using PyPDF2) and perform vector searches on the Pinecone cloud service.


<br> **TLDR: this line of code installs libraries for:**

Working with NLP models (transformers)
Managing datasets (datasets)
Processing PDFs (PyPDF2)
Interacting with Pinecone vector search service (pinecone-client)

"""

from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering, AutoModel

"""# tools for building a question answering system:

* Tokenizing text data (AutoTokenizer).
* Loading a pre-trained question answering model (AutoModelForQuestionAnswering).
* Potentially using a general model architecture (AutoModel).
* Creating a dedicated question answering pipeline (pipeline).








"""

from PyPDF2 import PdfReader

"""This line imports the PdfReader class from the PyPDF2 library

Other Tools in PyPDF2:

* PdfWriter: This class is the counterpart to PdfReader and is used to create new PDF documents or modify existing ones.
* PdfMerger: This class helps you merge multiple PDF files into a single document.
* PageObject: This class represents a single page within a PDF document. You can use it to extract text content, get information about page size and orientation, and even manipulate specific page elements.
* Transformation: This class allows you to rotate, scale, and crop pages within a PDF.
* DocumentInformation and XmpInformation: These classes provide access to the document's metadata, such as author, title, and creation date.

"""

import pinecone


import os
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(
    api_key='234d75df-1248-42e1-b908-a0e2d80513ae' )



index_name = 'pdf-qa-index'
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  # Adjust dimension as needed
        metric='cosine',  # Cosine similarity is commonly used for text embeddings
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )
index = pc.Index(index_name)



from transformers import AutoTokenizer, AutoModel
import torch

model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embeddings(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().tolist()

'''embeddings = [get_embeddings(chunk) for chunk in text_chunks]

for i, embedding in enumerate(embeddings):
    index.upsert(vectors=[(str(i), embedding, {"text": text_chunks[i]})])'''

import google.generativeai as genai

genai.configure(api_key='AIzaSyCjllNUu9M83w3yYxWIhezapaahx87ebfs')
gmodel = genai.GenerativeModel('gemini-1.5-flash')

def query_bot(question):
    # Get question embedding
    question_embedding = get_embeddings(question)

    # Query Pinecone
    results = index.query(vector=question_embedding, top_k=3, include_metadata=True)

    context = " ".join([result['metadata']['text'] for result in results['matches']])

    # Generate response with Gemini Pro
    prompt = f"You are Benjamin Graham, author of 'The Intelligent Investor', answer the following question as if you are Benjamin Graham yourself based on this context: {context} and your own knowledge as well. \n \n Question: {question}. ONLY ANSWER QUESTIONS RELATED TO INVESTMENTS. ensure your responses are well-formatted for readability but it still feels like you are conversing with the user. Use the following guidelines: Bold headings for major points.Use numbered lists for steps or sequential instructions.Use bullet points for non-sequential information.Separate paragraphs with a blank line.Use proper punctuation and grammar."
    response = gmodel.generate_content(prompt)

    # Extract the generated content
    generated_text = response.text
    

    return generated_text
