import os
import telebot
from dotenv import load_dotenv

# Загружаем переменные
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(BOT_TOKEN)

def format_digest(emails: list[dict]) -> str:
    """Группирует письма по категориям и красиво форматирует текст для Telegram."""
    if not emails:
        return "📭 Новых писем нет."

    # Разделяем письма по категориям
    important = [e for e in emails if e['category'] == 'Important']
    normal = [e for e in emails if e['category'] == 'Normal']
    not_important = [e for e in emails if e['category'] == 'Not important']

    # Собираем текст сообщения
    message_lines = ["📬 *Ваш новый почтовый дайджест:*\n"]

    if important:
        message_lines.append("🔴 *ВАЖНОЕ:*")
        for email in important:
            message_lines.append(f"• *{email['subject']}*\n  _{email['summary']}_")
        message_lines.append("") # Пустая строка для отступа

    if normal:
        message_lines.append("🟡 *Обычное:*")
        for email in normal:
            message_lines.append(f"• {email['subject']} - {email['summary']}")
        message_lines.append("")

    if not_important:
        # Неважные письма просто считаем, чтобы не засорять экран
        message_lines.append(f"⚪ *Неважное (рассылки/спам):* {len(not_important)} шт.")

    # Объединяем все строки в один текст
    return "\n".join(message_lines)

def send_digest(chat_id: str, text: str) -> None:
    """Отправляет готовый текст в Telegram с поддержкой Markdown."""
    try:
        # parse_mode="Markdown" позволяет использовать жирный текст и курсив
        bot.send_message(chat_id, text, parse_mode="Markdown")
        print("✅ Дайджест успешно отправлен!")
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")

# Блок для тестирования
if __name__ == "__main__":
    # Создаем фейковые письма по нашему "контракту"
    fake_emails = [
        {
            "subject": "Собеседование в Яндекс", 
            "summary": "Приглашение на техническое интервью во вторник в 15:00.", 
            "category": "Important"
        },
        {
            "subject": "Оплата за интернет", 
            "summary": "Счет за август сформирован, к оплате 500 сомов.", 
            "category": "Normal"
        },
        {
            "subject": "Скидки в Steam", 
            "summary": "Распродажа на выходных.", 
            "category": "Not important"
        },
        {
            "subject": "Дайджест новостей Python", 
            "summary": "Вышел новый фреймворк.", 
            "category": "Not important"
        }
    ]

    # Проверяем работу логики
    digest_text = format_digest(fake_emails)
    send_digest(CHAT_ID, digest_text)