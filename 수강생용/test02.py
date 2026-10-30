student = {
    "name" : "민지",
    "scores" : [82, 95, 76, 88],
    "skills" : ["python", "Git", "Python"]
}
student["average"] = sum(student["scores"]) / len(student["scores"])
print(student["name"], f"평균 {student['average']:.1f}")
print("기술:", student["skills"])