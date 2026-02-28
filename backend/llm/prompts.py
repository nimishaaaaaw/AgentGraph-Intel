"""
Prompt templates for all LLM interactions in AgentGraph Intel.
"""

# ---------------------------------------------------------------------------
# RAG answer generation
# ---------------------------------------------------------------------------

RAG_ANSWER_PROMPT = """\
You are a knowledgeable research assistant. Answer the question based *only* on \
the provided context. If the context does not contain enough information, say so clearly.

Question: {question}

Context:
{context}

Answer:\
"""

# ---------------------------------------------------------------------------
# Entity extraction
# ---------------------------------------------------------------------------

ENTITY_EXTRACTION_PROMPT = """\
Extract named entities from the following text. For each entity provide:
- name: the entity name as it appears in the text
- type: one of PERSON, ORGANIZATION, LOCATION, TECHNOLOGY, CONCEPT, EVENT, PRODUCT, DATE
- description: a brief description (1 sentence max)

Return ONLY a JSON array of objects. No explanation.

Text:
{text}

JSON:\
"""

# ---------------------------------------------------------------------------
# Relationship extraction
# ---------------------------------------------------------------------------

RELATIONSHIP_EXTRACTION_PROMPT = """\
Given the following entities and source text, identify meaningful relationships \
between the entities.

Entities:
{entities_json}

Text:
{text}

For each relationship provide:
- source: entity name
- target: entity name
- relationship: relationship type in UPPER_SNAKE_CASE (e.g. WORKS_AT, PART_OF, CREATED_BY)
- description: one-sentence description

Return ONLY a JSON array. No explanation.

JSON:\
"""

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

ANALYSIS_PROMPT = """\
You are an expert research analyst. Based on the following information, provide a \
comprehensive analysis.

User Query: {query}

Retrieved Documents:
{docs_text}

Knowledge Graph Context:
{kg_context}

Initial RAG Answer:
{rag_answer}

Please provide:
1. A thorough analysis addressing the query
2. Key insights and patterns identified
3. Supporting evidence from the sources
4. Any limitations or caveats

Analysis:\
"""

# ---------------------------------------------------------------------------
# Final synthesis
# ---------------------------------------------------------------------------

SYNTHESIS_PROMPT = """\
Based on the research and analysis below, provide a clear and comprehensive answer \
to the user's question.

Question: {query}

Research Findings: {rag_answer}

Analysis: {analysis}

Knowledge Graph Insights: {kg_context}

Provide a well-structured, accurate answer with appropriate citations where relevant.

Answer:\
"""

# ---------------------------------------------------------------------------
# Conversation (chat with history)
# ---------------------------------------------------------------------------

CHAT_SYSTEM_PROMPT = """\
You are AgentGraph Intel, an expert AI research assistant. You have access to:
- A curated knowledge base of documents
- A knowledge graph of entities and their relationships
- Advanced retrieval and analysis capabilities

Be helpful, accurate, and cite your sources when possible.\
"""

CHAT_WITH_CONTEXT_PROMPT = """\
{system_prompt}

Conversation History:
{history}

Relevant Context:
{context}

User: {query}
Assistant:\
"""
