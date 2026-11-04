package com.mss301.watch.service.saga;

import com.mss301.watch.entity.SagaLog;
import com.mss301.watch.entity.SagaState;
import com.mss301.watch.repository.SagaLogRepository;
import com.mss301.watch.repository.SagaStateRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Ghi trạng thái + nhật ký Saga (State Management - Slide 25, 27).
 * <p>
 * REQUIRES_NEW: mỗi lần ghi là 1 transaction riêng và COMMIT NGAY. Kể cả khi ai đó lỡ bọc
 * orchestrator trong @Transactional rồi bị rollback, nhật ký Saga vẫn còn để điều tra.
 */
// [TODO-6.4: ghi trạng thái/nhật ký bằng REQUIRES_NEW]
@Service
@RequiredArgsConstructor
public class SagaTracker {

    private final SagaStateRepository stateRepository;
    private final SagaLogRepository logRepository;

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public SagaState start(String sagaType, Integer watchId, String payload) {
        LocalDateTime now = LocalDateTime.now();
        return stateRepository.save(SagaState.builder()
            .sagaId(UUID.randomUUID().toString())
            .sagaType(sagaType)
            .watchId(watchId)
            .status(SagaStatus.PENDING)
            .payload(payload)
            .createdAt(now)
            .updatedAt(now)
            .build());
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void updateStatus(String sagaId, SagaStatus status) {
        SagaState s = get(sagaId);
        s.setStatus(status);
        s.setUpdatedAt(LocalDateTime.now());
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void currentStep(String sagaId, String stepName) {
        SagaState s = get(sagaId);
        s.setCurrentStep(stepName);
        s.setUpdatedAt(LocalDateTime.now());
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void attachWatch(String sagaId, Integer watchId) {
        get(sagaId).setWatchId(watchId);
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void fail(String sagaId, String reason) {
        SagaState s = get(sagaId);
        s.setStatus(SagaStatus.FAILED);
        s.setFailureReason(truncate(reason));
        s.setUpdatedAt(LocalDateTime.now());
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void log(String sagaId, int stepNo, String stepName, String phase, String result, String message) {
        logRepository.save(SagaLog.builder()
            .sagaId(sagaId)
            .stepNo(stepNo)
            .stepName(stepName)
            .phase(phase)
            .result(result)
            .message(truncate(message))
            .createdAt(LocalDateTime.now())
            .build());
    }

    private SagaState get(String sagaId) {
        return stateRepository.findBySagaId(sagaId)
            .orElseThrow(() -> new IllegalStateException("Saga not found: " + sagaId));
    }

    private String truncate(String s) {
        return s == null || s.length() <= 1000 ? s : s.substring(0, 1000);
    }
}
