import time
import requests
import telebot

# CONFIGURAÇÕES DO TELEGRAM
TOKEN = "8064880951:AAG2t9sq6PwOeQpMnDWgTI-DuvGj5QBhdLU"
CHAT_ID = "-1002550073701"
bot = telebot.TeleBot(TOKEN)

# API pública da Blaze
BLAZE_API = "https://blaze.com/api/roulette_games/recent"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Envia mensagem pro grupo
def send_message(text):
    try:
        bot.send_message(CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def get_color_name(color):
    if color == 0:
        return "⚪ Branco"
    elif color == 1:
        return "🔴 Vermelho"
    elif color == 2:
        return "⚫ Preto"
    return "❓ Desconhecido"

def main():
    send_message("🤖 Bot iniciado e monitorando API da Blaze (modo DEBUG)!")
    ultimos_ids = set()

    while True:
        try:
            resp = requests.get(BLAZE_API, headers=HEADERS)

            # DEBUG: mostra a resposta crua da API no grupo
            send_message(f"DEBUG API:\n{resp.text[:500]}")

            jogos = resp.json()

            if not jogos:
                time.sleep(5)
                continue

            ultimo = jogos[0]
            if ultimo["id"] not in ultimos_ids:
                ultimos_ids.add(ultimo["id"])
                numero = ultimo["roll"]
                cor = ultimo["color"]
                resultado = get_color_name(cor)

                send_message(f"🎲 Novo resultado: {numero} - {resultado}")

        except Exception as e:
            send_message(f"Erro no loop: {e}")

        time.sleep(10)

if __name__ == "__main__":
    main()
