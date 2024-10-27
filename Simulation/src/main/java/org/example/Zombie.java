package org.example;

import lombok.Getter;

import java.util.List;

@Getter
public class Zombie extends Character{
    public Zombie(Coordinates coordinates, Constants constants, CharacterConfig config, double contagionTime) {
        super(coordinates, constants, config, contagionTime);
    }

    @Override
    protected double getNextTheta(List<Character> characterList) {
        return 0; // todo
    }

}
