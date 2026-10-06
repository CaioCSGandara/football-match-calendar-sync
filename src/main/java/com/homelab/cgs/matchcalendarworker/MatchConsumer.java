package com.homelab.cgs.matchcalendarworker;

import com.homelab.cgs.matchcalendarworker.config.RabbitMQConfig;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
public class MatchConsumer {

    @RabbitListener(queues = RabbitMQConfig.QUEUE_NAME)
    public void receiveMessage(String string) {
        System.out.println("Received message: " + string);
    }
}
