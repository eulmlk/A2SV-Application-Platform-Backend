from app.domain.entities import Application
from typing import Optional

class SubmitApplicationUseCase:
    def __init__(self, application_repo):
        self.application_repo = application_repo

    def execute(self, applicant_id, school, degree, leetcode_handle, codeforces_handle, essay, resume_url) -> Optional[Application]:
        # Logic to submit application will go here
        pass 