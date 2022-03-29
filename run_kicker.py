import asyncio

from SessionKicker import Kicker

kicker = Kicker()

if __name__ == "__main__":
    try:
        asyncio.run(kicker.run())
    except KeyboardInterrupt:
        print("\nPlease wait while sessions are cleaned up")
        asyncio.run(kicker.close())
