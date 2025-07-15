from typing import List
from app.domain.entities import Application

class ListAssignedApplicationsUseCase:
    def __init__(self, application_repo):
        self.application_repo = application_repo

    def execute(self, reviewer_id) -> List[Application]:
        # Logic to list assigned applications will go here
        pass 