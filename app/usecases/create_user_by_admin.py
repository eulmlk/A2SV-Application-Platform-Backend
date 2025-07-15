from app.domain.entities import User
from typing import Optional

class CreateUserByAdminUseCase:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, full_name, email, password, role) -> Optional[User]:
        # Logic to create user by admin will go here
        pass 