import streamlit as st
import pyrebase
from email_validator import validate_email, EmailNotValidError
import re
import json
import requests
from requests.exceptions import HTTPError
import secrets

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
    # 이메일 유효성 검사
    def emailCK(id : str) -> dict:
        try:
            if validate_email(id, check_deliverability=True, timeout=5)['email'] == id:
                return {'allow' : True, 'result' : id}
            else:
                return {'allow' : False, 'result' : '이메일 형식이 잘못되었습니다.'}
        except EmailNotValidError as emailError:
            return {'allow' : False, 'result' : f'이메일 검증 오류 {emailError}'}
        except Exception as e:
            print(e)
            return {'allow' : False, 'result' : f'예기치 못한 오류 {e}'}

    # 중복 회원 검증
    def userOverlapCK(id : str, pw : str) -> bool:
        try:
            database().pyrebase_auth.create_user_with_email_and_password(email=id, password=pw)
            return True
        except HTTPError as error:
            errorMessage = json.loads(error.args[1])['error']['message']
            print(f'{id} // {errorMessage}')
            return False

    # 인증 메일 전송
    def sendEmail(userToken : str) -> bool:
        try:
            database().pyrebase_auth.send_email_verification(userToken)
            return True
        except Exception as e:
            print(f"인증 메일 전송 오류 : {e}")
            return False
    
    # 회원 가입 db 연동
    def signUP(email:str, pw:str, userInfo) -> dict:
        try:
            user = database().pyrebase_auth.sign_in_with_email_and_password(email=email, password=pw)
            database().pyrebase_db_user.child(user['localId']).set(userInfo)
            return {'allow' : True, 'result' : user}
        except Exception as e:
            return {'allow' : False, 'result' : f'회원가입 실패 {e}'}

    # 로그인
    def signIN(id : str, pw : str) -> dict:
        try:
            user = database().pyrebase_auth.sign_in_with_email_and_password(email=id, password=pw)
            return {'allow':True, 'result':user}
        except Exception as e:
            print(f"로그인 실패 : {e}")
            return {'allow':False, 'result':'로그인 시도 중 예기치 못한 오류 발생'}
        
    # 회원 정보 호출
    def showUserInfo(uid : str, token):
        try:
            userInfo = database().pyrebase_db_user.child(uid).get(token=token).val()
            return {'allow':True, 'result':userInfo}
        except Exception as e:
            print(e)
            return {'allow':False, 'result':f'정보 불러오기 실패 {e}'}

    # 비밀번호 변경
    def PWChange(token : str, newPW : str) -> bool:
        try:
            database().pyrebase_auth.change_password(token, newPW)
            return True
        except Exception as e:
            print(f"비밀번호 변경 오류 : {e}")
            return False

    # 비밀번호 연장
    def PWlaterChange(uid : str, date : str) -> bool:
        try:
            results = {
                'createPW' : date
            }
            database().pyrebase_db_user.child(uid).update(results)
            return True
        except Exception as e:
            print(f'비밀번호 연장 실패 {e}')
            return False
    
    # 회원 탈퇴
    def guestOUT():
        pass

    # 사용자 주소 추가
    def addAddr(uid : str, addAddr : str) -> bool:
        try:
            addrInfo = database().pyrebase_db_user.child(uid).child('address').get().val()
            database().pyrebase_db_user.child(uid).update({'address':addrInfo.append(addAddr)})
            return True
        except Exception as e:
            print(e)
            return False

    # 사용자 주소 삭제
    def delAddr(uid : str, delAddr : str) -> bool:
        try:
            addrInfo = database().pyrebase_db_user.child(uid).child('address').get().val()
            database().pyrebase_db_user.child(uid).update({'address':addrInfo.remove(delAddr)})
            return True
        except Exception as e:
            print(e)
            return False


class items(database):
    # 아이템 수량 및 상태    
    def itemStatus(itemId : str) -> dict:
        try:
            itemStatus = database().pyrebase_db_itemStatus.child(itemId).get().val() # 아이템 상태 조회
            return {'allow':True, 'result':itemStatus}
        except Exception as e:
            print(e)
            return {'allow':False, 'result':'아이템 조회 실패'}
    
    # 아이템 ID 리스트
    def itemsIdList():
        itemsId_dict = database().pyrebase_db_items.get().val() # 아이템 키값 dict {'items1':True}
        itemsId = list(itemsId_dict.keys()) # 아이템 키값 list
        return itemsId

    # 아이템 구매 및 상태 변경
    def itemOrder(uid : str, itemID : str, orderInfo : dict) -> bool:
        try:
            database().pyrebase_db_user.child(uid).child('orderList').push(orderInfo)
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