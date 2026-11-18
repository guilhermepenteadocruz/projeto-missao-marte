# language: pt
Funcionalidade: Solicitação de suprimentos de oxigênio
  Como engenheiro do habitat de Marte
  Eu quero solicitar oxigênio para um período de dias
  Para garantir a sobrevivência dos astronautas

  Cenário: Solicitação em condições normais
    Dado que o habitat tem 500 kg de oxigênio e 5 astronautas
    Quando a tripulação solicita oxigênio para 10 dias
    Então a solicitação deve ser aprovada
    E o oxigênio restante deve ser 458 kg
    E nenhum alerta de emergência deve ser enviado para a Terra

  Cenário: Solicitação em condição de crise
    Dado que o habitat tem 20 kg de oxigênio e 5 astronautas
    Quando a tripulação solicita oxigênio para 10 dias
    Então a solicitação deve ser negada com a mensagem "Oxigenio insuficiente"
    E um alerta de emergência deve ser enviado para a Terra
