package org.example;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;


public class PDSimulation { // Pedestrian Dynamics Simulation represents the model of the game
    private final double CHARACTER_GENERATION_MAX_TRIES = 100;

    private final SimulationParams params;
    private final CharacterConfig zombieConfig;
    private final CharacterConfig humanConfig;
    private long iterationNo = 0;
    private boolean minShootProportionReached = false;
    private String simulationStatusMsg = "DRAW";

    public PDSimulation(SimulationParams params){
        this.params = params;
        this.zombieConfig = new CharacterConfig(params.vzMax(), params.rMin(), params.rMax(), params.dt(), params.nearestHumansToConsider(), params.nearestZombiesToConsider(), params.nearestHumansImportance(), params.nearestZombiesImportance(), params.wallImportance(), params.humanImportanceDecayAlpha(), params.zombieImportanceDecayAlpha(), params.wallImportanceDecayAlpha());
        this.humanConfig = new CharacterConfig(params.vhMax(), params.rMin(), params.rMax(), params.dt(), params.nearestHumansToConsider(), params.nearestZombiesToConsider(), params.nearestHumansImportance(), params.nearestZombiesImportance(), params.wallImportance(), params.humanImportanceDecayAlpha(), params.zombieImportanceDecayAlpha(), params.wallImportanceDecayAlpha());
    }

    public SimulationResults run(){
        List<List<Character>> resultsList = new ArrayList<>();

        // Create the wall
        Wall wall = new Wall(params.arenaRadius());

        // We create initial character list and add it
        List<Character> characterList = generateRandomCharacters(wall);
        resultsList.add(characterList);

        // Iterate until we reach maxTime or all characters are now zombies
        for (double dt = 0; dt < params.maxTime(); dt+=params.dt()) {
            iterationNo++;
            List<Character> currentState = resultsList.getLast();

            // Create the newState
            List<Character> newState = new ArrayList<>();
            currentState.forEach(character -> newState.add(character.getNext(currentState, wall)));


            // Temporary set to store the characters participating in contagion process
            Set<Character> contagionCharacters = new HashSet<>();

            for (Character character : newState){
                // If the character is not a human, he can't shoot
                if (!(character instanceof Human)) {
                    continue;
                }
                
                Human human = (Human) character;

                // If the human is already in the contagion process, he can't shoot
                if (human.isInContagion()) {
                    continue;
                }

                Zombie collidingZombie = human.collidingZombie(newState);

                // If the human is not colliding with any zombies, continue to the next human
                if (collidingZombie == null) {
                    continue;
                }

                // If the human was already in the contagion process, continue to the next human
                if (human.getRemainingContagion() > 0) {
                    continue;
                }

                // If the human didn't start the contagion process, start it
                if(!human.isInContagion()){
                    human.startContagion(params.contagionTime());
                    collidingZombie.startContagion(params.contagionTime());
                    continue;
                }

                if(human.getRemainingContagion()<0){
                    human.stopContagion();
                }

                contagionCharacters.add(human);
                contagionCharacters.add(collidingZombie);
            }

            transformHumans(newState, contagionCharacters);

            // Check if we have met the minimum shoot proportion yet
            if (!minShootProportionReached) {
                int zombieAmount = (int) newState.stream().filter(c -> c instanceof Zombie).count();
                int humanAmount = (int) newState.stream().filter(c -> c instanceof Human).count();
                minShootProportionReached = zombieAmount >= Math.ceil(params.minShootProportion() * humanAmount);
            }
            // Do the shoot logic if we are on the right time, and we have the sufficient amount of zombies
            else if (iterationNo % params.shootInterval() == 0) {
                List<Character> shotCharacters = new ArrayList<>();
                for (Character character : newState) {
                    if (character instanceof Zombie){
                        continue;
                    }

                    // Given we are a human, find the nearest zombie
                    Human human = (Human) character;
                    Zombie nearestZombie = (Zombie) human.findNNearestZombies(newState, 1).getFirst();

                    // If the zombie is in the shooting range, shoot it with the given probability
                    if (human.distanceToCollision(nearestZombie) <= params.maxShootRange()) {
                        if (Math.random() < params.shootProbability()) {
                            shotCharacters.add(nearestZombie);
                        }
                    }
                }

                // Remove the shot zombies from the newState
                newState.removeAll(shotCharacters);
            }


            // Add the updated state to the results list
            resultsList.add(newState);

            // If every character is a zombie, end the simulation
            if (newState.stream().allMatch(c -> c instanceof Zombie)) {
                simulationStatusMsg = "ZOMBIES WON";
                break;
            }

            // If every character is a human, end the simulation
            if (newState.stream().allMatch(c -> c instanceof Human)) {
                simulationStatusMsg = "HUMANS WON";
                break;
            }
        }

        double meanSpeed = resultsList.stream()
                .mapToDouble(characters -> characters.stream()
                        .mapToDouble(Character::getV)
                        .average()
                        .orElse(0))
                .average()
                .orElse(0);

        System.out.println("Simulation finish status: " + simulationStatusMsg);
        return new SimulationResults(params, resultsList, meanSpeed);
    }

    private void transformHumans(List<Character> characterList, Set<Character> contagionCharacters){
        // This method transforms a Human to a Zombie
        for (Character c : contagionCharacters) {
                characterList.remove(c);
                characterList.add(new Zombie(c.getCoordinates(), params.constants(), zombieConfig, 0, false));
        }
    }

    private List<Character> generateRandomCharacters(Wall wall) {
        List<Character> generatedCharacters = new ArrayList<>();
        Character newCharacter = new Zombie(new Coordinates(0, 0), params.constants(), zombieConfig, 0, false);
        generatedCharacters.add(newCharacter);

        // Generate nh Humans
        double tries = 0;
        while (generatedCharacters.size() <= params.nh()) {
            // Generate new characters with random coordinates
            Coordinates coordinates = wall.generateRandomCoordinatesInWall(params.nonSpawnR());
            newCharacter = new Human(coordinates, params.constants(), humanConfig, false);

            // Check if new character collides with any other particle in the list
            boolean collides = false;
            for (Character c : generatedCharacters) {
                // For any two characters, their rMin cannot overlap
                if (c.isOverlappingWithCharacter(newCharacter)) {
                    collides = true;
                }

                if (collides) {
                    tries++;
                    break;
                }
            }

            // If the new character does not collide with any other character, add it to the list and reset the tries
            if (!collides) {
                generatedCharacters.add(newCharacter);
                tries = 0;
            } else if (tries > CHARACTER_GENERATION_MAX_TRIES) {
                System.out.println("---------------------------------------------------------------------------");
                System.out.println("Reached max tries when generating random characters:");
                System.out.println("Generated " + generatedCharacters.size() + "/" + params.nh() + " characters");
                System.out.println("---------------------------------------------------------------------------");
                break;
            }
        }
        return generatedCharacters;
    }
}
