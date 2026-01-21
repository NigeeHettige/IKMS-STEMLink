"""Agent implementations for the multi-agent RAG flow.

This module defines three LangChain agents (Retrieval, Summarization,
Verification) and thin node functions that LangGraph uses to invoke them.
"""

from typing import List

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from ..llm.factory import create_chat_model
from .prompts import (
    RETRIEVAL_SYSTEM_PROMPT,
    SUMMARIZATION_SYSTEM_PROMPT,
    VERIFICATION_SYSTEM_PROMPT,
    PLANNER_SYSTEM_PROMPT,
)
from .state import QAState
from .tools import retrieval_tool


def _extract_last_ai_content(messages: List[object]) -> str:
    """Extract the content of the last AIMessage in a messages list."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            return str(msg.content)
    return ""


def _parse_plan_and_subquestions(content: str) -> tuple[str | None, list[str] | None]:
    """Parse plan and sub-questions from the AI response content."""
    if not content:
        return None, None

    plan_lines = []
    sub_questions = []

    lines = content.split("\n")
    in_plan = False
    in_subq = False

    for line in lines:
        line = line.strip()

        if line.startswith("plan:"):
            in_plan = True
            in_subq = False
            continue
        elif line.startswith("sub_questions:"):
            in_plan = False
            in_subq = True
            continue

        if in_plan and line and line[0].isdigit():
            plan_lines.append(line)
        elif in_subq and line.startswith("-"):
            query = line.strip("- ").strip('"')
            sub_questions.append(query)

    plan = "\n".join(plan_lines) if plan_lines else None
    subqs = sub_questions if sub_questions else None

    return plan, subqs


# Define agents at module level for reuse
planner_agent = create_agent(
    model=create_chat_model(),
    tools=[],
    system_prompt=PLANNER_SYSTEM_PROMPT,
)

retrieval_agent = create_agent(
    model=create_chat_model(),
    tools=[retrieval_tool],
    system_prompt=RETRIEVAL_SYSTEM_PROMPT,
)

summarization_agent = create_agent(
    model=create_chat_model(),
    tools=[],
    system_prompt=SUMMARIZATION_SYSTEM_PROMPT,
)

verification_agent = create_agent(
    model=create_chat_model(),
    tools=[],
    system_prompt=VERIFICATION_SYSTEM_PROMPT,
)


def planner_node(state: QAState) -> QAState:
    """Planning Agent node: analyzes and decomposes user questions.

    This node:
    - Sends the user's question to the Planning Agent
    - The agent identifies ambiguities and key entities
    - Decomposes complex questions into focused sub-questions
    - Generates a structured search plan for retrieval
    - Stores the plan in `state["plan"]` and sub-questions in `state["sub_questions"]`
    """
    question = state["question"]
    messages_history = state.get("messages", [])
    
    agent_messages = []
    
    
    for msg in messages_history[-6:]:
        if msg["role"] == "user":
            agent_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            agent_messages.append(AIMessage(content=msg["content"]))
            
    agent_messages.append(HumanMessage(content=question))
    
    result = planner_agent.invoke({"messages": agent_messages})

    messages = result.get("messages", [])
    content = _extract_last_ai_content(messages)
    plan, sub_questions = _parse_plan_and_subquestions(content)
    
  
    return {
        "plan": plan,
        "sub_questions":sub_questions
    }
 

   


def retrieval_node(state: QAState) -> QAState:
    """Retrieval Agent node: gathers context from vector store.

    This node:
    - Sends the user's question to the Retrieval Agent.
    - The agent uses the attached retrieval tool to fetch document chunks.
    - Extracts the tool's content (CONTEXT string) from the ToolMessage.
    - Stores the consolidated context string in `state["context"]`.
    """
    question = state["question"]
    plan = state["plan"]
    sub_questions = state["sub_questions"]
    messages_history = state.get("messages", [])
    
    
    formatted_subqs = '\n'.join(f"- {sq}" for sq in sub_questions) if sub_questions else "None"
    
    context_note = ""
    if len(messages_history) >= 2:
      
        last_answer = next(
            (msg["content"] for msg in reversed(messages_history) 
             if msg["role"] == "assistant"),
            None
        )
        if last_answer:
            context_note = f"\n[Previous answer excerpt: {last_answer[:200]}...]\n"
    
    user_content = f"""{context_note}Question: {question}

Plan:
{plan}

Sub-Questions:
{formatted_subqs}"""
   
    result = retrieval_agent.invoke({"messages": [HumanMessage(content=user_content)]})
    

    messages = result.get("messages", [])
    context = ""

    
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            context = str(msg.content)
            break
 
    return {
        "context": context,
    }


def summarization_node(state: QAState) -> QAState:
    """Summarization Agent node: generates draft answer from context.

    This node:
    - Sends question + context to the Summarization Agent.
    - Agent responds with a draft answer grounded only in the context.
    - Stores the draft answer in `state["draft_answer"]`.
    """
    question = state["question"]
    context = state.get("context")

    user_content = f"Question: {question}\n\nContext:\n{context}"

    result = summarization_agent.invoke(
        {"messages": [HumanMessage(content=user_content)]}
    )
    messages = result.get("messages", [])
    draft_answer = _extract_last_ai_content(messages)

    return {
        "draft_answer": draft_answer,
    }


def verification_node(state: QAState) -> QAState:
    """Verification Agent node: verifies and corrects the draft answer.

    This node:
    - Sends question + context + draft_answer to the Verification Agent.
    - Agent checks for hallucinations and unsupported claims.
    - Stores the final verified answer in `state["answer"]`.
    """
    question = state["question"]
    context = state.get("context", "")
    draft_answer = state.get("draft_answer", "")

    user_content = f"""Question: {question}

Context:
{context}

Draft Answer:
{draft_answer}

Please verify and correct the draft answer, removing any unsupported claims."""

    result = verification_agent.invoke(
        {"messages": [HumanMessage(content=user_content)]}
    )
    messages = result.get("messages", [])
    answer = _extract_last_ai_content(messages)

    return {
        "answer": answer,
        "messages": [{"role": "assistant", "content": answer}]
    }
