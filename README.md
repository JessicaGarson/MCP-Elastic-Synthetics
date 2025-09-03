# Automating User Journeys for Elastic Synthetics with Warp, Gemini & MCP
Elastic Synthetics enables you to track user pathways using a global testing infrastructure, emulating the full user path to measure the impact of web applications. It provides comprehensive insights into website performance, functionality, and availability across development and production environments, helping you identify and resolve issues before they impact customers. One of its main features is the ability to create user journeys, which can be done with or without code. Using Playwright under the hood, Elastic makes it easy to author synthetic browser tests with additional configuration.

This experimental project demonstrates how to create user journeys using TypeScript and Elastic Synthetics automatically. You can use Warp as an MCP Client, Gemini 2.5 Pro. This application is written with FastMCP and wraps the Elastic Synthetics CLI agent to deploy browser tests automatically.

## Available MCP Functions

### `diagnose_warp_mcp_config`
Debugs environment variable issues. Usually only needed for troubleshooting.  

### `create_and_deploy_browser_test`
Creates Playwright tests using a template-based approach.  
- Inputs: test name, URL, schedule  
- Reliable but tests may look similar across runs.  

### `llm_create_and_deploy_test_from_prompt`
Generates Playwright tests dynamically based on your prompt.  
- Inputs: test name, URL, prompt, schedule  
- Uses an LLM for more flexible, prompt-driven test generation.  

## Getting Started

### Prerequisites
- The version of Python that is used is Python 3.12.1 but you can use any version of Python higher than 3.10.
- This demo uses Elastic Observability version 9.1.2, but you can use any version that is higher than 8.10.
- You will also need an OpenAI API key for LLM-based metrics. You will want to configure an environment variable for your OpenAI API Key, which you can find on the API keys page in [OpenAI's developer portal](https://platform.openai.com/api-keys).

### Step 1: Clone Repo & Install Packages 

```bash
git clone https://github.com/JessicaGarson/MCP-Elastic-Synthetics.git
pip install fastmcp openai
npm install -g playwright @elastic/synthetics
```

### Step 2: Configure Warp
In Warp’s MCP servers panel, add a JSON configuration file:

```json
{
  "elastic-synthetics": {
    "command": "python",
    "args": ["elastic_synthetics_server.py"],
    "env": {
      "PYTHONPATH": ".",
      "ELASTIC_KIBANA_URL": "https://your-kibana-url.elastic-cloud.com",
      "ELASTIC_API_KEY": "your-api-key-here",
      "ELASTIC_PROJECT_ID": "mcp-synthetics-demo",
      "ELASTIC_SPACE": "default",
      "ELASTIC_AUTO_PUSH": "true",
      "ELASTIC_USE_JAVASCRIPT": "false",
      "ELASTIC_INSTALL_DEPENDENCIES": "true",
      "OPENAI_API_KEY": "sk-your-openai-key",
      "LLM_MODEL": "gpt-4o"
    },
    "working_directory": "/path/to/your/file",
    "start_on_launch": true
  }
}
```

### Step 3: Run Tests
1. Toggle Agent Mode in Warp.
2. Ask a question that contains the test name, URL, prompt, and schedule. or call the function directly and you will be prompted for a test name, URL, prompt, and schedule `llm_create_and_deploy_test_from_prompt()`
3. You should be able to see the monitor you created inside of Elastic Observablity. 

## Troubleshooting 
- Pop-ups and complex flows may require additional manual adjustments.
