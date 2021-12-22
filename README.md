[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Bot para Trade na Binance
Siga a sequência de passos a seguir para usar o "trade_bot"

**Passo 1**: Baixe os arquivos desse repositório.

**Passo 2**: Crie uma sua API de gerenciamento na Binance ([detalhes aqui](https://www.binance.com/en/support/faq/360002502072)). Não esqueça de habilitar a opção _Enable Spot & Margin Trading_ e, de preferência, limitar o uso apenas para o seu IP. Guarde as credenciais no arquivo `credentials.json`.

**Passo 4**: Em seguida rode o arquivo principal "main_unit.py", ou execute o arquivo executável "execultavel.bat".

**Obs 1**: As bibliotecas necessárias estão no arquivo "requiriments.txt".

**Obs 2**: Rentabilidade passada não é garantia de rentabilidade futura

**Disclaimer**:
Nada assegura que a estratégia de investimento contida nesse robô(código) são adequadas ao perfil e circunstâncias individuais de quem o recebe.
Investimentos envolvem riscos e os investidores devem ter prudência ao tomar suas decisões, pois o presente robô não é um substituto para o exercício de seu próprio julgamento.

Este documento não pode ser reproduzido ou distribuído por qualquer pessoa, parcialmente ou em sua totalidade, sem o prévio consentimento
por escrito do Autor. 

### Formatação 

Para manter uma formatação padronizada de código e para melhor legibilidade, o projeto usa a biblioteca [black](https://github.com/psf/black). Sempre que for sugerir mudanças, rode o comando `black .` para que todo o projeto seja formatado. Se desejar apenas visualizar onde tem mudanças sugeridas pela bilbioteca, use `black . --check`.