package com.mss301.watch.exception;

import com.mss301.watch.dto.ApiResponse;
import com.mss301.watch.service.saga.SagaExecutionException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ResponseStatusException;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.stream.Collectors;

// [TODO-6.15: chuyển SagaExecutionException / validation thành HTTP response]
@RestControllerAdvice
public class GlobalExceptionHandler {

    /** Saga thất bại: trả về sagaId + trạng thái cuối để client tra cứu GET /api/sagas/{sagaId}. */
    @ExceptionHandler(SagaExecutionException.class)
    public ResponseEntity<ApiResponse<Map<String, Object>>> handleSaga(SagaExecutionException ex) {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("sagaId", ex.getSagaId());
        data.put("sagaStatus", ex.getSagaStatus());
        data.put("failedStep", ex.getFailedStep());
        data.put("reason", ex.getReason());
        return ResponseEntity.status(ex.getHttpStatus())
            .header("X-Saga-Id", ex.getSagaId())
            .body(ApiResponse.<Map<String, Object>>builder()
                .success(false)
                .message("Saga " + ex.getSagaStatus() + ": " + ex.getReason())
                .data(data)
                .build());
    }

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<ApiResponse<Void>> handleResponseStatus(ResponseStatusException ex) {
        return ResponseEntity.status(ex.getStatusCode())
            .body(ApiResponse.error(ex.getReason()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidation(MethodArgumentNotValidException ex) {
        String message = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return ResponseEntity.badRequest().body(ApiResponse.error(message));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGeneral(Exception ex) {
        return ResponseEntity.internalServerError()
            .body(ApiResponse.error("Internal error: " + ex.getMessage()));
    }
}
