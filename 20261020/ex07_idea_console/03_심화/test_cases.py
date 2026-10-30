# -*- coding: utf-8 -*-
"""실습 07 심화: main.py를 완성한 후 테스트 세 개를 직접 작성한다."""
# [제공 코드] import와 assert는 검사 도구를 사용하기 위한 최소 형태만 제공한다.
# assert 조건, 메시지: 조건이 False이면 실패하고 메시지를 보여준다. -O 옵션 없이 실행한다.
from main import add_idea, normalize_roles, count_by_difficulty


def test_normalize_roles():
    # TODO 1: 중복·빈 역할을 섞은 입력을 만들고 기대되는 역할 List와 비교하세요.
    # 작성 패턴: actual = 함수(입력); assert actual == 직접_적은_기대값, actual
    raise NotImplementedError("TODO 1: 역할 정리 테스트")


def test_duplicate_does_not_change_data():
    # TODO 2: 같은 이름을 공백·대소문자만 바꾸어 두 번 등록해 보세요.
    # 성공 여부뿐 아니라 List 길이와 기존 데이터가 그대로인지도 확인하세요.
    raise NotImplementedError("TODO 2: 중복과 상태 보존 테스트")


def test_empty_statistics():
    # TODO 3: 빈 List의 난이도 통계에 키 세 개와 0이 모두 있는지 확인하세요.
    raise NotImplementedError("TODO 3: 빈 통계 테스트")


if __name__ == "__main__":
    test_normalize_roles()
    print("PASS 1: 역할 정리")
    test_duplicate_does_not_change_data()
    print("PASS 2: 중복 등록 시 원본 보존")
    test_empty_statistics()
    print("PASS 3: 빈 데이터 통계")
