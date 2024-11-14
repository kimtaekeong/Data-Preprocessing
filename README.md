# 자유 발화 정규화

## normalization.py

### norm_time
> input
- “text”: “오늘 3시30분에 만나.”
- “text”: “이십분에 갈게”
- “text”: “두시 삼십분에 만나자”
- “text”: “자정에 잘려고”
- “text”: “정오에 만날까 ?”
> output
- 'HH:mm' : 24h 으로 리턴

### norm_year
> input
- “text”: “올해 너무 바빴어”
- “text”: “내년은 뭐할거야”
- “text”: “2025에 만나자”
- “text”: “2024년”
- “text”: “이천십팔년에 했어”
> output
- 'YYYY' 으로 리턴

### norm_day
> input
- “text”: “월요일”
- “text”: “워료일”
- “text”: “Mon”
- “text”: “월”
- “text”: “Monday”
> output
- 월: ”1” ~ 일: ”7” 으로 리턴

### norm_date
### norm_month
### norm_date_time
### norm_email
> input
- “text”: “asdfg@gmail.com입니다”
- “text”: "아 제거는 rothhdk@daum.net이요”
> output
- "____@____.___" or "____@____.__.__" 
### norm_entity
### norm_number
> input
- “text”: “010-1234-5678으로 보내줘”
- “text”: "01012345678입니다”
- “text”: “공일공에 일이삼사에 오육칠팔”
> output
- "010********" 10개 or 11개
### norm_yes_no
### norm_plural(복수개)

## norm_preprocess.py
### early_day
"day"만 들어온 경우, 오늘 날짜보다 숫자가 작으면 다음달로, 숫자가 같거나 크면 이번달로 리턴
### korean_number_to_int
문자 형태의 숫자가 들어온 경우 숫자로 리턴

## entity.py
> DB와 연동 후 자유 발화 중 DB에 저장된 엔티티 출력
