"""
Nora UI Agent for Nora.
Provides a web-based user interface for interacting with Nora.
"""

import logging
import os
import json
import time
from typing import Dict, Any, List, Optional
from flask import Flask, render_template, request, jsonify, redirect, url_for
import threading
from utils.helpers import generate_unique_id
from utils.file_utils import ensure_directory

logger = logging.getLogger("nora.agents.nora_ui_agent")

class NoraUIAgent:
    """
    Nora UI Agent for Nora.
    Provides a web-based user interface for interacting with Nora.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Nora UI Agent.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
        """
        self.config = config
        self.app = Flask(__name__)
        self.port = 58281
        self.server_thread = None
        self.task_history = []
        self.projects = []
        self.is_running = False
        
        # Set up routes
        self._setup_routes()
        
        # Load task history and projects
        self._load_data()
    
    def execute(self, task_description: str) -> Dict[str, Any]:
        """
        Execute a UI-related task.
        
        Args:
            task_description (str): Description of the task to execute
            
        Returns:
            Dict[str, Any]: Task result
        """
        logger.info(f"Nora UI Agent executing task: {task_description}")
        
        try:
            # Start the UI server if it's not already running
            if not self.is_running:
                self._start_server()
                return {
                    "status": "success",
                    "message": f"Nora UI started on http://localhost:{self.port}",
                    "url": f"http://localhost:{self.port}"
                }
            else:
                return {
                    "status": "success",
                    "message": f"Nora UI is already running on http://localhost:{self.port}",
                    "url": f"http://localhost:{self.port}"
                }
        except Exception as e:
            logger.error(f"Error in Nora UI Agent: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _setup_routes(self):
        """Set up Flask routes for the UI."""
        
        @self.app.route('/')
        def index():
            """Home page."""
            return render_template('index.html', 
                                  task_history=self.task_history,
                                  projects=self.projects)
        
        @self.app.route('/submit_task', methods=['POST'])
        def submit_task():
            """Submit a new task."""
            task = request.form.get('task', '').strip()
            if task:
                # In a real implementation, this would submit the task to the task manager
                task_id = generate_unique_id()
                new_task = {
                    "id": task_id,
                    "description": task,
                    "status": "pending",
                    "created_at": time.time(),
                    "updated_at": time.time()
                }
                self.task_history.append(new_task)
                self._save_data()
                
                # Redirect to the task page
                return redirect(url_for('task', task_id=task_id))
            return redirect(url_for('index'))
        
        @self.app.route('/task/<task_id>')
        def task(task_id):
            """Task details page."""
            task = next((t for t in self.task_history if t["id"] == task_id), None)
            if task:
                return render_template('task.html', task=task)
            return redirect(url_for('index'))
        
        @self.app.route('/projects')
        def projects():
            """Projects page."""
            return render_template('projects.html', projects=self.projects)
        
        @self.app.route('/project/<project_id>')
        def project(project_id):
            """Project details page."""
            project = next((p for p in self.projects if p["id"] == project_id), None)
            if project:
                return render_template('project.html', project=project)
            return redirect(url_for('projects'))
        
        @self.app.route('/api/tasks')
        def api_tasks():
            """API endpoint for tasks."""
            return jsonify(self.task_history)
        
        @self.app.route('/api/projects')
        def api_projects():
            """API endpoint for projects."""
            return jsonify(self.projects)
    
    def _start_server(self):
        """Start the Flask server in a separate thread."""
        if not self.is_running:
            def run_server():
                self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
            
            self.server_thread = threading.Thread(target=run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            self.is_running = True
            logger.info(f"Nora UI server started on port {self.port}")
    
    def _load_data(self):
        """Load task history and projects from disk."""
        # Load task history
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
        
        # Load projects
        projects_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                  "data", "generated")
        
        if os.path.exists(projects_dir):
            try:
                # Get all project directories
                project_dirs = [d for d in os.listdir(projects_dir) 
                              if os.path.isdir(os.path.join(projects_dir, d)) and d.startswith("project_")]
                
                # Load project information
                for project_dir in project_dirs:
                    project_id = project_dir.replace("project_", "")
                    project_path = os.path.join(projects_dir, project_dir)
                    
                    # Check if README.md exists
                    readme_path = os.path.join(project_path, "README.md")
                    description = ""
                    if os.path.exists(readme_path):
                        with open(readme_path, 'r') as f:
                            # Extract the first line as the title
                            first_line = f.readline().strip()
                            if first_line.startswith("# "):
                                description = first_line[2:]
                    
                    # Get list of files
                    files = [f for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f))]
                    
                    # Add project to list
                    self.projects.append({
                        "id": project_id,
                        "name": f"Project {project_id[:8]}",
                        "description": description,
                        "path": project_path,
                        "files": files,
                        "created_at": os.path.getctime(project_path)
                    })
                
                logger.info(f"Loaded {len(self.projects)} projects")
            except Exception as e:
                logger.error(f"Error loading projects: {str(e)}")
                self.projects = []
    
    def _save_data(self):
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
    
    def create_templates(self):
        """Create the HTML templates for the UI."""
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        ensure_directory(templates_dir)
        
        # Create index.html
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nora - Autonomous Software Development Agent</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px 0;
            text-align: center;
            border-radius: 8px 8px 0 0;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        .header p {
            margin: 10px 0 0;
            font-size: 1.2rem;
            opacity: 0.8;
        }
        .task-form {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #2c3e50;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            box-sizing: border-box;
        }
        textarea {
            height: 120px;
            resize: vertical;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        .task-history {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .task-history h2 {
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .task-list {
            list-style-type: none;
            padding: 0;
        }
        .task-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .task-item:last-child {
            border-bottom: none;
        }
        .task-info {
            flex: 1;
        }
        .task-description {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .task-status {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .status-pending {
            background-color: #f39c12;
            color: white;
        }
        .status-in-progress {
            background-color: #3498db;
            color: white;
        }
        .status-completed {
            background-color: #2ecc71;
            color: white;
        }
        .status-failed {
            background-color: #e74c3c;
            color: white;
        }
        .task-date {
            font-size: 12px;
            color: #7f8c8d;
        }
        .task-actions a {
            text-decoration: none;
            color: #3498db;
            margin-left: 10px;
        }
        .task-actions a:hover {
            text-decoration: underline;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px 0;
            color: #7f8c8d;
            font-size: 0.9rem;
        }
        .nav {
            display: flex;
            background-color: white;
            padding: 10px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .nav a {
            text-decoration: none;
            color: #2c3e50;
            padding: 10px 15px;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .nav a:hover, .nav a.active {
            background-color: #f5f5f5;
        }
        .nav a.active {
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Nora</h1>
            <p>Autonomous Software Development Agent</p>
        </div>
        
        <div class="nav">
            <a href="/" class="active">Home</a>
            <a href="/projects">Projects</a>
        </div>
        
        <div class="task-form">
            <h2>What would you like me to do?</h2>
            <form action="/submit_task" method="post">
                <div class="form-group">
                    <label for="task">Task Description</label>
                    <textarea id="task" name="task" placeholder="Describe your task here..." required></textarea>
                </div>
                <button type="submit">Submit Task</button>
            </form>
        </div>
        
        <div class="task-history">
            <h2>Task History</h2>
            {% if task_history %}
                <ul class="task-list">
                    {% for task in task_history %}
                        <li class="task-item">
                            <div class="task-info">
                                <div class="task-description">{{ task.description }}</div>
                                <div class="task-date">Created: {{ task.created_at|timestamp_to_date }}</div>
                            </div>
                            <div class="task-status status-{{ task.status }}">{{ task.status }}</div>
                            <div class="task-actions">
                                <a href="/task/{{ task.id }}">View Details</a>
                            </div>
                        </li>
                    {% endfor %}
                </ul>
            {% else %}
                <p>No tasks yet. Submit a task to get started!</p>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>Powered by Nora - Autonomous Software Development Agent</p>
            <p>&copy; 2025 Nora</p>
        </div>
    </div>
</body>
</html>"""
        
        # Create task.html
        task_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nora - Task Details</title>
    <style>
        /* Same styles as index.html */
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px 0;
            text-align: center;
            border-radius: 8px 8px 0 0;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        .header p {
            margin: 10px 0 0;
            font-size: 1.2rem;
            opacity: 0.8;
        }
        .task-details {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .task-details h2 {
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .task-status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 20px;
        }
        .status-pending {
            background-color: #f39c12;
            color: white;
        }
        .status-in-progress {
            background-color: #3498db;
            color: white;
        }
        .status-completed {
            background-color: #2ecc71;
            color: white;
        }
        .status-failed {
            background-color: #e74c3c;
            color: white;
        }
        .task-info {
            margin-bottom: 20px;
        }
        .task-info-item {
            margin-bottom: 10px;
        }
        .task-info-label {
            font-weight: bold;
            color: #2c3e50;
        }
        .task-description {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .task-results {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
        }
        .back-button {
            display: inline-block;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            padding: 10px 15px;
            border-radius: 4px;
            margin-top: 20px;
            font-weight: bold;
        }
        .back-button:hover {
            background-color: #2980b9;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px 0;
            color: #7f8c8d;
            font-size: 0.9rem;
        }
        .nav {
            display: flex;
            background-color: white;
            padding: 10px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .nav a {
            text-decoration: none;
            color: #2c3e50;
            padding: 10px 15px;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .nav a:hover, .nav a.active {
            background-color: #f5f5f5;
        }
        .nav a.active {
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Nora</h1>
            <p>Autonomous Software Development Agent</p>
        </div>
        
        <div class="nav">
            <a href="/">Home</a>
            <a href="/projects">Projects</a>
        </div>
        
        <div class="task-details">
            <h2>Task Details</h2>
            
            <div class="task-status status-{{ task.status }}">{{ task.status }}</div>
            
            <div class="task-description">
                {{ task.description }}
            </div>
            
            <div class="task-info">
                <div class="task-info-item">
                    <span class="task-info-label">Task ID:</span> {{ task.id }}
                </div>
                <div class="task-info-item">
                    <span class="task-info-label">Created:</span> {{ task.created_at|timestamp_to_date }}
                </div>
                <div class="task-info-item">
                    <span class="task-info-label">Updated:</span> {{ task.updated_at|timestamp_to_date }}
                </div>
            </div>
            
            {% if task.result %}
                <h3>Results</h3>
                <div class="task-results">
                    <pre>{{ task.result|tojson(indent=2) }}</pre>
                </div>
            {% endif %}
            
            <a href="/" class="back-button">Back to Home</a>
        </div>
        
        <div class="footer">
            <p>Powered by Nora - Autonomous Software Development Agent</p>
            <p>&copy; 2025 Nora</p>
        </div>
    </div>
</body>
</html>"""
        
        # Create projects.html
        projects_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nora - Projects</title>
    <style>
        /* Same styles as index.html */
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px 0;
            text-align: center;
            border-radius: 8px 8px 0 0;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        .header p {
            margin: 10px 0 0;
            font-size: 1.2rem;
            opacity: 0.8;
        }
        .projects-container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .projects-container h2 {
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .project-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .project-card {
            background-color: #f8f9fa;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .project-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .project-header {
            background-color: #3498db;
            color: white;
            padding: 15px;
        }
        .project-name {
            margin: 0;
            font-size: 1.2rem;
        }
        .project-body {
            padding: 15px;
        }
        .project-description {
            margin-bottom: 15px;
            color: #2c3e50;
        }
        .project-date {
            font-size: 12px;
            color: #7f8c8d;
            margin-bottom: 15px;
        }
        .project-files {
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 15px;
        }
        .project-link {
            display: inline-block;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 14px;
        }
        .project-link:hover {
            background-color: #2980b9;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px 0;
            color: #7f8c8d;
            font-size: 0.9rem;
        }
        .nav {
            display: flex;
            background-color: white;
            padding: 10px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .nav a {
            text-decoration: none;
            color: #2c3e50;
            padding: 10px 15px;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .nav a:hover, .nav a.active {
            background-color: #f5f5f5;
        }
        .nav a.active {
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Nora</h1>
            <p>Autonomous Software Development Agent</p>
        </div>
        
        <div class="nav">
            <a href="/">Home</a>
            <a href="/projects" class="active">Projects</a>
        </div>
        
        <div class="projects-container">
            <h2>Generated Projects</h2>
            
            {% if projects %}
                <div class="project-grid">
                    {% for project in projects %}
                        <div class="project-card">
                            <div class="project-header">
                                <h3 class="project-name">{{ project.name }}</h3>
                            </div>
                            <div class="project-body">
                                <div class="project-description">{{ project.description }}</div>
                                <div class="project-date">Created: {{ project.created_at|timestamp_to_date }}</div>
                                <div class="project-files">{{ project.files|length }} files</div>
                                <a href="/project/{{ project.id }}" class="project-link">View Project</a>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <p>No projects yet. Submit a task to generate a project!</p>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>Powered by Nora - Autonomous Software Development Agent</p>
            <p>&copy; 2025 Nora</p>
        </div>
    </div>
</body>
</html>"""
        
        # Create project.html
        project_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nora - Project Details</title>
    <style>
        /* Same styles as index.html */
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px 0;
            text-align: center;
            border-radius: 8px 8px 0 0;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        .header p {
            margin: 10px 0 0;
            font-size: 1.2rem;
            opacity: 0.8;
        }
        .project-details {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .project-details h2 {
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .project-info {
            margin-bottom: 20px;
        }
        .project-info-item {
            margin-bottom: 10px;
        }
        .project-info-label {
            font-weight: bold;
            color: #2c3e50;
        }
        .project-description {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .project-files {
            margin-top: 20px;
        }
        .file-list {
            list-style-type: none;
            padding: 0;
        }
        .file-item {
            padding: 10px 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        .file-icon {
            margin-right: 10px;
            color: #3498db;
        }
        .file-name {
            flex: 1;
            font-family: monospace;
        }
        .file-actions a {
            text-decoration: none;
            color: #3498db;
            margin-left: 10px;
        }
        .file-actions a:hover {
            text-decoration: underline;
        }
        .back-button {
            display: inline-block;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            padding: 10px 15px;
            border-radius: 4px;
            margin-top: 20px;
            font-weight: bold;
        }
        .back-button:hover {
            background-color: #2980b9;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px 0;
            color: #7f8c8d;
            font-size: 0.9rem;
        }
        .nav {
            display: flex;
            background-color: white;
            padding: 10px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .nav a {
            text-decoration: none;
            color: #2c3e50;
            padding: 10px 15px;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .nav a:hover, .nav a.active {
            background-color: #f5f5f5;
        }
        .nav a.active {
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Nora</h1>
            <p>Autonomous Software Development Agent</p>
        </div>
        
        <div class="nav">
            <a href="/">Home</a>
            <a href="/projects">Projects</a>
        </div>
        
        <div class="project-details">
            <h2>{{ project.name }}</h2>
            
            <div class="project-description">
                {{ project.description }}
            </div>
            
            <div class="project-info">
                <div class="project-info-item">
                    <span class="project-info-label">Project ID:</span> {{ project.id }}
                </div>
                <div class="project-info-item">
                    <span class="project-info-label">Created:</span> {{ project.created_at|timestamp_to_date }}
                </div>
                <div class="project-info-item">
                    <span class="project-info-label">Path:</span> {{ project.path }}
                </div>
            </div>
            
            <div class="project-files">
                <h3>Files</h3>
                <ul class="file-list">
                    {% for file in project.files %}
                        <li class="file-item">
                            <div class="file-icon">📄</div>
                            <div class="file-name">{{ file }}</div>
                            <div class="file-actions">
                                <a href="#" onclick="alert('View file functionality not implemented')">View</a>
                                <a href="#" onclick="alert('Download file functionality not implemented')">Download</a>
                            </div>
                        </li>
                    {% endfor %}
                </ul>
            </div>
            
            <a href="/projects" class="back-button">Back to Projects</a>
        </div>
        
        <div class="footer">
            <p>Powered by Nora - Autonomous Software Development Agent</p>
            <p>&copy; 2025 Nora</p>
        </div>
    </div>
</body>
</html>"""
        
        # Write templates to files
        with open(os.path.join(templates_dir, "index.html"), "w") as f:
            f.write(index_html)
        
        with open(os.path.join(templates_dir, "task.html"), "w") as f:
            f.write(task_html)
        
        with open(os.path.join(templates_dir, "projects.html"), "w") as f:
            f.write(projects_html)
        
        with open(os.path.join(templates_dir, "project.html"), "w") as f:
            f.write(project_html)
        
        logger.info("Created UI templates")
    
    def stop(self):
        """Stop the UI server."""
        self.is_running = False
        logger.info("Nora UI server stopped")