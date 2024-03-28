from enum import Enum

from pydantic import BaseModel, Field, computed_field, model_validator


class ContentSource(BaseModel):
    """A content source."""

    type: str
    media_type: str
    data: str


class ContentBlock(BaseModel):
    """A content block."""

    type: str
    text: str | None = None
    source: ContentSource | None = None

    @model_validator(mode='after')
    def validate_content(self) -> 'ContentBlock':
        """Ensure that only one of text or source is provided."""
        if self.text is None and self.source is None:
            raise ValueError('One of text or source must be provided')
        if self.text is not None and self.source is not None:
            raise ValueError('Only one of text or source can be provided')
        return self


class ClaudeRole(str, Enum):
    """Roles for Claude."""

    USER = 'user'
    SYSTEM = 'system'
    ASSISTANT = 'assistant'


class ClaudeMessage(BaseModel):
    """A message from Claude."""

    role: ClaudeRole
    content: list[ContentBlock]

    # don't allow empty content
    @model_validator(mode='after')
    def validate_content(self) -> 'ClaudeMessage':
        if not self.content:
            raise ValueError('Content cannot be empty')
        return self


class LLMResponse(BaseModel):
    """Response from the language model."""

    contents: list[ContentBlock] = []
    input_token_count: int | None = None
    output_token_count: int | None = None
    stop_reason: str
    stop_sequence: str | None = None


class LLMInput(BaseModel):
    """Input to the language model."""

    stop_sequences: list[str] | None = None

    temperature: float | None = None
    max_tokens: int = 200
    top_p: float| None = None
    top_k: int| None = None

class AnthropicInput(LLMInput):
    """Input to the Anthropic model."""

    anthropic_version: str = 'bedrock-2023-05-31'

    inputs: list[ClaudeMessage] = Field(exclude=True)


    @computed_field
    def system(self) -> str | None:
        """Get the system message."""
        for message in self.inputs:
            if message.role == ClaudeRole.SYSTEM:
                return message.content if isinstance(message.content, str) else message.content[0].text
        return None

    @computed_field
    def messages(self) ->list[ClaudeMessage]:
        """Get the user and assistant messages."""
        return [
            message
            for message in self.inputs
            if message.role in (ClaudeRole.USER, ClaudeRole.ASSISTANT)
        ]

class AnthropicResponseUsage(BaseModel):
    """Usage information for the Anthropic model."""

    input_tokens: int
    output_tokens: int

class AnthropicResponse(BaseModel):
    """Response from the Anthropic model."""

    type: str
    role: ClaudeRole
    content: list[ContentBlock]

    stop_reason: str
    stop_sequence: str | None
    usage: AnthropicResponseUsage

    def to_llm_response(self) -> LLMResponse:
        """Convert to an LLMResponse."""
        return LLMResponse(
            contents=self.content,
            input_token_count=self.usage.input_tokens,
            output_token_count=self.usage.output_tokens,
            stop_reason=self.stop_reason,
            stop_sequence=self.stop_sequence,
        )