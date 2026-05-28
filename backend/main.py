import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import auth, admin_onboard, admin_proposals, admin_plans, admin_status, admin_export
from .routers import village_me, village_proposal, village_plan, village_status, village_evidence
from .routers import threads, channels, donor

app = FastAPI(title="Pancham API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

for r in [
    auth.router,
    admin_onboard.router,
    admin_proposals.router,
    admin_plans.router,
    admin_status.router,
    admin_export.router,
    village_me.router,
    village_proposal.router,
    village_plan.router,
    village_status.router,
    village_evidence.router,
    threads.router,
    channels.router,
    donor.router,
]:
    app.include_router(r)
