package org.example;

import java.util.ArrayList;
import java.util.List;

public class PDSimulation { //Pedestrian Dynamics Simulation represents the model of the game
    private final SimulationParams params;
    private final CharacterConfig zombieConfig;
    private final CharacterConfig humanConfig;

    public PDSimulation(SimulationParams params){
        this.params = params;
        this.zombieConfig = new CharacterConfig(params.vzMax(), params.rMin(), params.rMax());
        this.humanConfig = new CharacterConfig(params.vhMax(), params.rMin(), params.rMax());
    }

    public SimulationResults run(){
        // Set Character
        List<Character> initialCharacterList = generateRandomCharacters();
        
        return new SimulationResults(params, null);
    }

    private void transformHuman(List<Character> characterList, Character c){
        // This method transforms a Human to a Zombie
        characterList.remove(c);
        characterList.add(new Zombie(c.getCoordinates(), params.constants(), zombieConfig, params.contagionTime()));
    }

    private List<Character> generateRandomCharacters() {
        List<Character> generatedCharacters = new ArrayList<>();
        Character newCharacter = new Zombie(new Coordinates(0, 0), params.constants(), zombieConfig, 0);
        generatedCharacters.add(newCharacter);

        // Generate nh Humans
        while (generatedCharacters.size() <= params.nh()) {
            // Generate new characters with random coordinates
            Coordinates coordinates = Coordinates.generateRandomCoordinatesInCircle(params.arenaRadius()-params.nonSpawnR());
            newCharacter = new Human(coordinates, params.constants(), humanConfig);

            // Check if new character collides with any other particle in the list
            boolean collides = false;
            for (Character c : generatedCharacters) {
                // For any two characters, their rMin cannot overlap
                if (c.isOverlapping(newCharacter)) {
                    collides = true;
                }

                // If it is a zombie, the distance has to be >= nonSpawnR
                if (!collides && c instanceof Zombie) {
                    double distanceToCollision = c.distanceToCollision(newCharacter);
                    collides = distanceToCollision <= params.nonSpawnR();
                }

                if (collides) {
                    break;
                }
            }
            // If the new character does not collide with any other character, add it to the list
            if (!collides) {
                generatedCharacters.add(newCharacter);
            }
        }
        System.out.println("Finished generation");
        return generatedCharacters;
    }
}
