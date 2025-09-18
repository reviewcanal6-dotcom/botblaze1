import os
import time
import requests
from bs4 import BeautifulSoup
import telebot

# Configurações do Telegram
TOKEN = "8064880951:AAG2t9sq6PwOeQpMnDWgTI-DuvGj5QBhdLU"
CHAT_ID = "-1002550073701"
bot = telebot.TeleBot(TOKEN)

# URL do Tipminer (Blaze Double histórico)
URL = "https://www.tipminer.com/br/historico/blaze/double"

# Função para pegar os últimos resultados
def pegar_resultados():
    try:
        r = requests.get(URL)
        soup = BeautifulSoup(r.text, "html.parser")
        resultados = soup.find_all("div", class_="cell__result")
        numeros = [int(r.text.strip()) for r in resultados[:30]]  # pega últimos 30
        return numeros
    except Exception as e:
        print("Erro ao pegar resultados:", e)
        return []

# Converte número em cor
def numero_para_cor(numero):
    if numero == 0:
        return "Branco"
    elif 1 <= numero <= 7:
        return "Vermelho"
    elif 8 <= numero <= 14:
        return "Preto"
    return "Desconhecido"

# Monitorar padrões
def monitorar():
    enviados = set()
    bot.send_message(CHAT_ID, "🤖 Bot iniciado e monitorando padrões no Blaze Double!")

    while True:
        numeros = pegar_resultados()
        if len(numeros) < 3:
            time.sleep(10)
            continue

        cores = [numero_para_cor(n) for n in numeros]

        # últimos 2
        ultimos = cores[0:2]
        padrao = "-".join(ultimos)

        if padrao in enviados:
            time.sleep(10)
            continue

        entrada = None
        if ultimos[0] == "Vermelho" and ultimos[1] == "Vermelho":
            entrada = "Preto"
        elif ultimos[0] == "Preto" and ultimos[1] == "Preto":
            entrada = "Vermelho"

        if entrada:
            enviados.add(padrao)
            bot.send_message(
                CHAT_ID,
                f"🎯 Padrão detectado: {ultimos[0]} + {ultimos[1]}\n👉 Entrada no {entrada}\n📊 Até 2 gales"
            )

            # Monitorar próximos resultados para validar GREEN/RED
            tentativa = 0
            green = False
            while tentativa <= 2:  # entrada + 2 gales
                time.sleep(35)  # espera próximo giro (ajuste se necessário)
                novos = pegar_resultados()
                if not novos:
                    tentativa += 1
                    continue

                cor_atual = numero_para_cor(novos[0])
                if cor_atual == entrada:
                    bot.send_message(CHAT_ID, f"✅ GREEN no {entrada} ({'Gale ' + str(tentativa) if tentativa > 0 else 'Entrada'})")
                    green = True
                    break
                else:
                    tentativa += 1

            if not green:
                bot.send_message(CHAT_ID, f"❌ RED após 2 gales no {entrada}")

        time.sleep(10)

if __name__ == "__main__":
    monitorar()
