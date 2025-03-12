"""
Task Manager Agent for Nora.
Coordinates between different specialized agents to complete tasks.
"""

import logging
from typing import Dict, Any, List, Optional
import json
import os
from utils.helpers import generate_unique_id, get_timestamp

logger = logging.getLogger("nora.agents.task_manager")

class TaskManager:
    """
    Task Manager Agent for Nora.
    Responsible for breaking down tasks, coordinating between agents, and tracking progress.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Task Manager agent.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
        """
        self.config = config
        self.task_history = []
        self.current_task = None
        
        # Load task history if available
        self._load_task_history()
    
    def execute(self, task_description: str, agents: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task by coordinating between specialized agents.
        
        Args:
            task_description (str): Description of the task to execute
            agents (Dict[str, Any]): Dictionary of available agents
            
        Returns:
            Dict[str, Any]: Task result
        """
        # Create a new task
        task_id = generate_unique_id()
        self.current_task = {
            "id": task_id,
            "description": task_description,
            "status": "in_progress",
            "created_at": get_timestamp(),
            "updated_at": get_timestamp(),
            "steps": [],
            "result": None
        }
        
        logger.info(f"Starting task {task_id}: {task_description}")
        
        try:
            # Break down the task into steps
            steps = self._break_down_task(task_description)
            self.current_task["steps"] = steps
            
            # Execute each step using the appropriate agent
            results = []
            for step in steps:
                step_result = self._execute_step(step, agents)
                results.append(step_result)
                
                # Update task status
                self.current_task["updated_at"] = get_timestamp()
                self.current_task["steps"][steps.index(step)]["status"] = "completed"
                self.current_task["steps"][steps.index(step)]["result"] = step_result
                
                # Save progress
                self._save_task_history()
            
            # Compile final result
            final_result = self._compile_results(results)
            self.current_task["result"] = final_result
            self.current_task["status"] = "completed"
            self.current_task["updated_at"] = get_timestamp()
            
            # Add to task history
            self.task_history.append(self.current_task)
            self._save_task_history()
            
            logger.info(f"Task {task_id} completed successfully")
            return final_result
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            self.current_task["status"] = "failed"
            self.current_task["error"] = str(e)
            self.current_task["updated_at"] = get_timestamp()
            self._save_task_history()
            raise
    
    def _break_down_task(self, task_description: str) -> List[Dict[str, Any]]:
        """
        Break down a task into smaller steps.
        
        Args:
            task_description (str): Description of the task
            
        Returns:
            List[Dict[str, Any]]: List of steps
        """
        # This is a simplified implementation
        # In a real implementation, this would use the LLM to break down the task
        
        # Example task breakdown for a web app creation task
        if "web app" in task_description.lower() or "website" in task_description.lower():
            return [
                {
                    "id": generate_unique_id(),
                    "description": "Research and gather information",
                    "agent": "web_agent",
                    "status": "pending"
                },
                {
                    "id": generate_unique_id(),
                    "description": "Generate code for the application",
                    "agent": "code_agent",
                    "status": "pending"
                },
                {
                    "id": generate_unique_id(),
                    "description": "Test the application",
                    "agent": "code_agent",
                    "status": "pending"
                },
                {
                    "id": generate_unique_id(),
                    "description": "Deploy the application",
                    "agent": "deployment_agent",
                    "status": "pending"
                }
            ]
        
        # Example task breakdown for a data analysis task
        elif "data" in task_description.lower() or "analysis" in task_description.lower():
            return [
                {
                    "id": generate_unique_id(),
                    "description": "Gather data and information",
                    "agent": "web_agent",
                    "status": "pending"
                },
                {
                    "id": generate_unique_id(),
                    "description": "Generate data analysis code",
                    "agent": "code_agent",
                    "status": "pending"
                },
                {
                    "id": generate_unique_id(),
                    "description": "Run analysis and generate visualizations",
                    "agent": "code_agent",
                    "status": "pending"
                }
            ]
        
        # Default task breakdown
        else:
            return [
                {
                    "id": generate_unique_id(),
                    "description": "Research and gather information",
                    "agent": "web_agent",
                    "status": "pending"
                },
                {
                    "id": generate_unique_id(),
                    "description": "Generate solution",
                    "agent": "code_agent",
                    "status": "pending"
                }
            ]
    
    def _execute_step(self, step: Dict[str, Any], agents: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step using the appropriate agent.
        
        Args:
            step (Dict[str, Any]): Step to execute
            agents (Dict[str, Any]): Dictionary of available agents
            
        Returns:
            Dict[str, Any]: Step result
        """
        agent_name = step["agent"]
        agent = agents.get(agent_name)
        
        if not agent:
            logger.error(f"Agent {agent_name} not found")
            raise ValueError(f"Agent {agent_name} not found")
        
        logger.info(f"Executing step {step['id']}: {step['description']} with agent {agent_name}")
        
        # Execute the step with the agent
        result = agent.execute(step["description"])
        
        logger.info(f"Step {step['id']} completed")
        return result
    
    def _compile_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compile results from multiple steps into a final result.
        
        Args:
            results (List[Dict[str, Any]]): List of step results
            
        Returns:
            Dict[str, Any]: Compiled result
        """
        # This is a simplified implementation
        # In a real implementation, this would use the LLM to compile the results
        
        compiled_result = {
            "summary": "Task completed successfully",
            "steps_completed": len(results),
            "details": results
        }
        
        return compiled_result
    
    def _load_task_history(self):
        """Load task history from disk."""
        history_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                  "data", "task_history.json")
        
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r') as f:
                    self.task_history = json.load(f)
                logger.info(f"Loaded {len(self.task_history)} tasks from history")
            except Exception as e:
                logger.error(f"Error loading task history: {str(e)}")
                self.task_history = []
    
    def _save_task_history(self):
        """Save task history to disk."""
        history_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                  "data", "task_history.json")
        
        try:
            directory = os.path.dirname(history_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(history_path, 'w') as f:
                json.dump(self.task_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving task history: {str(e)}")