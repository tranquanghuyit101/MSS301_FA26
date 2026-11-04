package com.mss301.watch.service.saga;

import lombok.Getter;
import org.springframework.http.HttpStatus;

/** Ném ra khi Saga thất bại (sau khi đã chạy compensation). GlobalExceptionHandler chuyển thành HTTP response. */
// [TODO-6.15]
@Getter
public class SagaExecutionException extends RuntimeException {

    private final String sagaId;
    private final SagaStatus sagaStatus;   // COMPENSATED hoặc COMPENSATING (nếu compensation lỗi)
    private final String failedStep;
    private final HttpStatus httpStatus;
    private final String reason;

    public SagaExecutionException(String sagaId, SagaStatus sagaStatus, String failedStep,
                                  HttpStatus httpStatus, String reason, Throwable cause) {
        super("Saga " + sagaId + " " + sagaStatus + " - failed at " + failedStep + ": " + reason, cause);
        this.sagaId = sagaId;
        this.sagaStatus = sagaStatus;
        this.failedStep = failedStep;
        this.httpStatus = httpStatus;
        this.reason = reason;
    }
}
