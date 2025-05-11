package org.asaa.behaviors;

import jade.core.AID;
import jade.core.behaviours.CyclicBehaviour;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.lang.acl.ACLMessage;
import org.asaa.agents.CrossroadAgent;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

import static java.util.Objects.nonNull;
import static java.util.stream.Collectors.toMap;

public class HandleNeighbors extends CyclicBehaviour {

    private final CrossroadAgent agent;

    public HandleNeighbors(CrossroadAgent agent) {
        this.agent = agent;
        sendSubscriptions();
    }

    private void sendSubscriptions() {
        try {
            DFAgentDescription template = new DFAgentDescription();
            ServiceDescription serviceCriteria = new ServiceDescription();
            serviceCriteria.setType("crossroad");  // Specify the service type to search for
            template.addServices(serviceCriteria);

            // Search the DF for matching services
            DFAgentDescription[] result = DFService.search(agent, template);
            if (result.length == 0) {
                System.out.println("[%s] No delivery possibilities found");
                return;
            }
            final Map<AID, Boolean> newPlatforms = Arrays.stream(result)
                    .collect(toMap(DFAgentDescription::getName, desc -> desc.getAllServices().hasNext()));
            final List<AID> addedPlatforms = newPlatforms.entrySet().stream()
                    .filter(Map.Entry::getValue)
                    .map(Map.Entry::getKey)
                    .filter(x -> agent.getNeighbors().contains(x.getLocalName()))
                    .toList();

            System.out.printf("[%s] Found the following services:\n", agent.getLocalName());
            for (AID neighbor : addedPlatforms) {
                System.out.printf("\t[%s]Agent name: %s\n", agent.getLocalName(), neighbor.getLocalName());
                ACLMessage msg = new ACLMessage(ACLMessage.SUBSCRIBE);
                msg.addReceiver(neighbor);
                System.out.printf("\t[%s] sending subscribe message to %s\n", agent.getLocalName(), neighbor.getLocalName());
                agent.send(msg);
            }

        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public void action() {
        final ACLMessage msg = agent.receive();

        if (nonNull(msg)) {
            switch (msg.getPerformative()) {
                case ACLMessage.INFORM:
                    handleInform(msg);
                    break;
                case ACLMessage.SUBSCRIBE:
                    handleSubscribe(msg);
                    break;
                case ACLMessage.CANCEL:
                    handleCancel(msg);
                    break;
                default:
                    System.out.printf("[%s] Received not expected message: %s\n", agent.getLocalName(), msg.getContent());
                    break;
            }
        } else {
            block();
        }
    }

    private void handleSubscribe(final ACLMessage msg) {
        System.out.printf("[%s] Received SUBSCRIBE from [%s]\n", agent.getLocalName(),
                msg.getSender().getLocalName());
        if(agent.getNeighbors().contains(msg.getSender().getLocalName())) {
            if (!agent.getActiveNeighbors().containsKey(msg.getSender().getLocalName())) {
                ACLMessage reply = msg.createReply();
                reply.setPerformative(ACLMessage.SUBSCRIBE);
                agent.send(reply);
            }
            agent.getActiveNeighbors().put(msg.getSender().getLocalName(), msg.getSender());
        }
    }

    private void handleCancel(final ACLMessage msg) {
        System.out.printf("[%s] Received CANCEL from [%s]\n", agent.getLocalName(),
                msg.getSender().getLocalName());
        agent.getActiveNeighbors().remove(msg.getSender().getLocalName());
    }

    private void handleInform(final ACLMessage msg) {
        System.out.printf("[%s] Received an INFORM message from [%s]: %s\n", agent.getLocalName(),
                msg.getSender().getLocalName(), msg.getContent());
    }
}
