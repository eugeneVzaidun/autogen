import asyncio
import signal
from autogen_core.application import WorkerAgentRuntimeHost
import logging


async def main():
    host = WorkerAgentRuntimeHost(address="localhost:50051")
    host.start()  # Start a host service in the background.
    await host.stop_when_signal(signals=[signal.SIGTERM, signal.SIGINT])  # Stop the host on termination signals.


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
