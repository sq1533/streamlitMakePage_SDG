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
    failResultHtml = '<div id="chatIDresult">요청 실패</div>'
    result = await telegramBotAPI.getChatID(botAPI=botAPI)
    if result and result['ok'] == True:
        chatID = result['result'][-1]['message']['chat']['id']
        return templates.TemplateResponse(request=request,name="output.html",context={'botAPI':botAPI,'chatID':chatID})
    else:
        return HTMLResponse(content=failResultHtml)

#텍스트 데이터 전송
@app.post("/sendText")
async def telebot_sendText(botAPI : str = Form(...), chatID : str = Form(...), text : str = Form(...)):
    successResultHtml = '<div id="sendTextResult">요청 성공</div>'
    failResultHtml = '<div id="sendTextResult">요청 실패</div>'
    result = await telegramBotAPI.sendText(
                                        botAPI = botAPI,
                                        chatID = chatID,
                                        text = text
                                        )
    if result and result['ok'] == True:
        return HTMLResponse(content=successResultHtml)
    else:
        return HTMLResponse(content=failResultHtml)

#텍스트_inline 데이터 전송
@app.post("/sendTextWithInline")
async def telebot_sendText_withInline(botAPI : str = Form(...), chatID : str = Form(...), text : str = Form(...), buttonText : str = Form(...), callback : str = Form(...)):
    successResultHtml = '<div id="sendTextWithLinlineResult">요청 성공</div>'
    failResultHtml = '<div id="sendTextWithLinlineResult">요청 실패</div>'
    result = await telegramBotAPI.sendText_withInline(
                                        botAPI = botAPI,
                                        chatID = chatID,
                                        text = text,
                                        buttonText=buttonText,
                                        callback=callback
                                        )
    if result and result['ok'] == True:
        return HTMLResponse(content=successResultHtml)
    else:
        return HTMLResponse(content=failResultHtml)

"""
@app.get("/add_input{count}")
def add_input(count:int):
    replyMarkup = f"input_html"
    if count < 6:
        return HTMLResponse(content=replyMarkup)
    else:
        return HTMLResponse(content=f"<div>최대 5개 추가</div>")

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