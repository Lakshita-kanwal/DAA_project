import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import AppConfig

"""
Student Grouping Algorithm
Creates balanced teams based on academic performance and interests
Uses a modified chmod-inspired approach for student classification
"""

def organise_students_into_groups(student_list, is_initial_run=True):
    """
    Main grouping function that:
    1. Classifies students using performance codes
    2. Creates balanced groups
    3. Ensures diversity in each team
    """
    
    coded_students = [
        {
            'id': student['id'],
            'name': student['name'],
            'email': student['email'],
            'performance': student['cgpa'],
            'accommodation': student['residence'],
            'specialisation': student['interest'],
            'code': calculate_student_code(student)
        }
        for student in student_list
    ]

    # Group by residence_type first
    from collections import defaultdict
    residence_groups = defaultdict(list)
    for s in coded_students:
        residence_groups[s['accommodation'].lower()].append(s)

    final_groups = {}
    group_number = 1

    for residence, students in residence_groups.items():
        # Split by performance (10-point scale)
        high = [s for s in students if s['performance'] >= 8.5]
        medium = [s for s in students if 7.5 <= s['performance'] <8.5]
        low = [s for s in students if s['performance'] < 7.5]

        used_ids = set()
        # Try to form groups with 1 high, 1 medium, 1 low, all with different study_focus
        while high or medium or low:
            group = []
            group_codes = []
            # Try to add one from each performance bucket
            for bucket in [high, medium, low]:
                for i, s in enumerate(bucket):
                    # Only add if study_focus is unique in this group
                    if s['id'] not in used_ids and all(s['specialisation'].lower() != g['specialisation'].lower() for g in group):
                        group.append(s)
                        group_codes.append(s['code'])
                        used_ids.add(s['id'])
                        del bucket[i]
                        break
            # If group has at least 2, check chmod777 compatibility (all bits different)
            if len(group) >= 2:
                # For chmod777, ensure all students in group have different specialisation bits and at least one different performance bit
                # (bits: 0o700 = performance, 0o007 = specialisation)
                perf_levels = set([(g['code'] & 0o700) for g in group])
                specs = set([(g['code'] & 0o007) for g in group])
                if len(perf_levels) == len(group) and len(specs) == len(group):
                    group_names = [s['id'] for s in group]
                    final_groups[f"Project Team {group_number}"] = group_names
                    group_number += 1
                    continue
            # If can't form a full diverse group, add remaining students as a group
            leftovers = [s for bucket in [high, medium, low] for s in bucket if s['id'] not in used_ids]
            if group or leftovers:
                group_names = [s['id'] for s in group + leftovers]
                for s in leftovers:
                    used_ids.add(s['id'])
                # Remove all from buckets
                high = [s for s in high if s['id'] not in used_ids]
                medium = [s for s in medium if s['id'] not in used_ids]
                low = [s for s in low if s['id'] not in used_ids]
                final_groups[f"Project Team {group_number}"] = group_names
                group_number += 1
                break

    return final_groups

def calculate_student_code(student):
    """
    Creates a classification code for each student using bit patterns:
    - Bits 7-5: Academic performance (High/Medium/Low)
    - Bits 4-3: Accommodation type (Hosteller/Dayscholar)
    - Bits 2-0: Specialisation area
    """
    
    student_code = 0o000  # Start with empty code
    
    # Set performance bits (10-point scale)
    if student['performance'] >= 8.5:   # High performer
        student_code |= 0o400
    elif student['performance'] >= 7.5: # Medium performer
        student_code |= 0o200
    else:                               # Needs support
        student_code |= 0o100
    
    # Set accommodation type
    if student['accommodation'].lower() == 'hosteller':
        student_code |= 0o040
    else:  # Dayscholar
        student_code |= 0o020
    
    # Set specialisation area
    specialisation_map = {
        'web dev': 0o001,
        'cloud': 0o002,
        'cybersecurity': 0o003,
        'ai': 0o004,
        'none': 0o000
    }
    student_code |= specialisation_map.get(
        student['specialisation'].lower(), 
        0o000
    )
    
    return student_code

def create_balanced_group(student_entries, grouped_students, is_initial_run):
    """Forms one balanced group considering all diversity factors"""
    
    new_group = []
    
    # Find first available student not yet in a group
    for student_id, student_code in student_entries:
        if student_id not in grouped_students:
            new_group.append(student_id)
            grouped_students.add(student_id)
            break
    
    # If we couldn't find anyone, return empty group
    if not new_group:
        return None
    
    # Try to find compatible students to balance the group
    for other_id, other_code in student_entries:
        if other_id in grouped_students:
            continue  # Skip already grouped students
        
        # Check if students are compatible (same level but different specialties)
        if are_students_compatible(student_code, other_code):
            new_group.append(other_id)
            grouped_students.add(other_id)
            
            # Stop when group reaches ideal size
            if len(new_group) >= AppConfig.MAX_GROUP_SIZE:
                break
    
    return new_group

def are_students_compatible(code1, code2):
    """
    Determines if two students should be in the same group
    based on their classification codes
    """
    same_performance_level = (code1 & 0o700) == (code2 & 0o700)
    different_specialities = (code1 & 0o007) != (code2 & 0o007)
    same_accommodation = (code1 & 0o060) == (code2 & 0o060)
    
    return same_performance_level and different_specialities and same_accommodation
