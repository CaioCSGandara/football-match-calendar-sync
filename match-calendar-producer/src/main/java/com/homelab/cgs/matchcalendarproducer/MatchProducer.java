package com.homelab.cgs.matchcalendarproducer;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
public class MatchProducer {

    public final RabbitTemplate rabbitTemplate;
    public static final String EXCHANGE_NAME = "calendar.matches.sync.exchange";
    public static final String ROUTING_KEY = "matches.scheduled";

    @Autowired
    public MatchProducer(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void sendMessage(String message) {
        rabbitTemplate.convertAndSend(EXCHANGE_NAME, ROUTING_KEY, message);
    }
}
