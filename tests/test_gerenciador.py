import pytest

from src.gerenciador_recursos import (
    AguaInsuficienteError,
    GerenciadorRecursosMarte,
    NivelEmergenciaInvalidoError,
    OxigenioInsuficienteError,
)
from src.servico_telemetria import ServicoTelemetriaEspacial


# ---------------- Fixtures ----------------
def test_fixture_de_modulo_carrega_parametros(parametros_habitat):
    assert parametros_habitat["astronautas"] == 5
    assert parametros_habitat["oxigenio"] == 500.0


def test_fixture_function_entrega_instancia_limpa(gerenciador):
    assert gerenciador.oxigenio == 500.0
    gerenciador.oxigenio = 1.0  # sujeira que nao pode vazar para o proximo teste


def test_fixture_function_nao_herda_estado_do_teste_anterior(gerenciador):
    assert gerenciador.oxigenio == 500.0


# ---------------- Parametrizacao ----------------
@pytest.mark.parametrize(
    "astronautas, esperado",
    [(1, 0.84), (2, 1.68), (5, 4.2), (10, 8.4)],
)
def test_consumo_diario_oxigenio_varia_com_astronautas(gerenciador, astronautas, esperado):
    assert gerenciador.consumo_diario_oxigenio(astronautas) == pytest.approx(esperado)


@pytest.mark.parametrize(
    "astronautas, esperado",
    [(1, 3.0), (4, 12.0), (6, 18.0)],
)
def test_consumo_diario_agua(gerenciador, astronautas, esperado):
    assert gerenciador.consumo_diario_agua(astronautas) == pytest.approx(esperado)


@pytest.mark.parametrize(
    "nivel, taxa",
    [(1, 1.0), (2, 1.25), (3, 1.5), (4, 2.0), (5, 3.0)],
)
def test_taxa_de_emergencia(gerenciador, nivel, taxa):
    assert gerenciador.taxa_emergencia(nivel) == taxa


@pytest.mark.parametrize(
    "nivel, esperado",
    [(1, 4.2), (2, 5.25), (3, 6.3), (4, 8.4), (5, 12.6)],
)
def test_consumo_de_oxigenio_em_emergencia(gerenciador, nivel, esperado):
    assert gerenciador.consumo_emergencia_oxigenio(nivel) == pytest.approx(esperado)


@pytest.mark.parametrize(
    "percentual, esperado",
    [(100, 4.2), (50, 2.1), (25, 1.05), (10, 0.42)],
)
def test_cota_de_racionamento(gerenciador, percentual, esperado):
    assert gerenciador.aplicar_cota_racionamento(percentual) == pytest.approx(esperado)


@pytest.mark.parametrize("dias", [1, 10, 100])
def test_estoque_de_oxigenio_suficiente(gerenciador, dias):
    assert gerenciador.validar_estoque_oxigenio(dias) is True


def test_estoque_de_agua_suficiente(gerenciador):
    assert gerenciador.validar_estoque_agua(dias=10) is True


# ---------------- Excecoes ----------------
def test_oxigenio_insuficiente_levanta_excecao(gerenciador):
    with pytest.raises(OxigenioInsuficienteError, match="Oxigenio insuficiente"):
        gerenciador.validar_estoque_oxigenio(dias=200)


def test_agua_insuficiente_levanta_excecao(gerenciador):
    with pytest.raises(AguaInsuficienteError):
        gerenciador.validar_estoque_agua(dias=500)


@pytest.mark.parametrize("nivel_invalido", [0, 6, -1, 99, "alto", None, True])
def test_nivel_de_emergencia_invalido(gerenciador, nivel_invalido):
    with pytest.raises(NivelEmergenciaInvalidoError):
        gerenciador.taxa_emergencia(nivel_invalido)


@pytest.mark.parametrize("percentual", [0, -10, 101])
def test_cota_de_racionamento_invalida(gerenciador, percentual):
    with pytest.raises(ValueError, match="Cota de racionamento"):
        gerenciador.aplicar_cota_racionamento(percentual)


@pytest.mark.parametrize(
    "oxigenio, agua, astronautas",
    [(-1, 10, 1), (10, -1, 1), (10, 10, 0)],
)
def test_construtor_rejeita_valores_invalidos(oxigenio, agua, astronautas):
    with pytest.raises(ValueError):
        GerenciadorRecursosMarte(oxigenio, agua, astronautas)


def test_construtor_cria_telemetria_padrao_quando_omitida():
    ger = GerenciadorRecursosMarte(10, 10, 1)
    assert isinstance(ger.telemetria, ServicoTelemetriaEspacial)


# ---------------- Mocks: isolamento do ServicoTelemetriaEspacial ----------------
def test_alerta_de_emergencia_disparado_com_argumentos_corretos(gerenciador, telemetria_mock):
    telemetria_mock.disparar_alerta.return_value = {"status": "recebido"}

    with pytest.raises(OxigenioInsuficienteError):
        gerenciador.solicitar_suprimentos(dias=200)

    telemetria_mock.disparar_alerta.assert_called_once_with(
        "CRITICO", "Oxigenio insuficiente para 200 dias"
    )
    telemetria_mock.enviar_relatorio_status.assert_not_called()


def test_relatorio_de_status_enviado_quando_ha_estoque(gerenciador, telemetria_mock):
    resultado = gerenciador.solicitar_suprimentos(dias=10)

    assert resultado == {
        "aprovado": True,
        "oxigenio_necessario": 42.0,
        "oxigenio_restante": 458.0,
    }
    telemetria_mock.enviar_relatorio_status.assert_called_once_with(
        {"oxigenio": 458.0, "agua": 1500.0, "astronautas": 5, "status": "NORMAL"}
    )
    telemetria_mock.disparar_alerta.assert_not_called()


def test_patch_do_metodo_da_classe_simula_resposta_da_terra(mocker):
    alerta = mocker.patch.object(
        ServicoTelemetriaEspacial, "disparar_alerta", return_value={"status": "recebido"}
    )
    ger = GerenciadorRecursosMarte(oxigenio=10, agua=100, astronautas=5)

    with pytest.raises(OxigenioInsuficienteError):
        ger.solicitar_suprimentos(dias=10)

    alerta.assert_called_once_with("CRITICO", "Oxigenio insuficiente para 10 dias")


def test_patch_da_classe_inteira_no_modulo(mocker):
    classe_falsa = mocker.patch("src.gerenciador_recursos.ServicoTelemetriaEspacial")
    ger = GerenciadorRecursosMarte(oxigenio=500, agua=100, astronautas=5)

    ger.solicitar_suprimentos(dias=1)

    classe_falsa.assert_called_once_with()
    classe_falsa.return_value.enviar_relatorio_status.assert_called_once()


# ---------------- ServicoTelemetriaEspacial (rede isolada com patch) ----------------
def test_servico_envia_alerta_sem_acessar_a_rede(mocker):
    resposta = mocker.MagicMock()
    resposta.read.return_value = b'{"status": "recebido"}'
    resposta.__enter__.return_value = resposta
    urlopen = mocker.patch("src.servico_telemetria.urllib.request.urlopen", return_value=resposta)

    retorno = ServicoTelemetriaEspacial().disparar_alerta("CRITICO", "teste")

    assert retorno == {"status": "recebido"}
    urlopen.assert_called_once()


def test_servico_envia_relatorio_de_status(mocker):
    resposta = mocker.MagicMock()
    resposta.read.return_value = b'{"ok": true}'
    resposta.__enter__.return_value = resposta
    mocker.patch("src.servico_telemetria.urllib.request.urlopen", return_value=resposta)

    assert ServicoTelemetriaEspacial().enviar_relatorio_status({"oxigenio": 1}) == {"ok": True}


def test_servico_converte_falha_de_rede_em_connection_error(mocker):
    import urllib.error

    mocker.patch(
        "src.servico_telemetria.urllib.request.urlopen",
        side_effect=urllib.error.URLError("sem sinal"),
    )

    with pytest.raises(ConnectionError, match="Falha na comunicacao com a Terra"):
        ServicoTelemetriaEspacial().disparar_alerta("CRITICO", "teste")
