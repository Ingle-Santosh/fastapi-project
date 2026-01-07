from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.api import routes_auth, routes_predict, routes_health
from app.middleware.logging_middleware import LoggingMiddleware
from app.core.custom_exceptions import register_exception_handler

app = FastAPI(title="Car Price Prediction API")

#Link Middleware
app.add_middleware(LoggingMiddleware)

# Link Endpoints
app.include_router(routes_auth.router, tags=['Auth'])
app.include_router(routes_predict.router, tags=['Prediction'])
app.include_router(routes_health.router, tags=['Health'])

# Monitoring using Prometheus
Instrumentator().instrument(app).expose(app)

# Add Exception handler
register_exception_handler(app)