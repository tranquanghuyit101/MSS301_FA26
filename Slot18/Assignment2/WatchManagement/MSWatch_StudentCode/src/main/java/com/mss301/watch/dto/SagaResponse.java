package com.mss301.watch.dto;

import com.mss301.watch.entity.SagaLog;
import com.mss301.watch.entity.SagaState;
import com.mss301.watch.service.saga.SagaStatus;

import java.time.LocalDateTime;
import java.util.List;

// [TODO-6.14]
public record SagaResponse(
    String sagaId,
    String sagaType,
    Integer watchId,
    SagaStatus status,
    String currentStep,
    String failureReason,
    String payload,
    LocalDateTime createdAt,
    LocalDateTime updatedAt,
    List<StepLog> steps
) {
    public record StepLog(Integer stepNo, String stepName, String phase, String result, String message, LocalDateTime at) {
    }

    public static SagaResponse of(SagaState s, List<SagaLog> logs) {
        List<StepLog> steps = logs == null ? null : logs.stream()
            .map(l -> new StepLog(l.getStepNo(), l.getStepName(), l.getPhase(), l.getResult(), l.getMessage(), l.getCreatedAt()))
            .toList();
        return new SagaResponse(s.getSagaId(), s.getSagaType(), s.getWatchId(), s.getStatus(), s.getCurrentStep(),
            s.getFailureReason(), s.getPayload(), s.getCreatedAt(), s.getUpdatedAt(), steps);
    }
}
