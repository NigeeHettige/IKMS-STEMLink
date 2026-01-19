"""LangGraph orchestration for the linear multi-agent QA flow."""

from functools import lru_cache
from typing import Any, Dict, Optional

from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import InMemorySaver

from .agents import retrieval_node, summarization_node, verification_node, planner_node
from .state import QAState
import uuid

_checkpointer = None


def get_checkpointer():
    """Get or create the global checkpointer instance."""
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = InMemorySaver()
    return _checkpointer


def create_qa_graph() -> Any:
    """Create and compile the linear multi-agent QA graph.

    The graph executes in order:
    1. Retrieval Agent: gathers context from vector store
    2. Summarization Agent: generates draft answer from context
    3. Verification Agent: verifies and corrects the answer

    Returns:
        Compiled graph ready for execution.
    """
    builder = StateGraph(QAState)

    # Add nodes for each
    builder.add_node("planner", planner_node)
    builder.add_node("retrieval", retrieval_node)
    builder.add_node("summarization", summarization_node)
    builder.add_node("verification", verification_node)

    # Define linear flow: START -> retrieval -> summarization -> verification -> END
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "retrieval")
    builder.add_edge("retrieval", "summarization")
    builder.add_edge("summarization", "verification")
    builder.add_edge("verification", END)

    return builder.compile(checkpointer=get_checkpointer())


@lru_cache(maxsize=1)
def get_qa_graph() -> Any:
    """Get the compiled QA graph instance (singleton via LRU cache)."""
    return create_qa_graph()


def run_qa_flow(question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Run the complete multi-agent QA flow for a question.

    This is the main entry point for the QA system. It:
    1. Initializes the graph state with the question
    2. Executes the linear agent flow (Retrieval -> Summarization -> Verification)
    3. Extracts and returns the final results

    Args:
        question: The user's question about the vector databases paper.

    Returns:
        Dictionary with keys:
        - `answer`: Final verified answer
        - `draft_answer`: Initial draft answer from summarization agent
        - `context`: Retrieved context from vector store
    """

    thread_id = session_id if session_id else str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    graph = get_qa_graph()
    existing_state = graph.get_state(config)

    if existing_state and existing_state.values.get("messages"):
        messages = existing_state.values["messages"] + [
            {"role": "user", "content": question}
        ]
    else:
        messages = [{"role": "user", "content": question}]

    initial_state: QAState = {
        "plan": None,
        "sub_questions": None,
        "question": question,
        "context": None,
        "draft_answer": None,
        "answer": None,
        "messages": messages,
    }

    final_state = graph.invoke(initial_state, config)
    final_state["session_id"] = thread_id

    return final_state
