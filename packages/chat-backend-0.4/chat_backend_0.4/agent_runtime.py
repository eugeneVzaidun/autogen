import asyncio
from dataclasses import dataclass
from autogen_core.application import WorkerAgentRuntime
from autogen_core.base import MessageContext
from autogen_core.components import DefaultTopicId, RoutedAgent, default_subscription, message_handler


@dataclass
class MyMessage:
    content: str


@default_subscription
class MyAgent(RoutedAgent):
    def __init__(self, name: str) -> None:
        super().__init__("My agent")
        self._name = name
        self._counter = 0

    @message_handler
    async def my_message_handler(self, message: MyMessage, ctx: MessageContext) -> None:
        self._counter += 1
        if self._counter > 5:
            return
        content = f"{self._name}: Hello x {self._counter}"
        print(content)
        await self.publish_message(MyMessage(content=content), DefaultTopicId())


async def main():
    print("start worker 1")
    worker1 = WorkerAgentRuntime(host_address="localhost:50051")
    worker1.start()
    await MyAgent.register(worker1, "worker1", lambda: MyAgent("worker1"))

    print("start worker 2")
    worker2 = WorkerAgentRuntime(host_address="localhost:50051")
    worker2.start()
    await MyAgent.register(worker2, "worker2", lambda: MyAgent("worker2"))

    await worker2.publish_message(MyMessage(content="Hello!"), DefaultTopicId())
    await asyncio.sleep(5)


# Run the main function within an asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
