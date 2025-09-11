"""
Semantic Matching Implementation with Performance Optimizations
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import httpx
from src.core.protocol import Tool, Resource, Prompt
from src.core.models import MatchResult
from src.discovery.scanner import MCPDiscoveryScanner, ServerCapabilities


@dataclass
class MatchingConfig:
    """Configuration for semantic matching"""
    llm_endpoint: str = "http://127.0.0.1:1234/v1/chat/completions"
    model: str = "openhermes-2.5-mistral-7b"
    temperature: float = 0.3
    max_tokens: int = 1000
    threshold: float = 0.3
    cache_ttl: int = 300  # 5 minutes
    max_llm_calls: int = 5  # Limit LLM calls for performance


class FastSemanticMatcher:
    """High-performance semantic matcher with caching and batch processing"""
    
    def __init__(self, config: Optional[MatchingConfig] = None):
        self.config = config or MatchingConfig()
        self.logger = logging.getLogger(__name__)
        self.discovery_scanner = MCPDiscoveryScanner()
        
        # Performance optimizations
        self.cache = {}
        self.llm_call_count = 0
        self.start_time = time.time()
        
        # Fallback domain servers for when discovery fails
        self.fallback_domain_servers = {
            "finance": {
                "tools": [
                    Tool(name="file_reader", description="Tool for file reader operations", inputSchema={}),
                    Tool(name="bank_statement_parser", description="Tool for bank statement parser operations", inputSchema={}),
                    Tool(name="subscription_detector", description="Tool for detecting recurring subscriptions", inputSchema={}),
                    Tool(name="budget_planner_tool", description="Tool for budget planning and analysis", inputSchema={}),
                    Tool(name="financial_advice_generator", description="Tool for generating financial advice", inputSchema={}),
                    Tool(name="spending_pattern_visualizer", description="Tool for visualizing spending patterns", inputSchema={}),
                    Tool(name="progress_monitor_tool", description="Tool for monitoring financial progress", inputSchema={})
                ],
                "resources": [
                    Resource(uri="finance://reports/monthly_summary", name="Monthly Financial Summary", description="Monthly financial summary report"),
                    Resource(uri="finance://reports/budget_analysis", name="Budget Analysis Report", description="Budget analysis report"),
                    Resource(uri="finance://data/market_trends", name="Market Trends Data", description="Market trends data")
                ],
                "prompts": [
                    Prompt(name="budget_advice", description="Budget advice prompt", arguments=[]),
                    Prompt(name="investment_advice", description="Investment advice prompt", arguments=[])
                ]
            },
            "productivity": {
                "tools": [
                    Tool(name="email_summarizer", description="Tool for summarizing emails", inputSchema={}),
                    Tool(name="meeting_assistant", description="Tool for meeting assistance", inputSchema={}),
                    Tool(name="task_converter", description="Tool for converting tasks", inputSchema={}),
                    Tool(name="calendar_optimizer", description="Tool for calendar optimization", inputSchema={}),
                    Tool(name="smart_reply_generator", description="Tool for generating smart replies", inputSchema={}),
                    Tool(name="focus_time_scheduler", description="Tool for scheduling focus time", inputSchema={}),
                    Tool(name="collaboration_enhancer", description="Tool for enhancing collaboration", inputSchema={}),
                    Tool(name="workflow_automator", description="Tool for workflow automation", inputSchema={}),
                    Tool(name="productivity_analyzer", description="Tool for productivity analysis", inputSchema={}),
                    Tool(name="goal_tracker", description="Tool for tracking goals", inputSchema={})
                ],
                "resources": [
                    Resource(uri="productivity://templates/email_templates", name="Email Templates", description="Email templates"),
                    Resource(uri="productivity://guides/time_management", name="Time Management Guide", description="Time management guide"),
                    Resource(uri="productivity://tools/productivity_tools", name="Productivity Tools Reference", description="Productivity tools reference")
                ],
                "prompts": [
                    Prompt(name="email_composition", description="Email composition prompt", arguments=[]),
                    Prompt(name="meeting_summary", description="Meeting summary prompt", arguments=[])
                ]
            }
        }
    
    async def match_requirements(self, ba_data: Dict[str, Any]) -> Dict[str, List[MatchResult]]:
        """Match BA requirements with available MCP capabilities using performance optimizations"""
        try:
            self.logger.info("Starting optimized semantic matching process")
            self.start_time = time.time()
            
            # Convert dataclass to dict if needed
            if hasattr(ba_data, 'workflow_metadata'):
                ba_dict = self._convert_dataclass_to_dict(ba_data)
            else:
                ba_dict = ba_data
            
            # Extract domain from workflow metadata
            domain = ba_dict.get("workflow_metadata", {}).get("domain", "").lower()
            
            # Try to discover servers first
            discovered_servers = await self.discovery_scanner.discover_all_servers()
            
            if discovered_servers:
                self.logger.info(f"Discovered {len(discovered_servers)} servers with capabilities")
                # Use discovered servers for matching
                return await self._fast_batch_match(ba_dict, discovered_servers)
            else:
                self.logger.info("No servers discovered, using fallback domain servers")
                # Use fallback domain servers
                return await self._match_with_fallback_servers(ba_dict, domain)
            
        except Exception as e:
            self.logger.error(f"Error in semantic matching: {e}")
            raise
    
    def _convert_dataclass_to_dict(self, ba_data) -> Dict[str, Any]:
        """Convert dataclass to dictionary efficiently"""
        return {
            "workflow_metadata": {
                "domain": ba_data.workflow_metadata.domain
            },
            "agents": [
                {
                    "tools": [
                        {
                            "name": tool.name,
                            "purpose": tool.purpose
                        } for tool in agent.tools
                    ],
                    "resources": [
                        {
                            "name": resource.name,
                            "description": resource.description,
                            "uri": resource.uri
                        } for resource in agent.resources
                    ],
                    "prompts": [
                        {
                            "name": prompt.name,
                            "description": prompt.description,
                            "template": prompt.template
                        } for prompt in agent.prompts
                    ]
                } for agent in ba_data.agents
            ]
        }
    
    async def _fast_batch_match(self, ba_dict: Dict[str, Any], discovered_servers: Dict[str, ServerCapabilities]) -> Dict[str, List[MatchResult]]:
        """Fast batch matching with caching and keyword pre-filtering"""
        # Check cache first
        cache_key = self._generate_cache_key(ba_dict, discovered_servers)
        if cache_key in self.cache:
            cached, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.config.cache_ttl:
                self.logger.info("Using cached matching results")
                return cached
        
        # Extract all requirements
        all_tools = []
        all_resources = []
        all_prompts = []
        
        for agent in ba_dict.get("agents", []):
            all_tools.extend(agent.get("tools", []))
            all_resources.extend(agent.get("resources", []))
            all_prompts.extend(agent.get("prompts", []))
        
        # Fast keyword matching first, LLM only for unclear cases
        matches = {
            "tools": [],
            "resources": [],
            "prompts": []
        }
        
        # Process tools with batch optimization
        if all_tools:
            tool_matches = await self._batch_match_tools(all_tools, discovered_servers)
            matches["tools"] = tool_matches
        
        # Process resources with batch optimization
        if all_resources:
            resource_matches = await self._batch_match_resources(all_resources, discovered_servers)
            matches["resources"] = resource_matches
        
        # Process prompts with batch optimization
        if all_prompts:
            prompt_matches = await self._batch_match_prompts(all_prompts, discovered_servers)
            matches["prompts"] = prompt_matches
        
        # Cache results
        self.cache[cache_key] = (matches, time.time())
        
        execution_time = time.time() - self.start_time
        self.logger.info(f"Fast batch matching completed in {execution_time:.2f}s with {self.llm_call_count} LLM calls")
        
        return matches
    
    async def _batch_match_tools(self, tools: List[Dict], servers: Dict[str, ServerCapabilities]) -> List[MatchResult]:
        """Batch match tools with keyword pre-filtering"""
        matches = []
        
        for tool_req in tools:
            # Fast keyword matching first
            best_match = await self._fast_tool_match(tool_req, servers)
            if best_match:
                matches.append(best_match)
        
        return matches
    
    async def _fast_tool_match(self, tool_req: Dict[str, Any], servers: Dict[str, ServerCapabilities]) -> Optional[MatchResult]:
        """Fast tool matching with keyword pre-filtering and limited LLM calls"""
        best_match = None
        best_score = 0.0
        
        for server_id, capabilities in servers.items():
            for tool in capabilities.tools:
                # Handle both string and object formats
                if isinstance(tool, str):
                    tool_name = tool
                    tool_description = f"Tool: {tool}"
                    tool_input_schema = {}
                elif isinstance(tool, dict):
                    tool_name = tool.get('name', '')
                    tool_description = tool.get('description', '')
                    tool_input_schema = tool.get('inputSchema', {})
                else:
                    continue
                
                # Fast keyword matching first (no LLM call)
                keyword_score = self._keyword_match_tool(tool_req, tool_name, tool_description)
                
                if keyword_score >= self.config.threshold:
                    if keyword_score > best_score:
                        best_score = keyword_score
                        best_match = MatchResult(
                            tool=Tool(
                                name=tool_name,
                                description=tool_description,
                                inputSchema=tool_input_schema
                            ),
                            score=keyword_score,
                            confidence=keyword_score,
                            reasoning=f"Keyword match with {server_id}",
                            server=server_id
                        )
                
                # Only use LLM if keyword matching fails and we haven't exceeded the limit
                elif self.llm_call_count < self.config.max_llm_calls:
                    try:
                        llm_match = await self._llm_tool_match(tool_req, tool_name, tool_description, server_id)
                        if llm_match and llm_match.score > best_score:
                            best_match = llm_match
                            best_score = llm_match.score
                    except Exception as e:
                        self.logger.debug(f"LLM matching failed for {tool_name}: {e}")
        
        return best_match
    
    def _keyword_match_tool(self, tool_req: Dict[str, Any], tool_name: str, tool_description: str) -> float:
        """Fast keyword-based tool matching without LLM calls"""
        req_name = tool_req.get("name", "").lower()
        req_purpose = tool_req.get("purpose", "").lower()
        
        tool_name_lower = tool_name.lower()
        tool_desc_lower = tool_description.lower()
        
        # Exact name match
        if req_name == tool_name_lower:
            return 1.0
        
        # Partial name match
        if req_name in tool_name_lower or tool_name_lower in req_name:
            return 0.9
        
        # Word overlap scoring
        req_words = set(req_name.split('_') + req_purpose.split())
        tool_words = set(tool_name_lower.split('_') + tool_desc_lower.split())
        
        if req_words and tool_words:
            overlap = len(req_words.intersection(tool_words))
            total = len(req_words.union(tool_words))
            if total > 0:
                return min(overlap / total * 0.8, 0.8)
        
        # Substring matching
        if req_name in tool_desc_lower or req_purpose in tool_desc_lower:
            return 0.7
        
        return 0.0
    
    async def _llm_tool_match(self, tool_req: Dict[str, Any], tool_name: str, tool_description: str, server_id: str) -> Optional[MatchResult]:
        """LLM-based tool matching (limited use for performance)"""
        if self.llm_call_count >= self.config.max_llm_calls:
            return None
        
        try:
            self.llm_call_count += 1
            
            # Create a Tool object for LLM matching
            available_tool = Tool(
                name=tool_name,
                description=tool_description,
                inputSchema={}
            )
            
            # Use LLM for intelligent matching
            llm_match = await self._find_best_tool_match(
                tool_req.get("name", ""),
                tool_req.get("purpose", ""),
                [available_tool],
                "finance"  # Extract from context
            )
            
            if llm_match and llm_match["score"] >= self.config.threshold:
                return MatchResult(
                    tool=available_tool,
                    score=llm_match["score"],
                    confidence=llm_match["confidence"],
                    reasoning=llm_match["reasoning"],
                    server=server_id
                )
        
        except Exception as e:
            self.logger.debug(f"LLM matching failed for {tool_name}: {e}")
        
        return None
    
    async def _batch_match_resources(self, resources: List[Dict], servers: Dict[str, ServerCapabilities]) -> List[MatchResult]:
        """Batch match resources with keyword pre-filtering"""
        matches = []
        
        for resource_req in resources:
            best_match = await self._fast_resource_match(resource_req, servers)
            if best_match:
                matches.append(best_match)
        
        return matches
    
    async def _fast_resource_match(self, resource_req: Dict[str, Any], servers: Dict[str, ServerCapabilities]) -> Optional[MatchResult]:
        """Fast resource matching with keyword pre-filtering"""
        best_match = None
        best_score = 0.0
        
        for server_id, capabilities in servers.items():
            for resource in capabilities.resources:
                if isinstance(resource, str):
                    resource_uri = resource
                    resource_description = f"Resource: {resource}"
                elif isinstance(resource, dict):
                    resource_uri = resource.get('uri', '')
                    resource_description = resource.get('description', '')
                else:
                    continue
                
                # Fast keyword matching
                score = self._keyword_match_resource(resource_req, resource_uri, resource_description)
                
                if score >= self.config.threshold and score > best_score:
                    best_score = score
                    best_match = MatchResult(
                        tool=Tool(
                            name=resource_uri,
                            description=resource_description,
                            inputSchema={}
                        ),
                        score=score,
                        confidence=score,
                        reasoning=f"Keyword match with {server_id}",
                        server=server_id
                    )
        
        return best_match
    
    def _keyword_match_resource(self, resource_req: Dict[str, Any], resource_uri: str, resource_description: str) -> float:
        """Fast keyword-based resource matching"""
        req_uri = resource_req.get("uri", "").lower()
        req_name = resource_req.get("name", "").lower()
        req_desc = resource_req.get("description", "").lower()
        
        resource_uri_lower = resource_uri.lower()
        resource_desc_lower = resource_description.lower()
        
        # Exact URI match
        if req_uri == resource_uri_lower:
            return 1.0
        
        # URI pattern matching
        if req_uri and resource_uri_lower:
            req_parts = req_uri.split('/')
            resource_parts = resource_uri_lower.split('/')
            
            if len(req_parts) >= 2 and len(resource_parts) >= 2:
                if req_parts[0] == resource_parts[0] and req_parts[1] == resource_parts[1]:
                    return 0.8
        
        # Word overlap
        req_words = set(req_uri.split('/') + req_name.split() + req_desc.split())
        resource_words = set(resource_uri_lower.split('/') + resource_desc_lower.split())
        
        if req_words and resource_words:
            overlap = len(req_words.intersection(resource_words))
            total = len(req_words.union(resource_words))
            if total > 0:
                return min(overlap / total * 0.7, 0.7)
        
        return 0.0
    
    async def _batch_match_prompts(self, prompts: List[Dict], servers: Dict[str, ServerCapabilities]) -> List[MatchResult]:
        """Batch match prompts with keyword pre-filtering"""
        matches = []
        
        for prompt_req in prompts:
            best_match = await self._fast_prompt_match(prompt_req, servers)
            if best_match:
                matches.append(best_match)
        
        return matches
    
    async def _fast_prompt_match(self, prompt_req: Dict[str, Any], servers: Dict[str, ServerCapabilities]) -> Optional[MatchResult]:
        """Fast prompt matching with keyword pre-filtering"""
        best_match = None
        best_score = 0.0
        
        for server_id, capabilities in servers.items():
            for prompt in capabilities.prompts:
                if isinstance(prompt, str):
                    prompt_name = prompt
                    prompt_description = f"Prompt: {prompt}"
                elif isinstance(prompt, dict):
                    prompt_name = prompt.get('name', '')
                    prompt_description = prompt.get('description', '')
                else:
                    continue
                
                # Fast keyword matching
                score = self._keyword_match_prompt(prompt_req, prompt_name, prompt_description)
                
                if score >= self.config.threshold and score > best_score:
                    best_score = score
                    best_match = MatchResult(
                        tool=Tool(
                            name=prompt_name,
                            description=prompt_description,
                            inputSchema={}
                        ),
                        score=score,
                        confidence=score,
                        reasoning=f"Keyword match with {server_id}",
                        server=server_id
                    )
        
        return best_match
    
    def _keyword_match_prompt(self, prompt_req: Dict[str, Any], prompt_name: str, prompt_description: str) -> float:
        """Fast keyword-based prompt matching"""
        req_name = prompt_req.get("name", "").lower()
        req_desc = prompt_req.get("description", "").lower()
        
        prompt_name_lower = prompt_name.lower()
        prompt_desc_lower = prompt_description.lower()
        
        # Exact name match
        if req_name == prompt_name_lower:
            return 1.0
        
        # Partial name match
        if req_name in prompt_name_lower or prompt_name_lower in req_name:
            return 0.9
        
        # Word overlap
        req_words = set(req_name.split('_') + req_desc.split())
        prompt_words = set(prompt_name_lower.split('_') + prompt_desc_lower.split())
        
        if req_words and prompt_words:
            overlap = len(req_words.intersection(prompt_words))
            total = len(req_words.union(prompt_words))
            if total > 0:
                return min(overlap / total * 0.7, 0.7)
        
        return 0.0
    
    def _generate_cache_key(self, ba_dict: Dict[str, Any], servers: Dict[str, ServerCapabilities]) -> str:
        """Generate cache key for matching results"""
        # Create a hash of the requirements and server capabilities
        content = str(ba_dict) + str(list(servers.keys()))
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _match_with_fallback_servers(self, ba_dict: Dict[str, Any], domain: str) -> Dict[str, List[MatchResult]]:
        """Match requirements using fallback domain servers"""
        if domain not in self.fallback_domain_servers:
            self.logger.warning(f"Unknown domain: {domain}")
            return {"tools": [], "resources": [], "prompts": []}
        
        matches = {
            "tools": [],
            "resources": [],
            "prompts": []
        }
        
        # Extract all requirements
        all_tools = []
        all_resources = []
        all_prompts = []
        
        for agent in ba_dict.get("agents", []):
            all_tools.extend(agent.get("tools", []))
            all_resources.extend(agent.get("resources", []))
            all_prompts.extend(agent.get("prompts", []))
        
        # Map domain to actual server names from config
        domain_to_server = {
            "finance": "finance-core-mcp",
            "productivity": "productivity-gmail-mcp"
        }
        
        server_name = domain_to_server.get(domain, f"{domain}-mcp")
        
        # Match tools
        for tool_req in all_tools:
            match = await self._find_best_tool_match_fallback(tool_req, domain, server_name)
            if match:
                matches["tools"].append(match)
        
        # Match resources
        for resource_req in all_resources:
            match = await self._find_best_resource_match_fallback(resource_req, domain, server_name)
            if match:
                matches["resources"].append(match)
        
        # Match prompts
        for prompt_req in all_prompts:
            match = await self._find_best_prompt_match_fallback(prompt_req, domain, server_name)
            if match:
                matches["prompts"].append(match)
        
        return matches
    
    async def _find_best_tool_match_fallback(self, tool_req: Dict[str, Any], domain: str, server_name: str) -> Optional[MatchResult]:
        """Find best tool match using fallback servers"""
        if domain not in self.fallback_domain_servers:
            return None
        
        domain_servers = self.fallback_domain_servers[domain]
        
        for tool in domain_servers["tools"]:
            # Simple name-based matching for now
            if tool.name == tool_req.get("name"):
                return MatchResult(
                    tool=tool,
                    score=1.0,
                    confidence=1.0,
                    reasoning="Exact name match in fallback server",
                    server=server_name
                )
        
        return None
    
    async def _find_best_resource_match_fallback(self, resource_req: Dict[str, Any], domain: str, server_name: str) -> Optional[MatchResult]:
        """Find best resource match using fallback servers"""
        if domain not in self.fallback_domain_servers:
            return None
        
        domain_servers = self.fallback_domain_servers[domain]
        
        for resource in domain_servers["resources"]:
            # Simple URI-based matching for now
            if resource.uri == resource_req.get("uri"):
                return MatchResult(
                    tool=resource,  # Using tool field for resource
                    score=1.0,
                    confidence=1.0,
                    reasoning="Exact URI match in fallback server",
                    server=server_name
                )
        
        return None
    
    async def _find_best_prompt_match_fallback(self, prompt_req: Dict[str, Any], domain: str, server_name: str) -> Optional[MatchResult]:
        """Find best prompt match using fallback servers"""
        if domain not in self.fallback_domain_servers:
            return None
        
        domain_servers = self.fallback_domain_servers[domain]
        
        for prompt in domain_servers["prompts"]:
            # Simple name-based matching for now
            if prompt.name == prompt_req.get("name"):
                return MatchResult(
                    tool=prompt,  # Using tool field for prompt
                    score=1.0,
                    confidence=1.0,
                    reasoning="Exact name match in fallback server",
                    server=server_name
                )
        
        return None
    
    async def _find_best_tool_match(self, tool_name: str, tool_purpose: str, available_tools: List[Tool], domain: str) -> Optional[Dict[str, Any]]:
        """Find the best tool match using LLM semantic analysis"""
        try:
            # Create prompt for LLM
            prompt = self._create_tool_matching_prompt(tool_name, tool_purpose, available_tools, domain)
            
            # Get LLM response
            response = await self._call_llm(prompt)
            
            # Parse response
            match_data = self._parse_tool_match_response(response, available_tools)
            
            if match_data and match_data["score"] >= self.config.threshold:
                return match_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding tool match: {e}")
            return None
    
    def _create_tool_matching_prompt(self, tool_name: str, tool_purpose: str, available_tools: List[Tool], domain: str) -> str:
        """Create prompt for tool matching"""
        tools_list = "\n".join([f"- {tool.name}: {tool.description}" for tool in available_tools])
        
        prompt = f"""
You are a semantic matching system for {domain} domain tools. Your task is to find the best match for a required tool.

Required Tool:
- Name: {tool_name}
- Purpose: {tool_purpose}

Available Tools:
{tools_list}

Please analyze the semantic similarity and return a JSON response with:
1. "tool_name": The name of the best matching tool
2. "score": A similarity score between 0.0 and 1.0
3. "confidence": Your confidence in this match (0.0 to 1.0)
4. "reasoning": Brief explanation of why this tool matches

Consider:
- Functional similarity
- Purpose alignment
- Domain relevance
- Name similarity

Return only the JSON response, no additional text.
"""
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the local LLM with timeout control"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:  # Reduced timeout for performance
                payload = {
                    "model": self.config.model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that performs semantic matching."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens
                }
                
                response = await client.post(self.config.llm_endpoint, json=payload)
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
        except Exception as e:
            self.logger.error(f"Error calling LLM: {e}")
            self.logger.error(f"LLM endpoint: {self.config.llm_endpoint}")
            self.logger.error(f"LLM model: {self.config.model}")
            self.logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            # Fallback to simple name matching
            return self._fallback_matching(prompt)
    
    def _fallback_matching(self, prompt: str) -> str:
        """Fallback matching when LLM is unavailable"""
        # Simple fallback logic
        return '{"tool_name": "file_reader", "score": 0.8, "confidence": 0.7, "reasoning": "Fallback matching"}'
    
    def _parse_tool_match_response(self, response: str, available_tools: List[Tool]) -> Optional[Dict[str, Any]]:
        """Parse LLM response for tool matching"""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                return None
            
            json_str = response[json_start:json_end]
            match_data = json.loads(json_str)
            
            # Find the tool object
            tool_name = match_data.get("tool_name", "")
            tool = next((t for t in available_tools if t.name == tool_name), None)
            
            if tool:
                return {
                    "tool": tool,
                    "score": float(match_data.get("score", 0.0)),
                    "confidence": float(match_data.get("confidence", 0.0)),
                    "reasoning": match_data.get("reasoning", "")
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing tool match response: {e}")
            return None
    
    async def get_available_capabilities(self, domain: str) -> Dict[str, Any]:
        """Get available capabilities for a domain"""
        if domain not in self.fallback_domain_servers:
            return {}
        
        return {
            "tools": self.fallback_domain_servers[domain]["tools"],
            "resources": self.fallback_domain_servers[domain]["resources"],
            "prompts": self.fallback_domain_servers[domain]["prompts"]
        }


# Backward compatibility
SemanticMatcher = FastSemanticMatcher
