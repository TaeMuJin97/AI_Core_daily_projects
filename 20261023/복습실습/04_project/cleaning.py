"""정제 담당 모듈. 파일을 읽거나 화면에 출력하지 않고 값만 돌려줍니다."""
from validation import check_row, reject_record


def clean_orders(rows):
    """기본·응용 프로젝트용. 제공된 정상 주문 5행을 새 List로 반환합니다."""
    # TODO P_B1: 정상 원본 행을 공백·숫자 정제한 새 목록으로 반환하세요.
    raise NotImplementedError("P_B1: 정상 원본 행을 공백·숫자 정제한 새 목록으로 반환하세요.")


def clean_orders_advanced(rows):
    """선택 심화용. (정상 List, 제외 List)를 반환합니다."""
    # TODO P_D1: 잘못된 행과 중복 ID를 이유와 함께 분리하세요.
    raise NotImplementedError("P_D1: 잘못된 행과 중복 ID를 이유와 함께 분리하세요.")
