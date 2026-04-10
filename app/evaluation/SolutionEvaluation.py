## -- Imports -- ##

## -- Functions -- ##


def sec_to_hmsms(seconds):

    # input : (int) seconds
    # output : (str) hour-minute-second-milisecond

    s, ms = divmod(seconds, 1)
    s = int(s)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    ms = ms * 10
    return f"{h}h {m}m {s}s {ms:.1f}ms"


def mean_travel_time(solution_stats_arr):

    edgeweight_array = [solution_stats_arr[i][1] for i in solution_stats_arr]

    total_tt = 0
    num_paths = len(edgeweight_array)
    
    for weight in edgeweight_array:

        #if weight == float('inf'):
        #    num_paths -= 1
        #else:
        total_tt += weight

    mean_tt = total_tt / num_paths
    return mean_tt


def number_of_busses_taken(modeInfo_array):

    bus_number = 0
    prev_edge = None

    for edge in modeInfo_array:

        if edge[2][0] == 'walk':
            pass
        elif edge[2][0] == 'bus':
            if prev_edge[2][0] == 'walk':
                bus_number += 1
            elif prev_edge[2][0] == 'bus' and prev_edge[2][1] != edge[2][1]:
                bus_number += 1
            else:
                pass
        else:
            break

        prev_edge = edge

    return bus_number


def mean_busses_taken(solution_stats_arr):

    solutionPath_array = [solution_stats_arr[i][0] for i in solution_stats_arr]
    num_paths = len(solutionPath_array)

    total_bus_num = 0
    for route_list in solutionPath_array:
        total_bus_num += number_of_busses_taken(route_list)

    avg_bus_num = total_bus_num / num_paths
    return avg_bus_num


def best_and_worst_travel_time(solution_stats_arr):

    edgeweight_array = [solution_stats_arr[i][1] for i in solution_stats_arr]
    edgeweight_array.sort()
    
    num_of_paths = len(solution_stats_arr)
    ten_percent_size = num_of_paths // 10
    if ten_percent_size == 0:
        ten_percent_size = 1
    ninety_percent_size = num_of_paths - ten_percent_size

    lower_sum = 0
    for weight in edgeweight_array[:ten_percent_size]:
        lower_sum += weight
    lower_avg = lower_sum / ten_percent_size

    upper_sum = 0
    for weight in edgeweight_array[ninety_percent_size:]:
        upper_sum += weight
    upper_avg = upper_sum / ten_percent_size

    best_case = edgeweight_array[0]
    worst_case = edgeweight_array[-1]

    return best_case, lower_avg, worst_case, upper_avg


def print_all_statistics(solution_stats_arr, graph_type = ""):

    avg_travel_time = mean_travel_time(solution_stats_arr)

    avg_busses_taken = mean_busses_taken(solution_stats_arr)

    best_time, best_avg, worst_time, worst_avg = best_and_worst_travel_time(solution_stats_arr)

    graph_type_str = "FOR GRAPH " + graph_type
    print(f"\n\nSTATISTICS of the PATHS COMPUTED for {len(solution_stats_arr)} JOURNEYS {graph_type_str}:\n")

    print(f"-> Average travel time among all journeys = {sec_to_hmsms(avg_travel_time)} [{avg_travel_time:.3f} seconds]")
    print(f"-> Average number of busses for a journey = {avg_busses_taken:.1f} busses per journey\n")

    print(f"-> Best Case Analysis -")
    print(f"---> Shortest journey time = {sec_to_hmsms(best_time)} [{best_time:.3f} seconds]")
    print(f"---> Average journey time for shortest 10% of journeys = {sec_to_hmsms(best_avg)} [{best_avg:.3f} seconds]\n")

    print(f"-> Worst Case Analysis -")
    print(f"---> Longest journey time = {sec_to_hmsms(worst_time)} [{worst_time:.3f} seconds]")
    print(f"---> Average journey time for longest 10% of journeys = {sec_to_hmsms(worst_avg)} [{worst_avg:.3f} seconds]\n")

    return