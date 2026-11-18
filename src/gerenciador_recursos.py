"""Regra de negocio do ECLSS (Environmental Control and Life Support System)."""
from src.servico_telemetria import ServicoTelemetriaEspacial


class OxigenioInsuficienteError(Exception):
    """Estoque de oxigenio nao cobre o periodo solicitado."""


class AguaInsuficienteError(Exception):
    """Estoque de agua nao cobre o periodo solicitado."""


class NivelEmergenciaInvalidoError(ValueError):
    """Nivel de emergencia fora da faixa de 1 a 5."""


TAXAS_EMERGENCIA = {1: 1.0, 2: 1.25, 3: 1.5, 4: 2.0, 5: 3.0}


class GerenciadorRecursosMarte:
    OXIGENIO_POR_ASTRONAUTA_DIA = 0.84  # kg
    AGUA_POR_ASTRONAUTA_DIA = 3.0  # litros

    def __init__(self, oxigenio, agua, astronautas, telemetria=None):
        if oxigenio < 0 or agua < 0:
            raise ValueError("Estoque nao pode ser negativo")
        if astronautas <= 0:
            raise ValueError("Numero de astronautas deve ser positivo")
        self._estado_inicial = (oxigenio, agua, astronautas)
        self.oxigenio = oxigenio
        self.agua = agua
        self.astronautas = astronautas
        self.telemetria = telemetria if telemetria is not None else ServicoTelemetriaEspacial()

    # ---------- consumo ----------
    def consumo_diario_oxigenio(self, astronautas=None):
        n = self.astronautas if astronautas is None else astronautas
        return round(self.OXIGENIO_POR_ASTRONAUTA_DIA * n, 2)

    def consumo_diario_agua(self, astronautas=None):
        n = self.astronautas if astronautas is None else astronautas
        return round(self.AGUA_POR_ASTRONAUTA_DIA * n, 2)

    # ---------- emergencia ----------
    def taxa_emergencia(self, nivel):
        if isinstance(nivel, bool) or nivel not in TAXAS_EMERGENCIA:
            raise NivelEmergenciaInvalidoError(f"Nivel de emergencia invalido: {nivel}")
        return TAXAS_EMERGENCIA[nivel]

    def consumo_emergencia_oxigenio(self, nivel):
        return round(self.consumo_diario_oxigenio() * self.taxa_emergencia(nivel), 2)

    # ---------- racionamento ----------
    def aplicar_cota_racionamento(self, percentual):
        if not 0 < percentual <= 100:
            raise ValueError("Cota de racionamento deve estar entre 0 (exclusivo) e 100")
        return round(self.consumo_diario_oxigenio() * percentual / 100, 2)

    # ---------- validacao de estoque ----------
    def validar_estoque_oxigenio(self, dias, nivel=1):
        necessario = round(self.consumo_emergencia_oxigenio(nivel) * dias, 2)
        if necessario > self.oxigenio:
            raise OxigenioInsuficienteError(
                f"Oxigenio insuficiente: necessario {necessario:.2f} kg, "
                f"disponivel {self.oxigenio:.2f} kg"
            )
        return True

    def validar_estoque_agua(self, dias):
        necessario = round(self.consumo_diario_agua() * dias, 2)
        if necessario > self.agua:
            raise AguaInsuficienteError(
                f"Agua insuficiente: necessario {necessario:.2f} L, disponivel {self.agua:.2f} L"
            )
        return True

    # ---------- fluxo com telemetria ----------
    def solicitar_suprimentos(self, dias, nivel=1):
        """Reserva oxigenio para `dias`. Em crise, alerta a Terra e levanta erro."""
        try:
            self.validar_estoque_oxigenio(dias, nivel)
        except OxigenioInsuficienteError:
            self.telemetria.disparar_alerta(
                "CRITICO", f"Oxigenio insuficiente para {dias} dias"
            )
            raise
        necessario = round(self.consumo_emergencia_oxigenio(nivel) * dias, 2)
        self.oxigenio = round(self.oxigenio - necessario, 2)
        self.telemetria.enviar_relatorio_status(
            {
                "oxigenio": self.oxigenio,
                "agua": self.agua,
                "astronautas": self.astronautas,
                "status": "NORMAL",
            }
        )
        return {"aprovado": True, "oxigenio_necessario": necessario,
                "oxigenio_restante": self.oxigenio}

    def resetar_estado(self):
        self.oxigenio, self.agua, self.astronautas = self._estado_inicial
