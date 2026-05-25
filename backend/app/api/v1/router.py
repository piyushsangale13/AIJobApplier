from fastapi import APIRouter

from app.api.v1.endpoints import applications, dashboard, jobs, resumes, search_preferences


api_router = APIRouter()
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(
    search_preferences.router, prefix="/search-preferences", tags=["search-preferences"]
)
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
