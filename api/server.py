from fastapi import FastAPI
from api.routes_control import router as control_router
from api.routes_status import router as status_router
from api.routes_debug import router as debug_router

def create_app() -> FastAPI:
    app = FastAPI(title="OrganismRobot")
    app.include_router(control_router)
    app.include_router(status_router)
    app.include_router(debug_router)

    @app.get("/")
    def root():
        return {"status": "ok", "service": "OrganismRobot"}

    return app

app = create_app()
