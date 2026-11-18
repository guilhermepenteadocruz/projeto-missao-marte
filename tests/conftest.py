from pathlib import Path

import pytest

from src.gerenciador_recursos import GerenciadorRecursosMarte
from src.servico_telemetria import ServicoTelemetriaEspacial

RAIZ = Path(__file__).resolve().parent.parent
PASTA_SCREENSHOTS = RAIZ / "screenshots"


# ---------- Fixture de modulo: parametros iniciais do habitat ----------
@pytest.fixture(scope="module")
def parametros_habitat():
    """Carrega os parametros iniciais do habitat (uma vez por modulo)."""
    return {"oxigenio": 500.0, "agua": 1500.0, "astronautas": 5}


# ---------- Fixture de escopo function com yield (preparacao e limpeza) ----------
@pytest.fixture
def telemetria_mock(mocker):
    """Dubles da telemetria: nenhuma chamada de rede real e feita."""
    return mocker.MagicMock(spec=ServicoTelemetriaEspacial)


@pytest.fixture
def gerenciador(parametros_habitat, telemetria_mock):
    """Instancia limpa do gerenciador para cada teste."""
    ger = GerenciadorRecursosMarte(
        oxigenio=parametros_habitat["oxigenio"],
        agua=parametros_habitat["agua"],
        astronautas=parametros_habitat["astronautas"],
        telemetria=telemetria_mock,
    )
    yield ger  # o teste roda aqui
    ger.resetar_estado()  # limpeza apos o teste


# ---------- Auditoria: screenshot automatico em caso de falha ----------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    resultado = yield
    relatorio = resultado.get_result()
    if relatorio.when == "call" and relatorio.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            PASTA_SCREENSHOTS.mkdir(exist_ok=True)
            driver.save_screenshot(str(PASTA_SCREENSHOTS / f"{item.name}.png"))
