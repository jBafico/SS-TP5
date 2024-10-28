package org.example;

import java.util.List;

public class Human extends Character {
    public Human(Coordinates coordinates, Constants constants, CharacterConfig config) {
        super(coordinates, constants, config);
    }

    @Override
    protected double getNextTheta(List<Character> characterList, Wall wall) {
        /* The human is more intelligent than the zombie, it tries to avoid humans, zombies and the wall */

        int nearestZombiesToConsider = 4;
        int nearestHumansToConsider = 2;
        double maxFactor = 4;

        // Find nearest zombies and humans
        List<Character> nearestZombies = this.findNNearestZombies(characterList, nearestZombiesToConsider, maxFactor);
        List<Character> nearestHumans = this.findNNearestHumans(characterList, nearestHumansToConsider, maxFactor);

        // Get the nearest point to the wall
        Coordinates nearestPointToWall = wall.nearestPointToWall(this.getCoordinates());

        // Base weights for zombies, humans, and wall point
        double baseZombieWeight = 1;
        double baseHumanWeight = 0.3;
        double baseWallWeight = 0.5;

        // Exponential decay constant
        double alpha = 0.5;

        // Initialize sums for weighted x and y coordinates
        double weightedSumX = 0;
        double weightedSumY = 0;
        double totalWeight = 0;

        // Weighted sum of zombie coordinates with exponential decay based on distance
        for (Character zombie : nearestZombies) {
            double distance = this.distanceToCollision(zombie);
            double effectiveWeight = baseZombieWeight * Math.exp(-alpha * distance);
            weightedSumX += zombie.getX() * effectiveWeight;
            weightedSumY += zombie.getY() * effectiveWeight;
            totalWeight += effectiveWeight;
        }

        // Weighted sum of human coordinates with exponential decay based on distance
        for (Character human : nearestHumans) {
            double distance = this.distanceToCollision(human);
            double effectiveWeight = baseHumanWeight * Math.exp(-alpha * distance);
            weightedSumX += human.getX() * effectiveWeight;
            weightedSumY += human.getY() * effectiveWeight;
            totalWeight += effectiveWeight;
        }

        // Weighted sum of the wall point coordinates with exponential decay based on distance
        double wallDistance = this.getCoordinates().distanceTo(nearestPointToWall);
        double effectiveWallWeight = baseWallWeight * Math.exp(-alpha * wallDistance);
        weightedSumX += nearestPointToWall.getX() * effectiveWallWeight;
        weightedSumY += nearestPointToWall.getY() * effectiveWallWeight;
        totalWeight += effectiveWallWeight;

        // Calculate the average danger point coordinates
        double dangerPointX = weightedSumX / totalWeight;
        double dangerPointY = weightedSumY / totalWeight;

        // Calculate the direction vector away from the danger point
        double escapeDeltaX = this.getX() - dangerPointX;
        double escapeDeltaY = this.getY() - dangerPointY;

        // Calculate and return the escape angle theta in radians
        return Math.atan2(escapeDeltaY, escapeDeltaX);
    }
}
