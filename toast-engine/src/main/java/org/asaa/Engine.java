package org.asaa;

import static org.asaa.JADEEngine.runAgent;
import static org.asaa.JADEEngine.runGUI;
//import static org.labs.laboratory2.domain.Genre.COMEDY;
//import static org.labs.laboratory2.domain.Genre.CRIMINAL;
//import static org.labs.laboratory2.domain.Genre.HORROR;
//import static org.labs.laboratory2.domain.Genre.SCIFI;
//import static org.labs.laboratory2.domain.Region.EU;
//import static org.labs.laboratory2.domain.Region.US;

import java.lang.reflect.Array;
import java.util.List;
import java.util.Vector;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.asaa.domain.LightCycle;
import org.asaa.exceptions.JadePlatformInitializationException;

import jade.core.Profile;
import jade.core.ProfileImpl;
import jade.core.Runtime;
import jade.wrapper.ContainerController;

public class Engine {

    private static final ExecutorService jadeExecutor = Executors.newCachedThreadPool();

    public static void main(String[] args) {
        final Runtime runtime = Runtime.instance();
        final Profile profile = new ProfileImpl();

        try {
            final ContainerController container = jadeExecutor.submit(() -> runtime.createMainContainer(profile)).get();

            runGUI(container);
            runDFTask(container);
        } catch (final InterruptedException | ExecutionException e) {
            throw new JadePlatformInitializationException(e);
        }
    }

    private static void runDFTask(final ContainerController container) {
        runAgent(container, "Simulation", "SimulationAgent", new Object[] {});

        runAgent(container, "A1", "CrossroadAgent", new Object[] {
                List.of("A2", "A3"), new LightCycle(List.of(List.of("A2", "A3"), List.of()), List.of(4000, 1000))
        });
        runAgent(container, "A2", "CrossroadAgent", new Object[] {
                List.of("A1", "A4"), new LightCycle(List.of(List.of("A1", "A4"), List.of()), List.of(3000, 1000))
        });

        try {
            Thread.sleep(5000);
        } catch (final InterruptedException e) {
            throw new RuntimeException(e);
        }

        runAgent(container, "A3", "CrossroadAgent", new Object[] {
                List.of("A4", "A1"), new LightCycle(List.of(List.of("A2", "A4"), List.of()), List.of(5000, 1000))
        });
    }
}
