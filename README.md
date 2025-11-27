Para rodar o projeto, primeiro é necessário criar:
    1) Token JWT para segurança do endpoint de Update (`.env` do diretório `backend-java`)
    2) Chaves das APIs do Groq e do Hugging Face (`.env` do diretório `backend-python`)

Após isso, executar o comando `docker compose up --build` na raiz do projeto.

# POST /ask
O endpoint /ask é o funcionamento principal do sistema: aciona o funcionamento da LLM através
 da API do Groq.

# POST /upload
Este endpoint permite o carregamento de arquivos `.pdf` para o banco vetorial do sistema.
O backend python pode utilizar de regras de pré-processamento (utilizando Regex) para
melhor análise e indexação do conteúdo.