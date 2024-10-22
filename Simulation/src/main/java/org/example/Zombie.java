package org.example;

import lombok.Getter;

@Getter
public class Zombie extends Character{

    private double nonSpawnR;
    public Zombie(int id, double x, double y, double vx, double vy, double r, double nonSpawnR) {
        super(id, x, y, vx, vy, r);
    }

    @Override
    public void findTarget() { //Here goes the heuristic logic

    }
}
