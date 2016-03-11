"""Pagerduty lib methods."""
import pygerduty
import os


class PagerDuty(object):
    """Open a communication channel with pagerduty."""

    def __init__(self, subdomain='', api='', service_key=''):
        """Set up required vars."""
        self._subdomain = os.environ.get('PD_SUBDOMAIN', subdomain)
        self._api = os.environ.get('PD_API_TOKEN', api)
        self._service_key = os.environ.get('PD_SERVICE_KEY', service_key)

        self.pagerduty = pygerduty.PagerDuty(self._subdomain, self._api)

    def send(self, description, incident_key='', details='',
             event_type='trigger'):
        """Trigger a new event at Pagerduty."""
        return self.pagerduty.create_event(
            self._service_key,
            description,
            event_type,
            details,
            incident_key
        )

    def resolve(self, incident_key):
        """Resolve an earlier triggered/acknowledged event at Pagerduty."""
        return self.pagerduty.resolve_incident(
            self._service_key,
            incident_key
        )
