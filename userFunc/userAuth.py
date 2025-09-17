import streamlit as st
from utils import database
import re
import requests
import urllib.parse
import secrets
# import smtplib
# from email.message import EmailMessage

# guest 관리
class guest(database):
    def tokenToUid(token : dict) -> dict:
        try:
            # if token.get('firebase') != None:
            #     uid = token.get('firebase').get('localId')
            #     return {'allow':True, 'result':uid}
            if token.get('naver') != None:
                userInfo = requests.post(
                    url='https://openapi.naver.com/v1/nid/me',
                    headers={'Authorization':f'Bearer {token.get('naver')['access_token']}'}
                    )
                if userInfo.status_code == 200 and userInfo.json()['resultcode'] == '00':
                    return {'allow':True, 'result':userInfo.json()['response']['id']}
                else:
                    return {'allow':False, 'result':'네이버 고객정보 확인 실패'}
            elif token.get('kakao') != None:
                pass
            elif token.get('gmail') != None:
                pass
            else:
                {'allow':False, 'result':'회원 정보 없음'}
        except Exception as e:
            return {'allow':False, 'result':e}

    # 네이버 로그인 요청
    def naverSignUP() -> str:
        naverSignInParams = {
            'response_type':'code',
            'client_id':st.secrets['naver_api']['client_id'],
            'state':secrets.randbits(k=16),
            'redirect_uri':st.secrets['naver_api']['redirect_uri']
        }
        encoded_params = urllib.parse.urlencode(naverSignInParams)
        return f'https://nid.naver.com/oauth2.0/authorize?{encoded_params}'

    # 네이버 고객 토큰 발급
    def naverToken(code : str, state : str) -> dict:
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
                return {'allow':True, 'result':userToken.json()}
            else:
                return {'allow':False, 'result':'토큰 발행 실패'}
        except Exception as e:
            return {'allow':False, 'result':e}

    # 네이버 로그인 고객 firebase 처리
    def naverUser(response : dict) -> bool:
        try:
            if response['id'] in database().rtDatabase_user.get(shallow=True):
                userInfo = database().rtDatabase_user.child(response['id']).get()
                return {'allow':True, 'result':userInfo}
            else:
                userData = {
                    'name':response['name'],
                    'phoneNumber':response['mobile'].replace('-',''),
                    'email':response['email'],
                    'age':response['birthyear'] + response['birthday'].replace('-','')
                }
                database().rtDatabase_user.child(response['id']).set(value=userData)
                return {'allow':True, 'result':userData}

        except Exception as e:
            print(e)
            return {'allow':False, 'result':e}

    # 카카오 로그인 요청
    def kakaoSignUP() -> str:
        kakaoSignInParams = {
            'response_type':'code',
            'client_id':st.secrets['kakao_api']['client_id'],
            'state':secrets.randbits(k=16),
            'redirect_uri':st.secrets['kakao_api']['redirect_uri']
        }
        encoded_params = urllib.parse.urlencode(kakaoSignInParams)
        return f'https://kauth.kakao.com/oauth/authorize?{encoded_params}'

    # 카카오 토큰 발행
    def kakaoToken(code : str) -> dict:
        kakaoHeader = "Content-Type: application/x-www-form-urlencoded;charset=utf-8"
        kakaoParams = {
            'grant_type':'authorization_code',
            'client_id':st.secrets['kakao_api']['client_id'],
            'redirect_uri':st.secrets['kakao_api']['redirect_uri'],
            'code':code,
            'client_secret':st.secrets['kakao_api']['client_sc']
        }
        encoded_params = urllib.parse.urlencode(kakaoParams)
        try:
            userToken = requests.post(url='https://kauth.kakao.com/oauth/token', params=encoded_params, headers=kakaoHeader)
            if userToken.status_code == 200:
                return {'allow':True, 'result':userToken.json()}
            else:
                return {'allow':False, 'result':'토큰 발행 실패'}
        except Exception as e:
            return {'allow':False, 'result':e}

    # 카카오 로그인 고객 firebase 처리
    def kakaoUser(response : dict) -> bool:
        try:
            if response['id'] in database().rtDatabase_user.get(shallow=True):
                userInfo = database().rtDatabase_user.child(response['id']).get()
                return {'allow':True, 'result':userInfo}
            else:
                userData = {
                    'name':response['name'],
                    'phoneNumber':response['phone_number'].replace('-',''),
                    'email':response['email'],
                    'age':response['birthyear'] + response['birthday']
                }
                database().rtDatabase_user.child(response['id']).set(value=userData)
                return {'allow':True, 'result':userData}

        except Exception as e:
            print(e)
            return {'allow':False, 'result':e}

    # 회원 정보호출
    def showUserInfo(token : dict) -> dict:
        uid = guest.tokenToUid(token=token)
        if uid['allow']:
            userInfo = database().rtDatabase_user.child(uid['result']).get()
            return userInfo
        else:
            return None

    # 회원 탈퇴
    def guestOUT(token : dict) -> bool:
        uid = guest.tokenToUid(token=token)
        if token.get('firebase') != None:
            if uid['allow']:
                database().auth.update_user(uid=uid['result'], disabled=True)
                userInfo = database().rtDatabase_user.child(uid['result']).get()
                database().rtDatabase_user.child('out_'+uid['result']).set(userInfo)
                database().rtDatabase_user.child(uid['result']).delete()
                return True
            else:
                print(f'회원탈퇴 실패')
                return False
        else:
            userInfo = database().rtDatabase_user.child(uid['result']).get()
            database().rtDatabase_user.child('out_'+uid['result']).set(userInfo)
            database().rtDatabase_user.child(uid['result']).delete()

    # 소셜 사용자 기본 배송지 추가
    def addHomeAddr(token : dict, addr : str) -> bool:
        uid = guest.tokenToUid(token=token)
        if uid['allow']:
            database().rtDatabase_user.child(uid['result']).child('address').set({'home':addr})
            return True
        else:
            print('소셜 고객 기본 배송지 설정 실패')
            return False

    # 사용자 주소 추가
    def addAddr(token : dict, addAddr : str):
        uid = guest.tokenToUid(token=token)
        if uid['allow']:
            database().rtDatabase_user.child(uid['result']).child('address').push(addAddr)
        else:
            pass

    # 사용자 주소 삭제
    def delAddr(token : dict, delAddrKey : str):
        uid = guest.tokenToUid(token=token)
        if uid['allow']:
            database().rtDatabase_user.child(uid['result']).child(f'address/{delAddrKey}').delete()
        else:
            pass

    # 주 배송지 수정
    def homeAddr(token : dict, homeAddrKey : str, homeAddr : str):
        uid = guest.tokenToUid(token=token)
        if uid['allow']:
            oldAddr = database().rtDatabase_user.child(uid['result']).child('address').child('home').get()
            database().rtDatabase_user.child(uid['result']).child('address').push(oldAddr)
            database().rtDatabase_user.child(uid['result']).child('address').update({'home':homeAddr})
            database().rtDatabase_user.child(uid['result']).child(f'address/{homeAddrKey}').delete()
        else:
            pass

    # # firebase 로그인 고객
    # def signIN(id : str, pw : str) -> dict:
    #     try:
    #         signINuser = database().pyrebase_auth.sign_in_with_email_and_password(email=id, password=pw)
    #         return {'allow':True, 'result':signINuser}

    #     except requests.exceptions.HTTPError as httpError:
    #         print(httpError)
    #         return {'allow':False, 'result':'회원 로그인 실패, 아이디와 비밀번호를 확인해주세요.'}

    #     except Exception as e:
    #         print(e)
    #         return {'allow':False, 'result':'회원 로그인 실패, 아이디와 비밀번호를 확인해주세요.'}

    # # 중복 이메일 확인 및 이메일 검증
    # def emailCK(id : str) -> dict:
    #     try:
    #         database().auth.get_user_by_email(email=id)
    #         return {'allow' : False, 'result' : '가입된 이메일입니다.'}
    #     except database().auth.UserNotFoundError:
    #         return {'allow' : True, 'result' : id}
    #     except ValueError:
    #         return {'allow' : False, 'result' : '올바르지 않은 이메일 형식입니다.'}
    #     except Exception as e:
    #         print(e)
    #         return {'allow' : False, 'result' : '예기치 못한 오류'}

    # # 회원 가입 db 연동
    # def createUser(email : str, pw : str) -> bool:
    #     try:
    #         database().auth.create_user(email=email, password=pw, disabled=True)
    #         return True
    #     except Exception as e:
    #         print(e)
    #         return False

    # # firebase 고객 DB 저장
    # def userInfoAddDB(email : str, userInfo : dict) -> bool:
    #     try:
    #         userAuth = database().auth.get_user_by_email(email=email)
    #         database().rtDatabase_user.child(path=userAuth.uid).set(value=userInfo)
    #         return True
    #     except Exception as e:
    #         print(e)
    #         return False

    # # 인증 메일 전송
    # def sendEmail(userMail: str) -> bool:
    #     findUser = database().auth.get_user_by_email(email=userMail)
    #     settingCode = database().auth.ActionCodeSettings(
    #         url=f"{database().emailAccess['DEPLOYED_BASE_URL']}/success?email={userMail}",
    #         handle_code_in_app=True
    #     )
    #     link = database().auth.generate_email_verification_link(
    #         email=userMail,
    #         action_code_settings=settingCode
    #     )
    #     emailMain = EmailMessage()
    #     emailMain['Subject'] = 'amuredo 회원가입, 이메일 인증 입니다.'
    #     emailMain['From'] = database().emailAccess['SENDER_EMAIL']
    #     emailMain['To'] = userMail
    #     emailMain.set_content(database().emailMain + link)
    #     try:
    #         with smtplib.SMTP(
    #             host=database().emailAccess['SENDER_SERVER'],
    #             port=database().emailAccess['SENDER_PORT']
    #             ) as smtp_server:
    #             smtp_server.ehlo() # 서버에 자신을 소개
    #             smtp_server.starttls() # TLS 암호화 시작
    #             smtp_server.login(database().emailAccess['SENDER_EMAIL'], database().emailAccess['SENDER_APP_PASSWORD'])
    #             smtp_server.send_message(emailMain)
    #         database().auth.update_user(uid=findUser.uid, disabled=False)
    #         return True
    #     except smtplib.SMTPAuthenticationError:
    #         print('오류: SMTP 인증 실패.')
    #         return False
    #     except smtplib.SMTPServerDisconnected:
    #         print('오류: SMTP 서버 연결 끊김.')
    #         return False
    #     except Exception as e:
    #         print(e)
    #         return False

    # # 회원 이메일 인증 확인
    # def showEmailVerified(token : dict) -> bool:
    #     try:
    #         if token.keys() == 'firebase':
    #             uid = guest.tokenToUid(token=token)
    #             if uid['allow']:
    #                 emailVer = database().auth.get_user(uid=uid['result']).email_verified
    #                 if emailVer:
    #                     return True
    #                 else:
    #                     return False
    #             else:
    #                 return False
    #         else:
    #             return True
    #     except Exception as e:
    #         print(e)
    #         return False

    # # 비밀번호 변경
    # def PWchange(token : dict, newPW : str, date : str) -> bool:
    #     uid = guest.tokenToUid(token=token)
    #     if uid['allow']:
    #         database().auth.update_user(uid=uid['result'], password=newPW)
    #         database().rtDatabase_user.child(uid['result']).update({'createPW':date})
    #     else:
    #         print('비밀번호 변경 실패')
    #         pass

    # # 비밀번호 연장
    # def PWchangeLater(token : dict, date : str):
    #     uid = guest.tokenToUid(token=token)
    #     if uid['allow']:
    #         database().rtDatabase_user.child(uid['result']).update({'createPW':date})
    #     else:
    #         pass


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