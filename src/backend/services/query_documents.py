from llama_index.core import VectorStoreIndex, PromptTemplate
from llama_index.core.response_synthesizers import CompactAndRefine
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from models.structured_response import RelationshipType
from llama_index.core.prompts import PromptTemplate
from models.structured_response import RelationshipType

def query_documents(query_str: str, index: VectorStoreIndex):
    # Define system prompt for structured output
    relationship_types_str = ", ".join([r.value for r in RelationshipType])

    # Define the template string with relationship types inserted
    system_prompt = PromptTemplate(
        f"""
        You are a precise and knowledgeable assistant specializing in bio-medical queries. Use the provided context to answer the query in a structured JSON format, extracting relevant information as per the instructions.

        **Instructions:**
        1. Extract relationships between entities (e.g., organisms, chemicals, proteins) using only the following relationship types:
        {relationship_types_str}
        2. Use exact entity names from the context, avoiding generic terms.
        3. Link relationships as pairs or triplets where applicable:
        - If an entity is isolated from an organism (`ISOLATED_FROM`), check if the same organism produces it (`PRODUCES`).
        - If a chemical is a metabolite (`METABOLITE_OF`) or precursor (`PRECURSOR_OF`), check for related biosynthetic relationships.
        4. Provide a concise natural language explanation summarizing the results.
        5. If the query’s answer or relationship type is not found, return an empty list of relationships and an explanation stating: "Not found in the provided context."
        6. Output the response as a JSON object conforming to the provided schema.

        **Context:**
        {{context_str}}

        **Query:**
        {{query_str}}
        """
    )

    # Create query engine with structured output
    vector_retriever = index.as_retriever(
        vector_store_query_mode="default",
        similarity_top_k=5,
    )
    text_retriever = index.as_retriever(
        vector_store_query_mode="sparse",
        similarity_top_k=5,
    )
    retriever = QueryFusionRetriever(
        [vector_retriever, text_retriever],
        similarity_top_k=5,
        num_queries=1,
        mode="relative_score",
        use_async=False,
    )

    response_synthesizer = CompactAndRefine()
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
    )

    query_engine.update_prompts(
        {"response_synthesizer:text_qa_template": system_prompt}
    )

    # Execute query and return structured response
    response = query_engine.query(query_str)
    return response
