package org.example;

import java.util.ArrayList;
import java.util.List;

public class PDSimulation { //Pedestrian Dynamics Simulation represents the model of the game

    public SimulationResults run(SimulationParams params){
        List<Character> initialCharacterList = generateRandomCharacters(params.nh(), params.nz(), params.ra(), params.characterRadius(), params.r()); //TODO check the value of the character inner radius
        
        return new SimulationResults(params, null);
    }

    private void transformHuman(List<Character> characterList, Character c){ //This method transforms a Human to a Zombie
        characterList.remove(c);
        characterList.add(new Zombie(c.getId(), c.getX(), c.getY(), c.getR()));
    }

    private List<Character> generateRandomCharacters(int nh, int nz, double wallRadius, double characterRadius, double nonSpawnR) {
        List<Character> generatedCharacters = new ArrayList<>();
        int nTotal = nh + nz;

        // Generate nh Humans and nz Zombies
        while (generatedCharacters.size() < nTotal) {
            // Generate new characters with random coordinates
            Coordinates coordinates = Coordinates.generateRandomCoordinatesInCircle(wallRadius-nonSpawnR, characterRadius);
            Character newCharacter;
            if (generatedCharacters.size() < nz){
                newCharacter = new Zombie(generatedCharacters.size(), coordinates.getX(), coordinates.getY(), characterRadius);
            } else {
                newCharacter = new Human(generatedCharacters.size(), coordinates.getX(), coordinates.getY(), characterRadius);
            }

            // Check if new character collides with any other particle in the list
            boolean collides = false;
            for (Character c : generatedCharacters) {
                if (newCharacter.isCollidingWithCharacter(c,
                        (c instanceof Zombie && newCharacter instanceof Human) ? nonSpawnR : 0)) { // If the new character is a Human and c is a Zombie, the zombie has a nonSpawnRadius
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
