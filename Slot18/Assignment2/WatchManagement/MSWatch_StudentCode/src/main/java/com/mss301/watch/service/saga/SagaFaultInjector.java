package com.mss301.watch.service.saga;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * Fault injection cho mục đích HỌC TẬP: client gửi header "X-Saga-Fail-After-Step: N"
 * -> Saga sẽ ném lỗi giả ngay SAU khi bước N commit thành công.
 * <p>
 * Nhờ vậy có thể chứng minh: các bước đã commit (kể cả ở MSBrand) đều được bù trừ theo thứ tự ngược.
 * Tắt bằng saga.fault-injection.enabled=false.
 */
// [TODO-6.12: fault injection để chứng minh compensation]
@Component
@Slf4j
public class SagaFaultInjector {

    @Value("${saga.fault-injection.enabled:false}")
    private boolean enabled;

    public boolean shouldFailAfter(Integer failAfterStep, int completedStepNo) {
        if (failAfterStep == null) {
            return false;
        }
        if (!enabled) {
            log.warn("Header X-Saga-Fail-After-Step={} ignored because saga.fault-injection.enabled=false", failAfterStep);
            return false;
        }
        return failAfterStep == completedStepNo;
    }
}
