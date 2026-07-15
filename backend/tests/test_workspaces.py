import unittest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models.user import User
from app.database.enums import UserStatus
from app.services.workspace_service import WorkspaceService
from app.schemas.workspace import WorkspaceCreateRequest, WorkspaceUpdateRequest
from app.exceptions.workspace import (
    WorkspaceAlreadyExistsError,
    WorkspaceNotFoundError,
    WorkspaceAccessDeniedError,
)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_service.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestWorkspaceService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        self.db = TestingSessionLocal()
        self.service = WorkspaceService(self.db)

        # Create dummy users for testing
        self.user1_id = uuid4()
        self.user1 = User(
            id=self.user1_id,
            email=f"user1_{uuid4().hex[:6]}@example.com",
            full_name="User One",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )

        self.user2_id = uuid4()
        self.user2 = User(
            id=self.user2_id,
            email=f"user2_{uuid4().hex[:6]}@example.com",
            full_name="User Two",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )

        self.db.add(self.user1)
        self.db.add(self.user2)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_create_workspace(self):
        req = WorkspaceCreateRequest(name="WS 1", description="Desc 1")
        ws = self.service.create_workspace(self.user1_id, req)
        self.assertEqual(ws.name, "WS 1")
        self.assertEqual(ws.description, "Desc 1")
        self.assertEqual(ws.owner_id, self.user1_id)

    def test_create_duplicate_name_rejected(self):
        req = WorkspaceCreateRequest(name="WS Dup", description="Desc")
        self.service.create_workspace(self.user1_id, req)

        # Create again with same name for user 1 -> should fail
        with self.assertRaises(WorkspaceAlreadyExistsError):
            self.service.create_workspace(self.user1_id, req)

        # Create same name for user 2 -> should succeed (uniqueness is per owner)
        ws2 = self.service.create_workspace(self.user2_id, req)
        self.assertEqual(ws2.name, "WS Dup")

    def test_list_workspaces(self):
        req1 = WorkspaceCreateRequest(name="WS List 1")
        req2 = WorkspaceCreateRequest(name="WS List 2")
        self.service.create_workspace(self.user1_id, req1)
        self.service.create_workspace(self.user1_id, req2)

        workspaces = self.service.list_workspaces(self.user1_id)
        names = [w.name for w in workspaces]
        self.assertIn("WS List 1", names)
        self.assertIn("WS List 2", names)

    def test_cannot_access_another_user_workspace(self):
        req = WorkspaceCreateRequest(name="Secret WS")
        ws = self.service.create_workspace(self.user1_id, req)

        # User 1 should be able to get it
        ws_retrieved = self.service.get_workspace(self.user1_id, ws.id)
        self.assertEqual(ws_retrieved.id, ws.id)

        # User 2 should be denied
        with self.assertRaises(WorkspaceAccessDeniedError):
            self.service.get_workspace(self.user2_id, ws.id)

    def test_update_workspace(self):
        req = WorkspaceCreateRequest(name="WS Update")
        ws = self.service.create_workspace(self.user1_id, req)

        # Update description and name
        update_req = WorkspaceUpdateRequest(name="WS Updated", description="New description")
        updated = self.service.update_workspace(self.user1_id, ws.id, update_req)
        self.assertEqual(updated.name, "WS Updated")
        self.assertEqual(updated.description, "New description")

        # Try to update to an existing name of another workspace of same owner
        other_req = WorkspaceCreateRequest(name="Other WS")
        self.service.create_workspace(self.user1_id, other_req)

        dup_update = WorkspaceUpdateRequest(name="Other WS")
        with self.assertRaises(WorkspaceAlreadyExistsError):
            self.service.update_workspace(self.user1_id, ws.id, dup_update)

        # Updating without changing the name should not trigger duplicate error
        same_name_update = WorkspaceUpdateRequest(name="WS Updated", description="Another description")
        updated_same = self.service.update_workspace(self.user1_id, ws.id, same_name_update)
        self.assertEqual(updated_same.description, "Another description")

    def test_delete_workspace(self):
        req = WorkspaceCreateRequest(name="WS Delete")
        ws = self.service.create_workspace(self.user1_id, req)

        # Delete it
        self.service.delete_workspace(self.user1_id, ws.id)

        # Retrieve should fail with NotFound (as it is soft-deleted)
        with self.assertRaises(WorkspaceNotFoundError):
            self.service.get_workspace(self.user1_id, ws.id)


if __name__ == "__main__":
    unittest.main()
