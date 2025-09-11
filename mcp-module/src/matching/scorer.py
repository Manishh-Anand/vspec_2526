"""
Confidence Scorer
Scores matching confidence for MCP capabilities
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class MatchScore:
    """Match score information"""
    score: float
    confidence: float
    reasoning: str
    factors: Dict[str, float]


class ConfidenceScorer:
    """MCP Confidence Scorer"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def score_tool_match(self, requirement: Dict[str, Any], capability: Dict[str, Any]) -> MatchScore:
        """Score a tool match"""
        try:
            score = 0.0
            factors = {}
            
            # Name similarity
            name_similarity = self._calculate_name_similarity(
                requirement.get('name', ''),
                capability.get('name', '')
            )
            factors['name_similarity'] = name_similarity
            score += name_similarity * 0.3
            
            # Description similarity
            desc_similarity = self._calculate_description_similarity(
                requirement.get('description', ''),
                capability.get('description', '')
            )
            factors['description_similarity'] = desc_similarity
            score += desc_similarity * 0.4
            
            # Parameter compatibility
            param_compatibility = self._calculate_parameter_compatibility(
                requirement.get('parameters', []),
                capability.get('inputSchema', {}).get('properties', {})
            )
            factors['parameter_compatibility'] = param_compatibility
            score += param_compatibility * 0.3
            
            # Calculate confidence
            confidence = min(score, 1.0)
            
            reasoning = f"Tool match score: {score:.3f} (name: {name_similarity:.3f}, desc: {desc_similarity:.3f}, params: {param_compatibility:.3f})"
            
            return MatchScore(
                score=score,
                confidence=confidence,
                reasoning=reasoning,
                factors=factors
            )
            
        except Exception as e:
            self.logger.error(f"Error scoring tool match: {e}")
            return MatchScore(score=0.0, confidence=0.0, reasoning=f"Error: {e}", factors={})
    
    def score_resource_match(self, requirement: Dict[str, Any], capability: Dict[str, Any]) -> MatchScore:
        """Score a resource match"""
        try:
            score = 0.0
            factors = {}
            
            # URI pattern matching
            uri_match = self._calculate_uri_match(
                requirement.get('uri', ''),
                capability.get('uri', '')
            )
            factors['uri_match'] = uri_match
            score += uri_match * 0.5
            
            # Name similarity
            name_similarity = self._calculate_name_similarity(
                requirement.get('name', ''),
                capability.get('name', '')
            )
            factors['name_similarity'] = name_similarity
            score += name_similarity * 0.3
            
            # Description similarity
            desc_similarity = self._calculate_description_similarity(
                requirement.get('description', ''),
                capability.get('description', '')
            )
            factors['description_similarity'] = desc_similarity
            score += desc_similarity * 0.2
            
            confidence = min(score, 1.0)
            reasoning = f"Resource match score: {score:.3f} (uri: {uri_match:.3f}, name: {name_similarity:.3f}, desc: {desc_similarity:.3f})"
            
            return MatchScore(
                score=score,
                confidence=confidence,
                reasoning=reasoning,
                factors=factors
            )
            
        except Exception as e:
            self.logger.error(f"Error scoring resource match: {e}")
            return MatchScore(score=0.0, confidence=0.0, reasoning=f"Error: {e}", factors={})
    
    def score_prompt_match(self, requirement: Dict[str, Any], capability: Dict[str, Any]) -> MatchScore:
        """Score a prompt match"""
        try:
            score = 0.0
            factors = {}
            
            # Name similarity
            name_similarity = self._calculate_name_similarity(
                requirement.get('name', ''),
                capability.get('name', '')
            )
            factors['name_similarity'] = name_similarity
            score += name_similarity * 0.4
            
            # Description similarity
            desc_similarity = self._calculate_description_similarity(
                requirement.get('description', ''),
                capability.get('description', '')
            )
            factors['description_similarity'] = desc_similarity
            score += desc_similarity * 0.4
            
            # Argument compatibility
            arg_compatibility = self._calculate_argument_compatibility(
                requirement.get('arguments', []),
                capability.get('arguments', [])
            )
            factors['argument_compatibility'] = arg_compatibility
            score += arg_compatibility * 0.2
            
            confidence = min(score, 1.0)
            reasoning = f"Prompt match score: {score:.3f} (name: {name_similarity:.3f}, desc: {desc_similarity:.3f}, args: {arg_compatibility:.3f})"
            
            return MatchScore(
                score=score,
                confidence=confidence,
                reasoning=reasoning,
                factors=factors
            )
            
        except Exception as e:
            self.logger.error(f"Error scoring prompt match: {e}")
            return MatchScore(score=0.0, confidence=0.0, reasoning=f"Error: {e}", factors={})
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate name similarity"""
        if not name1 or not name2:
            return 0.0
        
        name1_lower = name1.lower()
        name2_lower = name2.lower()
        
        if name1_lower == name2_lower:
            return 1.0
        
        # Simple word overlap
        words1 = set(name1_lower.split())
        words2 = set(name2_lower.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _calculate_description_similarity(self, desc1: str, desc2: str) -> float:
        """Calculate description similarity"""
        if not desc1 or not desc2:
            return 0.0
        
        desc1_lower = desc1.lower()
        desc2_lower = desc2.lower()
        
        if desc1_lower == desc2_lower:
            return 1.0
        
        # Simple word overlap
        words1 = set(desc1_lower.split())
        words2 = set(desc2_lower.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _calculate_parameter_compatibility(self, required_params: List[Dict], available_params: Dict) -> float:
        """Calculate parameter compatibility"""
        if not required_params:
            return 1.0
        
        if not available_params:
            return 0.0
        
        compatible_count = 0
        for param in required_params:
            param_name = param.get('name', '')
            if param_name in available_params:
                compatible_count += 1
        
        return compatible_count / len(required_params)
    
    def _calculate_uri_match(self, uri1: str, uri2: str) -> float:
        """Calculate URI pattern match"""
        if not uri1 or not uri2:
            return 0.0
        
        if uri1 == uri2:
            return 1.0
        
        # Simple pattern matching
        if uri1 in uri2 or uri2 in uri1:
            return 0.8
        
        return 0.0
    
    def _calculate_argument_compatibility(self, required_args: List[Dict], available_args: List[Dict]) -> float:
        """Calculate argument compatibility"""
        if not required_args:
            return 1.0
        
        if not available_args:
            return 0.0
        
        compatible_count = 0
        for arg in required_args:
            arg_name = arg.get('name', '')
            for available_arg in available_args:
                if available_arg.get('name') == arg_name:
                    compatible_count += 1
                    break
        
        return compatible_count / len(required_args)
