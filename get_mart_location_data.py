import pandas as pd
import requests
from tqdm import tqdm


def get_api_key(key_file_path):
    api_key = open(key_file_path).read().strip()
    return api_key

def search_places(query):
    
    MAX_NUM_PAGE = 45
    places = []
    
    for i in range(1, MAX_NUM_PAGE + 1):
        url = 'https://dapi.kakao.com/v2/local/search/keyword?query={}&page={}&size=15&category_group_code=MT1'.format(query, i)
        headers = {
            "Authorization": f"KakaoAK {KAKAO_MAP_API_KEY}"
        }
        _places = requests.get(url, headers = headers).json()['documents']
        places += _places
        
    return places

def remove_duplicated_places(places):
    unique_places = []
    unique_place_names = set()
    for place in places:
        if place['place_name'] not in unique_place_names:
            unique_places.append(place)
            unique_place_names.add(place['place_name'])
    return unique_places

def search_places_with_sido_names(query, sido_names):
    places = []
    for sido_name in tqdm(sido_names):
        query_for_sido = '{} {}'.format(sido_name, query)
        places += search_places(query_for_sido)
    places = remove_duplicated_places(places)
    return places

def get_homeplus_places(sido_names):
    
    def is_homeplus_place_name(name):
        if '익스프레스' in name:
            return False
        if '홈플러스' not in name:
            return False
        return True
    print('홈플러스 위치 정보 수집 중..')
    places = search_places_with_sido_names('홈플러스', sido_names)
    places = [x for x in places if is_homeplus_place_name(x['place_name'])]
    print('홈플러스 위치 정보 수집 완료!')
    return places

def get_emart_places(sido_names):
    
    def is_emart_place_name(name):
        if any([x in name for x in ['에브리데이', '트레이더스', '노브랜드', '몰리스']]):
            return False
        if '이마트' not in name:
            return False
        return True
    print('이마트 위치 정보 수집 중..')
    places = search_places_with_sido_names('이마트', sido_names)
    places = [x for x in places if is_emart_place_name(x['place_name'])]
    print('이마트 위치 정보 수집 완료!')
    return places

def get_lottemart_places(sido_names):
    
    def is_lottemart_place_name(name):
        if any([x in name for x in ['슈퍼', '빅마켓', '마켓디', '맥스']]):
            return False
        if '롯데마트' not in name:
            return False
        return True
    print('롯데마트 위치 정보 수집 중..')
    places = search_places_with_sido_names('롯데마트', sido_names)
    places = [x for x in places if is_lottemart_place_name(x['place_name'])]
    print('롯데마트 위치 정보 수집 완료!')
    return places


if __name__ == '__main__':

    KAKAO_MAP_API_KEY_FILE = './map_api_key.txt'
    KAKAO_MAP_API_KEY = get_api_key(KAKAO_MAP_API_KEY_FILE) 

    SIDO_NAMES = ['서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시',
                  '대전광역시', '울산광역시', '세종특별자치시', '경기도',
                  '강원도', '충청북도', '충청남도', '전라북도', '전라남도',
                  '경상북도', '경상남도', '제주특별자치도']

    homeplus_places = get_homeplus_places(SIDO_NAMES)
    emart_places = get_emart_places(SIDO_NAMES)
    lottemart_places = get_lottemart_places(SIDO_NAMES)

    mart_location_data = pd.DataFrame(homeplus_places + emart_places + lottemart_places)
    mart_location_data.to_excel('mart_location_data.xlsx', index=False)
