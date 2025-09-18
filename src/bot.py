import time
import requests
import telebot

# CONFIGURAÇÕES DO TELEGRAM
TOKEN = "8064880951:AAG2t9sq6PwOeQpMnDWgTI-DuvGj5QBhdLU"
CHAT_ID = "-1002550073701"
bot = telebot.TeleBot(TOKEN)

# API pública da Blaze
BLAZE_API = "https://blaze.com/api/roulette_games/recent"

# Envia mensagem pro grupo
def send_message(text):
    try:
        bot.send_message(CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

# Converte cor numérica da API
def get_color_name(color):
    if color == 0:
        return "⚪ Branco"
    elif color == 1:
        return "🔴 Vermelho"
    elif color == 2:
        return "⚫ Preto"
    return "❓ Desconhecido"

# Lógica principal
def main():
    send_message("🤖 Bot iniciado e monitorando padrões no Blaze Double!")

    ultimos = []   # Armazena os últimos resultados
    entrada = None # Cor que o bot mandou apostar
    gales = 0      # Contador de gales

    while True:
        try:
            resp = requests.get(BLAZE_API)
            jogos = resp.json()

            if not jogos:
                time.sleep(5)
                continue

            ultimo = jogos[0]
            cor = ultimo["color"]
            numero = ultimo["roll"]
            resultado = get_color_name(cor)

            # Se for resultado novo, processa
            if not ultimos or ultimo["id"] != ultimos[0]["id"]:
                ultimos.insert(0, ultimo)
                ultimos = ultimos[:10]  # guarda só últimos 10

                print(f"Novo resultado: {numero} - {resultado}")

                # Se já tinha entrada em andamento
                if entrada:
                    if cor == entrada:
                        send_message("✅ GREEN! 🎉")
                        entrada = None
                        gales = 0
                    else:
                        if gales < 2:
                            gales += 1
                            send_message(f"❌ Deu ruim! Fazendo GALE {gales}...")
                        else:
                            send_message("❌ RED! Encerrando entrada.")
                            entrada = None
                            gales = 0

                # Detecta padrão (2 seguidas mesma cor)
                if not entrada and len(ultimos) >= 2:
                    c1 = ultimos[0]["color"]
                    c2 = ultimos[1]["color"]

                    if c1 == 1 and c2 == 1:  # 2 vermelhos
                        entrada = 2  # aposta no preto
                        send_message("🎯 Padrão detectado!\n➡️ Entre no ⚫ Preto\n🎲 Proteção ⚪ Branco")
                    elif c1 == 2 and c2 == 2:  # 2 pretos
                        entrada = 1  # aposta no vermelho
                        send_message("🎯 Padrão detectado!\n➡️ Entre no 🔴 Vermelho\n🎲 Proteção ⚪ Branco")

        except Exception as e:
            print("Erro no loop:", e)

        time.sleep(8)  # checa a cada 8s


if __name__ == "__main__":
    main()
