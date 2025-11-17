import os
import tempfile
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from pydantic import BaseModel
from preprocessing import CurricularStructureProcessor, CourseSubjectsProcessor, GenericProcessor

load_dotenv()
app = FastAPI()

class Question(BaseModel):
    prompt: str

# Carregar ou criar o banco vetorial
persist_dir = "./chroma_db"
embedding = HuggingFaceEmbeddings(model="intfloat/multilingual-e5-base")

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
    Você é **Ada**, assistente virtual do curso de **Tecnologia em Sistemas para Internet da UFSM**.
    Responda apenas com base no contexto fornecido.  
    Se não houver informação suficiente, diga:  
    "Não encontrei informações suficientes no contexto."

    **IMPORTANTE sobre cálculos de carga horária:**
    - Se a pergunta for sobre carga horária TOTAL do curso, você DEVE somar:
      * Carga horária do currículo fixo (conteúdos)
      * Carga horária mínima de DCG (Disciplinas Complementares de Graduação)
      * Carga horária mínima de ACG (Atividades Complementares de Graduação)
      * Carga horária mínima de ACEx (Atividades Complementares de Extensão)
    - Mostre o cálculo detalhado da soma
    - Sempre verifique se há informações de resumo de carga horária no contexto

    Contexto:
    {context}

    Pergunta: {question}
""")

retriever = vectorStore.as_retriever(search_kwargs={"k": 6})

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
async def ask_question(question: Question):
    response = rag_chain.invoke(f"query: {question.prompt}")
    return {"answer": response}

@app.post("/upload")
async def upload_pdf(file: UploadFile):    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    loader = PyPDFLoader(tmp_path)
    # Carrega as páginas do PDF em memória
    loaded_docs = loader.load()
    content = " ".join(doc.page_content for doc in loaded_docs)
    
    # Construir a Chain of Responsibility
    # O GenericProcessor é o fallback, então ele vem por último.
    processor_chain = CurricularStructureProcessor(
        next_processor=CourseSubjectsProcessor(
            next_processor=GenericProcessor()
        )
    )
    
    # Executar a cadeia de processamento
    processed_docs = processor_chain.handle(content)
    
    # Se nenhum processador lidar com o conteúdo, usamos os documentos carregados originalmente
    if not processed_docs:
        processed_docs = loaded_docs

    # Split dos documentos
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, 
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(processed_docs)
    
    # Adicionar prefixo para embeddings
    for chunk in chunks:
        chunk.page_content = "passage: " + chunk.page_content
    
    vectorStore.add_documents(chunks)
    
    # Limpar arquivo temporário
    os.unlink(tmp_path)
    
    return {"message": f"{len(chunks)} novos documentos indexados."}