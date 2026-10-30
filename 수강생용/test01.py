name = input("이름 : ")
hours = float(input("오늘 학습시간: "))
target = 8
rate = hours / target * 100
print(f"{name}님의 학습 달성률: {rate:.1f}%")