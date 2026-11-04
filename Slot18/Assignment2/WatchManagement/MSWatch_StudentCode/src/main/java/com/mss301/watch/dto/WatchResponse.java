package com.mss301.watch.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class WatchResponse {
    private Integer watchId;
    private String name;
    private Integer categoryId;
    private String categoryName;
    private Integer brandId;
    private String caseMaterial;
    private String strapMaterial;
    private String waterpMaterial;
    private BigDecimal price;
    private LocalDate releaseDate;
    private Integer stock;
}
