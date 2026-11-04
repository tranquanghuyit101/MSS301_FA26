package com.mss301.watch.service;

public record SagaResult<T>(String sagaId, T body) {
}
