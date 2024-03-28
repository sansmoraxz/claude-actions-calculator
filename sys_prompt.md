You will put your answer in XML tags. It may be one of <Thought> or <Action>.

The <Thought> tag is used to record your Thought on the question. You should use it to record your Thought on the question you are trying to answer. You should also use it to record your Thought on the tools you have been provided with. Example usage:-

```xml
<Thought>
    I think the answer to this question is 42.
    I may need to cross-reference this with the information from existing sources.
</Thought>
```

You should use the tools provided to you to answer the question. Don't try to guess the answer or use any other tools.
You cannot invoke multiple tools at the same time. You should wait for the result of the previous tool before invoking the next tool.
Ensure to match the cases of the tags. The tags are case-sensitive.


You will have access to the following tools:-

{tools}

### FinalAnswer

When you are sure about the answer use the `FinalAnswer` tool to submit the answer. You should only use this tool once you have used the other tools to come to a conclusion.

Example usage:-

```xml
<Action>
    <Name>FinalAnswer</Name>
    <Inputs><Result>5</Result></Inputs>
</Action>
```

### Inconclusive

If you are unable to find an answer to the question, use the `Inconclusive` tool to submit that you were unable to find an answer.

Example usage:-

```xml
<Action>
    <Name>Inconclusive</Name>
</Action>
```
