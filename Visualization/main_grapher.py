import json
import matplotlib.pyplot as plt
import imageio
import os
import re
import numpy as np
import time
import gc

REPETITIONS = None
SKIP = None

def main():
    global REPETITIONS, SKIP  # Declare them as global
    with open("./config.json", "r") as f:
        config = json.load(f)

    REPETITIONS = config["repetitions"]
    SKIP = config["skip"]

    if config["withShooting"]:
        withFixedProbabilityConfig = config["withFixedProbability"]
        if withFixedProbabilityConfig["avg_speed_temporal_shooting"]:
            avg_speed_temporal_shooting(withFixedProbabilityConfig["initialNh"],withFixedProbabilityConfig["finalNh"],withFixedProbabilityConfig["stepNh"],withFixedProbabilityConfig["probability"])
            gc.collect()
        if withFixedProbabilityConfig["avg_speed_observable"]:
            generate_avg_speed_graph_observable_for_shooting_fixed_prob(withFixedProbabilityConfig["initialNh"],withFixedProbabilityConfig["finalNh"],withFixedProbabilityConfig["stepNh"],withFixedProbabilityConfig["probability"])
            gc.collect()


        if withFixedProbabilityConfig["frac_zombie_shooting_fixed_nh_temporal"]:
            generate_frac_zombie_graph_shooting_with_variable_nh_fixed_prob(withFixedProbabilityConfig["initialNh"],withFixedProbabilityConfig["finalNh"],withFixedProbabilityConfig["stepNh"],withFixedProbabilityConfig["probability"])
            gc.collect()

        if withFixedProbabilityConfig["frac_zombie_shooting_fixed_nh_observable"]:
            generate_mean_frac_zombie_graph_shooting_observable_last_frame_fixed_nh_variable_prob(withFixedProbabilityConfig["initialNh"],withFixedProbabilityConfig["finalNh"],withFixedProbabilityConfig["stepNh"],withFixedProbabilityConfig["probability"])
            gc.collect()


        withVariableProbabilityConfig = config["withVariableProbability"]
        if withVariableProbabilityConfig["frac_zombie"]:
            generate_frac_zombie_graph_shooting(withFixedProbabilityConfig["fixedNHforProb"], withFixedProbabilityConfig["initialProbability"], withFixedProbabilityConfig["finalProbability"], withFixedProbabilityConfig["probabilityStep"])
            gc.collect()

        if withVariableProbabilityConfig["frac_zombie_observable"]:
            generate_mean_frac_zombie_graph_shooting_observable_last_frame(withFixedProbabilityConfig["fixedNHforProb"],withFixedProbabilityConfig["initialProbability"],config["finalProbability"],withFixedProbabilityConfig["probabilityStep"])

        return

    if config["animations"]:
        # Load JSON data
        data = load_simulation_data(100, 0, shoot_probability='0.10')

        skip_frames = 20
        max_frames = 100000
        # Generate frames
        generate_frames(data, skip_frames, max_frames)
        # Create GIF
        generate_gif(data, 1, max_frames)
        # Clean up frames
        # for file in os.listdir('./frames'):
        #     os.remove(f'frames/{file}')
        # os.rmdir('frames')

    if config["frac_zombie"]: 
        #TODO estos graficos pero con Nh y Pe en el eje x (DE ACA SACAMOS 2 OBSERVABLES) 
        # 1 Observable con Nh Fijo y Pe variando
        # 2 Observalbe con Nh variable y Pe fijo
        generate_mean_frac_zombie_in_all_frames_plot()
        generate_frac_zombie_graph()
        generate_mean_frac_zombie_graph()

    if config["avg_v"]: #TODO esto creo que lo podemos dejar igual pero hay que agregar que Pe fijo estamos agarrando, variar Nh y dejar Pe fijo y hablar acerca de compararlo con el TP5 
        generate_human_and_zombie_avg_speed_for_single_simulation_graph(40, 0)
        generate_avg_speed_graph()
        generate_avg_speed_graph_observable()
        generate_human_and_zombie_avg_speed_observable()


def __get_dt(simulation):
    return simulation['params']['dt']


def generate_avg_speed_graph():
    # Load JSON data (for nh in 10, 20, ..., 100)
    simulations_per_nh = {}
    output_directory='avg_v_vs_time'
    for nh in range(30, 51, SKIP):
        simulations_per_nh[nh] = load_simulation_data(nh, 0) 

    avg_speed_per_nh = {}
    dt_per_nh = {}
    for nh, simulations in simulations_per_nh.items():
        results = simulations['results']
        dt = __get_dt(simulations)
        dt_per_nh[nh] = dt
        avg_speed_per_dt = {}
        for i, frame in enumerate(results):
            if i % 30 != 0:
                continue
            # Calculate mean speed for entities in the frame
            speed_modulus_sum_in_dt = sum(character['v'] for character in frame)
            speed_modulus_avg_in_dt = speed_modulus_sum_in_dt / len(frame) if frame else 0
            avg_speed_per_dt[i * dt] = speed_modulus_avg_in_dt
        avg_speed_per_nh[nh] = avg_speed_per_dt

    # Plot the graph with `dt` on the x-axis
    plt.figure(figsize=(10, 6))
    for nh, avg_speed in avg_speed_per_nh.items():
        # Extract time and average speed values for plotting
        time_axis = list(avg_speed.keys())
        speed_values = list(avg_speed.values())
        plt.plot(time_axis, speed_values, label=f"nh = {nh}")

    # Add labels and title
    plt.xlabel("Tiempo (s)")
    plt.ylabel("$\\bar{v}(m/s)$")
    plt.legend()
    plt.grid(True)
    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, f"avg_v_vs_time.png")

    # Save the plot to the file
    plt.savefig(file_path)

    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()


def generate_avg_speed_graph_observable():
    # Load JSON data for all repetitions for nh values (10, 20, ..., 100)
    mean_speed_per_nh_per_repetition: dict[float, list[float]] = {}
    output_directory='avg_v_vs_time'
    for nh in range(100, 101, SKIP):
        mean_speed_per_nh_per_repetition[nh] = []
        for rep in range(REPETITIONS):
            print('Loading nh:', nh, 'rep:', rep)
            simulation = load_simulation_data(nh, rep)
            total_speed_in_simulation = 0
            for frame in simulation['results']:
                total_speed_in_simulation += sum(character['v'] for character in frame)
            mean_speed_per_nh_per_repetition[nh].append(total_speed_in_simulation / (len(simulation['results']) * (nh + 1)))

    avg_speed_per_nh = {}
    std_dev_per_nh = {}

    for nh, speed_list in mean_speed_per_nh_per_repetition.items():
        # Compute the average speed and standard deviation across all repetitions for each nh
        avg_speed_per_nh[nh] = np.mean(speed_list)
        std_dev_per_nh[nh] = np.std(speed_list)

    # Plotting the average speed for each nh value with error bars
    plt.figure(figsize=(10, 6))
    nh_values = list(avg_speed_per_nh.keys())
    avg_speeds = list(avg_speed_per_nh.values())
    std_devs = list(std_dev_per_nh.values())

    plt.errorbar(nh_values, avg_speeds, yerr=std_devs, marker='o', linestyle='-', color='b', capsize=5)

    # Add labels and title
    plt.xlabel("$N_h$")
    plt.ylabel("$\\bar{v}(m/s)$")
    plt.grid(True)
    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, f"avg_v_vs_nh_observable.png")

    # Save the plot to the file
    plt.savefig(file_path)

    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()


def generate_human_and_zombie_avg_speed_observable():
    # Load JSON data for all repetitions for nh values (10, 20, ..., 100)
    human_speed_per_nh_per_repetition: dict[float, list[float]] = {}
    zombie_speed_per_nh_per_repetition: dict[float, list[float]] = {}
    output_directory='avg_v_vs_time'

    for nh in range(100, 101, SKIP):
        human_speed_per_nh_per_repetition[nh] = []
        zombie_speed_per_nh_per_repetition[nh] = []

        for rep in range(REPETITIONS):
            print('Loading nh:', nh, 'rep:', rep)
            simulation = load_simulation_data(nh, rep)

            total_human_speed = 0
            total_zombie_speed = 0
            human_count = 0
            zombie_count = 0

            for frame in simulation['results']:
                for character in frame:
                    if character["type"] == "human":
                        total_human_speed += character['v']
                        human_count += 1
                    elif character["type"] == "zombie":
                        total_zombie_speed += character['v']
                        zombie_count += 1

            # Calculate mean speeds for humans and zombies for this repetition
            mean_human_speed = total_human_speed / human_count if human_count > 0 else 0
            mean_zombie_speed = total_zombie_speed / zombie_count if zombie_count > 0 else 0

            human_speed_per_nh_per_repetition[nh].append(mean_human_speed)
            zombie_speed_per_nh_per_repetition[nh].append(mean_zombie_speed)

    # Calculate average speeds and standard deviations across all repetitions for each nh
    avg_human_speed_per_nh = {nh: np.mean(speeds) for nh, speeds in human_speed_per_nh_per_repetition.items()}
    std_dev_human_per_nh = {nh: np.std(speeds) for nh, speeds in human_speed_per_nh_per_repetition.items()}

    avg_zombie_speed_per_nh = {nh: np.mean(speeds) for nh, speeds in zombie_speed_per_nh_per_repetition.items()}
    std_dev_zombie_per_nh = {nh: np.std(speeds) for nh, speeds in zombie_speed_per_nh_per_repetition.items()}

    # Plotting the average speed for humans and zombies with error bars for each nh value
    plt.figure(figsize=(10, 6))

    nh_values = list(avg_human_speed_per_nh.keys())
    avg_human_speeds = list(avg_human_speed_per_nh.values())
    std_dev_humans = list(std_dev_human_per_nh.values())

    avg_zombie_speeds = list(avg_zombie_speed_per_nh.values())
    std_dev_zombies = list(std_dev_zombie_per_nh.values())

    plt.errorbar(nh_values, avg_human_speeds, yerr=std_dev_humans, marker='o', linestyle='-', color='b', capsize=5, label="Humans")
    plt.errorbar(nh_values, avg_zombie_speeds, yerr=std_dev_zombies, marker='o', linestyle='-', color='r', capsize=5, label="Zombies")

    # Add labels and title
    plt.xlabel("$N_h$")
    plt.ylabel("$\\bar{v}(m/s)$")
    plt.legend()
    plt.grid(True)
    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, f"avg_v_vs_nh_observable.png")

    # Save the plot to the file
    plt.savefig(file_path)

    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()


def generate_frac_zombie_graph():
    # Load JSON data (for nh in 10, 20, ..., 100)
    simulations_per_nh = {}
    output_directory='frac_zombies_vs_time'
    for nh in range(100, 101, SKIP):
        simulations_per_nh[nh] = load_simulation_data(nh, 0)

    zombie_frac_per_nh = {}
    dt_per_nh = {}
    for nh, simulations in simulations_per_nh.items():
        zombie_frac = []
        results = simulations['results']
        dt = __get_dt(simulations)
        dt_per_nh[nh] = dt
        for i, frame in enumerate(results):
            humans = sum(1 for entity in frame if entity["type"] == "human")
            zombies = sum(1 for entity in frame if entity["type"] == "zombie")
            if humans + zombies > 0:
                zombie_frac.append(zombies / (humans + zombies))
            else:
                zombie_frac.append(0)
        zombie_frac_per_nh[nh] = zombie_frac

    # Plot the graph with `dt` on the x-axis
    plt.figure(figsize=(10, 6))
    for nh, zombie_frac in zombie_frac_per_nh.items():
        # Generate time axis based on dt
        time_axis = [i * dt_per_nh[nh] for i in range(len(zombie_frac))]
        plt.plot(time_axis, zombie_frac, label=f"$n_h$ = {nh}")

    # Add labels and title
    plt.xlabel("Tiempo (s)")
    plt.ylabel("$\\langle \\phi_z(t) \\rangle$")
    plt.legend()
    plt.grid(True)
    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, f"frac_zombies_vs_time.png")

    # Save the plot to the file
    plt.savefig(file_path)

    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()


def generate_human_and_zombie_avg_speed_for_single_simulation_graph(nh: int, repetition_no: int):
    """This graph has time as X axis and speed (for humans in blue and zombies in red) as Y axis"""
    # Load JSON data
    simulation = load_simulation_data(nh, repetition_no)
    dt = __get_dt(simulation)
    output_directory='avg_v_vs_time'

    # Initialize dictionaries to store results
    human_speed_per_dt = {}
    zombie_speed_per_dt = {}

    for i, frame in enumerate(simulation['results']):
        if i % 30 != 0:
            continue
        # Calculate mean speed for entities in the frame
        human_speeds = [character['v'] for character in frame if character['type'] == 'human']
        human_speed_sum_in_dt = sum(human_speeds)
        human_amount = len(human_speeds)
        human_speed_avg_in_dt = human_speed_sum_in_dt / human_amount if human_amount > 0 else 0
        human_speed_per_dt[i * dt] = human_speed_avg_in_dt

        zombie_speeds = [character['v'] for character in frame if character['type'] == 'zombie']
        zombie_speed_sum_in_dt = sum(zombie_speeds)
        zombie_amount = len(zombie_speeds)
        zombie_speed_avg_in_dt = zombie_speed_sum_in_dt / zombie_amount if zombie_amount > 0 else 0
        zombie_speed_per_dt[i * dt] = zombie_speed_avg_in_dt

    # Plot the graph with `dt` on the x-axis
    plt.figure(figsize=(10, 6))

    # Extract time and average speed values for plotting
    time_axis = list(human_speed_per_dt.keys())
    human_speed_values = list(human_speed_per_dt.values())
    zombie_speed_values = list(zombie_speed_per_dt.values())

    plt.plot(time_axis, human_speed_values, label="Human speed", color='b')
    plt.plot(time_axis, zombie_speed_values, label="Zombie speed", color='r')

    # Add labels and title
    plt.xlabel("Tiempo (s)")
    plt.ylabel("$\\bar{v}(m/s)$")
    plt.legend()
    plt.grid(True)
    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, f"avg_v_vs_time_nh_{nh}_repetition_{repetition_no}.png")

    # Save the plot to the file
    plt.savefig(file_path)

    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()


def generate_mean_frac_zombie_graph():
    # Initialize dictionaries to store results
    mean_zombie_frac_per_nh = {}
    std_zombie_frac_per_nh = {}
    dt_per_nh = {}
    output_directory='frac_zombies_vs_nh'

    # Iterate over the number of humans (nh) values
    for nh in range(100, 101, SKIP):
        total_humans_per_frame = {}
        total_zombies_per_frame = {}
        dt = None

        # Load each repetition and accumulate totals for each frame
        for rep in range(REPETITIONS):
            print(f'Loading nh: {nh}, rep: {rep}')
            simulation = load_simulation_data(nh, rep)
            if dt is None:
                dt = __get_dt(simulation)  # Get dt from the first repetition

            # Iterate over frames but only take every 30th frame
            for i, frame in enumerate(simulation['results']):
                if i % 400 == 0:  # Process every 30th frame
                    if i not in total_humans_per_frame:
                        total_humans_per_frame[i] = [0, 0]  # [total humans, total zombies]

                    for entity in frame:
                        if entity["type"] == "human":
                            total_humans_per_frame[i][0] += 1
                        elif entity["type"] == "zombie":
                            total_humans_per_frame[i][1] += 1

        # Now compute mean fractions and standard deviations
        mean_frac_per_dt = {}
        std_frac_per_dt = {}

        for i, totals in total_humans_per_frame.items():
            total_humans, total_zombies = totals
            if total_humans + total_zombies > 0:
                mean_frac_for_dt = total_zombies / (total_humans + total_zombies)
                mean_frac_per_dt[i * dt] = mean_frac_for_dt
                std_frac_per_dt[i * dt] = np.sqrt((total_zombies * (1 - mean_frac_for_dt)) / (total_humans + total_zombies))  # Standard deviation formula
            else:
                mean_frac_per_dt[i * dt] = 0
                std_frac_per_dt[i * dt] = 0  # No variance if there are no entities

        mean_zombie_frac_per_nh[nh] = mean_frac_per_dt
        std_zombie_frac_per_nh[nh] = std_frac_per_dt

    # Plot the graph with `dt` on the x-axis
    plt.figure(figsize=(10, 6))
    for idx, nh in enumerate(mean_zombie_frac_per_nh.keys()):
        # Extract time and fraction values for plotting
        time_axis = list(mean_zombie_frac_per_nh[nh].keys())
        fraction_values = list(mean_zombie_frac_per_nh[nh].values())
        error_values = list(std_zombie_frac_per_nh[nh].values())

        plt.plot(time_axis, fraction_values, label=f"$N_h = {nh}$", linewidth=2)
        plt.fill_between(time_axis,
                         np.array(fraction_values) - np.array(error_values),
                         np.array(fraction_values) + np.array(error_values),
                         alpha=0.2)
    # Set y-axis limits to avoid negative values
    plt.ylim(0, 1)
    # Add labels and title
    plt.xlabel("Tiempo (s)", fontsize=14)
    plt.ylabel("$\\langle \\phi_z(t) \\rangle$", fontsize=14)
    plt.legend(loc="best", fontsize=12)
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, "frac_zombies_vs_time_mean.png")

    # Save the plot to the file
    plt.savefig(file_path)

    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()


def generate_mean_frac_zombie_in_all_frames_plot():
    """This has the value of nh on the X axis and the mean last fraction of zombies on the Y axis for all repetitions of that nh."""
    # Initialize variables
    zombie_fraction_by_nh = {}
    std_dev_by_nh = {}
    output_directory='frac_zombies_vs_nh'
    # Iterate over the number of humans (nh) values
    for nh in range(100, 101, SKIP):
        last_zombie_fraction_in_simulation_repetition = []

        for rep in range(REPETITIONS):
            print(f'Loading nh: {nh}, rep: {rep}')
            simulation = load_simulation_data(nh, rep)

            # Process only the last frame to calculate the zombie fraction
            last_frame = simulation['results'][-1]  # Get the last frame
            amount_of_humans = sum(1 for entity in last_frame if entity["type"] == "human")
            amount_of_zombies = sum(1 for entity in last_frame if entity["type"] == "zombie")
            last_zombie_fraction = (
                amount_of_zombies / (amount_of_humans + amount_of_zombies)
                if amount_of_humans + amount_of_zombies > 0
                else 0
            )
            last_zombie_fraction_in_simulation_repetition.append(last_zombie_fraction)

        # Store the mean and standard deviation for each nh
        zombie_fraction_by_nh[nh] = np.mean(last_zombie_fraction_in_simulation_repetition)
        std_dev_by_nh[nh] = np.std(last_zombie_fraction_in_simulation_repetition)

    # Prepare data for plotting
    nh_values = list(zombie_fraction_by_nh.keys())
    means = list(zombie_fraction_by_nh.values())
    std_devs = list(std_dev_by_nh.values())

    # Plot the mean last zombie fraction with error bars
    plt.figure(figsize=(10, 6))
    plt.errorbar(nh_values, means, yerr=std_devs, fmt='-o', capsize=5, color='b', ecolor='blue')
    plt.xlabel("$N_h$")
    plt.ylabel("$\\langle \\phi_z(N_h) \\rangle$ (last frame)")
    plt.grid()
    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, f"frac_zombies_vs_nh.png")

    # Save the plot to the file
    plt.savefig(file_path)

    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()



def generate_frames(data, skip_frames, max_frames=5000):
    arena_radius = data["params"]["arenaRadius"]
    results = data["results"]

    ensure_output_directory_creation('Animations')

    # Delete old frames folder if exists and create a new one
    if os.path.exists('frames'):
        for file in os.listdir('./frames'):
            os.remove(f'frames/{file}')
        os.rmdir('frames')
    os.makedirs('frames')

    results = results[:max_frames]

    # Generate frames
    for i, frame in enumerate(results):
        if i % skip_frames != 0:
            continue
        fig, ax = plt.subplots()
        ax.set_xlim(-arena_radius, arena_radius)
        ax.set_ylim(-arena_radius, arena_radius)
        ax.set_aspect('equal')
        ax.set_title(f"Frame {i}")

        # Draw the circular arena boundary
        arena_boundary = plt.Circle((0, 0), arena_radius, color='black', fill=False, linestyle='--')
        ax.add_patch(arena_boundary)

        # Plot humans and zombies
        for entity in frame:
            x, y = entity['x'], entity['y']
            if entity['type'] == 'human':
                plt.plot(x, y, 'bo')  # Blue circles for humans
            elif entity['type'] == 'zombie':
                plt.plot(x, y, 'ro')  # Red circles for zombies

        # Save frame
        plt.xlabel("x (m)")
        plt.ylabel("y (m)")
        plt.savefig(f'frames/frame_{i:04d}.png')
        print('Frame', i, 'saved')
        plt.close(fig)


def generate_gif(data, skip_frames=30, max_frames=5000):
    # Regular expression to extract frame numbers
    frame_pattern = re.compile(r'frame_(\d+)\.png')

    # Get a sorted list of frame files that match the pattern
    frame_dir = 'frames'
    frames = sorted(
        (f for f in os.listdir(frame_dir) if frame_pattern.match(f)),
        key=lambda x: int(frame_pattern.search(x).group(1))  # Sort by frame number
    )
    frames = frames[:max_frames]

    # Create GIF
    with imageio.get_writer('Animations/simulation.gif', mode='I', duration=data["params"]["dt"]) as writer:
        counter = 0
        for frame_file in frames:
            counter += 1
            if counter % skip_frames != 0:
                continue
            frame_path = os.path.join(frame_dir, frame_file)
            image = imageio.imread(frame_path)
            writer.append_data(image)
            print(f'Creating GIF: {counter / len(frames) * 100:.2f}% done. {counter / skip_frames}/{len(frames) / skip_frames} frames processed.')


def load_simulation_data(nh: int, repetition_no: int, timestamp: str = None, shoot_probability: str | None = None):
    # Base directory where the simulation files are stored
    base_dir = '../outputs'

    # Determine the directory based on the timestamp or find the newest one
    if timestamp:
        target_dir = os.path.join(base_dir, timestamp)
    else:
        # Get all timestamped directories in the outputs folder
        directories = [
            d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))
        ]
        # Sort directories by descending timestamp to get the latest one
        directories.sort(reverse=True)
        target_dir = os.path.join(base_dir, directories[0]) if directories else None

    if not target_dir:
        raise FileNotFoundError("No directories found with the given or latest timestamp.")

    # Construct the filename and path
    if shoot_probability:
        file_name = f"simulation_nh_{nh}_repetition_{repetition_no}_shoot_probability_{shoot_probability}.json"
    else:
        file_name = f"simulation_nh_{nh}_repetition_{repetition_no}.json"

    file_path = os.path.join(target_dir, file_name)

    # Open and load the file
    with open(file_path, 'r') as file:
        data = json.load(file)

    return data


def get_output_directory(timestamp: str = None):
    # Base directory where the simulation files are stored
    base_dir = '../outputs'

    # Determine the directory based on the timestamp or find the newest one
    if timestamp:
        target_dir = os.path.join(base_dir, timestamp)
    else:
        # Get all timestamped directories in the outputs folder
        directories = [
            d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))
        ]
        # Sort directories by descending timestamp to get the latest one
        directories.sort(reverse=True)
        target_dir = os.path.join(base_dir, directories[0]) if directories else None

    if not target_dir:
        raise FileNotFoundError("No directories found with the given or latest timestamp.")

    return target_dir


def ensure_output_directory_creation(directory):
    # Check if the directory exists, if not, create it
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created.")
    else:
        print(f"Directory '{directory}' already exists.")








def generate_frac_zombie_graph_shooting(fixedNH,initialProb, finalProb, probStep):
    ensure_output_directory_creation("frac_zombies_vs_time_probability")
    # Load JSON data (for nh in 10, 20, ..., 100)
    simulations_per_probability = {}
    output_directory='frac_zombies_vs_time_probability'
    ensure_output_directory_creation(output_directory)
    initial_probability = initialProb
    final_probability = finalProb
    probability_step = probStep

    # Scale up by a factor of 100 to use integers
    scale_factor = 100
    scaled_initial = int(initial_probability * scale_factor)
    scaled_final = int(final_probability * scale_factor)
    scaled_step = int(probability_step * scale_factor)


    for scaled_prob in range(scaled_initial, scaled_final + 1, scaled_step):
        probability = scaled_prob / scale_factor
        print(probability)
        
        simulations_per_probability[probability] = load_simulation_data(fixedNH, 6,None,f"{probability:.2f}" )
    zombie_frac_per_probability = {}
    dt_per_probability = {}
    for probability, simulations in simulations_per_probability.items():
        zombie_frac = []
        results = simulations['results']
        dt = __get_dt(simulations)
        dt_per_probability[probability] = dt
        for i, frame in enumerate(results):
            humans = sum(1 for entity in frame if entity["type"] == "human")
            zombies = sum(1 for entity in frame if entity["type"] == "zombie")
            if humans + zombies > 0:
                zombie_frac.append(zombies / (humans + zombies))
            else:
                zombie_frac.append(0)
        zombie_frac_per_probability[probability] = zombie_frac

    # Plot the graph with `dt` on the x-axis
    plt.figure(figsize=(10, 6))
    for probability, zombie_frac in zombie_frac_per_probability.items():
        # Generate time axis based on dt
        time_axis = [i * dt_per_probability[probability] for i in range(len(zombie_frac))]
        plt.plot(time_axis, zombie_frac, label=f"$p$ = {probability}")

    # Add labels and title
    plt.xlabel("Tiempo (s)")
    plt.ylabel("$\\phi_z(t)$")
    plt.legend()
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, f"frac_zombies_vs_time_{time.time()}.png")

    # Save the plot to the file
    plt.savefig(file_path, bbox_inches='tight')  # Ensure the legend is included in the saved file

    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()





def generate_mean_frac_zombie_graph_shooting_observable(fixedNH,initialProb, finalProb, probStep):
    # Initialize dictionaries to store results
    probability_to_repetitions_factor_list: dict[str, list[float]] = {}
    output_directory='frac_zombies_vs_probability_observable'
    ensure_output_directory_creation(output_directory)

    dt = None


    # Scale up by a factor of 100 to use integers
    scale_factor = 100
    scaled_initial = int(initialProb * scale_factor)
    scaled_final = int(finalProb * scale_factor)
    scaled_step = int(probStep * scale_factor)



    for scaled_prob in range(scaled_initial, scaled_final + 1, scaled_step):
        probability = scaled_prob / scale_factor
        probability_to_repetitions_factor_list[probability] = []
        for rep in range(0, REPETITIONS):
            print("Loading repetition",rep,"for probability",probability)
            simulation = load_simulation_data(fixedNH, rep,None,f"{probability:.2f}" )
            if dt is None:
                dt = __get_dt(simulation)  # Get dt from the first repetition

            # Iterate over frames but only take every 30th frame
            realization_frames = []
            humans = 0
            zombies = 0
            for i, frame in enumerate(simulation['results']):
                for entity in frame:
                    if entity["type"] == "human":
                        humans += 1
                    elif entity["type"] == "zombie":
                        zombies += 1
                zombie_fracc = zombies / (zombies + humans)
                realization_frames.append(zombie_fracc)
            
            probability_to_repetitions_factor_list[probability].append(np.mean(realization_frames))
            gc.collect()
    

    # Plot the graph with `dt` on the x-axis
    plt.figure(figsize=(10, 6))
    x_axis = []
    # Calculate means and standard deviations
    means = []
    errors = []
    for prob in probability_to_repetitions_factor_list.keys():
        # Extract time and fraction values for plotting
        x_axis.append(prob)
        repetition_values = probability_to_repetitions_factor_list[prob]
        means.append(np.mean(repetition_values))
        errors.append(np.std(repetition_values)) 

    # Add labels and title
    plt.errorbar(x_axis, means, yerr=errors, fmt="o")
    plt.xlabel("Probabilidades")
    plt.ylabel("$\\langle \\phi_z \\rangle$")
    plt.legend()
    plt.grid(True)
    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, f"frac_zombies_observables_{time.time()}.png")
    # Save the plot to the file
    plt.savefig(file_path)
    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()




def generate_mean_frac_zombie_graph_shooting_observable_last_frame(fixedNH,initialProb, finalProb, probStep):
    # Initialize dictionaries to store results
    probability_to_repetitions_factor_list: dict[str, list[float]] = {}
    output_directory='frac_zombies_vs_probability_observable_solo_final'
    ensure_output_directory_creation(output_directory)

    dt = None


    # Scale up by a factor of 100 to use integers
    scale_factor = 100
    scaled_initial = int(initialProb * scale_factor)
    scaled_final = int(finalProb * scale_factor)
    scaled_step = int(probStep * scale_factor)



    for scaled_prob in range(scaled_initial, scaled_final + 1, scaled_step):
        probability = scaled_prob / scale_factor
        probability_to_repetitions_factor_list[probability] = []
        for rep in range(0, REPETITIONS):
            print("Loading repetition",rep,"for probability",probability)
            simulation = load_simulation_data(fixedNH, rep,None,f"{probability:.2f}" )
            if dt is None:
                dt = __get_dt(simulation)  # Get dt from the first repetition

            last_frame = simulation['results'][-1]  # Get the last frame
            humans = 0
            zombies = 0
            # Count humans and zombies in the last frame
            for entity in last_frame:
                if entity["type"] == "human":
                    humans += 1
                elif entity["type"] == "zombie":
                    zombies += 1
            
            probability_to_repetitions_factor_list[probability].append(zombies / (humans + zombies))
            gc.collect()
    

    # Plot the graph with `dt` on the x-axis
    plt.figure(figsize=(10, 6))
    x_axis = []
    # Calculate means and standard deviations
    means = []
    errors = []
    for prob in probability_to_repetitions_factor_list.keys():
        # Extract time and fraction values for plotting
        x_axis.append(prob)
        repetition_values = probability_to_repetitions_factor_list[prob]
        means.append(np.mean(repetition_values))
        errors.append(np.std(repetition_values)) 

    # Add labels and title
    plt.scatter(x=x_axis,y=means)
    plt.errorbar(x_axis, means, yerr=errors, capsize=5, color="blue")
    plt.xlabel("Probabilidades")
    plt.ylabel("$\\langle \\phi_z \\rangle$")
    plt.grid(True)
    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, f"frac_zombies_observables_{time.time()}.png")
    # Save the plot to the file
    plt.savefig(file_path)
    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()




# NEW OBSERVABLES


def avg_speed_temporal_shooting(initialNh, finalNh, stepNh ,fixedProb : str,repetition_no: int = 0):
    """This graph has time as X axis and speed (for humans in blue and zombies in red) as Y axis"""
    # Load JSON data

    nh_to_avg_speed_simulation : dict[int,list] = {}
    output_directory='avg_speed_temporal_shooting'
    ensure_output_directory_creation(output_directory)
    for humans in range(initialNh, finalNh + 1, stepNh):
        print("in avg_speed_temporal_shooting loading", humans)
        nh_to_avg_speed_simulation[humans] = load_simulation_data(humans, repetition_no, None ,fixedProb)
    
 

    avg_speed_per_nh = {}
    dt_per_nh = {}
    for nh, simulations in nh_to_avg_speed_simulation.items():
        results = simulations['results']
        dt = __get_dt(simulations)
        dt_per_nh[nh] = dt
        avg_speed_per_dt = {}
        for i, frame in enumerate(results):
            # Calculate mean speed for entities in the frame
            speed_modulus_sum_in_dt = sum(character['v'] for character in frame)
            speed_modulus_avg_in_dt = speed_modulus_sum_in_dt / len(frame) if frame else 0
            avg_speed_per_dt[i * dt] = speed_modulus_avg_in_dt
        avg_speed_per_nh[nh] = avg_speed_per_dt
        nh_to_avg_speed_simulation[nh] = None
        gc.collect()

    # Plot the graph with `dt` on the x-axis
    plt.figure(figsize=(10, 6))
    for nh, avg_speed in avg_speed_per_nh.items():
        # Extract time and average speed values for plotting
        time_axis = list(avg_speed.keys())
        speed_values = list(avg_speed.values())
        plt.plot(time_axis, speed_values, label=f"nh = {nh}")

    # Add labels and title
    plt.xlabel("Tiempo (s)")
    plt.ylabel("$\\bar{v}(m/s)$")
    plt.legend()
    plt.grid(True)
    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, f"avg_v_vs_time_{time.time()}.png")
    # Save the plot to the file
    plt.savefig(file_path)
    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()


def generate_frac_zombie_graph_shooting_with_variable_nh_fixed_prob(initialNh, finalNh, stepNh, fixedProb):
    # Load JSON data (for nh in 10, 20, ..., 100)
    simulations_per_nh = {}
    output_directory='generate_frac_zombie_graph_shooting_with_variable_nh_fixed_prob'
    ensure_output_directory_creation(output_directory)


    for humans in range(initialNh, finalNh + 1, stepNh):
        simulations_per_nh[humans] = load_simulation_data(humans, 0,None,f"{fixedProb}" )
    zombie_frac_per_nh = {}
    dt_per_nh = {}
    for nh, simulations in simulations_per_nh.items():
        zombie_frac = []
        results = simulations['results']
        dt = __get_dt(simulations)
        dt_per_nh[nh] = dt
        for i, frame in enumerate(results):
            humans = sum(1 for entity in frame if entity["type"] == "human")
            zombies = sum(1 for entity in frame if entity["type"] == "zombie")
            if humans + zombies > 0:
                zombie_frac.append(zombies / (humans + zombies))
            else:
                zombie_frac.append(0)
        zombie_frac_per_nh[nh] = zombie_frac

    # Plot the graph with `dt` on the x-axis
    plt.figure(figsize=(10, 6))
    for humans, zombie_frac in zombie_frac_per_nh.items():
        # Generate time axis based on dt
        time_axis = [i * dt_per_nh[humans] for i in range(len(zombie_frac))]
        plt.plot(time_axis, zombie_frac, label=f"$Nh$ = {humans}")

    # Add labels and title
    plt.xlabel("Tiempo (s)")
    plt.ylabel("$\\phi_z(t)$")
    plt.legend()
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, f"frac_zombies_vs_time_{time.time()}.png")
    # Save the plot to the file
    plt.savefig(file_path, bbox_inches='tight')  # Ensure the legend is included in the saved file
    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()





def generate_mean_frac_zombie_graph_shooting_observable_last_frame_fixed_nh_variable_prob(initialNh, finalNh, stepNh, fixedProb):
    # Initialize dictionaries to store results
    humans_to_repetitions_factor_list: dict[str, list[float]] = {}
    output_directory='generate_mean_frac_zombie_graph_shooting_observable_last_frame_fixed_nh_variable_prob'
    ensure_output_directory_creation(output_directory)


    for nh in range(initialNh, finalNh + 1, stepNh):
        humans_to_repetitions_factor_list[nh] = []
        for rep in range(0, REPETITIONS):
            print("Loading repetition",rep, "nh",nh,"for probability fixed",fixedProb )
            simulation = load_simulation_data(nh, rep,None,f"{fixedProb}" )

            last_frame = simulation['results'][-1]  # Get the last frame
            humans = 0
            zombies = 0
            # Count humans and zombies in the last frame
            for entity in last_frame:
                if entity["type"] == "human":
                    humans += 1
                elif entity["type"] == "zombie":
                    zombies += 1
            
            humans_to_repetitions_factor_list[nh].append(zombies / (humans + zombies))
            gc.collect()
    

    # Plot the graph with `dt` on the x-axis
    plt.figure(figsize=(10, 6))
    x_axis = []
    # Calculate means and standard deviations
    means = []
    errors = []
    for humans in humans_to_repetitions_factor_list.keys():
        # Extract time and fraction values for plotting
        x_axis.append(humans)
        repetition_values = humans_to_repetitions_factor_list[humans]
        means.append(np.mean(repetition_values))
        errors.append(np.std(repetition_values)) 

    # Add labels and title
    plt.scatter(x=x_axis,y=means)
    plt.errorbar(x_axis, means, yerr=errors, capsize=5, color="blue")
    plt.xlabel("Nh")
    plt.ylabel("$\\langle \\phi_z \\rangle$")
    plt.grid(True)
    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, f"frac_zombies_observables_{time.time()}.png")
    # Save the plot to the file
    plt.savefig(file_path)
    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()


def generate_avg_speed_graph_observable_for_shooting_fixed_prob(initialNh, finalNh, stepNh, fixedProb):
    # Load JSON data for all repetitions for nh values (10, 20, ..., 100)
    mean_speed_per_nh_per_repetition: dict[float, list[float]] = {}
    output_directory='generate_avg_speed_graph_observable_for_shooting_fixed_prob'
    ensure_output_directory_creation(output_directory)
    for nh in range(initialNh, finalNh + 1, stepNh):
        mean_speed_per_nh_per_repetition[nh] = []
        for rep in range(REPETITIONS):
            
            print('Loading in generate_avg_speed_graph_observable_for_shooting_fixed_prob  nh:', nh, 'rep:', rep," for avg_speed_observable_fixed_nh")
            simulation = load_simulation_data(nh, rep , None,f"{fixedProb}")
            total_speed_in_simulation = 0
            for frame in simulation['results']:
                total_speed_in_simulation += sum(character['v'] for character in frame)
            mean_speed_per_nh_per_repetition[nh].append(total_speed_in_simulation / (len(simulation['results']) * (nh + 1)))


    avg_speed_per_nh = {}
    std_dev_per_nh = {}
    for nh, speed_list in mean_speed_per_nh_per_repetition.items():
        # Compute the average speed and standard deviation across all repetitions for each nh
        avg_speed_per_nh[nh] = np.mean(speed_list)
        std_dev_per_nh[nh] = np.std(speed_list)

    # Plotting the average speed for each nh value with error bars
    plt.figure(figsize=(10, 6))
    nh_values = list(avg_speed_per_nh.keys())
    avg_speeds = list(avg_speed_per_nh.values())
    std_devs = list(std_dev_per_nh.values())

    plt.errorbar(nh_values, avg_speeds, yerr=std_devs, marker='o', linestyle='-', color='b', capsize=5)
    # Add labels and title
    plt.xlabel("$N_h$")
    plt.ylabel("$\\bar{v}(m/s)$")
    plt.grid(True)
    # Define the output file path with dt in the filename
    file_path = os.path.join(output_directory, f"avg_v_vs_nh_observable_{time.time()}.png")

    # Save the plot to the file
    plt.savefig(file_path)

    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()


if __name__ == "__main__":
    main()


