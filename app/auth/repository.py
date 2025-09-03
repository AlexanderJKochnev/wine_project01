# app/auth/repository.py
from app.core.repositories.sqlalchemy_repository import Repository
from app.auth.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository(Repository):
    model = User

    def get_query(self):
        return select(User)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def authenticate(self, username: str, password: str, session: AsyncSession):
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def create(self, data: dict, session):
        data["hashed_password"] = self.get_password_hash(data.pop("password"))
        verified_data = self.model(**data)
        return await super().create(verified_data, session)

    async def get_superuser_by_username(self, username: str, session: AsyncSession):
        from sqlalchemy import select
        stmt = select(User).where(User.username == username,
                                  User.is_superuser == True,
                                  User.is_active == True)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
