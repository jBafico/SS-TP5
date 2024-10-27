package org.example;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
public abstract class Character { //This class is the abstract class of the Entities of the model
    private Constants constants;
    private Coordinates coordinates; // Current X and Y positions
    private CharacterConfig config;
    private double v; // Current velocity module
    private double theta; // Current velocity direction [0, 360)
    private double r; // Current radius
    private double remainingContagion; // The amount of time the character has to wait to move again

    // Without contagion time
    public Character(Coordinates coordinates, Constants constants, CharacterConfig config){
        this.coordinates = coordinates;
        this.constants = constants;
        this.config = config;
        this.r = config.rMin(); // Characters initialize with rMin
        this.remainingContagion = 0;
    }

    // With contagion time
    public Character(Coordinates coordinates, Constants constants, CharacterConfig config, double remainingContagion){
        this.coordinates = coordinates;
        this.constants = constants;
        this.config = config;
        this.r = config.rMin(); // Characters initialize with rMin
        this.remainingContagion = remainingContagion;
    }

    public double getX(){
        return coordinates.getX();
    }

    public double getY(){
        return coordinates.getY();
    }

    protected double getVx() {
        // Convert theta to radians and calculate the x-component of velocity
        return v * Math.cos(Math.toRadians(theta));
    }

    protected double getVy() {
        // Convert theta to radians and calculate the y-component of velocity
        return v * Math.sin(Math.toRadians(theta));
    }


    public double distanceToCollision(Character c) {
        final double deltaX = getX() - c.getX();
        final double deltaY = getY() - c.getY();
        return Math.sqrt(Math.pow(deltaX, 2) + Math.pow(deltaY, 2));
    }

    // When the two rMax overlap
    public boolean isColliding(Character c) {
        double distanceToCollision = distanceToCollision(c);
        return distanceToCollision <= 2 * config.rMax();
    }

    // When the two rMin overlap (this cannot happen ever)
    public boolean isOverlapping(Character c) {
        double distanceToCollision = distanceToCollision(c);
        return distanceToCollision <= 2 * config.rMin();
    }

    private double getNextR(boolean isColliding, double dt){
        if (isColliding){
            return config.rMin();
        }

        return Math.min(config.rMax(), r + config.rMax() / (constants.tau() / dt));
    }

    private double getNextV(boolean isColliding){
        if (isColliding){ // Escape speed
            return config.vMax();
        }

        return config.vMax() * Math.pow(((r-config.rMin())/(config.rMax()-config.rMin())), constants.beta());
    }

    // Calculate the desired angle of movement in degrees [0, 360)
    protected abstract double getNextTheta(List<Character> characterList);

    private Coordinates getNextCoordinates(boolean isColliding, double dt, List<Character> characterList){
        double nextV = getNextV(isColliding);
        double nextTheta = getNextTheta(characterList);
        double nextX = getX() + nextV * Math.cos(nextTheta) * dt;
        double nextY = getY() + nextV * Math.sin(nextTheta) * dt;
        return new Coordinates(nextX, nextY);
    }

}
