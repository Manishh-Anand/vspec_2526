import asyncio
import json
from orchestrator import TripPlannerOrchestrator

async def main():
    # Initialize the trip planner
    planner = TripPlannerOrchestrator()
    
    # Create the context with user requirements
    context = {
        "budget": 100000,  # 1 lakh rupees
        "days": 5,
        "preferences": {
            "vegetarian": True,
            "hygiene_rating": "4-star or higher",
            "transport": "train",
            "starting_city": "Bhopal"
        }
    }
    
    # Plan the trip
    result = await planner.plan_trip(context)
    
    # Print the result
    print("\nTrip Planning Results:")
    print("=" * 50)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main()) 