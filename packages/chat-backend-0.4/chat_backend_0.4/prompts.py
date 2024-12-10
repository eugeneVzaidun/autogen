from autogen_core.components.models import SystemMessage

GENERAL_AGENT_DESCRIPTION = "A general-purpose agent."
GENERAL_AGENT_SYSTEM_MESSAGE = SystemMessage(
    content="You are a versatile agent capable of handling various business workflows. "
    "Assist users by performing tasks, retrieving information, and escalating issues when necessary."
)

SUPPORT_AGENT_DESCRIPTION = "A support agent."
SUPPORT_AGENT_SYSTEM_MESSAGE = SystemMessage(
    content="You are a support agent specialized in assisting with customer inquiries and issues."
)

HUMAN_AGENT_DESCRIPTION = "A human agent."

USER_AGENT_DESCRIPTION = "A user agent."
