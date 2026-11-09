"""
==============================================================================
[실습 보고서: 04_messages.py - 멀티모달 VLM 입력을 위한 메시지 구조(Messages) 설계]
1. 실험 목적: 문서 이미지 경로와 질문을 Hugging Face Transformers 멀티모달 규격에 맞는
              messages 대화 형식(image/text content list)으로 구성하고, 모의 응답 데이터와 묶어
              JSON 파일(p04_mock_answers.json)로 저장함.
2. 핵심 개념 및 엔지니어링 포인트:
   - 멀티모달 입력 포맷(Messages API): 텍스트 질의문뿐만 아니라 이미지 파일 경로를 함께 전달하기 위해
     content 내부를 단일 문자열이 아닌 [{"type": "image", ...}, {"type": "text", ...}] 형태의 리스트로 정의함.
   - 파이프라인 연동성: 이후 실제 VLM 모델(Processor/Pipeline)을 연동할 때 이 메시지 구조를 
     그대로 apply_chat_template에 전달하여 토큰화와 전처리를 수행할 수 있도록 표준화함.
3. 주요 산출물: p04_mock_answers.json (멀티모달 질의응답 모의 기록 및 메시지 명세)
==============================================================================
"""
"""실습 04: 이미지+질문을 구성하고 모의 응답을 읽습니다. 실제 VLM을 호출하지 않습니다."""
from pathlib import Path
import json

base = Path(__file__).resolve().parent
lesson = json.loads((base / 'lesson.json').read_text(encoding='utf-8'))
doc = lesson['documents']['doc01']
rows = []

for answer in doc['mock_vlm']['responses']:
    question = lesson['questions'][answer['field']]
    
# TODO B05
    # [핵심 구현: VLM 입력을 위한 멀티모달 대화 형식(messages) 딕셔너리 구조 생성]
    # - role: 대화 주체 ('user')
    # - content: 이미지 타입 항목(path)과 텍스트 타입 항목(question)을 동시에 포함하는 리스트
    messages = [
        {
            "role": "user",
            "content": [
                # {"type": "image", "path": str(base / doc['image_path'])},
                # lesson.json 안의 각 문서(doc01, doc02 등) 구조를 보면 이미지 파일명 키는 'image_path'가 아니라 'file'로 정의되어 있음.
                {"type": "image", "path": str(base / doc['file'])},
                {"type": "text", "text": question}
            ]
        }
    ]
# TODO 끝 B05

    rows.append({
        'backend': 'mock', 
        'messages': messages, 
        'response': answer, 
        'model_id': None, 
        'inference_ms': None
    })
    print(question, '->', answer['answer'])

(base / 'p04_mock_answers.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
print('MOCK: 교사가 작성한 응답 예시입니다. 실제 모델 출력이 아닙니다.')