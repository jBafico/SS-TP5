package org.example;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.BufferedWriter;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Date;
import java.util.List;

public class Main {
    public static void main(String[] args) {

        System.out.println("Starting simulation!");

        GlobalParams params = null;
        try {
            // Load the JSON file from resources
            InputStream inputStream = Main.class.getClassLoader().getResourceAsStream("./GlobalParams.json");

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
                    // Run the simulation
                    System.out.printf("Running simulation with nh: %d, repetition_no: %d\n", nh, repetition_no);
                    double dt = params.rMin() / (2 * params.vhMax());
                    SimulationParams simulationParams = new SimulationParams(nh, repetition_no, dt, params.maxTime(), params.arenaRadius(), params.vzMax(), params.vhMax(), params.sleepTime(), params.rMin(), params.rMax(), params.nonSpawnR(), new Constants(params.tau(), params.beta(), params.mu()), params.contagionTime(), params.nearestHumansToConsider(), params.nearestZombiesToConsider(), params.nearestHumansImportance(), params.nearestZombiesImportance(), params.wallImportance(), params.maxLengthFactor(), params.humanImportanceDecayAlpha(), params.zombieImportanceDecayAlpha(), params.wallImportanceDecayAlpha());
                    PDSimulation simulation = new PDSimulation(simulationParams);
                    SimulationResults results = simulation.run();
                    System.out.println("Simulation finished!");

                    System.out.println("Writing output...");
                    writeOutput(results, outputDirectoryPath.toString());
                    System.out.println("Output written!");
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

    public static void writeOutput(SimulationResults results, String outputDirectoryPath) {
        try {
            // Create the output directory if it doesn't exist
            Files.createDirectories(Path.of(outputDirectoryPath));

            // Create an ObjectMapper instance
            ObjectMapper objectMapper = new ObjectMapper();

            // Define the output file with a unique name for each simulation result
            String filename = String.format("simulation_nh_%d_repetition_%d.json",
                    results.params().nh(), results.params().repetition_no());
            File outputFile = new File(outputDirectoryPath, filename);

            // Write the SimulationResults to the file in JSON format
            objectMapper.writerWithDefaultPrettyPrinter().writeValue(outputFile, results);

            System.out.printf("Results successfully written to %s\n", outputFile.getAbsolutePath());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


}