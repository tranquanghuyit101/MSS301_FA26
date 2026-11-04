package com.mss301.watch.service;

import com.mss301.watch.entity.Watch;
import com.mss301.watch.repository.WatchCategoryRepository;
import com.mss301.watch.repository.WatchRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

/**
 * Các LOCAL TRANSACTION của MSWatch trên DBWatch.
 * Mỗi method có @Transactional riêng -> commit ngay khi method kết thúc (ACID trong phạm vi 1 database).
 */
// [TODO-6.5: các local transaction trên DBWatch]
@Service
@RequiredArgsConstructor
@Slf4j
public class WatchLocalService {

    private final WatchRepository watchRepository;
    private final WatchCategoryRepository categoryRepository;

    @Transactional(readOnly = true)
    public WatchData load(Integer id) {
        return watchRepository.findById(id)
            .map(WatchData::from)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Watch not found with id: " + id));
    }

    /** Bước CREATE_WATCH. */
    @Transactional
    public Integer insert(WatchData d) {
        Watch w = new Watch();
        apply(w, d);
        Integer id = watchRepository.save(w).getWatchId();
        log.info("[LOCAL TX] INSERT watch id={} brand={}", id, d.brandId());
        return id;
    }

    /** Bước UPDATE_WATCH và cũng là compensation RESTORE_WATCH (ghi lại dữ liệu snapshot). */
    @Transactional
    public void update(WatchData d) {
        Watch w = watchRepository.findById(d.watchId())
            .orElseThrow(() -> new IllegalStateException("Watch " + d.watchId() + " no longer exists"));
        apply(w, d);                       // dirty checking -> UPDATE khi commit
        log.info("[LOCAL TX] UPDATE watch id={} brand={} name='{}'", d.watchId(), d.brandId(), d.name());
    }

    /** Compensation DELETE_WATCH - IDEMPOTENT: gọi lại nhiều lần vẫn an toàn. */
    @Transactional
    public void deleteIfExists(Integer id) {
        if (id != null && watchRepository.existsById(id)) {
            watchRepository.deleteById(id);
            log.info("[LOCAL TX] DELETE watch id={} (compensation)", id);
        }
    }

    /** Bước DELETE_WATCH (pivot của saga xoá). */
    @Transactional
    public void delete(Integer id) {
        Watch w = watchRepository.findById(id)
            .orElseThrow(() -> new IllegalStateException("Watch " + id + " no longer exists"));
        watchRepository.delete(w);
        log.info("[LOCAL TX] DELETE watch id={}", id);
    }

    private void apply(Watch w, WatchData d) {
        w.setName(d.name());
        w.setCategory(categoryRepository.getReferenceById(d.categoryId()));
        w.setBrandId(d.brandId());
        w.setCaseMaterial(d.caseMaterial());
        w.setStrapMaterial(d.strapMaterial());
        w.setWaterpMaterial(d.waterpMaterial());
        w.setPrice(d.price());
        w.setReleaseDate(d.releaseDate());
        w.setStock(d.stock());
    }
}
