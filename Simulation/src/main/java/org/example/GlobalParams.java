package org.example;

public record GlobalParams(
        int minNh, // Minimum number of humans to simulate
        int maxNh, // Maximum number of humasn to simulate
        int nhIncrement, // Increments to get from min to max
        int repetitions, // How many repetitions of each set of params
        double maxTime, // When reached stop the simulation
        double dt, // Integration step
        int saveToMemoryDt, // Save to memory every X dts
        double arenaRadius, // Radius of arena
        double nonSpawnR, // non-spawnable radius from arena wall/zombie
        double rMin, // Min (physical) radius for characters
        double rMax, // Max (social) radius for characters
        double vzMax, // Max (desired) zombie speed
        double vhMax, // Max (desired) human speed
        double sleepTime, // Time to wait whan a human turns into zombie
        double tau, // Constant used in getNextR formula
        double beta, // Constant used in getNextV formula
        double contagionTime // Time that the character remains inactive after contagion process
) { }
