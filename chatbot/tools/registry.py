from chatbot.tools.web_search import web_search


def get_tools():
    """Return every tool the chatbot agent is allowed to execute."""
    return [web_search]


def get_tool_map():
    tool_map = {}
    for tool in get_tools():
        tool_map[tool.name] = tool

    return tool_map
