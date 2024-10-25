package org.example;

import lombok.Getter;

@Getter
public class Zombie extends Character{
    public Zombie(int id, double x, double y, double r) {
        super(id, x, y, r);
    }

    @Override
    public void findTarget() { //Here goes the heuristic logic

    }
}
