package com.mss301.watch.repository;

import com.mss301.watch.entity.WatchCategory;
import org.springframework.data.jpa.repository.JpaRepository;

// [TODO-6.16]
public interface WatchCategoryRepository extends JpaRepository<WatchCategory, Integer> {
}
