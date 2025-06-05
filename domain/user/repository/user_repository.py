from domain.user.entity import User


class UserRepository:

    @staticmethod
    async def save_user_info(db: AsyncSession, user: User) -> User:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
