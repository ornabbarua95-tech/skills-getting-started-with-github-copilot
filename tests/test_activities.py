import pytest


class TestGetActivities:
    """Test the GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Arrange-Act-Assert: Verify activities endpoint returns 200 OK."""
        # Arrange: Ready to make request (client fixture provided)
        
        # Act: Fetch all activities
        response = client.get("/activities")
        
        # Assert: Should return success status
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Arrange-Act-Assert: Verify activities endpoint returns a dictionary."""
        # Arrange: No special setup needed
        
        # Act: Fetch all activities
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Response should be a dictionary
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_has_required_fields(self, client):
        """Arrange-Act-Assert: Verify each activity has required fields."""
        # Arrange: No special setup needed
        
        # Act: Fetch all activities
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Each activity should have required fields
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())

    def test_get_activities_participants_is_list(self, client):
        """Arrange-Act-Assert: Verify participants field is a list."""
        # Arrange: No special setup needed
        
        # Act: Fetch all activities
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Participants should be a list
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_includes_known_activities(self, client, sample_activities):
        """Arrange-Act-Assert: Verify response includes expected activities."""
        # Arrange: Know which activities should exist
        expected_activities = set(sample_activities.keys())
        
        # Act: Fetch all activities
        response = client.get("/activities")
        data = response.json()
        actual_activities = set(data.keys())
        
        # Assert: Known activities should be present
        assert expected_activities.issubset(actual_activities)
