package com.mss301.watch.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;

/**
 * Client gọi các LOCAL TRANSACTION của participant MSBrand.
 * - HTTP 4xx/5xx  -> FeignException (VD: FeignException.NotFound khi brand không tồn tại)
 * - MSBrand tắt    -> RetryableException (status = -1)
 * Orchestrator bắt các exception này để quyết định compensate.
 */
// [TODO-6.7: Feign gọi API nội bộ của MSBrand]
@FeignClient(name = "ms-brand", url = "${brand-service.url}")
public interface BrandServiceClient {

    /** Gán watch vào brand (idempotent). Dùng làm bước Saga và cũng làm compensation. */
    @PutMapping("/internal/brands/{brandId}/watches/{watchId}")
    void assignWatch(@PathVariable("brandId") Integer brandId, @PathVariable("watchId") Integer watchId);

    /** Gỡ watch khỏi brand (idempotent). */
    @DeleteMapping("/internal/brands/watches/{watchId}")
    void unassignWatch(@PathVariable("watchId") Integer watchId);
}
