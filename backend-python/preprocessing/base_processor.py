from abc import ABC, abstractmethod
from typing import List, Optional
from langchain_core.documents import Document

class BaseProcessor(ABC):
    """
    Classe base abstrata para definir a estrutura de um processador de documentos.
    Implementa o padrão Chain of Responsibility.
    """
    def __init__(self, next_processor: Optional['BaseProcessor'] = None):
        self._next_processor = next_processor

    @abstractmethod
    def can_handle(self, content: str) -> bool:
        """
        Verifica se este processador pode manipular o conteúdo do documento.

        :param content: O conteúdo textual do documento.
        :return: True se o processador puder manipular o conteúdo, False caso contrário.
        """
        pass

    @abstractmethod
    def process(self, content: str) -> List[Document]:
        """
        Processa o conteúdo do documento e o transforma em uma lista de Documentos LangChain.

        :param content: O conteúdo textual do documento.
        :return: Uma lista de objetos Document.
        """
        pass

    def handle(self, content: str) -> List[Document]:
        """
        Executa o processamento se o manipulador for adequado, ou passa para o próximo na cadeia.

        :param content: O conteúdo textual do documento.
        :return: Uma lista de objetos Document processados.
        """
        if self.can_handle(content):
            return self.process(content)
        elif self._next_processor:
            return self._next_processor.handle(content)
        else:
            return []
