from app.domain.entities import ApplicationCycle
from typing import Optional

class ActivateCycleByAdminUseCase:
    def __init__(self, cycle_repo):
        self.cycle_repo = cycle_repo

    def execute(self, cycle_id) -> Optional[ApplicationCycle]:
        # Logic to activate cycle by admin will go here
        pass 