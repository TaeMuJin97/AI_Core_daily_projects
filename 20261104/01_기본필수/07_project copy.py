"""
OpenCV 이미지·영상 전처리 파이프라인(개요)

처리 과정:
1. 이미지 읽기
2. Grayscale 변환
3. Resize (160×120)
4. Canny Edge 검출
5. 이미지 및 영상 저장
6. CSV 결과 저장
7. 결과 파일 재검증
"""

from pathlib import Path
import csv
import cv2
import numpy as np


# ============================================================
# 1. 전역 설정
# ============================================================

# 현재 Python 파일이 위치한 디렉터리
ROOT = Path(__file__).resolve().parent

# 전처리 대상 이미지 목록
IMAGE_FILES = [
    "scene.png",
    "noisy.png",
    "objects.png"
]

# 전처리 설정
OUTPUT_SIZE = (160, 120)
CANNY_LOW = 80
CANNY_HIGH = 160


# ============================================================
# 2. 이미지 전처리 함수
# ============================================================

def preprocess_frame(frame):
    """
    입력 이미지를 Grayscale → Resize → Canny 순서로 처리합니다.

    Parameters
    ----------
    frame : np.ndarray
        OpenCV에서 읽은 BGR 이미지

    Returns
    -------
    gray : np.ndarray
        Grayscale 이미지

    small : np.ndarray
        160×120으로 축소된 이미지

    edge : np.ndarray
        Canny Edge 검출 결과
    """

    # ① BGR → Grayscale
    # 색상 정보를 제거하고 밝기 정보만 사용
    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    # ② Resize
    # 이미지 크기를 160×120으로 축소하여 연산량 감소
    small = cv2.resize(
        gray,
        OUTPUT_SIZE,
        interpolation=cv2.INTER_AREA
    )

    # ③ Canny Edge Detection
    # 밝기가 급격하게 변하는 경계 검출
    # 80: 하한 임계값, 160: 상한 임계값
    edge = cv2.Canny(
        small,
        CANNY_LOW,
        CANNY_HIGH
    )

    return gray, small, edge


# ============================================================
# 3. 이미지 파일 처리 함수
# ============================================================

def process_images():
    """
    이미지 3개를 전처리하고 결과 PNG 파일을 저장합니다.

    이미지마다 다음 결과를 저장:
    - Grayscale
    - Resize
    - Edge

    총 3 × 3 = 9개의 PNG 파일 생성
    """

    rows = []

    for filename in IMAGE_FILES:

        # 이미지 파일 읽기
        image = cv2.imread(str(ROOT / filename))

        # 파일 읽기 실패 시 명확하게 오류 발생
        if image is None:
            raise FileNotFoundError(
                f"이미지 읽기 실패: {filename}"
            )

        # 공통 전처리 함수 호출
        gray, small, edge = preprocess_frame(image)

        # 파일명에서 확장자 제거
        # 예: scene.png → scene
        stem = Path(filename).stem

        # 처리 단계별 이미지 저장
        outputs = {
            "gray": gray,
            "small": small,
            "edge": edge
        }

        for step, result in outputs.items():
            output_path = ROOT / f"p07_{stem}_{step}.png"

            # 이미지 저장 성공 여부 확인
            if not cv2.imwrite(str(output_path), result):
                raise RuntimeError(
                    f"이미지 저장 실패: {output_path}"
                )

        # 결과 통계 수집
        # np.count_nonzero(edge):
        # Edge 이미지에서 0이 아닌 픽셀 개수
        rows.append([
            filename,
            image.shape[1],   # 원본 너비
            image.shape[0],   # 원본 높이
            small.shape[1],   # 출력 너비
            small.shape[0],   # 출력 높이
            int(np.count_nonzero(edge))
        ])

        print(f"[IMAGE] {filename} 처리 완료")

    return rows


# ============================================================
# 4. 영상 처리 함수
# ============================================================

def process_video():
    """
    sample.avi를 읽어 각 프레임에 Edge 검출을 적용하고
    p07_video.avi로 저장합니다.

    입력 영상의 FPS를 유지하고 출력 해상도는 160×120입니다.

    Returns
    -------
    count : int
        실제로 처리한 프레임 수
    """

    input_path = ROOT / "sample.avi"
    output_path = ROOT / "p07_video.avi"

    # ① 입력 영상 열기
    cap = cv2.VideoCapture(str(input_path))

    if not cap.isOpened():
        raise RuntimeError("입력 영상 열기 실패")

    writer = None
    count = 0

    try:
        # ② 원본 영상 FPS 확인
        fps = cap.get(cv2.CAP_PROP_FPS)

        if not np.isfinite(fps) or fps <= 0:
            raise RuntimeError("영상 FPS를 확인할 수 없습니다.")

        # ③ 출력 영상 Writer 생성
        # MJPG 코덱, 원본 FPS, 160×120 해상도 사용
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")

        writer = cv2.VideoWriter(
            str(output_path),
            fourcc,
            fps,
            OUTPUT_SIZE
        )

        if not writer.isOpened():
            raise RuntimeError("영상 Writer 생성 실패")

        print("Writer:", writer.isOpened())

        # ④ 영상의 모든 프레임을 순차 처리
        while True:

            # 영상에서 프레임 한 장 읽기
            ok, frame = cap.read()

            # 마지막 프레임 또는 읽기 실패 시 종료
            if not ok:
                break

            # 이미지와 동일한 전처리 함수 사용
            _, _, edge = preprocess_frame(frame)

            # ⑤ Grayscale → BGR
            # VideoWriter가 사용할 3채널 형태로 변환
            # 실제 원본 색상이 복원되는 것은 아님
            edge_bgr = cv2.cvtColor(
                edge,
                cv2.COLOR_GRAY2BGR
            )

            # ⑥ 처리된 프레임을 출력 영상에 저장
            writer.write(edge_bgr)

            count += 1

    finally:
        # 오류 여부와 관계없이 영상 리소스 해제
        cap.release()

        if writer is not None:
            writer.release()

    print(f"[VIDEO] 처리 완료: {count} Frames")

    return count


# ============================================================
# 5. CSV 결과 저장 함수
# ============================================================

def save_summary(rows):
    """
    이미지별 전처리 통계를 CSV 파일로 저장합니다.
    """

    output_path = ROOT / "p07_summary.csv"

    with open(
        output_path,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.writer(f)

        # CSV 헤더 작성
        writer.writerow([
            "source",
            "source_w",
            "source_h",
            "output_w",
            "output_h",
            "edge_pixels"
        ])

        # 이미지별 분석 결과 저장
        writer.writerows(rows)

    print("[CSV] 요약 결과 저장 완료")


# ============================================================
# 6. 결과 검증 함수
# ============================================================

def verify_outputs(image_count, frame_count):
    """
    저장된 이미지와 영상을 다시 읽어 결과를 검증합니다.

    단순히 저장 성공 메시지만 확인하지 않고
    실제 출력 파일이 정상적으로 열리는지 확인합니다.
    """

    # ① 저장된 Edge 이미지 재읽기
    image_path = ROOT / "p07_scene_edge.png"

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise RuntimeError("출력 이미지 재읽기 실패")

    # ② 저장된 영상 재읽기
    video_path = ROOT / "p07_video.avi"
    check = cv2.VideoCapture(str(video_path))

    if not check.isOpened():
        raise RuntimeError("출력 영상 재읽기 실패")

    try:
        saved_frames = int(
            check.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        saved_fps = check.get(cv2.CAP_PROP_FPS)

        # 실제 프레임을 읽어 재디코딩 가능 여부 확인
        decoded_frames = 0

        while True:
            ok, _ = check.read()
            if not ok:
                break
            decoded_frames += 1

    finally:
        check.release()

    # ③ 검증 결과 출력
    print("\n" + "=" * 55)
    print("        OpenCV 전처리 결과 검증")
    print("=" * 55)

    print(f"처리 이미지 수     : {image_count}")
    print(f"처리 영상 Frame 수 : {frame_count}")
    print(f"출력 이미지 Shape  : {image.shape}")
    print(f"저장 영상 Frame 수 : {saved_frames}")
    print(f"재읽기 Frame 수    : {decoded_frames}")
    print(f"저장 영상 FPS      : {saved_fps:.2f}")

    # ④ 주요 결과 일치 여부 확인
    passed = (
        image.shape == (120, 160)
        and saved_frames == frame_count
        and decoded_frames == frame_count
    )

    print("-" * 55)
    print("최종 검증:", "PASS" if passed else "FAIL")
    print("=" * 55)

    if not passed:
        raise RuntimeError("출력 파일 검증 실패")


# ============================================================
# 7. Main 함수: 전체 파이프라인 실행
# ============================================================

def main():
    """
    전체 OpenCV 전처리 작업의 실행 흐름을 관리합니다.

    1. 이미지 처리
    2. 영상 처리
    3. 결과 CSV 저장
    4. 출력 파일 검증
    """

    print("\n[START] OpenCV 전처리 파이프라인\n")

    # 이미지 전처리 및 결과 통계 수집
    rows = process_images()

    # 영상 프레임 전처리 및 저장
    frame_count = process_video()

    # 이미지 분석 결과 CSV 생성
    save_summary(rows)

    # 실제 출력 파일 재읽기 및 검증
    verify_outputs(
        image_count=len(rows),
        frame_count=frame_count
    )

    print("\n[DONE] 전체 작업 완료")
    print("결과: p07_ PNG 9개 + AVI 1개 + CSV 1개")


# ============================================================
# 8. 프로그램 시작점
# ============================================================

# 이 파일을 직접 실행했을 때만 main() 호출
# 다른 Python 파일에서 import하면 자동 실행되지 않음
if __name__ == "__main__":
    main()
