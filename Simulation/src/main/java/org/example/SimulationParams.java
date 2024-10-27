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
    double contagionTime
) {}