package com.mss301.watch.repository;

import com.mss301.watch.entity.SagaState;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

// [TODO-6.2]
public interface SagaStateRepository extends JpaRepository<SagaState, Long> {
    Optional<SagaState> findBySagaId(String sagaId);
    List<SagaState> findAllByOrderByIdDesc(Pageable pageable);
}
