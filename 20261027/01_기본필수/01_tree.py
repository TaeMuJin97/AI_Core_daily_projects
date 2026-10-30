"""실습 01: 입력을 질문으로 나누는 트리를 만듭니다. 성능 평가가 아닌 원리 예제입니다."""
from sklearn.tree import DecisionTreeClassifier

X = [[100], [200], [300], [700], [800], [900]]
y = [0, 0, 0, 1, 1, 1]  # 같은 순서의 정답: 성공 0, 실패 1
model = DecisionTreeClassifier(max_depth=1, random_state=42)
# TODO B01a: X와 y로 model을 학습하세요.

model.fit(X, y)
# TODO B01b: 250과 850을 예측하여 prediction에 넣으세요.

prediction = model.predict([[250], [850]]) 
# 각 데이터가 하나의 값만 가지고 있으므로 특성 개수가 1개(1 features)인 상태로 모델이 학습
# 250과 850을 각각 별개의 데이터(샘플)로 나누어 예측해야 하므로, 내부 리스트를 따로 감싸서 2개의 행 형태로 전달해 주어야 함
# [[250], [850]]은 2행 1열 입력
# ValueError 조심
# TODO 끝
print("분기 기준:", model.tree_.threshold[0])
print("250·850 예측:", prediction.tolist())