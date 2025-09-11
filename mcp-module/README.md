# MCP Module - Model Context Protocol Implementation

A production-ready implementation of the Model Context Protocol (MCP) module that processes Base Agent Output (BA_op.json) files and generates comprehensive MCP configurations for multi-domain workflows.

## Overview

The MCP Module is designed to:
- Parse complex BA_op.json input files containing multi-agent workflows
- Perform semantic matching using local LLM (openhermes-2.5-mistral-7b)
- Execute MCP operations across domain-specific servers
- Generate comprehensive MCP configuration outputs

## Architecture

```
mcp-module/
├── src/
│   ├── main.py                 # Main MCP module orchestrator
│   ├── core/
│   │   └── protocol.py         # JSON-RPC 2.0 protocol implementation
│   ├── parser/
│   │   └── base_agent.py       # BA_op.json parser
│   ├── matching/
│   │   └── semantic.py         # Semantic matching with LLM
│   ├── execution/
│   │   └── executor.py         # MCP operation execution engine
│   ├── output/
│   │   └── generator.py        # Configuration output generator
│   ├── transport/
│   │   ├── base.py            # Transport layer interface
│   │   ├── stdio.py           # Stdio transport implementation
│   │   ├── http.py            # HTTP transport implementation
│   │   └── websocket.py       # WebSocket transport implementation
│   ├── session/
│   │   ├── manager.py         # Session management
│   │   ├── client.py          # MCP client implementation
│   │   └── connection_pool.py # Connection pooling
│   ├── discovery/
│   │   ├── scanner.py         # Server discovery
│   │   ├── inspector.py       # Capability inspection
│   │   └── registry.py        # Server registry
│   ├── cache/
│   │   └── manager.py         # Caching layer
│   ├── monitoring/
│   │   └── metrics.py         # Performance monitoring
│   └── utils/
│       └── exceptions.py      # Custom exceptions
├── servers/                   # Domain-specific MCP servers
│   ├── finance/
│   ├── productivity/
│   ├── education/
│   ├── sports/
│   └── software_dev/
├── config/                    # Configuration files
├── tests/                     # Test suite
├── requirements/              # Dependency management
└── docs/                      # Documentation
```

## Features

### Core Functionality
- **BA_op.json Parsing**: Comprehensive parser for complex workflow definitions
- **Semantic Matching**: LLM-powered matching of requirements to capabilities
- **Multi-Domain Support**: Finance, Productivity, Education, Sports, Software Development
- **Execution Engine**: Concurrent execution of MCP operations
- **Configuration Generation**: Structured MCP configuration output

### Domain Servers
Each domain server implements the MCP protocol and provides:

#### Finance Server
- File reader operations
- Bank statement parsing
- Subscription detection
- Budget planning
- Financial advice generation
- Spending pattern visualization
- Progress monitoring

#### Productivity Server
- Email summarization
- Meeting assistance
- Task conversion
- Calendar optimization
- Smart reply generation
- Focus time scheduling
- Collaboration enhancement
- Workflow automation
- Productivity analysis
- Goal tracking

#### Education Server
- Research assistance
- Paper summarization
- Career guidance
- Skill recommendations
- Study planning
- Adaptive learning
- Knowledge assessment
- Learning path generation
- Progress tracking
- Collaborative learning

#### Sports Server
- Performance analysis
- Match prediction
- Training optimization
- Injury prevention
- Nutrition planning
- Recovery monitoring
- Tactical analysis
- Scout reporting
- Fitness tracking
- Competition planning

#### Software Development Server
- CI/CD automation
- Code optimization
- API documentation generation
- Code review
- Security scanning
- Performance analysis
- Test generation
- Dependency management
- Architecture analysis
- Deployment optimization

## Installation

### Prerequisites
- Python 3.8+
- LM Studio with openhermes-2.5-mistral-7b model
- Local LLM server running on http://127.0.0.1:1234

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd mcp-module

# Install dependencies
pip install -r requirements/base.txt

# For development
pip install -r requirements/dev.txt
```

## Usage

### Basic Usage
```python
import asyncio
from src.main import MCPModule

async def main():
    # Initialize MCP module
    mcp_module = MCPModule()
    
    # Process BA_op.json file
    ba_op_path = "path/to/BA_op.json"
    mcp_config = await mcp_module.process_ba_output(ba_op_path)
    
    # Save configuration
    output_path = "mcp_configuration_output.json"
    await mcp_module.output_generator.save_config(mcp_config, output_path)

# Run
asyncio.run(main())
```

### Running the Test Suite
```bash
python test_mcp_module.py
```

## Configuration

### LLM Configuration
The module uses a local LLM for semantic matching. Configure in `src/matching/semantic.py`:

```python
@dataclass
class MatchingConfig:
    llm_endpoint: str = "http://127.0.0.1:1234/v1/chat/completions"
    model: str = "openhermes-2.5-mistral-7b"
    temperature: float = 0.3
    max_tokens: int = 1000
    threshold: float = 0.7
```

### Server Configuration
Domain servers are configured in the `servers/` directory. Each server implements:
- MCP protocol over stdio transport
- Domain-specific tools, resources, and prompts
- Simulated execution logic

## Input Format

The module expects BA_op.json files with the following structure:

```json
{
  "workflow_metadata": {
    "workflow_id": "string",
    "workflow_name": "string",
    "domain": "string",
    "version": "string",
    "description": "string",
    "created_by": "string",
    "created_at": "ISO8601 timestamp"
  },
  "agents": [
    {
      "agent_id": "string",
      "agent_name": "string",
      "position": "number",
      "identity": {
        "role": "string",
        "agent_type": "string",
        "description": "string"
      },
      "data_interface": {
        "input": {"types": ["string"], "schema": {}, "validation": []},
        "output": {"types": ["string"], "schema": {}, "delivery": "string"}
      },
      "llm_config": {
        "provider": "string",
        "model": "string",
        "params": {},
        "reasoning": "string"
      },
      "tools": [
        {
          "name": "string",
          "server": "string",
          "purpose": "string",
          "auth_required": "boolean"
        }
      ],
      "state": {},
      "interface": {
        "primary_method": "string",
        "dependencies": [],
        "outputs_to": [],
        "error_strategy": "string"
      }
    }
  ],
  "orchestration": {
    "strategy": "string",
    "parallel_execution": "boolean",
    "error_handling": "string",
    "retry_policy": {},
    "timeout": "number",
    "dependencies": []
  },
  "domain_config": {
    "domain": "string",
    "specific_requirements": [],
    "constraints": {},
    "preferences": {}
  }
}
```

## Output Format

The module generates comprehensive MCP configurations:

```json
{
  "metadata": {
    "workflow_id": "string",
    "workflow_name": "string",
    "domain": "string",
    "version": "string",
    "mcp_module_version": "string",
    "protocol_version": "string",
    "generated_at": "ISO8601 timestamp"
  },
  "servers": {
    "server_name": {
      "transport": {
        "type": "stdio",
        "command": ["python", "server_script.py"]
      },
      "capabilities": {
        "tools": [...],
        "resources": [...],
        "prompts": [...]
      },
      "execution_stats": {...},
      "status": "active"
    }
  },
  "workflow": {
    "agents": [...],
    "orchestration": {...},
    "domain_config": {...}
  },
  "execution_summary": {
    "total_operations": "number",
    "successful_operations": "number",
    "failed_operations": "number",
    "total_execution_time": "number",
    "average_execution_time": "number",
    "by_category": {...},
    "by_server": {...},
    "errors": [...]
  },
  "capabilities": {
    "total_matches": "number",
    "by_category": {...},
    "by_server": {...},
    "match_quality": {...}
  }
}
```

## Development

### Adding New Domains
1. Create a new directory in `servers/`
2. Implement `server.py` with MCP protocol
3. Implement `tools.py` with domain-specific logic
4. Add domain capabilities to `src/matching/semantic.py`
5. Update server paths in `src/execution/executor.py`

### Extending Capabilities
- Add new tools, resources, or prompts to domain servers
- Update semantic matching logic in `src/matching/semantic.py`
- Extend execution engine in `src/execution/executor.py`
- Enhance output generation in `src/output/generator.py`

## Testing

### Running Tests
```bash
# Run complete test suite
python test_mcp_module.py

# Run individual component tests
python -m pytest tests/
```

### Test Coverage
- Unit tests for all components
- Integration tests for complete workflow
- Mock LLM responses for testing
- Sample BA_op.json data for validation

## Performance

### Optimization Features
- Concurrent execution of MCP operations
- Connection pooling for server communication
- Caching layer for repeated operations
- Performance monitoring and metrics
- Efficient semantic matching with LLM

### Monitoring
- Real-time execution metrics
- Performance profiling
- Error tracking and reporting
- Resource utilization monitoring

## Troubleshooting

### Common Issues

1. **LLM Connection Failed**
   - Ensure LM Studio is running
   - Verify endpoint URL: http://127.0.0.1:1234
   - Check model availability

2. **Server Execution Errors**
   - Verify server script paths
   - Check Python environment
   - Review server logs

3. **Parsing Errors**
   - Validate BA_op.json format
   - Check required fields
   - Review error messages

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## License

[License information]

## Support

For issues and questions:
- Create an issue in the repository
- Check the documentation
- Review troubleshooting guide
