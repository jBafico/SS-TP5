package org.example;

public record SimulationParams (
    int nh,
    int repetition_no,
    double dt,
    double maxTime,
    double arenaRadius,
    double vzMax,
    double vhMax,
    double sleepTime,
    double rMin,
    double rMax,
    double nonSpawnR,
    Constants constants,
    double contagionTime,
    // Parameters for getNextDesiredTheta heuristic
    int nearestHumansToConsider, // Number of nearest humans to consider in getNextDesiredTheta
    int nearestZombiesToConsider, // Number of nearest zombies to consider in getNextDesiredTheta
    double nearestHumansImportance, // Importance of nearest humans in getNextDesiredTheta
    double nearestZombiesImportance, // Importance of nearest zombies in getNextDesiredTheta
    double wallImportance, // Importance of wall in getNextDesiredTheta
    double humanImportanceDecayAlpha, // Alpha parameter for the exponential decay of the importance of the nearest humans
    double zombieImportanceDecayAlpha, // Alpha parameter for the exponential decay of the importance of the nearest zombies
    double wallImportanceDecayAlpha // Alpha parameter for the exponential decay of the importance of the wall
) {}