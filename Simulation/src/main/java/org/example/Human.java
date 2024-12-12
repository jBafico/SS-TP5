package org.example;

import java.util.List;

public class Human extends Character {
    public Human(Coordinates coordinates, Constants constants, CharacterConfig config, boolean inContagion, int shootReloadTime) {
        super(coordinates, constants, config, "human", inContagion, shootReloadTime, shootReloadTime);
    }

    private Human(Coordinates coordinates, Constants constants, CharacterConfig config, double v, double theta, double r, double remainingContagion, boolean inContagion, int shootReloadTime, int shootReloadTimeLeft) {
        super(coordinates, constants, config, v, theta, r, "human", remainingContagion, inContagion, shootReloadTime, shootReloadTimeLeft);
    }

    @Override
    protected Character createNextInstance(Coordinates coordinates, double v, double theta, double r, double remainingContagion, boolean inContagion) {
        int newShootReloadTimeLeft;
        if (this.hasShot) { // If the human has shot, reset the reload time
            newShootReloadTimeLeft = this.shootReloadTime;
        } else if (this.shootReloadTimeLeft > 0) { // If the human has not shot, decrement the reload time
            newShootReloadTimeLeft = this.shootReloadTimeLeft - 1;
        } else { // If the reload time is already 0, keep it at 0
            newShootReloadTimeLeft = 0;
        }
        return new Human(coordinates, this.getConstants(), this.getConfig(), v, theta, r, remainingContagion, inContagion, shootReloadTime, newShootReloadTimeLeft);
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

        // 3. Calculate and apply avoidance for zombies
        for (Character zombie : nearestZombies) {
            double distance = this.distanceToCollision(zombie);
            if (distance == 0) continue; // Avoid division by zero
            double directionX = zombie.getX() - this.getX();
            double directionY = zombie.getY() - this.getY();
            double weight = baseZombieWeight * Math.exp(-distance / zombieImportanceDecayAlpha);
            weightedSumX += (directionX / distance) * weight;
            weightedSumY += (directionY / distance) * weight;
        }

        // 4. Calculate and apply avoidance for humans
        for (Character human : nearestHumans) {
            double distance = this.distanceToCollision(human);
            if (distance == 0) continue; // Avoid division by zero
            double directionX = human.getX() - this.getX();
            double directionY = human.getY() - this.getY();
            double weight = baseHumanWeight * Math.exp(-distance / humanImportanceDecayAlpha);
            weightedSumX += (directionX / distance) * weight;
            weightedSumY += (directionY / distance) * weight;
        }

        // 5. Calculate and apply wall avoidance
        double wallDistance = this.getCoordinates().distanceTo(nearestPointToWall);
        if (wallDistance == 0) return 0; // Avoid division by zero
        double directionX = nearestPointToWall.getX() - this.getX();
        double directionY = nearestPointToWall.getY() - this.getY();
        double weight = baseWallWeight * Math.exp(-wallDistance / wallImportanceDecayAlpha);
        weightedSumX += (directionX / wallDistance) * weight;
        weightedSumY += (directionY / wallDistance) * weight;

        // Compute the angle of escape to avoid collisions
        double escapeAngle = Math.atan2(-weightedSumY, -weightedSumX);
        escapeAngle %= 2 * Math.PI; // Ensure angle is in [0, 2π]
        if (escapeAngle < 0) {
            escapeAngle += 2 * Math.PI; // Ensure angle is in [0, 2π]
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
