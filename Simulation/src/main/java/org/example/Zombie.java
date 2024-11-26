package org.example;

import lombok.Getter;

import java.util.List;

@Getter
public class Zombie extends Character{
    public Zombie(Coordinates coordinates, Constants constants, CharacterConfig config, double contagionTime) {
        super(coordinates, constants, config, contagionTime, "zombie");
    }

    private Zombie(Coordinates coordinates, Constants constants, CharacterConfig config, double v, double theta, double r, double remainingContagion) {
        super(coordinates, constants, config, v, theta, r, "zombie", remainingContagion);
    }

    @Override
    protected Character createNextInstance(Coordinates coordinates, double v, double theta, double r, double remainingContagion) {
        return new Zombie(coordinates, this.getConstants(), this.getConfig(), v, theta, r, remainingContagion);
    }

    private Zombie isCollidingWithZombie(List<Character> characterList) {
        for (Character character : characterList) {
            if (character != this && character instanceof Zombie && this.distanceToCollision(character) < getConfig().rMin() + character.getConfig().rMin()) {
                return (Zombie) character;
            }
        }
        return null;
    }


    @Override
    protected double getNextDesiredTheta(List<Character> characterList, Wall wall) {
        /* The zombie just considers the nearest human and doesn't avoid obstacles */
        // Check if colliding with other zombie
        Zombie collidingZombie = this.isCollidingWithZombie(characterList);
        if (collidingZombie != null) {
            // Calculate the angle between the two zombies and try to escape from the collision
            double deltaX = collidingZombie.getX() - this.getX();
            double deltaY = collidingZombie.getY() - this.getY();
            return Math.atan2(deltaY, deltaX) + Math.PI;
        }

        // Find the nearest human and follow him
        Character nearestHuman = this.findNNearestHumans(characterList, 1).getFirst();

        // Calculate the difference in x and y coordinates
        double deltaX = nearestHuman.getX() - this.getX();
        double deltaY = nearestHuman.getY() - this.getY();

        double theta = Math.atan2(deltaY, deltaX);

        // Adjust theta if it's in the wrong range
        if (theta < 0) {
            theta += 2 * Math.PI; // Convert to a positive angle in [0, 2π]
        }

        // Calculate the angle theta in radians, using atan2 for correct quadrant
        return theta;
    }

}
