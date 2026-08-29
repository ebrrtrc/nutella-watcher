import json
import os
import sys
import time
from playwright.sync_api import sync_playwright
import urllib.request
import urllib.parse

URL = "https://www.nutella.com/tr/tr/xp/mutlulugapuan/hediyeler/"
STATE_FILE = "state.json"

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram bilgileri eksik, mesaj gönderilemedi.")
        print(text)
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "false",
    }).encode()
    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
    except Exception as e:
        print(f"Telegram gönderim hatası: {e}")


def scrape_gifts():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ))
        page.goto(URL, wait_until="networkidle", timeout=60000)

        # Cookie banner'ı kapatmayı dene (varsa)
        try:
            page.click("text=Kabul", timeout=4000)
        except Exception:
            pass

        # Ürün kartlarının render olmasını bekle
        page.wait_for_selector('[class*="product_product__"]', timeout=30000)
        # Sayfa lazy-load yapıyor olabilir, biraz aşağı kaydırıp bekleyelim
        for _ in range(6):
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(500)
        page.wait_for_timeout(1500)

        cards = page.query_selector_all('[class*="product_product__"]')
        gifts = []
        for card in cards:
            class_attr = card.get_attribute("class") or ""
            if "product_productBody" in class_attr:
                # yanlış seçici eşleşmesi olabilir, atla
                continue
            name_el = card.query_selector('[class*="product_name__"]')
            name = name_el.inner_text().strip() if name_el else None
            if not name:
                continue
            out_of_stock = (
                "product_disabled__" in class_attr
                or card.query_selector('[class*="product_noStock__"]') is not None
            )
            gifts.append({"name": name, "out_of_stock": out_of_stock})

        browser.close()
        return gifts


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def main():
    gifts = scrape_gifts()
    if not gifts:
        print("UYARI: Hiç hediye bulunamadı, site yapısı değişmiş olabilir.")
        sys.exit(0)

    prev_state = load_state()
    new_state = {}
    messages = []

    for g in gifts:
        name = g["name"]
        out_of_stock = g["out_of_stock"]
        new_state[name] = out_of_stock

        if name not in prev_state:
            # Daha önce görülmemiş yeni bir hediye
            if out_of_stock:
                messages.append(f"🆕 Yeni hediye eklendi (şu an tükenmiş): <b>{name}</b>")
            else:
                messages.append(f"🆕🎁 Yeni hediye eklendi ve STOKTA: <b>{name}</b>")
        else:
            was_out = prev_state[name]
            if was_out and not out_of_stock:
                messages.append(f"🎉 STOĞA GİRDİ: <b>{name}</b>\n{URL}")

    if messages:
        text = "\n\n".join(messages)
        send_telegram(text)
        print("Bildirim gönderildi:\n" + text)
    else:
        print("Değişiklik yok.")

    save_state(new_state)


if __name__ == "__main__":
    main()
