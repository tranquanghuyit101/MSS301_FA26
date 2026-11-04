package com.mss301.brand.dto;

import java.util.List;

public record BrandWatchesResponse(Integer brandId, String brandName, int watchCount, List<Integer> watchIds) {
}
