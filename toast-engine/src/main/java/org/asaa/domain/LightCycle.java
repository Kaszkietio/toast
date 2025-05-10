package org.asaa.domain;

import java.util.ArrayList;
import java.util.List;

public class LightCycle {
    private final List<List<String>> correspondingNeighbors = new ArrayList<>();
    private final List<Integer> lightsLength = new ArrayList<>();
    private int currentIndex = 0;

    public LightCycle(List<List<String>> correspondingNeighbors, List<Integer> lightsLength) {
        this.correspondingNeighbors.addAll(correspondingNeighbors);
        this.lightsLength.addAll(lightsLength);
    }

    public List<String> GetCurrentNeighbors() {
        return correspondingNeighbors.get(currentIndex);
    }

    public Integer getLightsLength() {
        return lightsLength.get(currentIndex);
    }

    public void AdvanceCycle() {
        currentIndex++;
        if (currentIndex == lightsLength.size()) {
            currentIndex = 0;
        }
    }
}
