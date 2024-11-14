from datetime import datetime
import re

def early_day(date):
    parsed_date_obj = datetime.strptime(date, "%Y-%m-%d")
    point_day = parsed_date_obj.day
    current_day = datetime.now().day
    current_month = parsed_date_obj.month
    current_year = parsed_date_obj.year
    # day가 오늘 날짜보다 작으면 다음 달로 처리
    if point_day < current_day:
        if current_month == 12:
            current_year += 1
            current_month = 1
        else:
            current_month += 1

            # 업데이트된 year, month, day로 새로운 parsed_date 생성
        parsed_date_obj = datetime(current_year, current_month, point_day)
        result = parsed_date_obj.strftime("%Y-%m-%d")

    else:
        # 조건이 맞지 않으면 원래 날짜 반환
        result = date
        
    return result

def korean_number_to_int(kr_str):
    current_year = datetime.now().year
    current_century = current_year // 100 * 100  # 현재 세기 (2000, 1900 등)

    numbers = {
        "일": 1, "이": 2, "삼": 3, "사": 4, "오": 5, "육": 6, "칠": 7, "팔": 8, "구": 9,
        "십": 10, "백": 100, "천": 1000,
        "만": 10**4, "억": 10**8, "조": 10**12, "경": 10**16
    }

    # 숫자 변환
    result = 0
    temp_result = 0
    current_value = 0

    for char in kr_str:
        if char in numbers:
            unit_value = numbers[char]
            if unit_value >= 10:
                if unit_value >= 10000:
                    result += (temp_result + (current_value or 1)) * unit_value
                    temp_result = 0
                else:
                    temp_result += (current_value or 1) * unit_value
                current_value = 0
            else:
                current_value = unit_value

    result += temp_result + current_value

    # 두 자리 연도 처리 (2000년대 보정)
    if result < 100:
        result += current_century

    return result if result > 2000 else None


#def split_datetime(input_text):
#    # 시간 패턴을 탐지하여 분리
#    time_pattern = r'(오전|오후|정오|자정|\bAM\b|\bPM\b|\d{1,2}시|\d{1,2}:\d{2}|' \
#               r'(한|두|세|네|다섯|여섯|일곱|여덟|아홉|열|' \
#               r'열한|열두|열세|열네|열다섯|열여섯|열일곱|열여덟|열아홉|' \
#               r'스물|스물한|스물두|스물세|스물네)시)'
#
#    # 시간 패턴을 찾고, 그 위치를 기준으로 날짜와 시간 구분
#    time_match = re.search(time_pattern, input_text)
#
#    if time_match:
#        date_part = input_text[:time_match.start()].strip()  # 날짜 부분
#        time_part = input_text[time_match.start():].strip()  # 시간 부분
#        return date_part, time_part
#    else:
#        return 'False'
