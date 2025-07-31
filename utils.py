import streamlit as st
import pyrebase
from email_validator import validate_email, EmailNotValidError
import re
import requests

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
    def emailCheck(id : str) -> dict:
        try:
            # 이메일 형식 확인
            if validate_email(id, check_deliverability=True, timeout=5)['email'] == id:
                # 가입 유무 확인 > 미가입, 가입 미인증, 가입 인증
                pathID = id.replace('@','__aA__').replace('.','__dD__')
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
    
    # 인증 메일 전송
    def sendEmail(id : str, pw : str) -> bool:
        try:
            user = database().pyrebase_auth.sign_in_with_email_and_password(email=id, password=pw)
            database().pyrebase_auth.send_email_verification(user['idToken'])
            return True
        except Exception as e:
            print(f"회원가입 또는 이메일 인증 메일 전송 중 오류 발생: {e}")
            return False
    
    # 회원 가입 db 연동
    def signUP(id : str, pw : str, userInfo) -> bool:
        try:
            pathID = id.replace('@','__aA__').replace('.','__dD__')
            database().pyrebase_auth.create_user_with_email_and_password(email=id, password=pw)
            database().pyrebase_db_user.child(pathID).set(userInfo)
            return True
        except Exception as e:
            print(f"가입 시도 중 예상치 못한 오류 발생: {e}")
            return False

    # 로그인
    def signIN(id : str, pw : str) -> bool:
        try:
            database().pyrebase_auth.sign_in_with_email_and_password(email=id, password=pw)
            return True
        except Exception as e:
            print(f'로그인 실패 {e}')
            return False

    def PWlaterChange(id : str, date : str):
        try:
            pathID = id.replace('@','__aA__').replace('.','__dD__')
            results = {
                'createPW' : date
            }
            database().pyrebase_db_user.child(pathID).update(results)
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
            pathID = id.replace('@','__aA__').replace('.','__dD__')
            if like in userInfo['like']:
                userInfo['like'].remove(like)
                results = {
                    'like' : userInfo['like']
                }
                database().pyrebase_db_user.child(pathID).update(results)
                return userInfo['like']
            else:
                userInfo['like'].append(like)
                results = {
                    'like' : userInfo['like']
                }
                database().pyrebase_db_user.child(pathID).update(results)
                return userInfo['like']
        except Exception as e:
            print(f'like 실패 {e}')
            return False

    # 아이템 구매 및 상태 변경
    def itemOrder(id : str, itemID : str, orderList : list):
        try:
            pathID = id.replace('@','__aA__').replace('.','__dD__')
            results = {
                'orderList' : orderList
            }
            database().pyrebase_db_user.child(pathID).update(results)
            itemStatus = database().pyrebase_db_itemStatus.child(itemID).get().val() # 아이템 수량 변경
            countResults = int(itemStatus['count']) - 1
            if countResults < 4:
                itemResults = {
                    'count' : countResults,
                    'enable' : False
                }
                database().pyrebase_db_itemStatus.child(itemID).update(itemResults)
                return True
            else:
                itemResults = {
                    'count' : countResults
                }
                database().pyrebase_db_itemStatus.child(itemID).update(itemResults)
                return True
        except Exception as e:
            print(f'상품 주문 실패 {e}')
            return False


# 주소 검색
def seachAddress(address : str):
    sqlInjection = ["OR", "SELECT", "INSERT", "DELETE", "UPDATE", "CREATE", "DROP", "EXEC", "UNION",  "FETCH", "DECLARE", "TRUNCATE"]
    if re.search(r"[\]\[%;<>=]", address):
        return [{'False':'특수문자는 포함할 수 없습니다.'}]
    elif any(i in address.upper() for i in sqlInjection):
        return [{'False':'포함할 수 없는 단어가 존재합니다.'}]
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
                    return [{'None':'검색 결과가 없습니다. 주소를 다시 확인해주세요.'}]
                else:
                    addrList = []
                    for i in range(addrLen):
                        addrList.append({response.json()["results"]["juso"][i]["zipNo"] : response.json()["results"]["juso"][i]["roadAddr"]})
                    return addrList
        except Exception as e:
            return [{'False':f'알 수 없는 오류 발생 {e}'}]