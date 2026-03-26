

from fastapi import FastAPI,Depends,Request
from fastapi.exceptions import RequestValidationError,HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse,FileResponse
import json
from model import User,Submit,UserTable,Submissions
from questions import QUESTIONS
from database import get_db,engine,Base
from sqlalchemy.orm import Session

app=FastAPI()
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(request.url.path)
    print(request.method)
    print(request.headers)
    return JSONResponse(
        status_code=422,
        content={
            "message": "Invalid input data",
            "errors": exc.errors()
        },
    )
Base.metadata.create_all(bind=engine)
app.mount("/static",StaticFiles(directory="static"),name="static")
@app.get("/")
def home():
    return FileResponse("static/homepage.html")


@app.get("/user/{email}")
def user(email:str,db:Session=Depends(get_db)):
   user_db=db.query(UserTable).filter(UserTable.email==email).first()
   if user_db:
       return{
           "status":"success",
           "user":user_db.model_dump()
       }
   return{
       "status":"error",
       "error_code":"404, user not found"
   }
@app.get("/form")
def form_see():
    return FileResponse("static/form.html")

@app.post("/form")
def create_user(u:User,db:Session=Depends(get_db)):
    us=db.query(UserTable).filter(UserTable.email==u.email).first()
    try:
        if us:
            return{
                "message":"user already exists"

            }
        else:
            new_user=UserTable(
                full_name=u.full_name,
                email=u.email,
                age=u.age,
                gender=u.gender,
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return{
                "message":"user created successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=422,detail=str(e))


@app.get("/quiz-page")
def get_quiz():
    return FileResponse("static/qestions.html")


@app.post("/quiz/submit")
def submit_quiz(s:Submit,db:Session=Depends(get_db)):
    existing = db.query(Submissions).filter(Submissions.email == s.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already submitted")
    responses=[]
    for i, chosen in enumerate(s.chosen_options):
        responses.append({
        "id":i+1,
        "question":QUESTIONS[i]["question"],

        "chosen_option": QUESTIONS[i]["options"][chosen]
        })

    result={
        "status":"success",
        "email":s.email,
        "responses":responses,
    }
    new_sub=Submissions(
        email=s.email,
        chosen_options=json.dumps(s.chosen_options)    
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return result





