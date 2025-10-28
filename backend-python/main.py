import os
import tempfile
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, Header, HTTPException
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
app = FastAPI()

# Carregar ou criar o banco vetorial
persist_dir = "./chroma_db"
embedding = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-mpnet-base-v2",
    task="feature-extraction",
    huggingfacehub_api_token=os.getenv('HUGGINGFACE_API_KEY')
)

vectorStore = Chroma(
    persist_directory="/app/chroma_db",
    embedding_function=embedding,
    collection_name="documentos"
)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# Função para formatar documentos recuperados
def format_docs(docs):
    """Extrai o conteúdo de texto dos documentos"""
    return "\n\n".join(doc.page_content for doc in docs)

# Criar o pipeline RAG
prompt = ChatPromptTemplate.from_template("""
    Use o contexto a seguir para responder com precisão e clareza.
    Se a resposta não estiver no contexto, diga "Não encontrei informações suficientes no contexto".

    Contexto:
    {context}

    Pergunta: {question}
""")

retriever = vectorStore.as_retriever(search_kwargs={"k": 4})

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

@app.get("/")
def read_root():
    return {"message": "Serviço de RAG com FastAPI está no ar!"}

@app.post("/ask")
async def ask_question(prompt: str):
    response = rag_chain.invoke(prompt)
    return {"answer": response}

@app.post("/upload")
async def upload_pdf(file: UploadFile):    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    loader = PyPDFLoader(tmp_path)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(docs)
    
    vectorStore.add_documents(chunks)
    
    # Limpar arquivo temporário
    os.unlink(tmp_path)
    
    return {"message": f"{len(chunks)} novos documentos indexados."}