package org.example;

import java.util.List;

public class Human extends Character {
    public Human(Coordinates coordinates, Constants constants, CharacterConfig config) {
        super(coordinates, constants, config, "human");
    }

    private Human(Coordinates coordinates, Constants constants, CharacterConfig config, double v, double theta, double r, double remainingContagion) {
        super(coordinates, constants, config, v, theta, r, "human", remainingContagion);
    }

    @Override
    protected Character createNextInstance(Coordinates coordinates, double v, double theta, double r, double remainingContagion) {
        return new Human(coordinates, this.getConstants(), this.getConfig(), v, theta, r, remainingContagion);
    }


    @Override
protected double getNextDesiredTheta(List<Character> characterList, Wall wall) {
    // 1. Identify nearest characters and wall collision point
    List<Character> nearestZombies = this.findNNearestZombies(characterList, getConfig().nearestZombiesToConsider());
    List<Character> nearestHumans = this.findNNearestHumans(characterList, getConfig().nearestHumansToConsider());
    Coordinates nearestPointToWall = wall.nearestPointToWall(this.getCoordinates());

    // 2. Set weighted sums for zombies, humans, and wall points
    double baseZombieWeight = getConfig().nearestZombiesImportance();
    double baseHumanWeight = getConfig().nearestHumansImportance();
    double baseWallWeight = getConfig().wallImportance();

    // Exponential decay constants
    double humanImportanceDecayAlpha = getConfig().humanImportanceDecayAlpha();
    double zombieImportanceDecayAlpha = getConfig().zombieImportanceDecayAlpha();
    double wallImportanceDecayAlpha = getConfig().wallImportanceDecayAlpha();

    // Initialize sums for weighted coordinates
    double weightedSumX = 0;
    double weightedSumY = 0;
    double totalWeight = 0;

    // 3. Calculate and apply avoidance for zombies
    for (Character zombie : nearestZombies) {
        double distance = this.distanceToCollision(zombie);
        double effectiveWeight = baseZombieWeight * Math.exp(-distance / zombieImportanceDecayAlpha);
        weightedSumX += zombie.getX() * effectiveWeight;
        weightedSumY += zombie.getY() * effectiveWeight;
        totalWeight += effectiveWeight;
    }

    // 4. Calculate and apply avoidance for humans
    for (Character human : nearestHumans) {
        double distance = this.distanceToCollision(human);
        double effectiveWeight = baseHumanWeight * Math.exp(-distance / humanImportanceDecayAlpha);
        weightedSumX += human.getX() * effectiveWeight;
        weightedSumY += human.getY() * effectiveWeight;
        totalWeight += effectiveWeight;
    }

    // 5. Calculate and apply wall avoidance
    double wallDistance = this.getCoordinates().distanceTo(nearestPointToWall);
    double effectiveWallWeight = baseWallWeight * Math.exp(-wallDistance / wallImportanceDecayAlpha);
    weightedSumX += nearestPointToWall.getX() * effectiveWallWeight;
    weightedSumY += nearestPointToWall.getY() * effectiveWallWeight;
    totalWeight += effectiveWallWeight;

    // Calculate the danger point coordinates
    double dangerPointX = weightedSumX / totalWeight;
    double dangerPointY = weightedSumY / totalWeight;

    // Calculate the direction vector away from the danger point
    double escapeDeltaX = this.getX() - dangerPointX;
    double escapeDeltaY = this.getY() - dangerPointY;

    // Compute the angle of escape to avoid collisions
    double escapeAngle = Math.atan2(escapeDeltaY, escapeDeltaX);

    if (escapeAngle < 0) {
        escapeAngle += 2 * Math.PI; // Convert to a positive angle in [0, 2π]
    }

    // 6. Check for boundary collision and adjust angle if near boundary
    if (wallDistance < getR()) {
        escapeAngle = wall.reflectAngle(nearestPointToWall);
    }

    return escapeAngle;
}

    public Zombie collidingZombie(List<Character> characterList) {
        // Return all the colliding zombies
        return characterList
                .stream()
                .filter(c -> c instanceof Zombie && this.isCollidingWithCharacter(c))
                .map(c -> (Zombie) c)
                .findFirst()
                .orElse(null);
    }
}
