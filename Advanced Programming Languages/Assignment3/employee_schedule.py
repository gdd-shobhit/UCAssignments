import random
import sys
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def CheckExitCommand(input_str: str) -> None:
    """If user typed 'exit' (case-insensitive), print message and exit the program."""
    if input_str.strip().lower() == "exit":
        print("Exiting.")
        sys.exit(0)
SHIFTS = ["morning", "afternoon", "evening"]
MIN_EMPLOYEES_PER_SHIFT = 2
MAX_DAYS_PER_EMPLOYEE = 5
MAX_ASSIGNMENT_PASSES = 3


def GetShiftPriorityInput() -> List[str]:
    """Get employee's shift preference order (1=first choice, 2=second, 3=third)."""
    print("  Enter priority order (1=most preferred, 2=second, 3=least preferred):")
    order = [None, None, None]
    for index in range(3):
        while True:
            rank_str = input(f"    {SHIFTS[index]}: rank (1-3): ")
            CheckExitCommand(rank_str)
            rank = int(rank_str)
            if 1 <= rank <= 3 and order[rank - 1] is None:
                order[rank - 1] = SHIFTS[index]
                break
            print("    Invalid or duplicate rank. Use 1, 2, 3 each once.")
    return order


def CollectEmployeeData(use_priority: bool = True) -> Tuple[Dict[str, List[str]], Optional[Dict[str, List[str]]]]:
    """
    Collect employee names and shift preferences for each day.
    Returns: (preferences[employee][day] = shift, optional priority_order[employee] = [shift1, shift2, shift3])
    """
    preferences: Dict[str, List[str]] = {}
    priority_orders: Optional[Dict[str, List[str]]] = {} if use_priority else None

    num_str = input("Number of employees: ")
    CheckExitCommand(num_str)
    number_of_employees = int(num_str)
    if number_of_employees <= 0:
        return preferences, priority_orders
    for _ in range(number_of_employees):
        name = input("Employee name: ").strip()
        CheckExitCommand(name)
        if not name:
            continue
        day_preferences = []
        if use_priority:
            priority = GetShiftPriorityInput()
            if priority_orders is not None:
                priority_orders[name] = priority
        for day in DAYS:
            while True:
                preference = input(f"  {day} preferred shift (morning/afternoon/evening): ").strip().lower()
                CheckExitCommand(preference)
                if preference in SHIFTS:
                    day_preferences.append(preference)
                    break
                print("    Invalid. Enter morning, afternoon, or evening.")
        preferences[name] = day_preferences

    return preferences, priority_orders


def BuildSchedule(
    preferences: Dict[str, List[str]],
    priority_orders: Optional[Dict[str, List[str]]],
) -> Dict[Tuple[int, str], List[str]]:
    """
    This scheduler favors employee preferences early, then relaxes constraints
    to guarantee minimum staffing coverage. Fairness is approximate, not optimal.
    """
    # schedule[(day, shift)] = list of employee names
    schedule: Dict[Tuple[int, str], List[str]] = defaultdict(list)
    days_worked: Dict[str, int] = defaultdict(int)
    assigned_today: Dict[int, set] = {day_index: set() for day_index in range(7)}

    employees = list(preferences.keys())
    random.shuffle(employees)  # fairness in tie-breaking

    def CanAssign(employee: str, day: int, shift: str) -> bool:
        if employee in assigned_today[day]:
            return False
        if days_worked[employee] >= MAX_DAYS_PER_EMPLOYEE:
            return False
        return True

    # First pass: assign by preference in rounds; at most one day per employee per round.
    # Use MAX_ASSIGNMENT_PASSES rounds so backfill has enough capacity to ensure at least 2 per shift on all days.
    for round_index in range(MAX_ASSIGNMENT_PASSES):
        assigned_this_round: set = set()
        for index, employee in enumerate(employees):
            if employee in assigned_this_round or days_worked[employee] >= MAX_DAYS_PER_EMPLOYEE:
                continue
            for day_offset in range(7):
                day = (index + day_offset) % 7
                if employee in assigned_today[day]:
                    continue
                preferred = preferences[employee][day]
                if not CanAssign(employee, day, preferred):
                    continue
                if len(schedule[(day, preferred)]) < 3:
                    schedule[(day, preferred)].append(employee)
                    assigned_today[day].add(employee)
                    assigned_this_round.add(employee)
                    days_worked[employee] += 1
                    break
                else:
                    # Conflict: assign to another shift same day (use priority order if available)
                    if priority_orders:
                        order = priority_orders.get(employee, [])
                    else:
                        order = []
                    if not order:
                        order = [preferred] + [s for s in SHIFTS if s != preferred]
                    for shift_option in order:
                        if shift_option != preferred and CanAssign(employee, day, shift_option):
                            schedule[(day, shift_option)].append(employee)
                            assigned_today[day].add(employee)
                            assigned_this_round.add(employee)
                            days_worked[employee] += 1
                            break
                    else:
                        continue
                    break

    # Second pass: ensure at least MIN_EMPLOYEES_PER_SHIFT per shift per day
    for day in range(7):
        for shift in SHIFTS:
            need = MIN_EMPLOYEES_PER_SHIFT - len(schedule[(day, shift)])
            if need <= 0:
                continue
            candidates = [
                employee for employee in employees
                if employee not in assigned_today[day] and days_worked[employee] < MAX_DAYS_PER_EMPLOYEE
            ]
            random.shuffle(candidates)
            for employee in candidates:
                if need <= 0:
                    break
                schedule[(day, shift)].append(employee)
                assigned_today[day].add(employee)
                days_worked[employee] += 1
                need -= 1

    return schedule


def PrintSchedule(schedule: Dict[Tuple[int, str], List[str]]) -> None:
    """Output the final weekly schedule in a readable format."""
    print("\n" + "=" * 70)
    print("WEEKLY EMPLOYEE SCHEDULE")
    print("=" * 70)
    for day in range(7):
        print(f"\n{DAYS[day]}:")
        print("-" * 40)
        for shift in SHIFTS:
            names = schedule[(day, shift)]
            print(f"  {shift.capitalize():12} : {', '.join(names) if names else '(none)'}")
    print("\n" + "=" * 70)


def RunDemoWithSampleData() -> None:
    """Run with built-in sample data (no user input) for quick testing."""
    preferences = {
        "Alice": ["morning"] * 7,
        "Bob": ["afternoon"] * 7,
        "Carol": ["evening"] * 7,
        "Dave": ["morning", "afternoon", "evening", "morning", "afternoon", "evening", "morning"],
        "Eve": ["afternoon", "evening", "morning", "afternoon", "evening", "morning", "afternoon"],
        "Frank": ["morning", "morning", "afternoon", "afternoon", "evening", "evening", "morning"],
        "Grace": ["evening", "morning", "afternoon", "evening", "morning", "afternoon", "afternoon"],
        "Henry": ["afternoon", "evening", "morning", "afternoon", "evening", "morning", "evening"],
        "Ivy": ["morning", "afternoon", "evening", "morning", "afternoon", "evening", "morning"],
        "Jack": ["evening", "morning", "afternoon", "evening", "morning", "afternoon", "evening"],
    }
    priority_orders = {
        "Alice": ["morning", "afternoon", "evening"],
        "Bob": ["afternoon", "morning", "evening"],
        "Carol": ["evening", "afternoon", "morning"],
        "Dave": ["morning", "afternoon", "evening"],
        "Eve": ["afternoon", "evening", "morning"],
        "Frank": ["morning", "afternoon", "evening"],
        "Grace": ["evening", "morning", "afternoon"],
        "Henry": ["afternoon", "evening", "morning"],
        "Ivy": ["morning", "afternoon", "evening"],
        "Jack": ["evening", "morning", "afternoon"],
    }
    schedule = BuildSchedule(preferences, priority_orders)
    PrintSchedule(schedule)


def Main() -> None:
    print("Employee Schedule Manager")
    print("Options: 1 = Enter data manually  2 = Run demo with sample data  (type 'exit' anytime to quit)")
    choice = input("Choice (1/2): ").strip()
    CheckExitCommand(choice)
    if choice == "2":
        RunDemoWithSampleData()
        return
    use_priority_str = input("Use priority ranking for shifts? (y/n): ").strip()
    CheckExitCommand(use_priority_str)
    use_priority = use_priority_str.lower() == "y"
    preferences, priority_orders = CollectEmployeeData(use_priority)
    if not preferences:
        print("No employees entered. Exiting.")
        return
    schedule = BuildSchedule(preferences, priority_orders)
    PrintSchedule(schedule)


if __name__ == "__main__":
    Main()
