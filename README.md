# Deltatune

Deltatune é um jogo web diário de adivinhação musical inspirado no universo de **DELTARUNE**.

O jogador começa ouvindo apenas **0,5 segundo** de uma faixa e precisa descobrir o título associado a ela. Cada resposta incorreta ou tentativa pulada consome um coração e libera um trecho maior:

```text
0,5s → 1s → 2s → 4s → 8s → 16s
```

O projeto foi desenvolvido para estudo e portfólio, reunindo frontend, backend, banco de dados, processamento de áudio, testes automatizados, containers e deploy em uma aplicação full stack.

> O Deltatune é um projeto de fã não oficial, gratuito e sem fins lucrativos. Não possui vínculo ou aprovação de Toby Fox, Royal Sciences LLC ou Materia Music.

## Demonstração

**Aplicação:** https://deltatune.vercel.app

**API:** https://deltatune.onrender.com

**Documentação Swagger:** https://deltatune.onrender.com/docs

O frontend está hospedado na Vercel, a API FastAPI no Render e o PostgreSQL no Neon.

> A instância gratuita do Render pode entrar em suspensão após um período sem acessos. Por isso, a primeira requisição pode levar alguns segundos para carregar.

## Funcionalidades implementadas

### Jogo

* Desafio musical atualizado diariamente;
* Catálogo inicial com 13 títulos selecionados do Capítulo 1;
* Seis tentativas representadas por corações;
* Trechos progressivos de 0,5 a 16 segundos;
* Reprodução controlada conforme o trecho liberado;
* Controle de volume com preferência salva no navegador;
* Envio e validação de palpites pelo backend;
* Opção de pular uma tentativa;
* Autocomplete personalizado carregado pela API;
* Suporte a títulos alternativos;
* Indicação visual de respostas corretas, incorretas e puladas;
* Animação visual ao acertar;
* Resultado final da partida;
* Contador regressivo para o próximo desafio;
* Tutorial de como jogar;
* Liberação do trecho completo ao finalizar a partida;
* Recuperação da partida após recarregar a página.

### Sessões e progresso

* Criação de uma sessão individual para cada jogador;
* Identificação da sessão por UUID;
* Tentativas persistidas no PostgreSQL;
* Recuperação de partidas em andamento ou finalizadas;
* Controle de vidas realizado pelo backend;
* Bloqueio de palpites após o encerramento da partida;
* Validação de sessões pertencentes ao desafio diário atual;
* Armazenamento apenas do identificador da sessão no `localStorage`.

### Áudio

* Associação entre músicas do catálogo e identificadores neutros como `track-001`;
* Arquivos limitados a 16 segundos;
* Normalização de volume;
* Conversão automática para MP3;
* Processamento em lote com Python e FFmpeg;
* Rota fixa para entrega do áudio diário;
* Nome da resposta protegido na URL do arquivo.


### Frontend

* Interface responsiva para computadores e dispositivos móveis;
* Identidade visual inspirada nos menus de DELTARUNE;
* Navegação entre páginas com React Router;
* Componentes de tutorial, resultado e informações;
* Estados de carregamento, erro e indisponibilidade;
* Integração com a API por meio de uma camada de serviços;
* Autocomplete acessível com suporte a teclado;
* Controle de volume com ícones;
* Preferências armazenadas no navegador;
* Deploy contínuo na Vercel.

### Backend

* API REST criada com FastAPI;
* Catálogo de músicas armazenado no PostgreSQL;
* Persistência de sessões e tentativas;
* SQLAlchemy como ORM;
* Alembic para controle de migrations;
* Seed reutilizável para carregar e atualizar o catálogo;
* Rotação diária baseada na data;
* Renovação à meia-noite no horário de Brasília;
* Validação segura de palpites no servidor;
* Normalização de maiúsculas, minúsculas e espaços;
* Proteção da resposta correta durante a partida;
* Entrega dinâmica do arquivo de áudio;
* CORS configurável por variável de ambiente;
* Endpoint de verificação de saúde;
* Documentação interativa com Swagger;
* Testes automatizados com Pytest;
* Deploy em container Docker no Render.

## Tecnologias

### Frontend

* React;
* TypeScript;
* Vite;
* React Router;
* React Icons;
* CSS;
* ESLint;
* Vercel.

### Backend

* Python;
* FastAPI;
* Pydantic;
* Uvicorn;
* SQLAlchemy;
* Alembic;
* Psycopg;
* PostgreSQL;
* Pytest;
* FFmpeg;
* Docker;
* Render;
* Neon.

### Ferramentas

* Git;
* GitHub;
* Visual Studio Code;
* Swagger UI;
* Docker Desktop.

## Arquitetura

```text
Navegador
    │
    ▼
Frontend React + TypeScript
Vercel
    │
    ▼
API FastAPI
Render
    │
    ├── PostgreSQL
    │   Neon
    │
    └── Trechos de áudio CC0
        Imagem Docker
```

## Estrutura do projeto

```text
Deltatune/
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.tsx
│   │   └── App.css
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── media/
│   │   └── audio/
│   ├── migrations/
│   │   └── versions/
│   ├── scripts/
│   │   ├── process_audio.py
│   │   └── seed_songs.py
│   ├── tests/
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .dockerignore
│   └── .env.example
│
└── README.md
```

## Endpoints

| Método | Endpoint                                 | Descrição                                    |
| ------ | ---------------------------------------- | -------------------------------------------- |
| `GET`  | `/health`                                | Verifica se a API está funcionando           |
| `GET`  | `/songs`                                 | Retorna o catálogo disponível                |
| `GET`  | `/challenges/daily`                      | Retorna os dados públicos do desafio atual   |
| `GET`  | `/challenges/daily/audio`                | Entrega o áudio relacionado ao desafio atual |
| `POST` | `/challenges/daily/start`                | Cria uma nova sessão de partida              |
| `GET`  | `/challenges/daily/session/{session_id}` | Recupera uma partida existente               |
| `POST` | `/challenges/daily/guess`                | Valida um palpite                            |
| `POST` | `/challenges/daily/skip`                 | Registra uma tentativa pulada                |

### Exemplo do desafio diário

```json
{
  "challengeId": "013",
  "challengeNumber": 13,
  "attemptDurations": [
    0.5,
    1,
    2,
    4,
    8,
    16
  ],
  "nextResetAt": "2026-08-24T00:00:00-03:00"
}
```

### Exemplo de envio de palpite

```json
{
  "sessionId": "2bef0a0a-1e26-4d85-b19c-373a52c33b36",
  "challengeId": "013",
  "answer": "Don't Forget"
}
```

### Exemplo de tentativa pulada

```json
{
  "sessionId": "2bef0a0a-1e26-4d85-b19c-373a52c33b36",
  "challengeId": "013"
}
```

## Executando localmente

### Pré-requisitos

Instale:

* Git;
* Node.js;
* npm;
* Python;
* PostgreSQL;
* FFmpeg, caso queira gerar novos trechos;
* Docker, opcionalmente.

### 1. Clonar o repositório

```bash
git clone https://github.com/RafaDavila/Deltatune.git
cd Deltatune
```

### 2. Configurar o backend

No Windows PowerShell:

```powershell
cd backend

python -m venv .venv

& ".\.venv\Scripts\Activate.ps1"

python -m pip install -r requirements.txt
```

Crie o `.env` a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Configure as variáveis:

```env
DATABASE_URL=postgresql+psycopg://postgres:SUA_SENHA@localhost:5432/deltatune
TEST_DATABASE_URL=postgresql+psycopg://postgres:SUA_SENHA@localhost:5432/deltatune_test
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

Crie os bancos `deltatune` e `deltatune_test` no PostgreSQL.

Execute as migrations e carregue o catálogo:

```powershell
alembic upgrade head
python -m scripts.seed_songs
```

Inicie a API:

```powershell
uvicorn app.main:app --reload --port 8000
```

A API estará disponível em:

```text
http://127.0.0.1:8000
```

Documentação interativa:

```text
http://127.0.0.1:8000/docs
```

### 3. Executar o frontend

Em outro terminal:

```powershell
cd frontend
npm install
npm run dev
```

A aplicação estará disponível em:

```text
http://localhost:5173
```

Na ausência de `VITE_API_URL`, o frontend utiliza por padrão:

```text
http://127.0.0.1:8000
```

## Processamento dos áudios

As músicas completas utilizadas como fonte devem ser colocadas em:

```text
backend/audio_sources/
```

Essa pasta é ignorada pelo Git.

Para gerar automaticamente os trechos:

```powershell
python .\backend\scripts\process_audio.py
```

Os arquivos processados serão criados em:

```text
backend/media/audio/
```

Cada faixa será:

* limitada a 16 segundos;
* normalizada;
* convertida para MP3;
* renomeada com um identificador neutro.

## Docker

Construa a imagem a partir da raiz:

```powershell
docker build `
  -t deltatune-backend `
  -f .\backend\Dockerfile `
  .\backend
```

O container executa automaticamente:

1. migrations do Alembic;
2. seed do catálogo;
3. inicialização do Uvicorn.

## Testes

O backend possui testes automatizados para:

* health check;
* catálogo e filtros;
* criação de sessão;
* recuperação de sessão;
* palpites corretos e incorretos;
* normalização das respostas;
* tentativas puladas;
* encerramento da partida;
* sessões inválidas;
* desafios expirados;
* entrega do áudio diário.

Dentro de `backend`:

```powershell
python -m pytest -v --tb=short
```

## Verificações do frontend

Dentro de `frontend`:

```powershell
npm run lint
npm run build
```

## Variáveis de ambiente

### Backend

| Variável            | Obrigatória em produção | Descrição                         |
| ------------------- | ----------------------: | --------------------------------- |
| `DATABASE_URL`      |                     Sim | Conexão com o PostgreSQL          |
| `TEST_DATABASE_URL` |                     Não | Banco utilizado pelos testes      |
| `CORS_ORIGINS`      |                     Sim | Lista JSON de origens autorizadas |

### Frontend

| Variável       | Obrigatória em produção | Descrição               |
| -------------- | ----------------------: | ----------------------- |
| `VITE_API_URL` |                     Sim | Endereço público da API |

## Deploy

A arquitetura publicada utiliza:

* Vercel para o frontend;
* Render para a API Docker;
* Neon para o PostgreSQL.

O Dockerfile executa migrations e seed automaticamente antes de iniciar o servidor.

A origem da Vercel deve ser informada no `CORS_ORIGINS` sem uma barra no final:

```json
["https://deltatune.vercel.app"]
```

A variável utilizada pelo frontend é:

```env
VITE_API_URL=https://deltatune.onrender.com
```

## Próximas etapas

* Implementar três rodadas musicais em cada desafio diário;
* Impedir repetições recentes na rotação;
* Criar um placar final para as três rodadas;
* Gerar resultado compartilhável;
* Melhorar a experiência durante o cold start do backend;
* Criar pipeline de integração contínua;
* Expandir o catálogo para outros capítulos;
* Implementar futuramente o modo “Adivinhe o personagem”;
* Avaliar autenticação e perfis de usuário.

## Direitos autorais

DELTARUNE, seus personagens, nomes e trilha sonora pertencem aos seus respectivos titulares.

As músicas de DELTARUNE foram compostas por **Toby Fox**, com direitos administrados pela **Materia Music Publishing**.

Este projeto não reivindica propriedade sobre DELTARUNE ou sua trilha sonora. Uma solicitação de autorização para o uso das gravações originais foi enviada à Materia Music.

A versão pública atual não distribui as gravações oficiais de DELTARUNE. Para permitir o funcionamento completo da aplicação enquanto a autorização não é recebida, são utilizadas faixas demonstrativas com licença CC0 associadas aos títulos do catálogo.

## Autor

Desenvolvido por **Rafael Davila**.

* GitHub: [RafaDavila](https://github.com/RafaDavila)
* Repositório: [Deltatune](https://github.com/RafaDavila/Deltatune)

---

Este projeto continua em desenvolvimento.
