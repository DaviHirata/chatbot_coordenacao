import re
from typing import List
from langchain_core.documents import Document
from .base_processor import BaseProcessor

class CourseSubjectsProcessor(BaseProcessor):
    """
    Processa documentos que contêm grades de disciplinas divididas por semestre.
    """

    def can_handle(self, content: str) -> bool:
        """Verifica se o documento contém uma grade de disciplinas por semestre."""
        return bool(re.search(r"(\d+°\s*Semestre)", content))

    def process(self, content: str) -> List[Document]:
        """Divide o conteúdo em documentos, um para cada semestre."""
        docs = []
        # O split captura os delimitadores (ex: "1º Semestre")
        blocos = re.split(r"(\d+°\s*Semestre)", content)
        
        # A lista 'blocos' terá o formato: ['', '1º Semestre', 'conteúdo...', '2º Semestre', 'conteúdo...']
        # Portanto, iteramos de 3 em 3 a partir do índice 1
        for i in range(1, len(blocos), 2):
            titulo = blocos[i].strip()
            texto = blocos[i + 1].strip()
            
            docs.append(Document(
                page_content=f"{titulo}\n{texto}",
                metadata={"semestre": titulo, "tipo": "grade_disciplinas"}
            ))
            
        return docs
