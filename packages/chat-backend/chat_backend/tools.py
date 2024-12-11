from autogen_core.components.tools import FunctionToolAlias

general_agent_topic_type = "GeneralAgent"
support_agent_topic_type = "SupportAgent"
escalation_agent_topic_type = "EscalationAgent"
human_agent_topic_type = "HumanAgent"
user_topic_type = "User"


def execute_task(task_name: str, parameters: dict) -> str:
    print(f"\n\n=== Task Execution ===")
    print(f"Task: {task_name}")
    print(f"Parameters: {parameters}")
    print("======================\n")
    confirm = input("Confirm task execution? y/n: ").strip().lower()
    if confirm == "y":
        print("Task execution successful!")
        return "Success"
    else:
        print("Task cancelled!")
        return "User cancelled task."


def lookup_resource(query: str) -> str:
    resource_id = "resource_abcdef123"
    print("Found resource:", resource_id)
    return resource_id


def process_refund(resource_id: str, reason: str = "not provided") -> str:
    print(f"\n\n=== Refund Processing ===")
    print(f"Resource ID: {resource_id}")
    print(f"Reason: {reason}")
    print("========================\n")
    print("Refund processed successfully!")
    return "success"


def delegate_to_general_agent() -> str:
    return "GeneralAgent"


def delegate_to_support_agent() -> str:
    return "SupportAgent"


def delegate_back_to_escalation() -> str:
    return "EscalationAgent"


def escalate_to_human_agent() -> str:
    return "HumanAgent"


execute_task_tool = FunctionToolAlias(execute_task, description="Execute a specified task with given parameters.")
lookup_resource_tool = FunctionToolAlias(lookup_resource, description="Retrieve resource ID based on the search query.")
process_refund_tool = FunctionToolAlias(process_refund, description="Process a refund for a given resource.")
delegate_to_general_agent_tool = FunctionToolAlias(
    delegate_to_general_agent, description="Delegate task to a general agent."
)
delegate_to_support_agent_tool = FunctionToolAlias(
    delegate_to_support_agent, description="Delegate task to a support agent."
)
delegate_back_to_escalation_tool = FunctionToolAlias(
    delegate_back_to_escalation,
    description="Delegate task back to escalation agent or another appropriate agent.",
)
escalate_to_human_agent_tool = FunctionToolAlias(escalate_to_human_agent, description="Escalate task to a human agent.")
