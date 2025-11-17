import re
from typing import List
from langchain_core.documents import Document
from .base_processor import BaseProcessor

class CurricularStructureProcessor(BaseProcessor):
    """
    Processa documentos de estrutura curricular, extraindo seções e calculando a carga horária.
    """

    def can_handle(self, content: str) -> bool:
        """Verifica se o documento é sobre a estrutura curricular."""
        return "Estrutura Curricular" in content and "Carga horária" in content

    def _extrair_horas(self, texto: str) -> int:
        """Extrai valores de horas de um texto usando regex."""
        match = re.search(r'(\d+)\s*horas?', texto, re.IGNORECASE)
        return int(match.group(1)) if match else 0

    def process(self, content: str) -> List[Document]:
        """
        Processa o conteúdo da estrutura curricular, identificando e agrupando seções
        importantes como currículo fixo, flexível, ACG, ACEx, DCG.
        """
        docs = []
        
        # 1. Criar documento resumo com carga horária total calculada
        ch_fixo = 0
        ch_dcg = 0
        ch_acg = 0
        ch_acex = 0
        
        # Extrair informações de carga horária de cada seção
        if "Conteúdos do currículo fixo" in content:
            secao = re.search(
                r'Conteúdos do currículo fixo.*?Carga horária mínima:\s*([^\n]+)',
                content, re.DOTALL | re.IGNORECASE
            )
            if secao:
                ch_fixo = self._extrair_horas(secao.group(1))
        
        if "Disciplinas complementares de graduação" in content:
            secao = re.search(
                r'Disciplinas complementares de graduação.*?Carga horária mínima:\s*([^\n]+)',
                content, re.DOTALL | re.IGNORECASE
            )
            if secao:
                ch_dcg = self._extrair_horas(secao.group(1))
        
        if "Atividades complementares de graduação" in content:
            secao = re.search(
                r'Atividades complementares de graduação.*?Carga horária mínima:\s*([^\n]+)',
                content, re.DOTALL | re.IGNORECASE
            )
            if secao:
                ch_acg = self._extrair_horas(secao.group(1))
        
        if "Atividades complementares de extensão" in content:
            secao = re.search(
                r'Atividades complementares de extensão.*?Carga horária mínima:\s*([^\n]+)',
                content, re.DOTALL | re.IGNORECASE
            )
            if secao:
                ch_acex = self._extrair_horas(secao.group(1))
        
        # Calcular total
        ch_total = ch_fixo + ch_dcg + ch_acg + ch_acex
        
        # Criar documento resumo
        resumo = f"""RESUMO DA ESTRUTURA CURRICULAR - CARGA HORÁRIA TOTAL

Carga horária total do curso: {ch_total} horas

Detalhamento:
- Conteúdos do currículo fixo: {ch_fixo} horas
- Disciplinas Complementares de Graduação (DCG): {ch_dcg} horas
- Atividades Complementares de Graduação (ACG): {ch_acg} horas
- Atividades Complementares de Extensão (ACEx): {ch_acex} horas

Cálculo: {ch_fixo} + {ch_dcg} + {ch_acg} + {ch_acex} = {ch_total} horas
"""
        
        docs.append(Document(
            page_content=resumo,
            metadata={"tipo": "resumo_carga_horaria", "secao": "geral"}
        ))
        
        # 2. Extrair informações gerais do currículo
        info_gerais = re.search(
            r'Informações gerais do currículo.*?(?=Estruturas curriculares|Disciplinas do currículo)',
            content, re.DOTALL | re.IGNORECASE
        )
        if info_gerais:
            texto = info_gerais.group(0).strip()
            docs.append(Document(
                page_content=f"INFORMAÇÕES GERAIS DO CURRÍCULO\n\n{texto}",
                metadata={"tipo": "informacoes_gerais", "secao": "estrutura_curricular"}
            ))
        
        # 3. Extrair seção de Conteúdos do currículo fixo
        curriculo_fixo = re.search(
            r'Conteúdos do currículo fixo.*?(?=Disciplinas do currículo flexível|Atividades complementares)',
            content, re.DOTALL | re.IGNORECASE
        )
        if curriculo_fixo:
            texto = curriculo_fixo.group(0).strip()
            docs.append(Document(
                page_content=f"CURRÍCULO FIXO (CONTEÚDOS OBRIGATÓRIOS)\n\n{texto}\n\nEsta é a base obrigatória do curso com carga horária mínima de {ch_fixo} horas.",
                metadata={"tipo": "curriculo_fixo", "secao": "estrutura_curricular", "carga_horaria": ch_fixo}
            ))
        
        # 4. Extrair seção de Disciplinas do currículo flexível
        curriculo_flexivel = re.search(
            r'Disciplinas do currículo flexível.*?(?=Atividades complementares|Disciplinas complementares)',
            content, re.DOTALL | re.IGNORECASE
        )
        if curriculo_flexivel:
            texto = curriculo_flexivel.group(0).strip()
            docs.append(Document(
                page_content=f"CURRÍCULO FLEXÍVEL (DISCIPLINAS OPTATIVAS)\n\n{texto}",
                metadata={"tipo": "curriculo_flexivel", "secao": "estrutura_curricular"}
            ))
        
        # 5. Extrair DCG - Disciplinas Complementares de Graduação
        dcg = re.search(
            r'Disciplinas complementares de graduação \(DCG\).*?(?=Estrutura Curricular\d+|\Z)',
            content, re.DOTALL | re.IGNORECASE
        )
        if dcg:
            texto = dcg.group(0).strip()
            docs.append(Document(
                page_content=f"DCG - DISCIPLINAS COMPLEMENTARES DE GRADUAÇÃO\n\n{texto}\n\nCarga horária mínima obrigatória: {ch_dcg} horas",
                metadata={"tipo": "dcg", "secao": "estrutura_curricular", "carga_horaria": ch_dcg}
            ))
        
        # 6. Extrair ACG - Atividades Complementares de Graduação
        acg = re.search(
            r'Atividades complementares de graduação \(ACG\).*?(?=Disciplinas complementares|Atividades complementares de extensão|\Z)',
            content, re.DOTALL | re.IGNORECASE
        )
        if acg:
            texto = acg.group(0).strip()
            docs.append(Document(
                page_content=f"ACG - ATIVIDADES COMPLEMENTARES DE GRADUAÇÃO\n\n{texto}\n\nCarga horária mínima obrigatória: {ch_acg} horas",
                metadata={"tipo": "acg", "secao": "estrutura_curricular", "carga_horaria": ch_acg}
            ))
        
        # 7. Extrair ACEx - Atividades Complementares de Extensão
        acex = re.search(
            r'Atividades complementares de extensão \(ACEx\).*?(?=Atividades complementares de graduação|Disciplinas complementares|\Z)',
            content, re.DOTALL | re.IGNORECASE
        )
        if acex:
            texto = acex.group(0).strip()
            docs.append(Document(
                page_content=f"ACEx - ATIVIDADES COMPLEMENTARES DE EXTENSÃO\n\n{texto}\n\nCarga horária mínima obrigatória: {ch_acex} horas",
                metadata={"tipo": "acex", "secao": "estrutura_curricular", "carga_horaria": ch_acex}
            ))
        
        return docs
