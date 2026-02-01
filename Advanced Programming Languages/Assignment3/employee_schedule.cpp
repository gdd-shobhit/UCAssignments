#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cctype>

namespace
{

const std::vector<std::string> DAYS = {
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
};
const std::vector<std::string> SHIFTS = { "morning", "afternoon", "evening" };
const int MIN_EMPLOYEES_PER_SHIFT = 2;
const int MAX_DAYS_PER_EMPLOYEE = 5;
const int PREFERRED_SHIFT_CAP = 3;

// Define a alias for a 2D vector of strings. Its just easier than defining a class/struct.
using Schedule = std::vector<std::map<std::string, std::vector<std::string>>>;

// Compiled release builds exit after returning 0 from main(). This helps with showing what was there before exiting.
void CheckExitCommand(const std::string& input)
{
    std::string lower;
    for (unsigned char c : input) lower += static_cast<char>(std::tolower(c));
    if (lower == "exit")
    {
        std::cout << "Exiting.\n";
        std::exit(0);
    }
}

void WaitForEnterBeforeExit()
{
    std::cout << "\nPress Enter to exit...";
    std::cin.clear();
    std::cin.ignore(10000, '\n');
    std::cin.get();
}

void GetShiftPriorityInput(std::vector<std::string>& order)
{
    std::cout << "  Enter priority order (1=most preferred, 2=second, 3=least preferred):\n";
    order.resize(3);
    std::vector<bool> used(4, false);
    for (size_t index = 0; index < 3; ++index)
    {
        while (true)
        {
            std::cout << "    " << SHIFTS[index] << ": rank (1-3): ";
            std::string rank_str;
            if (!(std::cin >> rank_str))
            {
                std::cin.clear();
                std::cin.ignore(10000, '\n');
                continue;
            }
            CheckExitCommand(rank_str);
            int rank = 0;
            try { rank = std::stoi(rank_str); } catch (...) { rank = 0; }
            if (rank >= 1 && rank <= 3 && !used[rank])
            {
                used[rank] = true;
                order[rank - 1] = SHIFTS[index];
                break;
            }
            std::cout << "Invalid or duplicate rank. Use 1, 2, 3 each once.\n";
        }
    }
}

void CollectEmployeeData(
    std::map<std::string, std::vector<std::string>>& preferences,
    std::map<std::string, std::vector<std::string>>* priorityOrders,
    bool usePriority)
{
    std::cout << "Number of employees: ";
    std::string num_str;
    std::cin >> num_str;
    CheckExitCommand(num_str);
    int number_of_employees = 0;
    try { number_of_employees = std::stoi(num_str); } catch (...) {}
    if (number_of_employees <= 0) return;
    for (int index = 0; index < number_of_employees; ++index)
    {
        std::string name;
        std::cout << "Employee name: ";
        std::cin >> name;
        CheckExitCommand(name);
        if (name.empty()) continue;

        if (usePriority && priorityOrders)
        {
            std::vector<std::string> order;
            GetShiftPriorityInput(order);
            (*priorityOrders)[name] = std::move(order);
        }

        std::vector<std::string> day_preferences;
        for (const auto& day : DAYS)
        {
            while (true)
            {
                std::cout << "  " << day << " preferred shift (morning/afternoon/evening): ";
                std::string preference;
                std::cin >> preference;
                CheckExitCommand(preference);
                for (auto& character : preference) character = static_cast<char>(std::tolower(static_cast<unsigned char>(character)));
                if (preference == "morning" || preference == "afternoon" || preference == "evening")
                {
                    day_preferences.push_back(preference);
                    break;
                }
                std::cout << "Invalid. Enter morning, afternoon, or evening.\n";
            }
        }
        preferences[name] = std::move(day_preferences);
    }
}

bool CanAssign(const std::string& employee, int day,
               const Schedule& schedule,
               const std::vector<std::set<std::string>>& assignedToday,
               const std::map<std::string, int>& daysWorked)
{
    if (assignedToday[day].count(employee)) return false;
    auto iterator = daysWorked.find(employee);
    if (iterator != daysWorked.end() && iterator->second >= MAX_DAYS_PER_EMPLOYEE) return false;
    return true;
}

Schedule BuildSchedule(
    const std::map<std::string, std::vector<std::string>>& preferences,
    const std::map<std::string, std::vector<std::string>>* priorityOrders)
{
    Schedule schedule(7);
    for (int day_index = 0; day_index < 7; ++day_index)
    {
        for (const auto& shift_name : SHIFTS)
        {
            schedule[day_index][shift_name] = {};
        }
    }

    std::map<std::string, int> daysWorked;
    std::vector<std::set<std::string>> assignedToday(7);

    std::vector<std::string> employees;
    for (const auto& pair : preferences) employees.push_back(pair.first);
    std::random_device random_seed_device;
    std::mt19937 random_generator(random_seed_device());
    std::shuffle(employees.begin(), employees.end(), random_generator);

    // First pass: assign by preference in rounds; at most one day per employee per round.
    // Use 3 rounds so backfill has enough capacity to ensure at least 2 per shift on all days.
    std::set<std::string> assignedThisRound;
    for (int round_index = 0; round_index < 3; ++round_index)
    {
        assignedThisRound.clear();
        for (size_t index = 0; index < employees.size(); ++index)
        {
            const std::string& employee = employees[index];
            if (assignedThisRound.count(employee)) continue;
            if (daysWorked[employee] >= MAX_DAYS_PER_EMPLOYEE) continue;
            for (int day_offset = 0; day_offset < 7; ++day_offset)
            {
                int day = static_cast<int>((index + day_offset) % 7);
                if (assignedToday[day].count(employee)) continue;
                const std::string& preferred = preferences.at(employee)[day];
                if (!CanAssign(employee, day, schedule, assignedToday, daysWorked)) continue;
                auto& slot = schedule[day][preferred];
                if (static_cast<int>(slot.size()) < PREFERRED_SHIFT_CAP)
                {
                    slot.push_back(employee);
                    assignedToday[day].insert(employee);
                    assignedThisRound.insert(employee);
                    daysWorked[employee]++;
                    break;
                }
                else
                {
                    std::vector<std::string> order;
                    if (priorityOrders)
                    {
                        auto iterator = priorityOrders->find(employee);
                        if (iterator != priorityOrders->end()) order = iterator->second;
                    }
                    if (order.empty())
                        for (const auto& shift_name : SHIFTS)
                            if (shift_name != preferred) order.push_back(shift_name);
                    bool assigned = false;
                    for (const auto& shift : order)
                    {
                        if (shift == preferred) continue;
                        if (!CanAssign(employee, day, schedule, assignedToday, daysWorked)) continue;
                        schedule[day][shift].push_back(employee);
                        assignedToday[day].insert(employee);
                        assignedThisRound.insert(employee);
                        daysWorked[employee]++;
                        assigned = true;
                        break;
                    }
                    if (assigned) break;
                }
            }
        }
    }

    // Second pass: ensure at least MIN_EMPLOYEES_PER_SHIFT per shift per day
    for (int day = 0; day < 7; ++day)
    {
        for (const auto& shift : SHIFTS)
        {
            int need = MIN_EMPLOYEES_PER_SHIFT - static_cast<int>(schedule[day][shift].size());
            if (need <= 0) continue;
            std::vector<std::string> candidates;
            for (const auto& employee : employees)
            {
                if (assignedToday[day].count(employee)) continue;
                if (daysWorked[employee] >= MAX_DAYS_PER_EMPLOYEE) continue;
                candidates.push_back(employee);
            }
            std::shuffle(candidates.begin(), candidates.end(), random_generator);
            for (const auto& employee : candidates)
            {
                if (need <= 0) break;
                schedule[day][shift].push_back(employee);
                assignedToday[day].insert(employee);
                daysWorked[employee]++;
                need--;
            }
        }
    }

    return schedule;
}

void PrintSchedule(const Schedule& schedule)
{
    std::cout << "\n===\n";
    std::cout << "WEEKLY EMPLOYEE SCHEDULE\n";
    std::cout << "===\n";
    for (int day = 0; day < 7; ++day)
    {
        std::cout << "\n" << DAYS[day] << ":\n";
        std::cout << "-----------------------\n";
        for (const auto& shift : SHIFTS)
        {
            const auto& names = schedule[day].at(shift);
            std::string capitalized = shift;
            if (!capitalized.empty()) capitalized[0] = static_cast<char>(std::toupper(static_cast<unsigned char>(capitalized[0])));
            std::cout << "  " << capitalized;
            for (size_t index = capitalized.size(); index < 12; ++index) std::cout << ' ';
            std::cout << " : ";
            if (names.empty())
            {
                std::cout << "(none)";
            }
            else
            {
                for (size_t index = 0; index < names.size(); ++index)
                {
                    if (index > 0) std::cout << ", ";
                    std::cout << names[index];
                }
            }
            std::cout << "\n";
        }
    }
    std::cout << "\n====\n";
}

/// <summary>
/// Run with sample data. This data was generated by ChatGPT by a prommpt of
/// "Generate 10 employees with their preferred shifts for a week with afternoon, morning, and evening shifts."
/// It was also provided with what kind of variable it would be stored like std::map<std::string, std::vector<std::string>>
/// </summary>
void RunDemoWithSampleData()
{
    std::map<std::string, std::vector<std::string>> preferences = {
        {"Alice", {"morning","morning","morning","morning","morning","morning","morning"}},
        {"Bob", {"afternoon","afternoon","afternoon","afternoon","afternoon","afternoon","afternoon"}},
        {"Carol", {"evening","evening","evening","evening","evening","evening","evening"}},
        {"Dave", {"morning","afternoon","evening","morning","afternoon","evening","morning"}},
        {"Eve", {"afternoon","evening","morning","afternoon","evening","morning","afternoon"}},
        {"Frank", {"morning","morning","afternoon","afternoon","evening","evening","morning"}},
        {"Grace", {"evening","morning","afternoon","evening","morning","afternoon","afternoon"}},
        {"Henry", {"afternoon","evening","morning","afternoon","evening","morning","evening"}},
        {"Ivy", {"morning","afternoon","evening","morning","afternoon","evening","morning"}},
        {"Jack", {"evening","morning","afternoon","evening","morning","afternoon","evening"}},
    };
    std::map<std::string, std::vector<std::string>> priorityOrders = {
        {"Alice", {"morning","afternoon","evening"}},
        {"Bob", {"afternoon","morning","evening"}},
        {"Carol", {"evening","afternoon","morning"}},
        {"Dave", {"morning","afternoon","evening"}},
        {"Eve", {"afternoon","evening","morning"}},
        {"Frank", {"morning","afternoon","evening"}},
        {"Grace", {"evening","morning","afternoon"}},
        {"Henry", {"afternoon","evening","morning"}},
        {"Ivy", {"morning","afternoon","evening"}},
        {"Jack", {"evening","morning","afternoon"}},
    };
    Schedule schedule = BuildSchedule(preferences, &priorityOrders);
    PrintSchedule(schedule);
}

}  // namespace

int main()
{
    std::cout << "Employee Schedule Manager\n";
    std::cout << "Options: 1 = Enter data manually  2 = Run demo with sample data  (type 'exit' anytime to quit)\n";
    std::cout << "Choice (1/2): ";
    std::string choice_str;
    std::cin >> choice_str;
    CheckExitCommand(choice_str);
    int choice = 0;
    try { choice = std::stoi(choice_str); } catch (...) {}
    if (choice == 2)
    {
        RunDemoWithSampleData();
        WaitForEnterBeforeExit();
        return 0;
    }
    std::cout << "Use priority ranking for shifts? (y/n): ";
    std::string use_priority_str;
    std::cin >> use_priority_str;
    CheckExitCommand(use_priority_str);
    bool use_priority = (!use_priority_str.empty() && (use_priority_str[0] == 'y' || use_priority_str[0] == 'Y'));

    std::map<std::string, std::vector<std::string>> preferences;
    std::map<std::string, std::vector<std::string>> priority_orders;
    CollectEmployeeData(preferences, use_priority ? &priority_orders : nullptr, use_priority);
    if (preferences.empty())
    {
        std::cout << "No employees entered. Exiting.\n";
        WaitForEnterBeforeExit();
        return 0;
    }
    Schedule schedule = BuildSchedule(preferences, use_priority ? &priority_orders : nullptr);
    PrintSchedule(schedule);
    WaitForEnterBeforeExit();
    return 0;
}
