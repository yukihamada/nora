#!/usr/bin/env python3
"""
Nora UI - Web interface for Nora
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
    
    log_file = os.path.join(log_dir, "nora_ui.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger("nora_ui")

def main():
    """Main entry point for Nora UI."""
    logger = setup_logging()
    logger.info("Starting Nora UI")
    
    # Set up error handling
    setup_error_handling()
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize and run the agent
        agent_runner = AgentRunner(config)
        
        # Start the UI
        result = agent_runner.task_manager.execute("start nora ui", agent_runner.agents)
        
        logger.info(f"Nora UI started: {result}")
        
        # Get port from environment variable for Fly.io or use default
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Using port: {port}")
        
        # Keep the main thread running
        try:
            while True:
                input("Press Ctrl+C to exit...")
        except KeyboardInterrupt:
            logger.info("Shutting down Nora UI")
        
    except Exception as e:
        logger.error(f"Error in Nora UI: {str(e)}", exc_info=True)
        sys.exit(1)
    
    logger.info("Nora UI stopped")

if __name__ == "__main__":
    main()