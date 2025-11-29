import pytest
from router import route_request, AgentType, Route, MockRouterClient

# --- Mocking the Client for Deterministic Testing ---
# In a real CI/CD pipeline, you don't want to hit the real OpenAI API.
# You want to test your *logic* (how you handle the response), not the *model* (what it predicts).

class TestRouter:
    def setup_method(self):
        self.client = MockRouterClient()

    def test_coding_query(self):
        """Test that coding queries are routed to the Coding Agent"""
        query = "Write a Python script"
        route = route_request(self.client, query)
        assert route.agent == AgentType.CODING
        assert route.confidence > 0.5

    def test_weather_query(self):
        """Test that weather queries are routed to the Weather Agent"""
        query = "Is it raining?"
        route = route_request(self.client, query)
        assert route.agent == AgentType.WEATHER

    def test_general_query(self):
        """Test fallback to General Agent"""
        query = "Hello there"
        route = route_request(self.client, query)
        assert route.agent == AgentType.GENERAL

if __name__ == "__main__":
    # Manual run if pytest is not installed
    t = TestRouter()
    t.setup_method()
    t.test_coding_query()
    print("All tests passed!")
