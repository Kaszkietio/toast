package org.asaa.agents;

import jade.core.Agent;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.domain.FIPAException;
import org.asaa.behaviors.ListenToCrossroads;
import org.asaa.exceptions.InvalidServiceSpecification;


public class SimulationAgent extends Agent {

    // TODO: add communication with server

    @Override
    protected void setup() {
        final Object[] args = getArguments();

        registerSimulation();
        addBehaviour(new ListenToCrossroads(this));
    }

    @Override
    protected void takeDown() {
        try {
            DFService.deregister(this);
        } catch (final FIPAException e) {
            throw new InvalidServiceSpecification(e);
        }
    }

    private void registerSimulation() {
        final ServiceDescription serviceDescription = new ServiceDescription();
        serviceDescription.setName("simulation");
        serviceDescription.setType("simulation");
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
