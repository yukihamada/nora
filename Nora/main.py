#!/usr/bin/env python3
"""
Nora - Autonomous Software Development Agent
Main entry point for the Nora agent system.
"""

import os
import sys
import logging
from src.core.agent_runner import AgentRunner
from src.core.config import load_config
from utils.error_handler import setup_error_handling

def setup_logging():
    """Configure logging for the application."""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "nora.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger("nora")

def main():
    """Main entry point for Nora agent."""
    logger = setup_logging()
    logger.info("Starting Nora - Autonomous Software Development Agent")
    
    # Set up error handling
    setup_error_handling()
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize and run the agent
        agent_runner = AgentRunner(config)
        agent_runner.run()
        
    except Exception as e:
        logger.error(f"Error in Nora main process: {str(e)}", exc_info=True)
        sys.exit(1)
    
    logger.info("Nora agent completed successfully")

if __name__ == "__main__":
    main()