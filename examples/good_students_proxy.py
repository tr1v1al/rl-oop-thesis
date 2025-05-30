from rlistic.common import fuzzy_to_rl, rl_fuzzy_summary, rl_table
from rlistic.proxy import RL

class StudentsSet(set):
    def group_sizes(self) -> set[int]:
        """ Return proper divisors of cardinal of students """
        n = len(self)
        return {d for d in range(2, n) if n % d == 0}

def good_student_membership(grade:float) -> float:
    """ 
        Membership function of the 'good student' fuzzy subset of 
        the universe [0,10], which represents the grades of students.
    """
    return 0.0 if grade <= 7 else 1.0 if grade >= 9 else (grade - 7) / 2

def good_student_fuzzy_set(student_grades:dict) -> set:
    """
        Function that given students with their grades, returns the fuzzy set 
        of 'good student', where the universe is the set of student names.
    """
    return {name : good_student_membership(grade) for name, grade in student_grades.items()}

# Program that calculates the possible groups sizes for 'good students'
if __name__ == '__main__':
    # Students and their grades
    student_grades = {
        "Alberto" : 9.5, "Fernando" : 9.2, "Nacho" : 9.7,
        "Marta" : 9, "Jesus" : 8.5, "Pepe" : 8,
        "Jose" : 7.5, "Maria" : 7.5, "Manuel" : 5,
        "Antonio" : 5, "Alfonso" : 5, "Pedro" : 5
    }

    # Obtain the 'good student' fuzzy set
    fuzzy_set = good_student_fuzzy_set(student_grades)

    # Turn it into an RL-set dictionary
    rl_set_dict = fuzzy_to_rl(fuzzy_set)

    # Transform the RL-set dictionary into an RL-StudentSet dictionary
    rl_studentset_dict = {level : StudentsSet(students) for level, students in rl_set_dict.items()}
    
    # Instantiate RL-StudentSet with its dictionary
    rl_studentset = RL(rl_studentset_dict)
    print("\nRL with students:",rl_studentset, sep='\n')

    # Calculate the possible groups
    rl_groups = rl_studentset.group_sizes()
    print("\nRL with possible groups:",rl_groups, sep='\n')

    # Print the fuzzy summary
    print("\nFuzzy summary:", rl_fuzzy_summary(rl_groups.mapping))

# $ python -m examples.good_students_proxy

# RL with students:
# RL-StudentsSet
# Level  | Object
# -------+-------------------------------------------------------------------------------------------
# 1.0    | StudentsSet({'Alberto', 'Fernando', 'Nacho', 'Marta'})
# 0.75   | StudentsSet({'Nacho', 'Marta', 'Fernando', 'Alberto', 'Jesus'})
# 0.5    | StudentsSet({'Nacho', 'Marta', 'Fernando', 'Jesus', 'Alberto', 'Pepe'})
# 0.25   | StudentsSet({'Nacho', 'Marta', 'Fernando', 'Maria', 'Jesus', 'Alberto', 'Pepe', 'Jose'})

# RL with possible groups:
# RL-set
# Level  | Object
# -------+---------
# 1.0    | {2}
# 0.75   | set()
# 0.5    | {2, 3}
# 0.25   | {2, 4}

# Fuzzy summary: {2: 0.75, 3: 0.25, 4: 0.25}