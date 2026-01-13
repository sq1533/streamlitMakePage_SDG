import streamlit as st
import utils
import re
import requests
import urllib.parse
import secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

from schema.schema import user

class guest(utils.database):

    # 소셜 토큰으로 uid 확인
    def tokenToUid(token : dict) -> dict:
        try:
            if token.get('naver') != None:
                userInfo = requests.post(
                    url='https://openapi.naver.com/v1/nid/me',
                    headers={'Authorization':f"Bearer {token.get('naver')}"}
                    )
                if userInfo.status_code == 200 and userInfo.json()['resultcode'] == '00':
                    return {'allow':True, 'result':userInfo.json()['response']['id']}
                else:
                    return {'allow':False, 'result':'네이버 고객정보 확인 실패'}
            elif token.get('kakao') != None:
                userInfo = requests.post(
                    url='https://kapi.kakao.com/v2/user/me',
                    headers={'Authorization':f"Bearer {token.get('kakao')}"}
                    )
                if userInfo.status_code == 200:
                    return {'allow':True, 'result':userInfo.json()['id']}
                else:
                    return {'allow':False, 'result':'카카오 고객정보 확인 실패'}
            elif token.get('gmail') != None:
                userInfo = requests.get(
                    url='https://people.googleapis.com/v1/people/me',
                    params={'personFields': 'names'},
                    headers={'Authorization': f"Bearer {token.get('gmail')}"}
                )
                if userInfo.status_code == 200:
                    res_name = userInfo.json().get('resourceName', '')
                    user_id = res_name.split('/')[-1] if '/' in res_name else res_name
                    return {'allow': True, 'result': user_id}
                else:
                    return {'allow': False, 'result': '구글 고객정보 확인 실패'}
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
        return f"https://nid.naver.com/oauth2.0/authorize?{encoded_params}"

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
        realtimeUser = utils.utilsDb().realtimeDB.reference(path='user')
        try:
            userId = str(response.get('id'))
            if userId in realtimeUser.get(shallow=True):
                userInfo = realtimeUser.child(userId).get()
                try:
                    userResult = user(**userInfo)
                except Exception as e:
                    utils.get_logger().error(f"파싱 오류 {userId} : {e}")
                return {'allow':True, 'result':userResult.model_dump()}
            else:
                # 신규 가입 시도
                birthdate_int = int(response.get('birthyear') + response.get('birthday').replace('-',''))

                if check_under_14(birthdate_int):
                    return {'allow': False, 'result': '만 14세 이하는 회원가입이 불가능합니다.'}

                userData = {
                    'name':response.get('name'),
                    'phoneNumber':response.get('mobile').replace('-',''),
                    'email':response.get('email'),
                    'age':birthdate_int,
                    'address':'',
                    'orderList':''
                }
                try:
                    userResult = user(**userData)
                except Exception as e:
                    utils.get_logger().error(f"파싱 오류 {userId} : {e}")
                realtimeUser.child(userId).set(value=userResult.model_dump())
                return {'allow':True, 'result':userResult.model_dump()}
        except Exception as e:
            utils.get_logger().error(e)
            return {'allow':False, 'result':e}

    # 카카오 로그인 요청
    def kakaoSignUP() -> str:
        kakaoSignInParams = {
            'client_id':st.secrets['kakao_api']['client_id'],
            'redirect_uri':st.secrets['kakao_api']['redirect_uri'],
            'response_type':'code',
            'state':secrets.randbits(k=16)
        }
        encoded_params = urllib.parse.urlencode(kakaoSignInParams)
        return f"https://kauth.kakao.com/oauth/authorize?{encoded_params}"

    # 카카오 토큰 발행
    def kakaoToken(code : str) -> dict:
        kakaoHeader = {'Content-Type' : 'application/x-www-form-urlencoded;charset=utf-8'}
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
        realtimeUser = utils.utilsDb().realtimeDB.reference(path='user')
        try:
            userId = str(response.get('id'))
            if userId in realtimeUser.get(shallow=True):
                userInfo = realtimeUser.child(userId).get()
                try:
                    userResult = user(**userInfo)
                except Exception as e:
                    utils.get_logger().error(f"파싱 오류 {userId} : {e}")
                return {'allow':True, 'result':userResult.model_dump()}
            else:
                # 신규 가입 시도
                birthdate_int = int(response.get('kakao_account').get('birthyear') + response.get('kakao_account').get('birthday'))

                if check_under_14(birthdate_int):
                    return {'allow': False, 'result': '만 14세 이하는 회원가입이 불가능합니다.'}

                userData = {
                    'name':response.get('kakao_account').get('name'),
                    'phoneNumber':'0' + response.get('kakao_account').get('phone_number').split(' ')[1].replace('-',''),
                    'email':response.get('kakao_account').get('email'),
                    'age':birthdate_int,
                    'address':'',
                    'orderList':''
                }
                try:
                    userResult = user(**userData)
                except Exception as e:
                    utils.get_logger().error(f"파싱 오류 {userId} : {e}")
                realtimeUser.child(userId).set(value=userResult.model_dump())
                return {'allow':True, 'result':userResult.model_dump()}

        except Exception as e:
            utils.get_logger().error(e)
            return {'allow':False, 'result':e}

    # 구글 gmail 요청
    def gmailSignUP() -> str:
        scopes = [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/user.birthday.read',
            'https://www.googleapis.com/auth/user.phonenumbers.read'
        ]
        
        googleSignInParams = {
            'client_id': st.secrets['google_api']['client_id'],
            'redirect_uri': st.secrets['google_api']['redirect_uri'],
            'response_type': 'code',
            'scope': ' '.join(scopes), # 공백으로 구분하여 합침
            'access_type': 'offline',
            'state': secrets.randbits(k=16)
        }
        encoded_params = urllib.parse.urlencode(googleSignInParams)
        return f"https://accounts.google.com/o/oauth2/v2/auth?{encoded_params}"

    # gmail 토큰 발행
    def gmailToken(code : str) -> dict:
        googleParams = {
            'client_id': st.secrets['google_api']['client_id'],
            'client_secret': st.secrets['google_api']['client_sc'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': st.secrets['google_api']['redirect_uri']
        }
        try:
            tokenResponse = requests.post("https://oauth2.googleapis.com/token", data=googleParams)
            if tokenResponse.status_code == 200:
                return {'allow': True, 'result': tokenResponse.json()}
            else:
                return {'allow': False, 'result': '토큰 발행 실패'}
        except Exception as e:
            return {'allow': False, 'result': e}

    # gmail 로그인 고객 firebase 처리
    def gmailUser(response : dict) -> bool:
        realtimeUser = utils.utilsDb().realtimeDB.reference(path='user')
        try:
            res_name = response.get('resourceName', '') # google People API (people/userID)
            userId = res_name.split('/')[-1] if '/' in res_name else res_name
            if userId in realtimeUser.get(shallow=True):
                userInfo = realtimeUser.child(userId).get()
                try:
                    userResult = user(**userInfo)
                except Exception as e:
                    utils.get_logger().error(f"파싱 오류 {userId} : {e}")
                return {'allow': True, 'result': userResult.model_dump()}
            else:
                # 1. 이름 파싱
                names = response.get('names', [])
                name = names[0].get('displayName') if names else 'Unknown'

                # 2. 이메일 파싱
                emails = response.get('emailAddresses', [])
                email = emails[0].get('value') if emails else ''

                # 3. 전화번호 파싱 및 정제
                phones = response.get('phoneNumbers', [])
                raw_phone = phones[0].get('value') if phones else '00000000000'
                phoneNumber = raw_phone.replace('-', '').replace(' ', '').replace('+82', '0')

                # 4. 생년월일 파싱 및 나이 계산
                birthdays = response.get('birthdays', [])
                age = 0
                if birthdays:
                    date = birthdays[0].get('date', {})
                    year = date.get('year')
                    month = date.get('month')
                    day = date.get('day')
                    if year and month and day:
                        age = int(f"{year}{month:02d}{day:02d}")

                if check_under_14(age):
                    return {'allow': False, 'result': '만 14세 이하는 회원가입이 불가능합니다.'}

                userData = {
                    'name': name,
                    'phoneNumber': phoneNumber,
                    'email': email,
                    'age': age,
                    'address': '',
                    'orderList': ''
                }
                try:
                    userResult = user(**userData)
                except Exception as e:
                    utils.get_logger().error(f"파싱 오류 {userId} : {e}")
                realtimeUser.child(userId).set(value=userResult.model_dump())
                return {'allow': True, 'result': userResult.model_dump()}

        except Exception as e:
            utils.get_logger().error(e)
            return {'allow': False, 'result': e}

    # 회원 정보호출
    def showUserInfo(token : dict) -> dict:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            return {'result':'토큰 조회 실패'}

        uid = str(uid.get('result'))

        try:
            userInfo : dict = utils.utilsDb().realtimeDB.reference(path=f"user/{uid}").get()
            try:
                userData = user(**userInfo)
                return {'result':userData.model_dump()}
            except Exception as e:
                utils.get_logger().error(f"파싱 오류 {uid} : {e}")
                return {'result':'회원 정보 호출 실패'}

        except Exception as e:
            utils.get_logger().error(f"회원 정보 호출 오류 : {e}")
            return {'result':'회원 정보 호출 실패'}

    # 회원 탈퇴
    def guestOUT(token : dict) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            utils.get_logger().error('고객정보 호출 실패')
            return False

        uid = str(uid.get('result'))

        userInfo : dict = utils.utilsDb().realtimeDB.reference(path=f"user/{uid}").get()
        utils.utilsDb().realtimeDB.reference(path=f"user/out_{secrets.randbits(k=16)}_{uid}").set(userInfo)
        utils.utilsDb().realtimeDB.reference(path=f"user/{uid}").delete()
        return True

    # 소셜 사용자 기본 배송지 추가
    def addHomeAddr(token : dict, addr : str) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            utils.get_logger().error('고객정보 호출 실패')
            return False

        uid = str(uid.get('result'))

        utils.utilsDb().realtimeDB.reference(path=f"user/{uid}/address").set({'home':addr})
        return True

    # 사용자 주소 추가
    def addAddr(token : dict, addAddr : str):
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            utils.get_logger().error('고객정보 호출 실패')
            return False

        uid = str(uid.get('result'))

        utils.utilsDb().realtimeDB.reference(path=f"user/{uid}/address").push(addAddr)
        return True

    # 사용자 주소 삭제
    def delAddr(token : dict, delAddrKey : str) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            utils.get_logger().error('고객정보 호출 실패')
            return False

        uid = uid.get('result')

        utils.utilsDb().realtimeDB.reference().child(f"user/{uid}/address/{delAddrKey}").delete()
        return True

    # 주 배송지 수정
    def homeAddr(token : dict, homeAddrKey : str, homeAddr : str) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            utils.get_logger().error('고객정보 호출 실패')
            return False

        uid = str(uid.get('result'))

        oldAddr : str = utils.utilsDb().realtimeDB.reference(path=f"user/{uid}/address/home").get()
        utils.utilsDb().realtimeDB.reference(path=f"user/{uid}/address").push(oldAddr)
        utils.utilsDb().realtimeDB.reference(path=f"user/{uid}/address").update({'home':homeAddr})
        utils.utilsDb().realtimeDB.reference(path=f"user/{uid}/address/{homeAddrKey}").delete()
        return True

    # 고객 문의, 이메일전송(amuredo_shop@naver.com)
    def sendEmail(userInfo : dict, title : str, content : str) -> bool:
        # 고객정보 확인
        name = userInfo.get('name')
        phoneNumber = userInfo.get('phoneNumber')
        email = userInfo.get('email')

        # 이메일 셋팅
        emailMain = MIMEMultipart()
        emailMain['Subject'] = f"amuredo 문의 : {title}"
        emailMain['From'] = utils.utilsDb().emailAccess['SENDER_EMAIL']
        emailMain['To'] = utils.utilsDb().emailAccess['SENDER_EMAIL']
        body = f"""
        고객 이름 : {name}
        고객 이메일 : {email}
        고객 연락처 : {phoneNumber}
        [고객 문의 내용]
        {content}
        """        
        # 본문 추가
        emailMain.attach(MIMEText(body, 'plain'))

        # 이메일 전송 (비동기 처리)
        def sending_task():
            try:
                with smtplib.SMTP(
                    host=utils.utilsDb().emailAccess['SENDER_SERVER'],
                    port=utils.utilsDb().emailAccess['SENDER_PORT']
                    ) as smtp_server:
                    smtp_server.ehlo() # 서버에 자신을 소개
                    smtp_server.starttls() # TLS 암호화 시작
                    smtp_server.login(utils.utilsDb().emailAccess['SENDER_EMAIL'], utils.utilsDb().emailAccess['SENDER_APP_PASSWORD'])
                    smtp_server.send_message(emailMain)
                
            except smtplib.SMTPAuthenticationError:
                utils.get_logger().error('오류: SMTP 인증 실패.')

            except smtplib.SMTPServerDisconnected:
                utils.get_logger().error('오류: SMTP 서버 연결 끊김.')

            except Exception as e:
                utils.get_logger().error(f"이메일 전송 오류: {e}")

        import threading
        threading.Thread(target=sending_task).start()
        
        return True

# 나이 검증_만 14세 이하 (연도 기준)
def check_under_14(birthdate_int: int) -> bool:
    if not birthdate_int:
        return True
    today = date.today()
    birth_year = birthdate_int // 10000

    age_by_year = today.year - birth_year

    return age_by_year <= 14

# 주소 검색
def seachAddress(address : str) -> dict:
    # SQL 인젝션 및 특수문자 방어
    if re.search(r"[\]\[%;<>=]", address):
        return {'allow':False, 'result':'특수문자는 포함할 수 없습니다.'}
    if any(i in address.upper() for i in utils.utilsDb().sqlInjection):
        return {'allow':False, 'result':'포함할 수 없는 단어가 존재합니다.'}

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