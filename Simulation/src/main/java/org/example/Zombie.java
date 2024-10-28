package org.example;

import lombok.Getter;

import java.util.List;

@Getter
public class Zombie extends Character{
    public Zombie(Coordinates coordinates, Constants constants, CharacterConfig config, double contagionTime) {
        super(coordinates, constants, config, contagionTime);
    }

    @Override
    protected double getNextTheta(List<Character> characterList, Wall wall) {
        /* The zombie just considers the nearest human and doesn't avoid obstacles */

        // Find the nearest human
        Character nearestHuman = this.findNNearestHumans(characterList, 1, Double.MAX_VALUE).getFirst();

        // Calculate the difference in x and y coordinates
        double deltaX = nearestHuman.getX() - this.getX();
        double deltaY = nearestHuman.getY() - this.getY();

        // Calculate the angle theta in radians, using atan2 for correct quadrant
        return Math.atan2(deltaY, deltaX);
    }

}
