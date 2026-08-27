# Deltatune

Deltatune é um jogo web de adivinhação musical inspirado no universo de **DELTARUNE**. A aplicação possui um desafio diário e um modo infinito, com sessões persistentes, progressão de trechos e validação segura das respostas pelo backend.

O jogador começa ouvindo apenas **0,5 segundo** de uma faixa. Cada resposta incorreta ou tentativa pulada consome um coração e libera um trecho maior:

```text
0,5s → 1s → 2s → 4s → 8s → 16s
```

O projeto foi desenvolvido para estudo e portfólio, reunindo frontend, backend, banco de dados, processamento de áudio, testes automatizados, containers e deploy em uma aplicação full stack.

> O Deltatune é um projeto de fã não oficial, gratuito e sem fins lucrativos. Não possui vínculo ou aprovação de Toby Fox, Royal Sciences LLC ou Materia Music.

## Demonstração

- **Aplicação:** https://deltatune.vercel.app
- **API:** https://deltatune.onrender.com
- **Documentação Swagger:** https://deltatune.onrender.com/docs

O frontend está hospedado na Vercel, a API FastAPI no Render e o PostgreSQL no Neon.

> A instância gratuita do Render pode entrar em suspensão após um período sem acessos. Por isso, a primeira requisição pode levar alguns segundos para carregar.

## Modos de jogo

### Desafio diário

- Música atualizada diariamente;
- mesma faixa para todos os jogadores durante o dia;
- contador regressivo para a próxima música;
- sessão recuperada automaticamente após atualizar a página;
- resposta revelada somente após vitória ou fim das tentativas.

### Modo infinito

- Rodadas consecutivas sem esperar o próximo desafio diário;
- seleção aleatória entre as músicas disponíveis;
- nenhuma música se repete antes de todas serem utilizadas no ciclo;
- início automático de um novo ciclo após esgotar o catálogo;
- sequência de acertos mantida entre rodadas;
- sequência zerada após uma derrota;
- recorde pessoal salvo no navegador;
- nova sessão iniciada na rodada 001 ao recomeçar;
- recuperação da rodada, das tentativas e da sequência após recarregar a página.

## Funcionalidades implementadas

### Jogo

- Catálogo com 58 músicas cadastradas;
- seis tentativas representadas por corações;
- trechos progressivos de 0,5 a 16 segundos;
- reprodução controlada conforme o trecho liberado;
- controle de volume com preferência salva no navegador;
- envio e validação de palpites pelo backend;
- bloqueio de palpites repetidos sem consumo de vidas;
- opção de pular uma tentativa;
- autocomplete personalizado carregado pela API;
- suporte a títulos alternativos;
- indicação visual de respostas corretas, incorretas e puladas;
- resultado final com revelação da resposta;
- tutorial de como jogar;
- recuperação de partidas em andamento ou finalizadas.

### Sessões e progresso

- Criação de sessões identificadas por UUID;
- tentativas persistidas no PostgreSQL;
- controle de vidas realizado pelo backend;
- bloqueio de ações após o encerramento de uma rodada;
- validação do vínculo entre sessão e rodada;
- título e identificadores internos protegidos durante a partida;
- armazenamento apenas dos identificadores necessários no `localStorage`;
- recorde do Modo Infinito armazenado localmente enquanto não há autenticação.

### Áudio

- Associação entre músicas e identificadores neutros como `track-001`;
- arquivos limitados a 16 segundos;
- normalização de volume;
- conversão automática para MP3;
- processamento em lote com Python e FFmpeg;
- rotas dedicadas ao áudio diário e ao áudio de cada rodada infinita;
- validação segura do caminho dos arquivos;
- nome da resposta protegido na URL.

### Frontend

- Interface responsiva para computadores e dispositivos móveis;
- identidade visual inspirada nos menus de DELTARUNE;
- navegação com React Router;
- páginas separadas para o desafio diário e o Modo Infinito;
- componentes reutilizáveis de áudio, tentativas, vidas, tutorial e resultado;
- estados de carregamento, erro e indisponibilidade;
- integração com a API por meio de uma camada de serviços;
- autocomplete acessível com suporte a teclado;
- preferências e progresso local armazenados no navegador;
- testes de componentes e páginas com Vitest e React Testing Library;
- deploy contínuo na Vercel.

### Backend

- API REST criada com FastAPI;
- catálogo e sessões armazenados no PostgreSQL;
- SQLAlchemy como ORM;
- Alembic para controle de migrations;
- seed reutilizável para carregar e atualizar o catálogo;
- rotação diária baseada na data;
- renovação à meia-noite no horário de Brasília;
- seleção aleatória e ciclos sem repetição no Modo Infinito;
- validação segura de palpites no servidor;
- normalização de maiúsculas, minúsculas e espaços;
- proteção da resposta correta durante a partida;
- entrega dinâmica dos arquivos de áudio;
- CORS configurável por variável de ambiente;
- endpoint de verificação de saúde;
- documentação interativa com Swagger;
- testes automatizados com Pytest;
- deploy em container Docker no Render.

## Tecnologias

### Frontend

- React;
- TypeScript;
- Vite;
- React Router;
- React Icons;
- CSS;
- ESLint;
- Vitest;
- React Testing Library;
- jest-dom;
- jsdom;
- Vercel.

### Backend

- Python;
- FastAPI;
- Pydantic;
- Uvicorn;
- SQLAlchemy;
- Alembic;
- Psycopg;
- PostgreSQL;
- Pytest;
- FFmpeg;
- Docker;
- Render;
- Neon.

### Ferramentas

- Git e GitHub;
- Visual Studio Code;
- Swagger UI;
- Docker Desktop.

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
    └── Trechos de áudio
        Imagem Docker
```

O frontend mantém apenas identificadores de sessão e preferências no navegador. As regras do jogo, tentativas, vidas, respostas e sequências são validadas ou persistidas pelo backend.

## Endpoints

### Gerais e desafio diário

| Método | Endpoint | Descrição |
| --- | --- | --- |
| `GET` | `/health` | Verifica se a API está funcionando |
| `GET` | `/songs` | Retorna o catálogo disponível |
| `GET` | `/challenges/daily` | Retorna os dados públicos do desafio atual |
| `GET` | `/challenges/daily/audio` | Entrega o áudio do desafio atual |
| `POST` | `/challenges/daily/start` | Cria uma sessão para o desafio diário |
| `GET` | `/challenges/daily/session/{session_id}` | Recupera uma partida diária |
| `POST` | `/challenges/daily/guess` | Valida um palpite diário |
| `POST` | `/challenges/daily/skip` | Registra uma tentativa pulada |

### Modo Infinito

| Método | Endpoint | Descrição |
| --- | --- | --- |
| `POST` | `/infinite/start` | Cria uma sessão e a primeira rodada |
| `GET` | `/infinite/{run_id}` | Recupera a rodada atual da sessão |
| `GET` | `/infinite/{run_id}/rounds/{round_id}/audio` | Entrega o áudio da rodada |
| `POST` | `/infinite/guess` | Valida um palpite da rodada |
| `POST` | `/infinite/skip` | Registra uma tentativa pulada |
| `POST` | `/infinite/next` | Cria a próxima rodada após a atual terminar |

## Exemplos da API

### Desafio diário

```json
{
  "challengeId": "013",
  "challengeNumber": 13,
  "attemptDurations": [0.5, 1, 2, 4, 8, 16],
  "nextResetAt": "2026-08-24T00:00:00-03:00"
}
```

### Início do Modo Infinito

```json
{
  "runId": "c923ad32-42c3-4715-89b8-7795408ba64f",
  "roundId": "70fbd5df-daac-47c8-a783-286ae3cb60ac",
  "roundNumber": 1,
  "attemptDurations": [0.5, 1, 2, 4, 8, 16],
  "remainingLives": 6,
  "maximumAttempts": 6,
  "currentStreak": 0
}
```

### Envio de palpite infinito

```json
{
  "runId": "c923ad32-42c3-4715-89b8-7795408ba64f",
  "roundId": "70fbd5df-daac-47c8-a783-286ae3cb60ac",
  "answer": "Don't Forget"
}
```

## Testes e verificações

### Backend

O backend possui **36 testes automatizados** cobrindo, entre outros cenários:

- health check e catálogo;
- criação e recuperação de sessões;
- palpites corretos, incorretos e repetidos;
- normalização das respostas;
- tentativas puladas e encerramento das partidas;
- validação de sessões e rodadas;
- entrega segura dos áudios;
- sequência do Modo Infinito;
- criação da próxima rodada;
- ciclos completos sem repetição de músicas.

Dentro de `backend`:

```powershell
python -m pytest -v --tb=short
```

### Frontend

O frontend possui **4 testes automatizados** cobrindo:

- comportamento do modal diário;
- avanço e continuação no Modo Infinito;
- recuperação de uma sessão infinita;
- atualização e preservação do recorde.

Dentro de `frontend`:

```powershell
npm test
npm run lint
npm run build
```

## Variáveis de ambiente

### Backend

| Variável | Obrigatória em produção | Descrição |
| --- | ---: | --- |
| `DATABASE_URL` | Sim | Conexão com o PostgreSQL |
| `TEST_DATABASE_URL` | Não | Banco utilizado pelos testes |
| `CORS_ORIGINS` | Sim | Lista JSON de origens autorizadas |

### Frontend

| Variável | Obrigatória em produção | Descrição |
| --- | ---: | --- |
| `VITE_API_URL` | Sim | Endereço público da API |

## Deploy

A arquitetura publicada utiliza:

- Vercel para o frontend;
- Render para a API Docker;
- Neon para o PostgreSQL.

O Dockerfile executa migrations e seed automaticamente antes de iniciar o servidor.

A origem da Vercel deve ser informada em `CORS_ORIGINS` sem uma barra no final:

```json
["https://deltatune.vercel.app"]
```

A variável utilizada pelo frontend é:

```env
VITE_API_URL=https://deltatune.onrender.com
```


## Direitos autorais

DELTARUNE, seus personagens, nomes e trilha sonora pertencem aos seus respectivos titulares.

As músicas de DELTARUNE foram compostas por **Toby Fox**, com direitos administrados pela **Materia Music Publishing**.

Este projeto não reivindica propriedade sobre DELTARUNE ou sua trilha sonora. Uma solicitação de autorização para o uso das gravações originais foi enviada à Materia Music.

## Autor

Desenvolvido por **Rafael Davila**.

- GitHub: [RafaDavila](https://github.com/RafaDavila)
- Repositório: [Deltatune](https://github.com/RafaDavila/Deltatune)

---

Este projeto continua em desenvolvimento.
