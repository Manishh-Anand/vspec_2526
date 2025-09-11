#!/usr/bin/env python3
"""
Finance MCP Server - Complete Implementation
Implements all three MCP primitives: tools, resources, and prompts
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
import os

# Use FastMCP directly
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Finance MCP Server")

@mcp.tool()
def analyze_bank_statement(statement_data: str) -> str:
    """
    Analyze bank statement data for financial insights
    
    Args:
        statement_data: JSON string containing bank statement data
        
    Returns:
        Analysis results as JSON string
    """
    try:
        # Parse the statement data
        data = json.loads(statement_data) if isinstance(statement_data, str) else statement_data
        
        # Mock analysis logic
        total_transactions = len(data.get('transactions', []))
        total_income = sum(t.get('amount', 0) for t in data.get('transactions', []) if t.get('amount', 0) > 0)
        total_expenses = abs(sum(t.get('amount', 0) for t in data.get('transactions', []) if t.get('amount', 0) < 0))
        
        analysis = {
            "summary": {
                "total_transactions": total_transactions,
                "total_income": total_income,
                "total_expenses": total_expenses,
                "net_balance": total_income - total_expenses
            },
            "insights": [
                f"Processed {total_transactions} transactions",
                f"Total income: ${total_income:,.2f}",
                f"Total expenses: ${total_expenses:,.2f}",
                f"Net balance: ${total_income - total_expenses:,.2f}"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Bank statement analysis completed: {total_transactions} transactions")
        return json.dumps(analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing bank statement: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def calculate_budget(income: float, expenses: Dict[str, float], savings_goal: float = 0.0) -> str:
    """
    Calculate budget recommendations based on income and expenses
    
    Args:
        income: Monthly income amount
        expenses: Dictionary of expense categories and amounts
        savings_goal: Target monthly savings amount
        
    Returns:
        Budget analysis as JSON string
    """
    try:
        total_expenses = sum(expenses.values())
        remaining = income - total_expenses
        
        budget_analysis = {
            "income": income,
            "expenses": expenses,
            "total_expenses": total_expenses,
            "remaining_income": remaining,
            "savings_goal": savings_goal,
            "recommendations": []
        }
        
        # Generate recommendations
        if remaining < savings_goal:
            budget_analysis["recommendations"].append(
                f"Reduce expenses by ${savings_goal - remaining:,.2f} to meet savings goal"
            )
        elif remaining > savings_goal * 1.5:
            budget_analysis["recommendations"].append(
                f"Consider increasing savings goal to ${remaining * 0.8:,.2f}"
            )
        
        if total_expenses > income * 0.8:
            budget_analysis["recommendations"].append(
                "Consider reducing expenses - they exceed 80% of income"
            )
        
        logger.info(f"Budget calculation completed for income: ${income}")
        return json.dumps(budget_analysis)
        
    except Exception as e:
        logger.error(f"Error calculating budget: {e}")
        return json.dumps({"error": str(e)})

@mcp.resource("finance://market-data/{symbol}")
def get_market_data(symbol: str) -> str:
    """
    Get market data for a financial symbol
    
    Args:
        symbol: Financial symbol (e.g., AAPL, MSFT)
        
    Returns:
        Market data as JSON string
    """
    try:
        # Mock market data
        market_data = {
            "symbol": symbol.upper(),
            "price": 150.25 + hash(symbol) % 100,  # Mock price
            "change": (hash(symbol) % 20) - 10,    # Mock change
            "volume": 1000000 + hash(symbol) % 5000000,
            "timestamp": datetime.now().isoformat(),
            "source": "finance_mcp_server"
        }
        
        logger.info(f"Market data retrieved for symbol: {symbol}")
        return json.dumps(market_data)
        
    except Exception as e:
        logger.error(f"Error getting market data for {symbol}: {e}")
        return json.dumps({"error": str(e)})

@mcp.resource("finance://tax-rules/{year}")
def get_tax_rules(year: str) -> str:
    """
    Get tax rules for a specific year
    
    Args:
        year: Tax year (e.g., 2024, 2023)
        
    Returns:
        Tax rules as JSON string
    """
    try:
        # Mock tax rules
        tax_rules = {
            "year": year,
            "federal_tax_brackets": [
                {"min": 0, "max": 11000, "rate": 0.10},
                {"min": 11001, "max": 44725, "rate": 0.12},
                {"min": 44726, "max": 95375, "rate": 0.22},
                {"min": 95376, "max": 182050, "rate": 0.24},
                {"min": 182051, "max": 231250, "rate": 0.32},
                {"min": 231251, "max": 578125, "rate": 0.35},
                {"min": 578126, "max": float('inf'), "rate": 0.37}
            ],
            "standard_deduction": 13850 if year == "2024" else 12950,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Tax rules retrieved for year: {year}")
        return json.dumps(tax_rules)
        
    except Exception as e:
        logger.error(f"Error getting tax rules for {year}: {e}")
        return json.dumps({"error": str(e)})

@mcp.prompt("financial_advice")
def financial_advice_prompt(context: str) -> str:
    """
    Generate financial advice prompt based on context
    
    Args:
        context: Financial context or situation
        
    Returns:
        Financial advice prompt
    """
    try:
        prompt = f"""
Based on the following financial context: {context}

Please provide comprehensive financial advice including:

1. **Immediate Actions**: What should be done right now?
2. **Short-term Goals** (1-6 months): What financial goals should be prioritized?
3. **Long-term Planning** (1-5 years): What long-term financial strategies should be considered?
4. **Risk Assessment**: What financial risks should be aware of?
5. **Resource Recommendations**: What tools, services, or resources would be helpful?

Consider factors such as:
- Current financial situation
- Income stability
- Debt levels
- Savings and investments
- Financial goals
- Risk tolerance
- Market conditions

Provide specific, actionable advice tailored to this situation.
"""
        
        logger.info(f"Financial advice prompt generated for context: {context[:50]}...")
        return prompt
        
    except Exception as e:
        logger.error(f"Error generating financial advice prompt: {e}")
        return f"Error generating prompt: {str(e)}"

def main():
    """Main server function"""
    logger.info("Starting Finance MCP Server on port 3001")
    
    try:
        # Run the server using FastMCP's built-in runner
        mcp.run(transport="http", port=3001)
    except Exception as e:
        logger.error(f"Error running Finance MCP Server: {e}")
        raise

if __name__ == "__main__":
    main()
