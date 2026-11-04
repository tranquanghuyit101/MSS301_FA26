package com.mss301.watch.service.saga;

/**
 * Một bước của Saga = 1 local transaction (action) + 1 compensating transaction (compensation).
 * <p>
 * Bước KHÔNG có compensation gọi là <b>pivot</b>: khi pivot đã commit thì Saga không thể quay lui nữa,
 * chỉ có thể đi tiếp tới COMPLETED. Vì vậy pivot luôn được đặt ở CUỐI chuỗi.
 */
// [TODO-6.8: bước Saga = action + compensation; pivot]
public record SagaStep(String name, Runnable action, String compensationName, Runnable compensation) {

    public static SagaStep of(String name, Runnable action, String compensationName, Runnable compensation) {
        return new SagaStep(name, action, compensationName, compensation);
    }

    public static SagaStep pivot(String name, Runnable action) {
        return new SagaStep(name, action, null, null);
    }

    public boolean isPivot() {
        return compensation == null;
    }
}
