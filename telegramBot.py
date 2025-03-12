import streamlit
import requests
import json

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
    response = requests.get(url=f'https://api.telegram.org/bot{inputAPI}/getUpdates')
    if response.json()['ok'] == True:
        chatID = response.json()['result'][-1]['message']['chat']['id']
        streamlit.session_state['chatID'] = chatID
        streamlit.write(f"봇 채널 ID : **{chatID}**")
    else:
        streamlit.warning(body=f"요청 실패, {response}")

text, image = streamlit.columns(spec=2, gap='small', vertical_alignment='center')
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