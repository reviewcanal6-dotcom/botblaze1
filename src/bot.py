import requests
from bs4 import BeautifulSoup
import time
import telebot

# === CONFIGURAÇÕES DO TELEGRAM ===
TOKEN = "8064880951:AAG2t9sq6PwOeQpMnDWgTI-DuvGj5QBhdLU"
CHAT_ID = "-1002550073701"
bot = telebot.TeleBot(TOKEN)

# === FUNÇÃO PARA PEGAR RESULTADOS DA BLAZE ===
def get_results():
    url = "https://blaze.com/pt/games/double"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Busca todos os elementos com os números
    results = []
    for cell in soup.find_all("div", class_="cell"):
        number_tag = cell.find("div", class_="cell__result")
        if number_tag:
            num = int(number_tag.text.strip())
            results.append(num)

    return results[:10]  # retorna os últimos 10 resultados

# === CONVERTER NÚMERO PARA COR ===
def get_color(num):
    if num == 0:
        return "BRANCO"
    elif 1 <= num <= 7:
        return "VERMELHO"
    elif 8 <= num <= 14:
        return "PRETO"

# === MONITORAR PADRÕES ===
def monitor():
    last_checked = None
    gale_count = 0
    entrada = None

    bot.send_message(CHAT_ID, "🤖 Bot iniciado e monitorando padrões no Blaze Double!")

    while True:
        try:
            results = get_results()
            if not results:
                continue

            ultimo = results[0]  # número mais recente
            if ultimo != last_checked:  # só reage a novo resultado
                last_checked = ultimo
                cor = get_color(ultimo)

                # Verifica padrão: 2 da mesma cor
                if get_color(results[1]) == get_color(results[0]) and cor != "BRANCO":
                    entrada = "PRETO" if cor == "VERMELHO" else "VERMELHO"
                    gale_count = 0
                    bot.send_message(CHAT_ID, f"🎯 Entrada detectada: Apostar no {entrada}")

                # Se tiver entrada em andamento
                if entrada:
                    if cor == entrada:
                        bot.send_message(CHAT_ID, f"✅ GREEN no {entrada}!")
                        entrada = None
                    else:
                        gale_count += 1
                        if gale_count <= 2:
                            bot.send_message(CHAT_ID, f"⚠️ Gale {gale_count} - Continuar no {entrada}")
                        else:
                            bot.send_message(CHAT_ID, f"❌ RED no {entrada}")
                            entrada = None
                            gale_count = 0

            time.sleep(10)  # espera 10s antes de checar de novo
        except Exception as e:
            bot.send_message(CHAT_ID, f"Erro no loop: {e}")
            time.sleep(15)

# === INICIAR MONITORAMENTO ===
if __name__ == "__main__":
    monitor()
