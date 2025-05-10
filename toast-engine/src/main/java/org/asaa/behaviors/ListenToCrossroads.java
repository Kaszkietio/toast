package org.asaa.behaviors;

import jade.core.behaviours.CyclicBehaviour;
import jade.lang.acl.ACLMessage;
import org.asaa.agents.SimulationAgent;

import static java.util.Objects.nonNull;

public class ListenToCrossroads extends CyclicBehaviour {

    private final SimulationAgent agent;

    public ListenToCrossroads(SimulationAgent agent) {
        super(agent);
        this.agent = agent;
    }

    @Override
    public void action() {
        final ACLMessage msg = agent.receive();

        if (nonNull(msg)) {
            if (msg.getPerformative() == ACLMessage.REQUEST) {
                handleRequest(msg);
            } else {
                System.out.printf("[%s] Received not expected message: %s\n", agent.getLocalName(), msg.getContent());
            }
        } else {
            block();
        }
    }

    private void handleRequest(ACLMessage msg) {
        System.out.printf("[%s] Received REQUEST from crossroad [%s]: %s\n", agent.getLocalName(),
                msg.getSender().getLocalName(), msg.getContent());

        // TODO: Send message to simulation server

        ACLMessage reply = msg.createReply();
        reply.setPerformative(ACLMessage.REFUSE);
        System.out.printf("[%s] Sending REFUSE reply to %sn", agent.getLocalName(), msg.getSender().getLocalName());
        agent.send(reply);
    }
}
