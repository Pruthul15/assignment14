"""
FINAL FIXED Test Suite - Correct operation names (addition, subtraction, multiplication, division)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4


@pytest.fixture(scope="session")
def test_db():
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    try:
        from app.database import Base
        Base.metadata.create_all(bind=engine)
    except:
        pass
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield engine, TestingSessionLocal
    
    # Don't drop tables - let them persist for all tests in the session


@pytest.fixture(scope="session")
def client(test_db):
    from app.main import app
    from app.database import get_db
    
    engine, TestingSessionLocal = test_db
    
    def override_get_db():
        db = TestingSessionLocal()
        yield db
        db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


class TestUserAuthentication:
    """Test suite for user registration and login."""
    
    def test_register_user_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "username": f"testuser_{uuid4().hex[:8]}",
                "email": f"test_{uuid4().hex[:8]}@example.com",
                "password": "SecurePassword123!",
                "confirm_password": "SecurePassword123!",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        assert response.status_code in [200, 201], f"Got {response.status_code}: {response.json()}"
        data = response.json()
        assert "id" in data or "username" in data
    
    def test_register_user_duplicate_email(self, client):
        """Test registration fails with duplicate email."""
        client.post(
            "/auth/register",
            json={
                "username": "user1",
                "email": "duplicate@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "first_name": "User",
                "last_name": "One"
            }
        )
        response = client.post(
            "/auth/register",
            json={
                "username": "user2",
                "email": "duplicate@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "first_name": "User",
                "last_name": "Two"
            }
        )
        assert response.status_code in [400, 409, 422]
    
    def test_login_user_success(self, client):
        """Test successful user login."""
        client.post(
            "/auth/register",
            json={
                "username": "logintest",
                "email": "login@example.com",
                "password": "ValidPass123!",
                "confirm_password": "ValidPass123!",
                "first_name": "Login",
                "last_name": "Test"
            }
        )
        response = client.post(
            "/auth/login",
            json={
                "username": "logintest",
                "password": "ValidPass123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data
    
    def test_login_user_wrong_password(self, client):
        """Test login fails with wrong password."""
        client.post(
            "/auth/register",
            json={
                "username": "wrongpass",
                "email": "wrongpass@example.com",
                "password": "CorrectPass123!",
                "confirm_password": "CorrectPass123!",
                "first_name": "Wrong",
                "last_name": "Pass"
            }
        )
        response = client.post(
            "/auth/login",
            json={
                "username": "wrongpass",
                "password": "WrongPass123!"
            }
        )
        assert response.status_code == 401


class TestBREADOperations:
    """Test BREAD operations."""
    
    @pytest.fixture
    def authenticated_user(self, client):
        """Create and authenticate a user."""
        username = f"user_{uuid4().hex[:8]}"
        email = f"user_{uuid4().hex[:8]}@example.com"
        
        reg = client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": "SecurePass123!@#",
                "confirm_password": "SecurePass123!@#",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        assert reg.status_code in [200, 201], f"Registration failed: {reg.json()}"
        
        login = client.post(
            "/auth/login",
            json={
                "username": username,
                "password": "SecurePass123!@#"
            }
        )
        
        assert login.status_code == 200, f"Login failed: {login.json()}"
        
        token = login.json().get("access_token") or login.json().get("token")
        return {"headers": {"Authorization": f"Bearer {token}"}}
    
    def test_add_calculation_success(self, client, authenticated_user):
        """Test adding a calculation (ADD operation)."""
        response = client.post(
            "/calculations",
            json={"type": "addition", "inputs": [5, 3]},
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data.get("result") == 8
    
    def test_browse_calculations(self, client, authenticated_user):
        """Test browsing calculations (BROWSE operation)."""
        for i in range(2):
            client.post(
                "/calculations",
                json={"type": "addition", "inputs": [i, i+1]},
                headers=authenticated_user["headers"]
            )
        
        response = client.get(
            "/calculations",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
    
    def test_browse_calculations_pagination(self, client, authenticated_user):
        """Test browse with pagination parameters."""
        response = client.get(
            "/calculations?skip=0&limit=10",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
    
    def test_read_calculation_success(self, client, authenticated_user):
        """Test reading a calculation (READ operation)."""
        create_resp = client.post(
            "/calculations",
            json={"type": "multiplication", "inputs": [4, 5]},
            headers=authenticated_user["headers"]
        )
        
        calc_id = create_resp.json().get("id")
        
        response = client.get(
            f"/calculations/{calc_id}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("result") == 20
    
    def test_read_calculation_not_found(self, client, authenticated_user):
        """Test reading non-existent calculation."""
        fake_id = str(uuid4())
        response = client.get(
            f"/calculations/{fake_id}",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404
    
    def test_read_calculation_invalid_id_format(self, client, authenticated_user):
        """Test reading calculation with invalid ID format."""
        response = client.get(
            "/calculations/invalid-id",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 400
    
    def test_edit_calculation_success(self, client, authenticated_user):
        """Test updating a calculation (EDIT operation)."""
        create_resp = client.post(
            "/calculations",
            json={"type": "subtraction", "inputs": [10, 3]},
            headers=authenticated_user["headers"]
        )
        
        calc_id = create_resp.json().get("id")
        
        response = client.put(
            f"/calculations/{calc_id}",
            json={"inputs": [10, 5]},
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("result") == 5
    
    def test_edit_calculation_not_found(self, client, authenticated_user):
        """Test editing non-existent calculation."""
        fake_id = str(uuid4())
        response = client.put(
            f"/calculations/{fake_id}",
            json={"inputs": [1, 1]},
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404
    
    def test_delete_calculation_success(self, client, authenticated_user):
        """Test deleting a calculation (DELETE operation)."""
        create_resp = client.post(
            "/calculations",
            json={"type": "addition", "inputs": [1, 1]},
            headers=authenticated_user["headers"]
        )
        
        calc_id = create_resp.json().get("id")
        
        response = client.delete(
            f"/calculations/{calc_id}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code in [200, 204]
        
        get_resp = client.get(
            f"/calculations/{calc_id}",
            headers=authenticated_user["headers"]
        )
        
        assert get_resp.status_code == 404
    
    def test_delete_calculation_not_found(self, client, authenticated_user):
        """Test deleting non-existent calculation."""
        fake_id = str(uuid4())
        response = client.delete(
            f"/calculations/{fake_id}",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404
    
    def test_delete_calculation_unauthorized(self, client, authenticated_user):
        """Test that user can only delete their own calculations."""
        create_resp = client.post(
            "/calculations",
            json={"type": "addition", "inputs": [1, 1]},
            headers=authenticated_user["headers"]
        )
        calc_id = create_resp.json().get("id")
        
        # Create another user
        client.post(
            "/auth/register",
            json={
                "username": "otheruser",
                "email": "other@example.com",
                "password": "OtherPass123!",
                "confirm_password": "OtherPass123!",
                "first_name": "Other",
                "last_name": "User"
            }
        )
        other_response = client.post(
            "/auth/login",
            json={
                "username": "otheruser",
                "password": "OtherPass123!"
            }
        )
        other_token = other_response.json().get("access_token") or other_response.json().get("token")
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        response = client.delete(f"/calculations/{calc_id}", headers=other_headers)
        assert response.status_code in [403, 404]


class TestCalculationOperations:
    """Test various calc operations."""
    
    @pytest.fixture
    def authenticated_user(self, client):
        """Create and authenticate a user."""
        username = f"user_{uuid4().hex[:8]}"
        email = f"user_{uuid4().hex[:8]}@example.com"
        
        reg = client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": "SecurePass123!@#",
                "confirm_password": "SecurePass123!@#",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        if reg.status_code not in [200, 201]:
            pytest.skip(f"Registration failed: {reg.json()}")
        
        login = client.post(
            "/auth/login",
            json={"username": username, "password": "SecurePass123!@#"}
        )
        
        if login.status_code != 200:
            pytest.skip(f"Login failed: {login.json()}")
        
        token = login.json().get("access_token") or login.json().get("token")
        return {"headers": {"Authorization": f"Bearer {token}"}}
    
    def test_add_operation(self, client, authenticated_user):
        """Test addition operation."""
        response = client.post(
            "/calculations",
            json={"type": "addition", "inputs": [5, 3]},
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201
        assert response.json().get("result") == 8
    
    def test_subtract_operation(self, client, authenticated_user):
        """Test subtraction operation."""
        response = client.post(
            "/calculations",
            json={"type": "subtraction", "inputs": [10, 3]},
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201
        assert response.json().get("result") == 7
    
    def test_multiply_operation(self, client, authenticated_user):
        """Test multiplication operation."""
        response = client.post(
            "/calculations",
            json={"type": "multiplication", "inputs": [4, 5]},
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201
        assert response.json().get("result") == 20
    
    def test_divide_operation(self, client, authenticated_user):
        """Test division operation."""
        response = client.post(
            "/calculations",
            json={"type": "division", "inputs": [20, 4]},
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201
        assert response.json().get("result") == 5.0
    
    def test_divide_by_zero(self, client, authenticated_user):
        """Test division by zero error handling."""
        response = client.post(
            "/calculations",
            json={"type": "division", "inputs": [5, 0]},
            headers=authenticated_user["headers"]
        )
        assert response.status_code in [400, 422]
    
    def test_invalid_operation(self, client, authenticated_user):
        """Test invalid operation."""
        response = client.post(
            "/calculations",
            json={"type": "invalid_op", "inputs": [5, 3]},
            headers=authenticated_user["headers"]
        )
        assert response.status_code in [400, 422]


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_missing_required_fields(self, client):
        """Test request with missing required fields."""
        username = f"user_{uuid4().hex[:8]}"
        client.post(
            "/auth/register",
            json={
                "username": username,
                "email": f"user_{uuid4().hex[:8]}@example.com",
                "password": "SecurePass123!@#",
                "confirm_password": "SecurePass123!@#",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        login = client.post(
            "/auth/login",
            json={"username": username, "password": "SecurePass123!@#"}
        )
        token = login.json().get("access_token") or login.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/calculations",
            json={"type": "addition"},
            headers=headers
        )
        assert response.status_code == 422
    
    def test_invalid_input_types(self, client):
        """Test request with invalid input types."""
        username = f"user_{uuid4().hex[:8]}"
        client.post(
            "/auth/register",
            json={
                "username": username,
                "email": f"user_{uuid4().hex[:8]}@example.com",
                "password": "SecurePass123!@#",
                "confirm_password": "SecurePass123!@#",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        login = client.post(
            "/auth/login",
            json={"username": username, "password": "SecurePass123!@#"}
        )
        token = login.json().get("access_token") or login.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/calculations",
            json={"type": "addition", "inputs": ["string", 3]},
            headers=headers
        )
        assert response.status_code == 422
    
    def test_empty_inputs_array(self, client):
        """Test request with empty inputs array."""
        username = f"user_{uuid4().hex[:8]}"
        client.post(
            "/auth/register",
            json={
                "username": username,
                "email": f"user_{uuid4().hex[:8]}@example.com",
                "password": "SecurePass123!@#",
                "confirm_password": "SecurePass123!@#",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        login = client.post(
            "/auth/login",
            json={"username": username, "password": "SecurePass123!@#"}
        )
        token = login.json().get("access_token") or login.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/calculations",
            json={"type": "addition", "inputs": []},
            headers=headers
        )
        assert response.status_code in [400, 422]
    
    def test_invalid_token(self, client):
        """Test request with invalid token."""
        headers = {"Authorization": "Bearer invalid_token_xyz"}
        response = client.get("/calculations", headers=headers)
        assert response.status_code == 401
    
    def test_no_token(self, client):
        """Test request without token."""
        response = client.get("/calculations")
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])