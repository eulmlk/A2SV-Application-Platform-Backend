from app.domain.entities import Application
from typing import Optional

class GetApplicantStatusUseCase:
    def __init__(self, application_repo):
        self.application_repo = application_repo

    def execute(self, applicant_id) -> Optional[Application]:
        # Logic to get applicant status will go here
        pass 