# Getting Started with LangGraph: Building Stateful Agents

*Generated on: 2025-07-03 15:41:30*

*Source: Create a tutorial from the documentation at https://langchain-ai.github.io/langgraph/*

---

## 1. Introduction to LangGraph

```markdown
# Introduction to LangGraph

## What is LangGraph?

LangGraph is a powerful orchestration framework designed for building stateful, long-running agents and workflows. Trusted by companies like Klarna, Replit, and Elastic, it provides the foundation for creating sophisticated AI systems that can maintain context, handle complex tasks, and interact with users over extended periods.

## Core Benefits

LangGraph offers several key advantages for agent development:

1. **Durable Execution**: Build agents that persist through failures and can run for extended periods, automatically resuming from where they left off.

2. **Human-in-the-Loop**: Seamlessly incorporate human oversight by inspecting and modifying agent state at any point during execution.

3. **Comprehensive Memory**: Create truly stateful agents with both short-term working memory and long-term persistent memory across sessions.

4. **Production-Ready**: Deploy sophisticated agent systems with scalable infrastructure designed for stateful workflows.

## Ecosystem Positioning

While LangGraph can be used standalone, it integrates seamlessly with the broader LangChain ecosystem:

- **LangChain**: Provides integrations and composable components for LLM application development
- **LangSmith**: Offers debugging and observability tools for complex agent behavior
- **LangGraph Platform**: A deployment platform for managing and scaling agents in production

LangGraph is particularly well-suited for applications requiring:
- Multi-step reasoning
- Dynamic workflow adaptation
- Persistent conversation history
- Human approval workflows
- Integration with external tools and APIs

## Key Concepts

At its core, LangGraph models agent workflows as graphs composed of:
- **State**: A shared data structure representing the current system snapshot
- **Nodes**: Functions containing your agent's logic
- **Edges**: Connections that determine the flow between nodes

This architecture enables you to build complex, looping workflows that evolve state over time while maintaining full control over your agent's behavior.
```

## 2. Installation and Setup

```markdown
# Installation and Setup

## Prerequisites

Before installing LangGraph, ensure you have:
- Python 3.11 or later
- pip package manager
- An API key for your preferred LLM provider (Anthropic, OpenAI, etc.)

## Installing LangGraph

Install the core LangGraph package using pip:

```bash
pip install -U langgraph
```

For full functionality including LLM integrations, install with optional dependencies:

```bash
pip install -U "langgraph[anthropic]"  # For Anthropic models
# or
pip install -U "langgraph[openai]"     # For OpenAI models
```

## Verifying Your Installation

After installation, verify everything works by creating a simple agent:

```python
from langgraph.prebuilt import create_react_agent

# Simple tool example
def dummy_tool(query: str) -> str:
    return f"Processed: {query}"

agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[dummy_tool],
    prompt="You are a helpful assistant"
)

response = agent.invoke(
    {"messages": [{"role": "user", "content": "test message"}]}
)
print(response)
```

## Configuration

Set your API keys as environment variables:

```bash
export ANTHROPIC_API_KEY='your-api-key'
# or
export OPENAI_API_KEY='your-api-key'
```

## Troubleshooting

If you encounter issues:
1. Check Python version (`python --version`)
2. Verify pip is up to date (`pip install --upgrade pip`)
3. Ensure your API keys are properly set
4. Consult the [LangGraph documentation](https://langchain-ai.github.io/langgraph/) for version-specific notes

For production environments, consider using a dependency manager like `uv` for faster, more reliable installations:

```bash
uv pip install --python=3.11 "langgraph[anthropic]"
```

Now you're ready to start building with LangGraph!
```

## 3. Creating Your First Agent

# Creating Your First Agent

In this section, we'll walk through building your first agent using LangGraph's prebuilt components. This will give you a hands-on introduction to creating stateful agents without needing to build everything from scratch.

## Prerequisites

Before we begin, ensure you have:
1. Python 3.11+ installed
2. LangGraph installed (`pip install -U langgraph`)
3. An Anthropic API key (or other supported LLM provider)

## Step 1: Import Required Components

```python
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
```

## Step 2: Define Your Tools

Tools are functions your agent can call to perform actions. Let's create a simple weather lookup tool:

```python
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    if city.lower() == "san francisco":
        return "Sunny with a high of 65°F"
    return f"Weather information unavailable for {city}"
```

## Step 3: Initialize Your LLM

```python
# For Anthropic (requires langchain[anthropic])
llm = init_chat_model("anthropic:claude-3-7-sonnet-latest", temperature=0)
```

## Step 4: Create the Agent

Combine your LLM and tools into an agent:

```python
agent = create_react_agent(
    model=llm,
    tools=[get_weather],
    prompt="You are a helpful weather assistant"
)
```

## Step 5: Run Your Agent

Invoke the agent with a user message:

```python
response = agent.invoke({
    "messages": [{
        "role": "user", 
        "content": "What's the weather in San Francisco?"
    }]
})
```

## Understanding the Response

The agent will return a dictionary containing:
- `messages`: The conversation history
- Potentially a `structured_response` if configured
- Any custom state fields you've defined

## Adding Memory (Optional)

To enable multi-turn conversations, add a checkpointer:

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
agent = create_react_agent(
    model=llm,
    tools=[get_weather],
    checkpointer=checkpointer
)

# Use thread_id to maintain conversation state
config = {"configurable": {"thread_id": "123"}}
agent.invoke({"messages": [{"role": "user", "content": "Hi!"}]}, config)
```

## Next Steps

You've now created a basic agent! In the next sections, we'll explore:
- Customizing the agent's behavior
- Building more complex workflows
- Adding advanced features like human review

Try experimenting with different tools and prompts to see how they affect your agent's behavior.

## 4. Understanding Graph Concepts

# Understanding Graph Concepts

LangGraph models agent workflows as graphs composed of three fundamental components that work together to create stateful, controllable agents. Let's explore each concept in detail:

## State: The Shared Memory

The `State` is a shared data structure representing your application's current snapshot:
- Typically defined as a `TypedDict` or Pydantic `BaseModel`
- Contains all variables your nodes need to access and modify
- Persists throughout the execution of your graph

```python
from typing import Annotated, TypedDict
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # Message history
    user_preferences: dict  # User-specific settings
    session_data: dict  # Temporary session information
```

## Nodes: The Workers

Nodes are Python functions that contain your agent's logic:
- Receive the current `State` as input
- Perform computations or side effects
- Return updates to the `State`

```python
def process_user_input(state: AgentState):
    """Node to handle user input"""
    last_message = state["messages"][-1]
    processed = analyze_message(last_message)
    return {"messages": [processed], "session_data": {"last_processed": now()}}
```

## Edges: The Decision Makers

Edges determine the flow between nodes:
- **Normal edges**: Fixed transitions from one node to another
- **Conditional edges**: Dynamic routing based on state

```python
from langgraph.graph import StateGraph

builder = StateGraph(AgentState)

# Add nodes
builder.add_node("process_input", process_user_input)
builder.add_node("generate_response", generate_response)

# Fixed edge
builder.add_edge("process_input", "generate_response")

# Conditional edge
def should_escalate(state):
    if state["session_data"].get("needs_human"):
        return "human_review"
    return "generate_response"

builder.add_conditional_edges("process_input", should_escalate)
```

## Reducers: State Update Handlers

Reducers control how state updates are applied:
- Each state key can have its own reducer
- Default is overwrite behavior
- Custom reducers enable merging strategies

```python
from operator import add

class AgentState(TypedDict):
    message_count: Annotated[int, add]  # Will sum values
    message_history: Annotated[list, lambda x,y: x + y]  # Will concatenate
    current_status: str  # Will overwrite
```

### Key Takeaways:
1. **State** is your application's shared memory
2. **Nodes** contain your business logic
3. **Edges** control workflow routing
4. **Reducers** manage state updates

These components work together to create flexible, stateful agent workflows that can handle complex, multi-step processes while maintaining full control over execution flow.

## 5. Building Custom Workflows

# Building Custom Workflows

LangGraph's true power emerges when you move beyond prebuilt agents and start creating custom workflows tailored to your specific needs. This section will guide you through building stateful agent workflows from scratch.

## Defining Your State Schema

The foundation of any LangGraph workflow is its state. The state represents all the data your workflow needs to operate:

```python
from typing import TypedDict, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class WorkflowState(TypedDict):
    # Messages will be appended, not overwritten
    messages: Annotated[list, add_messages]
    # Other state variables will overwrite previous values
    user_query: str
    search_results: list[str]
```

## Creating Nodes

Nodes are the building blocks of your workflow - they contain the actual logic:

```python
def retrieve_information(state: WorkflowState):
    # Your retrieval logic here
    results = search_web(state["user_query"])
    return {"search_results": results}

def generate_response(state: WorkflowState):
    # Your generation logic here
    response = llm.invoke({
        "messages": state["messages"],
        "context": state["search_results"]
    })
    return {"messages": [response]}
```

## Building the Graph

Combine your nodes into a functional workflow:

```python
from langgraph.graph import StateGraph, START, END

# Initialize the graph builder
builder = StateGraph(WorkflowState)

# Add nodes
builder.add_node("retriever", retrieve_information)
builder.add_node("generator", generate_response)

# Define the workflow path
builder.add_edge(START, "retriever")
builder.add_edge("retriever", "generator")
builder.add_edge("generator", END)

# Compile the graph
workflow = builder.compile()
```

## Using Reducers for State Management

Reducers control how state updates are applied:

```python
from operator import add

class StateWithCounter(TypedDict):
    messages: Annotated[list, add_messages]
    call_count: Annotated[int, add]  # Will sum values

def counting_node(state: StateWithCounter):
    return {"call_count": 1}  # Each call adds 1 to the total
```

## Conditional Workflows

Add branching logic to your workflows:

```python
def should_retry(state: WorkflowState):
    if needs_more_info(state["messages"][-1]):
        return "retriever"
    return END

builder.add_conditional_edges(
    "generator",
    should_retry,
    {"retriever": "retriever", END: END}
)
```

## Compiling and Running

Finalize and test your workflow:

```python
# Invoke with initial state
result = workflow.invoke({
    "user_query": "What's the weather in SF?",
    "messages": [{"role": "user", "content": "What's the weather in SF?"}]
})

# Stream intermediate steps
for step in workflow.stream(initial_state, stream_mode="updates"):
    print(step)
```

This framework gives you complete control to design sophisticated agent workflows while LangGraph handles the state management and execution logic.

## 6. Advanced Features

```markdown
# Advanced Features

LangGraph provides several powerful features that enable building sophisticated, production-ready agents. In this section, we'll explore three key capabilities: durable execution, human-in-the-loop workflows, and memory management.

## Durable Execution

Durable execution allows your agents to persist through failures and run for extended periods by automatically saving state at key points. This means:

- Agents can resume exactly where they left off after interruptions
- Long-running workflows can span hours or days
- State is preserved across system restarts

**Key components:**
- `Checkpointer`: Saves and restores agent state
- `StateGraph`: Manages the workflow state schema
- `Command`: Handles state updates and control flow

Example of enabling durable execution:
```python
from langgraph.checkpoint.memory import MemorySaver

# Create a checkpointer
checkpointer = MemorySaver()

# Compile graph with checkpointer
graph = builder.compile(checkpointer=checkpointer)

# Run with thread_id for state tracking
config = {"configurable": {"thread_id": "123"}}
graph.invoke(inputs, config=config)
```

## Human-in-the-Loop

LangGraph makes it easy to incorporate human oversight into your agent workflows:

- Pause execution at any point for human review
- Modify agent state before continuing
- Approve or reject actions like API calls

**Implementation patterns:**
1. **Approval Gates**: Interrupt before critical actions
2. **State Inspection**: Allow humans to view and modify state
3. **Tool Validation**: Review tool calls before execution

Example of adding an approval checkpoint:
```python
def should_approve(state):
    return "approve" if human_review_passed() else "reject"

builder.add_conditional_edges(
    "critical_node",
    should_approve,
    {"approve": "next_node", "reject": "correction_node"}
)
```

## Memory Management

LangGraph provides comprehensive memory capabilities:

**Short-term Memory**:
- Maintains conversation history within a session
- Uses message reducers to manage context window size
- Persisted via checkpointer

**Long-term Memory**:
- Stores information across sessions
- Supports semantic search over memories
- Organized by custom namespaces

Example memory configuration:
```python
from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    # Short-term memory
    messages: Annotated[list, add_messages]
    
    # Long-term memory key
    user_profile: dict

# Access memories in nodes
def recall_memory(state: State):
    relevant_memories = memory_store.search(
        namespace=("user123", "preferences"),
        query=state["messages"][-1].content
    )
    return {"context": relevant_memories}
```

These advanced features enable you to build robust, adaptable agents that can handle complex real-world scenarios while maintaining control and observability.
```

## 7. Deployment and Monitoring

```markdown
# Deployment and Monitoring

## Deploying Your LangGraph Agents

Once you've built your agent, you'll want to deploy it for production use. LangGraph provides several deployment options:

### Local Deployment
For testing and development, you can run your agent locally:
```python
graph = builder.compile()
result = graph.invoke({"input": "your_input"})
```

### LangGraph Platform
For production deployments, consider using the LangGraph Platform which provides:
- Scalable infrastructure for long-running agents
- Built-in persistence and checkpointing
- Easy integration with LangSmith

```python
# Deploy using the LangGraph CLI
langgraph deploy my_agent.py
```

### Container Deployment
Package your agent as a Docker container for flexible deployment:
```dockerfile
FROM python:3.11
RUN pip install langgraph
COPY your_agent.py .
CMD ["python", "your_agent.py"]
```

## Monitoring with LangSmith

LangSmith provides powerful observability tools for your agents:

### Tracing Agent Execution
- View complete execution traces of your agent's decisions
- Inspect state changes at each step
- Visualize the graph traversal path

### Performance Monitoring
- Track latency and token usage
- Identify bottlenecks in your workflow
- Monitor tool call success rates

### Debugging Tools
- Replay specific executions
- Compare different runs
- Inspect intermediate states

```python
# Configure LangSmith (add to your agent setup)
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "my_agent_project"
```

## Best Practices for Production

1. **Set Recursion Limits**: Prevent infinite loops
   ```python
   graph.invoke(inputs, config={"recursion_limit": 25})
   ```

2. **Implement Checkpointing**: For long-running agents
   ```python
   from langgraph.checkpoint.memory import MemorySaver
   graph = builder.compile(checkpointer=MemorySaver())
   ```

3. **Enable Human Review**: For critical decisions
   ```python
   graph = builder.compile(interrupt_after=["approval_node"])
   ```

4. **Monitor Key Metrics**:
   - Success/failure rates
   - Average completion time
   - Tool usage statistics

By following these deployment and monitoring practices, you can ensure your LangGraph agents run reliably in production while maintaining visibility into their performance and behavior.
```

