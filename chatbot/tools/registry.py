from chatbot.tools.web_search import web_search


def get_tools():
    """Return every tool the chatbot agent is allowed to execute."""
    return [web_search]


def get_tool_map():
    return {tool.name: tool for tool in get_tools()}
