from typing import TypedDict, List, Optional, Annotated
import operator


class AgentState(TypedDict):
    query: str                                                  # Original user query
    subtasks: List[str]                                         # Planner's breakdown
    subtask: str                                                # Single task injected by Send
    research_results: Annotated[list[str], operator.add]        # Researcher's findings per subtask
    report: Optional[str]                                       # Final written report
    clientID: str                                               # clientID for client needed for websocket
    sources: Annotated[List[any], operator.add]                 # keep track of sources for citations
    subtask_index: int