"""
Agent Runner module for Nora.
Handles the initialization and execution of agents.
"""

import logging
import importlib
import os
from typing import Dict, Any, List

logger = logging.getLogger("nora.agent_runner")

class AgentRunner:
    """
    Manages the execution of Nora agents.
    Coordinates between different specialized agents to complete tasks.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the AgentRunner.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
        """
        self.config = config
        self.agents = {}
        self._load_agents()
        
        # Task manager is the main coordinator
        self.task_manager = self.agents.get("task_manager")
        if not self.task_manager:
            logger.error("Task manager agent not found. Cannot proceed.")
            raise ValueError("Task manager agent is required")
    
    def _load_agents(self):
        """Load all available agents from the agents directory."""
        agents_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents")
        
        # List of core agents to load
        core_agents = [
            "task_manager",
            "web_agent",
            "code_agent",
            "deployment_agent",
            "nora_ui_agent"
        ]
        
        for agent_name in core_agents:
            try:
                # Dynamically import the agent module
                module_path = f"src.agents.{agent_name}"
                module = importlib.import_module(module_path)
                
                # Get the agent class (assumed to be capitalized version of the filename)
                class_name = "".join(word.capitalize() for word in agent_name.split("_"))
                agent_class = getattr(module, class_name)
                
                # Initialize the agent with config
                self.agents[agent_name] = agent_class(self.config)
                logger.info(f"Loaded agent: {agent_name}")
                
            except (ImportError, AttributeError) as e:
                logger.warning(f"Failed to load agent {agent_name}: {str(e)}")
        
        # Log the loaded agents
        logger.info(f"Loaded {len(self.agents)} agents: {', '.join(self.agents.keys())}")
    
    def run(self, task: str = None):
        """
        Run the Nora agent system.
        
        Args:
            task (str, optional): Initial task description. If None, will wait for user input.
        """
        if not task:
            task = self._get_user_task()
        
        logger.info(f"Starting task: {task}")
        
        # Pass the task to the task manager
        result = self.task_manager.execute(task, self.agents)
        
        logger.info("Task completed")
        return result
    
    def _get_user_task(self) -> str:
        """
        Get task description from user input.
        
        Returns:
            str: Task description
        """
        print("\n=== Nora - Autonomous Software Development Agent ===")
        print("What would you like me to do? (Type your request below)")
        return input("> ")