import streamlit as st
import pyrebase
from email_validator import validate_email, EmailNotValidError
import smtplib
from email.message import EmailMessage
import re
import requests.exceptions
import json
import firebase_admin
from firebase_admin import auth, credentials, firestore


"""
# FireBase secret_keys
secretKeyPath = {
    "type" : st.secrets["firebaseKey"]["type"],
    "project_id" : st.secrets["firebaseKey"]["project_id"],
    "private_key_id" : st.secrets["firebaseKey"]["private_key_id"],
    "private_key" : st.secrets["firebaseKey"]["private_key"],
    "client_email" : st.secrets["firebaseKey"]["client_email"],
    "client_id" : st.secrets["firebaseKey"]["client_id"],
    "auth_uri" : st.secrets["firebaseKey"]["auth_uri"],
    "token_uri" : st.secrets["firebaseKey"]["token_uri"],
    "auth_provider_x509_cert_url" : st.secrets["firebaseKey"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url" : st.secrets["firebaseKey"]["client_x509_cert_url"],
    "universe_domain" : st.secrets["firebaseKey"]["universe_domain"]
    }

# Firebase 앱이 이미 초기화되었는지 확인
if not firebase_admin._apps:
    try:
        path = credentials.Certificate(cert=secretKeyPath)
        firebase_admin.initialize_app(credential=path)
        print("FireBase Admin SDK 앱 초기화 완료 (from utils.py)")
    except Exception as e:
        print(f"Firebase Admin SDK 초기화 오류 in utils.py: {e}")
"""

# Firebase 사용자 keys
firebaseWebConfig = {
    "apiKey" : st.secrets["firebaseWebConfig"]["apiKey"],
    "authDomain" : st.secrets["firebaseWebConfig"]["authDomain"],
    "projectId" : st.secrets["firebaseWebConfig"]["projectId"],
    "storageBucket" : st.secrets["firebaseWebConfig"]["storageBucket"],
    "messagingSenderId" : st.secrets["firebaseWebConfig"]["messagingSenderId"],
    "appId" : st.secrets["firebaseWebConfig"]["appId"],
    "databaseURL" : "https://shop-demo-5d78e-default-rtdb.firebaseio.com"
    }

# pyrebase - firebase 연결
firebase = pyrebase.initialize_app(config=firebaseWebConfig)

# database
class database:
    def __init__(self):
        self.pyrebase_auth = firebase.auth() # 회원 인증
        self.pyrebase_db_user = firebase.database().child('user') # 회원 정보 db
        self.pyrebase_db_items = firebase.database().child('items') # items 정보 db
        self.pyrebase_db_itemStatus = firebase.database().child('itemStatus') # itemStatus 정보 db
        self.pyrebase_db_orderList = firebase.database().child('orderList') # orderList 정보 db
        self.pyrebase_db_UIUX = firebase.database().child('UIUX') # UIUX 정보 db


# guest 관리
class guest(database):
    # 회원 가입 전 중복 이메일 검증
    def emailCheck(id : str):
        try:
            # 이메일 형식 확인
            if validate_email(id, check_deliverability=True, timeout=5)['email'] == id:
                # 가입 유무 확인 > 미가입, 가입 미인증, 가입 인증
                pathID = id.replace('@','_-A_-').replace('.','_-D_-')
                lookUPemail = database().pyrebase_db_user.child(pathID).get().val()
                if lookUPemail is None or not lookUPemail:
                    return {'allow' : True, 'result' : pathID}
                else:
                    return {'allow' : False, 'result' : '이미 가입한 이메일입니다.'}
            else:
                return {'allow' : False, 'result' : '이메일 형식이 잘못되었습니다.'}
        except EmailNotValidError as e:
            return {'allow' : False, 'result' : f'이메일 검증 오류 {e}'}
        except Exception as e:
            return {'allow' : False, 'result' : f'예기치 못한 오류 {e}'}
    
    # 회원 가입 db 연동
    def signUP(id : str, pw : str, userInfo):
        try:
            database().pyrebase_auth.create_user_with_email_and_password(email=id, password=pw)
            database().pyrebase_db_user.child(id).set(userInfo)
            return True
        except Exception as e:
            print(f"가입 시도 중 예상치 못한 오류 발생: {e}")
            return False

    # 로그인
    def signIN(id : str, pw : str):
        try:
            user = database().pyrebase_auth.sign_in_with_email_and_password(email=id, password=pw)
            userInfo = database().pyrebase_db_user.child(user['email']).get().val()
            return userInfo
        except Exception as e:
            print(f'로그인 실패 {e}')
            return False

    # 로그아웃
    def signOUT():
        try:
            return st.session_state.clear
        except Exception as e:
            print(f'로그아웃 실패 {e}')
            return False

    def PWlaterChange(id : str, date : str):
        try:
            results = {
                'createPW' : date
            }
            database().pyrebase_db_user.child(id).update(results)
            return True
        except Exception as e:
            print(f'비밀번호 연장 실패 {e}')
            return False
    
    # 회원 탈퇴
    def guestOUT():
        pass


class items(database):
    # 아이템 수량 및 상태    
    def itemStatus(itemId : str):
        try:
            itemStatus = database().pyrebase_db_itemStatus.child(itemId).get().val() # 아이템 상태 조회
            return itemStatus
        except Exception as e:
            print(f'아이템 상태 조회 실패 {e}')
            return False
    
    # 아이템 ID 리스트
    def itemsIdList():
        itemsId_dict = database().pyrebase_db_items.get().val() # 아이템 키값 dict {'items1':True}
        itemsId = list(itemsId_dict.keys()) # 아이템 키값 list
        return itemsId

    # 아이템 like 상태 (고객 info로 따라감)
    def itemsLike(id : str, userInfo : dict, like : str):
        try:
            if like in userInfo['like']:
                userInfo['like'].remove(like)
                results = {
                    'like' : userInfo['like']
                }
                database().pyrebase_db_user.child(id).update(results)
                return True
            else:
                userInfo['like'].append(like)
                results = {
                    'like' : userInfo['like']
                }
                database().pyrebase_db_user.child(id).update(results)
                return True
        except Exception as e:
            print(f'like 실패 {e}')
            return False

    # 아이템 구매 및 상태 변경
    def itemOrder(id : str, itemId : str):
        try:
            userInfo = database().pyrebase_db_user.child(id)
            orderList = userInfo.get()['orderList']
            orderResults = orderList.append(itemId)
            userResults = {
                'orderList' : orderResults
            }
            userInfo.update(userResults) # 고객 주문 내역에 추가
            itemStatus = database().pyrebase_db_itemStatus.child(itemId) # 아이템 수량 변경
            countResults = int(itemStatus.get()['count']) - 1
            if countResults < 4:
                itemResults = {
                    'count' : countResults,
                    'enable' : False
                }
                itemStatus.update(itemResults)
                return True
            else:
                itemResults = {
                    'count' : countResults
                }
                itemStatus.update(itemResults)
                return True
        except Exception as e:
            print(f'상품 주문 실패 {e}')
            return False


# 주소 검색
def seachAddress(address : str):
    sqlInjection = ["OR", "SELECT", "INSERT", "DELETE", "UPDATE", "CREATE", "DROP", "EXEC", "UNION",  "FETCH", "DECLARE", "TRUNCATE"]
    if re.search(r"[\]\[%;<>=]", address):
        st.error(body="특수문자는 포함할 수 없습니다.")
    elif any(i in address.upper() for i in sqlInjection):
        st.error(body="포함할 수 없는 단어가 존재합니다.")
    else:
        addressKey = {
            "confmKey" : st.secrets["address_search"]["keys"],
            "currentPage" : 1,
            "countPerPage" : 10,
            "keyword" : address,
            "resultType" : "json"
        }
        try:
            response = requests.post("https://business.juso.go.kr/addrlink/addrLinkApi.do", data=addressKey)
            if response.status_code == 200:
                addrLen = response.json()["results"]["juso"].__len__()
                if addrLen == 0:
                    return '검색 결과가 없습니다. 주소를 다시 확인해주세요.'
                else:
                    for i in range(addrLen):
                        st.write(response.json()["results"]["juso"][i]["zipNo"])
                        st.write(response.json()["results"]["juso"][i]["roadAddr"])
                        choise = st.button(
                            label="선택",
                            key=f"choise{i}"
                        )
                        if choise:
                            return response.json()['results']['juso'][i]['roadAddr']
        except Exception as e:
            st.error(f'주소 검색 실패 {e}')
            return False

"""
# 인증 이메일 검증
def sendEmail(userMail: str) -> bool:
    SENDER_EMAIL = st.secrets["email_credentials"]["sender_email"]
    SENDER_APP_PASSWORD = st.secrets["email_credentials"]["sender_password"]
    SENDER_SERVER = st.secrets["email_credentials"]["smtp_server"]
    SENDER_PORT = st.secrets["email_credentials"]["smtp_port"]
    DEPLOYED_BASE_URL = st.secrets["email_credentials"]["base_url"]

    settingCode = auth.ActionCodeSettings(
        url=f"{DEPLOYED_BASE_URL}/success?email={userMail}",
        handle_code_in_app=True
    )

    link = auth.generate_email_verification_link(
        email=userMail,
        action_code_settings=settingCode
    )

    msg = EmailMessage()
    msg['Subject'] = "회원가입 이메일 인증"
    msg['From'] = SENDER_EMAIL
    msg['To'] = userMail
    msg.set_content(f""
안녕하세요!

회원가입을 완료하려면 아래 링크를 클릭하여 이메일 주소를 인증해주세요:

{link}

이 링크는 일정 시간 후에 만료될 수 있습니다.

감사합니다.
"")
    try:
        with smtplib.SMTP(SENDER_SERVER, SENDER_PORT) as smtp_server:
            smtp_server.ehlo() # 서버에 자신을 소개
            smtp_server.starttls() # TLS 암호화 시작
            smtp_server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            smtp_server.send_message(msg)
        print(f"인증 이메일이 {userMail} 주소로 성공적으로 발송되었습니다.")
        return True
    except smtplib.SMTPAuthenticationError:
        print("오류: SMTP 인증 실패.")
        return False
    except smtplib.SMTPServerDisconnected:
        print("오류: SMTP 서버 연결 끊김.")
        return False
    except Exception:
        print("오류: 이메일 발송 중 예상치 못한 오류")
        return False


# firestore 연결
db = firestore.client()
logoDB = db.collection('logo') # 로고 정보 가져오기
itemsDB = db.collection('items') # items 컬렉션 연결
userInfoDB = db.collection('userInfo')
orderDB = db.collection('orderList')

# 상품 추가 함수
def addItem(item_data, item_id):
    try:
        if item_id:
            item_data_to_set = item_data.copy()
            item_data_to_set['id'] = item_id
            itemsDB.document(item_id).set(item_data_to_set)
            print(f"상품 '{item_id}'이(가) Firestore에 성공적으로 설정되었습니다.")
            return item_id
        else:
            print("상품 ID 미지정, 실패")
            return None
    except Exception as e:
        print(f"Firestore에 상품을 추가/설정하는 중 오류 발생: {e}")
        return None

# 사용자 orders status 수정_배송중
def deliveryStatus(orderStatus:list):
    try:
        allUsers = userInfoDB.stream()
        for user in allUsers:
            orderLists = user.get().to_dict()["orders"]
            for orderList in orderLists:
                if orderList in orderStatus:
                    orderDelivery = orderList + "/" + "delivery"
                    orderLists.remove(orderList)
                    orderLists.append(orderDelivery)
                else:
                    pass
            userInfoDB.document(user.id).update({"orders":orderLists})
    except Exception:
        print("배송 상태 업데이트 오류")

# 사용자 orders status 수정_완료
def completeStatus(orderStatus:list):
    try:
        allUsers = userInfoDB.stream()
        for user in allUsers:
            orderLists = user.get().to_dict()["orders"]
            for orderList in orderLists:
                if orderList in orderStatus:
                    orderComplete = orderList.replace("delivery", "complete")
                    orderLists.remove(orderList)
                    orderLists.append(orderComplete)
                else:
                    pass
            userInfoDB.document(user.id).update({"orders":orderLists})
    except Exception:
        print("완료 상태 업데이트 오류")
"""