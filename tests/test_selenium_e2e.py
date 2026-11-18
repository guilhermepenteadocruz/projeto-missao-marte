from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PAINEL_URL = (Path(__file__).resolve().parent.parent / "web" / "painel.html").as_uri()


@pytest.fixture
def driver():
    """Inicializa o Chrome em modo headless e garante o encerramento (driver.quit())."""
    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument("--headless=new")
    opcoes.add_argument("--no-sandbox")
    opcoes.add_argument("--disable-dev-shm-usage")
    opcoes.add_argument("--window-size=1280,900")
    navegador = webdriver.Chrome(options=opcoes)
    yield navegador
    navegador.quit()


def solicitar_cota(driver, quantidade):
    driver.get(PAINEL_URL)
    campo = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "input-quantidade"))
    )
    campo.clear()
    campo.send_keys(str(quantidade))
    driver.find_element(By.ID, "btn-solicitar").click()


def test_painel_exibe_nivel_inicial_de_oxigenio(driver):
    driver.get(PAINEL_URL)
    nivel = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "nivel-oxigenio"))
    )
    assert nivel.text == "1000"


def test_solicitar_cota_extra_atualiza_nivel_de_oxigenio(driver):
    solicitar_cota(driver, 42)

    # Espera explicita: aguarda o DOM refletir o novo nivel (1000 - 42).
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "nivel-oxigenio"), "958")
    )
    mensagem = driver.find_element(By.ID, "mensagem-status").text
    assert "Solicitacao aprovada: 42 kg" in mensagem


def test_solicitacao_acima_do_limite_e_negada(driver):
    solicitar_cota(driver, 500)

    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "mensagem-status"), "negada")
    )
    assert driver.find_element(By.ID, "nivel-oxigenio").text == "1000"
