import json
import matplotlib.pyplot as plt
import imageio
import os
import re
import glob
import numpy as np

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
        for file in os.listdir('frames'):
            os.remove(f'frames/{file}')
        os.rmdir('frames')

    ruta_archivos = get_output_directory()
    archivos = glob.glob(os.path.join(ruta_archivos, '*.json'))
    
    if config["frac_zombie"]: #TODO hacer graficos zombies vs tiempo
        fracciones_por_tiempo = {}  # Guarda las fracciones de zombies en función del tiempo para cada simulación
        fraccion_final_por_humanos = []  # Guarda la fracción final de zombies para cada número de humanos iniciales


        # Iterar sobre cada archivo JSON
        for archivo in archivos:
            with open(archivo, 'r') as f:
                data = json.load(f)
                nh = data['params']['nh']  # Número de humanos iniciales
                resultados = data['results']  # Datos de resultados por frame
                tiempos = []
                fracciones_zombies = []

                # Iterar sobre cada frame de la simulación
                for frame_no, frame in enumerate(resultados):
                    num_humanos = sum(1 for entity in frame if entity["type"] == "human")
                    num_zombies = sum(1 for entity in frame if entity["type"] == "zombie")
                    fraccion_zombies = num_zombies / (num_humanos + 1)
                    tiempos.append(frame_no * data['params']['dt'])
                    fracciones_zombies.append(fraccion_zombies)
                
                # Guardar los datos para graficar en función del tiempo
                fracciones_por_tiempo[nh] = (tiempos, fracciones_zombies)

                final_fraction = fraccion_zombies[-1] if isinstance(fraccion_zombies, list) else fraccion_zombies
                
                # Guardar la fracción final de zombies al final de la simulación
                fraccion_final_por_humanos.append((nh, final_fraction))

            
        frac_zombies_vs_time(fracciones_por_tiempo)
        frac_zombies_vs_nh(fraccion_final_por_humanos)

    if config["avg_v"]:
        velocidades_por_tiempo = {}  # Guarda las velocidades medias en función del tiempo para cada simulación
        velocidad_media_por_humanos = []  # Guarda la velocidad media al final de la simulación para cada número de humanos iniciales


        # Iterar sobre cada archivo JSON
        for archivo in archivos:
            with open(archivo, 'r') as f:
                data = json.load(f)
                nh = data['params']['nh']  # Número de humanos iniciales
                resultados = data['results']  # Datos de resultados por frame
                velocidades_medias = []

                for frame_no, frame in enumerate(resultados):
                    # Calcular la velocidad media para este frame
                    velocidades = [entity['velocity'] for entity in frame if 'velocity' in entity]
                    velocidad_media = np.mean(velocidades) if velocidades else 0
                    velocidades_medias.append(velocidad_media)

                velocidades_por_tiempo[nh] = (tiempos, velocidades_medias)

        avg_v_vs_time(velocidades_por_tiempo)
        
        #TODO este grafico
        #avg_v_vs_nh(velocidad_media_por_humanos)


def generate_frames(data):
    arena_radius = data["params"]["arenaRadius"]
    results = data["results"]

    ensure_output_directory_creation('Animations')

    # Delete old frames folder if exists and create a new one
    if os.path.exists('frames'):
        os.rmdir('frames')
    os.makedirs('frames')

    # Generate frames
    for i, frame in enumerate(results):
        if i % 10 != 0:
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
            x, y = entity['coordinates']['x'], entity['coordinates']['y']
            if entity['type'] == 'human':
                plt.plot(x, y, 'bo')  # Blue circles for humans
            elif entity['type'] == 'zombie':
                plt.plot(x, y, 'ro')  # Red circles for zombies

        # Save frame
        plt.savefig(f'frames/frame_{i:04d}.png')
        print('Frame', i, 'saved')
        plt.close(fig)


def generate_gif(data, skip_frames = 1, max_frames = 100000):
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
            print(f'Creating GIF: {counter/len(frames)*100:.2f}% done. {counter/skip_frames}/{len(frames)/skip_frames} frames processed.')

def frac_zombies_vs_time(fracciones_por_tiempo):
    ensure_output_directory_creation('frac_zombies_vs_time')
    plt.figure(figsize=(10, 6))
    for nh, (tiempos, fracciones_zombies) in fracciones_por_tiempo.items():
        plt.plot(tiempos, fracciones_zombies, label=f'Nh: {nh}')

    plt.xlabel('Time (s)')
    plt.ylabel('$\\langle \\phi_z(t) \\rangle$')
    plt.legend()
    plt.grid(True)
    # Define the output file path with dt in the filename
    file_path = os.path.join('frac_zombies_vs_time', f"frac_zombies_vs_time.png")

    # Save the plot to the file
    plt.savefig(file_path)

    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()

    print(f"Saved plot to '{file_path}'")
    

def frac_zombies_vs_nh(fraccion_final_por_humanos):
    ensure_output_directory_creation('frac_zombies_vs_nh')
    # Graficar fracción final de zombies en función del número de humanos iniciales
    humanos_iniciales, fracciones_finales = zip(*sorted(fraccion_final_por_humanos))

    plt.figure(figsize=(10, 6))
    plt.plot(humanos_iniciales, fracciones_finales, marker='o')
    plt.xlabel('N_h')
    plt.ylabel('$\\langle \\phi_z ^final \\rangle$')
    plt.grid(True)
    
    # Define the output file path with dt in the filename
    file_path = os.path.join('frac_zombies_vs_nh', f"frac_zombies_vs_nh.png")

    # Save the plot to the file
    plt.savefig(file_path)

    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()

    print(f"Saved plot to '{file_path}'")
    

def avg_v_vs_time(velocidades_por_tiempo):
    ensure_output_directory_creation('avg_v_vs_time')
    plt.figure(figsize=(10, 6))

    for nh, (tiempos, velocidades) in velocidades_por_tiempo.items():
        plt.plot(tiempos, velocidades, label=f'N_h = {nh}')

    plt.xlabel("Time (s)")
    plt.ylabel("Velocidad media del sistema")
    plt.legend()
     # Define the output file path with dt in the filename
    file_path = os.path.join('avg_v_vs_time', f"avg_v_vs_time.png")

    # Save the plot to the file
    plt.savefig(file_path)

    # Optionally, you can clear the current figure to prevent overlay issues in future plots
    plt.clf()

    print(f"Saved plot to '{file_path}'")
    

def avg_v_vs_nh(data):
    ensure_output_directory_creation('avg_v_vs_nh')
    
    

def load_simulation_data(nh: int, repetition_no: int, timestamp: str = None):
    # Base directory where the simulation files are stored
    base_dir = '../Simulation/outputs'

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

def get_output_directory(timestamp: str= None):
     # Base directory where the simulation files are stored
    base_dir = '../Simulation/outputs'

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