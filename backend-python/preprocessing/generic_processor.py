from typing import List
from langchain_core.documents import Document
from .base_processor import BaseProcessor

class GenericProcessor(BaseProcessor):
    """
    Processador genérico para documentos que não se encaixam em outras categorias.
    Realiza uma limpeza básica no texto.
    """

    def can_handle(self, content: str) -> bool:
        """
        Este processador é um fallback, então ele sempre pode manipular o conteúdo,
        assumindo que ele é o último na cadeia de responsabilidade.
        """
        return True

    def process(self, content: str) -> List[Document]:
        """
        Processa o conteúdo genérico, limpando quebras de linha e espaços extras.
        Retorna o conteúdo como um único Documento.
        """
        # A lógica original criava um único documento se não fosse de um tipo específico
        # A limpeza de \n era feita em um loop, mas o conteúdo já estava concatenado.
        # Portanto, aplicamos a limpeza ao conteúdo completo e criamos um Documento.
        cleaned_content = content.replace('\n', ' ').strip()
        
        # A lógica original em main.py não criava um Document para o caso 'else',
        # ela apenas modificava os 'docs' carregados pelo PyPDFLoader.
        # Para manter a consistência do padrão, criaremos um novo Document aqui.
        # Se o conteúdo original já estiver dividido em documentos, o ideal
        # seria iterar sobre eles. Como recebemos 'content' como uma string única,
        # criamos um único documento a partir dela.
        return [Document(page_content=cleaned_content)]
