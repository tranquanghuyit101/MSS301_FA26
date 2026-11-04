package com.mss301.watch.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

/** Nhật ký từng bước của Saga: đây là "bằng chứng" để chứng minh Saga đã chạy / bù trừ thế nào. */
// [TODO-6.2: bảng SagaLogs (nhật ký từng bước)]
@Entity
@Table(name = "SagaLogs")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SagaLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "SagaId", nullable = false, length = 36)
    private String sagaId;

    @Column(name = "StepNo")
    private Integer stepNo;

    @Column(name = "StepName", length = 50)
    private String stepName;            // CREATE_WATCH, ASSIGN_BRAND, DELETE_WATCH, UNASSIGN_BRAND, ...

    @Column(name = "Phase", length = 20)
    private String phase;               // EXECUTE | COMPENSATE | FAULT

    @Column(name = "Result", length = 20)
    private String result;              // SUCCESS | FAILED | TRIGGERED | SKIPPED

    @Column(name = "Message", length = 1000)
    private String message;

    @Column(name = "CreatedAt")
    private LocalDateTime createdAt;
}
