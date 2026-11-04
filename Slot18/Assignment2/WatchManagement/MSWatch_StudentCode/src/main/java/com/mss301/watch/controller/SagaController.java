package com.mss301.watch.controller;

import com.mss301.watch.dto.ApiResponse;
import com.mss301.watch.dto.SagaResponse;
import com.mss301.watch.entity.SagaState;
import com.mss301.watch.repository.SagaLogRepository;
import com.mss301.watch.repository.SagaStateRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

/** Xem trạng thái + nhật ký Saga để CHỨNG MINH Saga đã chạy / bù trừ thế nào (Admin only). */
// [TODO-6.14: GET /api/sagas, /api/sagas/{sagaId}]
@RestController
@RequestMapping("/api/sagas")
@RequiredArgsConstructor
@Tag(name = "Saga", description = "Saga state & step logs (for testing/monitoring)")
public class SagaController {

    private final SagaStateRepository stateRepository;
    private final SagaLogRepository logRepository;

    @GetMapping
    @Operation(summary = "Các saga gần nhất (mới nhất trước)")
    public ResponseEntity<ApiResponse<List<SagaResponse>>> recent(
            @RequestHeader(value = "X-User-Role", required = false) String role,
            @RequestParam(defaultValue = "20") int limit) {
        WatchController.checkAdminRole(role);
        List<SagaResponse> list = stateRepository.findAllByOrderByIdDesc(PageRequest.of(0, Math.min(limit, 100)))
            .stream().map(s -> SagaResponse.of(s, null)).toList();
        return ResponseEntity.ok(ApiResponse.success(list, "Success"));
    }

    @GetMapping("/{sagaId}")
    @Operation(summary = "Chi tiết 1 saga kèm từng bước EXECUTE / COMPENSATE")
    public ResponseEntity<ApiResponse<SagaResponse>> detail(
            @RequestHeader(value = "X-User-Role", required = false) String role,
            @PathVariable String sagaId) {
        WatchController.checkAdminRole(role);
        SagaState state = stateRepository.findBySagaId(sagaId)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Saga not found: " + sagaId));
        return ResponseEntity.ok(ApiResponse.success(
            SagaResponse.of(state, logRepository.findBySagaIdOrderByIdAsc(sagaId)), "Success"));
    }
}
