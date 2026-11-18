import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from src.gerenciador_recursos import GerenciadorRecursosMarte, OxigenioInsuficienteError

scenarios("features/solicitacao_oxigenio.feature")


@pytest.fixture
def contexto():
    """Guarda o resultado (ou o erro) da acao executada no passo Quando."""
    return {}


@given(
    parsers.parse("que o habitat tem {oxigenio:d} kg de oxigênio e {astronautas:d} astronautas"),
    target_fixture="habitat",
)
def habitat_com_estoque(oxigenio, astronautas, telemetria_mock):
    return GerenciadorRecursosMarte(
        oxigenio=oxigenio, agua=1500, astronautas=astronautas, telemetria=telemetria_mock
    )


@when(parsers.parse("a tripulação solicita oxigênio para {dias:d} dias"))
def tripulacao_solicita(habitat, contexto, dias):
    try:
        contexto["resultado"] = habitat.solicitar_suprimentos(dias)
    except OxigenioInsuficienteError as erro:
        contexto["erro"] = str(erro)


@then("a solicitação deve ser aprovada")
def solicitacao_aprovada(contexto):
    assert contexto["resultado"]["aprovado"] is True
    assert "erro" not in contexto


@then(parsers.parse("o oxigênio restante deve ser {restante:d} kg"))
def oxigenio_restante(habitat, restante):
    assert habitat.oxigenio == restante


@then("nenhum alerta de emergência deve ser enviado para a Terra")
def nenhum_alerta(telemetria_mock):
    telemetria_mock.disparar_alerta.assert_not_called()


@then(parsers.parse('a solicitação deve ser negada com a mensagem "{mensagem}"'))
def solicitacao_negada(contexto, mensagem):
    assert mensagem in contexto["erro"]
    assert "resultado" not in contexto


@then("um alerta de emergência deve ser enviado para a Terra")
def alerta_enviado(telemetria_mock):
    telemetria_mock.disparar_alerta.assert_called_once_with(
        "CRITICO", "Oxigenio insuficiente para 10 dias"
    )
