import streamlit as st
from utils import database
import re
import requests
import urllib.parse
import secrets
import smtplib
from email.message import EmailMessage

# guest 관리
class guest(database):
    # 네이버 로그인 요청
    def naverSignUP() -> str:
        naverSignInParams = {
            'response_type':'code',
            'client_id':st.secrets['naver_api']['client_id'],
            'state':secrets.randbits(k=16),
            'redirect_uri':'http://localhost:8080/signIN'
        }
        encoded_params = urllib.parse.urlencode(naverSignInParams)
        return f'https://nid.naver.com/oauth2.0/authorize?{encoded_params}'

    # 네이버 고객 토큰 발급
    def naverUser(code : str, state : str):
        naverParams = {
            'grant_type':'authorization_code',
            'client_id':st.secrets['naver_api']['client_id'],
            'client_secret':st.secrets['naver_api']['client_sc'],
            'code':code,
            'state':state
        }
        encoded_params = urllib.parse.urlencode(naverParams)
        try:
            userToken = requests.post(url='https://nid.naver.com/oauth2.0/token', params=encoded_params)
            if userToken.status_code == 200:
                userInfo = requests.post(url='https://openapi.naver.com/v1/nid/me', headers={'Authorization':f'Bearer {userToken.json()['access_token']}'})
                if userInfo.status_code == 200 and userInfo.json()['resultcode'] == '00':
                    return userInfo.json()
                else:
                    print('토큰발행 성공, 고객정보 확인 실패')
                    return False
            else:
                print('토큰 발행 실패')
                return False
        except Exception as e:
            print(e)
            return False

    # 네이버 로그인 고객 firebase 처리
    def naverSignIN(response : dict) -> dict:
        try:
            if response['id'] in database().rtDatabase_user.get(shallow=True):
                userInfo = database().rtDatabase_user.child(response['id']).get()
                return {'allow':True, 'result':userInfo, 'uid':response['id']}
            else:
                userData = {
                    'name':response['name'],
                    'mobile':response['mobile_e164'],
                    'age':response['birthyear'] + response['birthday'].replace('-','')
                }
                database().rtDatabase_user.child(response['id']).set(value=userData)
                return {'allow':True, 'result':userData, 'uid':response['id']}
        except Exception as e:
            print(e)
            return {'allow':False, 'result':'회원 로그인 실패'}

    # firebase 로그인 고객
    def signIN(id : str, pw : str) -> dict:
        try:
            findUser = database().auth.get_user_by_email(email=id)
            database().pyrebase_auth.sign_in_with_email_and_password(email=id, password=pw)
            userInfo = database().rtDatabase_user.child(findUser.uid).get()
            return {'allow':True, 'result':userInfo, 'uid':findUser.uid}

        except database().auth.UserNotFoundError:
            return {'allow':False, 'result':'로그인 정보를 확인할 수 없습니다.'}

        except requests.exceptions.HTTPError as httpError:
            print(httpError)
            return {'allow':False, 'result':'회원 로그인 실패, 아이디와 비밀번호를 확인해주세요.'}

        except Exception as e:
            print(e)
            return {'allow':False, 'result':'회원 로그인 실패, 아이디와 비밀번호를 확인해주세요.'}

    # 중복 이메일 확인 및 이메일 검증
    def emailCK(id : str) -> dict:
        try:
            database().auth.get_user_by_email(email=id)
            return {'allow' : False, 'result' : '가입된 이메일입니다.'}
        except database().auth.UserNotFoundError:
            return {'allow' : True, 'result' : id}
        except ValueError:
            return {'allow' : False, 'result' : '올바르지 않은 이메일 형식입니다.'}
        except Exception as e:
            print(e)
            return {'allow' : False, 'result' : '예기치 못한 오류'}

    # 회원 가입 db 연동
    def createUser(email : str, pw : str) -> bool:
        try:
            database().auth.create_user(email=email, password=pw, disabled=True)
            return True
        except Exception as e:
            print(e)
            return False

    # firebase 고객 DB 저장
    def userInfoAddDB(email : str, userInfo : dict) -> bool:
        try:
            userAuth = database().auth.get_user_by_email(email=email)
            database().rtDatabase_user.child(path=userAuth.uid).set(value=userInfo)
            return True
        except Exception as e:
            print(e)
            return False

    # 인증 메일 전송
    def sendEmail(userMail: str) -> bool:
        findUser = database().auth.get_user_by_email(email=userMail)
        settingCode = database().auth.ActionCodeSettings(
            url=f"{database().emailAccess['DEPLOYED_BASE_URL']}/success?email={userMail}",
            handle_code_in_app=True
        )
        link = database().auth.generate_email_verification_link(
            email=userMail,
            action_code_settings=settingCode
        )
        emailMain = EmailMessage()
        emailMain['Subject'] = 'amuredo 회원가입, 이메일 인증 입니다.'
        emailMain['From'] = database().emailAccess['SENDER_EMAIL']
        emailMain['To'] = userMail
        emailMain.set_content(database().emailMain + link)
        try:
            with smtplib.SMTP(
                host=database().emailAccess['SENDER_SERVER'],
                port=database().emailAccess['SENDER_PORT']
                ) as smtp_server:
                smtp_server.ehlo() # 서버에 자신을 소개
                smtp_server.starttls() # TLS 암호화 시작
                smtp_server.login(database().emailAccess['SENDER_EMAIL'], database().emailAccess['SENDER_APP_PASSWORD'])
                smtp_server.send_message(emailMain)
            database().auth.update_user(uid=findUser.uid, disabled=False)
            return True
        except smtplib.SMTPAuthenticationError:
            print('오류: SMTP 인증 실패.')
            return False
        except smtplib.SMTPServerDisconnected:
            print('오류: SMTP 서버 연결 끊김.')
            return False
        except Exception as e:
            print(e)
            return False

    # 회원 이메일 인증 확인
    def showUserEmailCK(uid : str) -> bool:
        try:
            emailVer = database().auth.get_user(uid=uid).email_verified
            if emailVer:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    # 회원 정보 재호출
    def showUserInfo(uid : str):
        try:
            userInfo = database().rtDatabase_user.child(uid).get()
            return {'allow':True, 'result':userInfo}
        except Exception as e:
            print(f'사용자 정보 호출 실패 {e}')
            return {'allow':False, 'result':'사용자 정보 호출 실패'}

    # 비밀번호 변경
    def PWchange(uid : str, pw : str, date : str) -> bool:
        try:
            database().auth.update_user(uid=uid, password=pw)
            database().rtDatabase_user.child(uid).update(values={'createPW':date})
            return True
        except Exception as e:
            print(f"비밀번호 변경 오류 : {e}")
            return False

    # 비밀번호 연장
    def PWchangeLater(uid : str, date : str) -> bool:
        try:
            database().rtDatabase_user.child(uid).update(values={'createPW':date})
            return True
        except Exception as e:
            print(f'비밀번호 연장 실패 {e}')
            return False
    # 회원 탈퇴
    def guestOUT(uid : str, token : str) -> bool:
        try:
            database().pyrebase_db_user.child(uid).remove(token=token)
            database().pyrebase_auth.delete_user_account(id_token=token)
            return True
        except Exception as e:
            print(f'회원탈퇴 실패 {e}')
            return False

    # 사용자 주소 추가
    def addAddr(uid : str, token : str, addAddr : str) -> bool:
        try:
            database().pyrebase_db_user.child(uid).child('address').push(data=addAddr, token=token)
            return True
        except Exception as e:
            print(e)
            return False

    # 사용자 주소 삭제
    def delAddr(uid : str, token : str, delAddr : str) -> bool:
        try:
            database().pyrebase_db_user.child(uid).child('address').child(delAddr).remove(token=token)
            return True
        except Exception as e:
            print(e)
            return False

    # 주 배송지 수정
    def homeAddr(uid : str, token : str, addr : str, delAddr : str) -> bool:
        try:
            oldAddr = database().pyrebase_db_user.child(uid).child('address').child('home').get(token=token).val()
            database().pyrebase_db_user.child(uid).child('address').push(data=oldAddr, token=token)
            database().pyrebase_db_user.child(uid).child('address').update(data={'home':addr}, token=token)
            database().pyrebase_db_user.child(uid).child('address').child(delAddr).remove(token=token)
            return True
        except Exception as e:
            print(e)
            return False

# 주소 검색
def seachAddress(address : str):
    if re.search(r"[\]\[%;<>=]", address):
        return {'allow':False, 'result':'특수문자는 포함할 수 없습니다.'}
    elif any(i in address.upper() for i in database().sqlInjection):
        return {'allow':False, 'result':'포함할 수 없는 단어가 존재합니다.'}
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
                    return {'allow':False, 'result':'주소가 없습니다.'}
                else:
                    addrList = []
                    for i in range(addrLen):
                        addrList.append(response.json()["results"]["juso"][i]["zipNo"] + ' ' + response.json()["results"]["juso"][i]["roadAddr"])
                    return {'allow':True, 'result':addrList}
        except Exception:
            return {'allow':False, 'result':'주소 검색 실패, 다시 시도해주세요.'}