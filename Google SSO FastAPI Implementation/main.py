from fastapi import FastAPI, Request
from authlib.integrations.starlette_client import OAuth
import jwt
from starlette.config import Config
from datetime import datetime, timedelta
from starlette.middleware.sessions import SessionMiddleware


config = Config(".env")

app= FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="1234"
)

oauth = OAuth(config)


oauth.register(
    name="google",
    client_id=config("Client_id"),
    client_secret=config("Client_sec"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope":"openid email profile"
    }
)

JWT_SECRET = config("jwt_sec")


def create_jwt(email):
    email="Enter Your email here..."
    payload={
        "sub":email,
        "exp": datetime.utcnow()+timedelta(hours=1)
    }
    
    token=jwt.encode(
        payload,
        JWT_SECRET,
        algorithm ="HS256"
    )
    
    return token

@app.get("/")
async def home():
    return {
        "message":"FastAPI google SSO Demo"
    }
    
@app.get("/login/google")
async def login_google(request:Request):
    redirect_url = request.url_for("google_callback")
    
    
    return await oauth.google.authorize_redirect(request,redirect_url)

@app.get("/auth/google/callback")
async def google_callback(request:Request):
    token= await oauth.google.authorize_access_token(request)
    
    user=token["userinfo"]
    jwt_token=create_jwt(
        user["email"]
    )
    
    return {
        "email":user["email"],
        "name":user["name"],
        "picture":user["picture"],
        "jwt_token":jwt_token
    }
