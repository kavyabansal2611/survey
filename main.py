

from fastapi import FastAPI,Depends,Request
from fastapi.exceptions import RequestValidationError,HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse,FileResponse
import json
from model import User,Submit,UserTable,Submissions
from questions import QUESTIONS
from database import get_db,engine,Base
from sqlalchemy.orm import Session
from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

app=FastAPI()
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])


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
def custom_key_func(request: Request):
    user_ip = request.headers.get("X-Forwarded-For", request.client.host)
    user_id=request.headers.get("id","anonymous")
    user_api_key=request.headers.get("api_key","no-key")
    return f"{user_ip}:{user_id}:{user_api_key}"


limiter=Limiter(key_func=custom_key_func)
app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)


@app.get("/")
@limiter.limit("10/minute")
def home(request: Request):
    return FileResponse("static/homepage.html")


@app.get("/user/{email}")
@limiter.limit("20/minute")
def user(request:Request,email:str,db:Session=Depends(get_db)):
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
@limiter.limit("10/minute")
def form_see(request:Request):
    return FileResponse("static/homepage.html")

@app.post("/form")
@limiter.limit("10/minute")
def create_user(request:Request,u:User,db:Session=Depends(get_db)):

    us=db.query(UserTable).filter(UserTable.email==u.email).first()
    print(us)
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
        db.rollback()
        raise HTTPException(status_code=422,detail=str(e))
    print(exc.errors())


@app.get("/quiz-page")
@limiter.limit("10/minute")
def get_quiz(request:Request):
    return FileResponse("static/homepage.html")


@app.post("/quiz/submit")
@limiter.limit("20/minute")
def submit_quiz(request:Request,s:Submit,db:Session=Depends(get_db)):
    existing = db.query(Submissions).filter(Submissions.email == s.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already submitted")
    try:
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
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=422,detail=str(e))
@app.get("/quiz/results")
@limiter.limit("20/minute")
def get_quiz_results(request:Request,db:Session=Depends(get_db)):
    results=db.query(Submissions,UserTable)\
    .join(UserTable,UserTable.email==Submissions.email)\
    .all()
    if not results:
        raise HTTPException(status_code=404, detail="No results")
    male_scores=[]
    female_scores=[]
    other_score=[]
    other_score = [0] * 15
    for i in range(15):
        male_scores.append(0)
    for i in range(15):
        female_scores.append(0)
    male_count=0
    female_count=0
    other_count=0
    for sub,user in results:
        if user.gender=="M":
            answers = json.loads(sub.chosen_options)
            for i in range(15):
                male_scores[i] += answers[i]
            male_count += 1
        elif user.gender=="F":
            answers = json.loads(sub.chosen_options)
            for i in range(15):
                female_scores[i] += answers[i]
            female_count += 1
            for i in range(15):
                other_score[i] += answers[i]
            other_count += 1
        for i in range(15):
            male_avg=round(male_scores[i]/male_count,2) if male_count else 0
            female_avg=round(female_scores[i]/female_count,2) if female_count else 0
    final_results=[]
    for i in range(15):
        final_results.append({
            "question": QUESTIONS[i]["question"],
            "male_avg": male_avg,
            "female_avg": female_avg,

        })

    return final_results

@app.get("/")
@limiter.limit("20/minute")
def health():
    return {"status": "alive"}







