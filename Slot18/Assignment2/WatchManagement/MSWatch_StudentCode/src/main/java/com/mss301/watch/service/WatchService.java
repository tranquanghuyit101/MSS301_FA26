package com.mss301.watch.service;

import com.mss301.watch.dto.WatchRequest;
import com.mss301.watch.dto.WatchResponse;
import com.mss301.watch.entity.Watch;
import com.mss301.watch.repository.WatchCategoryRepository;
import com.mss301.watch.repository.WatchRepository;
import com.mss301.watch.service.saga.SagaOutcome;
import com.mss301.watch.service.saga.WatchSagaOrchestrator;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDate;
import java.util.List;

/**
 * Business service: kiểm tra nghiệp vụ TRƯỚC khi chạy Saga (validate rẻ, không cần compensate),
 * sau đó giao cho WatchSagaOrchestrator thực hiện các bước phân tán.
 */
// [TODO-6.13: validate nghiệp vụ TRƯỚC khi chạy Saga]
@Service
@RequiredArgsConstructor
public class WatchService {

    private final WatchRepository watchRepository;
    private final WatchCategoryRepository categoryRepository;
    private final WatchLocalService localService;
    private final WatchSagaOrchestrator sagaOrchestrator;

    /** Watch mới nhất ở đầu danh sách (ORDER BY WatchID DESC). */
    // [TODO-6.13: watch mới ở đầu danh sách]
    public List<WatchResponse> findAll() {
        return watchRepository.findAllByOrderByWatchIdDesc().stream()
            .map(this::toResponse).toList();
    }

    public SagaResult<WatchResponse> create(WatchRequest request, Integer failAfterStep) {
        validate(request);
        SagaOutcome outcome = sagaOrchestrator.createWatch(WatchData.from(request, null), failAfterStep);
        return new SagaResult<>(outcome.sagaId(), loadResponse(outcome.watchId()));
    }

    public SagaResult<WatchResponse> update(Integer id, WatchRequest request, Integer failAfterStep) {
        WatchData before = localService.load(id);          // 404 nếu không có
        validate(request);
        SagaOutcome outcome = sagaOrchestrator.updateWatch(before, WatchData.from(request, id), failAfterStep);
        return new SagaResult<>(outcome.sagaId(), loadResponse(id));
    }

    public SagaResult<Void> delete(Integer id, Integer failAfterStep) {
        WatchData before = localService.load(id);
        SagaOutcome outcome = sagaOrchestrator.deleteWatch(before, failAfterStep);
        return new SagaResult<>(outcome.sagaId(), null);
    }

    // [TODO-6.13]
    private void validate(WatchRequest request) {
        if (!LocalDate.now().equals(request.getReleaseDate())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                "Release date must be today's date: " + LocalDate.now());
        }
        if (!categoryRepository.existsById(request.getCategoryId())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                "Category not found with id: " + request.getCategoryId());
        }
        // Brand KHÔNG kiểm tra ở đây: brand thuộc MSBrand -> được xác nhận trong bước ASSIGN_BRAND của Saga.
    }

    private WatchResponse loadResponse(Integer id) {
        return watchRepository.findById(id).map(this::toResponse)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Watch not found with id: " + id));
    }

    private WatchResponse toResponse(Watch w) {
        return WatchResponse.builder()
            .watchId(w.getWatchId())
            .name(w.getName())
            .categoryId(w.getCategory() != null ? w.getCategory().getCategoryId() : null)
            .categoryName(w.getCategory() != null ? w.getCategory().getCategoryName() : null)
            .brandId(w.getBrandId())
            .caseMaterial(w.getCaseMaterial())
            .strapMaterial(w.getStrapMaterial())
            .waterpMaterial(w.getWaterpMaterial())
            .price(w.getPrice())
            .releaseDate(w.getReleaseDate())
            .stock(w.getStock())
            .build();
    }
}
