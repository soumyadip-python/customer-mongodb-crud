from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import dotenv_values
from urllib.parse import quote_plus
from src.routes import router as customer_router

config = dotenv_values(".env")

app = FastAPI()


@app.on_event("startup")
def startup_db_client():
    user = config["DB_USER"]
    password = config["DB_PASSWORD"]
    cluster = config["DB_CLUSTER"]
    dbname = config["DB_NAME"]

    user_enc = quote_plus(user)
    password_enc = quote_plus(password)

    uri = (
        f"mongodb+srv://{user_enc}:{password_enc}@{cluster}/"
        f"{dbname}?retryWrites=true&w=majority"
    )
    # print(f"Connecting to {uri}")
    client = MongoClient(uri)
    app.state.mongodb_client = client
    app.state.db = client[dbname]
    print("Connected to Mongo DB Atlas Database")


@app.on_event("shutdown")
def shutdown_db_client():
    client = getattr(app.state, "mongodb_client", None)
    if client:
        client.close()
        print("Mongo DB Atlas Client Closed")


app.include_router(customer_router, prefix="/customer", tags=["customer"])
