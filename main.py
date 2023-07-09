from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import numpy as np
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request, message='Hello, Dear'):
    #return {"message": "Hello World"}
    return templates.TemplateResponse("index.html", 
                                      {'request': request,
                                       'message': message})



def solve_quadratic_equation(a: int, b: int, c: int) -> dict:
    """
    Solves a quadratic equation of the form ax^2 + bx + c = 0 
    and returns the roots of the equation as a tuple (x1, x2)
    """

    def plot_parabola(a: int, b: int, c: int, roots: list) -> str:
        x = np.linspace(-10, 10, 400)

        y = a * x**2 + b * x + c

        # Создание графика
        fig = plt.figure()
        plt.plot(x, y)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Parabola')
        if roots:
            for root in roots:
                plt.axvline(root, color='red', linestyle='--')
                plt.text(root, (a * root**2 + b * root + c) + 5, f'({root:.1f})', verticalalignment='bottom', horizontalalignment='center')

        pngImage = io.BytesIO()
        fig.savefig(pngImage)
        pngImageB64String = base64.b64encode(pngImage.getvalue()).decode('ascii')
        
        return pngImageB64String

    discriminant = b**2 - 4*a*c
    if discriminant < 0 or a == 0:
        return {"roots": []}, plot_parabola(a,b,c, [])
    elif discriminant == 0:
        x = -b / (2*a)
        pngImageB64String = plot_parabola(a,b,c, [x])
        return {"roots": [x]}, pngImageB64String
    else:
        x1 = (-b + discriminant**0.5) / (2*a)
        x2 = (-b - discriminant**0.5) / (2*a)
        return {"roots": sorted([x1,x2])}, plot_parabola(a,b,c, [x1, x2])

@app.post("/solve")
async def plot(request: Request, numbers: str = Form(...)):
    try:
        numbers = list(map(int, numbers.split(',')))
    except:
        return {"result": "Input should be integers"}
    try:
        res, pngImageB64String = solve_quadratic_equation(*numbers)
    except:
        return {"result": "Length of input should be equal 3"}

    return templates.TemplateResponse("plot.html", 
                                      {"request": request,
                                       "numbers": numbers,
                                       "res": res,
                                       "picture": pngImageB64String})

@app.get("/solve")
async def solve_get(request: Request, a: float, b: float, c: float):
    try:
        res, _ = solve_quadratic_equation(a, b, c)
        return res
    except (TypeError, ValueError):
        return {"roots": [], "error": "Invalid input. Coefficients should be numbers."}
    

# run it: uvicorn main:app --reload --port 8080