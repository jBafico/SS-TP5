package org.example;

import java.util.List;

public class Human extends Character {
    public Human(Coordinates coordinates, Constants constants, CharacterConfig config) {
        super(coordinates, constants, config);
    }

    @Override
    protected double getNextTheta(List<Character> characterList) {
        return 0; // todo
    }
}
