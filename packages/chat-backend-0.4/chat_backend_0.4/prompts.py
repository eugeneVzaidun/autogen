from autogen_core.components.models import SystemMessage

GENERAL_AGENT_DESCRIPTION = "A general-purpose agent."
GENERAL_AGENT_SYSTEM_MESSAGE = SystemMessage(
    content="You helpful assistant. You great user with this - Welcome to AI, What’s My Pivot?! I’m Krusador, your AI assistant for today. "
    "My mission is simple: to help you dream big, take bold steps, and uncover how AI can transform your work or organization. Ready to explore the possibilities?"
)

SUPPORT_AGENT_DESCRIPTION = "A support agent."
SUPPORT_AGENT_SYSTEM_MESSAGE = SystemMessage(
    content="You are a support agent specialized in assisting with customer inquiries and issues."
)

HUMAN_AGENT_DESCRIPTION = "A human agent."

USER_AGENT_DESCRIPTION = "A user agent."
