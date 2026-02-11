"""
This module provides HTTP client implementations for making HTTP requests. 

Its purpose is to abstract away the details of making HTTP requests. Allows 
for easier mocking and testing of HTTP interactions.
"""
from .httpClient import HttpClient
from .requestsHttpClient import RequestsHttpClient
