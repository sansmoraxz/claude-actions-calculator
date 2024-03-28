from actions import ToolRequest
from models import ClaudeMessage, ClaudeRole, ContentBlock
from utils import start_loop

# TOOL definations

def multiply(a: str, b: str) -> str:
    return str(int(a) * int(b))

def add(a: str, b: str) -> str:
    return str(int(a) + int(b))

def subtract(a: str, b: str) -> str:
    return str(int(a) - int(b))

def divide(a: str, b: str) -> str:
    return str(int(a) // int(b))

def power(a: str, b: str) -> str:
    return str(int(a) ** int(b))

def log(a: str, b: str) -> str:
    import math
    return str(math.log(int(a), int(b)))



def get_tools() -> list[ToolRequest]:
    return [
        ToolRequest(
            tool_name="Multiply",
            tool_description="Multiply two numbers",
            tool_function=multiply
        ),
        ToolRequest(
            tool_name="Add",
            tool_description="Add two numbers",
            tool_function=add
        ),
        ToolRequest(
            tool_name="Subtract",
            tool_description="Subtract two numbers",
            tool_function=subtract
        ),
        ToolRequest(
            tool_name="Divide",
            tool_description="Divide two numbers",
            tool_function=divide
        ),
        ToolRequest(
            tool_name="Power",
            tool_description="Raise a number to the power of another",
            tool_function=power
        ),
        ToolRequest(
            tool_name="Log",
            tool_description="Take the logarithm of a number",
            tool_function=log
        ),
        
    ]

sys_prompt = open("sys_prompt.md", "r").read()
sys_prompt = sys_prompt.format(tools="\n".join([tool.get_tool_prompt() for tool in get_tools()]))

messages = [
        ClaudeMessage(role=ClaudeRole.SYSTEM, content=[ContentBlock(type='text', text=sys_prompt)]),
        ClaudeMessage(role=ClaudeRole.USER, content=[ContentBlock(type='text', text="Solve: 5 * 3 ^ 2 + 2 ^ 3 - 1")])
    ]

x, msgs = start_loop(messages, get_tools())

print(f'\n\n{x}\n\n')
