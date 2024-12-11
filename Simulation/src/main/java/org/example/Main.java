package org.example;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class Main {
    public static void main(String[] args) {
        GlobalParams params = null;
        try {
            // Load the JSON file from resources
            InputStream inputStream = Main.class.getClassLoader().getResourceAsStream("./globalParams.json");

            // Create an ObjectMapper instance
            ObjectMapper objectMapper = new ObjectMapper();

            // Read the JSON and map it to the Params class
            params = objectMapper.readValue(inputStream, GlobalParams.class);

            // Create an output folder with the current datetime
            Path outputDirectoryPath = createSimulationOutputDirectory(LocalDateTime.now());

            // Iterate through the repetitions
            for (int repetition_no = 0; repetition_no < params.repetitions(); repetition_no++) {
                // Iterate through the starting number of humans
                for (int nh = params.minNh(); nh <= params.maxNh(); nh += params.nhIncrement()) {
                    // Iterate through the different shoot probabilities
                    for (double shootProbability = params.minShootProbability(); shootProbability <= params.maxShootProbability(); shootProbability += params.shootProbabilityIncrement()){
                        // Run the simulation
                        System.out.printf("Running simulation with nh: %d, repetition_no: %d, shoot probability: %s\n", nh, repetition_no, shootProbability);
                        double dt = params.rMin() / (2 * params.vhMax());
                        SimulationParams simulationParams = new SimulationParams(
                                nh, repetition_no, dt, params.maxTime(), params.arenaRadius(), params.vzMax(), params.vhMax(), params.sleepTime(), params.rMin(), params.rMax(), params.nonSpawnR(),
                                new Constants(params.tau(), params.beta(), params.mu()), params.contagionTime(),
                                params.nearestHumansToConsider(), params.nearestZombiesToConsider(), params.nearestHumansImportance(), params.nearestZombiesImportance(), params.wallImportance(), params.humanImportanceDecayAlpha(), params.zombieImportanceDecayAlpha(), params.wallImportanceDecayAlpha(),
                                params.maxShootRange(), shootProbability, params.shootReloadTime(), params.minShootProportion()
                        );
                        PDSimulation simulation = new PDSimulation(simulationParams);
                        SimulationResults results = simulation.run();

                        // Write the results to a file
                        writeOutput(results, outputDirectoryPath.toString(), shootProbability);
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
    }

    private static Path createSimulationOutputDirectory(LocalDateTime datetime) {
        // Format datetime as 'yyyyMMdd_HHmmss'
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");
        String formattedDateTime = datetime.format(formatter);

        // Define paths for 'outputs' and datetime folder within it
        Path outputsPath = Paths.get("outputs");
        Path dateTimeFolderPath = outputsPath.resolve(formattedDateTime);

        // Check if 'outputs' folder exists, else create it
        try {
            if (!Files.exists(outputsPath)) {
                Files.createDirectory(outputsPath);
                System.out.println("Created 'outputs' folder.");
            }

            // Create folder for the specified datetime inside 'outputs'
            Files.createDirectory(dateTimeFolderPath);
            return dateTimeFolderPath; // Return the path of the created directory
        } catch (IOException e) {
            System.err.println("Failed to create directory: " + e.getMessage());
            return null; // Return null if there's an issue
        }
    }

    public static void writeOutput(SimulationResults results, String outputDirectoryPath,double shootProbability) {
        try {
            // Create the output directory if it doesn't exist
            Files.createDirectories(Path.of(outputDirectoryPath));

            // Create an ObjectMapper instance
            ObjectMapper objectMapper = new ObjectMapper();

            String formattedShootProbability = formatFloat(shootProbability);

            // Define the output file with a unique name for each simulation result
            System.out.printf("Shoot prob %s%n", formattedShootProbability);
            String filename = String.format("simulation_nh_%d_repetition_%d_shoot_probability_%s.json", results.params().nh(), results.params().repetition_no(), formattedShootProbability);
            File outputFile = new File(outputDirectoryPath, filename);

            // Write the SimulationResults to the file in JSON format
            objectMapper.writeValue(outputFile, results);

            System.out.printf("Results successfully written to %s\n", outputFile.getAbsolutePath());

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static String formatFloat(double value) {
        return String.format("%.2f", value);
    }


}