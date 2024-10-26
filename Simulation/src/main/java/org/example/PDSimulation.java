package org.example;

import java.util.ArrayList;
import java.util.List;

public class PDSimulation { //Pedestrian Dynamics Simulation represents the model of the game

    public SimulationResults run(SimulationParams params){
        List<Character> initialCharacterList = generateRandomCharacters(params.nh(), params.ra(), params.characterRadius(), params.r()); //TODO check the value of the character inner radius
        
        return new SimulationResults(params, null);
    }

    private void transformHuman(List<Character> characterList, Character c){ //This method transforms a Human to a Zombie
        characterList.remove(c);
        characterList.add(new Zombie(c.getId(), c.getX(), c.getY(), c.getR()));
    }

    private List<Character> generateRandomCharacters(int nh, double wallRadius, double characterRadius, double nonSpawnR) {
        List<Character> generatedCharacters = new ArrayList<>();
        Character newCharacter = new Zombie(0, 0, 0, characterRadius);
        generatedCharacters.add(newCharacter);

        // Generate nh Humans and nz Zombies
        while (generatedCharacters.size() <= nh) {
            // Generate new characters with random coordinates
            Coordinates coordinates = Coordinates.generateRandomCoordinatesInCircle(wallRadius-nonSpawnR, characterRadius);
            newCharacter = new Human(generatedCharacters.size(), coordinates.getX(), coordinates.getY(), characterRadius);

            // Check if new character collides with any other particle in the list
            boolean collides = false;
            for (Character c : generatedCharacters) {
                if (newCharacter.isCollidingWithCharacter(c,
                        (c instanceof Zombie) ? nonSpawnR : 0)) { // If the new character is a Human and c is a Zombie, the zombie has a nonSpawnRadius
                    collides = true;
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
