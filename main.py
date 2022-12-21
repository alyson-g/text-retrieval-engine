from dotenv import load_dotenv
from fastapi import FastAPI

from logging_tools.config import setup_logging


load_dotenv()
app = FastAPI()
setup_logging()


from routers import query  # noqa: E402

app.include_router(query.router)
