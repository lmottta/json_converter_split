# Conversor e Divisor de Arquivos JSON

Este projeto visa criar uma aplicação web simples em Python para converter diferentes formatos de arquivo (xlsx, csv, xml, etc.) para JSON e, em seguida, permitir que o usuário divida o arquivo JSON resultante em partes definidas.

## Funcionalidades:
1.  **Conversão de Arquivos**: Suporte para converter xlsx, csv, xml e outros formatos para JSON.
2.  **Divisão de Arquivos**: Capacidade de dividir o arquivo JSON em partes menores, conforme especificado pelo usuário.

## Estrutura do Projeto:
-   `app.py`: Ponto de entrada da aplicação web.
-   `celery_worker.py`: Configuração do worker Celery para processamento assíncrono.
-   `start_services.ps1`: Script PowerShell para iniciar os serviços da aplicação.
-   `git_publish.ps1`: Script PowerShell para publicar o projeto no Git.
-   `requirements.txt`: Lista de dependências do Python.
-   `docs/desenvolvimento`: Documentação do projeto.
-   `README.md`: Este arquivo.

## Como Executar:

1.  **Clone o repositório (se aplicável) ou navegue até a pasta do projeto:**
    ```bash
    cd json_converter
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate   # No Windows
    # source venv/bin/activate  # No macOS/Linux
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Inicie o Redis:**
    Certifique-se de que o servidor Redis esteja em execução. Você pode baixá-lo e instalá-lo a partir de: https://redis.io/docs/getting-started/installation/

5.  **Inicie os serviços da aplicação:**
    ```bash
    .\start_services.ps1
    ```

6.  **Acesse a aplicação no navegador:**
    Abra seu navegador e vá para `http://127.0.0.1:5000/`

## Publicação no Git

Para publicar o projeto no Git, você pode usar o script `git_publish.ps1` incluído:

1. **Execute o script PowerShell:**
   ```powershell
   .\git_publish.ps1
   ```

2. **Siga as instruções no prompt:**
   - Digite uma mensagem de commit (ou pressione Enter para usar a mensagem padrão)
   - Digite a URL do repositório remoto (ou pressione Enter para pular esta etapa)
   - Digite o nome do branch (ou pressione Enter para usar 'main')

3. **O script irá:**
   - Verificar se o Git está instalado
   - Inicializar um repositório Git (se necessário)
   - Adicionar todos os arquivos ao Git
   - Criar um commit com a mensagem fornecida
   - Configurar o repositório remoto (se fornecido)
   - Enviar as alterações para o repositório remoto

Se você pular a configuração do repositório remoto, o script fornecerá instruções sobre como configurá-lo posteriormente.