"""
Semantic Embedding Service

This service handles embedding generation for articles and beliefs using HuggingFace models.
Features:
- Multiple embedding models (sentence-transformers, transformers)
- Batch processing for efficiency
- Similarity search and ranking
- Caching and optimization
- Comprehensive logging and metrics
"""

import asyncio
import logging
import time
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import os
import pickle
from pathlib import Path

# HuggingFace imports
try:
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer, AutoModel
    import torch
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    logging.warning("HuggingFace libraries not available - using mock embeddings")

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    """Result of an embedding operation"""
    text: str
    embedding: np.ndarray
    model_name: str
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class SimilarityResult:
    """Result of a similarity search"""
    query_text: str
    matches: List[Tuple[str, float]]  # (text, similarity_score)
    model_name: str
    processing_time: float
    total_candidates: int

class SemanticEmbeddingService:
    """
    Service for generating and managing semantic embeddings
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        
        # Initialize model
        self.model = None
        self.tokenizer = None
        self.device = "cpu"
        
        # Cache for embeddings
        self.embedding_cache = {}
        self.cache_file = Path("embedding_cache.pkl")
        
        # Metrics
        self.metrics = {
            'total_embeddings': 0,
            'successful_embeddings': 0,
            'failed_embeddings': 0,
            'cache_hits': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0
        }
        
        # Initialize the model
        self._initialize_model()
        
        # Load cache if exists
        self._load_cache()
        
        self.logger.info(f"Initialized SemanticEmbeddingService with model: {model_name}")
    
    def _initialize_model(self):
        """Initialize the HuggingFace model"""
        if not HUGGINGFACE_AVAILABLE:
            self.logger.warning("HuggingFace not available - using mock embeddings")
            return
        
        try:
            self.logger.info(f"Loading model: {self.model_name}")
            
            # Use sentence-transformers for better performance
            if "sentence-transformers" in self.model_name or self.model_name in [
                "all-MiniLM-L6-v2", "all-mpnet-base-v2", "multi-qa-MiniLM-L6-cos-v1"
            ]:
                self.model = SentenceTransformer(self.model_name)
                self.logger.info(f"Loaded SentenceTransformer: {self.model_name}")
            else:
                # Fallback to transformers
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModel.from_pretrained(self.model_name)
                self.logger.info(f"Loaded Transformers model: {self.model_name}")
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.device = "cuda"
                if hasattr(self.model, 'to'):
                    self.model = self.model.to(self.device)
                self.logger.info("Model moved to GPU")
            
            self.logger.info(f"Model initialization completed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize model {self.model_name}: {e}")
            self.model = None
    
    def _load_cache(self):
        """Load embedding cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'rb') as f:
                    self.embedding_cache = pickle.load(f)
                self.logger.info(f"Loaded {len(self.embedding_cache)} cached embeddings")
        except Exception as e:
            self.logger.warning(f"Failed to load cache: {e}")
            self.embedding_cache = {}
    
    def _save_cache(self):
        """Save embedding cache to disk"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.embedding_cache, f)
            self.logger.info(f"Saved {len(self.embedding_cache)} embeddings to cache")
        except Exception as e:
            self.logger.warning(f"Failed to save cache: {e}")
    
    def _generate_mock_embedding(self, text: str) -> np.ndarray:
        """Generate mock embedding for testing"""
        # Create a deterministic mock embedding based on text
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 384-dimensional vector (like all-MiniLM-L6-v2)
        embedding = np.zeros(384)
        for i, byte in enumerate(hash_bytes):
            embedding[i % 384] += byte / 255.0
        
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        return embedding
    
    async def embed_text(self, text: str, use_cache: bool = True) -> EmbeddingResult:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            EmbeddingResult with embedding and metadata
        """
        start_time = time.time()
        
        # Check cache first
        if use_cache and text in self.embedding_cache:
            self.metrics['cache_hits'] += 1
            cached_result = self.embedding_cache[text]
            return EmbeddingResult(
                text=text,
                embedding=cached_result['embedding'],
                model_name=self.model_name,
                processing_time=0.001,  # Very fast for cache hits
                success=True,
                metadata={'cached': True}
            )
        
        try:
            self.metrics['total_embeddings'] += 1
            
            if self.model is None:
                # Use mock embedding
                embedding = self._generate_mock_embedding(text)
                processing_time = time.time() - start_time
                
                result = EmbeddingResult(
                    text=text,
                    embedding=embedding,
                    model_name=f"{self.model_name}_mock",
                    processing_time=processing_time,
                    success=True,
                    metadata={'mock': True}
                )
            else:
                # Generate real embedding
                if hasattr(self.model, 'encode'):
                    # SentenceTransformer
                    embedding = self.model.encode(text, convert_to_numpy=True)
                else:
                    # Transformers
                    inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
                    if self.device == "cuda":
                        inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    with torch.no_grad():
                        outputs = self.model(**inputs)
                        # Use mean pooling
                        embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy().flatten()
                
                processing_time = time.time() - start_time
                
                result = EmbeddingResult(
                    text=text,
                    embedding=embedding,
                    model_name=self.model_name,
                    processing_time=processing_time,
                    success=True,
                    metadata={'model': self.model_name, 'embedding_dim': len(embedding)}
                )
            
            # Cache the result
            if use_cache:
                self.embedding_cache[text] = {
                    'embedding': result.embedding,
                    'model_name': result.model_name,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Update metrics
            self.metrics['successful_embeddings'] += 1
            self.metrics['total_processing_time'] += processing_time
            self.metrics['average_processing_time'] = (
                self.metrics['total_processing_time'] / self.metrics['successful_embeddings']
            )
            
            self.logger.debug(f"Generated embedding for text (length: {len(text)}) in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.metrics['failed_embeddings'] += 1
            
            self.logger.error(f"Failed to generate embedding for text: {e}")
            
            return EmbeddingResult(
                text=text,
                embedding=np.array([]),
                model_name=self.model_name,
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
    
    async def embed_batch(self, texts: List[str], use_cache: bool = True) -> List[EmbeddingResult]:
        """
        Generate embeddings for a batch of texts
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            List of EmbeddingResult objects
        """
        self.logger.info(f"Generating embeddings for batch of {len(texts)} texts")
        
        # Process in parallel
        tasks = [self.embed_text(text, use_cache) for text in texts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Batch embedding failed for text {i}: {result}")
                processed_results.append(EmbeddingResult(
                    text=texts[i],
                    embedding=np.array([]),
                    model_name=self.model_name,
                    processing_time=0.0,
                    success=False,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        successful_count = sum(1 for r in processed_results if r.success)
        self.logger.info(f"Batch embedding completed: {successful_count}/{len(texts)} successful")
        
        return processed_results
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Normalize vectors
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    async def find_similar_texts(
        self, 
        query_text: str, 
        candidate_texts: List[str], 
        top_k: int = 10,
        threshold: float = 0.3
    ) -> SimilarityResult:
        """
        Find the most similar texts to a query
        
        Args:
            query_text: The query text
            candidate_texts: List of candidate texts to compare against
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            SimilarityResult with ranked matches
        """
        start_time = time.time()
        
        self.logger.info(f"Finding similar texts for query (length: {len(query_text)})")
        self.logger.info(f"Comparing against {len(candidate_texts)} candidates")
        
        try:
            # Generate query embedding
            query_result = await self.embed_text(query_text)
            if not query_result.success:
                return SimilarityResult(
                    query_text=query_text,
                    matches=[],
                    model_name=self.model_name,
                    processing_time=time.time() - start_time,
                    total_candidates=len(candidate_texts)
                )
            
            # Generate candidate embeddings
            candidate_results = await self.embed_batch(candidate_texts)
            
            # Calculate similarities
            similarities = []
            for i, candidate_result in enumerate(candidate_results):
                if candidate_result.success:
                    similarity = self.calculate_similarity(
                        query_result.embedding, 
                        candidate_result.embedding
                    )
                    if similarity >= threshold:
                        similarities.append((candidate_texts[i], similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Take top_k results
            top_matches = similarities[:top_k]
            
            processing_time = time.time() - start_time
            
            self.logger.info(f"Found {len(top_matches)} similar texts above threshold {threshold}")
            if top_matches:
                self.logger.info(f"Top similarity: {top_matches[0][1]:.3f}")
            
            return SimilarityResult(
                query_text=query_text,
                matches=top_matches,
                model_name=self.model_name,
                processing_time=processing_time,
                total_candidates=len(candidate_texts)
            )
            
        except Exception as e:
            self.logger.error(f"Error in similarity search: {e}")
            return SimilarityResult(
                query_text=query_text,
                matches=[],
                model_name=self.model_name,
                processing_time=time.time() - start_time,
                total_candidates=len(candidate_texts)
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        return {
            'metrics': self.metrics.copy(),
            'model_name': self.model_name,
            'cache_size': len(self.embedding_cache),
            'model_available': self.model is not None,
            'device': self.device,
            'timestamp': datetime.now().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the embedding service"""
        try:
            # Test embedding generation
            test_result = await self.embed_text("test")
            
            return {
                'status': 'healthy' if test_result.success else 'degraded',
                'model_loaded': self.model is not None,
                'test_embedding_success': test_result.success,
                'embedding_dimension': len(test_result.embedding) if test_result.success else 0,
                'metrics': self.get_metrics()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'metrics': self.get_metrics()
            }
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self._save_cache()
            self.logger.info("Embedding service cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

# Global instance
semantic_embedding_service = SemanticEmbeddingService() 