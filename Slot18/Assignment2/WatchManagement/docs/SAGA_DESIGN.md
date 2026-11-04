# Saga Design – Watch Management

> [TODO-4.1] Tài liệu thiết kế Saga (sinh viên tự điền trước khi code).

## Participants

| Service | Vai trò | Database | Dữ liệu tham gia Saga |
|---|---|---|---|
| MSWatch | Orchestrator | DBWatch | `Watches`, `SagaStates`, `SagaLogs` |
| MSBrand | Participant | DBBrand | `BrandWatches` |

## Saga CREATE_WATCH

| # | Local transaction | Service / DB | Compensation | Idempotent? |
|---|---|---|---|---|
| 1 | CREATE_WATCH – INSERT Watches | MSWatch / DBWatch | DELETE_WATCH | ✔ (`deleteIfExists`) |
| 2 | ASSIGN_BRAND – upsert BrandWatches | MSBrand / DBBrand | UNASSIGN_BRAND | ✔ |

## Saga UPDATE_WATCH

| # | Local transaction | Service / DB | Compensation | Idempotent? |
|---|---|---|---|---|
| 1 | UPDATE_WATCH | MSWatch / DBWatch | RESTORE_WATCH (snapshot `before`) | ✔ |
| 2 | ASSIGN_BRAND (brand mới) | MSBrand / DBBrand | ASSIGN_BRAND_BACK (brand cũ) | ✔ |

## Saga DELETE_WATCH

| # | Local transaction | Service / DB | Compensation | Idempotent? |
|---|---|---|---|---|
| 1 | UNASSIGN_BRAND | MSBrand / DBBrand | ASSIGN_BRAND_BACK | ✔ |
| 2 | DELETE_WATCH | MSWatch / DBWatch | — **PIVOT** | — |

## State machine

```
PENDING → EXECUTING → COMPLETED
               └→ FAILED → COMPENSATING → COMPENSATED
                                 └→ (compensation lỗi) dừng ở COMPENSATING
```

## Quyết định thiết kế

1. Orchestration (không dùng Choreography) vì chỉ có 2 service, luồng ngắn, dễ quan sát.
2. Orchestrator không có `@Transactional`; mỗi bước là 1 local transaction.
3. Compensation chạy LIFO, retry tối đa 3 lần, yêu cầu idempotent.
4. Bước xoá cứng (`DELETE_WATCH`) là pivot, đặt cuối Saga xoá.
5. Validate rẻ (name, price, releaseDate, category) chạy trước khi Saga bắt đầu.
