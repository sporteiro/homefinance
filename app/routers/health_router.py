from fastapi import APIRouter


class HealthRouter:
    def __init__(self) -> None:
        self.router = APIRouter(tags=["health"])
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route("/health", self.health, methods=["GET"])

    def health(self) -> dict[str, str]:
        return {"status": "ok"}


health_router = HealthRouter().router
