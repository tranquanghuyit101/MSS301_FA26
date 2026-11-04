package com.mss301.watch.controller;

import com.mss301.watch.dto.ApiResponse;
import com.mss301.watch.dto.WatchRequest;
import com.mss301.watch.dto.WatchResponse;
import com.mss301.watch.service.SagaResult;
import com.mss301.watch.service.WatchService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

// [TODO-6.14: CRUD /api/watches, header X-Saga-Id, X-Saga-Fail-After-Step, kiểm tra role]
@RestController
@RequestMapping("/api/watches")
@RequiredArgsConstructor
@Tag(name = "Watch", description = "Watch management with Saga Pattern")
public class WatchController {

    /** Header dùng để GIẢ LẬP lỗi sau bước N của Saga (chỉ khi saga.fault-injection.enabled=true). */
    public static final String FAIL_AFTER_HEADER = "X-Saga-Fail-After-Step";
    public static final String SAGA_ID_HEADER = "X-Saga-Id";

    private final WatchService watchService;

    @GetMapping
    @Operation(summary = "List all watches (public, newest first)")
    public ResponseEntity<ApiResponse<List<WatchResponse>>> findAll() {
        return ResponseEntity.ok(ApiResponse.success(watchService.findAll(), "Success"));
    }

    @PostMapping
    @Operation(summary = "Add a new watch (Admin only) - runs CREATE_WATCH saga")
    public ResponseEntity<ApiResponse<WatchResponse>> create(
            @RequestHeader(value = "X-User-Role", required = false) String role,
            @Parameter(description = "Test only: fail after step N")
            @RequestHeader(value = FAIL_AFTER_HEADER, required = false) Integer failAfterStep,
            @Valid @RequestBody WatchRequest request) {
        checkAdminRole(role);
        SagaResult<WatchResponse> result = watchService.create(request, failAfterStep);
        return ResponseEntity.status(HttpStatus.CREATED)
            .header(SAGA_ID_HEADER, result.sagaId())
            .body(ApiResponse.success(result.body(), "Watch created successfully (saga " + result.sagaId() + " COMPLETED)"));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update a watch (Admin only) - runs UPDATE_WATCH saga")
    public ResponseEntity<ApiResponse<WatchResponse>> update(
            @RequestHeader(value = "X-User-Role", required = false) String role,
            @RequestHeader(value = FAIL_AFTER_HEADER, required = false) Integer failAfterStep,
            @PathVariable Integer id,
            @Valid @RequestBody WatchRequest request) {
        checkAdminRole(role);
        SagaResult<WatchResponse> result = watchService.update(id, request, failAfterStep);
        return ResponseEntity.ok()
            .header(SAGA_ID_HEADER, result.sagaId())
            .body(ApiResponse.success(result.body(), "Watch updated successfully (saga " + result.sagaId() + " COMPLETED)"));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete a watch (Admin only) - runs DELETE_WATCH saga")
    public ResponseEntity<ApiResponse<Void>> delete(
            @RequestHeader(value = "X-User-Role", required = false) String role,
            @RequestHeader(value = FAIL_AFTER_HEADER, required = false) Integer failAfterStep,
            @PathVariable Integer id) {
        checkAdminRole(role);
        SagaResult<Void> result = watchService.delete(id, failAfterStep);
        return ResponseEntity.ok()
            .header(SAGA_ID_HEADER, result.sagaId())
            .body(ApiResponse.success(null, "Watch deleted successfully (saga " + result.sagaId() + " COMPLETED)"));
    }

    // [TODO-6.14: chỉ Admin (role=1)]
    static void checkAdminRole(String role) {
        if (!"1".equals(role)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN,
                "Only Administrator (role=1) can perform this action");
        }
    }
}
