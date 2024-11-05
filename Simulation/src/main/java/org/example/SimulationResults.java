package org.example;

import java.util.List;

public record SimulationResults (
    SimulationParams params,
    List<List<Character>> results,
    double meanCharacterSpeed
) {}
