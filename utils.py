from typing import Literal
from models import AnthropicInput, AnthropicResponse, ClaudeMessage, ClaudeRole, ContentBlock
from actions import ToolRequest, invoke_action
import boto3

from termcolor import colored

region='us-east-1'

bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)

def invoke_anthropic(
        inp: AnthropicInput,
        model_name: str = 'anthropic.claude-3-haiku-20240307-v1:0',
) -> AnthropicResponse:
    """Invoke the language model."""
    body = inp.model_dump_json(exclude_none=True)

    response = bedrock_runtime.invoke_model(
        body=body,
        modelId=model_name,
        contentType='application/json',
        accept = '*/*',
    )
    return AnthropicResponse.model_validate_json(response['body'].read())

def add_message(
    messages: list[ClaudeMessage],
    message: ClaudeMessage,
) -> list[ClaudeMessage]:
    """Add a message to the list of messages."""
    if len(messages) == 0:
        return [message]
    elif messages[-1].role == message.role:
        if messages[-1].content[-1].type == 'text' and message.content[0].type == 'text':
            messages[-1].content[-1].text += '\n' + message.content[0].text
        else:
            messages[-1].content += message.content
        return messages
    else:
        return messages + [message]

def join_messages(
    messages1: list[ClaudeMessage],
    messages2: list[ClaudeMessage],
) -> list[ClaudeMessage]:
    """Join two lists of messages."""
    for message in messages2:
        messages1 = add_message(messages1, message)
    return messages1

def get_response_for_xml_tag(
    messages: list[ClaudeMessage],
    tag: Literal['Action', 'Thoughts'],
) -> tuple[str, list[ClaudeMessage]]:
    """Get the modifiable response by invoking the language model with the given wrapped tag.
    Args:
        model_name: The name of the language model.
        messages: The list of messages.
        tag: The tag to wrap the response in.
    Returns:
        The modifiable response and the updated list of messages.
    """
    # first add the tag to the messages to prefill the model output and guide the response
    messages = add_message(
        messages,
        ClaudeMessage(role=ClaudeRole.ASSISTANT, content=[ContentBlock(type='text', text=f'<{tag}>')])
    )

    resp = invoke_anthropic(
        AnthropicInput(
            inputs=messages,
            stop_sequences=[f'</{tag}>'], # stop the model when it reaches the closing tag
        ),
    ).to_llm_response()
    # TODO: assertion for stop sequence
    return (
        f'<{tag}>' + ''.join([block.text for block in resp.contents if block.text]) + f'</{tag}>\n',
        join_messages(
            messages,
            [
                ClaudeMessage(role=ClaudeRole.ASSISTANT, content=resp.contents),
                ClaudeMessage(role=ClaudeRole.ASSISTANT,
                              content=[ContentBlock(type='text', text=f'</{tag}>\n')]),
            ],
        )
    )

def get_action_response(
    messages: list[ClaudeMessage],
    action_str: str,
    tools: list[ToolRequest],
) -> tuple[str, list[ClaudeMessage]]:
    """Get the modifiable response by invoking the language model with the given action.
    Args:
        model_name: The name of the language model.
        messages: The list of messages.
        action: The action to perform.
    Returns:
        The enclosed response and the updated list of messages.
    """
    action_resp = invoke_action(action_str, tools)
    action_resp = f'<Observation>{action_resp}</Observation>\n'
    return (
        action_resp,
        add_message(
            messages,
            ClaudeMessage(role=ClaudeRole.USER, content=[ContentBlock(type='text', text=action_resp)]),
        ),
    )

def final_answer(Result: str) -> str:
    """Return the final answer."""
    return f"\nFinal answer is:-\n{Result}"

def is_final_answer(action_txt: str) -> bool:
    from xml.etree import ElementTree as ET
    root = ET.fromstring(action_txt)
    return root.find("Name").text == "FinalAnswer"


def slow_print(text: str, delay: float = 0.01) -> None:
    """Print text slowly."""
    import time
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def start_loop(
    messages: list[ClaudeMessage],
    tools: list[ToolRequest],
    n : int = 10,
) -> tuple[str, list[ClaudeMessage]]:
    """Start the loop."""
    for msg in messages:
        slow_print(colored(
                f'{msg.role.name}:',
                "magenta", attrs=["bold", "underline"]
            ), 0)
        slow_print(
            " " +
            colored(
                " ".join([block.text for block in msg.content]),
                "white", attrs=["dark"]
            ), 0.003
        )
    
    print(colored("\n\nStarting ReAct loop...\n\n", "yellow", attrs=["bold"]))
    i = 0
    while i < n:
        # get the llm response loops
        thoughts_resp, messages = get_response_for_xml_tag(messages, 'Thoughts')
        slow_print(colored(thoughts_resp, "red"), 0.01)
        action_resp, messages = get_response_for_xml_tag(messages, 'Action')
        slow_print(colored(action_resp, "green"), 0.001)
        # invoke action
        if is_final_answer(action_resp):
            act = invoke_action(action_resp, [
                ToolRequest(
                    tool_name="FinalAnswer",
                    tool_description="Provide the final answer",
                    tool_function=final_answer
                )
            ])
            return (
                act,
                messages,
            )
        act, messages = get_action_response(messages, action_resp, tools)

        slow_print(colored(act, "blue"), 0)
        i += 1
    print(colored("Loop ended", "yellow", attrs=["bold"]))
    return (
        'Loop ended',
        messages,
    )
