package org.asaa.agents;

import jade.core.AID;
import jade.core.Agent;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.domain.FIPAException;
import lombok.Getter;
import org.asaa.behaviors.ChangeLights;
import org.asaa.behaviors.HandleNeighbors;
import org.asaa.domain.LightCycle;
import org.asaa.exceptions.InvalidServiceSpecification;

import java.util.*;

public class CrossroadAgent extends Agent {

    @Getter
    private final List<String> neighbors = new Vector<>();

    @Getter
    private final Map<String, AID> activeNeighbors = new HashMap<>();

    @Getter
    private LightCycle lightCycle;

    @Override
    protected void setup() {
        final Object[] args = getArguments();
        for (String neighbor : (List<String>)args[0]) {
            System.out.printf("[%s] Adding neighbor: %s\n", this.getLocalName(), neighbor);
        }
        this.neighbors.addAll((List<String>)args[0]);
        this.lightCycle = (LightCycle)args[1];

        registerCrossroad();
        addBehaviour(new HandleNeighbors(this));
        addBehaviour(new ChangeLights(this, this.lightCycle.getLightsLength()));
    }

    @Override
    protected void takeDown() {
        try {
            DFService.deregister(this);
        } catch (final FIPAException e) {
            throw new InvalidServiceSpecification(e);
        }
    }

    private void registerCrossroad() {
        final ServiceDescription serviceDescription = new ServiceDescription();
        serviceDescription.setType("crossroad");
        serviceDescription.setName(this.getLocalName());
        serviceDescription.setOwnership(this.getLocalName());

        try {
            final DFAgentDescription agentServices = new DFAgentDescription();
            agentServices.addServices(serviceDescription);
            DFService.register(this, agentServices);
        } catch (final FIPAException e) {
            throw new InvalidServiceSpecification(e);
        }
    }
}
