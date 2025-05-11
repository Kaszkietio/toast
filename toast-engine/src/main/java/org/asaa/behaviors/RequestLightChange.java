package org.asaa.behaviors;

import jade.core.AID;
import jade.lang.acl.ACLMessage;
import jade.proto.AchieveREInitiator;
import org.asaa.agents.CrossroadAgent;

public class RequestLightChange extends AchieveREInitiator {

    private final CrossroadAgent agent;

    public RequestLightChange(CrossroadAgent a, AID simulation) {
        super(a, getMessage(a, simulation));
        agent = a;
    }

    private static ACLMessage getMessage(CrossroadAgent a, AID simulation) {
        return null;
    }
}
