"""Tests for the Mergington High School Activities API."""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_returns_activity_details(self, client):
        """Test that activities contain required fields."""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_returns_participants_list(self, client):
        """Test that participants are returned as a list."""
        response = client.get("/activities")
        data = response.json()
        
        participants = data["Chess Club"]["participants"]
        assert isinstance(participants, list)
        assert "michael@mergington.edu" in participants


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Tennis Club" in data["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup adds participant to the activity."""
        # Sign up new participant
        client.post("/activities/Art%20Studio/signup?email=newartist@mergington.edu")
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        
        participants = data["Art Studio"]["participants"]
        assert "newartist@mergington.edu" in participants

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup fails for non-existent activity."""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_already_registered_fails(self, client):
        """Test that signup fails if student is already registered."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_multiple_students(self, client):
        """Test that multiple different students can sign up."""
        client.post("/activities/Music%20Band/signup?email=student1@mergington.edu")
        client.post("/activities/Music%20Band/signup?email=student2@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        
        participants = data["Music Band"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity."""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from the activity."""
        # Unregister participant
        client.delete(
            "/activities/Programming%20Class/unregister?email=emma@mergington.edu"
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        
        participants = data["Programming Class"]["participants"]
        assert "emma@mergington.edu" not in participants

    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregister fails for non-existent activity."""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_not_registered_fails(self, client):
        """Test that unregister fails if student is not registered."""
        response = client.delete(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_then_signup_again(self, client):
        """Test that a student can sign up again after unregistering."""
        # Unregister
        client.delete(
            "/activities/Basketball/unregister?email=james@mergington.edu"
        )
        
        # Sign up again
        response = client.post(
            "/activities/Basketball/signup?email=james@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify re-registration
        get_response = client.get("/activities")
        data = get_response.json()
        assert "james@mergington.edu" in data["Basketball"]["participants"]


class TestActivityCardLoading:
    """Tests for activity data structure used in frontend."""

    def test_activity_has_name_field(self, client):
        """Test that activities include a name field in the data."""
        response = client.get("/activities")
        data = response.json()
        
        # The name comes from the key, verify the structure works
        assert "Chess Club" in data
        assert isinstance(data["Chess Club"], dict)

    def test_activity_schedule_field(self, client):
        """Test that schedule field is properly formatted."""
        response = client.get("/activities")
        data = response.json()
        
        schedule = data["Gym Class"]["schedule"]
        assert "Mondays" in schedule or "Wednesdays" in schedule or "Fridays" in schedule

    def test_activity_description_field(self, client):
        """Test that description field is present and non-empty."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert len(activity_data["description"]) > 0
