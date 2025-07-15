from app.domain.entities import User
from typing import Optional

class RegisterApplicantUseCase:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, full_name: str, email: str, password: str) -> Optional[User]:
        # Logic to register applicant will go here
        pass 