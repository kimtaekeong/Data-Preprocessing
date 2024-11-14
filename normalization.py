from datetime import datetime, timedelta
import re
import norm_process as norm_process
import entity as ent
def norm_choice(input_list, input_text):
    value = input_list.split(":")[1].split(",")

    if input_text in value:
        return {"status": "100", "result": [{"type": "@choice", "norm": input_text}]}
    try:
        result = value[int(norm_number(input_text)['result'][0]['norm'])-1]
        return {"status": "100", "result": [{"type": "@choice", "norm": result}]}
    except:
        return {"status": "300"}

def norm_time(input_text):
    # 한글 숫자 표현 변환 딕셔너리
    korean_to_number = {
        "스물셋": 23, "스물 셋": 23, "스물넷": 24, "스물 넷": 24,
        "스물한": 21, "스물 한": 21, "스물둘": 22, "스물 둘": 22,
        "스물": 20, "스무": 20, 
        "열아홉": 19, "열여덟": 18, "열일곱": 17, "열여섯": 16, 
        "열다섯": 15, "열네": 14, "열세": 13, "열두": 12, "열한": 11, 
        "열": 10, "아홉": 9, "여덟": 8, "일곱": 7, "여섯": 6, 
        "다섯": 5, "네": 4, "세": 3, "두": 2, "한": 1
    }
    
    # 한글 숫자 변환 함수
    def convert_korean_numbers(text):
        for korean_num, arabic_num in korean_to_number.items():
            text = text.replace(korean_num, str(arabic_num))
        return text
    
    # 자정과 정오 처리
    if '자정' in input_text:
        return {"status": "100", "result": [{"type": "@time", "norm": "00:00"}]}
    elif '정오' in input_text:
        return {"status": "100", "result": [{"type": "@time", "norm": "12:00"}]}
    
    # 오전/오후 처리
    am_pm = ''
    if '오전' in input_text:
        am_pm = 'AM'
        input_text = input_text.replace('오전', '').strip()
    elif '오후' in input_text:
        am_pm = 'PM'
        input_text = input_text.replace('오후', '').strip()
    
    # 분 단위 처리
    minute_to_number = {
        "육십": 60, "오십": 50, "사십": 40, "삼십": 30, "이십": 20,  "십": 10, 
        "일": 1, "이": 2, "삼": 3 ,"사": 4 ,"오": 5 ,"육": 6 ,"칠": 7 ,"팔": 8 ,"구": 9
    }
    
    # 분 단위 매칭
    minute_pattern = r'((십|이십|삼십|사십|오십|육십)( |)*(일|이|삼|사|오|육|칠|팔|구)?(?=분))'
    minute_match = re.findall(minute_pattern, input_text)

    # 분 초기화
    minute = 0  

    if minute_match:
        # minute_match에서 시와 분을 분리
        minute_text = re.sub(r'\s+', '', minute_match[0][0])

        minute_han, minute_unit = minute_text.split("십")[0]+"십", minute_text.split("십")[1]

        if minute_han:
            minute += minute_to_number[minute_han]  # 한글 분 단위 숫자 추가
        if minute_unit:
            minute += minute_to_number[minute_unit]  # 추가적인 숫자 추가

        # 치환 후 텍스트에서 제거
        input_text = input_text.replace(minute_text, "")
    
    # 숫자 분 단위 매칭 추가
    minute_num_match = re.search(r'(\d{1,2})\s*분', input_text)
    if minute_num_match:
        minute += int(minute_num_match.group(1))  # 숫자로 된 분 추가
        input_text = input_text.replace(minute_num_match.group(0), "")  # 숫자 분 제거

    # 한글 숫자 처리
    input_text = convert_korean_numbers(input_text)
    
    # '시', '분', 그리고 ':' 표기를 사용한 시간 추출
    hour_match = re.search(r'(\d{1,2})\s*시', input_text)
    colon_match = re.search(r'(\d{1,2}):(\d{1,2})', input_text)
    
    hour = 0
    value = None
    
    # 00:00 형식 처리
    if colon_match:
        hour = int(colon_match.group(1))
        minute = int(colon_match.group(2))
        value = f"{hour:02}:{minute:02}"
    elif hour_match:
        hour = int(hour_match.group(1))
        value = f"{hour:02}:{minute:02}"
    
    # AM/PM에 따라 시간 조정
    if am_pm == 'PM' and hour < 12:
        hour += 12
    elif am_pm == 'AM' and hour == 12:
        hour = 0
    
    # 시간 유효성 검사 및 최종 결과 처리
    if hour > 23 or minute > 59:
        return {"status": "300"}  # 유효하지 않은 시간인 경우
    
    if value:
        return {"status": "100", "result": [{"type": "@time", "norm": f"{hour:02}:{minute:02}"}]}
    
    return {"status": "300"}  # 시간 정보가 없는 경우

def norm_year(input_text):
    current_year = datetime.now().year

    year_map = {
        "올해": current_year,
        "금년": current_year,
        "작년": current_year - 1,
        "재작년": current_year - 2,
        "내년": current_year + 1,
        "내후년": current_year + 2
        }

    for key, year in year_map.items():
        if key in input_text:
            return {"status": "100", "result": [{"type": "@year", "norm": str(year)}]}

    match = re.search(r'(\d{1,4}|[가-힣]+)(?=\s*년|연도|년도|연)', input_text)
    if match:
        extracted_value = match.group(1)
        try:
            if extracted_value.isdigit():
                converted_year = int(extracted_value)
                if converted_year > 2000:
                    return {"status": "100", "result": [{"type": "@year", "norm": str(converted_year)}]}
                elif converted_year < 100:
                    converted_year += 2000
                    return {"status": "100", "result": [{"type": "@year", "norm": str(converted_year)}]}
            else:
              converted_year = norm_process.korean_number_to_int(input_text)  # 예: "이십사" -> 24
              if isinstance(converted_year, int):
              # 2000년대 연도로 해석하여 반환
                  return {"status": "100", "result": [{"type": "@year", "norm": str(converted_year)}]}
        except ValueError:
            pass
    
    case1 = re.findall(r'\d+', input_text)
    if case1 and len(case1)==1:
        if int(case1[0]) > 2000:
            return {"status": "100", "result": [{"type": "@year", "norm": case1[0]}]}
        else:
            return {"status": "100", "result": [{"type": "@year", "norm": str(int(case1[0]) + 2000)}]}
    else:
        try:
            converted_year = norm_process.korean_number_to_int(input_text)  # 예: "이십사" -> 24
            if isinstance(converted_year, int):
              # 2000년대 연도로 해석하여 반환
                return {"status": "100", "result": [{"type": "@year", "norm": str(converted_year)}]}
        except ValueError:
            pass


    return {"status": "300"}

def norm_day(input_day):
    # 입력을 소문자로 변환
    input_day = input_day.lower()

    weekdays_korean = {
        '월요일': 1,
        '워료일': 1,
        '월': 1,
        '화요일': 2,
        '화': 2,
        '수요일': 3,
        '수': 3,
        '목요일': 4,
        '모교일': 4,
        '목': 4,
        '금요일': 5,
        '그묘일': 5,
        '금': 5,
        '토요일': 6,
        '토': 6,
        '일요일': 7,
        '이료일': 7,
        '일': 7
    }

    weekdays_english = {
        'monday': '월요일',
        'mon': '월요일',
        'tuesday': '화요일',
        'tue': '화요일',
        'wednesday': '수요일',
        'wed': '수요일',
        'thursday': '목요일',
        'thu': '목요일',
        'friday': '금요일',
        'fri': '금요일',
        'saturday': '토요일',
        'sat': '토요일',
        'sunday': '일요일',
        'sun': '일요일'
    }

    # 영어 요일을 한국어로 변환
    if input_day in weekdays_english:
        input_day = weekdays_english[input_day]

    found_day = None

    # 입력 텍스트에서 요일 찾기
    for day in weekdays_korean.keys():
        if day in input_day:
            found_day = day  # 가장 먼저 발견된 요일을 찾음
            break

    # 찾은 요일에 대해 숫자 반환
    day_number = weekdays_korean.get(found_day)

    if day_number is not None:
        return {"status": "100", "result": [{"type": "@day", "norm": str(day_number)}]}
    else:
        return {"status": "300"}

def norm_date(input_text):
    """개체명 date 조사 제거 및 날짜 형식 변환"""
    
    minute_pattern = r'((십|이십)( |)*(일|이|삼|사|오|육|칠|팔|구)?(?=일))'
    minute_match = re.findall(minute_pattern, input_text)

    if minute_match:
        for match in minute_match:
            input_text = input_text.replace(match[0], match[0].replace(" ", ""), 1)

    # 날짜 사전 정의
    date_dict = {
    "삼십일일": 31, "삼십일": 30, "이십구일": 29, "이십팔일": 28,
    "이십칠일": 27, "이십육일": 26, "이십오일": 25, "이십사일": 24,
    "이십삼일": 23, "이십이일": 22, "이십일일": 21, "이십일": 20,
    "십구일": 19, "십팔일": 18, "십칠일": 17, "십육일": 16,
    "십오일": 15, "십사일": 14, "십삼일": 13, "십이일": 12,
    "십일일": 11, "십일": 10, "구일": 9, "팔일": 8,
    "칠일": 7, "육일": 6, "오일": 5, "사일": 4,
    "삼일": 3, "이일": 2, "일일": 1
    }

   
    # 숫자 형태의 날짜 처리
    if input_text.isdigit():  # 숫자일 경우
        day = int(input_text)
        if 1 <= day <= 31:  # 1부터 31까지의 유효한 날짜인지 확인
            current_month = datetime.now().month
            current_year = datetime.now().year

            parsed_date = datetime(current_year, current_month, day)
            parsed_date = norm_process.early_day(parsed_date.strftime("%Y-%m-%d"))
            return {"status": "100", "result": [{"type": "@date", "norm": parsed_date}]}

    # 이번 주 및 다음 주 처리
    if any(keyword in input_text for keyword in ["이번 주", "이번주", "다음 주", "다음주"]):
        now = datetime.now()
        current_weekday = now.weekday()  # 월요일=0, 일요일=6
        next_name = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

        for day in next_name:
            if day in input_text:
                next_index = next_name.index(day)
                break

        if "다음주" in input_text or "다음 주" in input_text:
            date = now + timedelta(days=(7 - current_weekday) + next_index)
            parsed_date = date.strftime("%Y-%m-%d")
            return {"status": "100", "result": [{"type": "@date", "norm": parsed_date}]}
        else:
            date = now + timedelta(days=(next_index - current_weekday))
            parsed_date =  date.strftime("%Y-%m-%d")
            return {"status": "100", "result": [{"type": "@date", "norm": parsed_date}]}

    # 문자 형태의 날짜 처리
    matched_days = set()  # 이미 추가된 날짜를 저장할 집합
    parsed_dates = []
    for date_text in date_dict.keys():
        if date_text in input_text:
            day = date_dict[date_text]
            current_day = datetime.now().day
            current_month = datetime.now().month
            current_year = datetime.now().year

            # 날짜 생성 및 추가
            parsed_date = datetime(current_year, current_month, day)


            # 날짜 재설정
            parsed_date = datetime(current_year, current_month, day)
            date_str = norm_process.early_day(parsed_date.strftime("%Y-%m-%d"))

            if date_str not in matched_days:  # 중복 체크
                matched_days.add(date_str)
                parsed_dates.append(date_str)
                return {"status": "100", "result": [{"type": "@date", "norm": max(parsed_dates)}]}

    # 날짜 형식인 '9월 13일', '9/13', '2024-09-13' 처리
    date_patterns = [
        r'(\d{1,2})\s*월\s*(\d{1,2})\s*일',  # '9월 13일'
        r'(\d{1,2})/(\d{1,2})',               # '9/13'
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
        r'(\d{4})/(\d{1,2})/(\d{1,2})',        # '2024/09/30'
        r'(\d{4})\.(\d{1,2})\.(\d{1,2})',# '2024-09-13'
        r'(\d{1,2})일'
    ]


    current_year = datetime.now().year
    current_month = datetime.now().month

    for pattern in date_patterns:
        match = re.search(pattern, input_text)

        if match:
            if len(match.groups()) == 2:  # 예: '9월 13일' 또는 '9/13'
                month, day = map(int, match.groups())
                current_year = datetime.now().year
                if 1 <= month <= 12 and 1 <= day <= 31:
                    parsed_date = datetime(current_year, month, day)
                    parsed_date = parsed_date.strftime("%Y-%m-%d")
                    return {"status": "100", "result": [{"type": "@date", "norm": parsed_date}]}
            elif len(match.groups()) == 3:  # 예: '2024-09-13' 또는 '2024/09/30'
                year, month, day = map(int, match.groups())
                if 1 <= month <= 12 and 1 <= day <= 31:
                    parsed_date = datetime(year, month, day)
                    parsed_date = parsed_date.strftime("%Y-%m-%d")
                    return {"status": "100", "result": [{"type": "@date", "norm": parsed_date}]}
            elif len(match.groups()) == 1:  # 예: '28일'
                day = int(match.group(1))
                if 1 <= day <= 31:
                    parsed_date = datetime(current_year, current_month, day)
                    parsed_date = norm_process.early_day(parsed_date.strftime("%Y-%m-%d"))
                    return {"status": "100", "result": [{"type": "@date", "norm": parsed_date}]}

        # 날짜가 '오늘'인 경우 현재 날짜를 반영
    if "오늘" in input_text:
        today = datetime.now()
        parsed_date = today.strftime("%Y-%m-%d")
        return {"status": "100", "result": [{"type": "@date", "norm": parsed_date}]}

    if "내일" in input_text:
        tomorrow = datetime.now() + timedelta(days=1)
        parsed_date = tomorrow.strftime("%Y-%m-%d")
        return {"status": "100", "result": [{"type": "@date", "norm": parsed_date}]}


    int_str = re.findall(r"\d+", input_text)
    if len(int_str)==1:
        day = int(int_str[0])
        if 1 <= day <= 31:  # 1부터 31까지의 유효한 날짜인지 확인
            # current_month = datetime.now().month
            # current_year = datetime.now().year

            parsed_date = datetime(current_year, current_month, day)
            parsed_date = norm_process.early_day(parsed_date.strftime("%Y-%m-%d"))
            return {"status": "100", "result": [{"type": "@date", "norm": parsed_date}]}

    return {"status": "300"}

def norm_month(text):
    # 현재 날짜 기준
    today = datetime.today()
    result_month = None  # 리턴할 월을 저장하는 변수

    # 정규 표현식으로 '월' 또는 '달' 앞에 있는 숫자 추출
    month_num_match = re.search(r'(\d{1,2})(?=\s*월|\s*달)', text)
    if month_num_match:
        month_num = int(month_num_match.group(1))
        if 1 <= month_num <= 12:
            result_month = month_num
    # 문자일 때
    else:
        # '달' 앞에 붙은 특수한 표현 처리
        case_1 = re.search(r'(지난|저번|이번|다음)\s*달', text)
        if case_1:
            case_1_value = case_1.group(1).strip()  # 매칭된 문자열에서 단어 추출
            if case_1_value == "지난" or case_1_value == "저번":
                result_month = (today - timedelta(days=today.day)).month
            elif case_1_value == "이번":
                result_month = today.month
            elif case_1_value == "다음":
                result_month = (today + timedelta(days=31)).month

        # '월' 앞에 붙은 문자 처리
        case_2 = re.findall(r'((일|이|삼|사|오|유|육|칠|팔|구|시|십| |)*(?=월))', text)


        month_mapping = {
            "일": 1, "이": 2, "삼": 3, "사": 4,
            "오": 5, "유": 6, "칠": 7, "팔": 8,
            "구": 9, "시": 10, "십": 10, "십일": 11, "십이": 12
        }
        if case_2:
            case_2_value = case_2[0][0].strip()
            case_2_value = re.sub(r'\s+', '', case_2_value)

            result_month = month_mapping.get(case_2_value)
        case_3 = re.findall(r'(?:^|[^0-9])(1[0-2]|[1-9])(?=[^0-9]|$)', text)
        if case_3:
            if len(case_3) ==1:
                result_month = int(case_3[0])


    if result_month is None or (result_month < 1 or result_month > 12):
        return {"status": "300"}

    return {"status": "100", "result": [{"type": "@month", "norm": str(result_month)}]}

def norm_email(user_id):
    # 입력 문자열에서 처음과 끝의 한글 문자 및 공백을 제거
    cleaned_input = re.sub(r'^[가-힣\s]+|[가-힣\s]+$', '', user_id)
    
    # 이메일 형식을 캡처하는 정규 표현식
    regex = r'([a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+[.]?\w{2,3})'
    
    # 정규 표현식으로 이메일 주소만 추출
    match = re.search(regex, cleaned_input)
    
    if not match:
        return {"status": "300"}
    
    # 매치된 이메일 주소 반환
    email = match.group(1)
    
    return {"status": "100", "result": [{"type": "@email", "norm": email}]}

async def norm_entity(domain_id, input_text):
    
    entity_list = await ent.entity_process(domain_id, input_text)
    """
    ner_tags = ["히스로공항", "히스로", "런던", "인천", "인청공항"]  # 긴 문자열을 먼저 정의
    pattern = r'(' + '|'.join(map(re.escape, ner_tags)) + r')'

    # 정규 표현식으로 입력 텍스트에서 매칭되는 부분 찾기
    matches = re.findall(pattern, input_text)

    # 매칭 결과에서 가장 긴 일치 찾기
    if matches:
        longest_match = max(matches, key=len)  # 모든 매칭 중에서 가장 긴 것을 선택
    """
    if entity_list:
        return {'status': "100", 'result': [{'type': '@entity', 'norm': entity_list}]}
    
    else:
        return {'status': "300"}  # 빈 리스트를 포함한 반환값

def norm_number(input_text):
    # 한글 숫자와 정수의 매핑
    korean_to_num = {
            '일': 1, '하나': 1, '첫': 1, '처음':1,
        '이': 2, '둘': 2, '두': 2,
        '삼': 3, '셋': 3, '세': 3,
        '사': 4, '넷': 4, '네': 4,
        '오': 5, '다섯': 5,
        '육': 6, '여섯': 6,
        '칠': 7, '일곱': 7,
        '팔': 8, '여덟': 8,
        '구': 9, '아홉': 9,
        '십': 10, '열': 10,
        '백': 100, '천': 1000,
        "만": 10**4, "억": 10**8, "조": 10**12, "경": 10**16,
        "스무": 20, "스물": 20, "서른": 30, "마흔": 40, "쉰": 50,
        "예순": 60, "일흔": 70, "여든": 80, "아흔": 90
    }

    suffixes = r'(개|명|번째|째|살|마리|번|가지|곳|군데|사람|명)'
    
    # 숫자 및 한글 숫자 표현을 추출하기 위한 정규 표현식
    korean_numbers = r'(하나|일|첫|처음|둘|이|두|셋|세|삼|넷|네|다섯|오|여섯|육|일곱|칠|팔|여덟|구|아홉|구|십|열|백|천|만|억|조|경|스무|스물|서른|마흔|쉰|예순|일흔|여든|아흔|[0-9]+)'

    # 입력 텍스트가 오직 숫자만 있는지 확인
    if re.fullmatch(r'\d+', input_text):  # 정수만 포함된 경우
        return {"status": "100", "result": [{"type": "@number", "norm": input_text}]}
    
    # 접미사 앞의 숫자 표현을 추출
    match = re.search(r'(' + korean_numbers + r'(\s+)?)+' + suffixes, input_text)
    if match:
        cleaned_text = match.group(0)
        cleaned_text = re.sub(suffixes, '', cleaned_text).strip()  # 접미사 제거 및 공백 정리
    else:
        # 접미사가 없는 경우 처리
        match_simple = re.search(r'(' + korean_numbers + r'(\s+)?)+', input_text)
        if match_simple:
            cleaned_text = match_simple.group(0).strip()
            cleaned_text = re.sub(r'\s+', '', cleaned_text)  # 공백 제거
        else:
            cleaned_text = input_text.strip()  # 숫자가 없으면 원본 그대로
    
    if cleaned_text.isdigit():
        return {"status": "100", "result": [{"type": "@number", "norm": str(cleaned_text)}]}
    

    num = 0
    temp = 0
    current_value = 0

    # 큰 단위부터 매칭해 하나씩 처리
    words = re.findall(
        r'하나|일|첫|처음|둘|이|두|셋|세|삼|넷|네|다섯|오|여섯|육|일곱|칠|팔|여덟|아홉|구|십|열|백|천|만|억|조|경|스무|스물|서른|마흔|쉰|예순|일흔|여든|아흔',
        cleaned_text
    )


    # 잘못된 문자가 포함된 경우 처리
    if re.search(r'[^하나|일|첫|처음|둘|이|두|셋|세|삼|넷|네|다섯|오|여섯|육|일곱|칠|팔|여덟|아홉|구|십|열|백|천|만|억|조|경|스무|스물|서른|마흔|쉰|예순|일흔|여든|아흔\s]', cleaned_text):
        return {"status": "300"}

    for word in words:
        if word in korean_to_num:
            current_val = korean_to_num[word]
            if current_val >= 10 and current_val < 10000:  # '십', '백', '천'과 같은 단위는 곱해서 처리
                temp += (current_value or 1) * current_val
                current_value = 0
            elif current_val >= 10000:  # '만', '억', '조' 등 큰 단위는 별도로 처리
                temp = (temp + (current_value or 1)) * current_val
                num += temp
                temp = 0
                current_value = 0
            else:
                current_value += current_val

    num += temp + current_value
    
    # "3개"와 같은 경우도 처리
    digit_match = re.search(r'(\d+)\s*개', input_text)
    if digit_match:
        num = int(digit_match.group(1))  # 숫자 추출
    
    return {"status": "100", "result": [{"type": "@number", "norm": str(num)}]}

def norm_phone(input_text):
    # 숫자와 한글 숫자를 매핑
    num_dict = {
        '공': '0', '영': '0', '일': '1', '이': '2', '삼': '3',
        '사': '4', '오': '5', '육': '6', '칠': '7', '팔': '8', '구': '9'
    }

    # 한글 숫자를 아라비아 숫자로 변환
    for korean_num, arabic_num in num_dict.items():
        input_text = input_text.replace(korean_num, arabic_num)

    # 정규표현식으로 숫자만 추출
    phone_number = re.sub(r'\D', '', input_text)

    # 전화번호 길이 확인 (휴대폰 번호 10자리 또는 11자리)
    if len(phone_number) == 10 or len(phone_number) == 11:
        return {"status": "100", "result": [{"type": "@phone", "norm": phone_number}]}
    else:
        return {"status": "300"}

def norm_yes_no(input_text):
    response = None
    # 긍정적인 응답
    positive_responses = ['yes', 'y', '예', '응', '그래', '네']
    # 부정적인 응답
    negative_responses = ['no', 'n', '아니오', '아니', '아니요', '안이']

    # 입력값을 소문자로 변환하여 확인
    text_lower = input_text.lower()

    # 긍정적인 응답 확인
    if any(positive in text_lower.split() for positive in positive_responses):
        response = 'Y'
    # 부정적인 응답 확인
    elif any(negative in text_lower.split() for negative in negative_responses):
        response = 'N'

    if response is not None:
        return {"status": "100", "result": [{"type": "@yes_no", "norm": response}]}
    else:
        return {"status": "300"}

def norm_date_time(input_text):
    out_status = "100"
    
    date_norm = norm_date(input_text)
    time_norm = norm_time(input_text)
  
    
    # 두 개의 결과 상태가 "100"인지 확인
    if date_norm["status"] == "100" and time_norm["status"] == "100":
        return {"status": "100", "result": [{"type": "@date_time", "norm": f'{date_norm["result"][0]["norm"]} {time_norm["result"][0]["norm"]}'}]}
    else:
        return {"status": "300"} 

async def norm_plural(domain_id, norm_type, text):
    results = []  # 결과를 저장할 리스트
    overall_status = "100"  # 초기 상태

    value = text
    for type_ in norm_type:
        if type_ == "@date":
            date_result = norm_date(value)  # date 함수 호출
            if date_result["status"] == "300":
                overall_status = "300"
            else:
                results.append(date_result["result"][0])
        
        elif type_.startswith("@choice"):
            choice_result = norm_choice(type_, value)
            if choice_result["status"] == "300":
                overall_status = "300"
            else:
                results.append(choice_result["result"][0])

        elif type_ == "@time":
            time_result = norm_time(value)  # time 함수 호출
            if time_result["status"] == "300":
                overall_status = "300"
            else:
                results.append(time_result["result"][0])

        elif type_ == "@year":
            year_result = norm_year(value)  # year 함수 호출
            if year_result["status"] == "300":
                overall_status = "300"
            else:
                results.append(year_result["result"][0])

        elif type_ == "@day":
            day_result = norm_day(value)  # day 함수 호출
            if day_result["status"] == "300":
                overall_status = "300"
            else:
                results.append(day_result["result"][0])

        elif type_ == "@month":
            month_result = norm_month(value)  # month 함수 호출
            if month_result["status"] == "300":
                overall_status = "300"
            else:
                results.append(month_result["result"][0])

        elif type_ == "@date_time":
            date_time_result = norm_date_time(value)  # date_time 함수 호출
            if date_time_result["status"] == "300":
                overall_status = "300"
            else:
                results.append(date_time_result["result"][0])

        elif type_ == "@email":
            email_result = norm_email(value)  # email 함수 호출
            if email_result["status"] == "300":
                overall_status = "300"
            else:
                results.append(email_result["result"][0])

        elif type_ == "@entity":
            entity_result = await norm_entity(domain_id, value)  # entity 함수 호출
            if entity_result["status"] == "300":
                overall_status = "300"
            else:
                results.append(entity_result["result"][0])

        elif type_ == "@number":
            number_result = norm_number(value)  # number 함수 호출
            if number_result["status"] == "300":
                overall_status = "300"
            else:
                results.append(number_result["result"][0])

        elif type_ == "@phone":
            phone_result = norm_phone(value)  # phone 함수 호출
            if phone_result["status"] == "300":
                overall_status = "300"
            else:
                results.append(phone_result["result"][0])

        elif type_ == "@yes_no":
            yes_no_result = norm_yes_no(value)  # yes_no 함수 호출
            if yes_no_result["status"] == "300":
                overall_status = "300"
            else:
                results.append(yes_no_result["result"][0])

    # 전체 상태가 300인 경우 result는 빈 리스트로 설정
    if overall_status == "300":
        return {"status": overall_status}
    else:
        return {"status": overall_status, "result": results}

async def norm_engine(domain_id, norm_type, text):
    if len(norm_type) >= 2:
        plural_result = await norm_plural(domain_id, norm_type, text)
        return plural_result
    else:
        type_ = norm_type[0]
        value_text = text
        
        if type_.startswith("@choice"):
            choice_result = norm_choice(type_,value_text)
            return choice_result

        if type_ == "@date":
            date_result = norm_date(value_text)  # date 함수 호출
            return date_result

        elif type_ == "@time":
            time_result = norm_time(value_text)  # time 함수 호출
            return time_result

        elif type_ == "@year":
            year_result = norm_year(value_text)  # year 함수 호출
            return year_result

        elif type_ == "@day":
            day_result = norm_day(value_text)  # day 함수 호출
            return day_result

        elif type_ == "@month":
            month_result = norm_month(value_text)  # month 함수 호출
            return month_result

        elif type_ == "@date_time":
            date_time_result = norm_date_time(value_text)  # date_time 함수 호출
            return date_time_result

        elif type_ == "@email":
            email_result = norm_email(value_text)  # email 함수 호출
            return email_result

        elif type_ == "@entity":
            entity_result = await norm_entity(domain_id, value_text)  # entity 함수 호출
            return entity_result

        elif type_ == "@number":
            number_result = norm_number(value_text)  # number 함수 호출
            return number_result

        elif type_ == "@phone":
            phone_result = norm_phone(value_text)  # phone 함수 호출
            return phone_result

        elif type_ == "@yes_no":
            yes_no_result = norm_yes_no(value_text)  # yes_no 함수 호출
            return yes_no_result

if __name__ == "__main__":
    print(norm_engine("d2864098712", ["@entity"], "공유형 모기지 예약할건데 제가 어제 코로나19에 걸려서 좀 안좋아요"))

    #print(norm_engine({
    #"user_id": "admin@ktcs.co.kr", "domain_id": "t_mega_chatbot", "type": ["@choice:사과,딸기,복숭아"], "text": "사과"}))
    #print(norm_engine({
    #"user_id": "admin@ktcs.co.kr", "domain_id": "t_mega_chatbot", "type": ["@choice:사과,딸기,복숭아", "@entity"], "text": "두번째 주시고 히스로공항이요"}))
    #print(norm_engine({
    #"user_id": "admin@ktcs.co.kr", "domain_id": "t_mega_chatbot", "type": ["@time", "@entity"], "text": "오후 세시 삼십분에 히스로공항이요."}))
