import pytest
from src.app import activities


class TestSignup:
    """Test the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """Arrange-Act-Assert: Verify successful signup adds participant."""
        # Arrange: Use a new student email and available activity
        new_student = "newstudent@mergington.edu"
        activity = "Basketball Team"  # Known to have empty participants
        
        # Act: Sign up the student
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": new_student}
        )
        
        # Assert: Should return 200 OK and include success message
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_student.lower() in activities[activity]["participants"]

    def test_signup_activity_not_found(self, client):
        """Arrange-Act-Assert: Verify signup fails for non-existent activity."""
        # Arrange: Use a student email and non-existent activity
        student_email = "student@mergington.edu"
        fake_activity = "Nonexistent Activity"
        
        # Act: Attempt to sign up for non-existent activity
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": student_email}
        )
        
        # Assert: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data.get("detail", "")

    def test_signup_duplicate_rejected(self, client):
        """Arrange-Act-Assert: Verify duplicate signup is rejected."""
        # Arrange: Use an email already in Chess Club
        duplicate_student = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act: Attempt to sign up an already-registered student
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": duplicate_student}
        )
        
        # Assert: Should return 400 Bad Request with duplicate error
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data.get("detail", "").lower()

    def test_signup_email_normalization(self, client):
        """Arrange-Act-Assert: Verify email is normalized (lowercase)."""
        # Arrange: Use uppercase email for a new student
        activity = "Swimming Club"
        
        # Act: Sign up with uppercase email
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": "NEWEMAIL@MERGINGTON.EDU"}
        )
        
        # Assert: Should succeed and store as lowercase
        assert response.status_code == 200
        assert "newemail@mergington.edu" in activities[activity]["participants"]
        assert "NEWEMAIL@MERGINGTON.EDU" not in activities[activity]["participants"]

    def test_signup_email_whitespace_trimmed(self, client):
        """Arrange-Act-Assert: Verify email whitespace is trimmed."""
        # Arrange: Use email with leading/trailing whitespace
        activity = "Art Studio"
        
        # Act: Sign up with whitespace around email
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": "  trimmed@mergington.edu  "}
        )
        
        # Assert: Should succeed and store without whitespace
        assert response.status_code == 200
        assert "trimmed@mergington.edu" in activities[activity]["participants"]

    def test_signup_response_format(self, client):
        """Arrange-Act-Assert: Verify response includes correct message format."""
        # Arrange: Use a new student
        student = "formattest@mergington.edu"
        activity = "Debate Team"
        
        # Act: Sign up
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        
        # Assert: Response should have proper message format
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert student.lower() in data["message"]
        assert activity in data["message"]

    def test_signup_case_insensitive_activity_name(self, client):
        """Arrange-Act-Assert: Verify activity names are case-sensitive (current behavior)."""
        # Arrange: Use correct and incorrect case activity name
        student = "casetest@mergington.edu"
        
        # Act: Try with incorrect case
        response = client.post(
            f"/activities/chess club/signup",  # lowercase
            params={"email": student}
        )
        
        # Assert: Should fail because activity names are case-sensitive
        assert response.status_code == 404
