package org.example;

public record GlobalParams(
        int minNh, // Minimum number of humans to simulate
        int maxNh, // Maximum number of humasn to simulate
        int nhIncrement, // Increments to get from min to max
        int nz, // Number of zombies
        int repetitions, // How many repetitions of each set of params
        double maxTime,
        double dt, // Integration step
        int saveToMemoryDt, // Save to memory every X dts
        double ra, // Radius of arena
        double r, // non-spawnable radius from arena wall/zombie
        double vzMax, // Max zombie speed
        double vhMax, // Max human speed
        double sleepTime, // Time to wait whan a human turns into zombie
        double characterRadius // Radius of each character
) { }
