"""
Project Credits and Copyright Information for WordsProject-forstudent

This file contains attribution and copyright information for the project.
Include this in your application to properly credit the original author.
"""

PROJECT_INFO = {
    "name": "WordsProject-forstudent",
    "description": "A vocabulary learning web application built with Flask",
    "version": "1.0.0",
    "author": "[Your Name]",
    "email": "[Your Email]",
    "created": "2024",
    "license": "MIT License",
    "license_url": "https://opensource.org/licenses/MIT",
    "copyright": "Copyright (c) 2024 WordsProject-forstudent Authors"
}

def get_project_credits():
    """Return formatted project credits information."""
    return f"""
{PROJECT_INFO['name']} - {PROJECT_INFO['description']}
{PROJECT_INFO['copyright']}

Version: {PROJECT_INFO['version']}
Author: {PROJECT_INFO['author']}
License: {PROJECT_INFO['license']}
Created: {PROJECT_INFO['created']}

For more information, see:
- GitHub repository: [link to your repo]
- Contact: {PROJECT_INFO['email']}
"""

if __name__ == "__main__":
    print(get_project_credits())