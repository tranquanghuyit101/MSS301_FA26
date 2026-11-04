package com.mss301.watch.service;

import com.mss301.watch.dto.WatchRequest;
import com.mss301.watch.entity.Watch;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Bản chụp (snapshot) dữ liệu của 1 watch, không phụ thuộc JPA.
 * Dùng làm input cho các bước Saga và làm dữ liệu khôi phục (RESTORE) khi compensate.
 */
// [TODO-6.6: snapshot dữ liệu để RESTORE]
public record WatchData(
    Integer watchId,
    String name,
    Integer categoryId,
    Integer brandId,
    String caseMaterial,
    String strapMaterial,
    String waterpMaterial,
    BigDecimal price,
    LocalDate releaseDate,
    Integer stock
) {
    public static WatchData from(Watch w) {
        return new WatchData(w.getWatchId(), w.getName(),
            w.getCategory() != null ? w.getCategory().getCategoryId() : null,
            w.getBrandId(), w.getCaseMaterial(), w.getStrapMaterial(), w.getWaterpMaterial(),
            w.getPrice(), w.getReleaseDate(), w.getStock());
    }

    public static WatchData from(WatchRequest r, Integer watchId) {
        return new WatchData(watchId, r.getName(), r.getCategoryId(), r.getBrandId(),
            r.getCaseMaterial(), r.getStrapMaterial(), r.getWaterpMaterial(),
            r.getPrice(), r.getReleaseDate(), r.getStock());
    }
}
