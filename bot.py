import time
import requests
from bs4 import BeautifulSoup
import telebot

# Configurações fixas (se quiser depois dá pra passar pra variáveis de ambiente)
TOKEN = "8064880951:AAG2t9sq6PwOeQpMnDWgTI-DuvGj5QBhdLU"
CHAT_ID = "-1002550073701"
bot = telebot.TeleBot(TOKEN)

TIPMINER_URL = "https://www.tipminer.com/br/historico/blaze/double"

last_two = []
entrada_atual = None
gales = 0

def get_results_html():
    """Raspa os últimos resultados do Tipminer"""
    try:
        resp = requests.get(TIPMINER_URL, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        if resp.status_code != 200:
            print("Erro HTTP do Tipminer:", resp.status_code)
            return []
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        # Pega elementos que indicam as cores (ajustado pra várias possibilidades de classe)
        items = soup.find_all(["div","span","td"], class_=["red","black","white"])
        for it in items[:10]:  # últimos 10
            cls = it.get("class")
            cor = None
            if "red" in cls:
                cor = "vermelho"
            elif "black" in cls:
                cor = "preto"
            elif "white" in cls:
                cor = "branco"
            if cor:
                results.append(cor)
        return results
    except Exception as e:
        print("Erro scraping:", e)
        return []

def send_msg(txt):
    """Manda mensagem no Telegram"""
    try:
        bot.send_message(CHAT_ID, txt, parse_mode="HTML")
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def check_and_signal():
    """Verifica padrões e dispara sinais"""
    global last_two, entrada_atual, gales

    results = get_results_html()
    if not results:
        print("Nenhum resultado captado")
        return

    print("Resultados captados:", results[:5])

    # 2 últimos
    two = results[0:2]

    if two == last_two:
        return
    last_two = two

    if entrada_atual is None:
        if two == ["vermelho", "vermelho"]:
            entrada_atual = "preto"
            gales = 0
            send_msg("🎯 Entrada detectada!\nCor: ⚫ PRETO (2 vermelhos seguidos)\n🔁 Até 2 gales")
        elif two == ["preto", "preto"]:
            entrada_atual = "vermelho"
            gales = 0
            send_msg("🎯 Entrada detectada!\nCor: 🔴 VERMELHO (2 pretos seguidos)\n🔁 Até 2 gales")
    else:
        novo = results[0]
        if novo == entrada_atual:
            send_msg(f"✅ GREEN! Acertamos no {entrada_atual.upper()}")
            entrada_atual = None
            gales = 0
        else:
            if gales < 2:
                gales += 1
                send_msg(f"⚠️ Gale {gales} ativado! Continuar no {entrada_atual.upper()}")
            else:
                send_msg(f"❌ RED! Não bateu em 2 gales. Entrada {entrada_atual.upper()}")
                entrada_atual = None
                gales = 0

def main():
    send_msg("🤖 Bot iniciado e monitorando padrões no Blaze Double!")
    print("Bot rodando...")
    while True:
        try:
            check_and_signal()
        except Exception as e:
            print("Erro no loop:", e)
        time.sleep(12)

if __name__ == "__main__":
    main()
