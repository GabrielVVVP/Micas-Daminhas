# Sistema Micas Daminhas

## Visão Geral
O **Sistema Micas Daminhas** é uma aplicação web desenvolvida para gerenciar pagamentos, registros de eventos e participantes. Ele oferece funcionalidades como upload de dados, edição de registros, geração de relatórios e adição de novas entradas.

## Estrutura do Projeto
```
Micas-Daminhas
├── app
│   ├── pages               # Contém diferentes páginas da aplicação
│   │   ├── home.py         # Página inicial da aplicação
│   │   ├── upload.py       # Página para upload de arquivos
│   │   ├── edit.py         # Página para edição de registros
│   │   ├── report.py       # Página para geração de relatórios
│   │   ├── login.py        # Página de login e recuperação de senha
│   │   └── new_record.py   # Página para adição de novos registros
│   ├── utils               # Funções auxiliares e utilitários
│   │   ├── helpers.py      # Funções auxiliares para banco de dados e hashing
│   │   └── users.py        # Funções relacionadas à autenticação de usuários
│   └── main.py             # Ponto de entrada da aplicação
├── data                    # Diretório para o banco de dados SQLite
│   └── Micas_Daminhas.db   # Arquivo do banco de dados
├── env                     # Ambiente virtual Python
├── requirements.txt        # Lista de dependências do projeto
└── README.md               # Documentação do projeto
```

## Pré-requisitos
Certifique-se de ter os seguintes itens instalados no seu sistema:
- Python 3.8 ou superior
- Git (opcional, para controle de versão)

## Instruções de Configuração

### 1. Clone o Repositório
Se ainda não tiver o projeto, clone o repositório:
```bash
git clone https://github.com/seu-usuario/Micas-Daminhas.git
cd Micas-Daminhas
```

### 2. Crie um Ambiente Virtual
Crie um ambiente virtual chamado `env` no diretório do projeto:
```bash
python -m venv env
```

### 3. Ative o Ambiente Virtual
Ative o ambiente virtual:
- **Windows:**
  ```bash
  call env\Scripts\activate.bat
  ```
- **Linux/Mac:**
  ```bash
  source env/bin/activate
  ```

### 4. Instale as Dependências
Instale todas as dependências necessárias:
```bash
pip install -r requirements.txt
```

### 5. Configure o Banco de Dados
O banco de dados será criado automaticamente na primeira execução do sistema. Certifique-se de que o diretório `data` existe ou será criado pelo código.

## Uso

### 1. Execute a Aplicação
Inicie o servidor Streamlit:
```bash
streamlit run app/main.py
```

### 2. Acesse no Navegador
Abra o navegador e acesse:
```
http://localhost:8501
```

## Funcionalidades
- **Login e Recuperação de Senha:** Sistema de autenticação com recuperação de senha usando uma chave mestre.
- **Gerenciamento de Eventos:** Adicione, edite e visualize eventos e participantes.
- **Relatórios:** Gere relatórios detalhados de pagamentos e eventos.
- **Banco de Dados:** Gerenciamento automático do banco de dados SQLite.

## Contribuição
Contribuições são bem-vindas! Siga os passos abaixo para contribuir:
1. Faça um fork do repositório.
2. Crie uma branch para sua feature:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça commit das suas alterações:
   ```bash
   git commit -m "Adicionei uma nova feature"
   ```
4. Envie para o repositório remoto:
   ```bash
   git push origin minha-feature
   ```
5. Abra um Pull Request.

## Licença
Este projeto é licenciado sob os direitos reservados © 2025 Gabriel Vilaça.

---
Desenvolvido por Gabriel Vilaça. Direitos Reservados © 2025.

