from telethon import TelegramClient, errors
import asyncio
from datetime import datetime
import time
from tqdm import tqdm
from colorama import init, Fore, Style

init()  # Initialize colorama

# Telegram API credentials
API_ID = "24478406"
API_HASH = "c5539fd8f6eba52c11c401a1b84a4bb5"
PHONE_NUMBER = "+4917642526381"


async def delete_messages_batch(client, chat, messages):
    try:
        await client.delete_messages(chat, messages)
        return len(messages)
    except Exception as e:
        print(f"Error deleting batch: {e}")
        return 0


async def get_all_message_ids(client, chat, me):
    """Получение всех ID сообщений с использованием пакетной обработки"""
    all_messages = []
    date_counts = {}
    min_id = 0
    pbar = tqdm(desc="Scanning messages", unit="msg")

    while True:
        messages_chunk = []
        async for message in client.iter_messages(
            chat,
            from_user=me,
            min_id=min_id,  # Начинаем с последнего найденного ID
            limit=1000,  # Получаем по 1000 сообщений за раз
        ):
            messages_chunk.append(message)

        if not messages_chunk:
            break

        for message in messages_chunk:
            all_messages.append(message.id)
            message_date = message.date.strftime("%Y-%m-%d")
            date_counts[message_date] = date_counts.get(message_date, 0) + 1
            pbar.update(1)

            if len(all_messages) % 500 == 0:
                pbar.set_postfix(
                    {"Latest date": message_date, "Count": len(all_messages)}
                )

        min_id = max(msg.id for msg in messages_chunk)

    pbar.close()
    return all_messages, date_counts


async def delete_messages(chat_id, days_limit=None):
    client = TelegramClient("session_name", API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)

    try:
        chat = await client.get_entity(int(chat_id))
        me = await client.get_me()

        print(f"{Fore.CYAN}Fetching messages (including old ones)...{Style.RESET_ALL}")
        start_time = time.time()

        messages, date_counts = await get_all_message_ids(client, chat, me)

        if not messages:
            print(f"{Fore.YELLOW}No messages found to delete{Style.RESET_ALL}")
            return

        # Print statistics
        print(f"\n{Fore.GREEN}Message Statistics:{Style.RESET_ALL}")
        for date, count in sorted(date_counts.items()):
            print(f"{Fore.CYAN}{date}:{Style.RESET_ALL} {count} messages")
        print(
            f"\n{Fore.GREEN}Total messages to delete: {len(messages)}{Style.RESET_ALL}"
        )

        # Delete messages with optimized chunks
        chunk_size = 100
        chunks = [
            messages[i : i + chunk_size] for i in range(0, len(messages), chunk_size)
        ]

        with tqdm(total=len(messages), desc="Deleting messages", unit="msg") as pbar:
            for chunk in chunks:
                try:
                    await client.delete_messages(chat, chunk)
                    pbar.update(len(chunk))
                    await asyncio.sleep(0.5)
                except errors.FloodWaitError as e:
                    print(
                        f"\n{Fore.YELLOW}Rate limit hit. Waiting {e.seconds} seconds...{Style.RESET_ALL}"
                    )
                    await asyncio.sleep(e.seconds)
                    await client.delete_messages(chat, chunk)
                    pbar.update(len(chunk))

        elapsed_time = time.time() - start_time
        print(
            f"\n{Fore.GREEN}Successfully deleted {len(messages)} messages in {elapsed_time:.2f} seconds{Style.RESET_ALL}"
        )

    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    CHAT_ID = "-1001779469259"
    DAYS_LIMIT = None  # Удаляем все сообщения

    loop = asyncio.get_event_loop()
    loop.run_until_complete(delete_messages(CHAT_ID, DAYS_LIMIT))
