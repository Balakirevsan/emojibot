from telethon import TelegramClient, events, functions, types
from colorama import init, Fore, Style
import asyncio
import os
from uuid import uuid4
import random  # Add this import

init()

# Telegram API credentials
API_ID = "22943962"
API_HASH = "b27e806732cd5cdffc330d762d35b238"
PHONE_NUMBER = "+48669446875"

# List of user IDs to track (replace with actual user IDs)
TARGET_USERS = [
    5252510673,  # Светлана
    1075156676,  # Ежик
    890755578,  # Полковник
    1669751044,  # Нина
    7113915202,  # я
    5169039455,  # Игорь
    194857723,  # Грек
]

# Emoji constants
CLOWN_EMOJI = "🤡"
CHRISTMAS_TREE_EMOJI = "🎄"
HAND_SHAKE_EMOJI = "🤝"
BANANA_EMOJI = "🍌"
SNOWMAN_EMOJI = "☃️"
BLITZ_EMOJI = "⚡️"
STONE_EMOJI = "🗿"
GREEK_STATUE_EMOJI = "🏛️"

# User-specific settings with emoji, reaction chance, delay range and remove_delay
USER_SETTINGS = {
    5252510673: {  # Светлана
        "emoji": CHRISTMAS_TREE_EMOJI,
        "chance": 0.17,
        "delay_range": (60, 180),
        "remove_delay": 30,  # Remove after 30 seconds
    },
    1075156676: {  # Ежик
        "emoji": HAND_SHAKE_EMOJI,
        "chance": 0.3,
        "delay_range": (120, 300),
        "remove_delay": None,  # Remove after 3 minutes
    },
    890755578: {  # Полковник
        "emoji": BANANA_EMOJI,
        "chance": 0.15,
        "delay_range": (30, 120),
        "remove_delay": 60,  # Remove after 1 minute
    },
    1669751044: {  # Нина
        "emoji": SNOWMAN_EMOJI,
        "chance": 0.25,
        "delay_range": (90, 240),
        "remove_delay": None,  # Don't remove reaction
    },
    7113915202: {  # я
        "emoji": BLITZ_EMOJI,
        "chance": 1,
        "delay_range": (10, 60),
        "remove_delay": 5,  # Remove after 30 seconds
    },
    5169039455: {  # Игорь
        "emoji": STONE_EMOJI,
        "chance": 0.1,
        "delay_range": (180, 600),
        "remove_delay": 60,  # Remove after 5 minutes
    },
    194857723: {  # Грек
        "emoji": GREEK_STATUE_EMOJI,
        "chance": 0.2,
        "delay_range": (60, 180),
        "remove_delay": 30,  # Remove after 2 minutes
    },
}

# Add constant for session name
SESSION_NAME = "saved_session"


async def react_to_messages(chat_id):
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    try:
        await client.start(phone=PHONE_NUMBER)
        print(f"{Fore.GREEN}Bot started! Watching for messages...{Style.RESET_ALL}")

        @client.on(events.NewMessage(chats=int(chat_id)))
        async def handler(event):
            try:
                # Skip additional parts of grouped media messages
                if event.message.grouped_id and not event.message.text:
                    return

                sender = await event.get_sender()
                sender_name = getattr(sender, "first_name", "") or getattr(
                    sender, "title", "Unknown"
                )

                if (
                    sender.id in USER_SETTINGS
                    and random.random() < USER_SETTINGS[sender.id]["chance"]
                ):
                    settings = USER_SETTINGS[sender.id]
                    emoji = settings["emoji"]
                    min_delay, max_delay = settings["delay_range"]
                    delay = random.randint(min_delay, max_delay)

                    print(
                        f"{Fore.YELLOW}Luck triggered! User {sender_name} sent a message. "
                        f"Chance: {settings['chance']*100}%, "
                        f"Will add {emoji} reaction after {delay} seconds...{Style.RESET_ALL}"
                    )
                    await asyncio.sleep(delay)

                    try:
                        # Add reaction using messages.sendReaction method
                        await client(
                            functions.messages.SendReactionRequest(
                                peer=event.message.peer_id,
                                msg_id=event.message.id,
                                reaction=[types.ReactionEmoji(emoticon=emoji)],
                            )
                        )
                        print(
                            f"{Fore.GREEN}Added {emoji} reaction to message from {sender_name}{Style.RESET_ALL}"
                        )

                        # Check if reaction should be removed
                        if settings.get("remove_delay"):
                            await asyncio.sleep(settings["remove_delay"])
                            # Remove reaction by sending empty reaction list
                            await client(
                                functions.messages.SendReactionRequest(
                                    peer=event.message.peer_id,
                                    msg_id=event.message.id,
                                    reaction=[],
                                )
                            )
                            print(
                                f"{Fore.CYAN}Removed {emoji} reaction from message by {sender_name} "
                                f"after {settings['remove_delay']} seconds{Style.RESET_ALL}"
                            )
                    except Exception as reaction_error:
                        print(
                            f"{Fore.RED}Error managing reaction: {str(reaction_error)}{Style.RESET_ALL}"
                        )

                elif sender.id in USER_SETTINGS:
                    settings = USER_SETTINGS[sender.id]
                    print(
                        f"{Fore.BLUE}Skipping reaction for {sender_name} "
                        f"(chance was {settings['chance']*100}%){Style.RESET_ALL}"
                    )

            except Exception as e:
                print(f"{Fore.RED}Error processing message: {str(e)}{Style.RESET_ALL}")

        # Keep the script running
        await client.run_until_disconnected()

    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    finally:
        await client.disconnect()
        # Remove the session file deletion code that was here before


if __name__ == "__main__":
    CHAT_ID = "-1001779469259"  # Replace with your chat ID

    try:
        asyncio.run(react_to_messages(CHAT_ID))
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Script stopped by user{Style.RESET_ALL}")
