import streamlit
import requests
import json

streamlit.set_page_config(
                        page_title='howToUsed_telegramBot-API',
                        page_icon='',
                        layout='wide',
                        initial_sidebar_state='collapsed',
                        menu_items={
                                    'telegramBotAPI':'https://core.telegram.org/bots'
                                    }
                        )

#세션관리
if 'botAPI' not in streamlit.session_state:
    streamlit.session_state['botAPI'] = None
if 'chatID' not in streamlit.session_state:
    streamlit.session_state['chatID'] = None

streamlit.header(body="telegramBot_API 활용")

#텔레그램 봇 API 채널 확인
streamlit.subheader(body="telegramBot chatID값 확인하기")

inputAPI = streamlit.text_input(label='bot_API',
                     value='',
                     key='botAPI_chatID',
                     placeholder='telegramBotAPI 입력',
                     label_visibility='visible')

if streamlit.button(label='조회',key='chatID'):
    streamlit.session_state['botAPI'] = inputAPI
    response = requests.get(url=f'https://api.telegram.org/bot{inputAPI}/getUpdates')
    if response.json()['ok'] == True:
        chatID = response.json()['result'][-1]['message']['chat']['id']
        streamlit.session_state['chatID'] = chatID
        streamlit.write(f"봇 채널 ID : **{chatID}**")
    else:
        streamlit.warning(body=f"요청 실패, {response}")

streamlit.code(body=
                """
                inputAPI = streamlit.text_input(label='bot_API',
                                                value='',
                                                key='botAPI_chatID',
                                                placeholder='telegramBotAPI 입력')

                if streamlit.button(label='조회',key='chatID'):
                    response = requests.get(url=f'https://api.telegram.org/bot{inputAPI}/getUpdates')
                    if response.json()['ok'] == True:
                        chatID = response.json()['result'][-1]['message']['chat']['id']
                        streamlit.write(f"봇 채널 ID : **{chatID}**")
                    else:
                        streamlit.warning(body=f"요청 실패, {response}")
                """)

#텔레그램 봇 API text보내기
streamlit.subheader(body="telegramBot Text 데이터 전송")
with streamlit.expander(label='Text 데이터 전송'):
    API, chatID = streamlit.columns(spec=[3,1], gap='small', vertical_alignment='center')

    bot_API = API.text_input(label='bot_API',
                   value=streamlit.session_state['botAPI'],
                   key='botAPI_sendText',
                   label_visibility='visible')
    
    chat_id = chatID.text_input(label='chatID',
                   value=streamlit.session_state['chatID'],
                   key='chatID_sendText',
                   label_visibility='visible')
    
    textData = streamlit.text_input(label='text입력',
                   value='',
                   key='value_sendText',
                   label_visibility='visible')
    
    if streamlit.button(label='전송',key='sendText'):
        response = requests.get(url=f'https://api.telegram.org/bot{bot_API}/sendMessage?chat_id={chat_id}&text={textData}')
        if response:
            streamlit.write('전송 성공')
        else:
            streamlit.write(f'전송 실패, {response}')

    streamlit.code(body=
                    """
                    requests.post(url=f'https://api.telegram.org/bot{bot_API}/sendMessage?chat_id={chat_id}&text={textData}')
                    """)

#이미지 전송
streamlit.subheader(body="telegramBot 이미지 데이터 전송")
with streamlit.expander(label='이미지 데이터 전송'):
    API, chatID = streamlit.columns(spec=[3,1], gap='small', vertical_alignment='center')

    bot_API = API.text_input(label='bot_API',
                   value=streamlit.session_state['botAPI'],
                   key='botAPI_sendImage',
                   label_visibility='visible')
    
    chat_id = chatID.text_input(label='chatID',
                   value=streamlit.session_state['chatID'],
                   key='chatID_sendImage',
                   label_visibility='visible')

    file = streamlit.file_uploader(label='image',
                                   type=['jpg','jpeg','png'],
                                   help='200MB이하, JPG 및 JPEG, PNG 파일',
                                   accept_multiple_files=False,
                                   key='value_sendImage',
                                   label_visibility='visible')

    if streamlit.button(label='전송',key='sendImage'):
        response = requests.post(url=f'https://api.telegram.org/bot{bot_API}/sendDocument', data={"chat_id":chat_id}, files={"document":file})
        if response:
            streamlit.write('전송 성공')
        else:
            streamlit.write(f'전송 실패, {response}')

    streamlit.code(body=
                    """
                    requests.post(url=f'https://api.telegram.org/bot{bot_API}/sendDocument', data={"chat_id":chat_id}, files={"document":file})
                    """)