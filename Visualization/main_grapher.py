import json
import matplotlib.pyplot as plt
import imageio
import os
import re


def main():
    with open("./config.json", "r") as f:
        config = json.load(f)

    if config["animations"]:
        # Load JSON data
        data = load_simulation_data(10, 0)
        # Generate frames
        generate_frames(data)
        # Create GIF
        generate_gif(data, 5, 10000)
        # Clean up frames
        for file in os.listdir('./frames'):
            os.remove(f'frames/{file}')
        os.rmdir('frames')

    if config["frac_zombie"]:
        generate_frac_zombie_graph()
        generate_mean_frac_zombie_graph()

    if config["avg_v"]:
        # generate_avg_speed_graph()
        generate_avg_speed_graph_observable()
        generate_human_and_zombie_avg_speed_observable()


def generate_avg_speed_graph():
    # Load JSON data (for nh in 10, 20, ..., 100)
    results_per_nh = {}
    for nh in range(10, 101, 10):
        results_per_nh[nh] = load_simulation_data(nh, 0)['results']

    avg_speed_per_nh = {}
    dt_per_nh = {}
    for nh, results in results_per_nh.items():
        dt = results[0][0]['config']['dt']
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
    plt.xlabel("Time (seconds)")
    plt.ylabel("Average Speed of Entities")
    plt.title("Average Speed of Entities over Time for Different nh values")
    plt.legend(title="Number of Humans (nh)")
    plt.grid(True)
    plt.show()


def generate_avg_speed_graph_observable():
    # Load JSON data for all repetitions for nh values (10, 20, ..., 100)
    mean_speed_per_nh_per_repetition: dict[float, list[float]] = {}
    for nh in range(10, 101, 10):
        mean_speed_per_nh_per_repetition[nh] = []
        for rep in range(10):
            print('Loading nh:', nh, 'rep:', rep)
            simulation = load_simulation_data(nh, rep)
            total_speed_in_simulation = 0
            for frame in simulation['results']:
                total_speed_in_simulation += sum(character['v'] for character in frame)
            mean_speed_per_nh_per_repetition[nh].append(total_speed_in_simulation / (len(simulation['results']) * (nh+1)))

    print(mean_speed_per_nh_per_repetition)
    avg_speed_per_nh = {}
    for nh, speed_list in mean_speed_per_nh_per_repetition.items():
        # Compute the average speed across all repetitions for each nh
        avg_speed_per_nh[nh] = sum(speed_list) / len(speed_list)

    # Plotting the average speed for each nh value
    plt.figure(figsize=(10, 6))
    nh_values = list(avg_speed_per_nh.keys())
    avg_speeds = list(avg_speed_per_nh.values())

    plt.plot(nh_values, avg_speeds, marker='o', linestyle='-', color='b')

    # Add labels and title
    plt.xlabel("Number of Humans (nh)")
    plt.ylabel("Average Speed of Entities")
    plt.title("Average Speed of Entities for Different nh values")
    plt.grid(True)
    plt.show()


def generate_human_and_zombie_avg_speed_observable():
    # Load JSON data for all repetitions for nh values (10, 20, ..., 100)
    human_speed_per_nh_per_repetition: dict[float, list[float]] = {}
    zombie_speed_per_nh_per_repetition: dict[float, list[float]] = {}

    for nh in range(10, 101, 10):
        human_speed_per_nh_per_repetition[nh] = []
        zombie_speed_per_nh_per_repetition[nh] = []

        for rep in range(10):
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

    # Calculate average speeds across all repetitions for each nh
    avg_human_speed_per_nh = {nh: sum(speeds) / len(speeds) for nh, speeds in human_speed_per_nh_per_repetition.items()}
    avg_zombie_speed_per_nh = {nh: sum(speeds) / len(speeds) for nh, speeds in zombie_speed_per_nh_per_repetition.items()}

    # Plotting the average speed for humans and zombies for each nh value
    plt.figure(figsize=(10, 6))

    nh_values = list(avg_human_speed_per_nh.keys())
    avg_human_speeds = list(avg_human_speed_per_nh.values())
    avg_zombie_speeds = list(avg_zombie_speed_per_nh.values())

    plt.plot(nh_values, avg_human_speeds, marker='o', linestyle='-', color='b', label="Humans")
    plt.plot(nh_values, avg_zombie_speeds, marker='o', linestyle='-', color='r', label="Zombies")

    # Add labels and title
    plt.xlabel("Number of Humans (nh)")
    plt.ylabel("Average Speed of Entities")
    plt.title("Average Speed of Humans and Zombies for Different nh values")
    plt.legend()
    plt.grid(True)
    plt.show()


def generate_frac_zombie_graph():
    # Load JSON data (for nh in 10, 20, ..., 100)
    results_per_nh = {}
    for nh in range(10, 101, 10):
        results_per_nh[nh] = load_simulation_data(nh, 0)['results']

    zombie_frac_per_nh = {}
    dt_per_nh = {}
    for nh, results in results_per_nh.items():
        zombie_frac = []
        dt = results[0][0]['config']['dt']
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
        plt.plot(time_axis, zombie_frac, label=f"nh = {nh}")

    # Add labels and title
    plt.xlabel("Time (seconds)")
    plt.ylabel("Fraction of Zombies")
    plt.title("Fraction of Zombies over Time for Different nh values")
    plt.legend(title="Number of Humans (nh)")
    plt.grid(True)
    plt.show()


def generate_mean_frac_zombie_graph():
    # Load JSON data for all repetitions for nh values (10, 20, ..., 100)
    results_per_nh_reps = {}
    for nh in range(10, 101, 10):
        results_per_nh_reps[nh] = [load_simulation_data(nh, rep)['results'] for rep in range(10)]

    mean_zombie_frac_per_nh = {}
    dt_per_nh = {}

    for nh, repetitions in results_per_nh_reps.items():
        dt = repetitions[0][0][0]['config']['dt']  # Assuming dt is the same across repetitions
        dt_per_nh[nh] = dt
        mean_frac_per_dt = {}

        # Iterate over frames by index for averaging across repetitions
        for i in range(len(repetitions[0])):  # Assuming all repetitions have the same number of frames
            total_zombies = 0
            total_humans = 0

            for frame in repetitions:
                entities = frame[i]
                humans = sum(1 for entity in entities if entity["type"] == "human")
                zombies = sum(1 for entity in entities if entity["type"] == "zombie")
                total_humans += humans
                total_zombies += zombies

            if total_humans + total_zombies > 0:
                mean_frac_for_dt = total_zombies / (total_humans + total_zombies)
            else:
                mean_frac_for_dt = 0

            mean_frac_per_dt[i * dt] = mean_frac_for_dt  # Time = i * dt

        mean_zombie_frac_per_nh[nh] = mean_frac_per_dt

    # Plot the graph with `dt` on the x-axis
    plt.figure(figsize=(10, 6))
    for nh, zombie_frac in mean_zombie_frac_per_nh.items():
        # Extract time and fraction values for plotting
        time_axis = list(zombie_frac.keys())
        fraction_values = list(zombie_frac.values())
        plt.plot(time_axis, fraction_values, label=f"nh = {nh}")

    # Add labels and title
    plt.xlabel("Time (seconds)")
    plt.ylabel("Mean Fraction of Zombies")
    plt.title("Mean Fraction of Zombies over Time for Different nh values")
    plt.legend(title="Number of Humans (nh)")
    plt.grid(True)
    plt.show()


def generate_frames(data):
    arena_radius = data["params"]["arenaRadius"]
    results = data["results"]

    ensure_output_directory_creation('Animations')

    # Delete old frames folder if exists and create a new one
    if os.path.exists('frames'):
        for file in os.listdir('./frames'):
            os.remove(f'frames/{file}')
        os.rmdir('frames')
    os.makedirs('frames')

    # Generate frames
    for i, frame in enumerate(results):
        # if i % 10 != 0:
        #     continue
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
            x, y = entity['coordinates']['x'], entity['coordinates']['y']
            if entity['type'] == 'human':
                plt.plot(x, y, 'bo')  # Blue circles for humans
            elif entity['type'] == 'zombie':
                plt.plot(x, y, 'ro')  # Red circles for zombies

        # Save frame
        plt.savefig(f'frames/frame_{i:04d}.png')
        print('Frame', i, 'saved')
        plt.close(fig)


def generate_gif(data, skip_frames=1, max_frames=100000):
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


def load_simulation_data(nh: int, repetition_no: int, timestamp: str = None):
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


if __name__ == "__main__":
    main()
