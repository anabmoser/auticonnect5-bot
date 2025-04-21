# AutiConnect Bot - Telegram Bot para Interação entre Autistas

Este bot do Telegram foi desenvolvido para facilitar a interação entre pessoas autistas jovens e adultas, com mediação de agentes de IA disponíveis 24/7 e supervisão de Auxiliares Terapêuticos (ATs).

## Funcionalidades

- **Registro de usuários** (autistas e ATs)
- **Perfis expandidos** com informações detalhadas sobre:
  - Idade e gênero
  - Contatos de emergência
  - Histórico acadêmico
  - Profissionais com quem já trabalhou
  - Interesses especiais
  - Gatilhos de ansiedade
  - Preferências de comunicação
- **Grupos temáticos** para interação entre autistas
- **Atividades estruturadas** (discussões, projetos, jogos)
- **Mediação por IA** disponível 24/7
- **Suporte individual** através de conversas privadas
- **Sistema de alertas** para intervenção profissional quando necessário

## Requisitos

- Python 3.7+
- python-telegram-bot v20.0+
- MongoDB
- Conta no Telegram
- Bot do Telegram (criado via BotFather)

## Configuração

1. Clone este repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Crie um arquivo `.env` baseado no exemplo `.env.example`:
   ```
   BOT_TOKEN=seu_token_do_telegram
   MONGO_URI=sua_uri_do_mongodb
   LLM_API_KEY=sua_chave_api_do_openai
   LLM_MODEL=gpt-4
   ALERT_THRESHOLD=70
   ```

## Implantação

### No Railway

1. Crie uma conta em [railway.app](https://railway.app/)
2. Clique em "New Project" > "Deploy from GitHub repo"
3. Conecte seu repositório GitHub com o código do bot
4. Adicione as variáveis de ambiente:
   - `BOT_TOKEN`: Token do seu bot do Telegram (obtido via BotFather)
   - `MONGO_URI`: URI de conexão do MongoDB
   - `LLM_API_KEY`: Chave da API do OpenAI para GPT-4
   - `LLM_MODEL`: Definido como "gpt-4"
   - `ALERT_THRESHOLD`: Valor entre 0-100, recomendado: 70
5. Adicione um banco de dados MongoDB clicando em "New" > "Database" > "MongoDB"
6. O bot será implantado automaticamente!

### No Replit

1. Crie uma conta em [replit.com](https://replit.com/)
2. Crie um novo repl com template Python
3. Faça upload dos arquivos do projeto
4. Adicione as variáveis de ambiente em "Secrets":
   - `BOT_TOKEN`: Token do seu bot do Telegram
   - `MONGO_URI`: URI de conexão do MongoDB
   - `LLM_API_KEY`: Chave da API do OpenAI
   - `LLM_MODEL`: Definido como "gpt-4"
   - `ALERT_THRESHOLD`: Valor entre 0-100, recomendado: 70
5. Clique em "Run" para iniciar o bot

## Uso

### Comandos para Todos os Usuários

- `/start` - Iniciar o bot e criar perfil
- `/ajuda` - Mostrar ajuda
- `/grupos` - Listar grupos disponíveis
- `/atividades` - Listar atividades programadas
- `/perfil` - Atualizar perfil

### Comandos Exclusivos para ATs

- `/criar_grupo` - Criar um novo grupo temático
- `/iniciar_atividade` - Iniciar uma nova atividade estruturada

## Estrutura do Projeto

- `main.py` - Arquivo principal do bot
- `requirements.txt` - Dependências do projeto
- `Procfile` - Configuração para deployment
- `.env.example` - Exemplo de configuração de variáveis de ambiente

## Mediação por IA

O bot utiliza agentes de IA para:

1. **Facilitar conversas em grupo**:
   - Manter a conversa animada
   - Garantir que todos participem
   - Mediar mal-entendidos

2. **Oferecer suporte individual**:
   - Detectar sinais de ansiedade
   - Fornecer estratégias de regulação emocional
   - Oferecer um espaço seguro para processamento

3. **Estruturar atividades**:
   - Guiar discussões temáticas
   - Facilitar projetos colaborativos
   - Organizar jogos sociais

4. **Alertar profissionais**:
   - Detectar situações que requerem intervenção
   - Notificar ATs quando necessário

## Notas de Implementação

Esta versão do bot foi desenvolvida especificamente para compatibilidade com python-telegram-bot v20+, que utiliza padrões async/await e tem uma estrutura de importação diferente das versões anteriores.

Para o MVP, o bot simula a criação de grupos e atividades sem criar grupos reais no Telegram. Em uma implementação completa, o bot criaria e gerenciaria grupos reais do Telegram.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença

Este projeto está licenciado sob a licença MIT.
