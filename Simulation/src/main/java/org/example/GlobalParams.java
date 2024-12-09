package org.example;

public record GlobalParams(
        // Parameters that change between simulations
        int minNh, // Minimum number of humans to simulate
        int maxNh, // Maximum number of humasn to simulate
        int nhIncrement, // Increments to get from min to max
        int repetitions, // How many repetitions of each set of params

        // Parameters that are constant between simulations
        double maxTime, // When reached stop the simulation
        double arenaRadius, // Radius of arena
        double nonSpawnR, // non-spawnable radius from arena wall and initial zombie
        double rMin, // Min (physical) radius for characters
        double rMax, // Max (social) radius for characters
        double vzMax, // Max (desired) zombie speed
        double vhMax, // Max (desired) human speed
        double sleepTime, // Time to wait when a human turns into zombie
        double tau, // Constant used in getNextR formula
        double beta, // Constant used in getNextV formula
        double mu, // Constant used for noise in getNextTheta formula
        double contagionTime, // Time that the character remains inactive after contagion process

        // Parameters for getNextDesiredTheta heuristic
        int nearestHumansToConsider, // Number of nearest humans to consider in getNextDesiredTheta
        int nearestZombiesToConsider, // Number of nearest zombies to consider in getNextDesiredTheta
        int nearestHumansImportance, // Importance of nearest humans in getNextDesiredTheta
        double nearestZombiesImportance, // Importance of nearest zombies in getNextDesiredTheta
        double wallImportance, // Importance of wall in getNextDesiredTheta
        double humanImportanceDecayAlpha, // Alpha parameter for the exponential decay of the importance of the nearest humans
        double zombieImportanceDecayAlpha, // Alpha parameter for the exponential decay of the importance of the nearest zombies
        double wallImportanceDecayAlpha, // Alpha parameter for the exponential decay of the importance of the wall

        // Params for shooting
        double maxShootRange, // Maximum range of a human's shooting ability
        double shootProbability, // Probability of a zombie being killed
        int shootInterval, // Time interval between shots
        double minShootProportion // Minimum proportion of zombies to shoot
) { }
