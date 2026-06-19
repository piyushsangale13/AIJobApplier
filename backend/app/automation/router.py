from app.automation.greenhouse_handler import GreenhouseHandler
from app.automation.lever_handler import LeverHandler
from app.automation.linkedin_easy_apply_handler import LinkedInEasyApplyHandler
from app.automation.workday_handler import WorkdayHandler


HANDLER_REGISTRY = {
    "greenhouse": GreenhouseHandler,
    "lever": LeverHandler,
    "workday": WorkdayHandler,
    "linkedin_easy_apply": LinkedInEasyApplyHandler,
}


def get_handler_class(ats_type: str):
    return HANDLER_REGISTRY.get(ats_type)
