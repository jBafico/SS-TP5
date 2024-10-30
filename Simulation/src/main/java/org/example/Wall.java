package org.example;

import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
@Getter
public class Wall {
    private double radius;

    public Coordinates nearestPointToWall(Coordinates c) {
        double xCoordinates = c.getX();
        double yCoordinates = c.getY();

        // Calculate the distance from the center of the wall to the character
        double distanceToCenter = c.distanceTo(new Coordinates(0, 0));

        // Calculate scaling factor to project the point onto the wall’s circumference
        double scale = radius / distanceToCenter;

        // Calculate the nearest point coordinates on the wall’s circumference
        double nearestX = xCoordinates * scale;
        double nearestY = yCoordinates * scale;

        return new Coordinates(nearestX, nearestY);
    }

    public Coordinates generateRandomCoordinatesInWall(double nonSpawnR) {
        // generate random distance in the range [nonSpawnR, circleRadius-nonSpawnR)
        double distanceFromCenter = nonSpawnR + Math.random() * (radius - 2 * nonSpawnR);
        // generate random angle in radians (from 0 to 2pi)
        double angle = Math.random() * 2 * Math.PI;

        // decompose the distance into x and y coordinates
        double x = distanceFromCenter * Math.cos(angle);
        double y = distanceFromCenter * Math.sin(angle);
        return new Coordinates(x, y);
    }

}
