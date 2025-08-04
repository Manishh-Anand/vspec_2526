from abc import ABC, abstractmethod
from typing import Dict, Any, List
import requests
import json
from config import Config
from mcp_client import MCPSequentialThinkingClient

class Tool(ABC):
    """Base class for all tools in the system"""
    
    def __init__(self, name: str, purpose: str):
        self.name = name
        self.purpose = purpose
        self.mcp_client = MCPSequentialThinkingClient()
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool's functionality"""
        pass

class NorthIndiaDestinationResearchTool(Tool):
    def __init__(self):
        super().__init__(
            name="NorthIndiaDestinationResearchTool",
            purpose="Provides detailed information on North India destinations including travel times, costs, and dining options."
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Research suitable destinations within North India using sequential thinking"""
        try:
            budget = context.get("budget", 0)
            days = context.get("days", 0)
            preferences = context.get("preferences", {})
            
            prompt = f"""
            Research suitable destinations in North India with these requirements:
            - Budget: ₹{budget} for {days} days
            - Preferences: {preferences}
            - Starting from: Bhopal
            - Must be accessible by train
            - Must have good vegetarian options
            
            Consider:
            1. Travel time and cost from Bhopal
            2. Daily expenses in each city
            3. Major attractions and activities
            4. Vegetarian food availability
            5. Train connectivity
            """
            
            # Use sequential thinking to analyze destinations
            analysis = await self.mcp_client.analyze_with_sequential_thinking(
                prompt=prompt,
                context="destination research"
            )
            
            if analysis["status"] == "success":
                # Extract destinations from the components
                destinations = []
                for component in analysis["components"]:
                    if isinstance(component, dict) and "city" in component:
                        destinations.append(component)
                
                return {
                    "status": "success",
                    "destinations": destinations,
                    "message": f"Found {len(destinations)} suitable destinations within budget"
                }
            else:
                return {
                    "status": "error",
                    "message": analysis.get("message", "Error in destination research"),
                    "destinations": []
                }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error researching destinations: {str(e)}",
                "destinations": []
            }

class BudgetAllocationTool(Tool):
    def __init__(self):
        super().__init__(
            name="BudgetAllocationTool",
            purpose="Calculates daily budgets for hotels, transport, meals, etc., ensuring vegetarian availability."
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Allocate budget using sequential thinking"""
        try:
            total_budget = context.get("budget", 0)
            days = context.get("days", 0)
            destinations = context.get("destinations", [])
            
            if not destinations or days == 0:
                return {
                    "status": "error",
                    "message": "No destinations selected or invalid number of days",
                    "budget_breakdown": {}
                }
            
            prompt = f"""
            Allocate a budget of ₹{total_budget} for {days} days across these destinations:
            {json.dumps(destinations, indent=2)}
            
            Consider:
            1. Daily accommodation costs in each city
            2. Train travel between cities
            3. Meals (vegetarian)
            4. Activities and attractions
            5. Miscellaneous expenses
            
            Break down the budget into:
            - Daily amounts for each category
            - Total amounts for the entire trip
            - Transport costs between cities
            """
            
            # Use sequential thinking to analyze budget allocation
            analysis = await self.mcp_client.analyze_with_sequential_thinking(
                prompt=prompt,
                context="budget allocation"
            )
            
            if analysis["status"] == "success":
                # Extract budget breakdown from the components
                budget_breakdown = {}
                for component in analysis["components"]:
                    if isinstance(component, dict):
                        if "daily" in component:
                            budget_breakdown["daily"] = component["daily"]
                        if "total" in component:
                            budget_breakdown["total"] = component["total"]
                        if "transport_costs" in component:
                            budget_breakdown["transport_costs"] = component["transport_costs"]
                
                return {
                    "status": "success",
                    "budget_breakdown": budget_breakdown,
                    "message": "Budget allocation completed successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": analysis.get("message", "Error in budget allocation"),
                    "budget_breakdown": {}
                }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error allocating budget: {str(e)}",
                "budget_breakdown": {}
            }

class HotelBookingTool(Tool):
    def __init__(self):
        super().__init__(
            name="HotelBookingTool",
            purpose="Bookings hotels with hygiene ratings and vegetarian dining options within the allocated budget."
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Select hotels using sequential thinking"""
        try:
            destinations = context.get("destinations", [])
            budget_info = context.get("budget", {})
            daily_budget = budget_info.get("daily", {})
            hotel_budget = daily_budget.get("accommodation", 0)
            preferences = context.get("preferences", {})
            
            prompt = f"""
            Suggest hotels for these destinations with these requirements:
            Destinations: {json.dumps(destinations, indent=2)}
            Daily hotel budget: ₹{hotel_budget}
            Preferences: {preferences}
            
            Consider:
            1. Hotel ratings (4-star or higher)
            2. Vegetarian food availability
            3. Hygiene standards
            4. Location and accessibility
            5. Value for money
            
            For each destination, suggest the best hotel that meets all requirements.
            """
            
            # Use sequential thinking to analyze hotel options
            analysis = await self.mcp_client.analyze_with_sequential_thinking(
                prompt=prompt,
                context="hotel selection"
            )
            
            if analysis["status"] == "success":
                # Extract hotel selections from the components
                selected_hotels = []
                for component in analysis["components"]:
                    if isinstance(component, dict) and "name" in component:
                        selected_hotels.append(component)
                
                return {
                    "status": "success",
                    "selected_hotels": selected_hotels,
                    "message": f"Selected hotels for {len(selected_hotels)} cities"
                }
            else:
                return {
                    "status": "error",
                    "message": analysis.get("message", "Error in hotel selection"),
                    "selected_hotels": []
                }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error selecting hotels: {str(e)}",
                "selected_hotels": []
            }

class TrainSchedulingTool(Tool):
    def __init__(self):
        super().__init__(
            name="TrainSchedulingTool",
            purpose="Provides train schedules between cities in North India for budget-friendly travel."
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement train scheduling logic
        return {
            "status": "success",
            "schedules": [],
            "message": "Train scheduling completed"
        }

class ItineraryDesigner(Tool):
    def __init__(self):
        super().__init__(
            name="ItineraryDesigner",
            purpose="Creates a detailed day-wise itinerary based on researcher findings and budget constraints."
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement itinerary design logic
        return {
            "status": "success",
            "itinerary": {},
            "message": "Itinerary design completed"
        }

class TrainFareSearchTool(Tool):
    def __init__(self):
        super().__init__(
            name="TrainFareSearchTool",
            purpose="Searches for the cheapest train tickets between cities in North India."
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement train fare search logic
        return {
            "status": "success",
            "fares": [],
            "message": "Train fare search completed"
        } 