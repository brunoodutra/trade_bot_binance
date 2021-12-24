import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import numpy as np

# Importar bibliotecas necessárias da thread
import threading
import time

# Importar bibliotecas necessárias da binance
from binance.exceptions import BinanceAPIException  # here
from binance.helpers import round_step_size
from binance.client import Client
from binance.enums import *
import functions as Trade_bot
from tradingview_ta import TA_Handler, Interval, Exchange
import os.path
import pandas as pd
from datetime import datetime
import pytz
import json

from coloredlogs import CustomFormatter
logger = CustomFormatter().get_colored_logger()


credentials = json.load(open(f"./credentials.json"))
client_binance = Client(
    api_key=credentials.get("API_KEY"), api_secret=credentials.get("API_SECRET")
)

class Main(QtWidgets.QMainWindow):
    global client_binance

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)  # Call the inherited classes __init__ method
        uic.loadUi("trade_manage_unit.ui", self)  # Load the .ui file

        # Atribuição de funções
        self.percentage.setText("0")
        # self.text = self.findChild(QtWidgets.QTextBrowser, 'textBrowser')
        # self.textBrowser.setText('OI')
        self.text = self.findChild(QtWidgets.QLabel, "percentage")
        self.recommendation = self.findChild(QtWidgets.QLabel, "recommendation")
        self.aviso = self.findChild(QtWidgets.QLabel, "aviso")
        self.aviso_valor = self.findChild(QtWidgets.QLabel, "aviso_valor")
        self.aviso_valor_atual = self.findChild(QtWidgets.QLabel, "aviso_valor_atual")
        self.aviso_valor_quantidade = self.findChild(
            QtWidgets.QLabel, "aviso_valor_quantidade"
        )

        self.venda = False
        self.pushButton_venda.setEnabled(False)
        self.pushButton_venda.clicked.connect(self.Venda)

        self.pushButton_compra.setEnabled(False)
        self.pushButton_compra.clicked.connect(self.Compra)

        # self.aviso_valor.setText('oi')
        self.checkBox_trade.clicked.connect(self.Life_bot)
        self.Grafik = self.findChild(QtWidgets.QGraphicsView, "graphicsView_1")
        # Chama a função do grafico e recebe o atributo item para definir o valor
        self.item = self.grafico_rentabilidade(self.Grafik)

        self.show()  # Show the GUI

    def Venda(self):
        self.pushButton_venda.setEnabled(False)
        logger.info("apertou vender")
        self.pushButton_venda.setDisabled(True)
        # self.pushButton_compra.setEnabled(False)
        self.t.event_Venda()
        # self.Life_bot()

    def Compra(self):
        self.pushButton_compra.setEnabled(False)
        logger.info("apertou comprar")
        self.pushButton_compra.setDisabled(True)
        # self.pushButton_compra.setEnabled(False)
        self.t.event_Compra()
        # self.Life_bot()

    def grafico_rentabilidade(self, Grafik):
        # Configuração do ponteiro
        pen = QtGui.QPen(QtCore.Qt.white)
        pen.setWidth(4)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        scene = QtWidgets.QGraphicsScene()
        pen.setCosmetic(True)

        # adc a imagem de fundo
        scene.addPixmap(QtGui.QPixmap("bitmap.png"))
        item = scene.addLine(70, 160, 87, 87, pen)
        pen = QtGui.QPen(QtGui.QColor(QtCore.Qt.yellow))
        brush = QtGui.QBrush(QtCore.Qt.gray)
        scene.addEllipse(77, 77, 20, 20, pen, brush)
        item.setTransformOriginPoint(87, 87)
        item.setRotation(100)
        Grafik.setScene(scene)
        Grafik.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)
        return item

    def set_Status(self, val):
        if val == 1:
            self.radioButton_comprado.setChecked(False)
            self.radioButton_comprado.setDisabled(True)
            self.radioButton_vendido.setChecked(False)
            self.radioButton_vendido.setDisabled(True)
            self.radioButton_espera.setChecked(True)
            self.radioButton_espera.setDisabled(True)
        elif val == 2:
            self.radioButton_comprado.setChecked(True)
            self.radioButton_comprado.setDisabled(True)
            self.radioButton_vendido.setChecked(False)
            self.radioButton_vendido.setDisabled(True)
            self.radioButton_espera.setChecked(False)
            self.radioButton_espera.setDisabled(True)

        elif val == 3:
            self.radioButton_comprado.setChecked(False)
            self.radioButton_comprado.setDisabled(True)
            self.radioButton_vendido.setChecked(True)
            self.radioButton_vendido.setDisabled(True)
            self.radioButton_espera.setChecked(False)
            self.radioButton_espera.setDisabled(True)

        elif val == 4:
            self.radioButton_comprado.setDisabled(False)
            self.radioButton_comprado.setChecked(False)

            self.radioButton_vendido.setDisabled(False)
            self.radioButton_vendido.setChecked(False)

            self.radioButton_espera.setDisabled(False)
            self.radioButton_espera.setChecked(False)

    def Life_bot(self):
        if self.checkBox_trade.isChecked():
            self.set_Status(1)
            Crypto = self.Crypto.text()
            time = self.Tempo_grafico.text()
            valor_de_caixa = self.valor_de_caixa.text()
            if self.checkBox_sentimento.isChecked():
                valor_de_caixa = Trade_bot.Sentimento_do_mercado(float(valor_de_caixa))
                self.valor_de_caixa.setText(str(valor_de_caixa))
            else:
                valor_de_caixa = float(valor_de_caixa)

            self.t = wait_trade(client_binance, Crypto, time, valor_de_caixa)

            self.t.PRINT.connect(self.text.setText)
            self.t.Recommendation_text.connect(self.recommendation.setText)
            self.t.Aviso.connect(self.aviso.setText)
            self.t.Aviso_valor.connect(self.aviso_valor.setText)
            self.t.Aviso_valor_atual.connect(self.aviso_valor_atual.setText)
            self.t.Rotation.connect(self.item.setRotation)
            self.t.Set_status.connect(self.set_Status)
            self.t.Set_Button_Venda.connect(self.pushButton_venda.setEnabled)
            self.t.Set_Button_Compra.connect(self.pushButton_compra.setEnabled)
            self.t.Aviso_quantidade.connect(self.aviso_valor_quantidade.setText)

            # self.t.run(self.text)
            # self.t.begin()
            self.t.start()
            # if self.venda:
            #  print('iniciando evento de venda')
            #  self.t.event_Venda()
            #  self.venda=False

        else:
            self.t.kill()


class wait_trade(QtCore.QObject):
    PRINT = QtCore.pyqtSignal(str)
    Recommendation_text = QtCore.pyqtSignal(str)
    Aviso = QtCore.pyqtSignal(str)
    Aviso_valor = QtCore.pyqtSignal(str)
    Aviso_valor_atual = QtCore.pyqtSignal(str)
    Rotation = QtCore.pyqtSignal(int)
    Set_status = QtCore.pyqtSignal(int)
    Set_Button_Venda = QtCore.pyqtSignal(bool)
    Set_Button_Compra = QtCore.pyqtSignal(bool)
    Aviso_quantidade = QtCore.pyqtSignal(str)

    def __init__(self, client_binance, Crypto, temp, valor_de_caixa):
        super().__init__()
        self.Intervals = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d", "1W", "1M"]
        self.recommendation = "NEUTRAL"
        self.status_trade = "NEUTRAL"
        self.preco_atual = 0
        self.porcentagem = 0
        self.investimento_max = valor_de_caixa
        self.temp = temp
        self.time_atual = 10
        self._kill = threading.Event()
        self.client_binance = client_binance
        self.Crypto = Crypto
        self.venda = False
        self.compra = False

        self.T_br = pytz.timezone("America/Sao_Paulo")
        self.today = datetime.now(self.T_br)

        self.t = threading.Timer(self.time_atual, self._execute)

    def begin(self):

        self.Set_Button_Venda.emit(False)
        self.Set_Button_Compra.emit(False)

        if self.temp in self.Intervals:
            pass
        else:
            self.temp = "1h"

        self.tradingview = TA_Handler(
            symbol=self.Crypto,
            screener="crypto",
            exchange="BINANCE",
            interval=self.temp,
            timeout=(30),
        )

        self.arquivo = "trades_finalizados_" + self.Crypto + ".csv"
        if os.path.isfile(self.arquivo):
            self.trades_finalizados = pd.read_csv(self.arquivo, index_col=False)
        else:
            logger.info(f"Criando base de dados para: {self.Crypto}")
            dia = self.today.strftime("%d/%m/%Y")
            horario = self.today.strftime("%H:%M:%S")
            data_pd = {
                "Crypto": [self.Crypto],
                "Status": ["NEUTRAL"],
                "Price": [0],
                "Quantity": [0],
                "Day": [dia],
                "HOUR": [horario],
            }
            self.trades_finalizados = pd.DataFrame(data_pd)
            self.trades_finalizados.to_csv(self.arquivo, index=False)

        self.status_trade = self.trades_finalizados["Status"][
            self.trades_finalizados.index[-1]
        ]
        logger.warning(f"último status:  {self.status_trade}")
        if "BUY" in self.status_trade:
            self.valor_de_compra = self.trades_finalizados["Price"][
                self.trades_finalizados.index[-1]
            ]
            self.Aviso_valor.emit("Valor de Compra: " + str(self.valor_de_compra))
            self.valor_de_venda = 0
            self.Quantity = self.trades_finalizados["Quantity"][
                self.trades_finalizados.index[-1]
            ]
            # self.Quantity=0
            self.Aviso_quantidade.emit(str(self.Quantity))

            self.Venda_lucro = False
            self.Set_status.emit(2)
        else:
            self.valor_de_venda = self.trades_finalizados["Price"][
                self.trades_finalizados.index[-1]
            ]
            # self.Quantity=self.trades_finalizados['Quantity'][self.trades_finalizados.index[-1]]
            self.Quantity = 0
            self.Aviso_quantidade.emit(str(self.Quantity))
            self.valor_de_compra = 0
            self.Venda_lucro = False
            self.Set_status.emit(3)
            self.status_trade = "NEUTRAL"
            self.Set_Button_Compra.emit(True)

        self.espera = False

    def start(self):
        # threading.Timer(5, self._execute).start()
        self.t.start()

    def _execute(self):
        self.begin()
        self.Quantity, self.Trade, self.preco_medio = Trade_bot.main(
            self.Set_status,
            self.Aviso,
            self.client_binance,
            self.Crypto,
            self.investimento_max,
            self.Quantity,
        )
        # self.Aviso_quantidade.emit(str(self.Quantity))
        logger.info(f"Quantidade: {str(self.Quantity)}")
        # try:
        while True:
            if self.Trade:
                (
                    self.Quantity,
                    self.recommendation,
                    self.status_trade,
                    self.Trade,
                    self.preco_atual,
                    self.porcentagem,
                    self.Venda_lucro,
                    self.espera,
                    self.valor_de_compra,
                    self.tradingview,
                ) = Trade_bot.Trade_bot(
                    self.Aviso_valor_atual,
                    self.Set_status,
                    self.Aviso_valor,
                    self.Aviso_quantidade,
                    self.Aviso,
                    self.client_binance,
                    self.Crypto,
                    self.Quantity,
                    self.preco_atual,
                    self.temp,
                    self.today,
                    self.tradingview,
                    self.Venda_lucro,
                    self.recommendation,
                    self.arquivo,
                    self.espera,
                    self.status_trade,
                    self.trades_finalizados,
                    self.valor_de_compra,
                    self.valor_de_venda,
                    self.Trade,
                    self.porcentagem,
                    self.Set_Button_Venda,
                )
                value = self.porcentagem
                self.Recommendation_text.emit(self.recommendation)
                value_map = Trade_bot.Map(value, -20, 20, 50, 288)
                self.PRINT.emit(str(np.round(value, 1)) + "%")
                self.Rotation.emit(value_map)
                time.sleep(self.time_atual)
                # time.sleep(60)
            else:
                self.Quantity, self.Trade, self.preco_medio = Trade_bot.main(
                    self.Set_status,
                    self.Aviso,
                    self.client_binance,
                    self.Crypto,
                    self.investimento_max,
                    self.Quantity,
                )
                time.sleep(20)

            if self.venda == True:
                logger.info("Ativo vendido!")
                self.venda = False
                self.Set_Button_Venda.emit(False)
                self.Set_Button_Compra.emit(True)
            if self.compra == True:
                logger.info("Ativo comprado!")
                self.compra = False
                # self.Set_Button_Venda.emit(True)
                self.Set_Button_Compra.emit(False)

            if self._kill.is_set() == True:
                break

    # except:
    #    print('reiniciando a thread')
    #   self.t= threading.Timer(self.time_atual, self._execute)

    def event_Venda(self):
        self.venda = True
        logger.info("venda autorizada")
        try:
            self.Venda_lucro = True
            self.status_trade = "NEUTRAL"
            self.valor_de_venda, self.porcentagem = Trade_bot.Venda_trade(
                self.arquivo,
                self.client_binance,
                self.Crypto,
                self.Quantity,
                "SELL",
                self.valor_de_compra,
                self.trades_finalizados,
                self.today,
            )
            self.Aviso_valor.emit("Valor de venda: " + str(self.valor_de_venda))
            self.Set_status.emit(3)
            # self.Aviso_quantidade.emit(str(0))
            logger.info("Esperando oportunidade de compra")
            self.Aviso.emit("Esperando oportunidade de compra")
            self.Set_status.emit(1)
            self.tradingview.interval = self.temp

            self.Set_Button_Venda.emit(False)
            self.Set_Button_Compra.emit(True)

        except BinanceAPIException as e:
            self.Aviso.emit(e.message)

    def event_Compra(self):
        self.compra = True
        logger.info("Compra Autorizada")
        try:
            self.Venda_lucro = False
            self.status_trade = "BUY"
            # faz a compra

            # self.Aviso_valor.emit('Valor de compra '+str(self.valor_de_venda))
            # self.Set_status.emit(2)
            # print('Compra feita, esperando valorização')
            # self.Aviso.emit('Compra feita, esperando valorização')
            # self.tradingview.interval=self.temp
            # self.Set_Button_Compra.emit(False)

            logger.info("Comprando ativo")

            order_ = self.client_binance.order_market_buy(
                symbol=self.Crypto, quantity=self.Quantity
            )
            self.valor_de_compra = float(order_["fills"][0]["price"])
            logger.info(f"Valor de compra: {self.valor_de_compra}")
            self.Aviso_valor.emit("Valor de compra: " + str(self.valor_de_compra))
            self.Set_status.emit(2)

            dia = self.today.strftime("%d/%m/%Y")
            horario = self.today.strftime("%H:%M:%S")
            data_pd = {
                "Crypto": self.Crypto,
                "Status": self.recommendation,
                "Price": self.valor_de_compra,
                "Quantity": self.Quantity,
                "Day": dia,
                "HOUR": horario,
            }
            trades_finalizados = self.trades_finalizados.append(
                data_pd, ignore_index=True
            )
            trades_finalizados.to_csv(self.arquivo, index=False)

            self.espera = False
            self.status_trade = self.recommendation
            self.Set_Button_Venda.emit(True)
            self.Set_Button_Compra.emit(False)

        except BinanceAPIException as e:
            # loga no console
            logger.exception(f"Erro de status code {e.status_code}. Traceback abaixo.")
            self.Aviso.emit(e.message)

        try:
            logger.info(f"Quantidade: {float(order_['origQty'])}")
            Quantity = float(order_["executedQty"])
            logger.info(f"Quantidade comprada: {self.Quantity}")
            logger.info(order_)

        except BinanceAPIException as e:
            # loga no console
            logger.exception(f"Erro de status code {e.status_code}. Traceback abaixo.")
            self.Aviso.emit(e.message)

        self.Aviso_quantidade.emit(str(self.Quantity))

    def kill(self):
        self._kill.set()
        self.t.cancel()
        print("Afunção morreu")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # window = Upload_window()
    window = Main()
    window.show()
    sys.exit(app.exec_())
