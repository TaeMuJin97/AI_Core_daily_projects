"""
==============================================================================
[실습 보고서: 04_train.py - YOLO26 아키텍처 로드 및 1 Epoch 학습 파이프라인 연결 점검 (Smoke Test)]
1. 실험 목적: 데이터셋 설정 파일(p04_dataset.yaml)을 동적으로 생성하고, 무작위 초기화된 YOLO26n 모델에
              연결하여 1 Epoch 동안 데이터 로드 → 순전파 → 손실 계산 → 역전파 → 체크포인트 저장의
              전체 학습 파이프라인이 에러 없이 끝까지 도는지 점검(Smoke Test)함.
2. 핵심 개념 및 엔지니어링 포인트:
   - Smoke Test(연기 테스트): 본격적인 장시간 학습 전에, 소규모 설정(epochs=1, imgsz=160, batch=4)으로
     데이터 경로, 라벨 포맷, 출력 폴더 생성 등 파이프라인 연결 상태를 빠르게 검증하는 필수 엔지니어링 절차임.
   - .yaml vs .pt 모델 로드 차이:
     * YOLO("yolo26n.yaml"): 가중치 없이 신경망 뼈대(구조)만 무작위 초기화 상태로 생성함.
     * YOLO("yolo26n.pt"): 대규모 데이터셋(COCO 등)으로 사전학습된 가중치까지 함께 불러옴.
   - Windows 멀티프로세싱 보호 (if __name__ == "__main__":):
     Windows는 하위 프로세스(DataLoader worker) 생성 시 스크립트를 처음부터 다시 import하므로,
     진입점 보호 구문이 없으면 무한 재귀 에러가 발생함. 또한 소규모 점검에서는 workers=0으로 두어 메인 프로세스에서 즉시 읽게 함.
3. 주요 산출물: p04_dataset.yaml, p04_runs/smoke/ (weights/best.pt, weights/last.pt, results.csv 등)
==============================================================================
"""
"""실습 04. 무작위 초기화 YOLO26의 1 epoch 학습 연결 점검. 성능 실험이 아닙니다."""
from pathlib import Path
import yaml
import torch
from ultralytics import YOLO

BASE = Path(__file__).resolve().parent

# Windows에서도 읽기 worker가 스크립트를 재실행하지 않도록 진입점을 구분합니다.
if __name__ == "__main__":
    torch.set_num_threads(1)

    # [핵심 개념 1: YOLO 데이터 계약(Data Contract)을 정의하는 YAML 동적 생성]
    # Ultralytics 학습기는 이미지 폴더 경로가 적힌 YAML 파일을 읽고, 경로 내의 'images' 단어를
    # 자동으로 'labels'로 치환(data/images/train -> data/labels/train)하여 정답 TXT 파일들을 찾아냅니다.
    # 또한 모델 선택 및 학습 점검 과정에서는 데이터 누수 방지를 위해 test 경로를 절대 넘기지 않습니다.
    config = {"train": str(BASE/"data/images/train"), "val": str(BASE/"data/images/val"),
              "names": ["square", "circle", "triangle"]}
    config_path = BASE / "p04_dataset.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    # [핵심 개념 2: 모델 아키텍처 초기화 (yolo26n.yaml)]
    # .pt가 아닌 .yaml을 전달하면 사전학습 가중치 없이 모델 구조(Backbone-Neck-Head)만 무작위 가중치로 생성합니다.
    model = YOLO("yolo26n.yaml")  # 구조만 생성합니다. COCO 사전학습 .pt와 다릅니다.

    # >>> B05
    # 요구: config_path로 1 epoch, imgsz=160, batch=4, CPU 학습을 호출하세요.
    # 나머지 옵션은 제공한 그대로 유지하세요. test 경로는 전달하지 않습니다.
    # [핵심 개념 3: model.train() 주요 하이퍼파라미터와 실행 경로 제어]
    # - data: 데이터셋 경로와 클래스 매핑이 담긴 YAML 파일 경로
    # - epochs=1: 파이프라인 연결 확인 목적의 1회 반복 학습
    # - imgsz=160: 입력 이미지를 160x160 해상도로 리사이즈하여 CPU 연산 부담 최소화
    # - batch=4: 한 번의 가중치 업데이트(Iteration)에 사용할 이미지 묶음 크기
    # - device="cpu": GPU 유무에 상관없이 동일한 환경에서 빠르게 검증하기 위해 CPU 지정
    # - workers=0: 별도 서브프로세스를 띄우지 않고 메인 스레드에서 데이터를 직접 로드 (Windows 에러 및 오버헤드 방지)
    # - nms=True: 검증 단계에서 중복 박스를 제거하는 NMS 후처리 경로 활성화
    # - project / name: 학습 산출물(weights, results.csv 등)이 'p04_runs/smoke' 하위에 저장되도록 고정
    # TODO B05: 위 요구사항의 핵심 코드를 작성하세요.
    model.train(
        data=str(config_path),
        epochs=1,
        imgsz=160,
        batch=4,
        device="cpu",
        workers=0,
        nms=True,
        project=str(BASE / "p04_runs"),
        name="smoke",
        exist_ok=True,
    )
    # <<< B05

    # 학습 완료 후 모델의 작업 유형(detect), 학습 데이터셋 기준으로 덮어씌워진 클래스 이름(names), 실행 장치(device) 확인
    print("task:", model.task, "names:", model.names, "device:", model.device)
    print("학습 결과:", BASE/"p04_runs/smoke")
