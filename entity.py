import asyncio
import logging
from sqlalchemy import select, text
import re
from core.db_connect import Session, close_db

logger = logging.getLogger(__name__)


async def load_entity_list(domain_id):
    try:
        async with Session() as session:
            sql = text(f"SELECT DOMAIN_ID, FILENAME, ENTITY, DATA FROM NLU_API_DICTIONARY WHERE DOMAIN_ID = '{domain_id}'")
            result = await session.execute(sql)
            rows = result.fetchall()
            domain_id  = [row.DOMAIN_ID for row in rows]
            filename_datas  = [row.FILENAME for row in rows]
            entity_datas = [row.ENTITY for row in rows]
            tag_datas = [row.DATA for row in rows]

            return filename_datas, entity_datas, tag_datas
    
    except Exception as e:
        logger.error("Error loading question list: %s", e)
        raise


def user_dictionary(filename_datas, entity_datas):
    user_list = []
    for index, filename in enumerate(filename_datas):
        if filename == "ner_user.txt":
            user_list.append(entity_datas[index])

    return user_list

def system_dictionary(filename_datas, entity_datas):
    system_list = []
    for index, filename in enumerate(filename_datas):
        if filename == "ner.txt":
            system_list.append(entity_datas[index])
    
    return system_list

def synuser_dictionary(filename_datas, entity_datas, tag_datas):
    synuser_dict = {}
    for index, filename in enumerate(filename_datas):
        if filename == "syn-user.txt":
            key = entity_datas[index]
            value = tag_datas[index]
            synuser_dict[key] = value
            
    return synuser_dict

def coined_dictionary(filename_datas, entity_datas):
    coined_list = []
    for index, filename in enumerate(filename_datas):
        if filename == "coined.txt":
            coined_list.append(entity_datas[index])

    return coined_list

def tag_dictionary(filename_datas, entity_datas, tag_datas):
    tag_dict = {}
    for index, filename in enumerate(filename_datas):
        if filename == "ner-tags.txt":
            key = entity_datas[index]
            value = tag_datas[index]
            tag_dict[key] = value

    return tag_dict

async def entity_process(domain_id, input_text):
    filename_datas, entity_datas, tag_datas = await load_entity_list(domain_id)
    user_list = user_dictionary(filename_datas, entity_datas)
    system_list = system_dictionary(filename_datas, entity_datas)
    synuser_dict = synuser_dictionary(filename_datas, entity_datas, tag_datas)
    coined_list = coined_dictionary(filename_datas, entity_datas)
    tag_dict = tag_dictionary(filename_datas, entity_datas, tag_datas)


    ner_tags = []
    for key, values in synuser_dict.items():
        ner_tags.extend(values.split(", "))

    ner_tags.sort(key=len, reverse=True)  
    pattern = r'(' + '|'.join(map(re.escape, ner_tags)) + r')'

    # 입력 텍스트에서 매칭되는 부분 찾기
    matches = re.findall(pattern, input_text)

    # 가장 긴 매칭을 찾아 치환하기1
    for match in matches:
        for key, values in synuser_dict.items():
            if match in values.split(", "):
                input_text = input_text.replace(match, key)
                break  # 첫 번째 매칭된 키로 치환 후 종료 
    # print(input_text)
    dict_data = list(set(user_list+system_list+coined_list+list(synuser_dict.keys())))

    pattern = r'(' + '|'.join(map(re.escape, dict_data)) + r')'
    entity = re.findall(pattern, input_text)
    
    pattern = r'(' + '|'.join(map(re.escape,list(tag_dict.keys()))) + r')'
    tags = re.findall(pattern, input_text)
    entity = entity + tags
    
    if len(tags) == 0:
        pass
    elif len(tags) ==1:
        entity = entity + [tag_dict[tags[0]]]
    elif len(tags)>=2:
        for i in range(len(tags)):
            entity = entity + [tag_dict[tags[i]]]

    entity = sorted(set(entity), key = lambda x:entity.index(x)) 
    if '' in entity:
        entity.remove('')
    print(entity)
    return entity


    
if __name__ == "__main__":
    asyncio.run(entity_process('d2864098712','공유형 모기지 예약하려고 하는데요 제가 어제 코로나19에 걸려서 목이 좀 안좋아요. 상품 뭐있나요 ? 지갑이 어디있더라'))


