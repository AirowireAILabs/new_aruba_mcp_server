"""
Semantic Tool Filter for Aruba Central MCP Server

Uses sentence-transformers and FAISS for semantic similarity search to filter
90 tools down to the most relevant 5-8 tools based on user query.
"""

import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
import faiss

from tool_registry import TOOL_REGISTRY


class SemanticToolFilter:
    """
    Semantic filter that uses embeddings and cosine similarity to find
    the most relevant tools for a given query.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", min_relevance: float = 0.15):
        """
        Initialize the semantic tool filter.
        
        Args:
            model_name: Sentence transformer model to use (runs 100% locally)
            min_relevance: Minimum cosine similarity threshold for relevance
        """
        self.model_name = model_name
        self.min_relevance = min_relevance
        
        # Load the sentence transformer model
        print(f"Loading sentence transformer model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        # Build the tool index
        self._build_index()
        print(f"Tool filter initialized with {len(self.tool_names)} tools")
    
    def _build_index(self):
        """Build FAISS index from tool descriptions."""
        self.tool_names = list(TOOL_REGISTRY.keys())
        
        # Create rich text descriptions for better semantic matching
        tool_texts = []
        for tool_name in self.tool_names:
            metadata = TOOL_REGISTRY[tool_name]
            # Combine description and keywords for richer context
            text = f"{metadata['description']} Keywords: {', '.join(metadata['keywords'])}"
            tool_texts.append(text)
        
        # Generate embeddings
        print("Generating embeddings for all tools...")
        self.tool_embeddings = self.model.encode(tool_texts, convert_to_numpy=True)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.tool_embeddings)
        
        # Create FAISS index
        dimension = self.tool_embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product = cosine similarity with normalized vectors
        self.index.add(self.tool_embeddings)
    
    def filter(self, query: str, top_k: int = 8) -> List[str]:
        """
        Filter tools to find the most relevant ones for a query.
        
        Args:
            query: User query to search for relevant tools
            top_k: Number of top tools to return
            
        Returns:
            List of tool names, ordered by relevance
        """
        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Search for similar tools
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Filter by minimum relevance threshold
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score >= self.min_relevance:
                results.append(self.tool_names[idx])
        
        return results
    
    def filter_with_scores(self, query: str, top_k: int = 8) -> List[Tuple[str, float]]:
        """
        Filter tools and return with relevance scores for debugging.
        
        Args:
            query: User query to search for relevant tools
            top_k: Number of top tools to return
            
        Returns:
            List of (tool_name, score) tuples, ordered by relevance
        """
        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Search for similar tools
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Filter by minimum relevance threshold and return with scores
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score >= self.min_relevance:
                results.append((self.tool_names[idx], float(score)))
        
        return results


if __name__ == "__main__":
    """Test the semantic tool filter with example queries."""
    
    print("\n" + "=" * 80)
    print("Semantic Tool Filter Test")
    print("=" * 80)
    
    # Initialize filter
    filter = SemanticToolFilter()
    
    # Test queries
    test_queries = [
        "Show me all wireless networks",
        "List devices in inventory",
        "Create a new site location",
        "Check firmware upgrade status",
        "What rogue access points were detected?",
        "Assign licenses to my devices",
        "Get the running configuration for a switch",
        "Show me the network topology",
        "Create a new user account",
        "Get audit logs for configuration changes"
    ]
    
    print("\n" + "-" * 80)
    for query in test_queries:
        print(f"\nQuery: \"{query}\"")
        print("-" * 80)
        
        # Get filtered tools with scores
        results = filter.filter_with_scores(query, top_k=8)
        
        print(f"Top {len(results)} relevant tools:")
        for i, (tool_name, score) in enumerate(results, 1):
            metadata = TOOL_REGISTRY[tool_name]
            print(f"  {i}. {tool_name} (score: {score:.3f}, category: {metadata['category']})")
            print(f"     {metadata['description'][:80]}...")
    
    print("\n" + "=" * 80)
    print("Semantic filtering reduces 90 tools to 5-8 relevant tools per query!")
    print("This allows small local LLMs to work effectively with the MCP server.")
    print("=" * 80)
