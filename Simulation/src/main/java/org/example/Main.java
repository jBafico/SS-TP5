package org.example;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Date;

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
                    SimulationParams simulationParams = new SimulationParams(nh, params.nz(), repetition_no, params.dt(), params.maxTime(), params.ra(), params.r(), params.vzMax(), params.vhMax(), params.sleepTime(), params.characterRadius());
                    PDSimulation simulation = new PDSimulation();
                    simulation.run(simulationParams);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }

        // Get the current timestamp
        String timestamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
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
}