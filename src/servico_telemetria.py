"""Servico externo de telemetria: envia dados e alertas para a estacao na Terra."""
import json
import urllib.error
import urllib.request


class ServicoTelemetriaEspacial:
    """Dependencia externa (rede). Nos testes unitarios ela e sempre isolada com mocks."""

    URL_BASE = "https://estacao-terra.exemplo.invalid/api"

    def __init__(self, url_base=None, timeout=5):
        self.url_base = url_base or self.URL_BASE
        self.timeout = timeout

    def _enviar(self, endpoint, payload):
        requisicao = urllib.request.Request(
            f"{self.url_base}/{endpoint}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(requisicao, timeout=self.timeout) as resposta:
                return json.loads(resposta.read().decode("utf-8"))
        except urllib.error.URLError as erro:
            raise ConnectionError(f"Falha na comunicacao com a Terra: {erro}") from erro

    def enviar_relatorio_status(self, status):
        """Envia o relatorio de status do habitat para a Terra."""
        return self._enviar("status", status)

    def disparar_alerta(self, nivel, mensagem):
        """Dispara um alerta de crise para a Terra."""
        return self._enviar("alertas", {"nivel": nivel, "mensagem": mensagem})
