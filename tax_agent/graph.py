"""Tax Agent LangGraph definition.

Uses create_react_agent with a tax-specialised system prompt.
No tools — it answers purely from LLM knowledge.
"""

from __future__ import annotations

from langgraph.prebuilt import create_react_agent

from common.llm import get_llm

TAX_SYSTEM_PROMPT = """You are a specialist tax attorney and CPA.

Answer tax questions clearly and concisely. Focus on the most relevant
civil and criminal consequences, the main IRS/FinCEN/DOJ agencies involved,
and whether the liability belongs to the company, executives, or both.

Keep your response short and practical: prefer 3-5 bullet points or a brief
paragraph rather than a long essay.

Always note that your response is for educational purposes and the user
should consult a licensed attorney for specific legal advice.
"""


def create_graph():
    """Return a compiled LangGraph create_react_agent for tax questions."""
    llm = get_llm()
    graph = create_react_agent(
        model=llm,
        tools=[],
        prompt=TAX_SYSTEM_PROMPT,
    )
    return graph
