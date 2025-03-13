import os
import requests
from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__),"templates"))

#homePage
@app.get("/",response_class=HTMLResponse)
async def home(request:Request):
    return templates.TemplateResponse("samples.html",{"request":request})

#chatID 확인
@app.post("/chatID")
async def getChatID(request:Request):
    result = await request.form()
    botAPI = result['botAPI']
    url=f'https://api.telegram.org/bot{botAPI}/getUpdates?offset=-1'
    response = requests.get(url)
    if response.json()['ok'] == True:
        chatID = response.json()['result'][-1]['message']['chat']['id']
        return HTMLResponse(content=f"<div>{chatID}</div>")
    else:
        return HTMLResponse(content=f"<div>{response}</div>")

#텍스트 데이터 전송
@app.post("/sendText")
async def getChatID(request:Request):
    result = await request.form()
    botAPI = result['botAPI']
    chatID = result['chatID']
    sendText = result['sendText']
    url=f'https://api.telegram.org/bot{botAPI}/sendMessage?chat_id={chatID}&text={sendText}'
    response = requests.get(url)
    if response:
        return HTMLResponse(content="<div>전송 완료</div>")
    else:
        return HTMLResponse(content="<div>전송 실패</div>")

#텍스트(옵션버튼 추가) 전송
@app.post("/sendTextOption")
async def getChatID(request:Request):
    result = await request.form()
    botAPI = result['botAPI']
    chatID = result['chatID']
    mainText = result['mainText']
    buttonText = result['buttonText']
    callback = result['callback']
    url=f'https://api.telegram.org/bot{botAPI}/sendMessage'
    option = {
            "chat_id": chatID,
            "text": mainText,
            "reply_markup": {
                "inline_keyboard":[
                        [
                            {"text": buttonText, "callback_data": callback}
                        ]
                    ]
                }
            }
    response = requests.get(url, json=option)
    if response:
        return HTMLResponse(content="<div>전송 완료</div>")
    else:
        return HTMLResponse(content="<div>전송 실패</div>")

#이미지 데이터 전송
@app.post("/sendImage")
async def getChatID(request:Request):
    result = await request.form()
    botAPI = result['botAPI']
    chatID = result['chatID']
    file = result['sendImage']
    url=f'https://api.telegram.org/bot{botAPI}/sendDocument'
    response = requests.get(url, data={"chat_id":chatID}, files={"document":file})
    if response:
        return HTMLResponse(content="<div>전송 완료</div>")
    else:
        return HTMLResponse(content="<div>전송 실패</div>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8501)