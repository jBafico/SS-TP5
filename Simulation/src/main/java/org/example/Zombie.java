package org.example;

import lombok.Getter;

import java.util.List;

@Getter
public class Zombie extends Character{
    public Zombie(Coordinates coordinates, Constants constants, CharacterConfig config, double contagionTime) {
        super(coordinates, constants, config, contagionTime);
    }

    private Zombie(Coordinates coordinates, Constants constants, CharacterConfig config, double v, double theta, double r){
        super(coordinates, constants, config, v, theta, r);
    }

    @Override
    protected Character createNextInstance(Coordinates coordinates, double v, double theta, double r) {
        return new Zombie(coordinates, this.getConstants(), this.getConfig(), v, theta, r);
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
