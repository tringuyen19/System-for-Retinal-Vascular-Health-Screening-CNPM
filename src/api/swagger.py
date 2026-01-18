"""
AURA API Swagger Configuration

Note: This file is kept for legacy compatibility but is NOT actively used.
The AURA system uses Flasgger for API documentation, configured in:
- app.py: Swagger initialization
- config.py: SwaggerConfig class with template and settings

Swagger UI is automatically generated at /docs endpoint by Flasgger.
Each controller can define its own Swagger specs using decorators or docstrings.
"""

# This file intentionally left minimal - Flasgger handles all Swagger functionality
# See app.py and config.py for actual Swagger configuration
