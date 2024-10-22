package org.example;

public record GlobalParams(
        int Nh, //Number of humans
        int Nz, //Number of zombies
        double Ra, // Radius of arena
        double r //non-spawnable radius from arena wall/zombie
) { }
