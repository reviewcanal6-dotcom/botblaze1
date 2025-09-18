import time
import requests
from bs4 import BeautifulSoup
import telebot

# === CONFIGURAÇÕES DO TELEGRAM ===
TOKEN = "8064880951:AAG2t9sq6PwOeQpMnDWgTI-DuvGj5QBhdLU"
CHAT_ID = "-1002550073701"
bot = telebot.TeleBot(TOKEN)

# === CONFIGURAÇÕES DO TIPMINER ===
URL = "https://www.tipminer.com/br/historico/blaze/double"

# === VARIÁVEIS DE CONTROLE ===
ultimo_resultado = None
gale_count = 0
entrada = None

def pegar_resultados():
    """ Faz scrape do Tipminer e retorna os últimos resultados (lista de cores). """
    try:
        response = requests.get(URL, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Busca todos os círculos do histórico
        elementos = soup.find_all("div", class_="cell__circle")

        resultados = []
        for el in elementos[:5]:  # Pega só os últimos 5 para não sobrecarregar
            style = el.get("style", "")
            numero = el.find("div", class_="cell__result").text.strip()

            if "background-color: rgb(229, 62, 62)" in style:  # Vermelho
                resultados.append(("vermelho", numero))
            elif "background-color: rgb(26, 32, 44)" in style:  # Preto
                resultados.append(("preto", numero))
            else:  # Branco
                resultados.append(("branco", numero))

        return resultados

    except Exception as e:
        print("Erro ao pegar resultados:", e)
        return []

def monitorar():
    global ultimo_resultado, gale_count, entrada

    while True:
        resultados = pegar_resultados()
        if not resultados:
            time.sleep(5)
            continue

        cor, numero = resultados[0]  # Último resultado
        if cor != ultimo_resultado:
            ultimo_resultado = cor
            print(f"Novo resultado detectado: {cor} ({numero})")

            # Lógica de entradas
            if entrada:
                if cor == entrada:
                    bot.send_message(CHAT_ID, f"✅ GREEN no {cor.upper()}!")
                    entrada, gale_count = None, 0
                else:
                    if gale_count < 2:
                        gale_count += 1
                        bot.send_message(CHAT_ID, f"⚠️ Gale {gale_count} no {entrada.upper()}!")
                    else:
                        bot.send_message(CHAT_ID, f"❌ RED no {entrada.upper()}!")
                        entrada, gale_count = None, 0

            # Detecta padrões para entrada
            cores = [r[0] for r in resultados[:3]]
            if cores[0] == cores[1] and cores[0] in ["vermelho", "preto"]:
                entrada = "preto" if cores[0] == "vermelho" else "vermelho"
                gale_count = 0
                bot.send_message(CHAT_ID, f"🎯 Entrar no {entrada.upper()}!\nPadrão detectado: 2 {cores[0].upper()} seguidos")

        time.sleep(8)

# === INÍCIO ===
if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🤖 Bot iniciado e monitorando padrões no Blaze Double!")
    monitorar()
