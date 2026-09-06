# Infra CLI

**CLI para automação, diagnóstico e monitoramento básico de servidores Linux via SSH.**

O **Infra CLI** é uma ferramenta desenvolvida em Python para automatizar operações básicas de infraestrutura Linux.

A aplicação permite centralizar a configuração de servidores, estabelecer conexões SSH seguras, coletar métricas de CPU, memória e disco, avaliar a saúde dos hosts, gerar relatórios em JSON e HTML e enviar alertas por webhook.

O projeto foi desenvolvido com foco em práticas de engenharia de software aplicadas à infraestrutura, incluindo **segurança SSH, separação de responsabilidades, tratamento de falhas, testes automatizados e integração contínua**.

---

## Sobre o projeto

Em ambientes com múltiplos servidores, tarefas como verificar disponibilidade, consultar recursos do sistema e identificar condições críticas podem se tornar repetitivas quando realizadas manualmente.

O Infra CLI automatiza esse processo através de uma interface de linha de comando.

O operador fornece uma configuração contendo os servidores que devem ser monitorados e pode executar operações como:

```bash
python -m infra_cli.cli healthcheck
```
A aplicação então:

1. carrega a configuração;
2. identifica os servidores;
3. estabelece as conexões SSH;
4. executa comandos remotamente;
5. coleta as métricas;
6. avalia as condições de saúde;
7. apresenta os resultados;
8. gera relatórios;
9. pode disparar alertas quando necessário.

Uma característica importante é o tratamento individual de falhas. A indisponibilidade de um servidor não deve interromper o processamento dos demais hosts.

---

## Objetivo

O objetivo do projeto é aplicar conhecimentos de **Python, Linux, SSH, redes, automação, observabilidade, segurança, testes e CI/CD** na construção de uma ferramenta de infraestrutura organizada e evolutiva.

O projeto busca demonstrar a evolução de scripts isolados para uma aplicação com:

* arquitetura modular;
* configuração externa;
* interface CLI;
* comunicação SSH;
* coleta de métricas;
* regras de saúde;
* geração de relatórios;
* alertas;
* testes automatizados;
* tratamento de erros;
* integração contínua.

---

# Arquitetura

O fluxo principal da aplicação pode ser representado da seguinte forma:

```text
Usuário
                             │
                             ▼
                       ┌───────────┐
                       │ Infra CLI │
                       └─────┬─────┘
                             │
             ┌───────────────┼────────────────┐
             │               │                │
             ▼               ▼                ▼
       Configuração          SSH          Healthcheck
             │               │                │
             │               ▼                ▼
             │        Servidores Linux   Regras de saúde
             │               │                │
             │        ┌──────┼──────┐         │
             │        ▼      ▼      ▼         │
             │       CPU   Memória  Disco      │
             │        │      │      │         │
             └────────┴──────┴──────┘         │
                             │                │
                             ▼                ▼
                         Métricas       Status de saúde
                             │                │
                     ┌───────┴───────┐        │
                     ▼               ▼        ▼
                  Relatórios       Alertas  Webhook
                  JSON / HTML
                     │               │
                     └───────┬───────┘
                             ▼
                           Testes
                             │
                             ▼
                      GitHub Actions
```
### Fluxo de execução

```text
hosts.yaml
    │
    ▼
Configuração
    │
    ▼
Conexão SSH
    │
    ▼
Coleta de métricas
    │
    ├── CPU
    ├── Memória
    └── Disco
    │
    ▼
Regras de saúde
    │
    ▼
Resultado
    │
    ├───────────────┐
    ▼               ▼
Relatório         Alertas
JSON / HTML       Webhook
```
---

# Funcionalidades

Atualmente, o projeto possui:

* configuração de servidores através de YAML;
* interface de linha de comando;
* comunicação SSH com servidores Linux;
* validação segura de hosts SSH;
* execução remota de comandos;
* coleta de utilização de CPU;
* coleta de utilização de memória;
* coleta de utilização de disco;
* avaliação das métricas através de regras de saúde;
* classificação dos resultados;
* tratamento individual de erros;
* geração de relatório JSON;
* geração de relatório HTML;
* templates HTML utilizando Jinja2;
* suporte a alertas por webhook;
* testes automatizados com pytest;
* integração contínua através de GitHub Actions.

---

# Tecnologias

## Linguagem

* Python 3.12

## Bibliotecas

| Tecnologia | Utilização                  |
| ---------- | --------------------------- |
| Python     | Linguagem principal         |
| Click      | Interface CLI               |
| Paramiko   | Comunicação SSH             |
| PyYAML     | Configuração YAML           |
| Jinja2     | Templates e relatórios HTML |
| Requests   | Comunicação HTTP            |
| pytest     | Testes automatizados        |

## Ferramentas

* Git;
* GitHub;
* GitHub Actions;
* Linux;
* SSH.

O projeto evita adicionar tecnologias apenas para aumentar a lista de ferramentas. Cada dependência possui uma função específica dentro da aplicação.

---

# Estrutura do projeto

A estrutura atual do projeto é:

```text
infra-cli/
│
├── hosts.yaml
│
├── pyproject.toml
│
├── reports/
│   ├── health-report.html
│   └── health-report.json
│
├── src/
│   ├── infra_cli/
│   │   ├── __init__.py
│   │   ├── alerts.py
│   │   ├── cli.py
│   │   ├── config.py
│   │   ├── healthcheck.py
│   │   ├── health_rules.py
│   │   ├── metrics.py
│   │   ├── report.py
│   │   ├── ssh.py
│   │   └── webhook.py
│   │
│   └── infra_cli.egg-info/
│
├── templates/
│   └── report.html
│
├── tests/
│   ├── __init__.py
│   ├── test_alerts.py
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_healthcheck.py
│   ├── test_health_rules.py
│   ├── test_metrics.py
│   ├── test_report.py
│   ├── test_ssh.py
│   └── test_webhook.py
│
├── test_healthcheck.py
└── test_ssh_manual.py
```
> `__pycache__/` e arquivos `.pyc` são gerados automaticamente pelo Python e não fazem parte da aplicação. Da mesma forma, `infra_cli.egg-info/` é um artefato gerado durante a instalação/build do pacote e pode ser excluído do versionamento.

## Responsabilidades dos módulos

### `cli.py`

Implementa a interface de linha de comando da aplicação.

É o ponto de entrada para as operações disponibilizadas ao usuário.

### `config.py`

Responsável pelo carregamento e processamento da configuração dos servidores.

### `ssh.py`

Centraliza a comunicação SSH com os servidores Linux.

### `metrics.py`

Responsável pela coleta e interpretação das métricas de infraestrutura.

Atualmente são trabalhadas métricas de:

* CPU;
* memória;
* disco.

### `health_rules.py`

Contém as regras utilizadas para determinar se os valores coletados estão dentro das condições esperadas.

### `healthcheck.py`

Responsável por orquestrar o processo de healthcheck.

Integra:

```text
Configuração
     ↓
SSH
     ↓
Métricas
     ↓
Regras
     ↓
Resultado
```
### `report.py`

Responsável pela geração dos relatórios.

O projeto possui suporte aos formatos:

* JSON;
* HTML.

### `alerts.py`

Responsável pela lógica relacionada aos alertas.

### `webhook.py`

Responsável pela comunicação HTTP com o endpoint de webhook.

### `templates/report.html`

Template utilizado para geração do relatório HTML.

---

# Requisitos

Para executar o projeto, é necessário:

* Python 3.12;
* Git;
* acesso SSH aos servidores Linux;
* chave SSH configurada;
* servidores configurados no arquivo `hosts.yaml`.

O projeto foi desenvolvido e testado em ambiente Linux.

---

# Instalação

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
```
Entre no diretório:

```bash
cd infra-cli
```
Crie o ambiente virtual:

```bash
python3 -m venv .venv
```
Ative o ambiente virtual:

```bash
source .venv/bin/activate
```
Atualize o `pip`:

```bash
python -m pip install --upgrade pip
```
Instale o projeto:

```bash
pip install -e .
```
Verifique a CLI:

```bash
python -m infra_cli.cli --help
```
---

# Configuração

Os servidores são definidos no arquivo:

```text
hosts.yaml
```
Um exemplo de configuração:

```yaml
servers:
  - name: server01
    host: 192.168.1.101
    username: usuario

  - name: server02
    host: 192.168.1.102
    username: usuario
```
A configuração externa possui algumas vantagens:

* evita hardcode de servidores no código;
* facilita manutenção;
* permite adicionar novos hosts sem modificar a aplicação;
* separa infraestrutura da lógica da aplicação.

---

# Uso

A aplicação pode ser executada através do módulo Python:

```bash
python -m infra_cli.cli
```
Para consultar os comandos disponíveis:

```bash
python -m infra_cli.cli --help
```
---

## Listar hosts

O comando de listagem permite consultar os servidores configurados:

```bash
python -m infra_cli.cli hosts
```
Essa operação é útil para validar a configuração antes de executar operações sobre a infraestrutura.

---

## Healthcheck

O healthcheck é uma das principais funcionalidades da aplicação:

```bash
python -m infra_cli.cli healthcheck
```
O comando realiza a coleta das métricas dos servidores configurados e avalia seus respectivos estados.

Um resultado pode ser apresentado de forma semelhante a:

```text
Servidor: server01
----------------------------------------
CPU:      14.19% [OK]
Memória:  15.70% [OK]
Disco:    34.00% [OK]
```
Quando um servidor não pode ser acessado:

```text
Servidor: server01
----------------------------------------
Status: CONNECTION_ERROR
ERRO: Timeout ao conectar ao host
```
O erro é associado ao servidor específico, permitindo que os demais hosts continuem sendo processados.

---

# Relatório JSON

O projeto gera um relatório estruturado em JSON:

```text
reports/health-report.json
```
O JSON é destinado principalmente a consumo automatizado.

Exemplo conceitual:

```json
{
  "server01": {
    "status": "OK",
    "cpu": 14.19,
    "memory": 15.70,
    "disk": 34.00
  }
}
```
Esse formato permite futuras integrações com:

* scripts;
* APIs;
* pipelines;
* ferramentas de monitoramento;
* sistemas de automação.

---

# Relatório HTML

Também é gerado um relatório destinado à visualização humana:

```text
reports/health-report.html
```
A geração utiliza um template localizado em:

```text
templates/report.html
```
A utilização de templates permite separar os dados da lógica de apresentação.

O fluxo é:

```text
Healthcheck
     │
     ▼
Dados
     │
     ▼
report.py
     │
     ▼
templates/report.html
     │
     ▼
health-report.html
```
---

# SSH Test

A comunicação SSH pode ser validada antes de operações mais completas.

O projeto também possui um teste manual:

```text
test_ssh_manual.py
```
Esse teste é destinado à validação prática da comunicação com o ambiente de infraestrutura.

Já os testes automatizados utilizam mocks para evitar dependência de servidores SSH reais.

---

# Alertas

O Infra CLI possui suporte a alertas através de webhook.

O fluxo conceitual é:

```text
Healthcheck
     │
     ▼
Avaliação
     │
     ▼
Condição crítica?
     │
    Sim
     │
     ▼
Alerta
     │
     ▼
Webhook
```
A comunicação HTTP é isolada no módulo:

```text
src/infra_cli/webhook.py
```
Enquanto a lógica de alertas está em:

```text
src/infra_cli/alerts.py
```
Essa separação facilita testes e futuras integrações com diferentes serviços.

---

# Testes

O projeto utiliza **pytest** para testes automatizados.

A suíte está localizada em:

```text
tests/
```
Para executar todos os testes:

```bash
pytest -v
```
Para executar um módulo específico:

```bash
pytest -v tests/test_metrics.py
```
## Cobertura dos testes

A suíte contempla diferentes componentes:

```text
tests/
├── test_alerts.py
├── test_cli.py
├── test_config.py
├── test_healthcheck.py
├── test_health_rules.py
├── test_metrics.py
├── test_report.py
├── test_ssh.py
└── test_webhook.py
```
Os testes verificam tanto cenários de funcionamento normal quanto situações de erro.

Entre os cenários estão:

* processamento de métricas;
* dados insuficientes;
* valores inválidos;
* regras de saúde;
* falhas de conexão;
* comportamento do healthcheck;
* geração de relatórios;
* alertas;
* comunicação via webhook;
* comportamento da CLI.

---

# CI/CD

O projeto utiliza **GitHub Actions** para integração contínua.

O objetivo do pipeline é garantir que alterações submetidas ao repositório sejam verificadas automaticamente.

Fluxo esperado:

```text
Push / Pull Request
        │
        ▼
GitHub Actions
        │
        ▼
Configuração do Python
        │
        ▼
Instalação das dependências
        │
        ▼
Instalação do projeto
        │
        ▼
Execução do pytest
        │
        ▼
      PASS / FAIL
```
Dessa forma, os testes não dependem exclusivamente da execução manual pelo desenvolvedor.

---

# Segurança

Segurança é uma preocupação fundamental do projeto.

## Credenciais

Informações sensíveis não devem ser armazenadas no código-fonte.

O repositório não deve conter:

* senhas;
* chaves privadas SSH;
* tokens;
* credenciais;
* secrets de webhook.

---

## Segurança SSH

A aplicação utiliza uma política SSH restritiva.

Os hosts conhecidos são carregados através das chaves conhecidas do sistema:

```python
self.client.load_system_host_keys()
```
E hosts desconhecidos são rejeitados:

```python
self.client.set_missing_host_key_policy(
    paramiko.RejectPolicy()
)
```
O projeto **não utiliza `AutoAddPolicy()`**.

Essa é uma decisão deliberada de segurança.

A aplicação não deve aceitar automaticamente a chave de um host que ainda não tenha sido previamente validado.

Isso evita transformar conveniência em confiança automática.

---

## Timeouts

As conexões SSH utilizam timeout.

Isso impede que uma conexão indisponível permaneça bloqueada indefinidamente e ajuda a preservar o comportamento da aplicação quando existem múltiplos hosts.

---

## Separação entre código e infraestrutura

A configuração dos servidores fica fora da lógica Python:

```text
Código
   │
   └── src/infra_cli/

Infraestrutura
   │
   └── hosts.yaml
```
Essa separação facilita manutenção e reduz a necessidade de modificar código para alterar o ambiente monitorado.

---

# Tratamento de falhas

Ambientes de infraestrutura estão sujeitos a falhas parciais.

Por isso, o Infra CLI foi desenvolvido para tratar cada servidor individualmente.

Por exemplo:

```text
server01 → OK
server02 → CRITICAL
server03 → OK
server04 → CONNECTION_ERROR
```
O erro de `server04` não deve impedir o processamento dos demais.

## Falhas consideradas

O projeto trata cenários como:

* timeout SSH;
* falha de conexão;
* falha de autenticação;
* host indisponível;
* dados inválidos;
* dados insuficientes;
* erro na execução de comandos;
* respostas inesperadas;
* falhas de comunicação com webhook.

O objetivo é evitar que uma falha localizada provoque a interrupção completa da operação.

---

# Limitações

Apesar de funcional, o projeto possui limitações conhecidas.

Atualmente:

* a comunicação com os servidores depende de SSH;
* os hosts precisam estar previamente configurados;
* as métricas coletadas são limitadas principalmente a CPU, memória e disco;
* não existe armazenamento histórico permanente das métricas;
* os relatórios são gerados sob demanda;
* o webhook depende de um endpoint externo;
* o projeto não possui um dashboard de observabilidade permanente;
* não substitui plataformas completas de monitoramento.

Essas limitações fazem parte do escopo atual.

O objetivo é construir uma base de automação de infraestrutura sólida e evolutiva.

---

# Decisões técnicas

## Uso do Paramiko

O **Paramiko** foi escolhido para implementar a comunicação SSH programaticamente.

Isso permite que a aplicação:

* estabeleça conexões;
* execute comandos remotos;
* receba resultados;
* trate erros de comunicação.

---

## Uso de YAML

A configuração dos hosts foi externalizada para YAML.

Essa decisão reduz o acoplamento entre código e infraestrutura.

---

## Política SSH restritiva

Foi escolhida uma política baseada em hosts conhecidos:

```python
load_system_host_keys()
RejectPolicy()
```
Em vez de:

```python
AutoAddPolicy()
```
A escolha prioriza segurança e validação explícita da identidade dos servidores.

---

## Separação entre coleta e avaliação

A coleta de métricas e a avaliação de saúde são responsabilidades diferentes.

```text
metrics.py
    │
    ▼
Dados
    │
    ▼
health_rules.py
    │
    ▼
Avaliação
```
Isso permite modificar as regras de saúde sem precisar reescrever a lógica de coleta.

---

## Separação entre relatório e lógica

A geração de dados e a apresentação dos resultados são separadas.

O Python produz os dados enquanto o template HTML controla a apresentação:

```text
Python
  │
  ▼
Dados
  │
  ▼
Jinja2
  │
  ▼
HTML
```
---

## Tratamento individual de servidores

O healthcheck não considera todos os servidores como uma única operação indivisível.

Cada host possui seu próprio resultado.

Essa decisão representa melhor o comportamento esperado em ambientes distribuídos.

---

## JSON e HTML

Foram escolhidos dois formatos de relatório com objetivos diferentes.

### JSON

Prioriza:

* automação;
* integração;
* processamento por software.

### HTML

Prioriza:

* visualização;
* leitura humana;
* compartilhamento.

---

## Testes isolados

Os testes utilizam mocks quando uma funcionalidade depende de recursos externos.

Isso permite testar a lógica da aplicação sem exigir uma conexão SSH real para cada execução.

---

## CI/CD

GitHub Actions foi utilizado para automatizar a execução dos testes.

Assim, o processo de validação deixa de depender apenas da execução manual.

---

# Princípios de engenharia

O desenvolvimento do projeto segue alguns princípios importantes.

### Separação de responsabilidades

Cada módulo possui uma responsabilidade específica.

### Segurança por padrão

Hosts SSH desconhecidos não são aceitos automaticamente.

### Configuração externa

A infraestrutura é separada da lógica da aplicação.

### Tratamento explícito de erros

Falhas são capturadas e representadas de forma controlada.

### Testabilidade

Os componentes são desenvolvidos de forma que possam ser testados isoladamente.

### Automação

Operações repetitivas são automatizadas através da CLI.

### Evolução incremental

Novas funcionalidades são adicionadas progressivamente sem abandonar a estrutura existente.

---

# Próximas evoluções

O projeto possui espaço para diversas evoluções.

## Observabilidade

* histórico de métricas;
* armazenamento persistente;
* gráficos;
* dashboards;
* métricas adicionais;
* monitoramento de disponibilidade;
* acompanhamento de tendências.

## Infraestrutura

* inventário dos servidores;
* informações do sistema operacional;
* verificação de serviços;
* verificação de processos;
* verificação de portas;
* coleta de uptime;
* coleta de informações de kernel.

## Alertas

* diferentes níveis de severidade;
* alertas de recuperação;
* deduplicação;
* controle de frequência;
* múltiplos canais de notificação.

## Qualidade de código

* linting;
* formatação automática;
* análise estática;
* verificação de tipos;
* aumento da cobertura de testes.

## CI/CD

* testes em múltiplas versões do Python;
* validação de qualidade;
* geração de artefatos;
* versionamento automático;
* releases;
* publicação do pacote.

---

# Status do projeto

**Em desenvolvimento.**

O Infra CLI está sendo desenvolvido de forma incremental, evoluindo de uma ferramenta de automação SSH para uma aplicação estruturada de operações de infraestrutura.

O foco atual está em consolidar:

```text
Python
+
Linux
+
SSH
+
Automação
+
Observabilidade
+
Segurança
+
Testes
+
CI/CD
+
Documentação
```
---

# Conclusão

O Infra CLI demonstra a aplicação prática de conceitos de desenvolvimento de software e administração de infraestrutura em um único projeto.

O objetivo não é apenas executar comandos remotamente.

A proposta é construir uma ferramenta que considere aspectos importantes de um ambiente real:

```text
┌──────────────┐
              │  Automação   │
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │   Segurança  │
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │    Testes    │
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │  Tratamento  │
              │   de falhas  │
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │    CI/CD     │
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │ Documentação │
              └──────────────┘
```
O resultado é uma base de automação de infraestrutura que pode ser expandida progressivamente para atender cenários mais complexos de administração, monitoramento e operações de sistemas Linux.
