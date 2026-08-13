# Deltatune

Deltatune é um jogo web diário de adivinhação musical inspirado no universo de **DELTARUNE**.

O jogador começa ouvindo apenas **0,5 segundo** de uma música e precisa descobrir seu título. Cada resposta incorreta ou tentativa pulada consome um coração e libera um trecho maior:

```text
0,5s → 1s → 2s → 4s → 8s → 16s
```

O projeto está sendo desenvolvido para fins de estudo e portfólio, reunindo frontend e backend em uma aplicação full-stack.

> O Deltatune é um projeto de fã não oficial, gratuito e sem fins lucrativos. Não possui vínculo ou aprovação de Toby Fox, Royal Sciences LLC ou Materia Music.

## Demonstração

A versão provisória do frontend está publicada na Vercel:

**Aplicação:** https://deltatune.vercel.app/

O backend ainda está em desenvolvimento e, por enquanto, precisa ser executado localmente para que o desafio seja carregado e os palpites sejam validados.

## Funcionalidades implementadas

### Jogo

* Desafio musical atualizado diariamente;
* Seis tentativas representadas por corações;
* Trechos progressivos de 0,5 a 16 segundos;
* Reprodução controlada do trecho liberado;
* Controle de volume com preferência salva no navegador;
* Envio e validação de palpites;
* Opção de pular uma tentativa;
* Autocomplete personalizado para títulos de músicas;
* Indicação visual de respostas corretas, incorretas e puladas;
* Resultado final da partida;
* Persistência do progresso no `localStorage`;
* Contador regressivo para o próximo desafio;
* Tutorial de como jogar.

### Frontend

* Interface responsiva para computadores e dispositivos móveis;
* Identidade visual inspirada nos menus de DELTARUNE;
* Navegação entre páginas com React Router;
* Tratamento dos estados de carregamento e erro;
* Integração com a API por meio de uma camada de serviço;
* Armazenamento de preferências e progresso no navegador.

### Backend

* API criada com FastAPI;
* Endpoint de verificação de saúde;
* Endpoint público do desafio diário;
* Rotação automática baseada na data;
* Renovação à meia-noite no horário de Brasília;
* Validação de palpites no servidor;
* Suporte a títulos alternativos;
* Normalização de maiúsculas, minúsculas e espaços;
* Proteção da resposta correta em palpites incorretos;
* CORS configurado para o ambiente local;
* Documentação interativa com Swagger.

## Tecnologias

### Frontend

* React
* TypeScript
* Vite
* React Router
* React Icons
* CSS

### Backend

* Python
* FastAPI
* Pydantic
* Uvicorn
* tzdata

### Ferramentas

* Git
* GitHub
* ESLint
* Vercel
* Swagger UI

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
│   │   ├── data/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── requirements.txt
│   └── .gitignore
│
└── README.md
```

## Endpoints atuais

| Método | Endpoint                  | Descrição                                                |
| ------ | ------------------------- | -------------------------------------------------------- |
| `GET`  | `/health`                 | Verifica se a API está funcionando                       |
| `GET`  | `/challenges/daily`       | Retorna os dados públicos do desafio atual               |
| `POST` | `/challenges/daily/guess` | Valida um palpite sem revelar a resposta em caso de erro |

Exemplo de resposta do desafio diário:

```json
{
  "challengeId": "003",
  "challengeNumber": 3,
  "attemptDurations": [0.5, 1, 2, 4, 8, 16],
  "nextResetAt": "2026-08-14T00:00:00-03:00"
}
```

Exemplo de envio de um palpite:

```json
{
  "challengeId": "003",
  "answer": "Field of Hopes and Dreams"
}
```

## Executando localmente

### Pré-requisitos

Antes de começar, instale:

* Node.js;
* npm;
* Python;
* Git.

### 1. Clonar o repositório

```bash
git clone https://github.com/RafaDavila/Deltatune.git
cd Deltatune
```

### 2. Executar o backend

No Windows PowerShell:

```powershell
cd backend
python -m venv .venv
& "$PWD\.venv\Scripts\Activate.ps1"
python -m pip install -r requirements.txt
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

## Verificações do frontend

Dentro de `frontend`:

```bash
npm run lint
npm run build
```

## Próximas etapas

* Fazer o backend controlar as tentativas da partida;
* Revelar a resposta com segurança após uma derrota;
* Implementar três rodadas musicais por desafio diário;
* Adicionar PostgreSQL;
* Configurar SQLAlchemy e Alembic;
* Criar o catálogo completo de músicas;
* Evitar repetições recentes na seleção diária;
* Criar placar final das três rodadas;
* Gerar resultado compartilhável;
* Publicar o backend;
* Conectar a versão da Vercel à API publicada;
* Adicionar testes automatizados;
* Implementar futuramente o modo “Adivinhe o personagem”.

## Direitos autorais

DELTARUNE, seus personagens e sua trilha sonora pertencem aos seus respectivos titulares.

As músicas de DELTARUNE foram compostas por **Toby Fox**, com direitos administrados pela **Materia Music Publishing**.

Este projeto não reivindica propriedade sobre DELTARUNE ou sua trilha sonora. Uma solicitação de autorização para o uso das gravações originais no formato proposto foi enviada à Materia Music. A inclusão pública de um catálogo musical definitivo dependerá das orientações ou permissões recebidas.

Durante o desenvolvimento, os arquivos de áudio devem ser tratados como recursos provisórios de teste e não como conteúdo licenciado para distribuição pública.

## Autor

Desenvolvido por **Rafael Davila**.

* GitHub: [RafaDavila](https://github.com/RafaDavila)
* Repositório: [Deltatune](https://github.com/RafaDavila/Deltatune)

---

Este projeto está em desenvolvimento.
