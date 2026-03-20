from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    query: str                        # Original user query
    subtasks: List[str]               # Planner's breakdown
    research_results: List[str]       # Researcher's findings per subtask
    report: Optional[str]             # Final written report
