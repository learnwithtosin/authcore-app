from fastapi import FastAPI, status, HTTPException
from fastapi.staticfiles import StaticFiles
from database import engine
from models.base import Base
# from models.user_model import User
# from models.products import Product
# from models.farmers import Farmer
# from models.buyers import Buyer 
# from models.orders import Order
# from models.product_category import ProductCategory
from sqlalchemy.exc import OperationalError
from routes import user, organizations, auth, oauth, upload
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import logging
import time
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AuthCore App",
    version="0.0.1",
    description="authentication simplified..."
)


def db_and_table_init():
    retries = 30
    for i in range(retries):
        try:
            logger.info("Initializing database...")
            Base.metadata.create_all(bind=engine)
            logger.info("Database initialization successful.")
            break
        except Exception as e:
            logger.warning(f"MySQL NOT READY, RETRYING ({i+1}/{retries})...")
            logger.error(f"Error: {e}")
            time.sleep(3)


@app.on_event("startup")
def on_startup():
    db_and_table_init()



app.include_router(user.router)
app.include_router(organizations.router)
app.include_router(auth.router)
app.include_router(oauth.router)
app.include_router(upload.router)



app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv,
    # Set to True if your application is served over HTTPS
    https_only=False,
    # Customize other parameters like 'max_age', 'path', 'domain', etc.
)

origins = (
    "http://localhost:8000"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Allows specific origins
    allow_credentials=True, # Allows cookies to be included in cross-site requests
    allow_methods=["*"], # Allows all methods (GET, POST, PUT, PATCH DELETE)
    allow_headers=["*"], # Allows all headers, including "Authorization"
)


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Hello world"
    }