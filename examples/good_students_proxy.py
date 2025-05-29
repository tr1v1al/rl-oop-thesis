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
        "Alberto" : 9.5, "Fernando" : 9.2,
        "Marta" : 8, "Jesus" : 7.5,
        "Jose" : 9, "Maria" : 9.5,
        "Antonio" : 5
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