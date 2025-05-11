package org.asaa.behaviors;

import jade.core.behaviours.WakerBehaviour;
import jade.lang.acl.ACLMessage;
import org.asaa.agents.CrossroadAgent;
import java.util.List;

public class ChangeLights extends WakerBehaviour {

    private final CrossroadAgent agent;

    public ChangeLights(CrossroadAgent agent, long timeout) {
        super(agent, timeout);
        this.agent = agent;
    }

    @Override
    public void onWake() {
        List<String> oldNeighbors = agent.getLightCycle().GetCurrentNeighbors();
        for(String neighbor : oldNeighbors) {
            ACLMessage msg = new ACLMessage(ACLMessage.INFORM);
            if (agent.getActiveNeighbors().containsKey(neighbor)) {
                msg.addReceiver(agent.getActiveNeighbors().get(neighbor));
                msg.setContent("RED");
                agent.send(msg);
            }
        }

        agent.getLightCycle().AdvanceCycle();

        List<String> currentNeighbors = agent.getLightCycle().GetCurrentNeighbors();
        for(String neighbor : currentNeighbors) {
            ACLMessage msg = new ACLMessage(ACLMessage.INFORM);
            if (agent.getActiveNeighbors().containsKey(neighbor)) {
                msg.addReceiver(agent.getActiveNeighbors().get(neighbor));
                msg.setContent("GREEN");
                agent.send(msg);
            }
        }

        agent.addBehaviour(new ChangeLights(agent, agent.getLightCycle().getLightsLength()));
    }
}
