package com.mss301.watch.entity;

import com.mss301.watch.service.saga.SagaStatus;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

/** Trạng thái hiện tại của 1 Saga (1 dòng / 1 lần thêm-sửa-xoá). Lịch sử từng bước nằm ở SagaLogs. */
// [TODO-6.2: bảng SagaStates]
@Entity
@Table(name = "SagaStates")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SagaState {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "SagaId", nullable = false, unique = true, length = 36)
    private String sagaId;

    @Column(name = "SagaType", length = 20)
    private String sagaType;            // CREATE_WATCH, UPDATE_WATCH, DELETE_WATCH

    @Column(name = "WatchID")
    private Integer watchId;

    @Enumerated(EnumType.STRING)
    @Column(name = "Status", length = 20)
    private SagaStatus status;          // PENDING -> EXECUTING -> COMPLETED | FAILED -> COMPENSATING -> COMPENSATED

    @Column(name = "CurrentStep", length = 50)
    private String currentStep;

    @Column(name = "Payload", columnDefinition = "NVARCHAR(MAX)")
    private String payload;             // JSON snapshot (dữ liệu trước/sau) để có thể khôi phục

    @Column(name = "FailureReason", length = 1000)
    private String failureReason;

    @Column(name = "CreatedAt")
    private LocalDateTime createdAt;

    @Column(name = "UpdatedAt")
    private LocalDateTime updatedAt;
}
