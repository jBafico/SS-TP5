package org.example;

public record SimulationParams (
    int nh,
    int nz,
    int repetition_no,
    double dt,
    double maxTime,
    double ra,
    double r,
    double vzMax,
    double vhMax,
    double sleepTime,
    double characterRadius
) {}