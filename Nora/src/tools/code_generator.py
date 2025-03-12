"""
Code Generator Tool for Nora.
Handles code generation using LLMs.
"""

import logging
import os
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from utils.helpers import generate_unique_id, hash_content
from utils.file_utils import ensure_directory, write_file, read_file
from utils.error_handler import CodeGenerationError

logger = logging.getLogger("nora.tools.code_generator")

class CodeGenerator:
    """
    Code Generator Tool for Nora.
    Responsible for generating code using LLMs.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Code Generator.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
        """
        self.config = config
        self.generated_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                        "data", "generated")
        
        # Create generated directory if it doesn't exist
        ensure_directory(self.generated_dir)
        
        # Initialize OpenAI client if available
        self.openai_client = None
        if self.config["model"]["provider"] == "openai" and self.config["model"]["api_key"]:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=self.config["model"]["api_key"])
                logger.info(f"Initialized OpenAI client with model: {self.config['model']['name']}")
            except ImportError:
                logger.warning("OpenAI package not installed. Please install it with: pip install openai")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {str(e)}")
    
    def generate_code(self, task_description: str, language: str = None, requirements: List[str] = None) -> Dict[str, Any]:
        """
        Generate code based on a task description.
        
        Args:
            task_description (str): Description of the code to generate
            language (str, optional): Programming language to use
            requirements (List[str], optional): List of requirements
            
        Returns:
            Dict[str, Any]: Generated code and metadata
        """
        # Extract requirements if not provided
        if requirements is None:
            requirements = self._extract_requirements(task_description)
        
        # Determine the programming language if not provided
        if language is None:
            language = self._determine_language(task_description, requirements)
        
        logger.info(f"Generating {language} code for: {task_description}")
        
        # Generate the code
        code, explanation = self._generate_code_with_llm(task_description, language, requirements)
        
        # Create a project structure
        project_id = generate_unique_id()
        project_dir = os.path.join(self.generated_dir, f"project_{project_id}")
        ensure_directory(project_dir)
        
        # Save the code to files
        files = self._save_code_to_files(code, project_dir, language)
        
        # Create a README
        readme_content = self._generate_readme(task_description, language, requirements, explanation)
        readme_path = os.path.join(project_dir, "README.md")
        write_file(readme_path, readme_content)
        
        return {
            "project_id": project_id,
            "project_dir": project_dir,
            "language": language,
            "requirements": requirements,
            "files": files,
            "explanation": explanation,
            "timestamp": time.time()
        }
    
    def _extract_requirements(self, task_description: str) -> List[str]:
        """
        Extract requirements from a task description.
        
        Args:
            task_description (str): Task description
            
        Returns:
            List[str]: List of requirements
        """
        # Use LLM to extract requirements if available
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config["model"]["name"],
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that extracts technical requirements from task descriptions. Extract only the technical requirements, frameworks, and libraries mentioned."},
                        {"role": "user", "content": f"Extract the technical requirements from this task description: {task_description}"}
                    ],
                    max_tokens=200
                )
                requirements_text = response.choices[0].message.content.strip()
                # Parse the requirements from the response
                requirements = [req.strip() for req in requirements_text.split('\n') if req.strip()]
                return requirements
            except Exception as e:
                logger.warning(f"Error extracting requirements with LLM: {str(e)}")
        
        # Fallback to simple extraction
        requirements = []
        
        # Look for common requirement indicators
        if "using" in task_description.lower():
            using_parts = task_description.lower().split("using")[1].split()
            requirements.extend(using_parts[:3])  # Take the first few words after "using"
        
        if "with" in task_description.lower():
            with_parts = task_description.lower().split("with")[1].split()
            requirements.extend(with_parts[:3])  # Take the first few words after "with"
        
        # Clean up requirements
        clean_requirements = []
        for req in requirements:
            req = req.strip().strip(',.;:()[]{}')
            if req and len(req) > 2:  # Ignore very short words
                clean_requirements.append(req)
        
        return clean_requirements
    
    def _determine_language(self, task_description: str, requirements: List[str]) -> str:
        """
        Determine the programming language to use.
        
        Args:
            task_description (str): Task description
            requirements (List[str]): List of requirements
            
        Returns:
            str: Programming language
        """
        # Use LLM to determine language if available
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config["model"]["name"],
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that determines the most appropriate programming language for a task. Respond with just the language name."},
                        {"role": "user", "content": f"What programming language would be most appropriate for this task? Task: {task_description}\nRequirements: {', '.join(requirements)}"}
                    ],
                    max_tokens=50
                )
                language = response.choices[0].message.content.strip().lower()
                # Clean up the language name
                for lang in ["python", "javascript", "typescript", "java", "c#", "php", "ruby", "go", "rust", "swift", "kotlin", "html"]:
                    if lang in language:
                        return lang
            except Exception as e:
                logger.warning(f"Error determining language with LLM: {str(e)}")
        
        # Fallback to keyword matching
        task_lower = task_description.lower()
        
        language_keywords = {
            "python": ["python", "django", "flask", "pytorch", "tensorflow", "pandas", "numpy"],
            "javascript": ["javascript", "js", "node", "react", "vue", "angular", "express"],
            "typescript": ["typescript", "ts", "angular", "next.js"],
            "java": ["java", "spring", "android"],
            "c#": ["c#", "csharp", ".net", "dotnet", "asp.net"],
            "php": ["php", "laravel", "symfony"],
            "ruby": ["ruby", "rails"],
            "go": ["go", "golang"],
            "rust": ["rust", "cargo"],
            "swift": ["swift", "ios"],
            "kotlin": ["kotlin", "android"],
            "html": ["html", "css", "web page", "webpage"],
        }
        
        # Check task description for language keywords
        for lang, keywords in language_keywords.items():
            for keyword in keywords:
                if keyword in task_lower:
                    return lang
        
        # Check requirements for language keywords
        for req in requirements:
            req_lower = req.lower()
            for lang, keywords in language_keywords.items():
                for keyword in keywords:
                    if keyword in req_lower:
                        return lang
        
        # Default to Python if no language is specified
        return "python"
    
    def _generate_code_with_llm(self, task_description: str, language: str, requirements: List[str]) -> Tuple[str, str]:
        """
        Generate code using a language model.
        
        Args:
            task_description (str): Task description
            language (str): Programming language
            requirements (List[str]): List of requirements
            
        Returns:
            Tuple[str, str]: Generated code and explanation
        """
        # Use OpenAI to generate code if available
        if self.openai_client:
            try:
                # Prepare the prompt
                requirements_str = ", ".join(requirements) if requirements else "No specific requirements"
                prompt = f"Task: {task_description}\nLanguage: {language}\nRequirements: {requirements_str}\n\nGenerate complete, working code for this task."
                
                # Generate code
                response = self.openai_client.chat.completions.create(
                    model=self.config["model"]["name"],
                    messages=[
                        {"role": "system", "content": "You are an expert software developer. Generate complete, working code for the given task. Include all necessary imports, functions, and comments."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000
                )
                code = response.choices[0].message.content.strip()
                
                # Generate explanation
                explanation_response = self.openai_client.chat.completions.create(
                    model=self.config["model"]["name"],
                    messages=[
                        {"role": "system", "content": "You are an expert software developer. Explain the code you've generated in a clear, concise manner."},
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": code},
                        {"role": "user", "content": "Explain this code in a clear, concise manner."}
                    ],
                    max_tokens=500
                )
                explanation = explanation_response.choices[0].message.content.strip()
                
                return code, explanation
            except Exception as e:
                logger.warning(f"Error generating code with LLM: {str(e)}")
        
        # Fallback to template-based generation
        if language == "python":
            code = self._generate_python_example(task_description, requirements)
        elif language in ["javascript", "typescript"]:
            code = self._generate_javascript_example(task_description, requirements)
        elif language == "html":
            code = self._generate_html_example(task_description, requirements)
        else:
            # Generic code template
            code = f"// {language.capitalize()} code for: {task_description}\n\n"
            code += f"// TODO: Implement {language} solution\n"
        
        explanation = f"This code implements a solution for: {task_description}\n\n"
        explanation += f"It uses {language} as the programming language.\n"
        if requirements:
            explanation += f"Requirements: {', '.join(requirements)}\n"
        
        return code, explanation
    
    def _generate_python_example(self, task_description: str, requirements: List[str]) -> str:
        """
        Generate a Python example.
        
        Args:
            task_description (str): Task description
            requirements (List[str]): List of requirements
            
        Returns:
            str: Generated Python code
        """
        code = f"#!/usr/bin/env python3\n"
        code += f"# {task_description}\n\n"
        
        # Add imports
        code += "import os\n"
        code += "import sys\n"
        code += "import json\n"
        
        if "web" in task_description.lower() or "api" in task_description.lower():
            code += "import requests\n"
            
        if "flask" in [r.lower() for r in requirements] or "web" in task_description.lower():
            code += "from flask import Flask, request, jsonify, render_template\n\n"
            code += "app = Flask(__name__)\n\n"
            
            code += "@app.route('/')\n"
            code += "def home():\n"
            code += "    return render_template('index.html')\n\n"
            
            code += "@app.route('/api/data')\n"
            code += "def get_data():\n"
            code += "    data = {'message': 'This is sample data'}\n"
            code += "    return jsonify(data)\n\n"
            
            code += "if __name__ == '__main__':\n"
            code += "    app.run(debug=True, host='0.0.0.0')\n"
        else:
            code += "\n"
            code += "def main():\n"
            code += f"    print('Executing task: {task_description}')\n"
            code += "    # TODO: Implement the solution\n"
            code += "    print('Task completed')\n\n"
            
            code += "if __name__ == '__main__':\n"
            code += "    main()\n"
        
        return code
    
    def _generate_javascript_example(self, task_description: str, requirements: List[str]) -> str:
        """
        Generate a JavaScript example.
        
        Args:
            task_description (str): Task description
            requirements (List[str]): List of requirements
            
        Returns:
            str: Generated JavaScript code
        """
        code = f"// {task_description}\n\n"
        
        if "node" in [r.lower() for r in requirements] or "express" in [r.lower() for r in requirements]:
            code += "const express = require('express');\n"
            code += "const app = express();\n"
            code += "const port = process.env.PORT || 3000;\n\n"
            
            code += "app.use(express.json());\n\n"
            
            code += "app.get('/', (req, res) => {\n"
            code += "    res.send('Hello, World!');\n"
            code += "});\n\n"
            
            code += "app.get('/api/data', (req, res) => {\n"
            code += "    const data = { message: 'This is sample data' };\n"
            code += "    res.json(data);\n"
            code += "});\n\n"
            
            code += "app.listen(port, () => {\n"
            code += f"    console.log(`Server running on port ${{port}}`);\n"
            code += "});\n"
        elif "react" in [r.lower() for r in requirements]:
            code += "import React, { useState, useEffect } from 'react';\n\n"
            
            code += "function App() {\n"
            code += "    const [data, setData] = useState(null);\n\n"
            
            code += "    useEffect(() => {\n"
            code += "        // Fetch data when component mounts\n"
            code += "        fetch('/api/data')\n"
            code += "            .then(response => response.json())\n"
            code += "            .then(data => setData(data))\n"
            code += "            .catch(error => console.error('Error fetching data:', error));\n"
            code += "    }, []);\n\n"
            
            code += "    return (\n"
            code += "        <div className=\"App\">\n"
            code += "            <header className=\"App-header\">\n"
            code += f"                <h1>{task_description}</h1>\n"
            code += "                {data ? (\n"
            code += "                    <p>{data.message}</p>\n"
            code += "                ) : (\n"
            code += "                    <p>Loading data...</p>\n"
            code += "                )}\n"
            code += "            </header>\n"
            code += "        </div>\n"
            code += "    );\n"
            code += "}\n\n"
            
            code += "export default App;\n"
        else:
            code += "function main() {\n"
            code += f"    console.log('Executing task: {task_description}');\n"
            code += "    // TODO: Implement the solution\n"
            code += "    console.log('Task completed');\n"
            code += "}\n\n"
            
            code += "main();\n"
        
        return code
    
    def _generate_html_example(self, task_description: str, requirements: List[str]) -> str:
        """
        Generate an HTML example.
        
        Args:
            task_description (str): Task description
            requirements (List[str]): List of requirements
            
        Returns:
            str: Generated HTML code
        """
        code = "<!DOCTYPE html>\n"
        code += "<html lang=\"en\">\n"
        code += "<head>\n"
        code += "    <meta charset=\"UTF-8\">\n"
        code += "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        code += f"    <title>{task_description}</title>\n"
        code += "    <style>\n"
        code += "        body {\n"
        code += "            font-family: Arial, sans-serif;\n"
        code += "            line-height: 1.6;\n"
        code += "            margin: 0;\n"
        code += "            padding: 20px;\n"
        code += "            max-width: 800px;\n"
        code += "            margin: 0 auto;\n"
        code += "        }\n"
        code += "        header {\n"
        code += "            background-color: #f4f4f4;\n"
        code += "            padding: 20px;\n"
        code += "            text-align: center;\n"
        code += "        }\n"
        code += "        .container {\n"
        code += "            padding: 20px;\n"
        code += "        }\n"
        code += "    </style>\n"
        code += "</head>\n"
        code += "<body>\n"
        code += "    <header>\n"
        code += f"        <h1>{task_description}</h1>\n"
        code += "    </header>\n"
        code += "    <div class=\"container\">\n"
        code += "        <p>This is a sample web page.</p>\n"
        code += "        <div id=\"content\">\n"
        code += "            <!-- Content will be loaded here -->\n"
        code += "            <p>Loading content...</p>\n"
        code += "        </div>\n"
        code += "    </div>\n"
        code += "    <script>\n"
        code += "        // Sample JavaScript\n"
        code += "        document.addEventListener('DOMContentLoaded', function() {\n"
        code += "            const contentElement = document.getElementById('content');\n"
        code += "            contentElement.innerHTML = '<p>Content loaded successfully!</p>';\n"
        code += "        });\n"
        code += "    </script>\n"
        code += "</body>\n"
        code += "</html>\n"
        
        return code
    
    def _save_code_to_files(self, code: str, project_dir: str, language: str) -> List[Dict[str, str]]:
        """
        Save generated code to files.
        
        Args:
            code (str): Generated code
            project_dir (str): Project directory
            language (str): Programming language
            
        Returns:
            List[Dict[str, str]]: List of saved files with metadata
        """
        files = []
        
        # Extract code blocks if the code contains markdown-style code blocks
        if "```" in code:
            code_blocks = self._extract_code_blocks(code)
            if code_blocks:
                for i, block in enumerate(code_blocks):
                    lang, filename, content = block
                    
                    # If no filename is provided, generate one
                    if not filename:
                        if i == 0:
                            filename = self._get_default_filename(language)
                        else:
                            filename = f"file_{i}.{self._get_file_extension(lang or language)}"
                    
                    # Save the file
                    file_path = os.path.join(project_dir, filename)
                    write_file(file_path, content)
                    
                    files.append({
                        "name": filename,
                        "path": file_path,
                        "language": lang or language
                    })
                
                return files
        
        # If no code blocks found, save the entire code as a single file
        main_file = self._get_default_filename(language)
        main_file_path = os.path.join(project_dir, main_file)
        write_file(main_file_path, code)
        
        files.append({
            "name": main_file,
            "path": main_file_path,
            "language": language
        })
        
        return files
    
    def _extract_code_blocks(self, code: str) -> List[Tuple[str, str, str]]:
        """
        Extract code blocks from markdown-style code.
        
        Args:
            code (str): Code with markdown-style code blocks
            
        Returns:
            List[Tuple[str, str, str]]: List of (language, filename, content) tuples
        """
        import re
        
        # Pattern to match code blocks with optional language and filename
        # Format: ```language:filename
        pattern = r"```([\w\+\#\-\.]*):?([^\n]*)\n(.*?)```"
        matches = re.findall(pattern, code, re.DOTALL)
        
        result = []
        for lang, filename, content in matches:
            # Clean up the content
            content = content.strip()
            result.append((lang.strip(), filename.strip(), content))
        
        return result
    
    def _get_default_filename(self, language: str) -> str:
        """
        Get the default filename for a language.
        
        Args:
            language (str): Programming language
            
        Returns:
            str: Default filename
        """
        language_files = {
            "python": "main.py",
            "javascript": "index.js",
            "typescript": "index.ts",
            "java": "Main.java",
            "c#": "Program.cs",
            "php": "index.php",
            "ruby": "main.rb",
            "go": "main.go",
            "rust": "main.rs",
            "swift": "main.swift",
            "kotlin": "Main.kt",
            "html": "index.html",
        }
        
        return language_files.get(language, f"main.{self._get_file_extension(language)}")
    
    def _get_file_extension(self, language: str) -> str:
        """
        Get the file extension for a language.
        
        Args:
            language (str): Programming language
            
        Returns:
            str: File extension
        """
        language_extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "c#": "cs",
            "php": "php",
            "ruby": "rb",
            "go": "go",
            "rust": "rs",
            "swift": "swift",
            "kotlin": "kt",
            "html": "html",
            "css": "css",
            "markdown": "md",
            "json": "json",
            "yaml": "yml",
            "dockerfile": "Dockerfile",
        }
        
        return language_extensions.get(language.lower(), "txt")
    
    def _generate_readme(self, task_description: str, language: str, requirements: List[str], explanation: str) -> str:
        """
        Generate a README file for the project.
        
        Args:
            task_description (str): Task description
            language (str): Programming language
            requirements (List[str]): List of requirements
            explanation (str): Code explanation
            
        Returns:
            str: README content
        """
        readme = f"# {task_description}\n\n"
        
        readme += "## Description\n\n"
        readme += f"{explanation}\n\n"
        
        readme += "## Requirements\n\n"
        if requirements:
            for req in requirements:
                readme += f"- {req}\n"
        else:
            readme += "No specific requirements.\n"
        
        readme += "\n## Setup\n\n"
        
        if language == "python":
            readme += "```bash\n"
            readme += "# Install dependencies\n"
            readme += "pip install -r requirements.txt\n\n"
            readme += "# Run the application\n"
            readme += "python main.py\n"
            readme += "```\n"
        elif language == "javascript":
            readme += "```bash\n"
            readme += "# Install dependencies\n"
            readme += "npm install\n\n"
            readme += "# Run the application\n"
            readme += "node index.js\n"
            readme += "```\n"
        elif language == "html":
            readme += "Open `index.html` in your web browser.\n"
        else:
            readme += f"Instructions for setting up and running {language} projects.\n"
        
        readme += "\n## License\n\n"
        readme += "MIT\n"
        
        return readme