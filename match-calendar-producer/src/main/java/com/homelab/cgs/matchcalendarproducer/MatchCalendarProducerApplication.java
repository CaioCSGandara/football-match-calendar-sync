package com.homelab.cgs.matchcalendarproducer;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class MatchCalendarProducerApplication {

	public static void main(String[] args) {
		SpringApplication.run(MatchCalendarProducerApplication.class, args);
	}

}
