"""
LangGraph ReAct Agent for Aruba Central MCP Server

Integrates semantic tool filtering with LangGraph and Ollama for 100% local
LLM execution. Connects to the MCP server and provides an interactive CLI.
"""

import os
import sys
import asyncio
import json
from typing import TypedDict, Annotated, Sequence
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool as langchain_tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

from tool_filter import SemanticToolFilter

# Load environment variables
load_dotenv()

# Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
TOP_K_TOOLS = int(os.getenv("TOP_K_TOOLS", "8"))

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class AgentState(TypedDict):
    """State for the LangGraph agent."""
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    filtered_tool_names: Annotated[list[str], "Names of tools filtered for this query"]


class MCPToolManager:
    """
    Manages connection to the Aruba Central MCP server and converts
    MCP tools to LangChain-compatible tools.
    """
    
    def __init__(self):
        """Initialize the MCP tool manager."""
        self.session = None
        self.mcp_tools = {}
        self.langchain_tools = {}
        
        # Read MCP server config from environment
        self.base_url = os.getenv("ARUBA_CENTRAL_BASE_URL", "https://apigw-uswest4.central.arubanetworks.com")
        self.token = os.getenv("ARUBA_CENTRAL_TOKEN", "")
        self.client_id = os.getenv("ARUBA_CENTRAL_CLIENT_ID", "")
        self.client_secret = os.getenv("ARUBA_CENTRAL_CLIENT_SECRET", "")
        self.refresh_token = os.getenv("ARUBA_CENTRAL_REFRESH_TOKEN", "")
        self.timeout = os.getenv("ARUBA_CENTRAL_TIMEOUT", "30")
        
        if not all([self.token, self.client_id, self.client_secret, self.refresh_token]):
            print(f"{Colors.WARNING}Warning: Some Aruba Central credentials are missing from environment.{Colors.ENDC}")
            print("Please set ARUBA_CENTRAL_TOKEN, ARUBA_CENTRAL_CLIENT_ID, ARUBA_CENTRAL_CLIENT_SECRET, and ARUBA_CENTRAL_REFRESH_TOKEN")
    
    async def connect(self):
        """Connect to the MCP server and load all tools."""
        print(f"{Colors.OKBLUE}Connecting to Aruba Central MCP server...{Colors.ENDC}")
        
        # Get the path to the MCP server script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        server_script = os.path.join(script_dir, "aruba_central_mcp_server.py")
        
        if not os.path.exists(server_script):
            raise FileNotFoundError(f"MCP server script not found: {server_script}")
        
        # Set up environment for the server
        env = os.environ.copy()
        env.update({
            "ARUBA_CENTRAL_BASE_URL": self.base_url,
            "ARUBA_CENTRAL_TOKEN": self.token,
            "ARUBA_CENTRAL_CLIENT_ID": self.client_id,
            "ARUBA_CENTRAL_CLIENT_SECRET": self.client_secret,
            "ARUBA_CENTRAL_REFRESH_TOKEN": self.refresh_token,
            "ARUBA_CENTRAL_TIMEOUT": self.timeout
        })
        
        # Create server parameters
        server_params = StdioServerParameters(
            command="python3",
            args=[server_script],
            env=env
        )
        
        # Connect to the server
        stdio_transport = stdio_client(server_params)
        self.stdio, self.write = await stdio_transport.__aenter__()
        self.session = ClientSession(self.stdio, self.write)
        await self.session.__aenter__()
        
        # Initialize the session
        await self.session.initialize()
        
        # List available tools
        tools_response = await self.session.list_tools()
        
        print(f"{Colors.OKGREEN}Connected! Loaded {len(tools_response.tools)} MCP tools{Colors.ENDC}")
        
        # Store MCP tools
        for mcp_tool in tools_response.tools:
            self.mcp_tools[mcp_tool.name] = mcp_tool
            
            # Convert to LangChain tool
            self.langchain_tools[mcp_tool.name] = self._create_langchain_tool(mcp_tool)
    
    def _create_langchain_tool(self, mcp_tool):
        """Convert an MCP tool to a LangChain tool."""
        
        # Create a closure to capture the tool name
        tool_name = mcp_tool.name
        tool_description = mcp_tool.description or f"Execute {tool_name}"
        
        async def execute_tool(**kwargs):
            """Execute the MCP tool."""
            try:
                result = await self.session.call_tool(tool_name, arguments=kwargs)
                if result.content:
                    # Extract text from content
                    text_parts = [item.text for item in result.content if hasattr(item, 'text')]
                    return "\n".join(text_parts) if text_parts else str(result.content)
                return "Tool executed successfully (no output)"
            except Exception as e:
                return f"Error executing tool: {str(e)}"
        
        # Create a LangChain tool
        lc_tool = langchain_tool(execute_tool)
        lc_tool.name = tool_name
        lc_tool.description = tool_description
        
        return lc_tool
    
    def get_tools_by_names(self, tool_names: list[str]):
        """Get LangChain tools by their names."""
        return [self.langchain_tools[name] for name in tool_names if name in self.langchain_tools]
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.__aexit__(None, None, None)
        print(f"{Colors.OKBLUE}Disconnected from MCP server{Colors.ENDC}")


class ArubaLangGraphAgent:
    """
    LangGraph ReAct agent with semantic tool filtering for Aruba Central.
    """
    
    def __init__(self, tool_manager: MCPToolManager, semantic_filter: SemanticToolFilter):
        """
        Initialize the LangGraph agent.
        
        Args:
            tool_manager: MCPToolManager instance
            semantic_filter: SemanticToolFilter instance
        """
        self.tool_manager = tool_manager
        self.semantic_filter = semantic_filter
        
        # Initialize LLM
        print(f"{Colors.OKBLUE}Initializing Ollama LLM: {OLLAMA_MODEL}...{Colors.ENDC}")
        self.llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_URL,
            temperature=0
        )
        
        # Build the graph
        self._build_graph()
        
        print(f"{Colors.OKGREEN}LangGraph agent initialized{Colors.ENDC}")
    
    def _build_graph(self):
        """Build the LangGraph state graph."""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("filter_tools", self._filter_tools_node)
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("execute_tools", self._execute_tools_node)
        
        # Add edges
        workflow.set_entry_point("filter_tools")
        workflow.add_edge("filter_tools", "agent")
        
        # Conditional edge: after agent, check if we need to execute tools
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "execute_tools",
                "end": END
            }
        )
        
        # After executing tools, go back to agent for reasoning
        workflow.add_edge("execute_tools", "agent")
        
        # Compile the graph
        self.graph = workflow.compile()
    
    async def _filter_tools_node(self, state: AgentState) -> AgentState:
        """Node that filters tools based on the user query."""
        # Get the last user message
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        if not user_messages:
            state["filtered_tool_names"] = []
            return state
        
        query = user_messages[-1].content
        
        # Filter tools
        filtered_tools = self.semantic_filter.filter(query, top_k=TOP_K_TOOLS)
        state["filtered_tool_names"] = filtered_tools
        
        # Print filtered tools
        print(f"\n{Colors.OKCYAN}🔍 Filtered tools ({len(filtered_tools)}/{len(self.semantic_filter.tool_names)}):{Colors.ENDC}")
        for i, tool_name in enumerate(filtered_tools, 1):
            print(f"  {i}. {tool_name}")
        print()
        
        return state
    
    async def _agent_node(self, state: AgentState) -> AgentState:
        """Node that calls the LLM with filtered tools."""
        # Get the filtered tools
        filtered_tool_names = state.get("filtered_tool_names", [])
        langchain_tools = self.tool_manager.get_tools_by_names(filtered_tool_names)
        
        # Bind tools to the LLM
        llm_with_tools = self.llm.bind_tools(langchain_tools)
        
        try:
            # Call the LLM
            response = await llm_with_tools.ainvoke(state["messages"])
        except Exception as e:
            # If LLM invocation fails, return an error message
            user_query = next((msg.content for msg in state["messages"] if isinstance(msg, HumanMessage)), "unknown")
            error_msg = f"LLM invocation failed for query '{user_query}': {str(e)}"
            print(f"{Colors.FAIL}Error: {error_msg}{Colors.ENDC}")
            response = AIMessage(content=error_msg)
        
        # Add the response to messages
        state["messages"] = state["messages"] + [response]
        
        return state
    
    async def _execute_tools_node(self, state: AgentState) -> AgentState:
        """Node that executes tool calls."""
        # Get the last AI message with tool calls
        last_message = state["messages"][-1]
        
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return state
        
        # Execute each tool call
        tool_messages = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            print(f"{Colors.WARNING}🔧 Executing tool: {tool_name}{Colors.ENDC}")
            print(f"   Args: {json.dumps(tool_args, indent=2)}")
            
            # Get the tool and execute it
            if tool_name in self.tool_manager.langchain_tools:
                tool = self.tool_manager.langchain_tools[tool_name]
                try:
                    # Execute the async tool
                    result = await tool.func(**tool_args)
                    print(f"{Colors.OKGREEN}✓ Tool completed{Colors.ENDC}\n")
                except Exception as e:
                    result = f"Error executing tool '{tool_name}' with args {tool_args}: {str(e)}"
                    print(f"{Colors.FAIL}✗ Tool failed: {str(e)}{Colors.ENDC}\n")
                
                # Create tool message
                tool_messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"]
                    )
                )
        
        # Add tool messages to state
        state["messages"] = state["messages"] + tool_messages
        
        return state
    
    def _should_continue(self, state: AgentState):
        """Determine if we should continue or end."""
        last_message = state["messages"][-1]
        
        # If the last message has tool calls, continue
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        
        # Otherwise, end
        return "end"
    
    async def run(self, query: str):
        """
        Run the agent on a query.
        
        Args:
            query: User query
            
        Returns:
            Final response from the agent
        """
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "filtered_tool_names": []
        }
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Get the final response
        final_message = final_state["messages"][-1]
        
        return final_message.content if hasattr(final_message, "content") else str(final_message)


async def main():
    """Main interactive CLI loop."""
    print(f"\n{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}Aruba Central LangGraph Agent with Semantic Tool Filtering{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n")
    
    print(f"Model: {OLLAMA_MODEL}")
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"Top-K tools: {TOP_K_TOOLS}")
    print()
    
    # Initialize components
    semantic_filter = SemanticToolFilter()
    tool_manager = MCPToolManager()
    
    try:
        # Connect to MCP server
        await tool_manager.connect()
        
        # Initialize agent
        agent = ArubaLangGraphAgent(tool_manager, semantic_filter)
        
        print(f"\n{Colors.OKGREEN}Ready! Type your queries or 'quit' to exit.{Colors.ENDC}\n")
        
        # Interactive loop
        while True:
            try:
                # Get user input
                query = input(f"{Colors.BOLD}You:{Colors.ENDC} ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ["quit", "exit", "q"]:
                    print(f"\n{Colors.OKBLUE}Goodbye!{Colors.ENDC}\n")
                    break
                
                # Run the agent
                print(f"\n{Colors.OKBLUE}Processing query...{Colors.ENDC}\n")
                start_time = datetime.now()
                
                response = await agent.run(query)
                
                elapsed = (datetime.now() - start_time).total_seconds()
                
                # Print response
                print(f"\n{Colors.OKGREEN}{Colors.BOLD}Assistant:{Colors.ENDC} {response}\n")
                print(f"{Colors.OKCYAN}[Completed in {elapsed:.2f}s]{Colors.ENDC}\n")
                print("-" * 80 + "\n")
                
            except KeyboardInterrupt:
                print(f"\n\n{Colors.OKBLUE}Goodbye!{Colors.ENDC}\n")
                break
            except Exception as e:
                print(f"\n{Colors.FAIL}Error: {str(e)}{Colors.ENDC}\n")
    
    finally:
        # Cleanup
        await tool_manager.disconnect()


if __name__ == "__main__":
    """Run the interactive CLI."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
