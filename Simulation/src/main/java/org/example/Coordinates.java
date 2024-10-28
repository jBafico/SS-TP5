package org.example;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class Coordinates {
    private double x;
    private double y;

    public double distanceTo(Coordinates coordinates) {
        double deltaX = this.x - coordinates.x;
        double deltaY = this.y - coordinates.y;
        return Math.sqrt(Math.pow(deltaX, 2) + Math.pow(deltaY, 2));
    }
}
