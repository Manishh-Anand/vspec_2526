from typing import Dict, Any, List
from tools import (
    NorthIndiaDestinationResearchTool,
    BudgetAllocationTool,
    HotelBookingTool,
    TrainSchedulingTool,
    ItineraryDesigner,
    TrainFareSearchTool
)

class TripPlannerOrchestrator:
    """Orchestrates the trip planning process using multiple tools"""
    
    def __init__(self):
        # Initialize tools
        self.destination_tool = NorthIndiaDestinationResearchTool()
        self.budget_tool = BudgetAllocationTool()
        self.hotel_tool = HotelBookingTool()
        self.train_schedule_tool = TrainSchedulingTool()
        self.itinerary_tool = ItineraryDesigner()
        self.train_fare_tool = TrainFareSearchTool()
    
    async def plan_trip(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete trip planning process"""
        try:
            # Step 1: Research destinations
            destinations = await self.destination_tool.execute(context)
            
            # Step 2: Plan budget
            budget = await self.budget_tool.execute({
                **context,
                "destinations": destinations.get("destinations", [])
            })
            
            # Step 3: Select hotels
            hotels = await self.hotel_tool.execute({
                **context,
                "destinations": destinations.get("destinations", []),
                "budget": budget.get("budget_breakdown", {})
            })
            
            # Step 4: Plan transport
            transport = await self.train_schedule_tool.execute({
                **context,
                "destinations": destinations.get("destinations", []),
                "budget": budget.get("budget_breakdown", {})
            })
            
            # Step 5: Create itinerary
            itinerary = await self.itinerary_tool.execute({
                **context,
                "destinations": destinations.get("destinations", []),
                "budget": budget.get("budget_breakdown", {}),
                "hotels": hotels.get("selected_hotels", []),
                "transport": transport.get("schedules", [])
            })
            
            return {
                "status": "success",
                "plan": {
                    "destinations": destinations,
                    "budget": budget,
                    "hotels": hotels,
                    "transport": transport,
                    "itinerary": itinerary
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Trip planning failed: {str(e)}"
            } 