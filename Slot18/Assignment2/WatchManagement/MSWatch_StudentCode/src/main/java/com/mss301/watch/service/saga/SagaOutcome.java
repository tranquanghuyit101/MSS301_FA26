package com.mss301.watch.service.saga;

public record SagaOutcome(String sagaId, Integer watchId, SagaStatus status) {
}
