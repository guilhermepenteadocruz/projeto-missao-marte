![Pipeline Missao Marte](https://github.com/guilhermepenteadocruz/projeto-missao-marte/actions/workflows/pipeline.yml/badge.svg)

# Missão Marte: ECLSS

Suíte de testes automatizados do **Environmental Control and Life Support System (ECLSS)** do Habitat de Marte.

## O que é testado

| Componente | Arquivo | Como é testado |
|---|---|---|
| `GerenciadorRecursosMarte` | `src/gerenciador_recursos.py` | Pytest: fixtures, parametrização e `pytest.raises` |
| `ServicoTelemetriaEspacial` | `src/servico_telemetria.py` | Isolado com mocks (`pytest-mock`) |
| `PainelControleWeb` | `web/painel.html` | Selenium WebDriver headless com esperas explícitas |
| Solicitação de suprimentos | `tests/features/solicitacao_oxigenio.feature` | BDD com `pytest-bdd` (Gherkin) |

## Estrutura

```
projeto-missao-marte/
├── .github/workflows/pipeline.yml
├── src/
│   ├── gerenciador_recursos.py
│   └── servico_telemetria.py
├── tests/
│   ├── conftest.py
│   ├── test_gerenciador.py
│   ├── test_selenium_e2e.py
│   ├── test_bdd.py
│   └── features/solicitacao_oxigenio.feature
├── web/painel.html
├── requirements.txt
└── README.md
```

## Como executar localmente

Pré-requisitos: Python 3.10+, Git e Google Chrome instalado (usado pelo Selenium).

```bash
# 1. Clonar o repositório
git clone https://github.com/guilhermepenteadocruz/projeto-missao-marte.git
cd projeto-missao-marte

# 2. (Opcional) criar e ativar o ambiente virtual
python -m venv venv
# Windows (PowerShell): .\venv\Scripts\Activate.ps1
# Linux/macOS:          source venv/bin/activate

# 3. Instalar os requisitos
pip install -r requirements.txt

# 4. Executar a suíte de testes
pytest
```

Para ver o relatório de cobertura de código no console:

```bash
pytest --cov=src --cov-report=term-missing
```

## Integração contínua

O workflow `.github/workflows/pipeline.yml` roda a suíte completa (Pytest, Mocks, Selenium headless e BDD)
a cada `push` e `pull_request`, exibindo a cobertura de código via `pytest-cov`.
Se algum teste do Selenium falhar, o screenshot gerado em `screenshots/` é salvo como artefato da execução.
