from telethon import TelegramClient, errors
from telethon.tl.functions.channels import LeaveChannelRequest, JoinChannelRequest
import asyncio
from colorama import init, Fore, Style
import time
import os
from uuid import uuid4

init()  # Initialize colorama

# Telegram API credentials
API_ID = "24478406"
API_HASH = "c5539fd8f6eba52c11c401a1b84a4bb5"
PHONE_NUMBER = "+4917642526381"


async def leave_and_join_loop(chat_id):
    # Create unique session name
    session_name = f"session_{uuid4().hex}"
    client = TelegramClient(session_name, API_ID, API_HASH)

    try:
        await client.start(phone=PHONE_NUMBER)
        print(f"{Fore.CYAN}Finding chat...{Style.RESET_ALL}")
        chat = await client.get_entity(int(chat_id))

        while True:
            try:
                print(f"\n{Fore.YELLOW}Leaving chat...{Style.RESET_ALL}")
                await client(LeaveChannelRequest(chat))
                print(f"{Fore.GREEN}Successfully left the chat!{Style.RESET_ALL}")

                print(f"{Fore.YELLOW}Joining chat...{Style.RESET_ALL}")
                await client(JoinChannelRequest(chat))
                print(f"{Fore.GREEN}Successfully joined the chat!{Style.RESET_ALL}")

            except errors.UserNotParticipantError:
                print(f"{Fore.YELLOW}Attempting to join chat...{Style.RESET_ALL}")
                await client(JoinChannelRequest(chat))
                print(f"{Fore.GREEN}Successfully joined the chat!{Style.RESET_ALL}")

            except errors.ChannelPrivateError:
                print(
                    f"{Fore.RED}Cannot access the chat. It might be private.{Style.RESET_ALL}"
                )
                break
            except Exception as e:
                print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
                break

            print(f"{Fore.CYAN}Waiting 10 seconds...{Style.RESET_ALL}")
            await asyncio.sleep(10)

    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    finally:
        await client.disconnect()
        # Cleanup session file
        try:
            session_file = f"{session_name}.session"
            if os.path.exists(session_file):
                os.remove(session_file)
        except Exception as e:
            print(f"{Fore.RED}Error cleaning up session: {str(e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    CHAT_ID = "-1001779469259"
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(leave_and_join_loop(CHAT_ID))
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Script stopped by user{Style.RESET_ALL}")
    finally:
        loop.close()
