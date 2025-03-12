"""
Deployment Agent for Nora.
Handles deployment to cloud platforms, domain management, and monetization.
"""

import logging
import os
import json
import time
from typing import Dict, Any, List, Optional
from utils.helpers import generate_unique_id, hash_content
from utils.error_handler import CloudDeploymentError, DomainError, MonetizationError

logger = logging.getLogger("nora.agents.deployment_agent")

class DeploymentAgent:
    """
    Deployment Agent for Nora.
    Responsible for deploying applications to cloud platforms, managing domains, and setting up monetization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Deployment Agent.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
        """
        self.config = config
        self.deployments_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                          "data", "deployments")
        
        # Create deployments directory if it doesn't exist
        os.makedirs(self.deployments_dir, exist_ok=True)
    
    def execute(self, task_description: str) -> Dict[str, Any]:
        """
        Execute a deployment-related task.
        
        Args:
            task_description (str): Description of the task to execute
            
        Returns:
            Dict[str, Any]: Task result
        """
        logger.info(f"Deployment Agent executing task: {task_description}")
        
        try:
            # Determine what kind of deployment task this is
            if "deploy" in task_description.lower():
                result = self._deploy_application(task_description)
            elif "domain" in task_description.lower():
                result = self._manage_domain(task_description)
            elif "monetize" in task_description.lower() or "monetization" in task_description.lower():
                result = self._setup_monetization(task_description)
            elif "ads" in task_description.lower() or "advertising" in task_description.lower():
                result = self._setup_advertising(task_description)
            else:
                # Default to deployment
                result = self._deploy_application(task_description)
            
            return {
                "status": "success",
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Error in Deployment Agent: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _deploy_application(self, task_description: str) -> Dict[str, Any]:
        """
        Deploy an application to a cloud platform.
        
        Args:
            task_description (str): Description of the deployment task
            
        Returns:
            Dict[str, Any]: Deployment results
        """
        # Extract project ID from task description
        import re
        project_id_match = re.search(r'project_([a-f0-9-]+)', task_description)
        
        if not project_id_match:
            raise CloudDeploymentError("No project ID found in task description")
        
        project_id = f"project_{project_id_match.group(1)}"
        project_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                  "data", "generated", project_id)
        
        if not os.path.exists(project_dir):
            raise CloudDeploymentError(f"Project directory not found: {project_dir}")
        
        # Determine the cloud platform to use
        platform = self._determine_platform(task_description)
        
        logger.info(f"Deploying project {project_id} to {platform}")
        
        # Deploy to the selected platform
        if platform == "aws":
            deployment = self._deploy_to_aws(project_dir, project_id)
        elif platform == "gcp":
            deployment = self._deploy_to_gcp(project_dir, project_id)
        else:
            # Default to a mock deployment
            deployment = self._mock_deployment(project_dir, project_id, platform)
        
        # Save deployment information
        deployment_file = os.path.join(self.deployments_dir, f"{project_id}_deployment.json")
        try:
            with open(deployment_file, 'w') as f:
                json.dump(deployment, f, indent=2)
        except Exception as e:
            logger.warning(f"Error saving deployment information: {str(e)}")
        
        return deployment
    
    def _determine_platform(self, task_description: str) -> str:
        """
        Determine which cloud platform to use for deployment.
        
        Args:
            task_description (str): Task description
            
        Returns:
            str: Cloud platform name
        """
        task_lower = task_description.lower()
        
        # Check for explicit platform mentions
        if "aws" in task_lower or "amazon" in task_lower:
            return "aws"
        elif "gcp" in task_lower or "google cloud" in task_lower:
            return "gcp"
        elif "azure" in task_lower or "microsoft" in task_lower:
            return "azure"
        elif "heroku" in task_lower:
            return "heroku"
        elif "netlify" in task_lower:
            return "netlify"
        elif "vercel" in task_lower:
            return "vercel"
        
        # Check if AWS credentials are configured
        if self.config["cloud"]["aws"]["access_key"] and self.config["cloud"]["aws"]["secret_key"]:
            return "aws"
        
        # Check if GCP credentials are configured
        if self.config["cloud"]["gcp"]["project_id"] and self.config["cloud"]["gcp"]["credentials_file"]:
            return "gcp"
        
        # Default to AWS
        return "aws"
    
    def _deploy_to_aws(self, project_dir: str, project_id: str) -> Dict[str, Any]:
        """
        Deploy a project to AWS.
        
        Args:
            project_dir (str): Project directory
            project_id (str): Project ID
            
        Returns:
            Dict[str, Any]: Deployment information
        """
        # This is a placeholder for AWS deployment
        # In a real implementation, this would use the AWS SDK
        
        logger.warning("AWS deployment not fully implemented, using mock deployment")
        return self._mock_deployment(project_dir, project_id, "aws")
    
    def _deploy_to_gcp(self, project_dir: str, project_id: str) -> Dict[str, Any]:
        """
        Deploy a project to Google Cloud Platform.
        
        Args:
            project_dir (str): Project directory
            project_id (str): Project ID
            
        Returns:
            Dict[str, Any]: Deployment information
        """
        # This is a placeholder for GCP deployment
        # In a real implementation, this would use the Google Cloud SDK
        
        logger.warning("GCP deployment not fully implemented, using mock deployment")
        return self._mock_deployment(project_dir, project_id, "gcp")
    
    def _mock_deployment(self, project_dir: str, project_id: str, platform: str) -> Dict[str, Any]:
        """
        Create a mock deployment for demonstration purposes.
        
        Args:
            project_dir (str): Project directory
            project_id (str): Project ID
            platform (str): Cloud platform
            
        Returns:
            Dict[str, Any]: Mock deployment information
        """
        deployment_id = generate_unique_id()
        
        # Determine the application type
        app_type = self._determine_app_type(project_dir)
        
        # Generate a mock URL
        if platform == "aws":
            url = f"https://{deployment_id}.execute-api.us-east-1.amazonaws.com/prod"
        elif platform == "gcp":
            url = f"https://{project_id.replace('_', '-')}.appspot.com"
        elif platform == "netlify":
            url = f"https://{project_id.replace('_', '-')}.netlify.app"
        elif platform == "vercel":
            url = f"https://{project_id.replace('_', '-')}.vercel.app"
        else:
            url = f"https://example.com/{project_id}"
        
        return {
            "deployment_id": deployment_id,
            "project_id": project_id,
            "platform": platform,
            "url": url,
            "app_type": app_type,
            "status": "deployed",
            "created_at": time.time(),
            "resources": {
                "compute": "serverless" if platform in ["aws", "netlify", "vercel"] else "vm",
                "storage": "s3" if platform == "aws" else "cloud-storage",
                "database": None
            },
            "environment": "production",
            "region": "us-east-1" if platform == "aws" else "us-central1",
            "is_mock": True
        }
    
    def _determine_app_type(self, project_dir: str) -> str:
        """
        Determine the type of application in the project.
        
        Args:
            project_dir (str): Project directory
            
        Returns:
            str: Application type
        """
        # Check for common file patterns
        if os.path.exists(os.path.join(project_dir, "index.html")):
            return "static-website"
        elif os.path.exists(os.path.join(project_dir, "app.py")) or os.path.exists(os.path.join(project_dir, "main.py")):
            if os.path.exists(os.path.join(project_dir, "requirements.txt")):
                with open(os.path.join(project_dir, "requirements.txt"), 'r') as f:
                    requirements = f.read()
                    if "flask" in requirements.lower() or "django" in requirements.lower():
                        return "web-application"
            return "python-application"
        elif os.path.exists(os.path.join(project_dir, "package.json")):
            with open(os.path.join(project_dir, "package.json"), 'r') as f:
                try:
                    package_json = json.load(f)
                    dependencies = package_json.get("dependencies", {})
                    if "react" in dependencies:
                        return "react-application"
                    elif "express" in dependencies:
                        return "node-api"
                    elif "next" in dependencies:
                        return "nextjs-application"
                except json.JSONDecodeError:
                    pass
            return "node-application"
        else:
            return "unknown"
    
    def _manage_domain(self, task_description: str) -> Dict[str, Any]:
        """
        Manage a domain for a deployed application.
        
        Args:
            task_description (str): Description of the domain management task
            
        Returns:
            Dict[str, Any]: Domain management results
        """
        # Extract deployment ID or project ID from task description
        import re
        deployment_id_match = re.search(r'deployment_([a-f0-9-]+)', task_description)
        project_id_match = re.search(r'project_([a-f0-9-]+)', task_description)
        
        if deployment_id_match:
            deployment_id = f"deployment_{deployment_id_match.group(1)}"
            # Find the deployment file
            deployment_file = None
            for filename in os.listdir(self.deployments_dir):
                if deployment_id in filename:
                    deployment_file = os.path.join(self.deployments_dir, filename)
                    break
            
            if not deployment_file:
                raise DomainError(f"Deployment file not found for deployment ID: {deployment_id}")
            
            with open(deployment_file, 'r') as f:
                deployment = json.load(f)
            
            project_id = deployment["project_id"]
            
        elif project_id_match:
            project_id = f"project_{project_id_match.group(1)}"
            # Find the deployment file
            deployment_file = os.path.join(self.deployments_dir, f"{project_id}_deployment.json")
            
            if not os.path.exists(deployment_file):
                raise DomainError(f"Deployment file not found for project ID: {project_id}")
            
            with open(deployment_file, 'r') as f:
                deployment = json.load(f)
            
        else:
            raise DomainError("No deployment ID or project ID found in task description")
        
        # Extract domain name from task description
        domain_match = re.search(r'domain[:\s]+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', task_description)
        
        if not domain_match:
            # Generate a domain name based on the project ID
            domain = f"{project_id.replace('_', '-')}.example.com"
        else:
            domain = domain_match.group(1)
        
        logger.info(f"Managing domain {domain} for project {project_id}")
        
        # Determine the domain registrar to use
        registrar = self._determine_registrar(task_description)
        
        # Register or configure the domain
        if registrar == "namecheap":
            domain_info = self._manage_domain_namecheap(domain, deployment)
        elif registrar == "route53":
            domain_info = self._manage_domain_route53(domain, deployment)
        else:
            # Default to a mock domain registration
            domain_info = self._mock_domain_registration(domain, deployment, registrar)
        
        # Update the deployment information with the domain
        deployment["domain"] = domain_info
        
        # Save updated deployment information
        try:
            with open(deployment_file, 'w') as f:
                json.dump(deployment, f, indent=2)
        except Exception as e:
            logger.warning(f"Error saving updated deployment information: {str(e)}")
        
        return domain_info
    
    def _determine_registrar(self, task_description: str) -> str:
        """
        Determine which domain registrar to use.
        
        Args:
            task_description (str): Task description
            
        Returns:
            str: Domain registrar name
        """
        task_lower = task_description.lower()
        
        # Check for explicit registrar mentions
        if "namecheap" in task_lower:
            return "namecheap"
        elif "route53" in task_lower or "aws" in task_lower:
            return "route53"
        elif "godaddy" in task_lower:
            return "godaddy"
        
        # Check if Namecheap credentials are configured
        if (self.config["domains"]["namecheap"]["api_key"] and 
            self.config["domains"]["namecheap"]["username"]):
            return "namecheap"
        
        # Check if AWS credentials are configured (for Route 53)
        if (self.config["cloud"]["aws"]["access_key"] and 
            self.config["cloud"]["aws"]["secret_key"]):
            return "route53"
        
        # Default to Namecheap
        return "namecheap"
    
    def _manage_domain_namecheap(self, domain: str, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register or configure a domain with Namecheap.
        
        Args:
            domain (str): Domain name
            deployment (Dict[str, Any]): Deployment information
            
        Returns:
            Dict[str, Any]: Domain information
        """
        # This is a placeholder for Namecheap domain management
        # In a real implementation, this would use the Namecheap API
        
        logger.warning("Namecheap domain management not implemented, using mock registration")
        return self._mock_domain_registration(domain, deployment, "namecheap")
    
    def _manage_domain_route53(self, domain: str, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register or configure a domain with AWS Route 53.
        
        Args:
            domain (str): Domain name
            deployment (Dict[str, Any]): Deployment information
            
        Returns:
            Dict[str, Any]: Domain information
        """
        # This is a placeholder for Route 53 domain management
        # In a real implementation, this would use the AWS SDK
        
        logger.warning("Route 53 domain management not implemented, using mock registration")
        return self._mock_domain_registration(domain, deployment, "route53")
    
    def _mock_domain_registration(self, domain: str, deployment: Dict[str, Any], registrar: str) -> Dict[str, Any]:
        """
        Create a mock domain registration for demonstration purposes.
        
        Args:
            domain (str): Domain name
            deployment (Dict[str, Any]): Deployment information
            registrar (str): Domain registrar
            
        Returns:
            Dict[str, Any]: Mock domain information
        """
        return {
            "domain": domain,
            "registrar": registrar,
            "status": "registered",
            "expiration_date": time.time() + 31536000,  # One year from now
            "nameservers": [
                f"ns1.{registrar}.com",
                f"ns2.{registrar}.com"
            ],
            "dns_records": [
                {
                    "type": "A",
                    "name": "@",
                    "value": "192.0.2.1",  # Example IP
                    "ttl": 3600
                },
                {
                    "type": "CNAME",
                    "name": "www",
                    "value": "@",
                    "ttl": 3600
                }
            ],
            "is_mock": True
        }
    
    def _setup_monetization(self, task_description: str) -> Dict[str, Any]:
        """
        Set up monetization for a deployed application.
        
        Args:
            task_description (str): Description of the monetization task
            
        Returns:
            Dict[str, Any]: Monetization results
        """
        # Extract deployment ID or project ID from task description
        import re
        deployment_id_match = re.search(r'deployment_([a-f0-9-]+)', task_description)
        project_id_match = re.search(r'project_([a-f0-9-]+)', task_description)
        
        if deployment_id_match:
            deployment_id = f"deployment_{deployment_id_match.group(1)}"
            # Find the deployment file
            deployment_file = None
            for filename in os.listdir(self.deployments_dir):
                if deployment_id in filename:
                    deployment_file = os.path.join(self.deployments_dir, filename)
                    break
            
            if not deployment_file:
                raise MonetizationError(f"Deployment file not found for deployment ID: {deployment_id}")
            
            with open(deployment_file, 'r') as f:
                deployment = json.load(f)
            
            project_id = deployment["project_id"]
            
        elif project_id_match:
            project_id = f"project_{project_id_match.group(1)}"
            # Find the deployment file
            deployment_file = os.path.join(self.deployments_dir, f"{project_id}_deployment.json")
            
            if not os.path.exists(deployment_file):
                raise MonetizationError(f"Deployment file not found for project ID: {project_id}")
            
            with open(deployment_file, 'r') as f:
                deployment = json.load(f)
            
        else:
            raise MonetizationError("No deployment ID or project ID found in task description")
        
        # Determine the monetization method
        method = self._determine_monetization_method(task_description)
        
        logger.info(f"Setting up {method} monetization for project {project_id}")
        
        # Set up the monetization
        if method == "subscription":
            monetization = self._setup_subscription(deployment)
        elif method == "adsense":
            monetization = self._setup_adsense(deployment)
        else:
            # Default to a mock monetization setup
            monetization = self._mock_monetization(deployment, method)
        
        # Update the deployment information with the monetization
        deployment["monetization"] = monetization
        
        # Save updated deployment information
        try:
            with open(deployment_file, 'w') as f:
                json.dump(deployment, f, indent=2)
        except Exception as e:
            logger.warning(f"Error saving updated deployment information: {str(e)}")
        
        return monetization
    
    def _determine_monetization_method(self, task_description: str) -> str:
        """
        Determine which monetization method to use.
        
        Args:
            task_description (str): Task description
            
        Returns:
            str: Monetization method
        """
        task_lower = task_description.lower()
        
        # Check for explicit method mentions
        if "subscription" in task_lower or "stripe" in task_lower:
            return "subscription"
        elif "adsense" in task_lower or "ads" in task_lower or "advertising" in task_lower:
            return "adsense"
        elif "donation" in task_lower or "donate" in task_lower:
            return "donation"
        elif "affiliate" in task_lower:
            return "affiliate"
        
        # Default to subscription
        return "subscription"
    
    def _setup_subscription(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set up subscription monetization with Stripe.
        
        Args:
            deployment (Dict[str, Any]): Deployment information
            
        Returns:
            Dict[str, Any]: Subscription information
        """
        # This is a placeholder for Stripe subscription setup
        # In a real implementation, this would use the Stripe API
        
        logger.warning("Stripe subscription setup not implemented, using mock setup")
        return self._mock_monetization(deployment, "subscription")
    
    def _setup_adsense(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set up Google AdSense monetization.
        
        Args:
            deployment (Dict[str, Any]): Deployment information
            
        Returns:
            Dict[str, Any]: AdSense information
        """
        # This is a placeholder for Google AdSense setup
        # In a real implementation, this would use the Google AdSense API
        
        logger.warning("Google AdSense setup not implemented, using mock setup")
        return self._mock_monetization(deployment, "adsense")
    
    def _mock_monetization(self, deployment: Dict[str, Any], method: str) -> Dict[str, Any]:
        """
        Create a mock monetization setup for demonstration purposes.
        
        Args:
            deployment (Dict[str, Any]): Deployment information
            method (str): Monetization method
            
        Returns:
            Dict[str, Any]: Mock monetization information
        """
        if method == "subscription":
            return {
                "method": "subscription",
                "provider": "stripe",
                "status": "active",
                "plans": [
                    {
                        "id": "basic",
                        "name": "Basic Plan",
                        "price": 9.99,
                        "currency": "USD",
                        "interval": "month",
                        "features": ["Basic features"]
                    },
                    {
                        "id": "premium",
                        "name": "Premium Plan",
                        "price": 19.99,
                        "currency": "USD",
                        "interval": "month",
                        "features": ["Premium features", "Priority support"]
                    }
                ],
                "integration_code": "<script src=\"https://js.stripe.com/v3/\"></script>",
                "is_mock": True
            }
        elif method == "adsense":
            return {
                "method": "adsense",
                "provider": "google",
                "status": "active",
                "ad_units": [
                    {
                        "id": "header",
                        "name": "Header Ad",
                        "size": "728x90",
                        "position": "header"
                    },
                    {
                        "id": "sidebar",
                        "name": "Sidebar Ad",
                        "size": "300x250",
                        "position": "sidebar"
                    }
                ],
                "integration_code": "<script async src=\"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js\"></script>",
                "is_mock": True
            }
        elif method == "donation":
            return {
                "method": "donation",
                "provider": "paypal",
                "status": "active",
                "donation_options": [
                    {
                        "amount": 5,
                        "currency": "USD",
                        "description": "Small donation"
                    },
                    {
                        "amount": 10,
                        "currency": "USD",
                        "description": "Medium donation"
                    },
                    {
                        "amount": 25,
                        "currency": "USD",
                        "description": "Large donation"
                    }
                ],
                "integration_code": "<form action=\"https://www.paypal.com/donate\" method=\"post\"></form>",
                "is_mock": True
            }
        else:
            return {
                "method": method,
                "status": "active",
                "is_mock": True
            }
    
    def _setup_advertising(self, task_description: str) -> Dict[str, Any]:
        """
        Set up advertising for a deployed application.
        
        Args:
            task_description (str): Description of the advertising task
            
        Returns:
            Dict[str, Any]: Advertising results
        """
        # Extract deployment ID or project ID from task description
        import re
        deployment_id_match = re.search(r'deployment_([a-f0-9-]+)', task_description)
        project_id_match = re.search(r'project_([a-f0-9-]+)', task_description)
        
        if deployment_id_match:
            deployment_id = f"deployment_{deployment_id_match.group(1)}"
            # Find the deployment file
            deployment_file = None
            for filename in os.listdir(self.deployments_dir):
                if deployment_id in filename:
                    deployment_file = os.path.join(self.deployments_dir, filename)
                    break
            
            if not deployment_file:
                raise MonetizationError(f"Deployment file not found for deployment ID: {deployment_id}")
            
            with open(deployment_file, 'r') as f:
                deployment = json.load(f)
            
            project_id = deployment["project_id"]
            
        elif project_id_match:
            project_id = f"project_{project_id_match.group(1)}"
            # Find the deployment file
            deployment_file = os.path.join(self.deployments_dir, f"{project_id}_deployment.json")
            
            if not os.path.exists(deployment_file):
                raise MonetizationError(f"Deployment file not found for project ID: {project_id}")
            
            with open(deployment_file, 'r') as f:
                deployment = json.load(f)
            
        else:
            raise MonetizationError("No deployment ID or project ID found in task description")
        
        # Determine the advertising platform
        platform = self._determine_ad_platform(task_description)
        
        logger.info(f"Setting up {platform} advertising for project {project_id}")
        
        # Set up the advertising
        if platform == "google_ads":
            advertising = self._setup_google_ads(deployment)
        elif platform == "facebook":
            advertising = self._setup_facebook_ads(deployment)
        else:
            # Default to a mock advertising setup
            advertising = self._mock_advertising(deployment, platform)
        
        # Update the deployment information with the advertising
        deployment["advertising"] = advertising
        
        # Save updated deployment information
        try:
            with open(deployment_file, 'w') as f:
                json.dump(deployment, f, indent=2)
        except Exception as e:
            logger.warning(f"Error saving updated deployment information: {str(e)}")
        
        return advertising
    
    def _determine_ad_platform(self, task_description: str) -> str:
        """
        Determine which advertising platform to use.
        
        Args:
            task_description (str): Task description
            
        Returns:
            str: Advertising platform
        """
        task_lower = task_description.lower()
        
        # Check for explicit platform mentions
        if "google ads" in task_lower or "google ad" in task_lower:
            return "google_ads"
        elif "facebook" in task_lower:
            return "facebook"
        elif "twitter" in task_lower:
            return "twitter"
        elif "linkedin" in task_lower:
            return "linkedin"
        
        # Default to Google Ads
        return "google_ads"
    
    def _setup_google_ads(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set up Google Ads advertising.
        
        Args:
            deployment (Dict[str, Any]): Deployment information
            
        Returns:
            Dict[str, Any]: Google Ads information
        """
        # This is a placeholder for Google Ads setup
        # In a real implementation, this would use the Google Ads API
        
        logger.warning("Google Ads setup not implemented, using mock setup")
        return self._mock_advertising(deployment, "google_ads")
    
    def _setup_facebook_ads(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set up Facebook Ads advertising.
        
        Args:
            deployment (Dict[str, Any]): Deployment information
            
        Returns:
            Dict[str, Any]: Facebook Ads information
        """
        # This is a placeholder for Facebook Ads setup
        # In a real implementation, this would use the Facebook Ads API
        
        logger.warning("Facebook Ads setup not implemented, using mock setup")
        return self._mock_advertising(deployment, "facebook")
    
    def _mock_advertising(self, deployment: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
        Create a mock advertising setup for demonstration purposes.
        
        Args:
            deployment (Dict[str, Any]): Deployment information
            platform (str): Advertising platform
            
        Returns:
            Dict[str, Any]: Mock advertising information
        """
        domain = deployment.get("domain", {}).get("domain", "example.com")
        
        if platform == "google_ads":
            return {
                "platform": "google_ads",
                "status": "active",
                "campaign": {
                    "id": generate_unique_id(),
                    "name": f"Campaign for {domain}",
                    "budget": 10.0,
                    "currency": "USD",
                    "daily_budget": 10.0,
                    "targeting": {
                        "locations": ["United States"],
                        "languages": ["English"],
                        "devices": ["Desktop", "Mobile"]
                    }
                },
                "ad_groups": [
                    {
                        "id": generate_unique_id(),
                        "name": "Main Ad Group",
                        "status": "active",
                        "ads": [
                            {
                                "id": generate_unique_id(),
                                "type": "text",
                                "headline": f"Visit {domain}",
                                "description": "Check out our website for more information.",
                                "status": "active"
                            }
                        ],
                        "keywords": [
                            {
                                "text": domain,
                                "match_type": "exact"
                            },
                            {
                                "text": f"{domain} website",
                                "match_type": "phrase"
                            }
                        ]
                    }
                ],
                "is_mock": True
            }
        elif platform == "facebook":
            return {
                "platform": "facebook",
                "status": "active",
                "campaign": {
                    "id": generate_unique_id(),
                    "name": f"Campaign for {domain}",
                    "objective": "LINK_CLICKS",
                    "budget": 10.0,
                    "currency": "USD",
                    "daily_budget": 10.0
                },
                "ad_sets": [
                    {
                        "id": generate_unique_id(),
                        "name": "Main Ad Set",
                        "status": "active",
                        "targeting": {
                            "age_min": 18,
                            "age_max": 65,
                            "genders": [1, 2],  # 1 = male, 2 = female
                            "geo_locations": {
                                "countries": ["US"]
                            }
                        },
                        "ads": [
                            {
                                "id": generate_unique_id(),
                                "name": f"Ad for {domain}",
                                "status": "active",
                                "creative": {
                                    "title": f"Visit {domain}",
                                    "body": "Check out our website for more information.",
                                    "link": f"https://{domain}"
                                }
                            }
                        ]
                    }
                ],
                "is_mock": True
            }
        else:
            return {
                "platform": platform,
                "status": "active",
                "is_mock": True
            }