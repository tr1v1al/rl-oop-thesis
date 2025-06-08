from rlistic.common import fuzzy_to_rl, rl_fuzzy_summary, rl_table
from rlistic.rlprogram import rlify_program

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

def input_rl_to_str(input_rl:dict) -> dict:
    """ Function that processes input RL-set into an RL-str """
    input_rl = {
        level : ','.join(students) 
        for level, students in input_rl.items()
    }
    return input_rl

def output_rl_to_set(output_rl:dict) -> dict:
    """ Function that processes output RL-str into an RL-set"""
    output_rl = {
        level : set(int(x) for x in groups.split(',')) if groups != 'None' else set()
        for level, groups in output_rl.items()
    }
    return output_rl

# Program that calculates the possible groups sizes for 'good students'
if __name__ == '__main__':
    # Students and their grades
    student_grades = {
        "Alberto" : 9.5, "Fernando" : 9.2, "Nacho" : 9.7,
        "Marta" : 9, "Jesus" : 8.5, "Pepe" : 8.5,
        "Jose" : 8, "Maria" : 8, "Manuel" : 7.5,
        "Antonio" : 7.5, "Alfonso" : 5, "Pedro" : 5
    }

    # Obtain the 'good student' fuzzy set
    fuzzy_set = good_student_fuzzy_set(student_grades)

    # Turn it into an RL
    input_rl = fuzzy_to_rl(fuzzy_set)

    # Print out the input RL
    print("\nInput RL: ", rl_table("set", input_rl))

    # Transform the input RL-set into an RL-string to feed it to the program
    input_rl = input_rl_to_str(input_rl)
    
    # Run the RL-program to calculate the possible groups
    output_rl = rlify_program(["python","examples/possible_groups.py"], input_rl)

    # Transform the output RL-string into an RL-set
    output_rl = output_rl_to_set(output_rl)
    
    # Print the output RL
    print("\nOutput RL: ", rl_table("set", output_rl))

    # Print the fuzzy summary
    print("\nFuzzy summary:", rl_fuzzy_summary(output_rl))

# $ python -m examples.good_students_rlprogram

# Input RL:  RL-set
# Level  | Object
# -------+---------------------------------------------------------------------------------------------------
# 1.0    | {'Alberto', 'Nacho', 'Fernando', 'Marta'}
# 0.75   | {'Alberto', 'Fernando', 'Marta', 'Jesus', 'Pepe', 'Nacho'}
# 0.5    | {'Alberto', 'Maria', 'Fernando', 'Marta', 'Jesus', 'Pepe', 'Nacho', 'Jose'}
# 0.25   | {'Alberto', 'Manuel', 'Maria', 'Antonio', 'Fernando', 'Marta', 'Jesus', 'Pepe', 'Nacho', 'Jose'}  

# Output RL:  RL-set
# Level  | Object   
# -------+---------
# 1.0    | {2}
# 0.75   | {2, 3}
# 0.5    | {2, 4}
# 0.25   | {2, 5}

# Fuzzy summary: {2: 1.0, 3: 0.25, 4: 0.25, 5: 0.25}