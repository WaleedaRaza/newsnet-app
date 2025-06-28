from typing import Dict, List
import re

class UniversalRelevanceScorer:
    def __init__(self):
        # Universal relevance patterns that work for any topic
        self.relevance_indicators = {
            "depth": ["analysis", "investigation", "study", "research", "report", "examination", "review", "assessment", "evaluation"],
            "context": ["background", "history", "context", "overview", "summary", "explanation", "description"],
            "evidence": ["evidence", "proof", "data", "statistics", "facts", "findings", "conclusions", "results"],
            "expertise": ["expert", "authority", "specialist", "professional", "academic", "scholar", "researcher"],
            "timeliness": ["recent", "latest", "current", "new", "updated", "breaking", "developing"]
        }
    
    def calculate_relevance_score(self, article_content: str, topic: str, user_view: str) -> float:
        """
        Calculate relevance score for ANY topic using universal metrics
        """
        print(f"🔍 UNIVERSAL RELEVANCE: Scoring article for topic: '{topic}'")
        
        # 1. Topic presence (how much the article mentions the topic)
        topic_presence = self._calculate_topic_presence(article_content, topic)
        
        # 2. Contextual relevance (how well it matches the user's context)
        contextual_relevance = self._calculate_contextual_relevance(article_content, user_view)
        
        # 3. Depth of coverage (how thoroughly it covers the topic)
        depth_score = self._calculate_depth_score(article_content, topic)
        
        # 4. Source credibility (universal source scoring)
        source_credibility = self._calculate_source_credibility(article_content)
        
        # 5. Content quality indicators
        quality_score = self._calculate_quality_score(article_content)
        
        # Combine scores with weights
        final_score = (
            topic_presence * 0.35 +
            contextual_relevance * 0.25 +
            depth_score * 0.20 +
            source_credibility * 0.10 +
            quality_score * 0.10
        )
        
        print(f"🔍 UNIVERSAL RELEVANCE: Scores - Topic: {topic_presence:.3f}, Context: {contextual_relevance:.3f}, Depth: {depth_score:.3f}, Source: {source_credibility:.3f}, Quality: {quality_score:.3f}")
        print(f"🔍 UNIVERSAL RELEVANCE: Final score: {final_score:.3f}")
        
        return min(final_score, 1.0)
    
    def _calculate_topic_presence(self, content: str, topic: str) -> float:
        """Calculate how prominently the topic appears in the content"""
        content_lower = content.lower()
        topic_lower = topic.lower()
        
        # Count exact matches
        exact_matches = content_lower.count(topic_lower)
        
        # Count related terms (simple word variations)
        related_terms = self._get_related_terms(topic)
        related_matches = sum(content_lower.count(term.lower()) for term in related_terms)
        
        # Count mentions in title vs body (title mentions are more important)
        title_end = content.find('\n') if '\n' in content else len(content)
        title_content = content[:title_end].lower()
        title_matches = title_content.count(topic_lower) * 2  # Weight title matches more
        
        # Normalize by content length
        total_mentions = exact_matches + related_matches + title_matches
        content_length = len(content.split())
        
        if content_length == 0:
            return 0.0
        
        # Score based on mentions per 100 words
        mentions_per_100 = (total_mentions / content_length) * 100
        
        # Cap at reasonable level (5 mentions per 100 words = max score)
        return min(mentions_per_100 / 5.0, 1.0)
    
    def _get_related_terms(self, topic: str) -> List[str]:
        """Get related terms for any topic"""
        # Simple approach: add common suffixes/prefixes
        related = [topic]
        
        # Add plural forms
        if not topic.endswith('s'):
            related.append(topic + 's')
        
        # Add common prefixes/suffixes
        prefixes = ['anti-', 'pro-', 'non-', 'pre-', 'post-', 're-', 'un-', 'dis-']
        suffixes = ['-ism', '-ist', '-ic', '-al', '-ive', '-able', '-ible']
        
        for prefix in prefixes:
            related.append(prefix + topic)
        
        for suffix in suffixes:
            related.append(topic + suffix)
        
        return related
    
    def _calculate_contextual_relevance(self, content: str, user_view: str) -> float:
        """Calculate how well the content matches the user's contextual interests"""
        if not user_view:
            return 0.5  # Neutral if no user view
        
        content_lower = content.lower()
        user_view_lower = user_view.lower()
        
        # Extract key words from user view
        user_words = [word for word in user_view_lower.split() if len(word) > 3]
        
        if not user_words:
            return 0.5
        
        # Count how many user words appear in content
        matches = sum(1 for word in user_words if word in content_lower)
        
        # Calculate overlap ratio
        overlap_ratio = matches / len(user_words)
        
        return overlap_ratio
    
    def _calculate_depth_score(self, content: str, topic: str) -> float:
        """Calculate how thoroughly the content covers the topic"""
        content_lower = content.lower()
        
        # Count depth indicators
        depth_indicators = 0
        for indicator in self.relevance_indicators["depth"]:
            if indicator in content_lower:
                depth_indicators += 1
        
        # Count context indicators
        context_indicators = 0
        for indicator in self.relevance_indicators["context"]:
            if indicator in content_lower:
                context_indicators += 1
        
        # Count evidence indicators
        evidence_indicators = 0
        for indicator in self.relevance_indicators["evidence"]:
            if indicator in content_lower:
                evidence_indicators += 1
        
        # Calculate total depth score
        total_indicators = depth_indicators + context_indicators + evidence_indicators
        max_possible = len(self.relevance_indicators["depth"]) + len(self.relevance_indicators["context"]) + len(self.relevance_indicators["evidence"])
        
        return total_indicators / max_possible if max_possible > 0 else 0.0
    
    def _calculate_source_credibility(self, content: str) -> float:
        """Calculate source credibility based on content indicators"""
        content_lower = content.lower()
        
        # Count expertise indicators
        expertise_indicators = 0
        for indicator in self.relevance_indicators["expertise"]:
            if indicator in content_lower:
                expertise_indicators += 1
        
        # Count timeliness indicators
        timeliness_indicators = 0
        for indicator in self.relevance_indicators["timeliness"]:
            if indicator in content_lower:
                timeliness_indicators += 1
        
        # Calculate credibility score
        total_indicators = expertise_indicators + timeliness_indicators
        max_possible = len(self.relevance_indicators["expertise"]) + len(self.relevance_indicators["timeliness"])
        
        return total_indicators / max_possible if max_possible > 0 else 0.5
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate overall content quality"""
        if not content:
            return 0.0
        
        # Word count (longer articles tend to be more comprehensive)
        word_count = len(content.split())
        length_score = min(word_count / 500, 1.0)  # Cap at 500 words
        
        # Check for structured content (paragraphs, lists, etc.)
        paragraphs = content.count('\n\n') + 1
        structure_score = min(paragraphs / 5, 1.0)  # Cap at 5 paragraphs
        
        # Check for quotes (indicates research/interviews)
        quote_count = content.count('"') // 2  # Rough estimate of quote pairs
        quote_score = min(quote_count / 3, 1.0)  # Cap at 3 quotes
        
        # Check for numbers/data (indicates factual content)
        number_count = len(re.findall(r'\d+', content))
        data_score = min(number_count / 10, 1.0)  # Cap at 10 numbers
        
        # Combine quality indicators
        quality_score = (
            length_score * 0.3 +
            structure_score * 0.3 +
            quote_score * 0.2 +
            data_score * 0.2
        )
        
        return quality_score 