"""Custom throttling rules.

OTP endpoints are rate limited aggressively per IP because they are the entry
point for account takeover attempts. Everything else uses the generous
defaults from `settings.REST_FRAMEWORK`.
"""
from rest_framework.throttling import AnonRateThrottle


class OTPBurstThrottle(AnonRateThrottle):
    """Limits how often an anonymous client can request or verify an OTP."""

    scope = 'otp'
