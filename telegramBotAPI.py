import httpx

#텔레그램 봇 chat ID 확인
async def getChatID(botAPI):
    url=f'https://api.telegram.org/bot{botAPI}/getUpdates?offset=-1'
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url=url)
            return response.json()
        except:
            return None
        
#텔레그램 봇 text 전송
async def sendText(botAPI=str, chatID=str, text=str):
    url=f'https://api.telegram.org/bot{botAPI}/sendMessage'
    data = {
        "chat_id": chatID,
        "text": text,
        "parse_mode": "markdownV2",
        "disable_notification": False,
        "protect_content": True,
        "allow_paid_broadcast": False
        }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as err:
            print(f"HTTP 오류 발생: {err}")
            return None
        except httpx.RequestError as err:
            print(f"요청 오류 발생: {err}")
            return None

#텔레그램 봇 text_with_inline 전송
async def sendText_withInline(botAPI=str, chatID=str, text=str, buttonText=str, callback=str):
    url=f'https://api.telegram.org/bot{botAPI}/sendMessage'
    replyMarkup = {"inline_keyboard":[[{"text": buttonText, "url": callback}]]}
    data = {
        "chat_id": chatID,
        "text": text,
        "parse_mode": "markdownV2",
        "disable_notification": False,
        "protect_content": True,
        "allow_paid_broadcast": False,
        "reply_markup": replyMarkup
        }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as err:
            print(f"HTTP 오류 발생: {err}")
            return None
        except httpx.RequestError as err:
            print(f"요청 오류 발생: {err}")
            return None
"""
#봇 /sendMessage API
data = {
    "business_connection_id": businessConnectionID, #비즈니스 연결 ID(Business connection ID)
    "chat_id": chatID,
    "message_thread_id": messageThreadID, #메시지 스레드 ID(Message thread ID)
    "text": text,
    "parse_mode": "markdownV2", #텍스트 메시지를 파싱하는 방식을 지정합니다. HTML / markdownV2
    "entities": entities, #텍스트 메시지 내의 특정 부분에 대한 정보를 지정합니다. 예를 들어, 멘션, 해시태그, URL 등을 지정할 수 있습니다.
    "link_preview_options": linkPreviewOptions, #링크 미리보기 옵션.
    "disable_notification": False, #True로 설정하면 메시지를 보낼 때 사용자에게 알림을 보내지 않습니다.
    "protect_content": True, #True로 설정하면 메시지의 내용을 보호합니다.
    "allow_paid_broadcast": False, #True로 설정하면 유료 방송을 허용합니다.
    "message_effect_id": messageEffectId, #메시지 효과 ID
    "reply_parameters": replyParameters, #답장 파라미터
    "reply_markup": replyMarkup #메시지에 추가할 키보드를 지정합니다.
    }

async def sendPhoto(botAPI, chatID, photo):
    url = f"https://api.telegram.org/bot{botAPI}/sendPhoto"
    files = {
        "photo":(
            "photo.jpg",
            photo,
            "image/jpeg"
            )
        }
    data = {
        "chat_id":chatID,
        "caption": None
        }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as err:
            print(f"HTTP 오류 발생: {err}")
            return None
        except httpx.RequestError as err:
            print(f"요청 오류 발생: {err}")
            return None
"""