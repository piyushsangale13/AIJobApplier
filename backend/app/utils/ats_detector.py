from urllib.parse import urlparse


def detect_ats_type(apply_url: str) -> str:
    host = urlparse(apply_url).netloc.lower()
    path = urlparse(apply_url).path.lower()
    full = f"{host}{path}"

    if "greenhouse.io" in host:
        return "greenhouse"
    if "jobs.lever.co" in host or "lever.co" in host:
        return "lever"
    if "workday" in full:
        return "workday"
    if "linkedin.com" in host and ("easy apply" in full or "jobs/view" in full or "/jobs/" in full):
        return "linkedin_easy_apply"
    return "unknown"
