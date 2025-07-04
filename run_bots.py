import asyncio
from bot import send_message_with_buttons_manual


async def main():
    await send_message_with_buttons_manual(message_text="Эту новость надо проверить и принять решение о публикации")

if __name__ == "__main__":
    asyncio.run(main()) 