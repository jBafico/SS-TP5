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

    public PDSimulation(SimulationParams params){
        this.params = params;
        this.zombieConfig = new CharacterConfig(params.vzMax(), params.rMin(), params.rMax(), params.dt(), params.nearestHumansToConsider(), params.nearestZombiesToConsider(), params.nearestHumansImportance(), params.nearestZombiesImportance(), params.wallImportance(), params.maxLengthFactor(), params.zombieImportanceDecayAlpha(), params.zombieImportanceDecayAlpha(), params.wallImportanceDecayAlpha());
        this.humanConfig = new CharacterConfig(params.vhMax(), params.rMin(), params.rMax(), params.dt(), params.nearestHumansToConsider(), params.nearestZombiesToConsider(), params.nearestHumansImportance(), params.nearestZombiesImportance(), params.wallImportance(), params.maxLengthFactor(), params.humanImportanceDecayAlpha(), params.humanImportanceDecayAlpha(), params.wallImportanceDecayAlpha());
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
            List<Character> currentState = resultsList.getLast();

            // Create the newState
            List<Character> newState = new ArrayList<>();
            currentState.forEach(character -> newState.add(character.getNext(currentState, wall)));


            // Temporary set to store the characters participating in contagion process
            Set<Character> contagionCharacters = new HashSet<>();

            for(Character character : newState){
                if (!(character instanceof Human)) {
                    continue;
                }
                Human human = (Human) character;
                Zombie collidingZombie = human.collidingZombie(newState);

                // If the human is not colliding with any zombies, continue to the next human
                if (collidingZombie == null) {
                    continue;
                }

                // If the human was already in the contagion process, continue to the next human
                if (human.getRemainingContagion() > 0) {
                    continue;
                }

                contagionCharacters.add(human);
                contagionCharacters.add(collidingZombie);
            }

            transformHumans(newState, contagionCharacters);

            // Add the updated state to the results list
            resultsList.add(newState);

            // If every character is a zombie, end the simulation
            if (newState.stream().allMatch(c -> c instanceof Zombie)) {
                System.out.println("Finishing the simulation because all characters are now zombies");
                break;
            }
        }
        
        return new SimulationResults(params, resultsList);
    }

    private void transformHumans(List<Character> characterList, Set<Character> contagionCharacters){
        // This method transforms a Human to a Zombie
        for (Character c : contagionCharacters) {
            characterList.remove(c);
            characterList.add(new Zombie(c.getCoordinates(), params.constants(), zombieConfig, params.contagionTime()));
        }
    }

    private List<Character> generateRandomCharacters(Wall wall) {
        List<Character> generatedCharacters = new ArrayList<>();
        Character newCharacter = new Zombie(new Coordinates(0, 0), params.constants(), zombieConfig, 0);
        generatedCharacters.add(newCharacter);

        // Generate nh Humans
        double tries = 0;
        while (generatedCharacters.size() <= params.nh()) {
            // Generate new characters with random coordinates
            Coordinates coordinates = wall.generateRandomCoordinatesInWall(params.nonSpawnR());
            newCharacter = new Human(coordinates, params.constants(), humanConfig);

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
        System.out.println("Finished generation");
        return generatedCharacters;
    }
}
