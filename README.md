# Sistema Micas Daminhas 

## Visão Geral
Este projeto é uma aplicação web projetada para gerenciar pagamentos e registros para Micas Daminhas. Ele fornece funcionalidades para upload de dados, edição de registros, geração de relatórios e adição de novas entradas.

## Estrutura do Projeto
```
my-new-project
├── src
│   ├── components          # Contém componentes reutilizáveis
│   ├── pages               # Contém diferentes páginas da aplicação
│   │   ├── home.py         # Página inicial da aplicação
│   │   ├── upload.py       # Página para upload de arquivos
│   │   ├── edit.py         # Página para edição de registros
│   │   ├── report.py       # Página para geração de relatórios
│   │   └── new_record.py   # Página para adição de novos registros
│   ├── helpers.py          # Funções auxiliares para a aplicação
│   └── main.py             # Ponto de entrada da aplicação
├── requirements.txt        # Lista de dependências
└── README.md               # Documentação do projeto
```

## Setup Instructions
2. Crie um Ambiente Virtual: Crie um ambiente virtual chamado env no diretório do projeto:
- `python -m venv env`

3. Ative o Ambiente Virtual: Ative o ambiente virtual. 
- `call env\Scripts\activate.bat`

3. Instale as Dependências: 
- `pip install -r requirements.txt`

## Uso
5. Execute a Aplicação Streamlit:
- `streamlit run main.py`
- Access the application in your web browser at `http://localhost:8501`.

