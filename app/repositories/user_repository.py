# app/repositories/user_repository.py
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate
from app.core.exceptions import DuplicateEntryException, NotFoundException, DatabaseException


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_create: UserCreate) -> User:
        """
        Create a new user in the database.
        
        Args:
            user_create: UserCreate schema with user data
            
        Returns:
            The created User object
            
        Raises:
            DuplicateEntryException: If username or email already exists
            DatabaseException: For other database errors
        """
        try:
            db_user = User(
                username=user_create.username,
                email=user_create.email,
                hashed_password=user_create.password  # Note: Password should be hashed before this point
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            self.db.rollback()
            if "username" in str(e.orig):
                raise DuplicateEntryException("Username already exists")
            elif "email" in str(e.orig):
                raise DuplicateEntryException("Email already exists")
            raise DatabaseException("Database integrity error occurred")
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Unexpected error creating user: {str(e)}")

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get a user by their ID.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by their email.
        
        Args:
            email: Email address of the user
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by their username.
        
        Args:
            username: Username of the user
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.username == username).first()

    def update_user(self, user_id: UUID, user_update: UserUpdate) -> User:
        """
        Update a user's information.
        
        Args:
            user_id: UUID of the user to update
            user_update: UserUpdate schema with updated fields
            
        Returns:
            The updated User object
            
        Raises:
            NotFoundException: If user with given ID doesn't exist
            DuplicateEntryException: If new username or email already exists
            DatabaseException: For other database errors
        """
        try:
            db_user = self.get_user_by_id(user_id)
            if not db_user:
                raise NotFoundException("User not found")

            update_data = user_update.dict(exclude_unset=True)
            
            # Check for duplicate username if it's being updated
            if 'username' in update_data:
                existing_user = self.get_user_by_username(update_data['username'])
                if existing_user and existing_user.id != user_id:
                    raise DuplicateEntryException("Username already exists")

            # Check for duplicate email if it's being updated
            if 'email' in update_data:
                existing_user = self.get_user_by_email(update_data['email'])
                if existing_user and existing_user.id != user_id:
                    raise DuplicateEntryException("Email already exists")

            for key, value in update_data.items():
                setattr(db_user, key, value)

            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseException("Database integrity error occurred")
        except Exception as e:
            self.db.rollback()
            if isinstance(e, (NotFoundException, DuplicateEntryException)):
                raise
            raise DatabaseException(f"Unexpected error updating user: {str(e)}")

    def delete_user(self, user_id: UUID) -> bool:
        """
        Delete a user from the database.
        
        Args:
            user_id: UUID of the user to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            NotFoundException: If user with given ID doesn't exist
            DatabaseException: For other database errors
        """
        try:
            db_user = self.get_user_by_id(user_id)
            if not db_user:
                raise NotFoundException("User not found")

            self.db.delete(db_user)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            if isinstance(e, NotFoundException):
                raise
            raise DatabaseException(f"Unexpected error deleting user: {str(e)}")