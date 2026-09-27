import logging
from langgraph.graph import StateGraph, END
from app.agents.state import FactCheckState
from app.agents.claim_extractor import claim_extractor_node
from app.agents.evidence_retriever import evidence_retriever_node
from app.agents.verdict_judge import verdict_judge_node
from app.agents.critic import critic_node, should_reflect
from app.agents.digest_writer import finalize_and_persist_node

logger = logging.getLogger("factcheck.graph")

def create_fact_check_graph():
    """Builds and compiles the LangGraph StateGraph with sequential pipeline and Critic reflection loop."""
    workflow = StateGraph(FactCheckState)
    
    # 1. Add agent nodes
    workflow.add_node("claim_extractor", claim_extractor_node)
    workflow.add_node("evidence_retriever", evidence_retriever_node)
    workflow.add_node("verdict_judge", verdict_judge_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("finalize", finalize_and_persist_node)
    
    # 2. Add sequential pipeline edges
    workflow.set_entry_point("claim_extractor")
    workflow.add_edge("claim_extractor", "evidence_retriever")
    workflow.add_edge("evidence_retriever", "verdict_judge")
    workflow.add_edge("verdict_judge", "critic")
    
    # 3. Add reflection loop conditional edge
    workflow.add_conditional_edges(
        "critic",
        should_reflect,
        {
            "evidence_retriever": "evidence_retriever",
            "finalize": "finalize"
        }
    )
    
    workflow.add_edge("finalize", END)
    
    compiled_app = workflow.compile()
    logger.info("LangGraph fact-checking pipeline successfully compiled.")
    return compiled_app

fact_check_app = create_fact_check_graph()
