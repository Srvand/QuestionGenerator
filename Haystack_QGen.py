import streamlit as st
import os
import docx
import haystack
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import BM25Retriever,TfidfRetriever,PromptNode, PromptTemplate
from haystack.nodes import FARMReader,TransformersReader
from haystack.pipelines import ExtractiveQAPipeline,DocumentSearchPipeline,GenerativeQAPipeline,Pipeline
from haystack.utils import print_answers
from haystack.pipelines.standard_pipelines import TextIndexingPipeline
from haystack import Document
from haystack.utils import print_answers
import pdfplumber
from haystack.nodes import OpenAIAnswerGenerator
from haystack.nodes.prompt import PromptTemplate
import re
from haystack.pipelines import QuestionGenerationPipeline,RetrieverQuestionGenerationPipeline,QuestionAnswerGenerationPipeline
from haystack.nodes import QuestionGenerator
import openai

document_store = InMemoryDocumentStore(use_bm25=True)
documents=[]
def add_document(document_store, file):
    if file.type == 'text/plain':
        text = file.getvalue().decode("utf-8")
        # document_store.write_documents(dicts)
        # st.write(file.name)
        # st.write(text)
    elif file.type == 'application/pdf':
        with pdfplumber.open(file) as pdf:
            text = "\n\n".join([page.extract_text() for page in pdf.pages])
            # document_store.write_documents([{"text": text, "meta": {"name": file.name}}])
            # st.write(text)
    elif file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        doc = docx.Document(file)
        text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
        # document_store.write_documents([{"text": text, "meta": {"name": file.name}}])
        # st.write(text)
    else:
        st.warning(f"{file.name} is not a supported file format")
    dicts = {
            'content': text,
            'meta': {'name': file.name}
            }  
    documents.append(dicts) 

    
# create Streamlit app
st.title("Questions Generation for Document Archive")
API_KEY = st.secrets['OPENAI_API_KEY']
openai.api_key =API_KEY
# create file uploader
uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True)

# loop through uploaded files and add them to document store
if uploaded_files:
    for file in uploaded_files:
        add_document(document_store, file)
document_store.write_documents(documents)
# display number of documents in document store
st.write(f"Number of documents uploaded to document store: {document_store.get_document_count()}")

if (document_store.get_document_count()!=0):
    question_generator = QuestionGenerator()
    question_generation_pipeline = QuestionGenerationPipeline(question_generator)
    for idx, document in enumerate(document_store):
        document_name = document.meta['name']
        st.write(f"\n * Generating questions for document {document_name}")
        result = question_generation_pipeline.run(documents=[document])
        st.write(result['generated_questions'][0]['questions'])
