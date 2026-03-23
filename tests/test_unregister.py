import pytest
from src.app import activities


class TestUnregister:
    """Test the POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client):
        """Arrange-Act-Assert: Verify successful unregister removes participant."""
        # Arrange: Use a student already in Chess Club
        activity = "Chess Club"
        student = "michael@mergington.edu"
        initial_count = len(activities[activity]["participants"])
        
        # Act: Unregister the student
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        
        # Assert: Should return 200 OK and remove participant
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert student not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count - 1

    def test_unregister_activity_not_found(self, client):
        """Arrange-Act-Assert: Verify unregister fails for non-existent activity."""
        # Arrange: Use a student email and non-existent activity
        student_email = "student@mergington.edu"
        fake_activity = "Nonexistent Activity"
        
        # Act: Attempt to unregister from non-existent activity
        response = client.post(
            f"/activities/{fake_activity}/unregister",
            params={"email": student_email}
        )
        
        # Assert: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data.get("detail", "")

    def test_unregister_student_not_found(self, client):
        """Arrange-Act-Assert: Verify unregister fails if student not registered."""
        # Arrange: Use a student not in Programming Class
        activity = "Programming Class"
        student = "notregistered@mergington.edu"
        
        # Act: Attempt to unregister a student not in the activity
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        
        # Assert: Should return 400 Bad Request
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data.get("detail", "").lower()

    def test_unregister_email_normalization(self, client):
        """Arrange-Act-Assert: Verify unregister works with normalized email."""
        # Arrange: Pre-register a student with mixed case
        activity = "Gym Class"
        student_lowercase = "john@mergington.edu"
        
        # Act: Unregister using uppercase email
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": "JOHN@MERGINGTON.EDU"}
        )
        
        # Assert: Should succeed even with different case
        assert response.status_code == 200
        assert student_lowercase not in activities[activity]["participants"]

    def test_unregister_response_format(self, client):
        """Arrange-Act-Assert: Verify response includes correct message format."""
        # Arrange: Use a student in an activity
        activity = "Chess Club"
        student = "daniel@mergington.edu"
        
        # Act: Unregister
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        
        # Assert: Response should have proper message format
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert student in data["message"]
        assert activity in data["message"]

    def test_unregister_whitespace_handled(self, client):
        """Arrange-Act-Assert: Verify unregister handles whitespace in email."""
        # Arrange: Pre-register a student
        activity = "Drama Club"
        student = "newdrama@mergington.edu"
        
        # First, sign up the student
        client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        
        # Act: Unregister with whitespace
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": "  newdrama@mergington.edu  "}
        )
        
        # Assert: Should succeed with whitespace trimmed
        assert response.status_code == 200
        assert student not in activities[activity]["participants"]

    def test_unregister_double_unregister_fails(self, client):
        """Arrange-Act-Assert: Verify double unregister is rejected."""
        # Arrange: Sign up and unregister a student
        activity = "Basketball Team"
        student = "doubletest@mergington.edu"
        
        client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        
        # Act: First unregister succeeds
        response1 = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        assert response1.status_code == 200
        
        # Act: Second unregister attempt
        response2 = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        
        # Assert: Second unregister should fail
        assert response2.status_code == 400
        assert "not signed up" in response2.json().get("detail", "").lower()
