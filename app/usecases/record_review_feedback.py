from app.domain.entities import Review
from typing import Optional

class RecordReviewFeedbackUseCase:
    def __init__(self, review_repo):
        self.review_repo = review_repo

    def execute(self, application_id, reviewer_id, feedback_data) -> Optional[Review]:
        # Logic to record review feedback will go here
        pass 