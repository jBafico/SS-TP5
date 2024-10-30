package org.example;

import lombok.EqualsAndHashCode;
import lombok.Getter;

import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

@Getter
@EqualsAndHashCode
public abstract class Character { //This class is the abstract class of the Entities of the model
    private final Constants constants;
    private final Coordinates coordinates; // Current X and Y positions
    private final CharacterConfig config;
    private final double v; // Current velocity module
    private final double theta; // Current velocity direction in radians
    private final double r; // Current radius
    private final double remainingContagion; // The amount of time the character has to wait to move again
    private final String type; // Type of character

    // Without contagion time
    public Character(Coordinates coordinates, Constants constants, CharacterConfig config, String type){
        this.coordinates = coordinates;
        this.constants = constants;
        this.config = config;
        this.r = config.rMin(); // Characters initialize with rMin
        this.v = 0;
        this.theta = 0;
        this.remainingContagion = 0;
        this.type = type;
    }

    // With contagion time
    public Character(Coordinates coordinates, Constants constants, CharacterConfig config, double remainingContagion, String type){
        this.coordinates = coordinates;
        this.constants = constants;
        this.config = config;
        this.r = config.rMin(); // Characters initialize with rMin
        this.v = 0;
        this.theta = 0;
        this.remainingContagion = remainingContagion;
        this.type = type;
    }

    protected Character(Coordinates coordinates, Constants constants, CharacterConfig config, double v, double theta, double r, String type){
        this.coordinates = coordinates;
        this.constants = constants;
        this.config = config;
        this.r = r;
        this.v = v;
        this.theta = theta;
        this.remainingContagion = 0;
        this.type = type;
    }

    public double getX(){
        return coordinates.getX();
    }

    public double getY(){
        return coordinates.getY();
    }

    protected double getVx() {
        // Calculate the x-component of velocity
        return v * Math.cos(theta);
    }

    protected double getVy() {
        // Calculate the y-component of velocity
        return v * Math.sin(theta);
    }


    public double distanceToCollision(Character c) {
        return this.coordinates.distanceTo(c.getCoordinates());
    }

    // When the two r overlap
    protected boolean isCollidingWithCharacter(Character c) {
        double distanceToCollision = distanceToCollision(c);
        return distanceToCollision <= r + c.r;
    }

    public boolean isCollidingWithSomeone(List<Character> characterList) {
        return characterList
                .stream()
                .anyMatch(otherCharacter -> !otherCharacter.equals(this) && this.isCollidingWithCharacter(otherCharacter));
    }

    // When the two rMin overlap (this cannot happen ever)
    public boolean isOverlappingWithCharacter(Character c) {
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

    // Calculate the desired angle of movement in radians
    protected abstract double getNextDesiredTheta(List<Character> characterList, Wall wall);

    // The real next theta is the desired theta plus some noise
    private double getNextTheta(List<Character> characterList, Wall wall){
        // noise is random value between [-1, 1]
        double noise = Math.random() * 2 - 1;

        // thetaNoise is random value between [-mu/2, mu/2]
        double thetaNoise = noise * constants.mu() / 2;

        return getNextDesiredTheta(characterList, wall) + thetaNoise;
    }

    private Coordinates getNextCoordinates(double dt){
        double nextX = getX() + getVx() * dt;
        double nextY = getY() + getVy() * dt;
        return new Coordinates(nextX, nextY);
    }

    protected abstract Character createNextInstance(Coordinates coordinates, double v, double theta, double r);

    public Character getNext(double dt, List<Character> characterList, Wall wall) {
        Coordinates nextCoordinates = getNextCoordinates(dt); // Calculate the next position according to current speed and direction
        double nextTheta = getNextTheta(characterList, wall); // Calculate next direction

        boolean isColliding = isCollidingWithSomeone(characterList);
        double nextV = getNextV(isColliding); // Calculate next speed
        double nextR = getNextR(isColliding, dt); // Calculate next r

        return createNextInstance(nextCoordinates, nextV, nextTheta, nextR);
    }


    protected List<Character> findNNearestZombies(List<Character> characterList, int n, double maxFactor) {
        return findNNearestCharactersHelper(characterList, n, "human", maxFactor);
    }

    protected List<Character> findNNearestHumans(List<Character> characterList, int n, double maxFactor) {
        return findNNearestCharactersHelper(characterList, n, "zombie", maxFactor);
    }


    // Helper function
    private List<Character> findNNearestCharactersHelper(List<Character> characterList, int n, String typeToAvoid, double maxFactor) {
        List<Character> filteredCharacters = characterList.stream()
            // Filter out characters of the type specified in `typeToAvoid` and exclude the calling character `this`
            .filter(character -> {
                if (typeToAvoid.equals("human")) {
                    return !(character instanceof Human) && character != this;
                } else if (typeToAvoid.equals("zombie")) {
                    return !(character instanceof Zombie) && character != this;
                }
                return character != this; // Default case if typeToAvoid is not specified correctly
            })
            // Sort by distance to the calling character
            .sorted(Comparator.comparingDouble(this::distanceToCollision))
            .toList();

        if (characterList.isEmpty()){
            throw new Error("Unexpected error");
        }

        // Get the distance to the nearest character if any are found
        double nearestDistance = this.distanceToCollision(filteredCharacters.getFirst());

        // Now filter again based on maxFactor condition
        // This is to ignore the characters that appear in the list but are far from the calling character when compared to the nearest one
        return filteredCharacters.stream()
            .filter(character -> this.distanceToCollision(character) <= maxFactor * nearestDistance)
            .limit(n) // Limit to the `n` closest characters after filtering
            .collect(Collectors.toList());
    }

}
