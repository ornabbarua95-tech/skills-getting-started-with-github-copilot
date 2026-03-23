import pytest
from src.app import activities


class TestIntegration:
    """Test multi-step workflows involving signup and unregister."""

    def test_signup_unregister_sequence(self, client):
        """Arrange-Act-Assert: Verify signup then unregister workflow."""
        # Arrange: Fresh student and activity
        activity = "Science Club"
        student = "workflow@mergington.edu"
        
        # Act 1: Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        
        # Assert 1: Signup succeeds
        assert signup_response.status_code == 200
        assert student in activities[activity]["participants"]
        
        # Act 2: Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        
        # Assert 2: Unregister succeeds
        assert unregister_response.status_code == 200
        assert student not in activities[activity]["participants"]

    def test_signup_twice_then_unregister(self, client):
        """Arrange-Act-Assert: Verify can't signup twice, but unregister works."""
        # Arrange: Fresh student and activity
        activity = "Basketball Team"
        student = "twicestudent@mergington.edu"
        
        # Act 1: First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        assert response1.status_code == 200
        
        # Act 2: Second signup attempt
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        
        # Assert: Second signup should fail
        assert response2.status_code == 400
        
        # Act 3: Unregister
        response3 = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        
        # Assert: Unregister succeeds
        assert response3.status_code == 200
        assert student not in activities[activity]["participants"]

    def test_multiple_activities_independent(self, client):
        """Arrange-Act-Assert: Verify signup to multiple activities are independent."""
        # Arrange: One student, two activities
        student = "multiactivity@mergington.edu"
        activity1 = "Swimming Club"
        activity2 = "Art Studio"
        
        # Act: Sign up for both activities
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": student}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": student}
        )
        
        # Assert: Both signups succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert student in activities[activity1]["participants"]
        assert student in activities[activity2]["participants"]
        
        # Act: Unregister from first activity
        response3 = client.post(
            f"/activities/{activity1}/unregister",
            params={"email": student}
        )
        
        # Assert: Only removed from activity1, still in activity2
        assert response3.status_code == 200
        assert student not in activities[activity1]["participants"]
        assert student in activities[activity2]["participants"]

    def test_participant_count_updates(self, client):
        """Arrange-Act-Assert: Verify participant count updates correctly."""
        # Arrange: Know initial count
        activity = "Debate Team"
        student1 = "count1@mergington.edu"
        student2 = "count2@mergington.edu"
        initial_count = len(activities[activity]["participants"])
        
        # Act: Sign up two students
        client.post(
            f"/activities/{activity}/signup",
            params={"email": student1}
        )
        client.post(
            f"/activities/{activity}/signup",
            params={"email": student2}
        )
        
        # Assert: Count increased by 2
        assert len(activities[activity]["participants"]) == initial_count + 2
        
        # Act: Unregister one student
        client.post(
            f"/activities/{activity}/unregister",
            params={"email": student1}
        )
        
        # Assert: Count decreased by 1
        assert len(activities[activity]["participants"]) == initial_count + 1

    def test_get_activities_reflects_changes(self, client):
        """Arrange-Act-Assert: Verify GET /activities reflects signup/unregister."""
        # Arrange: Fresh student
        activity = "Programming Class"
        student = "gettest@mergington.edu"
        
        # Act 1: Get activities before signup
        response1 = client.get("/activities")
        data1 = response1.json()
        initial_participants = set(data1[activity]["participants"])
        
        # Act 2: Sign up
        client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        
        # Act 3: Get activities after signup
        response2 = client.get("/activities")
        data2 = response2.json()
        after_signup_participants = set(data2[activity]["participants"])
        
        # Assert: Student appears in the list
        assert student in after_signup_participants
        assert student not in initial_participants
        
        # Act 4: Unregister
        client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        
        # Act 5: Get activities after unregister
        response3 = client.get("/activities")
        data3 = response3.json()
        after_unregister_participants = set(data3[activity]["participants"])
        
        # Assert: Student removed from list
        assert student not in after_unregister_participants
