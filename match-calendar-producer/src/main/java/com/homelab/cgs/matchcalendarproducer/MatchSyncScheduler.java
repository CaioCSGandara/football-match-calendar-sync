package com.homelab.cgs.matchcalendarproducer;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class MatchSyncScheduler {

    public final MatchProducer matchProducer;

    public MatchSyncScheduler(MatchProducer matchProducer) {
        this.matchProducer = matchProducer;
    }

    @Scheduled(fixedRate = 10000) // runs every 10 seconds
    public void syncMatches() {
        matchProducer.sendMessage("Testing...");
    }
}
