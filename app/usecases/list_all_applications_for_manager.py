from typing import List
from app.domain.entities import Application

class ListAllApplicationsForManagerUseCase:
    def __init__(self, application_repo):
        self.application_repo = application_repo

    def execute(self, status: str = None) -> List[Application]:
        # Logic to list all applications for manager will go here
        pass 