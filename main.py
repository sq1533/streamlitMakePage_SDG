import os
import requests
from fastapi import FastAPI, Request, UploadFile, Form, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import telegramBotAPI

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__),"templates"))

#homePage
@app.get("/",response_class=HTMLResponse)
async def home(request:Request):
    return templates.TemplateResponse("samples.html",{"request":request})

#chatID 확인
@app.post("/chatID")
async def ChatID(request : Request, botAPI : str = Form(...)):
    result = await telegramBotAPI.getChatID(botAPI=botAPI)
    if result and result['ok'] == True:
        chatID = result['result'][-1]['message']['chat']['id']
        return templates.TemplateResponse(request=request,name="output.html",context={'botAPI':botAPI,'chatID':chatID})
    else:
        return HTMLResponse(content=f"<div>요청 실패</div>")

#텍스트 데이터 전송
@app.post("/sendText")
async def telebot_sendText(request : Request, botAPI : str = Form(...), chatID : str = Form(...), sendText : str = Form(...)):
    result = await telegramBotAPI.sendText(botAPI=botAPI, chatID=chatID, sendText=sendText)
    if result and result['ok'] == True:
        return templates.TemplateResponse(request=request,name="output.html",context={'botAPI':botAPI,'chatID':chatID})
    else:
        return HTMLResponse(content=f"<div>요청 실패</div>")

#텍스트(옵션버튼 추가) 전송
@app.post("/sendTextOption")
async def telebot_sendText_Option(botAPI : str = Form(...), chatID : str = Form(...), mainText : str = Form(...), buttonText : str = Form(...), callback : str = Form(...)):
    result = await telegramBotAPI.sendTextPotion(botAPI=botAPI, chatID=chatID, mainText=mainText, buttonText=buttonText, callback=callback)
    if result and result['ok'] == True:
        return HTMLResponse(content="<div>전송 완료</div>")
    else:
        return HTMLResponse(content=f"<div>요청 실패</div>")

""" 422응답 오류, 추후 재시도
#이미지 데이터 전송
@app.post("/sendImage")
async def getChatID(botAPI : str = Form(...), chatID : str = Form(...), sendImage : UploadFile = File(...)):
    photo = await sendImage.read()
    result = await telegramBotAPI.sendPhoto(botAPI=botAPI, chatID=chatID, photo=photo)
    if result and result['ok'] == True:
        return HTMLResponse(content="<div>전송 완료</div>")
    else:
        return HTMLResponse(content=f"<div>요청 실패</div>")
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8501)