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
async def sendText(botAPI, chatID, sendText):
    url=f'https://api.telegram.org/bot{botAPI}/sendMessage?chat_id={chatID}&text={sendText}'
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as err:
            print(f"HTTP 오류 발생: {err}")
            return None
        except httpx.RequestError as err:
            print(f"요청 오류 발생: {err}")
            return None

async def sendTextPotion(botAPI, chatID, mainText, buttonText, callback):
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
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=option)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as err:
            print(f"HTTP 오류 발생: {err}")
            return None
        except httpx.RequestError as err:
            print(f"요청 오류 발생: {err}")
            return None


""" 422응답 오류, 추후 재시도
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