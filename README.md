# Revisor de Conflitos entre ADRs

> Este projeto foi gerado automaticamente por IA e revisado por um agente automatizado, nao por uma pessoa. Leia o codigo antes de usar.

## Descrição

Ferramenta de linha de comando para revisar uma ADR proposta em relação a ADRs locais em Markdown. Ela envia a proposta e o contexto local a um modelo OpenAI e apresenta um parecer em português com resumo, conflitos potenciais, citações, impactos e perguntas de revisão.

## Objetivo

Apoiar a identificação de possíveis incompatibilidades entre uma nova decisão arquitetural e decisões já registradas localmente, mantendo no parecer o caminho da ADR relacionada e uma citação retornada pelo modelo.

## Como funciona

1. O CLI recebe o caminho de uma ADR proposta e o caminho de um diretório de ADRs.
2. A proposta é validada como um arquivo Markdown (`.md`) existente e não vazio.
3. O diretório é percorrido recursivamente para localizar arquivos Markdown. A própria proposta é excluída da lista de ADRs locais quando estiver dentro do diretório analisado.
4. Os documentos são ordenados pelo caminho, limitados a 20 ADRs locais e truncados em 12.000 caracteres por documento quando necessário. O truncamento recebe uma marcação visível.
5. A ferramenta monta um prompt com a ADR proposta e as ADRs locais, solicitando JSON válido com resumo, conflitos e perguntas de revisão.
6. O cliente OpenAI faz uma chamada pela API `responses.create`.
7. A resposta é decodificada como JSON e validada antes de ser renderizada no terminal.

O parecer inclui uma seção de conflitos potenciais. Quando a lista retornada estiver vazia, a saída informa que nenhum conflito potencial foi identificado. Também há uma seção de perguntas de revisão, mesmo quando nenhuma pergunta for sugerida.

## Arquitetura

O projeto está organizado no pacote `src/adr_conflict_reviewer/`:

- `src/adr_conflict_reviewer/__init__.py`: identifica o pacote e define sua versão.
- `src/adr_conflict_reviewer/__main__.py`: ponto de entrada para `python -m adr_conflict_reviewer`.
- `src/adr_conflict_reviewer/cli.py`: interpreta os argumentos posicionais, coordena a execução e apresenta erros esperados em português.
- `src/adr_conflict_reviewer/models.py`: define os modelos `AdrDocument`, `ConflictFinding` e `ReviewReport`.
- `src/adr_conflict_reviewer/repository.py`: valida caminhos, lê arquivos Markdown locais, aplica os limites de documentos e conteúdo e exclui a proposta da varredura local.
- `src/adr_conflict_reviewer/reviewer.py`: cria o cliente OpenAI a partir da configuração, monta o prompt, consulta o modelo e valida a resposta JSON.
- `src/adr_conflict_reviewer/renderer.py`: transforma um `ReviewReport` em texto para o terminal.
- `tests/conftest.py`: arquivo de suporte aos testes.
- `tests/test_cli.py`: testes do CLI.
- `tests/test_repository.py`: testes do carregamento de documentos locais.
- `tests/test_reviewer.py`: testes da revisão e do tratamento da resposta do modelo.
- `requirements.txt`: arquivo usado pelo comando de instalação de dependências.

## Tecnologias

- Python 3.11+.
- SDK Python `openai`, usado para criar o cliente `OpenAI` e consultar `responses.create`.
- `pydantic`, usado para validar os documentos, conflitos e pareceres.
- Biblioteca padrão do Python: `argparse`, `json`, `os`, `pathlib`, `sys` e `typing`.
- pytest, fornecido pelo ambiente de execução, para executar os testes.

## Instalação

Com Python 3.11+ disponível, instale as dependências do experimento:

```bash
python -m pip install -r requirements.txt
```

O pacote está em `src/` e o projeto não possui arquivo de instalação. Por isso, o diretório `src` precisa estar no `PYTHONPATH` ao executar o módulo.

## Configuração

A ferramenta lê as seguintes variáveis de ambiente, sem valores padrão:

- `OPENAI_API_KEY`: chave para criar o cliente OpenAI. Configure com `<sua-chave-aqui>`.
- `OPENAI_MODEL`: nome do modelo a ser usado na consulta. Configure com o nome do modelo disponível no ambiente.

Se qualquer uma dessas variáveis estiver ausente, a execução é encerrada com uma mensagem de erro em português.

## Uso

O comando recebe dois argumentos posicionais, nesta ordem:

1. caminho da ADR proposta em Markdown;
2. diretório que contém ADRs locais em Markdown.

Linux/macOS:

```bash
PYTHONPATH=src python -m adr_conflict_reviewer <caminho-da-adr-proposta.md> <diretorio-de-adrs>
```

Windows (PowerShell):

```powershell
$env:PYTHONPATH="src"; python -m adr_conflict_reviewer <caminho-da-adr-proposta.md> <diretorio-de-adrs>
```

A ADR proposta precisa ser um arquivo `.md` existente, legível e com conteúdo. O segundo argumento precisa apontar para um diretório existente. Arquivos locais com extensão `.md` são procurados recursivamente; arquivos com outras extensões não entram no contexto.

## Exemplos

Para revisar uma proposta localizada em um diretório de ADRs local, execute com os caminhos correspondentes ao seu ambiente.

Linux/macOS:

```bash
PYTHONPATH=src python -m adr_conflict_reviewer <caminho-da-adr-proposta.md> <diretorio-de-adrs>
```

Windows (PowerShell):

```powershell
$env:PYTHONPATH="src"; python -m adr_conflict_reviewer <caminho-da-adr-proposta.md> <diretorio-de-adrs>
```

A saída possui a seguinte estrutura:

```text
PARECER DE REVISÃO DE ADRs

Resumo
<resumo retornado pelo modelo>

Conflitos potenciais
<conflitos ou mensagem de ausência de conflitos>

Perguntas de revisão
<perguntas ou mensagem de ausência de perguntas>
```

Cada conflito exibido contém a ADR relacionada, a citação, a explicação e o impacto retornados no parecer validado.

## Testes

Execute os testes com:

```bash
python -m pytest
```

Os testes não acessam a rede. A interação com o cliente do modelo é dublada nos testes.

## Limitações

- Analisa somente arquivos locais com extensão `.md`.
- Não lê PDF, DOCX, repositórios remotos ou integrações com sistemas de gestão de ADR.
- A análise depende da resposta do modelo e os conflitos apresentados são potenciais; a decisão final exige revisão humana.
- São incluídas no máximo 20 ADRs locais no parecer.
- Cada documento é limitado a 12.000 caracteres, com uma marcação quando há truncamento.
- A ferramenta faz uma única consulta ao modelo por execução.
- Não há retentativas, streaming, persistência, indexação, busca semântica, embeddings ou processamento incremental.
- O modelo é instruído a citar literalmente ADRs locais, mas o código não verifica automaticamente se cada citação ocorre no arquivo de origem.
- O modelo é configurado exclusivamente pelas variáveis `OPENAI_API_KEY` e `OPENAI_MODEL`; não há seleção de modelo por argumento do CLI.

## O que foi aprendido

O experimento demonstra um fluxo pequeno de revisão assistida por modelo: carregar contexto local, restringir o tamanho do material enviado, solicitar uma estrutura JSON e validar essa estrutura antes da apresentação ao usuário. Também separa leitura de arquivos, consulta ao modelo e renderização, permitindo testar a revisão sem chamadas de rede.

## Possível aplicação na FOX

Pode servir como uma verificação inicial durante a preparação ou revisão de ADRs: uma ADR proposta é comparada ao diretório local de decisões do projeto, e o parecer pode orientar uma revisão humana com conflitos potenciais, impactos e perguntas a esclarecer.

## Status

O relatório de testes recebido informa que 9 de 9 testes coletados passaram (`passou: True`).
