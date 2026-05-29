import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import auth, admin_onboard, admin_proposals, admin_plans, admin_status, admin_export, admin_users, admin_maintenance
from .routers import village_me, village_proposal, village_plan, village_status, village_evidence
from .routers import threads, channels, donor, org

app = FastAPI(title="Pancham API")


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "")
    if raw:
        return [x.strip() for x in raw.split(",") if x.strip()]
    return [
        "https://pancham.up.railway.app",
        "https://pancham-frontend.up.railway.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def _cors_origin_regex() -> str:
    return os.getenv("CORS_ORIGIN_REGEX", r"https://.*\.railway\.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_origin_regex=_cors_origin_regex(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

for r in [
    auth.router,
    admin_onboard.router,
    admin_users.router,
    admin_maintenance.router,
    admin_proposals.router,
    admin_plans.router,
    admin_status.router,
    admin_export.router,
    village_me.router,
    village_proposal.router,
    village_plan.router,
    village_status.router,
    village_evidence.router,
    org.router,
    threads.router,
    channels.router,
    donor.router,
]:
    app.include_router(r)
