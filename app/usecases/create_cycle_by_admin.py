from app.domain.entities import ApplicationCycle
from typing import Optional

class CreateCycleByAdminUseCase:
    def __init__(self, cycle_repo):
        self.cycle_repo = cycle_repo

    def execute(self, name, start_date, end_date) -> Optional[ApplicationCycle]:
        # Logic to create cycle by admin will go here
        pass 