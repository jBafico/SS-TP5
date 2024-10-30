import json
import matplotlib.pyplot as plt
import imageio
import os
import re

def main():
    # Load JSON data
    with open('Simulation/outputs/20241030_195629/simulation_nh_100_repetition_0.json', 'r') as file:
        data = json.load(file)

    arena_radius = data["params"]["arenaRadius"]
    results = data["results"]

    ensure_output_directory_creation('Animations')

    # Create folder for frames
    if not os.path.exists('frames'):
        os.makedirs('frames')

    # Generate frames
    for i, frame in enumerate(results):
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

    # Create GIF
    with imageio.get_writer('Animations/simulation.gif', mode='I', duration=data["params"]["dt"]) as writer:
        for i in range(len(results)):
            frame_path = f'frames/frame_{i:04d}.png'
            image = imageio.imread(frame_path)
            writer.append_data(image)

    # Clean up frames
    for file in os.listdir('frames'):
        os.remove(f'frames/{file}')
    os.rmdir('frames')


def generate_gif(): #TODO encapsulate the GIF making logic
    return 



def load_most_recent_simulation_json(directory_path: str): #TODO make this grab all the files in a folder
    # Define the pattern for matching the file names
    pattern = re.compile(r"ex1_results_\d{8}_\d{6}\.json")

    # Get a list of all files in the directory that match the pattern
    files = [f for f in Path(directory_path).iterdir() if pattern.match(f.name)]

    if not files:
        print("No simulation files found.")
        return None

    # Sort files based on the timestamp in the filename
    most_recent_file = max(files, key=lambda f: f.stem.split('_')[1:])

    # Open and return the JSON data from the file
    with most_recent_file.open('r') as file:
        print(f'Opening file {most_recent_file.name}')
        return json.load(file)

def ensure_output_directory_creation(directory):
    # Check if the directory exists, if not, create it
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created.")
    else:
        print(f"Directory '{directory}' already exists.")


if __name__ == "__main__":
    main()