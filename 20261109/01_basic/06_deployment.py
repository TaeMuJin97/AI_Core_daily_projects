"""
==============================================================================
[실습 보고서: 06_deployment.py - 엣지(Edge) 추론 및 배포 파이프라인 아키텍처 설계]
1. 실험 목적: 학습된 딥러닝 모델을 실제 서비스/엣지 환경에 배포하기 위한 표준 변환 흐름
              (PyTorch -> ONNX -> TensorRT -> Jetson/DeepStream)을 정의하고 설계 명세서(JSON)로 저장함.
2. 핵심 포인트:
   - 단계별 역할 분리: 프레임워크 간 호환성을 위한 그래프 변환(ONNX)과 특정 NVIDIA GPU에 맞춘 
     하드웨어 추론 최적화(TensorRT Engine 빌드)의 순서를 명확히 구조화함.
   - 설계와 실측의 분리(DESIGN_ONLY): 실제 하드웨어(Jetson 등)나 엔진 빌드 없이 아키텍처를 먼저 정의할 때는
     latency_ms나 checked_on_hardware를 None/False로 비워두어 가짜 성능 수치가 기록되는 것을 방지함.
3. 주요 산출물: p06_deployment_plan.json (배포 파이프라인 설계 명세 - 포트폴리오용 Git 업로드 대상)
==============================================================================
"""
"""실습 06: 배포 흐름의 설계 기록입니다. ONNX·TensorRT 엔진을 실행하지 않습니다."""
from pathlib import Path
import json

# 기본 경로 설정 (이전 실습과 동일)
base = Path(__file__).resolve().parent

# TODO B07
# [핵심 구현: 딥러닝 모델의 엣지 배포 표준 4단계 파이프라인 정의]
# 1) 'PyTorch'          : 모델 학습 및 가중치(Weights) 확보 단계
# 2) 'ONNX'             : 프레임워크에 종속되지 않는 표준 계산 그래프(교환 포맷)로 변환하는 단계
# 3) 'TensorRT'         : 연산 결합(Layer Fusion), 상수 접기(Constant Folding), 정밀도(FP16/INT8) 최적화를 통해
#                         타깃 NVIDIA GPU 전용 고속 추론 엔진(.engine)을 빌드하는 단계
# 4) 'Jetson/DeepStream': 엣지 디바이스(Jetson) 및 실시간 영상/문서 스트림 파이프라인(DeepStream)에 탑재하는 단계
stages = ['PyTorch', 'ONNX', 'TensorRT', 'Jetson/DeepStream']
# TODO 끝 B07

# [중요] 배포 설계 명세서(plan) 구성
# 실제 엔진을 빌드하고 하드웨어에서 측정한 것이 아니므로(status='DESIGN_ONLY'),
# 타깃 장비, 버전, 해시값, 지연시간(latency_ms)은 투명하게 None/False로 기록하여 설계 단계임을 명시함
plan = {
    'stages': stages,
    'status': 'DESIGN_ONLY',
    'target_device': None,
    'tensorrt_version': None,
    'engine_sha256': None,
    'latency_ms': None,
    'checked_on_hardware': False
}

# 설계 명세를 JSON 파일로 저장하고 파이프라인 흐름을 화살표(->)로 시각화해 출력
(base / 'p06_deployment_plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
print(' -> '.join(stages))
print('DESIGN_ONLY: 오늘은 설계 기록. Tesseract 자체를 ONNX로 변환하는 예제가 아닙니다.')