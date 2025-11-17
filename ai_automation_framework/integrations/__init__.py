"""External automation framework integrations."""

from .zapier_integration import ZapierIntegration
from .n8n_integration import N8NIntegration
from .airflow_integration import AirflowIntegration

__all__ = ['ZapierIntegration', 'N8NIntegration', 'AirflowIntegration']
