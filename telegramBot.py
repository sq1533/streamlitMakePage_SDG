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

@app.post("/chatID")
async def getChatID(request:Request):
    result = await request.form()
    botAPI = result['botAPI']
    url=f'https://api.telegram.org/bot{botAPI}/getUpdates?offset=-1'
    response = requests.get(url)
    chatID = response.json()['result'][-1]['message']['chat']['id']
    return HTMLResponse(content=f"<div>{chatID}</div>")

@app.post("/sendText")
async def getChatID(request:Request):
    result = await request.form()
    botAPI = result['botAPI']
    chatID = result['chatID']
    sendText = result['sendText']
    url=f'https://api.telegram.org/bot{botAPI}/sendMessage?chat_id={chatID}&text={sendText}'
    requests.get(url)
    return HTMLResponse(content="<div>전송 완료</div>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8501)
"""
streamlit.set_page_config(
                        page_title='howToUsed_telegramBot-API',
                        page_icon='',
                        layout='wide',
                        initial_sidebar_state='collapsed'
                        )

streamlit.header(body="telegramBot_API 활용")

#텔레그램 봇 API 채널 확인
streamlit.subheader(body="telegramBot chatID값 확인하기")

inputAPI = streamlit.text_input(
                                label='bot_API',
                                value='',
                                key='botAPI_chatID',
                                placeholder='telegramBotAPI 입력',
                                label_visibility='visible'

                                )

if streamlit.button(label='조회',key='chatIDButton'):
    streamlit.session_state['botAPI'] = inputAPI
    response = requests.get(url=f'https://api.telegram.org/bot{inputAPI}/getUpdates?offset=-1')
    if response.json()['ok'] == True:
        chatID = response.json()['result'][-1]['message']['chat']['id']
        streamlit.write(f"봇 채널 ID : **{chatID}**")
    else:
        streamlit.warning(body=f"요청 실패, {response}")

text, image = streamlit.columns(spec=2, gap='small', vertical_alignment='center')
textOption, dd = streamlit.columns(spec=2, gap='small', vertical_alignment='center')

#텔레그램 봇 API 데이터 보내기
with text.container():
    streamlit.subheader(body="text 데이터 전송")
    API, chatID = streamlit.columns(spec=[3,1], gap='small', vertical_alignment='center')

    bot_API = API.text_input(
                            label='bot_API',
                            value='',
                            key='botAPI_sendText',
                            label_visibility='visible'
                            )
    
    chat_id = chatID.text_input(
                                label='chatID',
                                value='',
                                key='chatID_sendText',
                                label_visibility='visible'
                                )
    
    textData = streamlit.text_area(
                                    label='text입력',
                                    value='',
                                    key='value_sendText',
                                    label_visibility='visible'
                                    )
    
    if streamlit.button(label='전송',key='sendText'):
        response = requests.get(url=f'https://api.telegram.org/bot{bot_API}/sendMessage?chat_id={chat_id}&text={textData}')
        if response:
            streamlit.write('전송 성공')
        else:
            streamlit.write(f'전송 실패, {response}')

#이미지 전송
with image.container():
    streamlit.subheader(body="이미지 데이터 전송")
    API, chatID = streamlit.columns(spec=[3,1], gap='small', vertical_alignment='center')

    bot_API = API.text_input(
                            label='bot_API',
                            value='',
                            key='botAPI_sendImage',
                            label_visibility='visible'
                            )
    
    chat_id = chatID.text_input(
                                label='chatID',
                                value='',
                                key='chatID_sendImage',
                                label_visibility='visible'
                                )

    file = streamlit.file_uploader(
                                    label='image',
                                    type=['jpg','jpeg','png'],
                                    help='200MB이하, JPG 및 JPEG, PNG 파일',
                                    accept_multiple_files=False,
                                    key='value_sendImage',
                                    label_visibility='visible'
                                    )

    if streamlit.button(label='전송',key='sendImage'):
        response = requests.post(url=f'https://api.telegram.org/bot{bot_API}/sendDocument', data={"chat_id":chat_id}, files={"document":file})
        if response:
            streamlit.write('전송 성공')
        else:
            streamlit.write(f'전송 실패, {response}')

#텍스트(옵션추가) 전송
with textOption.container():
    streamlit.subheader(body="텍스트(옵션추가) 데이터 전송")
    API, chatID = streamlit.columns(spec=[3,1], gap='small', vertical_alignment='center')
    titleText, optionText = streamlit.columns(spec=2, gap='small', vertical_alignment='center')

    bot_API = API.text_input(
                            label='bot_API',
                            value='',
                            key='botAPI_sendTextoption',
                            label_visibility='visible'
                            )

    chat_id = chatID.text_input(
                                label='chatID',
                                value='',
                                key='chatID_sendTextoption',
                                label_visibility='visible'
                                )
    
    title = titleText.text_input(
                                label='메세지 내용 입력',
                                value='',
                                key='botAPI_titleTextoption',
                                label_visibility='visible'
                                )

    option = optionText.text_input(
                                label='버튼 내용 입력',
                                value='',
                                key='botAPI_optionTextoption',
                                label_visibility='visible'
                                )

    option = {
            "chat_id": chat_id,
            "text": title,
            "reply_markup": {
                "inline_keyboard":[
                        [
                            {"text": option, "callback_data": "callback"}
                        ]
                    ]
                }
            }

    if streamlit.button(label='전송',key='sendTextoption'):
        response = requests.post(url=f'https://api.telegram.org/bot{bot_API}/sendMessage', json=option)
        if response:
            streamlit.write('전송 성공')
        else:
            streamlit.write(f'전송 실패, {response}')
"""