from fastapi import FastAPI, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import text
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import shutil
import os

from database import engine, SessionLocal
from models import Base, Admin
from schemas import AdminCreate

# =========================
# CREATE TABLES
# =========================
Base.metadata.create_all(bind=engine)

# =========================
# APP
# =========================
app = FastAPI()

templates = Jinja2Templates(directory="templates")

# =========================
# CREATE FOLDERS
# =========================
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/reviews", exist_ok=True)

# =========================
# STATIC FILES
# =========================
app.mount("/static", StaticFiles(directory="static"), name="static")

# =========================
# AUTH
# =========================
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)


def create_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(hours=2)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(request: Request):
    try:
        token = request.cookies.get("token")

        if not token:
            raise HTTPException(status_code=401, detail="Not logged in")

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# =========================
# HOME PAGE
# =========================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index1.html"
    )


# =========================
# DONATE
# =========================
@app.get("/donate", response_class=HTMLResponse)
def donate_us(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="donate.html"
    )


# =========================
# DEVELOPER
# =========================
@app.get("/developer", response_class=HTMLResponse)
def developer(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="developer.html"
    )


# =========================
# ABOUT US
# =========================
@app.get("/aboutus", response_class=HTMLResponse)
def aboutus(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="aboutus.html"
    )


# =========================
# COMMITTEE
# =========================
@app.get("/committee", response_class=HTMLResponse)
def committee(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="committee.html"
    )


# =========================
# FAQ
# =========================
@app.get("/faq", response_class=HTMLResponse)
def faq(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="faq.html"
    )


# =========================
# REGISTER PAGE
# =========================
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )


# =========================
# SUBMIT REGISTRATION
# =========================
@app.post("/submit_registration")
def submit_registration(
    name: str = Form(...),
    age: int = Form(...),
    mobile: str = Form(...),
    address: str = Form(...),
    district: str = Form(...),
    state: str = Form(...),
    health_problem: str = Form(None)
):

    if len(mobile.strip()) != 10:
        return {"error": "Mobile number must be 10 digits"}

    with engine.connect() as conn:

        conn.execute(
            text("""
            INSERT INTO users
            (name, age, mobile, address, district, state, health_problem)
            VALUES
            (:n, :a, :m, :ad, :d, :s, :h)
            """),
            {
                "n": name,
                "a": age,
                "m": mobile,
                "ad": address,
                "d": district,
                "s": state,
                "h": health_problem
            }
        )

        conn.commit()

    return {"message": "Registration Successful"}


# =========================
# GALLERY
# =========================
@app.get("/gallery", response_class=HTMLResponse)
def gallery(request: Request):

    images = os.listdir("static/uploads")

    return templates.TemplateResponse(
        request=request,
        name="gallery.html",
        context={
            "request": request,
            "images": images
        }
    )


# =========================
# LOGIN PAGE
# =========================
@app.get("/login-page", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


# =========================
# REGISTER ADMIN
# =========================
@app.post("/register-admin")
def register(admin: AdminCreate):

    db = SessionLocal()

    try:

        existing = db.query(Admin).filter(
            Admin.email == admin.email
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        hashed = hash_password(admin.password)

        new_admin = Admin(
            name=admin.name,
            email=admin.email,
            password=hashed,
            role="admin",
            is_approved=False
        )

        db.add(new_admin)

        db.commit()

        return {
            "message": "Admin registered successfully"
        }

    finally:
        db.close()


# =========================
# LOGIN
# =========================
@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):

    db = SessionLocal()

    try:

        admin = db.query(Admin).filter(
            Admin.email == email
        ).first()

        if not admin:
            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={
                    "request": request,
                    "error": "Admin not found"
                }
            )

        if not verify_password(password, admin.password):
            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={
                    "request": request,
                    "error": "Wrong password"
                }
            )

        token = create_token({
            "admin_id": admin.id,
            "role": admin.role
        })

        response = RedirectResponse(
            url="/admin_dashboard",
            status_code=303
        )

        response.set_cookie(
            key="token",
            value=token,
            httponly=True
        )

        return response

    finally:
        db.close()


# =========================
# DASHBOARD
# =========================
@app.get("/admin_dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    user=Depends(verify_token)
):

    with engine.connect() as conn:

        users = conn.execute(
            text("SELECT COUNT(*) FROM users")
        ).scalar()

        reviews = conn.execute(
            text("SELECT COUNT(*) FROM reviews")
        ).scalar()

        branches = conn.execute(
            text("SELECT COUNT(*) FROM branches")
        ).scalar()

    photos = len(os.listdir("static/uploads"))

    today = datetime.now().strftime(
        "%d %B %Y | %I:%M %p"
    )

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "request": request,
            "users": users,
            "reviews": reviews,
            "branches": branches,
            "photos": photos,
            "today": today
        }
    )


# =========================
# LOGOUT
# =========================
@app.get("/logout")
def logout():

    response = RedirectResponse(
        url="/login-page",
        status_code=303
    )

    response.delete_cookie("token")

    return response
