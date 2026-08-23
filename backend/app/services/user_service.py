from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserUpdate
from app.core.exceptions import ServiceException

class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower().strip()).first()

    @staticmethod
    def update_profile(db: Session, user: User, update_data: UserUpdate) -> User:
        """
        Update safe user profile fields.
        Explicitly prevents modifications to roles, permissions, passwords, or lock statuses.
        """
        if update_data.first_name is not None:
            user.first_name = update_data.first_name.strip() or None
        if update_data.last_name is not None:
            user.last_name = update_data.last_name.strip() or None

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def assign_role(db: Session, user: User, role_name: str) -> User:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise ServiceException(f"Role '{role_name}' does not exist.", status_code=404)
        
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

user_service = UserService()
