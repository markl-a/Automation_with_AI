"""
External automation framework integrations.

This module provides integrations with various workflow automation platforms:

- Zapier: Cloud-based automation (webhooks)
- n8n: Self-hosted workflow automation
- Airflow: Apache Airflow for data pipelines
- Prefect: Modern data workflow orchestration
- Temporal: Durable execution platform
- Celery: Distributed task queue
- Make (Integromat): Visual automation platform

For enhanced features, use the *Enhanced classes which provide
additional functionality like retry logic, monitoring, and templates.
"""

# Basic integrations (backwards compatible)
from .zapier_integration import ZapierIntegration
from .n8n_integration import N8NIntegration
from .airflow_integration import AirflowIntegration

# Enhanced integrations (recommended for production)
from .zapier_integration_enhanced import (
    ZapierEnhancedIntegration,
    ZapierWebhookManager,
)
from .n8n_integration_enhanced import (
    N8NEnhancedIntegration,
    N8NWorkflowBuilder,
)

# Workflow orchestration integrations
from .prefect_integration import PrefectIntegration
from .temporal_integration import TemporalIntegration
from .celery_integration import CeleryIntegration

# Cloud service integrations
from .cloud_services import (
    AWSIntegration,
    GCPIntegration,
    AzureIntegration,
)

# Unified workflow abstraction
from .workflow_automation_unified import (
    UnifiedWorkflowManager,
    WorkflowProvider,
)

__all__ = [
    # Basic (backwards compatible)
    'ZapierIntegration',
    'N8NIntegration',
    'AirflowIntegration',

    # Enhanced (production recommended)
    'ZapierEnhancedIntegration',
    'ZapierWebhookManager',
    'N8NEnhancedIntegration',
    'N8NWorkflowBuilder',

    # Workflow orchestration
    'PrefectIntegration',
    'TemporalIntegration',
    'CeleryIntegration',

    # Cloud services
    'AWSIntegration',
    'GCPIntegration',
    'AzureIntegration',

    # Unified
    'UnifiedWorkflowManager',
    'WorkflowProvider',
]
