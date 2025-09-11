"""
Conflict Resolver
Resolves conflicts in MCP capability matching
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class Conflict:
    """Conflict information"""
    type: str
    description: str
    severity: str  # low, medium, high
    affected_items: List[str]
    resolution: Optional[str] = None


class ConflictResolver:
    """MCP Conflict Resolver"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def resolve_conflicts(self, matches: List[Any]) -> List[Any]:
        """Resolve conflicts in matches"""
        try:
            self.logger.info("Starting conflict resolution")
            
            # Detect conflicts
            conflicts = self._detect_conflicts(matches)
            
            if not conflicts:
                self.logger.info("No conflicts detected")
                return matches
            
            # Resolve conflicts
            resolved_matches = self._apply_resolutions(matches, conflicts)
            
            self.logger.info(f"Resolved {len(conflicts)} conflicts")
            return resolved_matches
            
        except Exception as e:
            self.logger.error(f"Error in conflict resolution: {e}")
            return matches
    
    def _detect_conflicts(self, matches: List[Any]) -> List[Conflict]:
        """Detect conflicts in matches"""
        conflicts = []
        
        # Check for duplicate matches
        duplicate_conflicts = self._detect_duplicate_conflicts(matches)
        conflicts.extend(duplicate_conflicts)
        
        # Check for priority conflicts
        priority_conflicts = self._detect_priority_conflicts(matches)
        conflicts.extend(priority_conflicts)
        
        # Check for domain conflicts
        domain_conflicts = self._detect_domain_conflicts(matches)
        conflicts.extend(domain_conflicts)
        
        return conflicts
    
    def _detect_duplicate_conflicts(self, matches: List[Any]) -> List[Conflict]:
        """Detect duplicate matches"""
        conflicts = []
        seen_matches = {}
        
        for match in matches:
            key = f"{match.requirement.name}_{match.matched_capability}"
            
            if key in seen_matches:
                conflict = Conflict(
                    type="duplicate_match",
                    description=f"Duplicate match for {match.requirement.name}",
                    severity="medium",
                    affected_items=[match.requirement.name, match.matched_capability],
                    resolution="keep_highest_confidence"
                )
                conflicts.append(conflict)
            else:
                seen_matches[key] = match
        
        return conflicts
    
    def _detect_priority_conflicts(self, matches: List[Any]) -> List[Conflict]:
        """Detect priority conflicts"""
        conflicts = []
        
        # Group by requirement
        requirement_groups = {}
        for match in matches:
            req_name = match.requirement.name
            if req_name not in requirement_groups:
                requirement_groups[req_name] = []
            requirement_groups[req_name].append(match)
        
        # Check for priority conflicts
        for req_name, req_matches in requirement_groups.items():
            if len(req_matches) > 1:
                priorities = [getattr(match.requirement, 'priority', 1) for match in req_matches]
                if len(set(priorities)) > 1:
                    conflict = Conflict(
                        type="priority_conflict",
                        description=f"Priority conflict for {req_name}",
                        severity="high",
                        affected_items=[req_name],
                        resolution="keep_highest_priority"
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def _detect_domain_conflicts(self, matches: List[Any]) -> List[Conflict]:
        """Detect domain conflicts"""
        conflicts = []
        
        # Group by requirement
        requirement_groups = {}
        for match in matches:
            req_name = match.requirement.name
            if req_name not in requirement_groups:
                requirement_groups[req_name] = []
            requirement_groups[req_name].append(match)
        
        # Check for domain conflicts
        for req_name, req_matches in requirement_groups.items():
            if len(req_matches) > 1:
                domains = [match.server_name for match in req_matches]
                if len(set(domains)) > 1:
                    conflict = Conflict(
                        type="domain_conflict",
                        description=f"Domain conflict for {req_name}",
                        severity="medium",
                        affected_items=[req_name],
                        resolution="keep_best_match"
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def _apply_resolutions(self, matches: List[Any], conflicts: List[Conflict]) -> List[Any]:
        """Apply conflict resolutions"""
        resolved_matches = matches.copy()
        
        for conflict in conflicts:
            if conflict.type == "duplicate_match":
                resolved_matches = self._resolve_duplicate_conflicts(resolved_matches, conflict)
            elif conflict.type == "priority_conflict":
                resolved_matches = self._resolve_priority_conflicts(resolved_matches, conflict)
            elif conflict.type == "domain_conflict":
                resolved_matches = self._resolve_domain_conflicts(resolved_matches, conflict)
        
        return resolved_matches
    
    def _resolve_duplicate_conflicts(self, matches: List[Any], conflict: Conflict) -> List[Any]:
        """Resolve duplicate conflicts by keeping highest confidence"""
        req_name = conflict.affected_items[0]
        
        # Find all matches for this requirement
        req_matches = [m for m in matches if m.requirement.name == req_name]
        
        if len(req_matches) > 1:
            # Keep the match with highest confidence
            best_match = max(req_matches, key=lambda m: getattr(m, 'confidence', 0))
            
            # Remove other matches
            matches = [m for m in matches if not (m.requirement.name == req_name and m != best_match)]
        
        return matches
    
    def _resolve_priority_conflicts(self, matches: List[Any], conflict: Conflict) -> List[Any]:
        """Resolve priority conflicts by keeping highest priority"""
        req_name = conflict.affected_items[0]
        
        # Find all matches for this requirement
        req_matches = [m for m in matches if m.requirement.name == req_name]
        
        if len(req_matches) > 1:
            # Keep the match with highest priority
            best_match = max(req_matches, key=lambda m: getattr(m.requirement, 'priority', 1))
            
            # Remove other matches
            matches = [m for m in matches if not (m.requirement.name == req_name and m != best_match)]
        
        return matches
    
    def _resolve_domain_conflicts(self, matches: List[Any], conflict: Conflict) -> List[Any]:
        """Resolve domain conflicts by keeping best match"""
        req_name = conflict.affected_items[0]
        
        # Find all matches for this requirement
        req_matches = [m for m in matches if m.requirement.name == req_name]
        
        if len(req_matches) > 1:
            # Keep the match with highest confidence
            best_match = max(req_matches, key=lambda m: getattr(m, 'confidence', 0))
            
            # Remove other matches
            matches = [m for m in matches if not (m.requirement.name == req_name and m != best_match)]
        
        return matches
