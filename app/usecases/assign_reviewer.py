from app.domain.entities import Application
from typing import Optional

class AssignReviewerUseCase:
    def __init__(self, application_repo):
        self.application_repo = application_repo

    def execute(self, application_id, reviewer_id) -> Optional[Application]:
        # Logic to assign reviewer will go here
        pass 