from claude_actions_demo.actions import ToolRequest
from claude_actions_demo.models import ClaudeMessage, ClaudeRole, ContentBlock
from claude_actions_demo.utils import start_loop
import pathlib

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


def main(problem: str = "Solve: 5 * 3 ^ 2 + 2 ^ 3 - 1"):
    f = pathlib.Path(__file__).parent / "sys_prompt.md"
    sys_prompt = open(f, "r").read()
    sys_prompt = sys_prompt.format(tools="\n".join([tool.get_tool_prompt() for tool in get_tools()]))
    messages = [
        ClaudeMessage(role=ClaudeRole.SYSTEM, content=[ContentBlock(type='text', text=sys_prompt)]),
        ClaudeMessage(role=ClaudeRole.USER, content=[ContentBlock(type='text', text=problem)])
    ]

    x, msgs = start_loop(messages, get_tools())
    print(f'\n\n{x}\n\n')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem", type=str)
    args = parser.parse_args()
    main(args.problem)
