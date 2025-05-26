
# 🎓 Skola2 - Sistema de Gestão Acadêmica

Skola2 é uma aplicação web desenvolvida em Python com o framework Flask, destinada à gestão acadêmica. Permite o gerenciamento eficiente de instituições, turmas, disciplinas, alunos, professores, avaliações e notas, através de uma interface web intuitiva.

## ✅ Funcionalidades

- ✅ Autenticação e gerenciamento de usuários.
- ✅ CRUD completo de Instituições, Turmas, Disciplinas, Alunos e Professores.
- ✅ Sistema de Avaliações e Lançamento de Notas.
- ✅ Cálculo automático de médias.
- ✅ Geração de templates e relatórios.
- ✅ Scripts auxiliares para automação e inicialização.

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.12, Flask
- **ORM**: SQLAlchemy
- **Autenticação**: Flask-Login
- **Templates**: Jinja2
- **Banco de Dados**: SQLite (padrão), compatível com PostgreSQL/MySQL
- **Outros**: Werkzeug, dotenv

## 🚀 Instalação

### 1. Clone o repositório:

```bash
git clone https://github.com/seuusuario/Skola2.git
cd Skola2
```

### 2. Crie e ative o ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências:

```bash
pip install -r requirements.txt
```

### 4. Configure o arquivo `.env`:

Crie o arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=uma_chave_muito_segura
DATABASE_URI=postgresql://user:senha@localhost:5432/skola_db
TEST_DATABASE_URI=postgresql://skolusera:SenhaSegura@localhost:5432/test_skola_db
SQLALCHEMY_DATABASE_URI=sqlite:///skola.db
```


### 5. Execute o seed de dados:

```bash
python seed.py
```

Isso criará as tabelas e adicionará usuários e dados iniciais.

### 6. Inicie a aplicação:

```bash
flask run
```

ou com o script:

```bash
bash start.sh
```

Acesse: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 👤 Usuário padrão para acesso

- Esta no script de inserçao de usuarios teste 


## 📂 Estrutura do Projeto

```
Skola2/
├── app/
│   ├── models.py
│   ├── routes/
│   ├── templates/
│   ├── static/
│   ├── forms.py
│   ├── config.py
│   └── extensions.py
├── run.py
├── seed.py
├── requirements.txt
├── start.sh
├── .env
└── .gitignore
```

## ✅ Scripts Úteis

- `add_test_users.py` — adiciona usuários de teste.
- `gerar_templates.py` — gera automaticamente templates de avaliação.
- `start.sh` — script shell para inicialização rápida.

## 💡 Melhorias Futuras

- ✅ Migração para Flask-Migrate.
- ✅ Implementação de testes automatizados.
- ✅ Adição de autenticação OAuth2.
- ✅ Implementação de Docker e docker-compose.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🤝 Contribuindo

Contribuições são bem-vindas!  
Abra uma issue para sugerir melhorias ou reportar bugs.

## 📞 Contato

Em caso de dúvidas ou sugestões, entre em contato via:  
professor@manoelmoraes.pro.br
