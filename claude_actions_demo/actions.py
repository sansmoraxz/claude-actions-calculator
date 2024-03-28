from pydantic import BaseModel
from typing import Callable


class ToolRequest(BaseModel):
    tool_name: str
    tool_description: str
    tool_function: Callable[[str], str]

    def get_tool_prompt(self) -> str:
        import inspect 
        sigs = inspect.signature(self.tool_function)
        inputs_str = [f"<{k}>Parameter input</{k}>" for k, v in sigs.parameters.items()]
        return f"""
### {self.tool_name}

{self.tool_description}

```xml
<Action>
    <Name>{self.tool_name}</Name>
    <Inputs>{''.join(inputs_str)}</Inputs>
</Action>
```
"""

def invoke_action(xml: str, tools: list[ToolRequest]) -> str:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml)
        tool_name = root.find("Name").text
        inputs = root.find("Inputs")
        tool = next(tool for tool in tools if tool.tool_name == tool_name)
        return tool.tool_function(
            **{input.tag: input.text for input in inputs}
        )
