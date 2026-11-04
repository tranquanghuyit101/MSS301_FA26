package com.mss301.watch.service.saga;

/**
 * 6 trạng thái của Saga (Chapter 06 - Slide 27).
 *
 * <pre>
 * PENDING -> EXECUTING -> COMPLETED                               (thành công)
 *                 \-> FAILED -> COMPENSATING -> COMPENSATED       (thất bại, đã bù trừ xong)
 *                                    \-> (dừng ở COMPENSATING)    (compensation cũng lỗi -> cần xử lý thủ công)
 * </pre>
 */
// [TODO-6.3: 6 trạng thái Saga (Slide 27)]
public enum SagaStatus {
    PENDING,
    EXECUTING,
    COMPLETED,
    FAILED,
    COMPENSATING,
    COMPENSATED
}
