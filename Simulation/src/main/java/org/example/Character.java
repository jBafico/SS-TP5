package org.example;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
public abstract class Character { //This class is the abstract class of the Entities of the model
    private int id;
    private double x;
    private double y;
    private double vx;
    private double vy;
    private double r;

    public abstract void findTarget(); //This is the method that will set the heuristic of the entity, it will change its velocity


    public boolean isCollidingWithCharacter(Character c, double nonSpawnR){
        final double deltaX = x - c.getX();
        final double deltaY = y - c.getY();
        final double sigma = r + c.getR() + nonSpawnR;
        final double deltaPosition= Math.sqrt(Math.pow(deltaX, 2) + Math.pow(deltaY, 2));

        return (deltaPosition-sigma<0);
    }
}
