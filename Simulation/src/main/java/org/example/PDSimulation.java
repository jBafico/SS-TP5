package org.example;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class PDSimulation { //Pedestrian Dynamics Simulation represents the model of the game
    private List<Character> characterList;  //This has all the characters in the arena
    private Wall wall;                      //This is the wall of the arena
    private double r;                       //This represents the non-spawnable radius

    public PDSimulation(int Nh, int Nz, double Ra, double r) {
        wall= new Wall(Ra);
        characterList = generateRandomCharacters(Nh, Nz, Ra, 1, r); //TODO check the vaue of the character inner radius
    }

    private List<Character> generateRandomCharacters(int nh, int nz, double wallRadius, double characterRadius, double nonSpawnR) {
        List<Character> generatedCharacters = new ArrayList<>();
        int nTotal=nh + nz;

        // Generate nh Humans and nz Zombies
        while (generatedCharacters.size() < nTotal) {
            // Generate new characters with random coordinates
            Coordinates coordinates = Coordinates.generateRandomCoordinatesInCircle(wallRadius-r, characterRadius);
            Character newCharacter;
            if(generatedCharacters.size()< nz){
                newCharacter = new Zombie(generatedCharacters.size(), coordinates.getX(), coordinates.getY(), 0, 0, characterRadius, nonSpawnR);
            }else{
                newCharacter = new Human(generatedCharacters.size(), coordinates.getX(), coordinates.getY(), 0, 0, characterRadius);
            }

            // Check if new character collides with any other particle in the list
            boolean collides = false;
            for (Character c : generatedCharacters) {
                if (newCharacter.isCollidingWithCharacter(c,
                        (c instanceof Zombie && newCharacter instanceof Human) ? ((Zombie) c).getNonSpawnR() : 0)) { //If the new character is a Human and c is a Zombie, the zombie has a nonSpawnRadius
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
