import numpy as np
import requests
import re
import pandas as pd
from math import floor

from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
import time

# Importar bibliotecas necessárias da binance
from binance.exceptions import BinanceAPIException
from binance.helpers import round_step_size
from binance.client import Client
from binance.enums import *


def Map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def Sentimento_do_mercado(investimento_max):
    try:
        response = requests.get("https://api.alternative.me/fng/?limit=1")
        data = response.json()  # This method is convenient when the API returns JSON
        # print("Fear and Greed Index:",data['data'][0]['value_classification'],'with',data['data'][0]['value']+'%')
        caixa = np.round(
            Map(int(data["data"][0]["value"]), 1, 100, 10, investimento_max)
        )
        return caixa
    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
        print(ReadTimeout)
        print("Problema de conexão")
        return investimento_max - 50


# Função para obter os valores floats a partir de strings
def STR2FLOAT(STR, tick_size):
    number = re.findall(r"[-+]?\d*\.\d+|\d+", STR)[0]
    number = float(number)
    number = round_step_size(number, float(tick_size))

    # number=float('{:.3f}'.format(number))
    return number


def Venda_trade(
    arquivo,
    client_binance,
    Crypto,
    Quantity,
    recommendation,
    valor_de_compra,
    trades_finalizados,
    today,
):

    print("Vendendo ativo")
    print("Quantidade:", Quantity)
    try:
        order_ = client_binance.order_market_sell(symbol=Crypto, quantity=Quantity)
        valor_de_venda = float(order_["fills"][0]["price"])
        print("Valor de venda", valor_de_venda)
        porcentagem = (valor_de_venda - valor_de_compra) * 100 / valor_de_compra

        print(Crypto + ":", "Tive lucro/preju de:", porcentagem, "%")

        dia = today.strftime("%d/%m/%Y")
        horario = today.strftime("%H:%M:%S")
        data_pd = {
            "Crypto": Crypto,
            "Status": recommendation,
            "Price": valor_de_venda,
            "Quantity": Quantity,
            "Day": dia,
            "HOUR": horario,
        }
        trades_finalizados = trades_finalizados.append(data_pd, ignore_index=True)
        trades_finalizados.to_csv(arquivo, index=False)
        return valor_de_venda, porcentagem

    except BinanceAPIException as e:
        print(e.status_code)
        print(e.message)
        porcentagem = (valor_de_venda - valor_de_compra) * 100 / valor_de_compra


def Trade_bot(
    Aviso_valor_atual,
    Set_status,
    Aviso_valor,
    Aviso_quantidade,
    Aviso,
    client_binance,
    Crypto,
    Quantity,
    preco_atual,
    temp,
    today,
    tradingview,
    Venda_lucro,
    recommendation,
    arquivo,
    espera,
    status_trade,
    trades_finalizados,
    valor_de_compra,
    valor_de_venda,
    Trade,
    porcentagem,
    Set_Button_Venda,
):
    # try:

    try:
        recommendation = tradingview.get_analysis().summary["RECOMMENDATION"]
        preco_atual = float(client_binance.get_avg_price(symbol=Crypto)["price"])
        Aviso_valor_atual.emit("Preço atual: " + str(preco_atual))

    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
        print(ReadTimeout)
        print("Problema de conexão")
        Trade = False
        time.sleep(10)

    if "SELL" in recommendation and (
        ("SELL") in status_trade or ("NEUTRAL") in status_trade
    ):
        if espera == False:
            print("Esperando oportunidade de compra")
            Set_status.emit(1)
            Aviso.emit("Esperando oportunidade de compra")
        espera = True
        Venda_lucro = False
        status_trade = recommendation

    elif "SELL" in recommendation and "BUY" in status_trade and Venda_lucro == False:

        valor_de_venda, porcentagem = Venda_trade(
            arquivo,
            client_binance,
            Crypto,
            Quantity,
            recommendation,
            valor_de_compra,
            trades_finalizados,
            today,
        )

        Aviso_valor.emit("Valor de venda: " + str(valor_de_venda))
        Set_status.emit(3)
        Aviso_quantidade.emit(str(0))
        Set_Button_Venda.emit(False)
        Trade = False
        espera = False

        if tradingview.interval in temp:
            status_trade = recommendation
        else:
            status_trade = "NEUTRAL"
            tradingview.interval = temp

    elif "BUY" in recommendation and "SELL" in status_trade and Venda_lucro == False:
        print("Comprando ativo")

        try:
            order_ = client_binance.order_market_buy(symbol=Crypto, quantity=Quantity)
            valor_de_compra = float(order_["fills"][0]["price"])
            print("Valor de compra", valor_de_compra)
            Aviso_valor.emit("Valor de compra: " + str(valor_de_compra))
            Set_status.emit(2)

            dia = today.strftime("%d/%m/%Y")
            horario = today.strftime("%H:%M:%S")
            data_pd = {
                "Crypto": Crypto,
                "Status": recommendation,
                "Price": valor_de_compra,
                "Quantity": Quantity,
                "Day": dia,
                "HOUR": horario,
            }
            trades_finalizados = trades_finalizados.append(data_pd, ignore_index=True)
            trades_finalizados.to_csv(arquivo, index=False)

            espera = False
            status_trade = recommendation
            Set_Button_Venda.emit(True)

        except BinanceAPIException as e:
            print(e.status_code)
            print(e.message)
            Aviso.emit(e.message)

        try:
            print("Quantidade", float(order_["origQty"]))
            Quantity = float(order_["executedQty"])
            print("Quantidade comprada", Quantity)
            print(order_)

        except BinanceAPIException as e:
            print(e.status_code)
            print(e.message)
            Aviso.emit(e.message)

        Aviso_quantidade.emit(str(Quantity))

    elif "BUY" in recommendation and "BUY" in status_trade and Venda_lucro == False:
        porcentagem = (preco_atual - valor_de_compra) * 100 / valor_de_compra
        # print(Crypto+":",'Tive lucro/preju de:',porcentagem,"%")

        if porcentagem > 3 and porcentagem < 10:
            tradingview.interval = "1h"
        elif porcentagem > 10 and porcentagem < 17:
            tradingview.interval = "30m"
        elif porcentagem > 17 and porcentagem < 25:
            tradingview.interval = "15m"
        elif porcentagem > 25:
            tradingview.interval = "5m"

        if porcentagem >= 50:
            Venda_lucro = True
            status_trade = "NEUTRAL"
            valor_de_venda = Venda_trade(
                arquivo,
                client_binance,
                Crypto,
                Quantity,
                "SELL",
                valor_de_compra,
                trades_finalizados,
                today,
            )
            Aviso_valor.emit("Valor de venda: " + str(valor_de_venda))
            Set_status.emit(3)
            print("Esperando oportunidade de compra")
            Aviso.emit("Esperando oportunidade de compra")
            Set_status.emit(1)
            tradingview.interval = temp

        if espera == False:
            print("Esperando ativo valorizar mais")
            Aviso.emit("Esperando ativo valorizar mais")
            status_trade = recommendation
            Set_Button_Venda.emit(True)

        espera = True
    elif "BUY" in recommendation and "NEUTRAL" in status_trade and Venda_lucro == False:
        if espera == False:
            print("Ativo muito valorizado, estou esperando oportunidade de compra")
            Aviso.emit("Ativo muito valorizado, estou esperando oportunidade de compra")
            Set_status.emit(1)
        espera = True
    try:
        if valor_de_compra:
            pass
    except:
        valor_de_compra = 1

    return (
        Quantity,
        recommendation,
        status_trade,
        Trade,
        preco_atual,
        porcentagem,
        Venda_lucro,
        espera,
        valor_de_compra,
        tradingview,
    )


def main(Set_status, Aviso, client_binance, Crypto, investimento_max, Quantity):
    valor_do_trade = investimento_max
    # verifica o tamanho de casas decimais da crypto
    tick_size = client_binance.get_symbol_info(Crypto)["filters"][0]["tickSize"]
    preco_medio = float(client_binance.get_avg_price(symbol=Crypto)["price"])

    # verifica na carteira, a informações sobre o dinheiro em caixa.
    saldo_usdt = client_binance.get_asset_balance(asset="USDT")
    saldo_btc = client_binance.get_asset_balance(asset="BTC")
    if Quantity == 0:
        Quantity_ = valor_do_trade / preco_medio
        # print('Quantidade1:',Quantity_)
        Quantity = STR2FLOAT(str(Quantity_), tick_size)
        if Quantity <= 0:
            tick_size = float(tick_size) / 100
            Quantity = STR2FLOAT(str(Quantity_), tick_size)

        if Quantity > 1 and Quantity < 10:
            Quantity = round(Quantity, 1)
        elif Quantity > 10:
            Quantity = floor(Quantity)
            # Quantity=round(Quantity)

    print("quantidade:", Quantity)
    if "USDT" in Crypto and float(saldo_usdt["free"]) > 1 and valor_do_trade > 10:
        print("Iniciando o trade de: ", Crypto)
        print("Com valor de caixa de: ", valor_do_trade)
        Trade = True
        # Trade_bot(Crypto,Quantity)
    elif "BTC" in Crypto and float(saldo_btc["free"]) > 0:
        print("Iniciando o trade de: ", Crypto)
        print("Com valor de caixa de: ", valor_do_trade)
        Trade = True
        # Trade_bot(Crypto,Quantity)
    else:
        print(
            "Saldo insuficiente ou o tamanho da ordem é menor que 10$ usdt ou o par não é com USDT"
        )
        Aviso.emit("Saldo insuficiente")
        Set_status.emit(1)
        Trade = False

    return Quantity, Trade, preco_medio
